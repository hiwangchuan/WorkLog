from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import AppError, ok, page
from app.models import Team, TeamMember, User
from app.schemas import TeamCreate, TeamMemberCreate, TeamMemberOut, TeamMemberUpdate, TeamOut, TeamUpdate
from app.utils.serializers import dump

router = APIRouter(prefix="/teams", tags=["teams"])

MANAGE_ROLES = {"admin", "leader"}


def _membership(db: Session, team_id: int, user_id: int) -> TeamMember | None:
    return db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id).first()


def _team_for_user(db: Session, team_id: int, user: User) -> tuple[Team, TeamMember]:
    team = db.get(Team, team_id)
    member = _membership(db, team_id, user.id)
    if not team or not member:
        raise AppError("团队不存在或无权访问", status_code=404)
    return team, member


def _require_manager(member: TeamMember) -> None:
    if member.role not in MANAGE_ROLES:
        raise AppError("当前角色无权管理团队", code=40003, status_code=403)


def _team_payload(db: Session, team: Team, role: str | None) -> dict:
    data = dump(TeamOut, team)
    data["role"] = role
    data["member_count"] = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
    return data


def _member_payload(row: tuple[TeamMember, User]) -> dict:
    member, user = row
    return TeamMemberOut(
        id=member.id,
        team_id=member.team_id,
        user_id=user.id,
        username=user.username,
        email=user.email,
        nickname=user.nickname,
        role=member.role,
        joined_at=member.joined_at,
    ).model_dump(mode="json")


@router.get("")
def list_teams(
    keyword: str | None = None,
    status: str | None = None,
    page_number: int = Query(1, alias="page", ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Team, TeamMember.role)
        .join(TeamMember, TeamMember.team_id == Team.id)
        .filter(TeamMember.user_id == current_user.id)
    )
    if keyword:
        query = query.filter(or_(Team.name.ilike(f"%{keyword}%"), Team.description.ilike(f"%{keyword}%")))
    if status:
        query = query.filter(Team.status == status)
    total = query.count()
    rows = query.order_by(Team.updated_at.desc()).offset((page_number - 1) * page_size).limit(page_size).all()
    return page([_team_payload(db, team, role) for team, role in rows], total, page_number, page_size)


@router.post("")
def create_team(payload: TeamCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    team = Team(**payload.model_dump(), owner_id=current_user.id)
    db.add(team)
    db.flush()
    db.add(TeamMember(team_id=team.id, user_id=current_user.id, role="admin"))
    db.commit()
    db.refresh(team)
    return ok(_team_payload(db, team, "admin"))


@router.get("/{team_id}")
def get_team(team_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    team, member = _team_for_user(db, team_id, current_user)
    return ok(_team_payload(db, team, member.role))


@router.put("/{team_id}")
def update_team(team_id: int, payload: TeamUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    team, member = _team_for_user(db, team_id, current_user)
    _require_manager(member)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(team, key, value)
    db.add(team)
    db.commit()
    db.refresh(team)
    return ok(_team_payload(db, team, member.role))


@router.delete("/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    team, member = _team_for_user(db, team_id, current_user)
    _require_manager(member)
    if team.owner_id != current_user.id:
        raise AppError("只有团队创建者可以删除团队", code=40003, status_code=403)
    db.delete(team)
    db.commit()
    return ok({"deleted": True})


@router.get("/{team_id}/members")
def list_members(team_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _team_for_user(db, team_id, current_user)
    rows = (
        db.query(TeamMember, User)
        .join(User, User.id == TeamMember.user_id)
        .filter(TeamMember.team_id == team_id)
        .order_by(TeamMember.joined_at.asc(), TeamMember.id.asc())
        .all()
    )
    return ok([_member_payload(row) for row in rows])


@router.post("/{team_id}/members")
def add_member(
    team_id: int,
    payload: TeamMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _team_for_user(db, team_id, current_user)
    _, member = _team_for_user(db, team_id, current_user)
    _require_manager(member)
    user = db.query(User).filter(or_(User.username == payload.username, User.email == payload.username)).first()
    if not user:
        raise AppError("用户不存在")
    if _membership(db, team_id, user.id):
        raise AppError("用户已在团队中")
    new_member = TeamMember(team_id=team_id, user_id=user.id, role=payload.role)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return ok(
        TeamMemberOut(
            id=new_member.id,
            team_id=team_id,
            user_id=user.id,
            username=user.username,
            email=user.email,
            nickname=user.nickname,
            role=new_member.role,
            joined_at=new_member.joined_at,
        ).model_dump(mode="json")
    )


@router.put("/{team_id}/members/{member_id}")
def update_member(
    team_id: int,
    member_id: int,
    payload: TeamMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team, current_member = _team_for_user(db, team_id, current_user)
    _require_manager(current_member)
    member = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.id == member_id).first()
    if not member:
        raise AppError("成员不存在", status_code=404)
    if member.user_id == team.owner_id and payload.role != "admin":
        raise AppError("团队创建者必须保持管理员角色")
    member.role = payload.role
    db.add(member)
    db.commit()
    return ok({"updated": True})


@router.delete("/{team_id}/members/{member_id}")
def remove_member(team_id: int, member_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    team, current_member = _team_for_user(db, team_id, current_user)
    _require_manager(current_member)
    member = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.id == member_id).first()
    if not member:
        raise AppError("成员不存在", status_code=404)
    if member.user_id == team.owner_id:
        raise AppError("不能移除团队创建者")
    if member.role == "admin":
        admin_count = db.query(func.count(TeamMember.id)).filter(TeamMember.team_id == team_id, TeamMember.role == "admin").scalar()
        if admin_count <= 1:
            raise AppError("至少保留一名管理员")
    db.delete(member)
    db.commit()
    return ok({"deleted": True})
