"""
Deep Agents — Tools Package.

Centralises all tool factory functions and data models for the
career suite and general-purpose agent workflows.

Tool Factories
--------------
* ``create_web_search_tool``     — General Tavily web search
* ``create_job_search_tool``     — Job-board-targeted search (3-day freshness)
* ``create_resume_parser_tool``  — Parse pasted resume text
* ``create_job_extractor_tool``  — Extract JD from URL or pasted text
* ``create_github_analyzer_tool``— Analyse GitHub profile / repos

Data Models
-----------
* ``ResumeProfile``  — Structured resume with nested entries
* ``JobPosting``     — Structured job description

Direct-Use Functions
--------------------
* ``parse_resume_file``      — Parse uploaded resume files (PDF/DOCX/TXT/MD)
* ``export_resume_to_pdf``   — Markdown resume → PDF bytes
* ``export_resume_to_docx``  — Markdown resume → DOCX bytes
* ``export_resume``          — Convenience: export to multiple formats at once
"""

from __future__ import annotations

# --- Search ---
from deep_agents.tools.search import (
    create_web_search_tool,
    create_job_search_tool,
)

# --- Resume Parser ---
from deep_agents.tools.resume_parser import (
    create_resume_parser_tool,
    parse_resume_file,
    ResumeProfile,
    ExperienceEntry,
    EducationEntry,
    ProjectEntry,
    SUPPORTED_EXTENSIONS,
)

# --- Job Extractor ---
from deep_agents.tools.job_extractor import (
    create_job_extractor_tool,
    JobPosting,
)

# --- GitHub Analyzer ---
from deep_agents.tools.github_analyzer import (
    create_github_analyzer_tool,
    GitHubProfile,
    GitHubRepo,
)

# --- Resume Exporter ---
from deep_agents.tools.resume_exporter import (
    export_resume_to_pdf,
    export_resume_to_docx,
    export_resume,
)


__all__ = [
    # Search
    "create_web_search_tool",
    "create_job_search_tool",
    # Resume Parser
    "create_resume_parser_tool",
    "parse_resume_file",
    "ResumeProfile",
    "ExperienceEntry",
    "EducationEntry",
    "ProjectEntry",
    "SUPPORTED_EXTENSIONS",
    # Job Extractor
    "create_job_extractor_tool",
    "JobPosting",
    # GitHub Analyzer
    "create_github_analyzer_tool",
    "GitHubProfile",
    "GitHubRepo",
    # Resume Exporter
    "export_resume_to_pdf",
    "export_resume_to_docx",
    "export_resume",
]
