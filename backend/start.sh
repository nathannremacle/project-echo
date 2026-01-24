#!/bin/sh
# Start script for DigitalOcean App Platform, Render, Heroku, etc.
# Uses PORT from the environment (default 8080).
exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8080}"
