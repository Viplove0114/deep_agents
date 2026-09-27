"""
Deep Agents — Job Description Extractor Tool.

Extracts and structures job postings from two input modes:

1. **URL mode** — Scrapes content from job board URLs (LinkedIn, Naukri,
   Indeed, Greenhouse, Lever, company career pages) via the Tavily API.
2. **Text mode** — Accepts raw JD text pasted directly by the user.

In both cases the tool returns the cleaned text alongside a structured
schema so the LLM can parse it into a ``JobPosting`` model.

Design Rationale
----------------
We use Tavily's ``search`` with ``include_raw_content=True`` for URL
extraction because it handles JavaScript-rendered pages (LinkedIn, Naukri)
better than simple HTTP requests. The structured parsing of fields
(required skills, experience level, etc.) is delegated to the LLM,
which understands context far better than regex.
"""

from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
#  Structured Job Posting Schema
# ---------------------------------------------------------------------------


class JobPosting(BaseModel):
    """Structured representation of a job posting.

    This schema is consumed downstream by the JD Analyzer subagent
    and the Resume Tailor subagent to perform gap analysis and
    keyword matching.
    """

    company: str = Field(default="", description="Company name.")
    role_title: str = Field(default="", description="Job title / role name.")
    location: str = Field(
        default="",
        description="Job location (city, remote, hybrid, on-site).",
    )
    job_type: str = Field(
        default="",
        description="Employment type (full-time, part-time, contract, internship).",
    )
    salary_range: str = Field(
        default="",
        description="Salary or compensation range, if mentioned.",
    )
    experience_level: str = Field(
        default="",
        description="Seniority level (Junior, Mid, Senior, Lead, Staff, etc.).",
    )
    required_skills: list[str] = Field(
        default_factory=list,
        description="Must-have skills and qualifications.",
    )
    nice_to_have: list[str] = Field(
        default_factory=list,
        description="Preferred or nice-to-have skills.",
    )
    responsibilities: list[str] = Field(
        default_factory=list,
        description="Key job responsibilities and duties.",
    )
    qualifications: list[str] = Field(
        default_factory=list,
        description="Education or certification requirements.",
    )
    tech_stack: list[str] = Field(
        default_factory=list,
        description="Specific technologies, frameworks, and tools mentioned.",
    )
    application_url: str = Field(
        default="",
        description="Direct application link.",
    )
    source_url: str = Field(
        default="",
        description="Original URL where the posting was found.",
    )
    raw_text: str = Field(
        default="",
        description="Full raw text of the job posting.",
    )


# ---------------------------------------------------------------------------
#  Extraction Instructions (shared between URL and text modes)
# ---------------------------------------------------------------------------

_EXTRACTION_INSTRUCTIONS: str = (
    "INSTRUCTIONS: Extract the following structured fields from the job posting above:\n"
    "- company, role_title, location, job_type (full-time/part-time/contract)\n"
    "- salary_range (if mentioned), experience_level (Junior/Mid/Senior/Lead)\n"
    "- required_skills[] (must-have skills and qualifications)\n"
    "- nice_to_have[] (preferred/bonus skills)\n"
    "- responsibilities[] (key duties)\n"
    "- qualifications[] (education/certification requirements)\n"
    "- tech_stack[] (specific technologies, frameworks, tools)\n"
    "- application_url (direct apply link, if available)\n\n"
    "IMPORTANT: Only extract information that is EXPLICITLY stated in the posting. "
    "Do NOT infer, assume, or add requirements that are not mentioned.\n"
    "Save the structured result to /jobs/ using write_file."
)


# ---------------------------------------------------------------------------
#  URL-Based Extraction
# ---------------------------------------------------------------------------


