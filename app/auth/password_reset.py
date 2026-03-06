import secrets
import redis

from app.config.settings import settings


redis_client = redis.Redis.from_url(settings.REDIS_URL)

TOKEN_EXPIRATION = 3600


def generate_reset_token(username):

    token = secrets.token_urlsafe(32)

    redis_client.set(
        f"reset_token:{token}",
        username,
        ex=TOKEN_EXPIRATION,
    )

    return token


def validate_reset_token(token):

    username = redis_client.get(f"reset_token:{token}")

    if not username:
        return None

    return username.decode()


def consume_token(token):

    redis_client.delete(f"reset_token:{token}")