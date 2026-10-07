"""
Celery application instance.

Run a worker with:
    celery -A app.workers.celery_app worker --loglevel=info

Actual PDF/OCR/AI task functions live in separate modules under this
package (added in Phase 9 — Core PDF Engine) and get registered via
`include=[...]` below as they're built, e.g. "app.workers.tasks.pdf_tasks".
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "pdf360",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks.pdf_tasks",
        "app.workers.tasks.conversion_tasks",
        "app.workers.tasks.security_tasks",
        "app.workers.tasks.page_ops_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
