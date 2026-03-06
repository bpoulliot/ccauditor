import re


MIN_PASSWORD_LENGTH = 12


def validate_password(password):

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError("Password must be at least 12 characters long")

    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain an uppercase letter")

    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain a lowercase letter")

    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain a number")

    if not re.search(r"[!@#$%^&*()_+=\-{}[\]|:;\"'<>,.?/]", password):
        raise ValueError("Password must contain a special character")

    return True