def _extract_jd_from_url(url: str, api_key: str) -> str:
    """Scrape job description content from a URL via Tavily.

    Parameters
    ----------
    url : str
        The job posting URL (LinkedIn, Naukri, Indeed, Greenhouse, etc.).
    api_key : str
        Tavily API key.

    Returns
    -------
    str
        Extracted job posting text with parsing instructions,
        or an error message if extraction fails.
    """
    from tavily import TavilyClient

    client = TavilyClient(api_key=api_key)

    try:
        result = client.search(
            query=f"site:{url}",
            max_results=1,
            include_raw_content=True,
        )

        content = ""
        source_url = url

        if result.get("results"):
            top = result["results"][0]
            content = top.get("raw_content") or top.get("content", "")
            source_url = top.get("url", url)

        if not content.strip():
            return (
                f"ERROR: Could not extract content from URL: {url}\n\n"
                "Possible reasons:\n"
                "- The page requires login (LinkedIn private postings)\n"
                "- The URL is invalid or the posting has been removed\n"
                "- The page uses heavy JavaScript rendering\n\n"
                "FALLBACK: Please copy-paste the job description text directly."
            )

        word_count = len(content.split())

        return (
            f"JOB POSTING EXTRACTED SUCCESSFULLY\n"
            f"Source: {source_url}\n"
            f"Words: {word_count}\n"
            f"{'=' * 60}\n\n"
            f"{content}\n\n"
            f"{'=' * 60}\n"
            f"{_EXTRACTION_INSTRUCTIONS}"
        )

    except Exception as exc:
        return (
            f"ERROR: Failed to extract job posting from URL: {url}\n"
            f"Details: {exc}\n\n"
            "FALLBACK: Please copy-paste the job description text directly."
        )


# ---------------------------------------------------------------------------
#  Text-Based Extraction
# ---------------------------------------------------------------------------


def _process_jd_text(raw_text: str) -> str:
    """Process raw JD text pasted by the user.

    Parameters
    ----------
    raw_text : str
        Raw job description text.

    Returns
    -------
    str
        The JD text with extraction instructions.
    """
    word_count = len(raw_text.split())

    return (
        f"JOB DESCRIPTION RECEIVED\n"
        f"Words: {word_count}\n"
        f"{'=' * 60}\n\n"
        f"{raw_text}\n\n"
        f"{'=' * 60}\n"
        f"{_EXTRACTION_INSTRUCTIONS}"
    )


# ---------------------------------------------------------------------------
#  Public API — Tool Factory
# ---------------------------------------------------------------------------


def create_job_extractor_tool(
    api_key: str | None = None,
) -> callable:
    """Create and return a job posting extraction function.

    The returned tool intelligently detects whether the input is a URL
    or raw text, and processes it accordingly.

    Parameters
    ----------
    api_key : str, optional
        Tavily API key. Falls back to ``TAVILY_API_KEY`` env var.

    Returns
    -------
    callable
        An ``extract_job_posting(input_text)`` function for agent tool registration.
    """
    resolved_key = api_key or os.getenv("TAVILY_API_KEY", "")

    def extract_job_posting(input_text: str) -> str:
        """Extract and structure a job posting from a URL or pasted text.

        Automatically detects the input type:
        - If the input starts with ``http://`` or ``https://``, treats it
          as a URL and scrapes the page content via Tavily.
        - Otherwise, treats it as raw JD text pasted by the user.

        Supports URLs from: LinkedIn, Naukri, Indeed, Greenhouse, Lever,
        and any company career page.

        Parameters
        ----------
        input_text : str
            Either a job posting URL or raw job description text.

        Returns
        -------
        str
            The extracted/processed JD text with structured extraction instructions.
        """
        if not input_text.strip():
            return "ERROR: Empty input. Please provide a job posting URL or paste the JD text."

        cleaned = input_text.strip()

        # Detect URL vs raw text
        if cleaned.startswith(("http://", "https://")):
            if not resolved_key:
                return (
                    "ERROR: TAVILY_API_KEY is not set. URL extraction requires a Tavily API key.\n"
                    "FALLBACK: Please paste the job description text directly instead."
                )
            return _extract_jd_from_url(cleaned, resolved_key)

        return _process_jd_text(cleaned)

    return extract_job_posting
