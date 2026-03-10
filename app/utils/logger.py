import logging

from app.config.settings import settings

logger = logging.getLogger("ccauditor")

if settings.LOG_DESTINATION == "stdout":
    logging.basicConfig(level=logging.INFO)
