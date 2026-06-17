from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import AppError, ok, page
from app.models import Task, User, WorkLog
from app.schemas import StatusPatch, TaskCreate, TaskOut, TaskUpdate
from app.utils.serializers import dump, dump_list

router = APIRouter(prefix="/tasks", tags=["tasks"])


def task_query(db: Session, user: User):
    return db.query(Task).filter(or_(Task.creator_id == user.id, Task.assignee_id == user.id))


def refresh_actual_hours(db: Session, task_id: int | None):
    if not task_id:
        return
    task = db.get(Task, task_id)
    if not task:
        return
    hours = sum(row[0] or 0 for row in db.query(WorkLog.duration_hours).filter(WorkLog.task_id == task_id).all())
    task.actual_hours = round(hours, 2)
    db.add(task)


@router.get("")
def list_tasks(
    keyword: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    project_id: int | None = None,
    page_number: int = Query(1, alias="page", ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = task_query(db, current_user)
    if keyword:
        query = query.filter(or_(Task.title.ilike(f"%{keyword}%"), Task.description.ilike(f"%{keyword}%")))
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    total = query.count()
    items = query.order_by(Task.due_date.asc().nullslast(), Task.updated_at.desc()).offset((page_number - 1) * page_size).limit(page_size).all()
    return page(dump_list(TaskOut, items), total, page_number, page_size)


@router.post("")
def create_task(payload: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    values = payload.model_dump()
    values["assignee_id"] = values.get("assignee_id") or current_user.id
    task = Task(**values, creator_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return ok(dump(TaskOut, task))


@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = task_query(db, current_user).filter(Task.id == task_id).first()
    if not task:
        raise AppError("任务不存在", status_code=404)
    return ok(dump(TaskOut, task))


@router.put("/{task_id}")
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = task_query(db, current_user).filter(Task.id == task_id).first()
    if not task:
        raise AppError("任务不存在", status_code=404)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    if task.status == "completed" and not task.completed_at:
        task.completed_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return ok(dump(TaskOut, task))


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = task_query(db, current_user).filter(Task.id == task_id).first()
    if not task:
        raise AppError("任务不存在", status_code=404)
    db.delete(task)
    db.commit()
    return ok({"deleted": True})


@router.patch("/{task_id}/status")
def patch_task_status(task_id: int, payload: StatusPatch, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = task_query(db, current_user).filter(Task.id == task_id).first()
    if not task:
        raise AppError("任务不存在", status_code=404)
    task.status = payload.status
    task.completed_at = datetime.now(timezone.utc) if payload.status == "completed" else None
    db.add(task)
    db.commit()
    db.refresh(task)
    return ok(dump(TaskOut, task))
