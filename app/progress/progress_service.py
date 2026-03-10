from app.progress.redis_progress import get_progress


def calculate_progress(job_id):
    """
    Retrieve scan progress for a job from Redis and compute
    a progress ratio usable by the UI.
    """

    if not job_id:
        return None

    progress = get_progress(job_id)

    if not progress:
        return None

    total = progress.get("total", 0)
    completed = progress.get("completed", 0)
    failed = progress.get("failed", 0)

    progress_ratio = 0

    if total > 0:
        progress_ratio = completed / total

    return {
        "progress": progress_ratio,
        "total": total,
        "completed": completed,
        "failed": failed,
    }