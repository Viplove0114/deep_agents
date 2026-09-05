"""
Deep Agents — Tavily Web Search Tool.

Provides a reusable web search function backed by the Tavily API,
extracted from notebooks 1, 2, and 4.
"""

from __future__ import annotations

import os
from typing import Literal

from tavily import TavilyClient


def create_web_search_tool(
    api_key: str | None = None,
) -> callable:
    """
    Create and return a web search function backed by Tavily.

    Parameters
    ----------
    api_key : str, optional
        Tavily API key. Falls back to ``TAVILY_API_KEY`` env var.

    Returns
    -------
    callable
        A ``web_search(query, ...)`` function ready for use as a deep-agent tool.
    """
    resolved_key = api_key or os.getenv("TAVILY_API_KEY", "")
    client = TavilyClient(api_key=resolved_key)

    def web_search(
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news", "finance", "sports"] = "general",
        include_raw_content: bool = False,
    ):
        """Run a web search using the Tavily API."""
        return client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )

    return web_search
