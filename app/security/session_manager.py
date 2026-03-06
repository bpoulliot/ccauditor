import time


SESSION_TIMEOUT = 3600


sessions = {}


def create_session(user_id):

    session_id = str(user_id) + "-" + str(time.time())

    sessions[session_id] = {
        "user_id": user_id,
        "created": time.time(),
    }

    return session_id


def validate_session(session_id):

    session = sessions.get(session_id)

    if not session:
        return False

    if time.time() - session["created"] > SESSION_TIMEOUT:
        del sessions[session_id]
        return False

    return True