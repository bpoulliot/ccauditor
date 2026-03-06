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
from app.analytics.department import extract_department

from app.observability.metrics import (
    COURSE_SCANS_TOTAL,
    SCAN_DURATION_SECONDS,
    SCAN_FAILURES_TOTAL,
    ACCESSIBILITY_ISSUES_TOTAL,
    BROKEN_LINKS_TOTAL,
    CAPTION_REMEDIATION_HOURS,
    COURSE_RISK_SCORE,
    DEPARTMENT_RISK_SCORE,
    DEPARTMENT_ACCESSIBILITY_ISSUES,
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

    if not acquire_term_lock(term_id):
        print(f"Scan already running for term {term_id}")
        return

    db = SessionLocal()

    try:

        job = ScanJob(term_id=term_id, status="running")
        db.add(job)
        db.commit()

        canvas_courses = get_courses()

        courses = []

        for course in canvas_courses:

            if course.enrollment_term_id == term_id:
                courses.append(course)

        courses = prioritize_courses(courses)

        init_scan_progress(term_id, len(courses))

        for course in courses:
            scan_course_task.delay(course.id, term_id)

    finally:

        release_term_lock(term_id)
        db.close()


@celery_app.task(bind=True, max_retries=3)
def scan_course_task(self, course_id, term_id):

    start_time = time.time()

    db = SessionLocal()

    try:

        if settings.SCAN_INCREMENTAL_ENABLED:

            if not should_scan_course(
                course_id,
                threshold_hours=settings.SCAN_INCREMENTAL_THRESHOLD_HOURS,
            ):
                increment_completed(term_id)
                return

        result = scan_course(course_id)

        risk_score = result.get("risk_score", 0)

        COURSE_SCANS_TOTAL.inc()
        COURSE_RISK_SCORE.labels(course_id=course_id).set(risk_score)

        duration = time.time() - start_time
        SCAN_DURATION_SECONDS.observe(duration)

        department = extract_department(result.get("course_name", ""))

        DEPARTMENT_RISK_SCORE.labels(department=department).set(risk_score)

        for issue in result.get("issues", []):

            ACCESSIBILITY_ISSUES_TOTAL.labels(
                issue_type=issue["type"]
            ).inc()

            DEPARTMENT_ACCESSIBILITY_ISSUES.labels(
                department=department,
                issue_type=issue["type"]
            ).inc()

        BROKEN_LINKS_TOTAL.inc(len(result.get("links", [])))

        CAPTION_REMEDIATION_HOURS.set(
            result["caption_workload"]["remediation_hours"]
        )

        scan_record = CourseScan(
            course_id=course_id,
            risk_score=risk_score,
        )

        db.add(scan_record)
        db.commit()

        increment_completed(term_id)

    except Exception as exc:

        SCAN_FAILURES_TOTAL.inc()
        increment_failed(term_id)

        raise self.retry(exc=exc, countdown=settings.SCAN_RETRY_DELAY)

    finally:

        db.close()