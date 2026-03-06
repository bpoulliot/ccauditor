import time
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

from app.progress.scan_lock import (
    acquire_term_lock,
    release_term_lock,
)

from app.optimization.incremental_scanner import should_scan_course

from app.observability.metrics import (
    SCAN_COUNTER,
    SCAN_DURATION,
    SCAN_FAILURES,
)


celery_app = Celery(
    "ccauditor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)


celery_app.conf.update(
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
)


@celery_app.task(bind=True)
def scan_term(self, term_id):
    """
    Launch a full term scan with distributed job locking.
    Prevents duplicate scans for the same term.
    """

    # Acquire distributed Redis lock
    if not acquire_term_lock(term_id):
        print(f"Scan already running for term {term_id}")
        return

    db = SessionLocal()

    try:

        # Create job record
        job = ScanJob(term_id=term_id, status="running")
        db.add(job)
        db.commit()

        canvas_courses = get_courses()

        courses = []

        for course in canvas_courses:

            if course.enrollment_term_id == term_id:

                courses.append(
                    {
                        "id": course.id,
                        "video_count": 0,
                        "file_count": 0,
                        "page_count": 0,
                    }
                )

        # Prioritize high-risk courses first
        courses = prioritize_courses(courses)

        total_courses = len(courses)

        init_scan_progress(term_id, total_courses)

        for course in courses:

            scan_course_task.delay(course["id"], term_id)

        job.status = "queued"
        db.commit()

    except Exception as e:

        job.status = "failed"
        db.commit()

        raise e

    finally:

        release_term_lock(term_id)
        db.close()


@celery_app.task(bind=True, max_retries=3)
def scan_course_task(self, course_id, term_id):
    """
    Scan a single Canvas course safely with retries and metrics.
    """

    start_time = time.time()

    db = SessionLocal()

    try:

        # Skip course if incremental scanning enabled
        if settings.SCAN_INCREMENTAL_ENABLED:

            if not should_scan_course(
                course_id,
                threshold_hours=settings.SCAN_INCREMENTAL_THRESHOLD_HOURS,
            ):

                increment_completed(term_id)
                return

        # Run scanner
        result = scan_course(course_id)

        risk_score = result.get("risk_score", 0)

        scan_record = CourseScan(
            course_id=course_id,
            risk_score=risk_score,
        )

        db.add(scan_record)
        db.commit()

        # Metrics
        SCAN_COUNTER.inc()

        duration = time.time() - start_time
        SCAN_DURATION.observe(duration)

        increment_completed(term_id)

    except Exception as exc:

        SCAN_FAILURES.inc()

        increment_failed(term_id)

        try:

            raise self.retry(
                exc=exc,
                countdown=settings.SCAN_RETRY_DELAY,
            )

        except Retry:

            raise

    finally:

        db.close()