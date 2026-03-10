from prometheus_client import start_http_server

from app.config.settings import settings

_metrics_started = False


def start_metrics_server():
    global _metrics_started

    if _metrics_started:
        return

    port = getattr(settings, "METRICS_PORT", 8000)

    try:
        start_http_server(port)
        print(f"Metrics server started on port {port}")
        _metrics_started = True
    except OSError:
        pass