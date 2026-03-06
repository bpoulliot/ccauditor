import os
import pytest
from canvasapi import Canvas


url = os.getenv("CANVAS_BASE_URL")
token = os.getenv("CANVAS_API_TOKEN")


@pytest.mark.skipif(
    not url or not token,
    reason="Canvas credentials not available",
)
def test_canvas_connection():

    canvas = Canvas(url, token)

    user = canvas.get_current_user()

    assert user is not None