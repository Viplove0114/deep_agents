"""
Deep Agents — GitHub Profile & Repository Analyzer Tool.

Fetches public GitHub data and transforms it into resume-ready
project bullet points that the Resume Tailor subagent can inject
directly into a tailored resume.

Supports Two Input Modes
------------------------
1. **Username mode** — Provide a GitHub username to fetch their full
   public profile, top repositories, languages, and stats.
2. **Repo URL mode** — Provide one or more direct repo URLs
   (e.g. ``https://github.com/user/repo``) to analyze specific projects.

Design Rationale
----------------
Uses the public GitHub REST API v3 which requires **no authentication**
for public repos (60 requests/hour unauthenticated). This is sufficient
for resume-building use cases. We use ``urllib`` instead of ``requests``
to avoid adding an extra dependency.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
#  Structured GitHub Data Schema
# ---------------------------------------------------------------------------


class GitHubRepo(BaseModel):
    """Structured representation of a single GitHub repository."""

    name: str = Field(default="", description="Repository name.")
    description: str = Field(default="", description="Repo description.")
    language: str = Field(default="", description="Primary programming language.")
    stars: int = Field(default=0, description="Star count.")
    forks: int = Field(default=0, description="Fork count.")
    topics: list[str] = Field(
        default_factory=list,
        description="Repository topics/tags.",
    )
    url: str = Field(default="", description="GitHub URL.")


class GitHubProfile(BaseModel):
    """Structured representation of a GitHub user's profile and repositories."""

    username: str = Field(default="", description="GitHub username.")
    name: str = Field(default="", description="Display name.")
    bio: str = Field(default="", description="Profile bio.")
    public_repos: int = Field(default=0, description="Total public repositories.")
    followers: int = Field(default=0, description="Follower count.")
    total_stars: int = Field(default=0, description="Total stars across all repos.")
    profile_url: str = Field(default="", description="GitHub profile URL.")
    languages: list[str] = Field(
        default_factory=list,
        description="All programming languages used across repos.",
    )
    top_repos: list[GitHubRepo] = Field(
        default_factory=list,
        description="Top repositories sorted by stars.",
    )


# ---------------------------------------------------------------------------
#  GitHub API Helpers
# ---------------------------------------------------------------------------

_HEADERS: dict[str, str] = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "DeepAgents-GitHubAnalyzer/1.0",
}

_API_TIMEOUT: int = 15  # seconds


