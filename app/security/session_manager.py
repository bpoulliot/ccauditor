import uuid
import redis

from app.config.settings import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)

SESSION_TTL = int(getattr(settings, "SESSION_TIMEOUT", 3600))

def create_session(user_id):

    session_id = str(uuid.uuid4())

    redis_client.set(
        f"session:{session_id}",
        user_id,
        ex=SESSION_TTL,
    )

    return session_id


def validate_session(session_id):

    try:

        key = f"session:{session_id}"
        user_id = redis_client.get(key)

        if not user_id:
            return False

        redis_client.expire(key, SESSION_TTL)
        return True

    except Exception:
        return False


def destroy_session(session_id):

    redis_client.delete(f"session:{session_id}")
