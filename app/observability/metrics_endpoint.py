from prometheus_client import generate_latest
import streamlit as st


def show_metrics():

    st.title("Observability")

    st.subheader("Prometheus Metrics")

    metrics = generate_latest().decode("utf-8")

    st.code(metrics, language="text")