import logging

logger = logging.getLogger("audit")


def log_event(event_type, user=None, details=None):

    logger.info(
        {
            "event": event_type,
            "user": user,
            "details": details,
        }
    )
