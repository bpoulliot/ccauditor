from datetime import datetime, timedelta

from app.database.db import SessionLocal
from app.database.models import CourseScan


def should_scan_course(course_id, threshold_hours=24):

    db = SessionLocal()

    last_scan = (
        db.query(CourseScan)
        .filter(CourseScan.course_id == course_id)
        .order_by(CourseScan.scan_date.desc())
        .first()
    )

    if not last_scan:
        return True

    if datetime.utcnow() - last_scan.scan_date > timedelta(hours=threshold_hours):
        return True

    return False
