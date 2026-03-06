import redis
from app.config.settings import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)


def init_scan_progress(term_id, total_courses):

    key = f"scan_progress:{term_id}"

    redis_client.hset(
        key,
        mapping={
            "total": total_courses,
            "completed": 0,
            "failed": 0,
        },
    )


def increment_completed(term_id):

    key = f"scan_progress:{term_id}"

    redis_client.hincrby(key, "completed", 1)


def increment_failed(term_id):

    key = f"scan_progress:{term_id}"

    redis_client.hincrby(key, "failed", 1)


def get_progress(term_id):

    key = f"scan_progress:{term_id}"

    data = redis_client.hgetall(key)

    if not data:
        return None

    return {
        "total": int(data[b"total"]),
        "completed": int(data[b"completed"]),
        "failed": int(data[b"failed"]),
    }