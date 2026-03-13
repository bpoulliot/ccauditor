from canvasapi import Canvas

from app.config.settings import settings
from app.canvas.rate_limiter import canvas_rate_limiter
from app.canvas.api import get_canvas, canvas_retry

def get_account():

    canvas = get_canvas()
    canvas_rate_limiter.acquire()
    return canvas_retry(lambda: canvas.get_account(settings.ACCOUNT_ID))


def get_course(course_id):

    canvas = get_canvas()
    canvas_rate_limiter.acquire()
    return canvas_retry(lambda: canvas.get_course(course_id))

def get_courses_by_term(term_id):

    account = get_account()
    canvas_rate_limiter.acquire()
    courses = list(
        canvas_retry(
            lambda: 
                account.get_courses(
                enrollment_term_id=term_id,
                per_page=100,
                with_enrollments=True,
                published=True,
                blueprint=False,
            )
        )
    )
    return results

def get_course_by_canvas_id(course_id):

    canvas = get_canvas()
    canvas_rate_limiter.acquire()
    return canvas.get_course(course_id)

def get_course_by_sis_id(sis_course_id):

    canvas = get_canvas()
    canvas_rate_limiter.acquire()
    return canvas.get_course(f"sis_course_id:{sis_course_id}")

def get_enrollment_terms():

    canvas = Canvas(settings.CANVAS_BASE_URL, settings.CANVAS_API_TOKEN)
    account = canvas.get_account(1)

    canvas_rate_limiter.acquire()
    terms = list(
        canvas_retry(
            lambda: account.get_enrollment_terms(per_page=100)
        )       
    )

    results = []

    for term in terms:

        if term.id in settings.excluded_term_ids():
            continue

        sis_id = getattr(term, "sis_term_id", None)

        results.append({
            "id": term.id,
            "name": term.name,
            "sis_id": sis_id or ""
        })

    # sort descending by SIS ID
    return sorted(
        results,
        key=lambda t: getattr(t, "sis_term_id", "") or "",
        reverse=True,
    )