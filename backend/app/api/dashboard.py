from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import ok
from app.models import User
from app.services.statistics_service import dashboard_summary, overtime_trend, project_hours, task_status, work_hours_trend
from app.utils.serializers import dump_list
from app.schemas import TaskOut, WorkLogOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = dashboard_summary(db, current_user.id)
    data["today_tasks"] = dump_list(TaskOut, data["today_tasks"])
    data["recent_work_logs"] = dump_list(WorkLogOut, data["recent_work_logs"])
    return ok(data)


@router.get("/work-hours-trend")
def work_hours(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ok(work_hours_trend(db, current_user.id, days=7))


@router.get("/task-status")
def statuses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ok(task_status(db, current_user.id))


@router.get("/project-hours")
def project_distribution(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ok(project_hours(db, current_user.id))


@router.get("/overtime-trend")
def overtime(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ok(overtime_trend(db, current_user.id, days=30))
