from celery import Celery

from app.config.settings import settings
from app.database.init_db import init_db
from app.observability.metrics_endpoint import start_metrics_server

# Ensure DB exists before workers start
init_db()

celery_app = Celery(
    "ccauditor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Load Celery configuration
celery_app.config_from_object("app.celeryconfig")

# Automatically discover all tasks in these packages
celery_app.autodiscover_tasks(
    [
        "app.tasks.scan_tasks",
        "app.observability.tasks",
    ]
)

start_metrics_server()

# Periodic jobs
celery_app.conf.beat_schedule = {
    "update-queue-metrics": {
        "task": "app.observability.tasks.update_queue_metrics_task",
        "schedule": 30.0,
    }
}