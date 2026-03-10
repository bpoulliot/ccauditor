from sqlalchemy import text
from app.database.db import engine
from app.database.models import Base


def init_db():
    """
    Initialize database schema and required extensions.
    Safe to run multiple times.
    """

    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    Base.metadata.create_all(bind=engine)