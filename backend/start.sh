#!/bin/sh
set -e

# Start local Redis server in background if REDIS_URL is local or unset
if [ -z "$REDIS_URL" ] || echo "$REDIS_URL" | grep -q "localhost\|127.0.0.1"; then
    echo "Starting internal Redis server..."
    redis-server --daemonize yes
fi

# Run database migrations and seed
echo "Running database migrations..."
alembic upgrade head
echo "Seeding initial database roles and permissions..."
python -m app.db.seed

# Start Celery worker in background (concurrency 2 to fit within Render free tier RAM)
echo "Starting Celery background worker..."
celery -A app.workers.celery_app worker --loglevel=info --concurrency=2 --detach --pidfile=/tmp/celery.pid --logfile=/tmp/celery.log || true

# Start FastAPI web server on dynamic Render PORT
echo "Starting FastAPI web server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
