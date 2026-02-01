#!/bin/sh
# Start script for DigitalOcean App Platform, Render, Heroku, etc.
# Uses PORT from the environment (default 8080).
#
# Run from backend dir. PYTHONPATH: (1) backend (for backend/shared) so it works
# when Source=/backend; (2) repo root (for shared at root) when Source=/.
cd "$(dirname "$0")"
ROOT="$(cd .. 2>/dev/null && pwd)"
export PYTHONPATH="$(pwd):${ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

# Run migrations before starting (idempotent)
alembic upgrade head 2>/dev/null || true

exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8080}"
