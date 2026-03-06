import os


REQUIRED_ENV_VARS = [
    "CANVAS_BASE_URL",
    "CANVAS_API_TOKEN",
    "DATABASE_URL",
]


def validate_environment():

    missing = []

    for var in REQUIRED_ENV_VARS:

        if not os.getenv(var):
            missing.append(var)

    if missing:

        raise RuntimeError(
            f"Missing required environment variables: {missing}"
        )