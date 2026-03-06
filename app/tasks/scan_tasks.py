from celery import Celery
from celery.exceptions import Retry

from app.config.settings import settings
from app.database.db import SessionLocal
from app.database.models import CourseScan, ScanJob

from app.canvas.client import get_courses
from app.canvas.course_prioritizer import prioritize_courses

from app.scanner.course_scanner import scan_course

from app.progress.redis_progress import (
    init_scan_progress,
    increment_completed,
    increment_failed,
)

from app.optimization.incremental_scanner import should_scan_course


celery_app = Celery(
    "ccauditor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)


celery_app.conf.update(
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
)


@celery_app.task
def scan_term(term_id):

    """
    Launch a full term scan.
    """

    db = SessionLocal()

    job = ScanJob(term_id=term_id, status="running")
    db.add(job)
    db.commit()

    # Fetch courses from Canvas
    canvas_courses = get_courses()

    courses = []

    for course in canvas_courses:

        if course.enrollment_term_id == term_id:

            courses.append({
                "id": course.id,
                "video_count": 0,
                "file_count": 0,
                "page_count": 0,
            })

    # Prioritize courses by risk signals
    courses = prioritize_courses(courses)

    total_courses = len(courses)

    init_scan_progress(term_id, total_courses)

    for course in courses:

        scan_course_task.delay(course["id"], term_id)

    job.status = "queued"
    db.commit()


@celery_app.task(bind=True, max_retries=3)
def scan_course_task(self, course_id, term_id):

    """
    Scan a single Canvas course.
    """

    try:

        # Skip if incremental scan determines course unchanged
        if settings.SCAN_INCREMENTAL_ENABLED:

            if not should_scan_course(
                course_id,
                threshold_hours=settings.SCAN_INCREMENTAL_THRESHOLD_HOURS,
            ):
                increment_completed(term_id)
                return

        db = SessionLocal()

        result = scan_course(course_id)

        risk_score = result.get("risk_score", 0)

        scan_record = CourseScan(
            course_id=course_id,
            risk_score=risk_score,
        )

        db.add(scan_record)
        db.commit()

        increment_completed(term_id)

    except Exception as exc:

        increment_failed(term_id)

        try:

            raise self.retry(
                exc=exc,
                countdown=settings.SCAN_RETRY_DELAY,
            )

        except Retry:

            raise