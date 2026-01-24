#!/bin/sh
# Start script for DigitalOcean App Platform, Render, Heroku, etc.
# Uses PORT from the environment (default 8080).
#
# Ensure we run from the backend dir and that the repo root (parent of backend)
# is on PYTHONPATH so the 'shared' package can be imported.
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8080}"
