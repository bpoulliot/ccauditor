from canvasapi import Canvas

from app.canvas.pagination import paginate
from app.config.settings import settings

if not settings.CANVAS_BASE_URL or not settings.CANVAS_API_TOKEN:
    raise RuntimeError("Canvas configuration missing: CANVAS_BASE_URL or CANVAS_API_TOKEN")

def get_canvas():
    return Canvas(settings.CANVAS_BASE_URL, settings.CANVAS_API_TOKEN)

def get_courses_by_term(term_id):
    canvas = get_canvas()
    account = canvas.get_account(1)
    return account.get_courses(enrollment_term_id=term_id)

def get_course_by_canvas_id(course_id):
    canvas = get_canvas()
    return canvas.get_course(course_id)

def get_course_by_sis_id(sis_id):
    canvas = get_canvas()
    return canvas.get_course(f"sis_course_id:{sis_id}")