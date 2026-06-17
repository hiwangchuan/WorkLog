from fastapi import APIRouter
from redis import Redis
from sqlalchemy import text

from app import __version__
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.responses import ok

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    database = "ok"
    redis_status = "ok"
    try:
        with SessionLocal() as db:
            db.execute(text("select 1"))
    except Exception:
        database = "error"
    try:
        client = Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1)
        client.ping()
    except Exception:
        redis_status = "error"
    return ok({"status": "ok" if database == "ok" else "degraded", "database": database, "redis": redis_status, "version": __version__})
