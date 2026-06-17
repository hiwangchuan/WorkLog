from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import ok
from app.models import OvertimeLog, Task, User, WorkLog
from app.services.statistics_service import overtime_trend, project_hours, task_status, work_hours_trend, work_type_ratio

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/tasks")
def tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ok({"status": task_status(db, current_user.id)})


@router.get("/work-hours")
def work_hours(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ok({"trend": work_hours_trend(db, current_user.id, days=30)})


@router.get("/overtime")
def overtime(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (
        db.query(OvertimeLog.overtime_type, func.coalesce(func.sum(OvertimeLog.duration_hours), 0))
        .filter(OvertimeLog.user_id == current_user.id)
        .group_by(OvertimeLog.overtime_type)
        .all()
    )
    return ok({"trend": overtime_trend(db, current_user.id, days=30), "types": [{"name": r[0], "value": float(r[1] or 0)} for r in rows]})


@router.get("/projects")
def projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ok(project_hours(db, current_user.id))


@router.get("/work-types")
def work_types(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ok(work_type_ratio(db, current_user.id))


@router.get("/calendar-heatmap")
def heatmap(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (
        db.query(WorkLog.work_date, func.coalesce(func.sum(WorkLog.duration_hours), 0))
        .filter(WorkLog.user_id == current_user.id)
        .group_by(WorkLog.work_date)
        .all()
    )
    return ok([{"date": row[0].isoformat(), "value": float(row[1] or 0)} for row in rows])
