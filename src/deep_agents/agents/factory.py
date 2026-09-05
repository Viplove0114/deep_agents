"""
Deep Agents — Agent Factory.

Unified entry-point for building agents with any combination of model,
tools, prompts, backends, checkpointers, memory, and subagents.

Consolidates the patterns from all four experiment notebooks into a
single ``create_agent_instance()`` call.
"""

from __future__ import annotations

from typing import Any

from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

from deep_agents.backends.factory import create_backend
from deep_agents.config import DEFAULT_MODEL


def create_agent_instance(
    model_id: str = DEFAULT_MODEL,
    *,
    tools: list | None = None,
    system_prompt: str = "",
    backend_type: str = "state",
    backend_kwargs: dict[str, Any] | None = None,
    checkpointer: Any | None = None,
    memory: list[str] | None = None,
    subagents: list[dict[str, Any]] | None = None,
):
    """
    Build and return a compiled deep-agent graph.

    Parameters
    ----------
    model_id : str
        Model identifier in ``"provider:model-name"`` format.
    tools : list, optional
        Custom tool functions to add.
    system_prompt : str
        Additional system instructions appended to the default prompt.
    backend_type : str
        ``"state"`` | ``"filesystem"`` | ``"store"``.
    backend_kwargs : dict, optional
        Extra kwargs forwarded to ``create_backend()``.
    checkpointer : object, optional
        A LangGraph checkpointer (e.g. ``MemorySaver``).
    memory : list[str], optional
        List of virtual file paths for the agent to auto-read at start.
    subagents : list[dict], optional
        Subagent definition dicts.

    Returns
    -------
    tuple[CompiledStateGraph, store | None]
        ``(agent, store)`` — *store* is non-None only for ``"store"`` backends.
    """
    bk_kwargs = backend_kwargs or {}
    backend, store = create_backend(backend_type, **bk_kwargs)

    # Normalize provider/model format (e.g., "groq/compound-mini" -> "groq:compound-mini")
    normalized_model_id = model_id
    if "/" in model_id and ":" not in model_id:
        provider, model_name = model_id.split("/", 1)
        normalized_model_id = f"{provider}:{model_name}"

    kwargs: dict[str, Any] = {
        "model": normalized_model_id,
        "backend": backend,
    }

    if tools:
        kwargs["tools"] = tools
    if system_prompt:
        kwargs["system_prompt"] = system_prompt
    if checkpointer is not None:
        kwargs["checkpointer"] = checkpointer
    if memory:
        kwargs["memory"] = memory
    if subagents:
        kwargs["subagents"] = subagents
    if store is not None:
        kwargs["store"] = store

    agent = create_deep_agent(**kwargs)
    return agent, store
