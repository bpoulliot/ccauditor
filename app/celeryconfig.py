from app.config.settings import settings
from kombu import Exchange, Queue

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
task_routes = {
    "app.tasks.scan_tasks.scan_term": {"queue": "scans"},
    "app.tasks.scan_tasks.scan_course_task": {"queue": "scans"},
    "app.observability.tasks.update_queue_metrics_task": {"queue": "hygiene"},
}

task_queues = (
    Queue("scans", Exchange("scans"), routing_key="scans"),
    Queue("ai", Exchange("ai"), routing_key="ai"),
    Queue("hygiene", Exchange("hygiene"), routing_key="hygiene"),
)

# Serialization
task_serializer="json"
result_serializer="json"
accept_content=["json"]

# Queue definitions
task_default_queue="scans"