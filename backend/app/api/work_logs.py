from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.tasks import refresh_actual_hours
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import AppError, ok, page
from app.models import User, WorkLog
from app.schemas import WorkLogCreate, WorkLogOut, WorkLogUpdate
from app.utils.serializers import dump, dump_list
from app.utils.time import calculate_hours

router = APIRouter(prefix="/work-logs", tags=["work-logs"])


def log_query(db: Session, user: User):
    return db.query(WorkLog).filter(WorkLog.user_id == user.id)


@router.get("")
def list_work_logs(
    keyword: str | None = None,
    date_start: date | None = None,
    date_end: date | None = None,
    project_id: int | None = None,
    task_id: int | None = None,
    work_type: str | None = None,
    page_number: int = Query(1, alias="page", ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = log_query(db, current_user)
    if keyword:
        query = query.filter(or_(WorkLog.title.ilike(f"%{keyword}%"), WorkLog.content.ilike(f"%{keyword}%")))
    if date_start:
        query = query.filter(WorkLog.work_date >= date_start)
    if date_end:
        query = query.filter(WorkLog.work_date <= date_end)
    if project_id:
        query = query.filter(WorkLog.project_id == project_id)
    if task_id:
        query = query.filter(WorkLog.task_id == task_id)
    if work_type:
        query = query.filter(WorkLog.work_type == work_type)
    total = query.count()
    items = query.order_by(WorkLog.work_date.desc(), WorkLog.id.desc()).offset((page_number - 1) * page_size).limit(page_size).all()
    return page(dump_list(WorkLogOut, items), total, page_number, page_size)


@router.post("")
def create_work_log(payload: WorkLogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = payload.model_dump()
    data["duration_hours"] = calculate_hours(data.get("start_time"), data.get("end_time"), data.get("duration_hours") or 0)
    record = WorkLog(**data, user_id=current_user.id)
    db.add(record)
    db.flush()
    refresh_actual_hours(db, record.task_id)
    db.commit()
    db.refresh(record)
    return ok(dump(WorkLogOut, record))


@router.get("/{log_id}")
def get_work_log(log_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = log_query(db, current_user).filter(WorkLog.id == log_id).first()
    if not record:
        raise AppError("工作记录不存在", status_code=404)
    return ok(dump(WorkLogOut, record))


@router.put("/{log_id}")
def update_work_log(log_id: int, payload: WorkLogUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = log_query(db, current_user).filter(WorkLog.id == log_id).first()
    if not record:
        raise AppError("工作记录不存在", status_code=404)
    old_task_id = record.task_id
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    record.duration_hours = calculate_hours(record.start_time, record.end_time, record.duration_hours)
    db.add(record)
    db.flush()
    refresh_actual_hours(db, old_task_id)
    refresh_actual_hours(db, record.task_id)
    db.commit()
    db.refresh(record)
    return ok(dump(WorkLogOut, record))


@router.delete("/{log_id}")
def delete_work_log(log_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = log_query(db, current_user).filter(WorkLog.id == log_id).first()
    if not record:
        raise AppError("工作记录不存在", status_code=404)
    task_id = record.task_id
    db.delete(record)
    db.flush()
    refresh_actual_hours(db, task_id)
    db.commit()
    return ok({"deleted": True})