def _github_get(endpoint: str) -> dict | list:
    """Make a GET request to the GitHub REST API.

    Parameters
    ----------
    endpoint : str
        Full API URL (e.g. ``https://api.github.com/users/octocat``).

    Returns
    -------
    dict | list
        Parsed JSON response.

    Raises
    ------
    URLError
        If the request fails (network, 404, rate limit, etc.).
    """
    req = Request(endpoint, headers=_HEADERS)
    with urlopen(req, timeout=_API_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _parse_repo_url(url: str) -> tuple[str, str] | None:
    """Extract (owner, repo_name) from a GitHub repo URL.

    Parameters
    ----------
    url : str
        A URL like ``https://github.com/owner/repo``.

    Returns
    -------
    tuple[str, str] | None
        ``(owner, repo_name)`` or ``None`` if the URL doesn't match.
    """
    match = re.match(
        r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/?",
        url.strip(),
    )
    if match:
        return match.group(1), match.group(2)
    return None


# ---------------------------------------------------------------------------
#  Core Analysis Functions
# ---------------------------------------------------------------------------


def _analyze_username(username: str) -> str:
    """Fetch and analyze a GitHub user's full public profile.

    Parameters
    ----------
    username : str
        GitHub username.

    Returns
    -------
    str
        Formatted analysis with resume-ready bullet points.
    """
    # Fetch user profile
    user_data = _github_get(f"https://api.github.com/users/{username}")

    # Fetch repos sorted by stars (top 15)
    repos_data = _github_get(
        f"https://api.github.com/users/{username}/repos"
        f"?sort=stars&per_page=15&direction=desc"
    )

    # Process repos (skip forks)
    top_repos: list[dict[str, Any]] = []
    languages: set[str] = set()
    total_stars = 0

    for repo in repos_data:
        if repo.get("fork"):
            continue

        lang = repo.get("language") or ""
        if lang:
            languages.add(lang)

        stars = repo.get("stargazers_count", 0)
        total_stars += stars

        top_repos.append({
            "name": repo.get("name", ""),
            "description": repo.get("description") or "No description provided",
            "language": lang or "N/A",
            "stars": stars,
            "forks": repo.get("forks_count", 0),
            "topics": repo.get("topics", []),
            "url": repo.get("html_url", ""),
        })

    # Build formatted output
    profile_name = user_data.get("name") or username
    bio = user_data.get("bio") or "N/A"
    public_repos = user_data.get("public_repos", 0)
    followers = user_data.get("followers", 0)
    profile_url = user_data.get("html_url", f"https://github.com/{username}")

    lines = [
        f"GITHUB PROFILE ANALYSIS: {profile_name}",
        f"{'=' * 60}",
        f"Profile: {profile_url}",
        f"Bio: {bio}",
        f"Public Repos: {public_repos} | Followers: {followers} | Total Stars: {total_stars}",
        f"Languages: {', '.join(sorted(languages)) if languages else 'N/A'}",
        "",
        f"TOP REPOSITORIES ({len(top_repos)} original, non-fork repos):",
        f"{'-' * 40}",
    ]

    for repo in top_repos[:10]:
        topics_str = f" [{', '.join(repo['topics'])}]" if repo["topics"] else ""
        lines.append(
            f"• {repo['name']} ({repo['language']}) — "
            f"⭐ {repo['stars']} | 🍴 {repo['forks']}{topics_str}"
        )
        lines.append(f"  {repo['description']}")
        lines.append(f"  {repo['url']}")
        lines.append("")

    lines.extend([
        f"{'=' * 60}",
        "RESUME BULLET POINT SUGGESTIONS:",
        f"{'-' * 40}",
    ])

    # Generate suggested bullet points from repos
    for repo in top_repos[:5]:
        desc = repo["description"]
        lang = repo["language"]
        stars = repo["stars"]
        topics = repo["topics"]

        tech_str = lang
        if topics:
            tech_str = f"{lang}, {', '.join(topics[:3])}"

        if stars > 0:
            lines.append(
                f"• Built {repo['name']}: {desc} "
                f"using {tech_str}, garnering {stars} GitHub stars"
            )
        else:
            lines.append(
                f"• Developed {repo['name']}: {desc} "
                f"using {tech_str}"
            )

    lines.extend([
        "",
        f"{'=' * 60}",
        "IMPORTANT: These bullet points are SUGGESTIONS based on repo metadata.",
        "The user should verify and customise them with accurate details.",
        "Do NOT fabricate metrics, user counts, or impact numbers that are not evident from the repos.",
        "Save this analysis to /profile/github_portfolio.md using write_file.",
    ])

    return "\n".join(lines)


def _analyze_repo_urls(urls: list[str]) -> str:
    """Fetch and analyze specific GitHub repositories by URL.

    Parameters
    ----------
    urls : list[str]
        List of GitHub repo URLs.

    Returns
    -------
    str
        Formatted analysis of each repo with resume-ready bullet points.
    """
    lines = [
        "GITHUB REPOSITORY ANALYSIS",
        f"{'=' * 60}",
        f"Analyzing {len(urls)} repositories...",
        "",
    ]

    analyzed_repos: list[dict[str, Any]] = []

    for url in urls:
        parsed = _parse_repo_url(url)
        if not parsed:
            lines.append(f"⚠ Skipping invalid URL: {url}")
            continue

        owner, repo_name = parsed

        try:
            repo_data = _github_get(
                f"https://api.github.com/repos/{owner}/{repo_name}"
            )

            repo_info = {
                "name": repo_data.get("name", repo_name),
                "full_name": repo_data.get("full_name", f"{owner}/{repo_name}"),
                "description": repo_data.get("description") or "No description",
                "language": repo_data.get("language") or "N/A",
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "topics": repo_data.get("topics", []),
                "url": repo_data.get("html_url", url),
                "created_at": repo_data.get("created_at", "")[:10],
                "updated_at": repo_data.get("updated_at", "")[:10],
            }
            analyzed_repos.append(repo_info)

            topics_str = f" [{', '.join(repo_info['topics'])}]" if repo_info["topics"] else ""
            lines.extend([
                f"✓ {repo_info['full_name']} ({repo_info['language']})",
                f"  ⭐ {repo_info['stars']} | 🍴 {repo_info['forks']}{topics_str}",
                f"  {repo_info['description']}",
                f"  Created: {repo_info['created_at']} | Updated: {repo_info['updated_at']}",
                f"  {repo_info['url']}",
                "",
            ])

        except URLError as exc:
            lines.append(f"⚠ Failed to fetch {owner}/{repo_name}: {exc}")
            lines.append("")

    if analyzed_repos:
        lines.extend([
            f"{'=' * 60}",
            "RESUME BULLET POINT SUGGESTIONS:",
            f"{'-' * 40}",
        ])

        for repo in analyzed_repos:
            tech_str = repo["language"]
            if repo["topics"]:
                tech_str = f"{repo['language']}, {', '.join(repo['topics'][:3])}"

            if repo["stars"] > 0:
                lines.append(
                    f"• Built {repo['name']}: {repo['description']} "
                    f"using {tech_str}, garnering {repo['stars']} GitHub stars"
                )
            else:
                lines.append(
                    f"• Developed {repo['name']}: {repo['description']} "
                    f"using {tech_str}"
                )

    lines.extend([
        "",
        f"{'=' * 60}",
        "IMPORTANT: These bullet points are SUGGESTIONS based on repo metadata.",
        "The user should verify and customise them with accurate details.",
        "Do NOT fabricate metrics, user counts, or impact numbers that are not evident from the repos.",
        "Save this analysis to /profile/github_portfolio.md using write_file.",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
#  Public API — Tool Factory
# ---------------------------------------------------------------------------


def create_github_analyzer_tool() -> callable:
    """Create and return a GitHub analysis function for agent tool registration.

    The returned tool intelligently detects whether the input is a
    username or repo URL(s), and processes accordingly.

    Returns
    -------
    callable
        An ``analyze_github(input_text)`` function ready for agent tool registration.
    """

    def analyze_github(input_text: str) -> str:
        """Analyze a GitHub profile or specific repositories for resume building.

        Automatically detects the input type:

        - **Username** (e.g. ``"Viplove0114"``) → fetches full profile + top repos
        - **Repo URLs** (e.g. ``"https://github.com/user/repo"``) → analyzes specific repos
        - **Mixed** (comma/newline separated) → analyzes all provided repos

        Parameters
        ----------
        input_text : str
            A GitHub username, a single repo URL, or multiple repo URLs
            separated by commas, spaces, or newlines.

        Returns
        -------
        str
            Formatted analysis with profile stats, repo details,
            and suggested resume bullet points.
        """
        if not input_text.strip():
            return "ERROR: Empty input. Please provide a GitHub username or repository URL(s)."

        cleaned = input_text.strip()

        # Split by common delimiters (comma, newline, space)
        parts = [
            p.strip()
            for p in re.split(r"[,\n\s]+", cleaned)
            if p.strip()
        ]

        # Separate URLs from potential usernames
        urls = [p for p in parts if p.startswith(("http://", "https://"))]
        non_urls = [p for p in parts if not p.startswith(("http://", "https://"))]

        try:
            # Case 1: Only repo URLs provided
            if urls and not non_urls:
                return _analyze_repo_urls(urls)

            # Case 2: Single username (no URLs)
            if len(non_urls) == 1 and not urls:
                return _analyze_username(non_urls[0])

            # Case 3: Username + repo URLs (analyze both)
            results: list[str] = []
            if non_urls:
                # Treat first non-URL as username
                results.append(_analyze_username(non_urls[0]))
            if urls:
                results.append(_analyze_repo_urls(urls))

            return "\n\n".join(results)

        except URLError as exc:
            return (
                f"ERROR: Failed to fetch GitHub data.\n"
                f"Details: {exc}\n\n"
                "Possible reasons:\n"
                "- The username or repo doesn't exist\n"
                "- GitHub API rate limit reached (60 req/hr unauthenticated)\n"
                "- Network connectivity issue\n\n"
                "Please check the username/URL and try again."
            )
        except Exception as exc:
            return f"ERROR: Unexpected error analysing GitHub data: {exc}"

    return analyze_github
