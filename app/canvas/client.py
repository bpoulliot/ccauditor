from canvasapi import Canvas
from app.config.settings import settings
from app.canvas.pagination import paginate

canvas = Canvas(settings.CANVAS_BASE_URL, settings.CANVAS_API_TOKEN)


def get_courses():

    courses = paginate(canvas.get_courses())

    return courses