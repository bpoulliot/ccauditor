from app.config.settings import settings

# Celery worker lifecycle
worker_max_tasks_per_child = 100
worker_prefetch_multiplier = 1

# Task reliability
task_acks_late = True
broker_connection_retry_on_startup = True

# Task execution limits
task_time_limit = settings.CELERY_TASK_TIME_LIMIT
task_soft_time_limit = settings.CELERY_TASK_SOFT_TIME_LIMIT
worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD

# Optional routing example
task_routes={
    "app.tasks.scan_tasks.*": {"queue": "scans"},
    "app.ai.*": {"queue": "ai"},
    "app.hygiene.*": {"queue": "hygiene"},
}

# Serialization
task_serializer="json"
result_serializer="json"
accept_content=["json"]

# Queue definitions
task_default_queue="scans"