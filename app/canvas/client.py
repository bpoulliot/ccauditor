from canvasapi import Canvas
from app.config.settings import settings

canvas = Canvas(settings.CANVAS_BASE_URL, settings.CANVAS_API_TOKEN)


def get_courses():
    return canvas.get_courses()