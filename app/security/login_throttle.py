import time

attempts = {}

MAX_ATTEMPTS = 5
LOCK_TIME = 300


def register_attempt(username):

    now = time.time()

    if username not in attempts:
        attempts[username] = []

    attempts[username].append(now)

    attempts[username] = [t for t in attempts[username] if now - t < LOCK_TIME]

    if len(attempts[username]) > MAX_ATTEMPTS:
        raise Exception("Too many login attempts. Try again later.")
