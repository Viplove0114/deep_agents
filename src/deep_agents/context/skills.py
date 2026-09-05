"""
Deep Agents — Skills Loading.

Reads SKILL.md files from a directory tree and packages them as a
``files`` dict that can be seeded into the agent's virtual filesystem,
extracted from notebook 2 (context engineering).
"""

from __future__ import annotations

from pathlib import Path


def load_skills_from_directory(skills_dir: str | Path) -> dict[str, dict]:
    """
    Recursively find ``SKILL.md`` files and return them as a files dict.

    Parameters
    ----------
    skills_dir : str | Path
        Root directory to scan (e.g. ``"projects/skills"``).

    Returns
    -------
    dict[str, dict]
        Mapping of virtual paths (e.g. ``"/skills/aws/SKILL.md"``) to
        ``{"content": "<file text>"}`` dicts, ready for ``files=`` seeding.
    """
    root = Path(skills_dir)
    files: dict[str, dict] = {}

    if not root.exists():
        return files

    for md_file in root.rglob("SKILL.md"):
        # Build a virtual path like /skills/aws/SKILL.md
        relative = md_file.relative_to(root)
        virtual_path = "/" + "/".join(relative.parts)
        try:
            content = md_file.read_text(encoding="utf-8")
            files[virtual_path] = {"content": content}
        except OSError:
            continue

    return files


def get_default_skills_dir() -> Path:
    """Return the default skills directory path."""
    return Path("projects") / "skills"
