from fastapi import APIRouter

from app.api import attachments, ai, auth, dashboard, health, overtime_logs, projects, reports, settings, statistics, tasks, teams, work_logs

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(tasks.router)
api_router.include_router(work_logs.router)
api_router.include_router(attachments.router)
api_router.include_router(overtime_logs.router)
api_router.include_router(projects.router)
api_router.include_router(ai.router)
api_router.include_router(reports.router)
api_router.include_router(statistics.router)
api_router.include_router(settings.router)
api_router.include_router(teams.router)
