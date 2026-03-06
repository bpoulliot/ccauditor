import redis
import time

from app.config.settings import settings


redis_client = redis.Redis.from_url(settings.REDIS_URL)


LOCK_TTL = 3600


def acquire_term_lock(term_id):

    key = f"scan_lock:{term_id}"

    return redis_client.set(
        key,
        "locked",
        nx=True,
        ex=LOCK_TTL,
    )


def release_term_lock(term_id):

    key = f"scan_lock:{term_id}"

    redis_client.delete(key)