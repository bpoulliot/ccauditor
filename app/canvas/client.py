import requests
import time
import socket
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from canvasapi import Canvas
from app.config.settings import settings
from app.canvas.rate_limiter import canvas_rate_limiter

ACCOUNT_ID = 1

session = None
canvas = None

def _resolve_canvas_host():
    """
    Resolve Canvas hostname once to reduce DNS queries during large scans.
    """
    host = settings.CANVAS_BASE_URL.replace("https://", "").replace("http://", "")
    host = host.split("/")[0]

    ip = socket.gethostbyname(host)

    return host, ip


def _create_session():

    host, ip = _resolve_canvas_host()
    session = requests.Session()

    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )

    adapter = HTTPAdapter(
        pool_connections=50,
        pool_maxsize=50,
        max_retries=retry,
    )

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # Force requests to use resolved IP but preserve Host header
    session.headers.update({
        "Host": host
    })

    session.verify = True

    return session


def canvas_retry(func, retries=3):

    for attempt in range(retries):

        try:
            return func()

        except requests.exceptions.ConnectionError:

            sleep = 2 ** attempt
            print(f"Canvas connection error, retrying in {sleep}s")

            time.sleep(sleep)

    raise


def get_canvas():

    global canvas

    if not settings.CANVAS_BASE_URL or not settings.CANVAS_API_TOKEN:
        raise ValueError("Canvas configuration missing")

    if canvas:
        return canvas

    # ------------------------------------------------
    # HTTP connection pooling
    # ------------------------------------------------

    session = _create_session()

    canvas = Canvas(
        settings.CANVAS_BASE_URL,
        settings.CANVAS_API_TOKEN,
        session=session,
    )

    return canvas


def get_account():

    canvas_rate_limiter.acquire()
    canvas = get_canvas()
    return canvas.get_account(ACCOUNT_ID)


def get_courses_by_term(term_id):
    """
    Return all courses in the account belonging to a specific enrollment term.
    """

    canvas_rate_limiter.acquire()

    account = get_account()

    courses = list(
        canvas_retry(
            lambda: 
                account.get_courses(
                enrollment_term_id=term_id,
                per_page=100,
            )
        )
    )

    # Canvas sometimes returns courses outside the term — enforce filter
    results = []

    for course in courses:

        if getattr(course, "enrollment_term_id", None) == term_id:
            results.append(course)

    return results


def get_course_by_canvas_id(course_id):
    """
    Fetch a single course by Canvas course ID.
    """

    canvas_rate_limiter.acquire()

    canvas = get_canvas()

    return canvas.get_course(course_id)


def get_course_by_sis_id(sis_course_id):
    """
    Fetch a single course by SIS course ID.
    """

    canvas_rate_limiter.acquire()
    canvas = get_canvas()

    return canvas.get_course(f"sis_course_id:{sis_course_id}")