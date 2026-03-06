import uuid
import time
import redis

from app.config.settings import settings


redis_client = redis.Redis.from_url(settings.REDIS_URL)

SESSION_TTL = int(settings.SESSION_TIMEOUT)


def create_session(user_id):

    session_id = str(uuid.uuid4())

    key = f"session:{session_id}"

    redis_client.set(
        key,
        user_id,
        ex=SESSION_TTL,
    )

    return session_id


def validate_session(session_id):

    key = f"session:{session_id}"

    user_id = redis_client.get(key)

    if not user_id:
        return False

    # refresh TTL on activity
    redis_client.expire(key, SESSION_TTL)

    return True


def destroy_session(session_id):

    key = f"session:{session_id}"

    redis_client.delete(key)
