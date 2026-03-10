from app.database.db import SessionLocal
from app.database.models import Role, User


def get_user_role(user_id):

    db = SessionLocal()

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    role = db.query(Role).filter(Role.id == user.role_id).first()

    return role.name


def require_role(user_id, allowed_roles):

    role = get_user_role(user_id)

    if role not in allowed_roles:
        raise PermissionError("Access denied")
