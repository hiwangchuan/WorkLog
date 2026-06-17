from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import AppError, ok, page
from app.models import Project, Task, User, WorkLog, OvertimeLog
from app.schemas import ProjectCreate, ProjectOut, ProjectUpdate
from app.utils.serializers import dump, dump_list

router = APIRouter(prefix="/projects", tags=["projects"])


def owned_query(db: Session, user: User):
    return db.query(Project).filter(Project.owner_id == user.id)


@router.get("")
def list_projects(
    keyword: str | None = None,
    status: str | None = None,
    page_number: int = Query(1, alias="page", ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = owned_query(db, current_user)
    if keyword:
        query = query.filter(or_(Project.name.ilike(f"%{keyword}%"), Project.description.ilike(f"%{keyword}%")))
    if status:
        query = query.filter(Project.status == status)
    total = query.count()
    items = query.order_by(Project.updated_at.desc()).offset((page_number - 1) * page_size).limit(page_size).all()
    return page(dump_list(ProjectOut, items), total, page_number, page_size)


@router.post("")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = Project(**payload.model_dump(), owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return ok(dump(ProjectOut, project))


@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = owned_query(db, current_user).filter(Project.id == project_id).first()
    if not project:
        raise AppError("项目不存在", status_code=404)
    return ok(dump(ProjectOut, project))


@router.put("/{project_id}")
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = owned_query(db, current_user).filter(Project.id == project_id).first()
    if not project:
        raise AppError("项目不存在", status_code=404)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.add(project)
    db.commit()
    db.refresh(project)
    return ok(dump(ProjectOut, project))


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = owned_query(db, current_user).filter(Project.id == project_id).first()
    if not project:
        raise AppError("项目不存在", status_code=404)
    db.delete(project)
    db.commit()
    return ok({"deleted": True})


@router.get("/{project_id}/summary")
def project_summary(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = owned_query(db, current_user).filter(Project.id == project_id).first()
    if not project:
        raise AppError("项目不存在", status_code=404)
    task_count = db.query(Task).filter(Task.creator_id == current_user.id, Task.project_id == project_id).count()
    work_hours = (
        db.query(WorkLog.duration_hours).filter(WorkLog.user_id == current_user.id, WorkLog.project_id == project_id).all()
    )
    overtime_hours = (
        db.query(OvertimeLog.duration_hours)
        .filter(OvertimeLog.user_id == current_user.id, OvertimeLog.project_id == project_id)
        .all()
    )
    return ok(
        {
            "project": dump(ProjectOut, project),
            "task_count": task_count,
            "work_hours": round(sum(row[0] or 0 for row in work_hours), 2),
            "overtime_hours": round(sum(row[0] or 0 for row in overtime_hours), 2),
        }
    )
