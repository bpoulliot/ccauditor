from app.celery_app import celery_app
import redis

from app.config.settings import settings
from app.observability.metrics import REDIS_QUEUE_LENGTH

redis_client = redis.Redis.from_url(settings.REDIS_URL)

def update_queue_metrics():

    for queue in ["scans", "ai", "hygiene"]:

        try:
            size = redis_client.llen(f"celery:{queue}")
        except Exception:
            size = 0

        REDIS_QUEUE_LENGTH.labels(queue=queue).set(size)

@celery_app.task
def update_queue_metrics_task():

    update_queue_metrics()