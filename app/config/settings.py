import os
from dotenv import load_dotenv

load_dotenv()


class Settings:

    CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL")
    CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")

    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")

    AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")
    AI_MODEL = os.getenv("AI_MODEL", "llama3")

    LOG_DESTINATION = os.getenv("LOG_DESTINATION", "stdout")


settings = Settings()