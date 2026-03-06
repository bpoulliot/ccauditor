from app.database.db import SessionLocal
from app.database.models import CourseScan


def get_institution_metrics():

    db = SessionLocal()

    scans = db.query(CourseScan).all()

    total_courses = len(scans)

    avg_risk = 0

    if scans:
        avg_risk = sum(s.risk_score for s in scans) / total_courses

    return {
        "courses_scanned": total_courses,
        "average_risk_score": avg_risk,
    }