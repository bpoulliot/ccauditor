import os
from argon2 import PasswordHasher

ph = PasswordHasher()

BOOTSTRAP_ADMIN_USERNAME = os.getenv("BOOTSTRAP_ADMIN_USERNAME")
BOOTSTRAP_ADMIN_PASSWORD = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")


def ensure_bootstrap_admin():

    if not BOOTSTRAP_ADMIN_USERNAME:
        return

    # Placeholder bootstrap logic
    pass