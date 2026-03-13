import time
from sqlalchemy.exc import IntegrityError

from app.config.runtime_config import get_scan_timeout_minutes
from app.analytics.department import extract_department
from app.scanner.course_scanner import scan_course
from app.scanner.incremental_scanner import should_scan_course
from app.canvas.course_prioritizer import prioritize_courses
from app.celery_app import celery_app
from app.config.settings import settings
from app.database.db import SessionLocal
from app.database.models import Course, CourseScan, ScanJob, Term
from app.progress.scan_lock import acquire_term_lock, release_term_lock
from app.progress.redis_progress import (
    increment_completed,
    increment_failed,
    init_scan_progress,
    is_cancelled,
)
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
from app.canvas.client import (
    get_courses_by_term,
    get_course_by_canvas_id,
    get_course_by_sis_id,
)

from app.canvas.content_export import (
    start_course_export,
    wait_for_export,
    download_export,
    extract_export,
    scan_export_directory,
    scan_export_html,
    scan_export_files
)



# ---------------------------------------------------------
# TERM SCAN TASK
# ---------------------------------------------------------

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

        # --------------------------------------------------
        # Ensure term exists in DB
        # --------------------------------------------------

        if term_id:

            existing_term = db.query(Term).get(term_id)

            if not existing_term:
                db.add(Term(id=term_id))
                db.commit()

        # --------------------------------------------------
        # Determine courses
        # --------------------------------------------------

        courses = []

        if canvas_course_id:

            course = get_course_by_canvas_id(canvas_course_id)
            courses = [course]

        elif sis_course_id:

            course = get_course_by_sis_id(sis_course_id)
            courses = [course]

        elif term_id:

            canvas_courses = get_courses_by_term(term_id)

            for c in canvas_courses:

                courses.append(
                    {
                        "id": c.id,
                        "name": getattr(c, "name", ""),
                        "sis_id": getattr(c, "sis_course_id", None),
                        "term_id": getattr(c, "enrollment_term_id", term_id),
                    }
                )

        else:

            raise ValueError("No scan target specified")

        courses = prioritize_courses(courses)

        init_scan_progress(job_id, len(courses))

        # --------------------------------------------------
        # Store courses in DB
        # --------------------------------------------------

        for c in courses:

            existing = db.query(Course).get(c["id"])

            if not existing:

                try:

                    db.add(
                        Course(
                            id=c["id"],
                            name=c["name"],
                            sis_id=c["sis_id"],
                            term_id=c["term_id"],
                        )
                    )

                except IntegrityError:
                    db.rollback()

        db.commit()

        # --------------------------------------------------
        # Dispatch Celery scan tasks
        # --------------------------------------------------

        for c in courses:

            scan_course_task.apply_async(
                args=[c, job_id],
                queue="scans",
            )

            time.sleep(0.05)

        job.status = "queued"
        db.commit()

        return job_id

    finally:

        release_term_lock(lock_id)
        db.close()


# ---------------------------------------------------------
# COURSE SCAN TASK
# ---------------------------------------------------------

@celery_app.task(bind=True, max_retries=3)
def scan_course_task(self, course_payload, job_id):

    start_time = time.time()

    db = SessionLocal()

    try:

        if is_cancelled(job_id):
            print(f"Scan job {job_id} cancelled")
            return

        course_id = course_payload["id"]

        # --------------------------------------------------
        # Incremental scan skip
        # --------------------------------------------------

        if settings.SCAN_INCREMENTAL_ENABLED:

            if not should_scan_course(
                course_id,
                threshold_hours=settings.SCAN_INCREMENTAL_THRESHOLD_HOURS,
            ):
                increment_completed(job_id)
                return

        # --------------------------------------------------
        # Run scanner
        # --------------------------------------------------

        result = scan_course(course_payload)

        risk_score = result.get("risk_score", 0)

        # --------------------------------------------------
        # Metrics
        # --------------------------------------------------

        COURSE_SCANS_TOTAL.inc()

        COURSE_RISK_SCORE.observe(risk_score)

        duration = time.time() - start_time
        SCAN_DURATION_SECONDS.observe(duration)

        department = extract_department(course_payload.get("name", ""))

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

        # --------------------------------------------------
        # Save scan result
        # --------------------------------------------------

        scan_record = CourseScan(
            course_id=course_id,
            risk_score=risk_score,
        )

        db.add(scan_record)
        db.commit()

        increment_completed(job_id)

    except Exception as exc:

        SCAN_FAILURES_TOTAL.inc()

        increment_failed(job_id)

        # Stop retrying after max_retries
        if self.request.retries >= self.max_retries:

            print(f"[SCAN FAILURE] Course {course_id} failed after max retries: {exc}")

            scan_record = CourseScan(
                course_id=course_id,
                risk_score=0,
                error=str(exc)
            )

            db.add(scan_record)
            db.commit()

            return {
                "course_id": course_id,
                "status": "failed",
                "error": str(exc),
            }

        raise self.retry(
            exc=exc,
            countdown=settings.SCAN_RETRY_DELAY,
        )

    finally:

        db.close()

def queue_course_scan(course_id):
    scan_course_task.delay(course_id)