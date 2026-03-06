from prometheus_client import generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
import streamlit as st


def show_metrics():

    st.title("Prometheus Metrics")

    metrics = generate_latest()

    st.code(metrics.decode("utf-8"))