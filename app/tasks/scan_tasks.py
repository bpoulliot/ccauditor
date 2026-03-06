from celery import Celery
from app.config.settings import settings
from app.database.db import SessionLocal
from app.database.models import CourseScan, ScanJob
from app.scanner.course_scanner import scan_course

celery_app = Celery(
    "ccauditor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

@celery_app.task
def scan_term(term_id):

    db = SessionLocal()

    job = ScanJob(term_id=term_id, status="running")
    db.add(job)
    db.commit()

    courses = []  # placeholder; will load via Canvas client

    for course in courses:
        scan_course.delay(course.id)

    job.status = "queued"
    db.commit()


@celery_app.task
def scan_course_task(course_id):

    db = SessionLocal()

    result = scan_course(course_id)

    scan = CourseScan(course_id=course_id, risk_score=result["risk_score"])

    db.add(scan)
    db.commit()