"""
Deep Agents — System Prompt Management.

Curated prompt templates extracted from the experiment notebooks,
plus helpers to load AGENTS.md context files from disk.
"""

from __future__ import annotations

from pathlib import Path


# Built-in prompt templates
 

DEFAULT_SYSTEM_PROMPT = "Act as a researcher"

RESEARCH_SYSTEM_PROMPT = (
    "You are a research assistant specializing in scientific literature. "
    "Always cite sources. Use subagents for parallel research on different topics."
)

CODING_SYSTEM_PROMPT = (
    "You are an expert software engineer. Write clean, well-documented code. "
    "Use planning to break complex tasks into steps."
)

GENERAL_ASSISTANT_PROMPT = (
    "You are a helpful, accurate, and concise AI assistant. "
    "Use planning for complex tasks. Offload large outputs to files. "
    "Delegate specialized work to subagents when available."
)

# Display-name - prompt mapping for the UI
PROMPT_OPTIONS: dict[str, str] = {
    "None (default)": "",
    "General Assistant": GENERAL_ASSISTANT_PROMPT,
    "Researcher": RESEARCH_SYSTEM_PROMPT,
    "Coder": CODING_SYSTEM_PROMPT,
    "Simple Researcher": DEFAULT_SYSTEM_PROMPT,
}


def get_system_prompt(prompt_type: str) -> str:
    """Return the system prompt for the given type name."""
    return PROMPT_OPTIONS.get(prompt_type, "")



# AGENTS.md context file loader


def load_agents_md(file_path: str | Path | None = None) -> str:
    """
    Read an ``AGENTS.md`` context file from disk.

    Parameters
    ----------
    file_path : str | Path | None
        Path to the file.  Defaults to ``projects/AGENTS.md`` relative to CWD.

    Returns
    -------
    str
        The file contents, or an empty string if the file does not exist.
    """
    path = Path(file_path) if file_path else Path("projects") / "AGENTS.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""
