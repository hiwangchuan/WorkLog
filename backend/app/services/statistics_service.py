from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import OvertimeLog, Project, Task, WorkLog


def date_range(days: int = 7) -> tuple[date, date]:
    end = date.today()
    return end - timedelta(days=days - 1), end


def dashboard_summary(db: Session, user_id: int) -> dict:
    today = date.today()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())
    todo_today = db.query(Task).filter(Task.creator_id == user_id, Task.status != "completed").count()
    completed_today = (
        db.query(Task).filter(Task.creator_id == user_id, Task.status == "completed", func.date(Task.completed_at) == today).count()
    )
    completed_week = (
        db.query(Task).filter(Task.creator_id == user_id, Task.status == "completed", func.date(Task.completed_at) >= week_start).count()
    )
    month_hours = (
        db.query(func.coalesce(func.sum(WorkLog.duration_hours), 0))
        .filter(WorkLog.user_id == user_id, WorkLog.work_date >= month_start)
        .scalar()
    )
    overtime_hours = (
        db.query(func.coalesce(func.sum(OvertimeLog.duration_hours), 0))
        .filter(OvertimeLog.user_id == user_id, OvertimeLog.overtime_date >= month_start)
        .scalar()
    )
    overdue = (
        db.query(Task)
        .filter(Task.creator_id == user_id, Task.status.notin_(["completed", "cancelled"]), Task.due_date < today)
        .count()
    )
    recent_work_logs = (
        db.query(WorkLog).filter(WorkLog.user_id == user_id).order_by(WorkLog.work_date.desc(), WorkLog.id.desc()).limit(6).all()
    )
    today_tasks = (
        db.query(Task)
        .filter(Task.creator_id == user_id, Task.status.notin_(["completed", "cancelled"]))
        .order_by(Task.due_date.asc().nullslast(), Task.id.desc())
        .limit(8)
        .all()
    )
    return {
        "today_todo": todo_today,
        "today_completed": completed_today,
        "week_completed": completed_week,
        "month_work_hours": float(month_hours or 0),
        "month_overtime_hours": float(overtime_hours or 0),
        "overdue_tasks": overdue,
        "today_tasks": today_tasks,
        "recent_work_logs": recent_work_logs,
    }


def work_hours_trend(db: Session, user_id: int, days: int = 7) -> list[dict]:
    start, end = date_range(days)
    rows = (
        db.query(WorkLog.work_date, func.coalesce(func.sum(WorkLog.duration_hours), 0))
        .filter(WorkLog.user_id == user_id, WorkLog.work_date >= start, WorkLog.work_date <= end)
        .group_by(WorkLog.work_date)
        .all()
    )
    mapping = {row[0].isoformat(): float(row[1] or 0) for row in rows}
    return [{"date": (start + timedelta(days=i)).isoformat(), "hours": mapping.get((start + timedelta(days=i)).isoformat(), 0)} for i in range(days)]


def overtime_trend(db: Session, user_id: int, days: int = 30) -> list[dict]:
    start, end = date_range(days)
    rows = (
        db.query(OvertimeLog.overtime_date, func.coalesce(func.sum(OvertimeLog.duration_hours), 0))
        .filter(OvertimeLog.user_id == user_id, OvertimeLog.overtime_date >= start, OvertimeLog.overtime_date <= end)
        .group_by(OvertimeLog.overtime_date)
        .all()
    )
    return [{"date": row[0].isoformat(), "hours": float(row[1] or 0)} for row in rows]


def task_status(db: Session, user_id: int) -> list[dict]:
    rows = db.query(Task.status, func.count(Task.id)).filter(Task.creator_id == user_id).group_by(Task.status).all()
    return [{"name": row[0], "value": row[1]} for row in rows]


def project_hours(db: Session, user_id: int) -> list[dict]:
    rows = (
        db.query(Project.name, func.coalesce(func.sum(WorkLog.duration_hours), 0))
        .join(WorkLog, WorkLog.project_id == Project.id)
        .filter(WorkLog.user_id == user_id)
        .group_by(Project.name)
        .all()
    )
    return [{"name": row[0], "hours": float(row[1] or 0)} for row in rows]


def work_type_ratio(db: Session, user_id: int) -> list[dict]:
    rows = (
        db.query(WorkLog.work_type, func.coalesce(func.sum(WorkLog.duration_hours), 0))
        .filter(WorkLog.user_id == user_id)
        .group_by(WorkLog.work_type)
        .all()
    )
    return [{"name": row[0], "value": float(row[1] or 0)} for row in rows]
