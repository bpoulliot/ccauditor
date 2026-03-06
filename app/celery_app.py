from celery import Celery
from app.config.settings import settings


celery_app = Celery(
    "ccauditor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)


celery_app.conf.update(

    # Task execution limits
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,

    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Retry behavior
    task_acks_late=True,
    worker_prefetch_multiplier=1,

    # Queue definitions
    task_default_queue="scans",

    task_routes={
        "app.tasks.scan_tasks.*": {"queue": "scans"},
        "app.ai.*": {"queue": "ai"},
        "app.hygiene.*": {"queue": "hygiene"},
    },

    # Worker reliability
    worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
)