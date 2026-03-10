#!/bin/sh
set -e

echo "Waiting for dependencies..."
python /app/scripts/wait_for_dependencies.py

echo "Starting Celery scheduler..."
exec celery -A app.celery_app beat