import secrets


def generate_csrf_token():

    return secrets.token_urlsafe(32)


def validate_csrf_token(session_token, form_token):

    return session_token == form_token
