from prometheus_client import start_http_server


def start_metrics_server():

    """
    Start Prometheus metrics endpoint.
    """

    start_http_server(8000)