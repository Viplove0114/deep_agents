"""
Deep Agents — A modular framework for building deep agents.

Re-exports key components so users can write::

    from deep_agents.config import load_environment
    from deep_agents.agents.factory import create_agent_instance
    from deep_agents.tools.search import create_web_search_tool
"""

from deep_agents.config import load_environment, get_available_models

__all__ = [
    "load_environment",
    "get_available_models",
]


def main() -> None:
    """CLI entry-point (placeholder)."""
    print("Deep Agents — use `streamlit run app.py` to launch the chat UI.")
