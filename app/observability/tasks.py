from app.celery_app import celery_app
from app.observability.queue_metrics import update_queue_metrics


@celery_app.task
def update_queue_metrics_task():

    update_queue_metrics()
