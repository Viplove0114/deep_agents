"""
Deep Agents — Configuration & Environment Setup.

Centralizes API key loading, model registry, task-based model routing,
and automatic provider fallback (OpenRouter → Groq).

Model Providers
---------------
* **OpenRouter** — Qwen 3.8 27B (free) — primary
* **Groq** — Qwen 3.8 27B — automatic fallback when OpenRouter is down
* **Google AI Studio** — Gemini 3.8 Flash, Gemma 4 31B
"""

from __future__ import annotations

import logging
import os
import time
from typing import Final

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
#  API key names used across the project
# ---------------------------------------------------------------------------

_API_KEYS: Final[tuple[str, ...]] = (
    "GOOGLE_API_KEY",
    "OPENROUTER_API_KEY",
    "GROQ_API_KEY",
    "TAVILY_API_KEY",
)


def load_environment() -> None:
    """Load environment variables from ``.env`` and Streamlit Cloud secrets.

    Order of precedence:
    1. Streamlit Cloud secrets (``st.secrets``)
    2. ``.env`` file via ``python-dotenv``
    3. Already-set environment variables
    """
    load_dotenv()

    # Streamlit Cloud: propagate secrets → os.environ
    try:
        import streamlit as st

        for key in _API_KEYS:
            if key in st.secrets and not os.getenv(key):
                os.environ[key] = str(st.secrets[key])
    except Exception:
        pass

    # Ensure .env values are promoted into os.environ
    for key in _API_KEYS:
        value = os.getenv(key)
        if value:
            os.environ[key] = value


# ---------------------------------------------------------------------------
#  Model Registry
# ---------------------------------------------------------------------------

DEFAULT_MODEL: str = "openrouter:qwen/qwen3.8-27b:free"

AVAILABLE_MODELS: dict[str, str] = {
    "Qwen 3.8 27B (OpenRouter)":  "openrouter:qwen/qwen3.8-27b:free",
    "Qwen 3.8 27B (Groq)":       "groq:qwen/qwen3.8-27b",
    "Gemini 3.8 Flash (Google)":  "google_genai:gemini-3.8-flash",
    "Gemma 4 31B (Google)":       "google_genai:gemma-4-31b-it",
}


# ---------------------------------------------------------------------------
#  Automatic Fallback: OpenRouter → Groq
# ---------------------------------------------------------------------------

FALLBACK_MAP: dict[str, str] = {
    "openrouter:qwen/qwen3.8-27b:free": "groq:qwen/qwen3.8-27b",
}

# Cache OpenRouter health status to avoid checking on every call
_openrouter_health: dict[str, float | bool] = {
    "last_check": 0.0,
    "is_healthy": True,
}

_HEALTH_CHECK_INTERVAL: Final[int] = 120  # seconds between health checks


def _is_openrouter_available() -> bool:
    """Quick health check on OpenRouter API (cached for 2 minutes).

    Returns True if OpenRouter responded within the last check interval,
    False if the last check failed.  Does NOT block on every call — uses
    a lightweight cache so the app stays fast.
    """
    now = time.time()
    if now - _openrouter_health["last_check"] < _HEALTH_CHECK_INTERVAL:
        return _openrouter_health["is_healthy"]

    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        _openrouter_health.update({"last_check": now, "is_healthy": False})
        return False

    try:
        import urllib.request
        import urllib.error

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            healthy = resp.status == 200
    except Exception:
        healthy = False

    _openrouter_health.update({"last_check": now, "is_healthy": healthy})

    if not healthy:
        logger.warning("OpenRouter health check failed — will use Groq fallback.")
    return healthy


def resolve_model_id(model_id: str) -> str:
    """Resolve a model ID with automatic provider fallback.

    If *model_id* is an OpenRouter model and OpenRouter is unreachable,
    returns the Groq equivalent from ``FALLBACK_MAP``.  Otherwise returns
    the original *model_id* unchanged.

    Parameters
    ----------
    model_id : str
        The primary model identifier (e.g. ``"openrouter:qwen/qwen3.8-27b:free"``).

    Returns
    -------
    str
        The resolved model identifier — either the original or the fallback.
    """
    if not model_id.startswith("openrouter:"):
        return model_id

    fallback = FALLBACK_MAP.get(model_id)
    if not fallback:
        return model_id

    # Only check health if a Groq key is available
    if not os.getenv("GROQ_API_KEY"):
        return model_id

    if _is_openrouter_available():
        return model_id

    logger.info("Falling back from %s → %s", model_id, fallback)
    return fallback


# ---------------------------------------------------------------------------
#  Task-Based Model Routing
# ---------------------------------------------------------------------------

MODEL_ROLES: dict[str, str] = {
    "orchestrator":      "openrouter:qwen/qwen3.8-27b:free",
    "document_parsing":  "google_genai:gemma-4-31b-it",
    "fast_reasoning":    "google_genai:gemini-3.8-flash",
    "coding_accuracy":   "openrouter:qwen/qwen3.8-27b:free",
    "quality_judge":     "openrouter:qwen/qwen3.8-27b:free",
}


def get_available_models() -> dict[str, str]:
    """Return a mapping of display name → model identifier string."""
    return AVAILABLE_MODELS.copy()


def get_model_for_role(role: str) -> str:
    """Resolve a task role to the appropriate model identifier.

    Applies automatic fallback — if the role maps to an OpenRouter model
    and OpenRouter is down, returns the Groq equivalent.

    Parameters
    ----------
    role : str
        One of ``"orchestrator"``, ``"document_parsing"``,
        ``"fast_reasoning"``, ``"coding_accuracy"``, ``"quality_judge"``.

    Returns
    -------
    str
        The resolved model identifier string.

    Raises
    ------
    KeyError
        If *role* is not a recognised task role.
    """
    if role not in MODEL_ROLES:
        raise KeyError(
            f"Unknown model role {role!r}. "
            f"Available roles: {list(MODEL_ROLES.keys())}"
        )
    return resolve_model_id(MODEL_ROLES[role])


def get_model_id(display_name: str) -> str:
    """Resolve a display name or raw model string to a valid model identifier.

    Applies automatic fallback for OpenRouter models.

    Handles display names from ``AVAILABLE_MODELS``, standard
    ``'provider:model'`` strings, and ``'provider/model'`` formats.
    """
    if display_name in AVAILABLE_MODELS:
        model_id = AVAILABLE_MODELS[display_name]
    elif "/" in display_name and ":" not in display_name:
        provider, model_name = display_name.split("/", 1)
        model_id = f"{provider}:{model_name}"
    else:
        model_id = display_name

    return resolve_model_id(model_id)
