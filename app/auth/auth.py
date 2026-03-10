import os

from argon2 import PasswordHasher

from app.database.db import SessionLocal
from app.database.models import Role, User

ph = PasswordHasher()

BOOTSTRAP_ADMIN_USERNAME = os.getenv("BOOTSTRAP_ADMIN_USERNAME")
BOOTSTRAP_ADMIN_PASSWORD = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")


def ensure_bootstrap_admin():
    """
    Ensure a bootstrap admin user exists on startup.
    """

    if not BOOTSTRAP_ADMIN_USERNAME or not BOOTSTRAP_ADMIN_PASSWORD:
        return

    db = SessionLocal()

    existing_user = (
        db.query(User).filter(User.username == BOOTSTRAP_ADMIN_USERNAME).first()
    )

    if existing_user:
        return

    role = db.query(Role).filter(Role.name == "admin").first()

    if not role:
        role = Role(name="admin")
        db.add(role)
        db.commit()

    password_hash = ph.hash(BOOTSTRAP_ADMIN_PASSWORD)

    user = User(
        username=BOOTSTRAP_ADMIN_USERNAME,
        password_hash=password_hash,
        role_id=role.id,
        locked=False,
    )

    db.add(user)
    db.commit()


def verify_password(password, password_hash):
    """
    Verify password using Argon2.
    """

    try:
        return ph.verify(password_hash, password)
    except Exception:
        return False
