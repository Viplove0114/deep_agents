"""
Deep Agents — Memory & Checkpointing.

Provides helpers for creating LangGraph checkpointers and thread IDs,
extracted from notebook 2 (context engineering).
"""

from __future__ import annotations

import uuid

from langgraph.checkpoint.memory import MemorySaver


def create_checkpointer() -> MemorySaver:
    """Return a fresh in-memory checkpointer for conversation persistence."""
    return MemorySaver()


def generate_thread_id() -> str:
    """Generate a unique thread ID for a new conversation."""
    return str(uuid.uuid4())


def make_thread_config(thread_id: str) -> dict:
    """Build the LangGraph config dict for the given thread."""
    return {"configurable": {"thread_id": thread_id}}
