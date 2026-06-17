#!/usr/bin/env sh
set -eu

python - <<'PY'
import os
import time
from sqlalchemy import create_engine, text

url = os.environ.get("DATABASE_URL", "postgresql+psycopg://worklog:worklog@postgres:5432/worklog")
if url.startswith("postgresql://"):
    url = url.replace("postgresql://", "postgresql+psycopg://", 1)

for attempt in range(60):
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("select 1"))
        print("database is ready")
        break
    except Exception as exc:
        print(f"waiting for database: {exc}")
        time.sleep(2)
else:
    raise SystemExit("database is not ready")
PY

alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
