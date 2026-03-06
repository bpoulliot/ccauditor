import secrets
import time

from app.database.db import SessionLocal
from app.database.models import User

RESET_TOKENS = {}

TOKEN_EXPIRATION = 3600


def generate_reset_token(username):

    token = secrets.token_urlsafe(32)

    RESET_TOKENS[token] = {
        "username": username,
        "created": time.time(),
    }

    return token


def validate_reset_token(token):

    record = RESET_TOKENS.get(token)

    if not record:
        return None

    if time.time() - record["created"] > TOKEN_EXPIRATION:

        del RESET_TOKENS[token]
        return None

    return record["username"]


def consume_token(token):

    if token in RESET_TOKENS:
        del RESET_TOKENS[token]