"""
Deep Agents — Subagent Definitions.

Pre-configured subagent definitions for deep agents, providing two specialized tiers:
  1. Light Research Subagent (``create_light_research_subagent`` / ``create_research_subagent``)
     - Designed for quick, lightweight factual lookups and concise summaries.
  2. Deep Structured Research Subagent (``create_structured_research_subagent``)
     - Designed for in-depth, multi-faceted investigation.
     - Emits structured output conforming to the ``ResearchFindings`` schema.
"""

from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class ResearchFindings(BaseModel):
    """Structured findings emitted by the deep research subagent."""

    summary: str = Field(
        description="A comprehensive synthesis of findings on the topic."
    )
    key_points: list[str] = Field(
        default_factory=list,
        description="Key takeaways, evidence points, or critical insights discovered.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="List of source URLs, documents, or citations consulted during research.",
    )
    confidence: float = Field(
        default=1.0,
        description="Confidence score between 0.0 and 1.0 reflecting evidence strength.",
    )


def _normalize_model_id(model_id: str | None) -> str | None:
    """Normalize 'provider/model' to 'provider:model' for langchain init_chat_model."""
    if model_id and "/" in model_id and ":" not in model_id:
        provider, model_name = model_id.split("/", 1)
        return f"{provider}:{model_name}"
    return model_id


def create_light_research_subagent(
    tools: list | None = None,
    model_override: str | None = None,
) -> dict[str, Any]:
    """
    Return a lightweight research subagent definition dict.

    Used for fast, brief factual lookups without heavy deep diving.

    Parameters
    ----------
    tools : list, optional
        Tools the subagent can use (e.g. ``[web_search]``).
    model_override : str, optional
        Model identifier to override the parent's model.

    Returns
    -------
    dict
        A subagent config suitable for ``create_deep_agent(subagents=[...])``.
    """
    subagent: dict[str, Any] = {
        "name": "light-researcher",
        "description": (
            "Performs quick, lightweight research for simple queries and brief factual lookups. "
            "Use this when a fast, concise summary is needed rather than an exhaustive deep dive."
        ),
        "system_prompt": (
            "You are a fast, lightweight research assistant. "
            "Provide clear, accurate, and concise answers to specific research questions. "
            "Focus on key facts and direct answers without unnecessary verbosity."
        ),
    }
    if tools:
        subagent["tools"] = tools
    if model_override:
        subagent["model"] = _normalize_model_id(model_override)
    return subagent



create_research_subagent = create_light_research_subagent


def create_structured_research_subagent(
    tools: list | None = None,
    model_override: str | None = None,
    response_format: type | None = ResearchFindings,
) -> dict[str, Any]:
    """
    Return a deep research subagent that emits Pydantic-structured output.

    Used for thorough, exhaustive investigation of complex topics and questions,
    returning validated structured findings.

    Parameters
    ----------
    tools : list, optional
        Tools the subagent can use (e.g. ``[web_search]``).
    model_override : str, optional
        Model identifier to override the parent's model.
    response_format : type, optional
        A Pydantic ``BaseModel`` subclass for structured responses.
        Defaults to ``ResearchFindings``.

    Returns
    -------
    dict
        A subagent config with ``response_format`` configured.
    """
    subagent: dict[str, Any] = {
        "name": "deep-researcher",
        "description": (
            "Performs exhaustive, in-depth deep research on complex topics and questions. "
            "Explores multiple facets, verifies sources, and returns structured findings "
            "including a thorough summary, key points, citations, and confidence score."
        ),
        "system_prompt": (
            "You are an expert deep-dive research specialist. "
            "Thoroughly analyze the requested topic from multiple angles. "
            "Verify facts across reliable sources, synthesize key insights, "
            "and format your findings strictly according to the required structured output schema."
        ),
    }
    if tools:
        subagent["tools"] = tools
    if model_override:
        subagent["model"] = _normalize_model_id(model_override)
    if response_format is not None:
        subagent["response_format"] = response_format
    return subagent


def get_default_subagents(
    tools: list | None = None,
    mode: Literal["both", "light", "deep"] = "both",
) -> list[dict[str, Any]]:
    """
    Return pre-configured research subagents.

    Parameters
    ----------
    tools : list, optional
        Tools shared by the subagents.
    mode : {"both", "light", "deep"}, optional
        - ``"both"``: Includes both light and deep structured research subagents.
        - ``"light"``: Includes only the light research subagent.
        - ``"deep"``: Includes only the deep structured research subagent.

    Returns
    -------
    list[dict]
        List of subagent configuration dicts.
    """
    if mode == "light":
        return [create_light_research_subagent(tools=tools)]
    if mode == "deep":
        return [create_structured_research_subagent(tools=tools)]
    return [
        create_light_research_subagent(tools=tools),
        create_structured_research_subagent(tools=tools),
    ]
