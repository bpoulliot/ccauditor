import redis

from app.config.settings import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)


LOCK_TTL = 3600


def acquire_term_lock(lock_id):

    key = f"scan_lock:{lock_id}"

    return redis_client.set(
        key,
        "1",
        nx=True,
        ex=3600  # auto release after 1 hour
    )


def release_term_lock(term_id):

    key = f"scan_lock:{term_id}"

    redis_client.delete(key)
