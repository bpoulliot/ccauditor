from app.progress.redis_progress import get_progress


def calculate_progress(term_id):

    data = get_progress(term_id)

    if not data:
        return None

    total = data["total"]
    completed = data["completed"]
    failed = data["failed"]

    progress = 0

    if total > 0:
        progress = (completed + failed) / total

    return {
        "total": total,
        "completed": completed,
        "failed": failed,
        "progress": progress,
    }