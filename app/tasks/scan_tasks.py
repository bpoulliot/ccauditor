from celery import Celery
from celery.exceptions import Retry
from app.config.settings import settings
from app.database.db import SessionLocal
from app.database.models import CourseScan
from app.scanner.course_scanner import scan_course
from app.progress.redis_progress import (
    init_scan_progress,
    increment_completed,
    increment_failed,
)

celery_app = Celery(
    "ccauditor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)


@celery_app.task(bind=True, max_retries=3)
def scan_course_task(self, course_id, term_id):

    try:

        db = SessionLocal()

        result = scan_course(course_id)

        scan = CourseScan(
            course_id=course_id,
            risk_score=result["risk_score"],
        )

        db.add(scan)
        db.commit()

        increment_completed(term_id)

    except Exception as exc:

        increment_failed(term_id)

        try:
            raise self.retry(exc=exc, countdown=30)
        except Retry:
            raise


@celery_app.task
def scan_term(term_id, courses):

    total_courses = len(courses)

    init_scan_progress(term_id, total_courses)

    for course in courses:

        scan_course_task.delay(course["id"], term_id)