import os
from canvasapi import Canvas


def test_canvas_connection():

    url = os.getenv("CANVAS_BASE_URL")
    token = os.getenv("CANVAS_API_TOKEN")

    canvas = Canvas(url, token)

    user = canvas.get_current_user()

    assert user is not None