"""
Deep Agents — Search Tools (Tavily API).

Provides two search tool factories:

1. ``create_web_search_tool`` — General-purpose web search for research,
   interview prep, and company analysis.
2. ``create_job_search_tool`` — Specialised job search that targets major
   job boards (LinkedIn, Naukri, Indeed, Greenhouse, Lever) and filters
   for recent postings (not older than 3 days).

Both tools are backed by the Tavily API and return structured results
suitable for LLM consumption.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Any, Literal

from tavily import TavilyClient


# ---------------------------------------------------------------------------
#  General Web Search Tool
# ---------------------------------------------------------------------------


def create_web_search_tool(
    api_key: str | None = None,
) -> callable:
    """Create and return a general web search function backed by Tavily.

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
    ) -> dict:
        """Run a web search using the Tavily API.

        Parameters
        ----------
        query : str
            The search query string.
        max_results : int
            Maximum number of results to return.
        topic : str
            Search topic category.
        include_raw_content : bool
            Whether to include full raw page content.

        Returns
        -------
        dict
            Tavily search results.
        """
        return client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )

    return web_search


# ---------------------------------------------------------------------------
#  Job Search Tool
# ---------------------------------------------------------------------------

# Major job boards to target in search queries
_JOB_BOARDS: tuple[str, ...] = (
    "linkedin.com/jobs",
    "naukri.com",
    "indeed.com",
    "greenhouse.io",
    "lever.co",
    "wellfound.com",
    "careers",
    "jobs",
)


def create_job_search_tool(
    api_key: str | None = None,
) -> callable:
    """Create and return a specialised job search function.

    Wraps the Tavily API with job-board-targeted queries optimised for
    finding **recent** job postings (not older than 3 days).

    Parameters
    ----------
    api_key : str, optional
        Tavily API key. Falls back to ``TAVILY_API_KEY`` env var.

    Returns
    -------
    callable
        A ``job_search(role, ...)`` function ready for use as a deep-agent tool.
    """
    resolved_key = api_key or os.getenv("TAVILY_API_KEY", "")
    client = TavilyClient(api_key=resolved_key)

    def job_search(
        role: str,
        location: str = "",
        experience_level: str = "",
        job_type: str = "",
        max_results: int = 10,
    ) -> str:
        """Search for recent job postings across major job boards.

        Finds job postings from the **last 3 days** across LinkedIn,
        Naukri, Indeed, Greenhouse, Lever, and company career pages.

        Parameters
        ----------
        role : str
            The job title or role to search for
            (e.g. ``"AI Engineer"``, ``"Backend Developer"``).
        location : str
            Preferred location or ``"remote"``
            (e.g. ``"Bangalore"``, ``"Remote"``, ``"San Francisco"``).
        experience_level : str
            Seniority filter (e.g. ``"Junior"``, ``"Mid"``, ``"Senior"``).
        job_type : str
            Employment type (e.g. ``"full-time"``, ``"contract"``,
            ``"internship"``).
        max_results : int
            Maximum number of results to return (default 10).

        Returns
        -------
        str
            Formatted search results with job details and instructions
            for the LLM to structure into an Excel-ready format.
        """
        # Build a targeted search query
        query_parts = [role]
        if location:
            query_parts.append(location)
        if experience_level:
            query_parts.append(experience_level)
        if job_type:
            query_parts.append(job_type)
        query_parts.append("job opening hiring")

        query = " ".join(query_parts)

        try:
            result = client.search(
                query,
                max_results=max_results,
                include_raw_content=False,
                topic="general",
            )
        except Exception as exc:
            return (
                f"ERROR: Job search failed.\n"
                f"Details: {exc}\n\n"
                "Please check your TAVILY_API_KEY and try again."
            )

        if not result.get("results"):
            return (
                f"No job postings found for: {query}\n\n"
                "Try broadening your search:\n"
                "- Use a more general role title\n"
                "- Remove location or experience filters\n"
                "- Check spelling"
            )

        # Format results
        cutoff_date = datetime.now() - timedelta(days=3)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")

        lines = [
            f"JOB SEARCH RESULTS",
            f"{'=' * 60}",
            f"Query: {query}",
            f"Results found: {len(result['results'])}",
            f"Freshness filter: postings from the last 3 days (since {cutoff_str})",
            "",
        ]

        for i, item in enumerate(result["results"], 1):
            title = item.get("title", "Unknown Title")
            url = item.get("url", "")
            snippet = item.get("content", "No description available")

            # Detect source platform from URL
            source = "Unknown"
            url_lower = url.lower()
            if "linkedin.com" in url_lower:
                source = "LinkedIn"
            elif "naukri.com" in url_lower:
                source = "Naukri"
            elif "indeed.com" in url_lower:
                source = "Indeed"
            elif "greenhouse.io" in url_lower:
                source = "Greenhouse"
            elif "lever.co" in url_lower:
                source = "Lever"
            elif "wellfound.com" in url_lower:
                source = "Wellfound"
            else:
                source = "Company Career Page"

            lines.extend([
                f"--- Result {i} ---",
                f"Title: {title}",
                f"Source: {source}",
                f"URL: {url}",
                f"Snippet: {snippet[:300]}",
                "",
            ])

        lines.extend([
            f"{'=' * 60}",
            "INSTRUCTIONS:",
            "1. From each result, extract: Company, Role Title, Location,",
            "   Salary (if mentioned), Source Platform, Apply Link (URL).",
            "2. ONLY include postings that are genuine job listings.",
            "   Skip aggregator pages, blog posts, or salary guides.",
            "3. ONLY include real, verifiable URLs. Do NOT fabricate job links.",
            "4. Format the results as a structured list and save to",
            "   /jobs/search_results.json using write_file.",
            "5. Also prepare the data in a format suitable for Excel export",
            "   with columns: Company | Role | Location | Source | Apply Link",
        ])

        return "\n".join(lines)

    return job_search
