"""
Deep Agents — Configuration & Environment Setup.

Loads API keys from .env and Streamlit secrets, providing model discovery utilities.
"""

import os
from dotenv import load_dotenv


def load_environment() -> None:
    """Load environment variables from .env file and Streamlit Cloud secrets."""
    load_dotenv()

    # If running on Streamlit Cloud, populate os.environ from st.secrets
    try:
        import streamlit as st
        for key in ("OPENAI_API_KEY", "GROQ_API_KEY", "TAVILY_API_KEY"):
            if key in st.secrets and not os.getenv(key):
                os.environ[key] = str(st.secrets[key])
    except Exception:
        pass

    for key in ("OPENAI_API_KEY", "GROQ_API_KEY", "TAVILY_API_KEY"):
        value = os.getenv(key)
        if value:
            os.environ[key] = value


# Default model identifier for the project
DEFAULT_MODEL: str = "groq:qwen/qwen3.8-27b"

# Available model identifiers keyed by display name (Qwen 3.8-27B is default first)
AVAILABLE_MODELS: dict[str, str] = {
    "Qwen 3.8-27B (Groq)": "groq:qwen/qwen3.8-27b",
    "Groq Compound Mini": "groq:compound-mini",
    "GPT-5.4 (OpenAI)": "openai:gpt-5.4",
    "GPT-5.5 (OpenAI)": "openai:gpt-5.5",
}


def get_available_models() -> dict[str, str]:
    """Return a mapping of display name → model identifier string."""
    return AVAILABLE_MODELS.copy()


def get_model_id(display_name: str) -> str:
    """
    Resolve a display name or raw model string to a valid model identifier.

    Handles display names, standard 'provider:model' strings,
    and 'provider/model' formats like 'groq/qwen/qwen3.8-27b'.
    """
    if display_name in AVAILABLE_MODELS:
        return AVAILABLE_MODELS[display_name]
    # Normalize slash to colon for langchain init_chat_model compatibility
    if "/" in display_name and ":" not in display_name:
        provider, model_name = display_name.split("/", 1)
        return f"{provider}:{model_name}"
    return display_name
