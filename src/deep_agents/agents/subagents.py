"""
Deep Agents — Subagent Definitions.

Pre-configured subagent definitions for deep agents, organised into two tiers:

Research Subagents (General Chat Mode)
--------------------------------------
1. ``create_light_research_subagent`` — Quick factual lookups and summaries.
2. ``create_structured_research_subagent`` — Deep research with ``ResearchFindings`` output.

Career Subagents (Career Mode)
------------------------------
1. ``create_jd_analyzer_subagent`` — Deep JD analysis → ``JDAnalysis`` output.
2. ``create_resume_tailor_subagent`` — ATS-optimised resume → ``TailoredResume`` output.
3. ``create_job_scout_subagent`` — Job search across boards → ``JobSearchResults`` output.
4. ``create_interview_coach_subagent`` — Interview prep → ``InterviewPrep`` output.
5. ``create_quality_judge_subagent`` — LLM-as-Judge validation → ``QualityVerdict`` output.
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
    mode: Literal["both", "light", "deep", "career"] = "both",
) -> list[dict[str, Any]]:
    """
    Return pre-configured subagents based on the selected mode.

    Parameters
    ----------
    tools : list, optional
        Tools shared by the subagents.
    mode : {"both", "light", "deep", "career"}, optional
        - ``"both"``: Includes both light and deep structured research subagents.
        - ``"light"``: Includes only the light research subagent.
        - ``"deep"``: Includes only the deep structured research subagent.
        - ``"career"``: Includes all career-focused subagents
          (JD Analyzer, Resume Tailor, Job Scout, Interview Coach, Quality Judge).

    Returns
    -------
    list[dict]
        List of subagent configuration dicts.
    """
    if mode == "light":
        return [create_light_research_subagent(tools=tools)]
    if mode == "deep":
        return [create_structured_research_subagent(tools=tools)]
    if mode == "career":
        return get_career_subagents(tools=tools)
    return [
        create_light_research_subagent(tools=tools),
        create_structured_research_subagent(tools=tools),
    ]


# ══════════════════════════════════════════════════════════════════════════════
#  Career-Focused Subagents
# ══════════════════════════════════════════════════════════════════════════════


# ---------------------------------------------------------------------------
#  1. JD Analyzer Subagent
# ---------------------------------------------------------------------------


class JDAnalysis(BaseModel):
    """Structured analysis of a job description.

    Produced by the JD Analyzer subagent after deep analysis of a
    job posting. Consumed by the Resume Tailor to optimise keyword
    matching and section ordering.
    """

    company: str = Field(
        default="", description="Company name extracted from the JD."
    )
    role_title: str = Field(
        default="", description="Exact job title as stated in the JD."
    )
    experience_level: str = Field(
        default="",
        description="Seniority level (Junior, Mid, Senior, Lead, Staff, etc.).",
    )
    domain: str = Field(
        default="",
        description="Industry or domain (e.g. 'AI/ML', 'FinTech', 'Healthcare').",
    )
    hard_skills: list[str] = Field(
        default_factory=list,
        description="Must-have technical skills explicitly required.",
    )
    soft_skills: list[str] = Field(
        default_factory=list,
        description="Soft skills or traits mentioned (e.g. 'leadership', 'communication').",
    )
    nice_to_have_skills: list[str] = Field(
        default_factory=list,
        description="Preferred but not mandatory skills.",
    )
    tech_stack: list[str] = Field(
        default_factory=list,
        description="Specific technologies, frameworks, tools, and platforms.",
    )
    ats_keywords: list[str] = Field(
        default_factory=list,
        description=(
            "High-priority keywords and exact phrases to mirror in the resume. "
            "These are the terms an ATS will scan for."
        ),
    )
    action_verbs: list[str] = Field(
        default_factory=list,
        description="Action verbs used in the JD that should be mirrored in resume bullets.",
    )
    responsibilities_summary: str = Field(
        default="",
        description="Concise summary of core responsibilities.",
    )
    qualifications_summary: str = Field(
        default="",
        description="Concise summary of required qualifications and education.",
    )
    red_flags: list[str] = Field(
        default_factory=list,
        description="Any red flags noticed (vague responsibilities, unrealistic requirements, etc.).",
    )
    green_flags: list[str] = Field(
        default_factory=list,
        description="Positive signals (salary transparency, clear growth path, etc.).",
    )


def create_jd_analyzer_subagent(
    tools: list | None = None,
    model_override: str | None = None,
) -> dict[str, Any]:
    """Return a JD Analyzer subagent for deep job description analysis.

    Uses Qwen 3.8 27B in thinking mode for thorough gap analysis of
    job descriptions. Extracts required skills, ATS keywords, tech stack,
    and flags to mirror in the tailored resume.

    Parameters
    ----------
    tools : list, optional
        Tools the subagent can use.
    model_override : str, optional
        Model identifier to override the default.
        Defaults to Qwen 3.8 27B (``openrouter:qwen/qwen3.8-27b:free``).

    Returns
    -------
    dict
        A subagent config with ``response_format`` set to ``JDAnalysis``.
    """
    subagent: dict[str, Any] = {
        "name": "jd-analyzer",
        "description": (
            "Performs deep analysis of job descriptions. Extracts required skills, "
            "nice-to-have skills, tech stack, ATS keywords, action verbs, experience "
            "level, and flags. Use this before resume tailoring to understand exactly "
            "what the JD demands."
        ),
        "system_prompt": (
            "You are an expert job description analyst and ATS specialist.\n\n"
            "Given a job description, perform a thorough analysis:\n"
            "1. Extract the company name and exact role title.\n"
            "2. Determine the experience/seniority level.\n"
            "3. Identify the domain/industry.\n"
            "4. Separate MUST-HAVE skills from NICE-TO-HAVE skills.\n"
            "5. List every specific technology, framework, and tool mentioned.\n"
            "6. Extract HIGH-PRIORITY ATS keywords — exact phrases the ATS will scan for.\n"
            "7. Note action verbs the JD uses (these should be mirrored in resume bullets).\n"
            "8. Summarise core responsibilities and required qualifications.\n"
            "9. Flag any red flags (vague duties, unrealistic requirements) "
            "and green flags (salary transparency, growth path).\n\n"
            "CRITICAL RULES:\n"
            "- ONLY extract information that is EXPLICITLY stated in the JD.\n"
            "- Do NOT infer, assume, or add skills/requirements that are not mentioned.\n"
            "- Do NOT hallucinate company details or role requirements.\n"
            "- If something is ambiguous, note it as ambiguous rather than guessing."
        ),
        "response_format": JDAnalysis,
    }
    if tools:
        subagent["tools"] = tools
    if model_override:
        subagent["model"] = _normalize_model_id(model_override)
    return subagent


# ---------------------------------------------------------------------------
#  2. Resume Tailor Subagent
# ---------------------------------------------------------------------------


class TailoredResume(BaseModel):
    """Structured output from the Resume Tailor subagent.

    Contains the fully tailored resume content alongside ATS analysis
    metrics. The Quality Judge subagent validates this output before
    it is presented to the user.
    """

    target_company: str = Field(
        description="Company the resume is tailored for.",
    )
    target_role: str = Field(
        description="Role the resume is tailored for.",
    )
    ats_keyword_score: float = Field(
        default=0.0,
        description=(
            "Estimated ATS keyword match score (0.0–1.0). "
            "Calculated as: matched_keywords / total JD keywords."
        ),
    )
    matched_keywords: list[str] = Field(
        default_factory=list,
        description="JD keywords successfully incorporated into the resume.",
    )
    missing_keywords: list[str] = Field(
        default_factory=list,
        description=(
            "Important JD keywords that could NOT be added because "
            "the user lacks the corresponding experience."
        ),
    )
    tailored_content: str = Field(
        description=(
            "The full tailored resume content in clean markdown format. "
            "Single-column, ATS-friendly structure."
        ),
    )
    changes_made: list[str] = Field(
        default_factory=list,
        description=(
            "List of specific changes made to the original resume "
            "(e.g. 'Rewrote bullet 3 in Experience #1 to include keyword X')."
        ),
    )
    improvement_notes: list[str] = Field(
        default_factory=list,
        description="Suggestions for further improvement the user could make manually.",
    )


def create_resume_tailor_subagent(
    tools: list | None = None,
    model_override: str | None = None,
) -> dict[str, Any]:
    """Return a Resume Tailor subagent for ATS-optimised resume generation.

    Uses Gemini 3.8 Flash for fast bullet-point rewriting. Takes a master
    resume + JD analysis and produces a tailored, ATS-optimised resume.

    Parameters
    ----------
    tools : list, optional
        Tools the subagent can use.
    model_override : str, optional
        Model identifier to override the default.

    Returns
    -------
    dict
        A subagent config with ``response_format`` set to ``TailoredResume``.
    """
    subagent: dict[str, Any] = {
        "name": "resume-tailor",
        "description": (
            "Takes a master resume and a JD analysis, then produces an "
            "ATS-optimised tailored resume. Performs keyword matching, "
            "bullet-point rewriting in Google XYZ format, section reordering, "
            "and ATS score calculation."
        ),
        "system_prompt": (
            "You are a professional resume writer and ATS optimisation expert.\n\n"
            "Given the user's ORIGINAL resume and a JD analysis, produce a tailored resume:\n\n"
            "PROCESS:\n"
            "1. Compare the user's existing skills and experience against the JD requirements.\n"
            "2. Identify which JD keywords ALREADY match the user's background.\n"
            "3. Rewrite bullet points using the Google XYZ format:\n"
            "   'Accomplished [X] as measured by [Y], by doing [Z]'\n"
            "4. Incorporate matched ATS keywords naturally into bullet points.\n"
            "5. Reorder resume sections to highlight the most relevant experience first.\n"
            "6. Produce a clean, single-column, ATS-friendly markdown resume.\n"
            "7. Calculate the ATS keyword match score.\n"
            "8. List all changes made so the user can review them.\n\n"
            "OUTPUT FORMAT:\n"
            "- The tailored_content must be clean markdown:\n"
            "  # Name\n"
            "  Contact info line\n"
            "  ## PROFESSIONAL SUMMARY\n"
            "  ## EXPERIENCE\n"
            "  ### Company — Title (Dates)\n"
            "  - Bullet points\n"
            "  ## PROJECTS\n"
            "  ## EDUCATION\n"
            "  ## SKILLS\n"
            "  ## CERTIFICATIONS\n\n"
            "CRITICAL ANTI-HALLUCINATION RULES:\n"
            "- NEVER add skills, experiences, projects, or achievements that are "
            "NOT present in the user's original resume.\n"
            "- NEVER fabricate metrics, numbers, percentages, or company names.\n"
            "- NEVER invent project names or technologies the user hasn't listed.\n"
            "- You may ONLY rephrase, reorder, and optimise EXISTING content.\n"
            "- If a JD keyword doesn't match the user's background, add it to "
            "'missing_keywords' — do NOT fabricate experience to fill the gap.\n"
            "- Every bullet point in the output MUST be traceable to the original resume.\n"
            "- In 'changes_made', document exactly what you changed and why."
        ),
        "response_format": TailoredResume,
    }
    if tools:
        subagent["tools"] = tools
    if model_override:
        subagent["model"] = _normalize_model_id(model_override)
    return subagent


# ---------------------------------------------------------------------------
#  3. Job Scout Subagent
# ---------------------------------------------------------------------------


class JobListing(BaseModel):
    """A single job listing discovered by the Job Scout."""

    company: str = Field(default="", description="Company name.")
    role_title: str = Field(default="", description="Job title.")
    location: str = Field(default="", description="Location (city, remote, hybrid).")
    salary_range: str = Field(default="", description="Salary range if available.")
    source_platform: str = Field(
        default="",
        description="Where the job was found (LinkedIn, Naukri, Indeed, etc.).",
    )
    apply_url: str = Field(default="", description="Direct application URL.")
    posted_date: str = Field(
        default="",
        description="When the job was posted (if available).",
    )
    fit_score: float = Field(
        default=0.0,
        description=(
            "Estimated fit score (0.0–1.0) based on: "
            "Hard Skills Match (40%) + Experience Level (30%) + "
            "Domain Familiarity (20%) + Tech Stack Overlap (10%)."
        ),
    )
    fit_reasoning: str = Field(
        default="",
        description="Brief explanation of why this role is a good/poor fit.",
    )


class JobSearchResults(BaseModel):
    """Structured job search results emitted by the Job Scout subagent."""

    search_query: str = Field(
        description="Summary of what was searched (role, location, level, type).",
    )
    total_found: int = Field(
        default=0, description="Total number of listings found.",
    )
    listings: list[JobListing] = Field(
        default_factory=list,
        description="Discovered job postings, ranked by fit score (highest first).",
    )
    top_recommendation: str = Field(
        default="",
        description="The single best-fit role and a brief explanation of why.",
    )
    search_tips: list[str] = Field(
        default_factory=list,
        description="Suggestions to refine the search if results are insufficient.",
    )


def create_job_scout_subagent(
    tools: list | None = None,
    model_override: str | None = None,
) -> dict[str, Any]:
    """Return a Job Scout subagent for searching job postings.

    Uses Gemini 3.8 Flash for fast search and analysis. Searches across
    LinkedIn, Naukri, Indeed, Greenhouse, Lever, and company career pages
    for recent postings (not older than 3 days).

    Parameters
    ----------
    tools : list, optional
        Tools the subagent can use (should include ``job_search``, ``web_search``).
    model_override : str, optional
        Model identifier to override the default.

    Returns
    -------
    dict
        A subagent config with ``response_format`` set to ``JobSearchResults``.
    """
    subagent: dict[str, Any] = {
        "name": "job-scout",
        "description": (
            "Searches for recent job openings across LinkedIn, Naukri, Indeed, "
            "Greenhouse, Lever, and company career pages. Evaluates each posting "
            "for fit and returns ranked, structured results ready for Excel export."
        ),
        "system_prompt": (
            "You are an expert job search specialist and tech recruiter.\n\n"
            "Given the user's job search criteria (role, experience level, "
            "location, job type), search for matching openings:\n\n"
            "PROCESS:\n"
            "1. Use the job_search tool to find postings across major job boards.\n"
            "2. Use web_search for additional results from company career pages.\n"
            "3. For each posting found, extract:\n"
            "   - Company name, role title, location, salary (if mentioned)\n"
            "   - Source platform (LinkedIn, Naukri, Indeed, etc.)\n"
            "   - Direct application URL\n"
            "4. Evaluate each posting's fit using this formula:\n"
            "   - Hard Skills Match: 40%\n"
            "   - Experience Level Match: 30%\n"
            "   - Domain Familiarity: 20%\n"
            "   - Tech Stack Overlap: 10%\n"
            "5. Rank results by fit score (highest first).\n"
            "6. Identify the single best recommendation.\n"
            "7. Save results to /jobs/search_results.json using write_file.\n\n"
            "FRESHNESS RULE:\n"
            "- ONLY include job postings from the LAST 3 DAYS.\n"
            "- Skip any postings that appear outdated or have been reposted.\n"
            "- If a posting date is unknown, include it but note 'Date unknown'.\n\n"
            "CRITICAL ANTI-HALLUCINATION RULES:\n"
            "- ONLY include REAL job postings with VERIFIABLE URLs.\n"
            "- NEVER generate fictional job listings or companies.\n"
            "- NEVER fabricate application URLs.\n"
            "- If you cannot find enough results, say so honestly and suggest "
            "alternative search terms rather than inventing listings.\n"
            "- Every apply_url MUST come directly from the search results."
        ),
        "response_format": JobSearchResults,
    }
    if tools:
        subagent["tools"] = tools
    if model_override:
        subagent["model"] = _normalize_model_id(model_override)
    return subagent


# ---------------------------------------------------------------------------
#  4. Interview Coach Subagent
# ---------------------------------------------------------------------------


class InterviewPrep(BaseModel):
    """Structured interview preparation from the Interview Coach subagent.

    Provides comprehensive preparation materials tailored to a specific
    company and role, covering technical, behavioral, and system design
    interview rounds.
    """

    company: str = Field(description="Company being prepared for.")
    role: str = Field(description="Target role.")
    company_insights: str = Field(
        default="",
        description=(
            "Key facts about the company: tech stack, engineering culture, "
            "recent news, funding, team size, products."
        ),
    )
    technical_questions: list[str] = Field(
        default_factory=list,
        description="8–10 probable technical interview questions based on the role and company.",
    )
    behavioral_questions: list[str] = Field(
        default_factory=list,
        description=(
            "5 likely behavioral questions, each with a suggested "
            "STAR-method answer angle from the user's experience."
        ),
    )
    system_design_topics: list[str] = Field(
        default_factory=list,
        description="3 system design topics the company is likely to test.",
    )
    coding_patterns: list[str] = Field(
        default_factory=list,
        description=(
            "Common algorithm/data structure patterns tested by this company "
            "(e.g. 'graph traversal', 'sliding window', 'dynamic programming')."
        ),
    )
    study_plan: str = Field(
        default="",
        description=(
            "A focused week-by-week study plan:\n"
            "Week 1–2: Fundamentals and core topics\n"
            "Week 3: Company-specific preparation\n"
            "Week 4: Mock interviews and revision"
        ),
    )
    salary_negotiation_tips: list[str] = Field(
        default_factory=list,
        description="3–5 salary negotiation talking points based on the role and market.",
    )


def create_interview_coach_subagent(
    tools: list | None = None,
    model_override: str | None = None,
) -> dict[str, Any]:
    """Return an Interview Coach subagent for comprehensive interview prep.

    Uses Gemini 3.8 Flash for fast research and question generation.
    Analyses the target company's tech stack, engineering blog, and
    role requirements to produce targeted preparation materials.

    Parameters
    ----------
    tools : list, optional
        Tools the subagent can use (should include ``web_search``).
    model_override : str, optional
        Model identifier to override the default.

    Returns
    -------
    dict
        A subagent config with ``response_format`` set to ``InterviewPrep``.
    """
    subagent: dict[str, Any] = {
        "name": "interview-coach",
        "description": (
            "Generates comprehensive interview preparation materials based on "
            "the target company and role. Covers technical questions, behavioral "
            "prep (STAR method), system design topics, and a study plan."
        ),
        "system_prompt": (
            "You are a senior technical interview coach with experience "
            "at top tech companies (FAANG, startups, and enterprises).\n\n"
            "Given a target company and role, generate comprehensive prep:\n\n"
            "PROCESS:\n"
            "1. RESEARCH the company using web_search:\n"
            "   - Tech stack (check StackShare, BuiltWith, engineering blog)\n"
            "   - Recent engineering blog posts and open-source projects\n"
            "   - Glassdoor interview reviews for this specific role\n"
            "   - Recent news, funding rounds, product launches\n"
            "2. Generate 8–10 TECHNICAL QUESTIONS based on:\n"
            "   - The role's required skills and tech stack\n"
            "   - Common patterns this company tests (from Glassdoor reviews)\n"
            "   - Industry-standard questions for this level\n"
            "3. Generate 5 BEHAVIORAL QUESTIONS with:\n"
            "   - The question itself\n"
            "   - A suggested STAR-method answer angle\n"
            "   (Situation → Task → Action → Result with quantified outcome)\n"
            "4. Identify 3 SYSTEM DESIGN topics they're likely to test:\n"
            "   - Based on the company's products and scale\n"
            "   - Include: Requirements → Estimation → API → Data Model → "
            "Architecture → Deep Dive → Trade-offs\n"
            "5. List common CODING PATTERNS they test.\n"
            "6. Create a FOCUSED STUDY PLAN:\n"
            "   - Week 1–2: Core fundamentals and data structures\n"
            "   - Week 3: Company-specific topics and mock system design\n"
            "   - Week 4: Mock interviews, revision, and confidence building\n"
            "7. Provide SALARY NEGOTIATION tips based on market rate.\n\n"
            "Save all prep materials to /interview-prep/ using write_file.\n\n"
            "CRITICAL ANTI-HALLUCINATION RULES:\n"
            "- Base company insights on REAL, VERIFIABLE information from search results.\n"
            "- Clearly DISTINGUISH between confirmed facts and reasonable assumptions.\n"
            "- Do NOT fabricate Glassdoor reviews or interview experiences.\n"
            "- If you cannot find specific company data, state that clearly "
            "and provide general industry-standard preparation instead.\n"
            "- Cite sources when referencing specific company information."
        ),
        "response_format": InterviewPrep,
    }
    if tools:
        subagent["tools"] = tools
    if model_override:
        subagent["model"] = _normalize_model_id(model_override)
    return subagent


# ---------------------------------------------------------------------------
#  5. Quality Judge Subagent (LLM-as-Judge)
# ---------------------------------------------------------------------------


class QualityIssue(BaseModel):
    """A single quality issue found by the Judge."""

    severity: str = Field(
        description="Issue severity: 'critical', 'warning', or 'info'.",
    )
    category: str = Field(
        description=(
            "Issue category: 'hallucination', 'ats_violation', "
            "'missing_content', 'factual_error', 'formatting'."
        ),
    )
    description: str = Field(
        description="What the issue is and where it was found.",
    )
    fix_suggestion: str = Field(
        default="",
        description="How to fix this issue.",
    )


class QualityVerdict(BaseModel):
    """Structured quality assessment from the Quality Judge subagent.

    The Judge compares the tailored resume against the original master
    resume and the JD analysis to catch hallucinations, ATS violations,
    and quality issues before output reaches the user.
    """

    passed: bool = Field(
        description=(
            "True if the output is acceptable quality with no critical issues. "
            "False if there are critical issues that must be fixed."
        ),
    )
    overall_score: float = Field(
        default=0.0,
        description="Quality score from 0.0 (terrible) to 1.0 (perfect).",
    )
    ats_compliance_score: float = Field(
        default=0.0,
        description=(
            "ATS format compliance score (0.0–1.0). "
            "Checks: single-column, no graphics, standard headings, keyword presence."
        ),
    )
    hallucination_check: str = Field(
        default="",
        description=(
            "Summary of hallucination check results. "
            "'CLEAN' if no fabricated content found, or a description of what was fabricated."
        ),
    )
    issues: list[QualityIssue] = Field(
        default_factory=list,
        description="List of specific quality issues found, ordered by severity.",
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="What the output does well.",
    )
    verdict_summary: str = Field(
        default="",
        description="One-paragraph summary of the quality assessment.",
    )


def create_quality_judge_subagent(
    tools: list | None = None,
    model_override: str | None = None,
) -> dict[str, Any]:
    """Return a Quality Judge subagent (LLM-as-Judge) for output validation.

    Uses Qwen 3.8 27B for deep reasoning. Validates output from every
    other career subagent by checking for hallucinations, ATS compliance,
    factual accuracy, and completeness.

    Parameters
    ----------
    tools : list, optional
        Tools the subagent can use.
    model_override : str, optional
        Model identifier to override the default.

    Returns
    -------
    dict
        A subagent config with ``response_format`` set to ``QualityVerdict``.
    """
    subagent: dict[str, Any] = {
        "name": "quality-judge",
        "description": (
            "LLM-as-Judge that validates output quality. Compares tailored resumes "
            "against the original to catch hallucinations, checks ATS compliance, "
            "verifies factual accuracy, and ensures completeness. Returns a "
            "pass/fail verdict with detailed issues."
        ),
        "system_prompt": (
            "You are a rigorous quality assurance judge for career documents.\n\n"
            "Your job is to VALIDATE output from other agents by performing "
            "5 critical checks:\n\n"
            "CHECK 1 — HALLUCINATION DETECTION (most important):\n"
            "- Compare EVERY claim in the tailored resume against the original.\n"
            "- Flag any skill, project, experience, metric, or achievement that "
            "does NOT appear in the user's original resume.\n"
            "- Flag any fabricated company names, job titles, or dates.\n"
            "- Flag any invented percentages, numbers, or impact metrics.\n"
            "- If ANYTHING is fabricated, set passed=False and severity='critical'.\n\n"
            "CHECK 2 — ATS COMPLIANCE:\n"
            "- Verify single-column layout (no multi-column formatting).\n"
            "- Verify standard section headings (Summary, Experience, Education, Skills).\n"
            "- Verify no tables, graphics, or text boxes.\n"
            "- Verify clean markdown formatting.\n"
            "- Check that JD keywords are naturally incorporated.\n\n"
            "CHECK 3 — COMPLETENESS:\n"
            "- All sections from the original resume are present.\n"
            "- No experience entries were accidentally dropped.\n"
            "- Contact information is preserved.\n"
            "- Skills section is comprehensive.\n\n"
            "CHECK 4 — FACTUAL ACCURACY:\n"
            "- Technical terms are spelled correctly.\n"
            "- Technology names use correct casing (e.g. 'PyTorch' not 'pytorch').\n"
            "- Dates and timelines are consistent.\n\n"
            "CHECK 5 — KEYWORD COVERAGE:\n"
            "- Check what percentage of JD keywords are in the tailored resume.\n"
            "- Flag important keywords that are missing.\n"
            "- Verify keywords are used naturally, not stuffed.\n\n"
            "SCORING:\n"
            "- overall_score: weighted average of all checks\n"
            "- ats_compliance_score: 0.0–1.0 based on Check 2\n"
            "- passed: False if ANY critical issues exist\n\n"
            "IMPORTANT:\n"
            "- Be STRICT. Your purpose is to catch errors before the user sees them.\n"
            "- Every issue must have a concrete fix_suggestion.\n"
            "- If the output is clean, say so — don't manufacture issues."
        ),
        "response_format": QualityVerdict,
    }
    if tools:
        subagent["tools"] = tools
    if model_override:
        subagent["model"] = _normalize_model_id(model_override)
    return subagent


# ---------------------------------------------------------------------------
#  Career Subagent Bundle
# ---------------------------------------------------------------------------


def get_career_subagents(
    tools: list | None = None,
) -> list[dict[str, Any]]:
    """Return all career-focused subagents as a list.

    Parameters
    ----------
    tools : list, optional
        Tools shared by the career subagents.

    Returns
    -------
    list[dict]
        List of career subagent configuration dicts.
    """
    return [
        create_jd_analyzer_subagent(tools=tools),
        create_resume_tailor_subagent(tools=tools),
        create_job_scout_subagent(tools=tools),
        create_interview_coach_subagent(tools=tools),
        create_quality_judge_subagent(tools=tools),
    ]





