import os
from typing import Optional
from dotenv import load_dotenv

from app.config.persistent_settings import get_setting

# Load .env if present (safe for Docker + local dev)
load_dotenv()


def _bool(value: Optional[str], default: bool = False) -> bool:
    """Parse environment booleans safely."""
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "on")

class Settings:

    # --------------------------------------------------
    # Canvas configuration
    # --------------------------------------------------

    CANVAS_BASE_URL: Optional[str] = os.getenv("CANVAS_BASE_URL")
    CANVAS_API_TOKEN: Optional[str] = os.getenv("CANVAS_API_TOKEN")

    # Canvas term exclusions (comma separated IDs)
    EXCLUDED_TERM_IDS = os.getenv("EXCLUDED_TERM_IDS", "")

    # Canvas account ID to get
    ACCOUNT_ID = str = os.getenv("ACCOUNT_ID")

    def excluded_term_ids(self):
        if not self.EXCLUDED_TERM_IDS:
            return []
        return [int(x.strip()) for x in self.EXCLUDED_TERM_IDS.split(",") if x.strip()]
    
    # --------------------------------------------------
    # Video API Keys
    # --------------------------------------------------

    PANOPTO_SERVER = os.getenv("PANOPTO_SERVER")
    CLIENT_ID = os.getenv("PANOPTO_CLIENT_ID")
    CLIENT_SECRET = os.getenv("PANOPTO_CLIENT_SECRET")
    VIMEO_API_TOKEN: str = os.getenv("VIMEO_API_TOKEN")
    PANOPTO_BASE: str = os.getenv("PANOPTO_BASE")
    
    # --------------------------------------------------
    # Infrastructure
    # --------------------------------------------------

    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # --------------------------------------------------
    # Session management
    # --------------------------------------------------

    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "3600"))
    ST_AUTO_REFRESH: int = int(os.getenv("ST_AUTO_REFRESH", "10"))

    # --------------------------------------------------
    # Logging
    # --------------------------------------------------

    LOG_DESTINATION: str = "stdout"

    # --------------------------------------------------
    # AI enhancement configuration
    # --------------------------------------------------

    AI_ENABLED: bool = os.getenv("AI_ENABLED", "false").lower() == "true"
    AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")
    AI_MODEL = os.getenv("AI_MODEL", "llama3.1:8b")
    VISION_MODEL = os.getenv("VISION_MODEL", "llava:13b")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    # --------------------------------------------------
    # Celery configuration
    # --------------------------------------------------

    CELERY_TASK_TIME_LIMIT: int = int(os.getenv("CELERY_TASK_TIME_LIMIT", "900"))
    CELERY_TASK_SOFT_TIME_LIMIT: int = int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "840"))

    CELERY_WORKER_MAX_TASKS_PER_CHILD: int = int(
        os.getenv("CELERY_WORKER_MAX_TASKS_PER_CHILD", "100")
    )

    SCAN_RETRY_DELAY: int = int(os.getenv("SCAN_RETRY_DELAY", "60"))

    # --------------------------------------------------
    # Scanning behavior
    # --------------------------------------------------

    SCAN_INCREMENTAL_ENABLED: bool = _bool(
        os.getenv("SCAN_INCREMENTAL_ENABLED"), True
    )

    SCAN_INCREMENTAL_THRESHOLD_HOURS: int = int(
        os.getenv("SCAN_INCREMENTAL_THRESHOLD_HOURS", "24")
    )

    SCAN_RETRY_DELAY: int = int(os.getenv("SCAN_RETRY_DELAY", "60"))

    DEFAULT_MAX_FILE_SCAN_MB: int = os.getenv("DEFAULT_MAX_FILE_SCAN_MB")
    DEFAULT_SCAN_TIMEOUT_MINUTES: int = os.getenv("DEFAULT_SCAN_TIMEOUT_MINUTES")

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    def validate(self) -> None:
        """Validate required configuration."""

        if not self.CANVAS_BASE_URL:
            raise RuntimeError(
                "CANVAS_BASE_URL environment variable is not set."
            )

        if not self.CANVAS_API_TOKEN:
            raise RuntimeError(
                "CANVAS_API_TOKEN environment variable is not set."
            )

        if not self.DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL environment variable is not set."
            )

    # --------------------------------------------------
    # Acessibility Standards
    # --------------------------------------------------

    ACCESSIBILITY_STANDARD = os.getenv(
        "ACCESSIBILITY_STANDARD",
        "WCAG 2.1 AA",
    )

    ACCESSIBILITY_STANDARD_VERSION = os.getenv(
        "ACCESSIBILITY_STANDARD_VERSION",
        "WCAG 2.2",
    )

    ACCESSIBILITY_LEVEL = os.getenv(
        "ACCESSIBILITY_LEVEL",
        "AA",
    )

settings = Settings()