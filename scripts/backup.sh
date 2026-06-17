#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${1:-$ROOT_DIR/.env}"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$ROOT_DIR/data/backups/$STAMP"

cd "$ROOT_DIR"
mkdir -p "$BACKUP_DIR"

if ! docker compose --env-file "$ENV_FILE" ps -q postgres >/dev/null 2>&1; then
  printf 'backup_skipped=no_postgres_container\n'
  rmdir "$BACKUP_DIR" 2>/dev/null || true
  exit 0
fi

if ! docker compose --env-file "$ENV_FILE" exec -T postgres pg_isready -U worklog -d worklog >/dev/null 2>&1; then
  printf 'backup_skipped=postgres_not_ready\n'
  rmdir "$BACKUP_DIR" 2>/dev/null || true
  exit 0
fi

docker compose --env-file "$ENV_FILE" exec -T postgres pg_dump -U worklog worklog > "$BACKUP_DIR/worklog.sql"
tar -czf "$BACKUP_DIR/files.tgz" data/uploads data/exports data/certs 2>/dev/null || true

printf 'backup_dir=%s\n' "$BACKUP_DIR"
