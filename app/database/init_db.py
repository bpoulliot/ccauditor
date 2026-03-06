from sqlalchemy import text
from app.database.db import engine

def init_db():

    with engine.connect() as conn:

        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()