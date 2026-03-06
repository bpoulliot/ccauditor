import time
import requests


def safe_request(request_func, *args, **kwargs):

    retries = 5

    for attempt in range(retries):

        response = request_func(*args, **kwargs)

        if response.status_code == 429:

            retry_after = int(response.headers.get("Retry-After", 5))

            time.sleep(retry_after)

            continue

        return response

    raise Exception("Canvas API rate limit exceeded repeatedly")