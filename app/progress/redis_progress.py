import redis

from app.config.settings import settings

# Redis connection
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def progress_key(job_id):
    """
    Standardized Redis key for scan progress.
    """
    return f"scan_progress:{job_id}"


def cancel_key(job_id):
    """
    Redis key used to signal cancellation to workers.
    """
    return f"scan_cancel:{job_id}"


def init_scan_progress(job_id, total_courses):
    """
    Initialize scan progress in Redis.
    """
    key = progress_key(job_id)

    redis_client.hset(
        key,
        mapping={
            "total": total_courses,
            "completed": 0,
            "failed": 0,
        },
    )


def get_progress(job_id):
    """
    Retrieve scan progress from Redis.
    """
    key = progress_key(job_id)

    progress = redis_client.hgetall(key)

    if not progress:
        return None

    return {
        "total": int(progress.get("total", 0)),
        "completed": int(progress.get("completed", 0)),
        "failed": int(progress.get("failed", 0)),
    }


def increment_completed(job_id):
    """
    Increment completed course count.
    """
    redis_client.hincrby(progress_key(job_id), "completed", 1)


def increment_failed(job_id):
    """
    Increment failed course count.
    """
    redis_client.hincrby(progress_key(job_id), "failed", 1)


def clear_progress(job_id):
    """
    Remove progress entry from Redis.
    """
    redis_client.delete(progress_key(job_id))


def set_cancelled(job_id):
    """
    Signal to workers that a job should stop.
    """
    redis_client.set(cancel_key(job_id), "1")


def is_cancelled(job_id):
    """
    Check if a scan job has been cancelled.
    """
    return redis_client.exists(cancel_key(job_id)) == 1


def clear_cancel(job_id):
    """
    Remove cancel flag after job completion.
    """
    redis_client.delete(cancel_key(job_id))