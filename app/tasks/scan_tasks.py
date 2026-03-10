import time

from app.analytics.department import extract_department
from app.canvas.client import (
    get_courses_by_term,
    get_course_by_canvas_id,
    get_course_by_sis_id,
)
from app.canvas.course_prioritizer import prioritize_courses
from app.celery_app import celery_app
from app.config.settings import settings
from app.database.db import SessionLocal
from app.database.models import CourseScan, ScanJob
from app.observability.metrics import (
    ACCESSIBILITY_ISSUES_TOTAL,
    BROKEN_LINKS_TOTAL,
    CAPTION_REMEDIATION_HOURS,
    COURSE_RISK_SCORE,
    COURSE_SCANS_TOTAL,
    DEPARTMENT_ACCESSIBILITY_ISSUES,
    DEPARTMENT_RISK_SCORE,
    SCAN_DURATION_SECONDS,
    SCAN_FAILURES_TOTAL,
)
from app.optimization.incremental_scanner import should_scan_course
from app.progress.redis_progress import (
    increment_completed,
    increment_failed,
    init_scan_progress,
    is_cancelled,
    get_progress,
    clear_progress,
    clear_cancel,
)
from app.progress.scan_lock import acquire_term_lock, release_term_lock
from app.scanner.course_scanner import scan_course


# --------------------------------------------------
# Scan Term Task
# --------------------------------------------------

@celery_app.task(bind=True)
def scan_term(self, term_id=None, canvas_course_id=None, sis_course_id=None):

    lock_id = term_id or canvas_course_id or sis_course_id

    if not acquire_term_lock(lock_id):
        print(f"Scan already running for target {lock_id}")
        return

    db = SessionLocal()

    try:

        job = ScanJob(term_id=term_id, status="running")
        db.add(job)
        db.commit()
        db.refresh(job)

        job_id = str(job.id)

        courses = []

        if canvas_course_id:
            course = get_course_by_canvas_id(canvas_course_id)
            courses = [course]

        elif sis_course_id:
            course = get_course_by_sis_id(sis_course_id)
            courses = [course]

        elif term_id:
            canvas_courses = get_courses_by_term(term_id)
            courses = [c for c in canvas_courses if c.enrollment_term_id == term_id]

        else:
            raise ValueError("No scan target specified")

        courses = prioritize_courses(courses)

        init_scan_progress(job_id, len(courses))

        for course in courses:

            if is_cancelled(job_id):
                break

            scan_course_task.apply_async(
                args=[course.id, job_id],
                queue="scans",
            )

        return job_id

    finally:
        release_term_lock(lock_id)
        db.close()


# --------------------------------------------------
# Scan Course Task
# --------------------------------------------------

@celery_app.task(bind=True, max_retries=3)
def scan_course_task(self, course_id, job_id):

    start_time = time.time()

    db = SessionLocal()

    try:

        # stop immediately if cancelled
        if is_cancelled(job_id):
            return

        if settings.SCAN_INCREMENTAL_ENABLED:

            if not should_scan_course(
                course_id,
                threshold_hours=settings.SCAN_INCREMENTAL_THRESHOLD_HOURS,
            ):
                increment_completed(job_id)
                return

        result = scan_course(course_id)

        # check cancel again after scan
        if is_cancelled(job_id):
            return

        risk_score = result.get("risk_score", 0)

        COURSE_SCANS_TOTAL.inc()
        COURSE_RISK_SCORE.labels(course_id=course_id).set(risk_score)

        duration = time.time() - start_time
        SCAN_DURATION_SECONDS.observe(duration)

        department = extract_department(result.get("course_name", ""))

        DEPARTMENT_RISK_SCORE.labels(department=department).set(risk_score)

        for issue in result.get("issues", []):

            ACCESSIBILITY_ISSUES_TOTAL.labels(issue_type=issue["type"]).inc()

            DEPARTMENT_ACCESSIBILITY_ISSUES.labels(
                department=department,
                issue_type=issue["type"],
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

        increment_completed(job_id)

        # --------------------------------------------------
        # Safe Job Completion Check
        # --------------------------------------------------

        progress = get_progress(job_id)

        if progress:

            finished = progress["completed"] + progress["failed"]

            if finished >= progress["total"]:

                job = db.get(ScanJob, job_id)

                if job and job.status not in ["completed", "cancelled"]:

                    job.status = "completed"
                    db.commit()

                # cleanup Redis progress entry
                clear_progress(job_id)

        progress = get_progress(job_id)

        if progress and (progress["completed"] + progress["failed"]) >= progress["total"]:

            job = db.get(ScanJob, job_id)

            if job:
                job.status = "completed"
                db.commit()

            clear_progress(job_id)
            clear_cancel(job_id)

    except Exception as exc:

        db.rollback()

        SCAN_FAILURES_TOTAL.inc()

        increment_failed(job_id)

        raise self.retry(
            exc=exc,
            countdown=settings.SCAN_RETRY_DELAY,
        )

    finally:

        db.close()