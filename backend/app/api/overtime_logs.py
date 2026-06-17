from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import AppError, ok, page
from app.models import OvertimeLog, User
from app.schemas import OvertimeCreate, OvertimeOut, OvertimeUpdate
from app.utils.serializers import dump, dump_list
from app.utils.time import calculate_hours

router = APIRouter(prefix="/overtime-logs", tags=["overtime-logs"])


def overtime_query(db: Session, user: User):
    return db.query(OvertimeLog).filter(OvertimeLog.user_id == user.id)


@router.get("")
def list_overtime(
    month: str | None = None,
    overtime_type: str | None = None,
    approval_status: str | None = None,
    project_id: int | None = None,
    page_number: int = Query(1, alias="page", ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = overtime_query(db, current_user)
    if month:
        query = query.filter(OvertimeLog.overtime_date >= date.fromisoformat(f"{month}-01"))
    if overtime_type:
        query = query.filter(OvertimeLog.overtime_type == overtime_type)
    if approval_status:
        query = query.filter(OvertimeLog.approval_status == approval_status)
    if project_id:
        query = query.filter(OvertimeLog.project_id == project_id)
    total = query.count()
    items = query.order_by(OvertimeLog.overtime_date.desc(), OvertimeLog.id.desc()).offset((page_number - 1) * page_size).limit(page_size).all()
    return page(dump_list(OvertimeOut, items), total, page_number, page_size)


@router.post("")
def create_overtime(payload: OvertimeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = payload.model_dump()
    data["duration_hours"] = calculate_hours(data.get("start_time"), data.get("end_time"), data.get("duration_hours") or 0)
    record = OvertimeLog(**data, user_id=current_user.id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return ok(dump(OvertimeOut, record))


@router.get("/{overtime_id}")
def get_overtime(overtime_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = overtime_query(db, current_user).filter(OvertimeLog.id == overtime_id).first()
    if not record:
        raise AppError("加班记录不存在", status_code=404)
    return ok(dump(OvertimeOut, record))


@router.put("/{overtime_id}")
def update_overtime(
    overtime_id: int, payload: OvertimeUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    record = overtime_query(db, current_user).filter(OvertimeLog.id == overtime_id).first()
    if not record:
        raise AppError("加班记录不存在", status_code=404)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    record.duration_hours = calculate_hours(record.start_time, record.end_time, record.duration_hours)
    db.add(record)
    db.commit()
    db.refresh(record)
    return ok(dump(OvertimeOut, record))


@router.delete("/{overtime_id}")
def delete_overtime(overtime_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = overtime_query(db, current_user).filter(OvertimeLog.id == overtime_id).first()
    if not record:
        raise AppError("加班记录不存在", status_code=404)
    db.delete(record)
    db.commit()
    return ok({"deleted": True})


@router.post("/{overtime_id}/submit")
def submit_overtime(overtime_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = overtime_query(db, current_user).filter(OvertimeLog.id == overtime_id).first()
    if not record:
        raise AppError("加班记录不存在", status_code=404)
    record.approval_status = "pending"
    db.add(record)
    db.commit()
    db.refresh(record)
    return ok(dump(OvertimeOut, record))


@router.post("/{overtime_id}/approve")
def approve_overtime(overtime_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = overtime_query(db, current_user).filter(OvertimeLog.id == overtime_id).first()
    if not record:
        raise AppError("加班记录不存在", status_code=404)
    record.approval_status = "approved"
    record.approver_id = current_user.id
    db.add(record)
    db.commit()
    db.refresh(record)
    return ok(dump(OvertimeOut, record))


@router.post("/{overtime_id}/reject")
def reject_overtime(overtime_id: int, comment: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = overtime_query(db, current_user).filter(OvertimeLog.id == overtime_id).first()
    if not record:
        raise AppError("加班记录不存在", status_code=404)
    record.approval_status = "rejected"
    record.approver_id = current_user.id
    record.approval_comment = comment
    db.add(record)
    db.commit()
    db.refresh(record)
    return ok(dump(OvertimeOut, record))
