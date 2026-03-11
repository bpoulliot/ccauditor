from prometheus_client import start_http_server

from app.config.settings import settings
import streamlit as st
from prometheus_client import generate_latest

_metrics_started = False

def show_metrics():
    """
    Streamlit page that displays Prometheus metrics.
    """

    st.title("Metrics")

    st.write("Prometheus metrics exported by CCAuditor.")

    try:

        metrics = generate_latest().decode("utf-8")

        st.code(metrics[:10000], language="text")

    except Exception as exc:

        st.error("Unable to load metrics")

        st.exception(exc)

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