#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${1:-$ROOT_DIR/.env}"

cd "$ROOT_DIR"

"$ROOT_DIR/scripts/backup.sh" "$ENV_FILE"

docker compose --env-file "$ENV_FILE" build
docker compose --env-file "$ENV_FILE" up -d --remove-orphans
docker compose --env-file "$ENV_FILE" exec -T backend alembic upgrade head
docker compose --env-file "$ENV_FILE" ps
