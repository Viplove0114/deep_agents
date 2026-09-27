"""
Deep Agents — Agent Construction Utilities.

Provides the agent factory and all subagent definitions, including
both research-focused and career-focused subagents.
"""

from deep_agents.agents.factory import create_agent_instance
from deep_agents.agents.subagents import (
    # Research subagents
    ResearchFindings,
    create_light_research_subagent,
    create_research_subagent,
    create_structured_research_subagent,
    # Career subagents
    JDAnalysis,
    TailoredResume,
    JobListing,
    JobSearchResults,
    InterviewPrep,
    QualityIssue,
    QualityVerdict,
    create_jd_analyzer_subagent,
    create_resume_tailor_subagent,
    create_job_scout_subagent,
    create_interview_coach_subagent,
    create_quality_judge_subagent,
    # Bundles
    get_default_subagents,
    get_career_subagents,
)

__all__ = [
    # Factory
    "create_agent_instance",
    # Research subagents
    "create_light_research_subagent",
    "create_research_subagent",
    "create_structured_research_subagent",
    "ResearchFindings",
    # Career subagents
    "create_jd_analyzer_subagent",
    "create_resume_tailor_subagent",
    "create_job_scout_subagent",
    "create_interview_coach_subagent",
    "create_quality_judge_subagent",
    # Career models
    "JDAnalysis",
    "TailoredResume",
    "JobListing",
    "JobSearchResults",
    "InterviewPrep",
    "QualityIssue",
    "QualityVerdict",
    # Bundles
    "get_default_subagents",
    "get_career_subagents",
]
