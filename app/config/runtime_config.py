from functools import lru_cache

from app.config.settings import settings
from app.config.persistent_settings import get_setting


DEFAULT_SCAN_TIMEOUT_MINUTES = 15
DEFAULT_MAX_FILE_SCAN_MB = 50


@lru_cache(maxsize=1)
def get_scan_timeout_minutes():
    """
    Get scan timeout value from persistent settings or fallback to default.
    Safe for workers (no Streamlit usage).
    """
    try:
        return int(
            get_setting(
                "SCAN_TIMEOUT_MINUTES",
                DEFAULT_SCAN_TIMEOUT_MINUTES,
            )
        )
    except Exception:
        return DEFAULT_SCAN_TIMEOUT_MINUTES


@lru_cache(maxsize=1)
def get_max_file_scan_mb():
    """
    Get file scan limit from persistent settings or fallback to default.
    """
    try:
        return int(
            get_setting(
                "MAX_FILE_SCAN_MB",
                DEFAULT_MAX_FILE_SCAN_MB,
            )
        )
    except Exception:
        return DEFAULT_MAX_FILE_SCAN_MB