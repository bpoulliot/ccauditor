import streamlit as st
import requests

from app.config.settings import settings
from app.config.persistent_settings import set_setting
from app.ai.ollama_client import get_ollama_models
from app.config.runtime_config import (
    get_max_file_scan_mb,
    get_scan_timeout_minutes,
    DEFAULT_MAX_FILE_SCAN_MB,
    DEFAULT_SCAN_TIMEOUT_MINUTES
)

from app.ai.ollama_client import get_ollama_models

def filter_embedding_models(models):
    return [m for m in models if "embed" in m or "embedding" in m]


def filter_general_models(models):
    return [
        m for m in models
        if "llava" not in m.lower() and "vision" not in m.lower() and "embed" not in m.lower()
    ]


def filter_vision_models(models):
    return [
        m for m in models
        if "llava" in m.lower() or "vision" in m.lower()
    ]

def safe_selectbox(label, options, default_value=None):

    if not options:

        st.warning(f"No compatible models found for {label}")
        return st.text_input(label, value=default_value or "")

    index = 0

    if default_value in options:
        index = options.index(default_value)

    return st.selectbox(label, options, index=index)

def show_settings():

    st.title("System Settings")

    st.subheader("Accessibility Standard")

    version = st.selectbox(
        "WCAG Version",
        ["WCAG 2.1", "WCAG 2.2"],
        index=1 if settings.ACCESSIBILITY_STANDARD_VERSION == "WCAG 2.2" else 0,
    )

    level = st.selectbox(
        "Conformance Level",
        ["A", "AA"],
        index=1 if settings.ACCESSIBILITY_LEVEL == "AA" else 0,
    )

    settings.ACCESSIBILITY_STANDARD_VERSION = version
    settings.ACCESSIBILITY_LEVEL = level

    st.subheader("AI Configuration")

    ai_enabled = st.checkbox(
        "Enable AI Features",
        value=settings.AI_ENABLED
    )

    settings.AI_ENABLED = ai_enabled

    if ai_enabled:

        import requests
        from app.ai.ollama_client import get_ollama_models

        # --------------------------------------------------
        # Ollama Server
        # --------------------------------------------------

        st.subheader("Ollama Configuration")

        ollama_host = st.text_input(
            "Ollama Server",
            value=settings.OLLAMA_HOST
        )

        if st.button("Verify Ollama Connection"):

            try:

                r = requests.get(f"{ollama_host}/api/tags", timeout=5)

                if r.status_code == 200:
                    st.success("Connected to Ollama successfully")
                else:
                    st.error("Ollama responded but returned an error")

            except Exception as e:

                st.error(f"Connection failed: {e}")

        # --------------------------------------------------
        # Model Selection
        # --------------------------------------------------

        ollama_models = get_ollama_models()

        general_models = filter_general_models(ollama_models)
        embedding_models = filter_embedding_models(ollama_models)
        vision_models = filter_vision_models(ollama_models)

        st.subheader("Model Selection")

        if st.button("Refresh Ollama Models"):
            get_ollama_models.clear()
            st.rerun()

        selected_model = safe_selectbox(
            "AI Model",
            general_models,
            settings.AI_MODEL
        )

        selected_embedding = safe_selectbox(
            "Embedding Model",
            embedding_models,
            settings.EMBEDDING_MODEL
        )

        selected_vision_model = safe_selectbox(
            "Vision Model",
            vision_models,
            settings.VISION_MODEL
        )

        # --------------------------------------------------
        # External Providers
        # --------------------------------------------------

        st.subheader("External AI Providers")

        openai_key = st.text_input(
            "OpenAI API Key",
            value=settings.OPENAI_API_KEY or "",
            type="password"
        )

        anthropic_key = st.text_input(
            "Anthropic API Key",
            value=settings.ANTHROPIC_API_KEY or "",
            type="password"
        )

        # --------------------------------------------------
        # Save Settings
        # --------------------------------------------------

        if st.button("Save AI Settings"):

            set_setting("AI_ENABLED", str(ai_enabled))
            set_setting("OLLAMA_HOST", ollama_host)
            set_setting("AI_MODEL", selected_model)
            set_setting("EMBEDDING_MODEL", selected_embedding)
            set_setting("VISION_MODEL", selected_vision_model)
            set_setting("OPENAI_API_KEY", openai_key)
            set_setting("ANTHROPIC_API_KEY", anthropic_key)

            st.success("AI settings saved")

    st.subheader("Scan Limits")

    max_file_mb = st.number_input(
        "Max File Scan Size (MB)",
        min_value=1,
        max_value=500,
        value=st.session_state.get(
            "max_file_scan_mb",
            DEFAULT_MAX_FILE_SCAN_MB
        ),
    )

    scan_timeout = st.number_input(
        "Scan Timeout (minutes)",
        min_value=1,
        max_value=120,
        value=st.session_state.get(
            "scan_timeout_minutes",
            DEFAULT_SCAN_TIMEOUT_MINUTES
        ),
    )

    st.session_state["max_file_scan_mb"] = max_file_mb
    st.session_state["scan_timeout_minutes"] = scan_timeout

    st.write("Logging Destination:", settings.LOG_DESTINATION)
