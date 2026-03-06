import logging
import json
import time


logger = logging.getLogger("ccauditor")


def log_event(event_type, details=None):

    payload = {
        "timestamp": time.time(),
        "event": event_type,
        "details": details or {},
    }

    logger.info(json.dumps(payload))