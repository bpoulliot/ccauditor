import time
from canvasapi import Canvas
from app.config.settings import settings
import random

_canvas = None


def get_canvas():
    global _canvas

    if _canvas:
        return _canvas

    _canvas = Canvas(
        settings.CANVAS_BASE_URL,
        settings.CANVAS_API_TOKEN,
    )

    return _canvas

    return _canvas


def canvas_retry(func, retries=5):
    last_exception = None

    for attempt in range(retries):
        try:
            canvas_rate_limiter.acquire()
            return func()

        except Exception as e:
            last_exception = e
            wait = 2 ** attempt + random.random()
            print(f"Canvas retry {attempt+1}/{retries} in {wait}s: {e}")
            time.sleep(wait) 

    raise last_exception