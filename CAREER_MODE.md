# 📄 Career Mode — Technical Documentation

> Complete technical reference for the Career Intelligence Suite in Deep Agents.
> Explains **what** each component does, **why** it was designed that way, and
> **what could be better** with alternative approaches.

---

## Table of Contents

- [Overview](#overview)
- [Pipeline Architecture](#pipeline-architecture)
- [Model Selection & Routing](#model-selection--routing)
- [Tools](#tools)
  - [Resume Parser](#1-resume-parser)
  - [Job Extractor](#2-job-extractor)
  - [GitHub Analyzer](#3-github-analyzer)
  - [Resume Exporter](#4-resume-exporter)
  - [Job Search](#5-job-search)
- [Subagents](#subagents)
  - [JD Analyzer](#1-jd-analyzer)
  - [Resume Tailor](#2-resume-tailor)
  - [Job Scout](#3-job-scout)
  - [Interview Coach](#4-interview-coach)
  - [Quality Judge](#5-quality-judge-llm-as-judge)
- [Skills](#skills)
- [Anti-Hallucination Protocol](#anti-hallucination-protocol)
- [ATS Template Design](#ats-template-design)
- [UI Architecture](#ui-architecture)
- [Trade-offs & Future Improvements](#trade-offs--future-improvements)

---

## Overview

Career Mode transforms Deep Agents from a general-purpose chatbot into a
**career intelligence system**. The user provides their resume and a job
description, and the system produces a tailored, ATS-optimised resume through
a multi-agent pipeline where each agent specialises in one task.

### Core Workflow

```
User Resume (PDF/DOCX/TXT)  ──┐
                               ├──→ [JD Analyzer] ──→ [Resume Tailor] ──→ [Quality Judge] ──→ Results
Job Description (URL/Text) ───┘                              ↑
                                                             │
GitHub Profile (optional) ───────────────────────────────────┘
```

### Design Principles

1. **Modularity** — Each tool and subagent is an independent, testable unit.
2. **Anti-hallucination** — Every component enforces strict rules against fabricating content.
3. **Smart routing** — The right LLM for each task (parsing ≠ analysis ≠ rewriting).
4. **Professional output** — ATS-compliant templates based on industry research.
5. **User control** — Preview before download, change tracking, score visibility.

---

## Pipeline Architecture

The resume tailoring pipeline executes 7 steps in sequence:

| Step | Component | Type | Input | Output |
|---|---|---|---|---|
| 1 | `resume_parser` | Tool | PDF/DOCX/TXT/MD file | Extracted text |
| 2 | `job_extractor` | Tool | URL or pasted text | Structured JD content |
| 3 | `jd-analyzer` | Subagent | Raw JD text | `JDAnalysis` (14 fields) |
| 4 | `github_analyzer` | Tool | Username or repo URLs | Resume bullet points |
| 5 | `resume-tailor` | Subagent | Resume + JDAnalysis | `TailoredResume` (8 fields) |
| 6 | `quality-judge` | Subagent | Original + Tailored | `QualityVerdict` (pass/fail) |
| 7 | `resume_exporter` | Tool | Tailored markdown | PDF + DOCX bytes |

**Why sequential, not parallel?** Each step depends on the output of the
previous step. The JD Analyzer's keywords feed into the Resume Tailor's
rewriting logic, and the Quality Judge needs both the original and tailored
resume to perform diff-based hallucination detection.

---

## Model Selection & Routing

### Why These 3 Models (+ 1 Fallback)?

| Model | Provider | Cost | Why Chosen |
|---|---|---|---|
| **Qwen 3.8 27B** | OpenRouter (primary) / Groq (fallback) | Free | "Thinking mode" enables deep chain-of-thought reasoning. Best for analytical tasks (JD analysis, quality judging) where thoroughness matters more than speed. Also handles technical accuracy for coding/engineering resumes. |
| **Gemini 3.8 Flash** | Google AI Studio | Free | Fastest "intelligent" flash model. Approaches frontier performance while being fast enough for real-time bullet rewriting and interview question generation. |
| **Gemma 4 31B** | Google AI Studio | Free | Top-tier document extraction and multimodal understanding. Best for parsing complex PDF/DOCX layouts with tables, columns, and varied formatting. |

### Routing Map

```
Document Parsing ──────→ Gemma 4 31B      (multimodal, layout understanding)
JD Deep Analysis ──────→ Qwen 3.8 27B     (thinking mode, exhaustive extraction)
Bullet Rewriting ──────→ Gemini 3.8 Flash  (fast, natural language generation)
Technical CVs ─────────→ Qwen 3.8 27B     (technical term precision + reasoning)
Quality Judging ───────→ Qwen 3.8 27B     (reasoning about correctness)
Interview Prep ────────→ Gemini 3.8 Flash  (fast research + generation)
Job Search ────────────→ Gemini 3.8 Flash  (fast tool calling)
```

### Provider Fallback: OpenRouter → Groq

OpenRouter's free tier can occasionally go down, hit rate limits, or respond
slowly. Since Qwen 3.8 27B powers 3 of the 5 career subagents (JD Analyzer,
Quality Judge, and coding accuracy), an OpenRouter outage would break the
entire resume tailoring pipeline. Groq solves this as an automatic fallback.

#### How It Works

```
User request
    │
    ▼
get_model_id() / get_model_for_role()
    │
    ▼
resolve_model_id("openrouter:qwen/qwen3.8-27b:free")
    │
    ├── Is GROQ_API_KEY set?
    │       │
    │       No ──→ return OpenRouter ID (no fallback available)
    │       │
    │       Yes
    │       │
    │       ▼
    │   Is OpenRouter healthy?  ←── cached health check (2 min TTL)
    │       │
    │       Yes ──→ return "openrouter:qwen/qwen3.8-27b:free"
    │       │
    │       No
    │       │
    │       ▼
    │   return "groq:qwen/qwen3.8-27b"  ← automatic swap
    │
    └── Not an OpenRouter model? ──→ return unchanged
```

#### Implementation Details

| Component | Detail |
|---|---|
| **Config:** `FALLBACK_MAP` | Maps `openrouter:qwen/qwen3.8-27b:free` → `groq:qwen/qwen3.8-27b` |
| **Health check:** `_is_openrouter_available()` | Hits `GET /api/v1/auth/key` with a 5-second timeout |
| **Cache:** `_openrouter_health` | Result cached for 120 seconds to avoid checking on every LLM call |
| **Resolution:** `resolve_model_id()` | Called by both `get_model_id()` and `get_model_for_role()` — every model resolution goes through fallback logic |
| **Activation:** | Fallback only activates if `GROQ_API_KEY` is set in `.env` or Streamlit secrets |

#### Design Decisions

**Why Groq as the fallback (not another provider)?**
- Groq hosts the exact same model (`qwen/qwen3.8-27b`) so output quality is identical.
- Groq has the fastest inference speed of any provider (LPU hardware), so the
  fallback is actually *faster* than the primary.
- Groq's free tier is generous (14,400 tokens/min for Qwen).
- No prompt or configuration changes needed — same model, different endpoint.

**Why not use Groq as primary?**
- Groq's free tier has stricter rate limits than OpenRouter's for sustained use.
- OpenRouter's `:free` tier has higher daily quotas for long sessions.
- Using OpenRouter as primary preserves Groq capacity for when it's truly needed.

**Why a health check instead of try/catch retry?**
- A failed LLM call inside `create_deep_agent()` can take 30+ seconds to timeout.
- The health check (`GET /auth/key`) takes < 1 second and is cached for 2 minutes.
- This gives instant failover without the user waiting for a timeout on every request.

**Why cache for 2 minutes?**
- Short enough to recover quickly when OpenRouter comes back.
- Long enough to avoid hammering the health endpoint on every chat message.
- A single resume tailoring pipeline makes ~5-8 LLM calls, so the cache
  ensures consistent routing throughout a single operation.

### Why Not GPT / Claude / Other Paid Models?

All selected models are **free-tier** endpoints, making the system accessible
without API billing. The `:free` suffix on OpenRouter model IDs selects the
free-tier endpoint. For production use, paid tiers would offer higher rate
limits and lower latency.

### Alternatives Considered

| Alternative | Why Not Used |
|---|---|
| GPT-4o | Paid, not significantly better for resume tasks |
| Claude 3.5 | Paid, excellent but cost-prohibitive for free tool |
| Llama 3.1 70B | Strong but Qwen 3.8's thinking mode is better for analysis |
| DeepSeek V4 Flash | Good technical precision but adds a fourth model; Qwen handles it well enough |

---

## Tools

### 1. Resume Parser

**File:** `src/deep_agents/tools/resume_parser.py`

**What it does:** Extracts text from uploaded resume files (PDF, DOCX, TXT, MD)
and structures it into a `ResumeProfile` Pydantic model.

**Design decisions:**
- **PyMuPDF (`fitz`) for PDF** — 10x faster than `pdfplumber`, handles most layouts well.
  Could be better: `pdfplumber` preserves table structures better for complex resumes.
- **`python-docx` for DOCX** — Standard library, handles paragraphs and tables.
  Could be better: Doesn't handle headers/footers or complex formatting.
- **Two entry points** — `parse_resume_file()` for uploaded files, `create_resume_parser_tool()`
  for pasted text in chat. This separation keeps the tool registry clean.

**Pydantic models:**
- `ResumeProfile` — name, email, phone, linkedin, github, summary, skills, experiences, education, projects, certifications
- `ExperienceEntry` — company, title, location, start_date, end_date, bullets
- `EducationEntry` — institution, degree, field, graduation_date, gpa
- `ProjectEntry` — name, description, technologies, url

### 2. Job Extractor

**File:** `src/deep_agents/tools/job_extractor.py`

**What it does:** Extracts structured job posting data from either a URL
(scrapes via Tavily) or pasted text.

**Design decisions:**
- **Tavily for URL scraping** — Handles JavaScript-rendered pages (LinkedIn, Greenhouse)
  that simple HTTP requests can't. Falls back gracefully if scraping fails.
  Could be better: Direct API integrations with LinkedIn/Naukri would be more reliable
  but require authentication and may violate ToS.
- **Auto-detection** — Checks if input starts with `http` to decide URL vs text mode.
  Simple but effective.

**Pydantic model:**
- `JobPosting` — company, role_title, location, employment_type, experience_level,
  salary_range, required_skills, nice_to_have, tech_stack, responsibilities, description

### 3. GitHub Analyzer

**File:** `src/deep_agents/tools/github_analyzer.py`

**What it does:** Fetches public GitHub data and generates resume-ready project
bullet points.

**Design decisions:**
- **Public API, no auth** — 60 requests/hour is enough for resume building.
  Could be better: Authenticated requests get 5,000/hour, needed if many users share one server.
- **`urllib` instead of `requests`** — Avoids adding a dependency for a simple HTTP client.
  Could be better: `httpx` would be cleaner and support async.
- **Skips forks** — Only original repos are relevant for resume projects.
- **Auto-generates bullet points** — Based on repo name, description, language, stars.
  These are SUGGESTIONS — the anti-hallucination rule requires users to verify.

**Pydantic models:**
- `GitHubProfile` — username, name, bio, public_repos, followers, total_stars, languages, top_repos
- `GitHubRepo` — name, description, language, stars, forks, topics, url

### 4. Resume Exporter

**File:** `src/deep_agents/tools/resume_exporter.py`

**What it does:** Converts tailored markdown resume into downloadable PDF and DOCX.

**Design decisions:**
- **WeasyPrint for PDF** — Produces high-quality CSS-styled PDFs. Renders markdown
  via a custom ATS CSS template.
  Could be better: WeasyPrint requires system libraries (Pango, Cairo) which complicates
  deployment. `reportlab` is pure Python but produces uglier output. `wkhtmltopdf` is
  another option but has its own dependencies.
- **`python-docx` for DOCX** — Generates proper Word documents with styles, not just
  text dumps. Users can edit the DOCX after download.
  Could be better: A proper Word template (`.dotx`) would give more consistent styling.
- **ATS CSS template** — See [ATS Template Design](#ats-template-design) for details.

### 5. Job Search

**File:** `src/deep_agents/tools/search.py` (`create_job_search_tool`)

**What it does:** Searches for recent job postings using Tavily, with results
filtered for freshness.

**Design decisions:**
- **3-day freshness filter** — Job postings older than 3 days are less likely to be
  open. This is enforced in the prompt, not via API parameter (Tavily doesn't support
  date filtering directly).
  Could be better: Direct job board APIs (LinkedIn API, Indeed API) would give exact
  posting dates and more structured data. However, these require partnership agreements.
- **Source detection** — Identifies LinkedIn/Naukri/Indeed from URL patterns.
- **Fit scoring** — Calculated by the Job Scout subagent using a weighted formula,
  not by this tool. The tool provides raw data; the subagent provides intelligence.

---

## Subagents

All 5 career subagents follow the same pattern:
- A **Pydantic model** defining the structured output schema
- A **factory function** that returns a config dict for `create_deep_agent(subagents=[...])`
- A **system prompt** with step-by-step instructions and anti-hallucination rules

### 1. JD Analyzer

**Output:** `JDAnalysis` (14 fields)

**What it extracts:**
- Company, role title, experience level, domain
- Hard skills vs soft skills vs nice-to-have
- Tech stack (every technology/framework/tool mentioned)
- **ATS keywords** — exact phrases the ATS will scan for
- Action verbs to mirror in resume bullets
- Red flags (vague duties, unrealistic requirements)
- Green flags (salary transparency, clear growth path)

**Why Qwen 3.8 27B?** The "thinking mode" (chain-of-thought reasoning) produces
significantly more thorough extraction than a fast model. JD analysis is a one-time
step, so latency is acceptable.

### 2. Resume Tailor

**Output:** `TailoredResume` (8 fields)

**What it does:**
- Rewrites bullet points in **Google XYZ format**: "Accomplished [X] as measured by [Y], by doing [Z]"
- Maximises ATS keyword overlap with the JD
- Reorders sections to highlight relevant experience first
- Calculates `ats_keyword_score` (matched / total JD keywords)
- Tracks every change in `changes_made` for user review
- Lists `missing_keywords` — skills the JD wants but the user doesn't have

**Why this is the most critical subagent:** The resume tailor is where hallucination
risk is highest. A model might be tempted to add impressive-sounding skills the user
doesn't have. That's why 7 explicit anti-hallucination rules are in its system prompt,
and every output goes through the Quality Judge.

### 3. Job Scout

**Output:** `JobSearchResults` with nested `JobListing` objects

**What it does:**
- Uses `job_search` + `web_search` tools to find postings
- Extracts: company, role, location, salary, source, apply URL
- Evaluates fit using a weighted formula:
  - Hard Skills Match: 40%
  - Experience Level: 30%
  - Domain Familiarity: 20%
  - Tech Stack Overlap: 10%
- Ranks by fit score, identifies single best recommendation

**Why the fit formula?** Pure keyword matching favours generic postings. The weighted
formula ensures that a Senior ML Engineer posting at a fintech company scores higher
for a senior ML engineer with fintech experience than a generic "engineer" posting
that happens to mention more keywords.

### 4. Interview Coach

**Output:** `InterviewPrep` (9 fields)

**What it generates:**
- 8–10 technical questions based on role + company tech stack
- 5 behavioral questions with STAR-method answer angles
- 3 system design topics based on company products
- Common coding patterns the company tests
- 4-week study plan
- Salary negotiation talking points

**Why Gemini 3.8 Flash?** Interview prep requires web research (company blog,
Glassdoor reviews, StackShare) which involves many tool calls. A fast model
keeps the total latency reasonable.

### 5. Quality Judge (LLM-as-Judge)

**Output:** `QualityVerdict` with nested `QualityIssue` objects

**5 checks performed:**
1. **Hallucination detection** — Compares every claim against the original resume
2. **ATS compliance** — Single-column, standard headings, no graphics
3. **Completeness** — No sections dropped, contact info preserved
4. **Factual accuracy** — Tech terms spelled correctly, dates consistent
5. **Keyword coverage** — What percentage of JD keywords are present

**Why Qwen 3.8 27B?** Quality judging requires careful comparison and reasoning
about whether specific claims are fabricated. The thinking mode excels at this
kind of analytical comparison.

**Why not just trust the Resume Tailor?** All LLMs occasionally hallucinate.
Having a separate model review the output catches errors that the generating
model would "blind spot" on. This is the same principle behind code review —
a different perspective catches what the author missed.

---

## Skills

Skills are instruction files loaded into the agent's virtual filesystem.

### `ats-resume/SKILL.md`

Contains:
- Single-column layout rules (and why multi-column fails ATS)
- Google XYZ bullet format with examples
- Strong action verbs categorised by type (Engineering, Impact, Leadership)
- Keyword strategy (mirror exact phrases, use both forms)
- Comprehensive "what to avoid" checklist
- Anti-hallucination rule

### `interview-prep/SKILL.md`

Contains:
- STAR method framework with worked example
- 7-step system design framework (Requirements → Trade-offs)
- Common question categories (Algorithms, System Design, Behavioral, ML-specific)
- Company research checklist (8 items)
- 4-week study plan template
- Salary negotiation basics

---

## Anti-Hallucination Protocol

The #1 design priority. These 7 rules are enforced at every level:

| # | Rule | Where Enforced |
|---|---|---|
| 1 | NEVER add content not in the original resume | Resume Tailor system prompt |
| 2 | NEVER fabricate metrics/numbers/percentages | Resume Tailor + Quality Judge |
| 3 | NEVER invent project/company/technology names | Resume Tailor + Quality Judge |
| 4 | NEVER generate fictional job listings | Job Scout system prompt |
| 5 | NEVER fabricate Glassdoor reviews | Interview Coach system prompt |
| 6 | FLAG, don't fill — missing skills go to "Missing Keywords" | Resume Tailor + Career Copilot prompt |
| 7 | Quality Judge reviews ALL output before user sees it | Pipeline architecture |

**Why is this so important?** A fabricated skill on a resume can:
- Get a candidate hired for a role they can't perform → termination
- Be caught during interview → immediate rejection
- Be caught during background check → blacklisted
- Damage the user's professional reputation permanently

---

## ATS Template Design

### Research Basis

The template design is based on analysis of how major ATS platforms parse resumes:

| ATS Platform | Market Share | Key Parsing Rule |
|---|---|---|
| Workday | ~35% | Reads single-column, left-to-right |
| Greenhouse | ~20% | Struggles with tables and text boxes |
| Taleo (Oracle) | ~15% | Ignores headers/footers |
| Lever | ~10% | Handles markdown reasonably well |

### Template Specifications

| Property | Value | Rationale |
|---|---|---|
| Layout | Single-column | All ATS parse correctly |
| Font | Calibri (primary), Arial (fallback) | Universally supported, professional |
| Body size | 11pt | Readable on screen and print |
| Heading size | 13–14pt | Clear hierarchy without wasting space |
| Margins | 1 inch (2.54cm) all sides | Professional standard |
| Page size | A4 | International standard |
| Section order | Summary → Experience → Projects → Education → Skills | Reverse-chronological, recruiter-preferred |

### What to Avoid (and Why)

| Element | Why It Breaks ATS |
|---|---|
| Multi-column layouts | ATS reads cells left-to-right, jumbling content |
| Graphics/icons | ATS ignores all images |
| Tables | Many ATS flatten tables into nonsensical text |
| Headers/footers | ATS can't read page headers (contact info gets lost) |
| Text boxes | ATS treats these as separate document fragments |

---

## UI Architecture

The Streamlit app uses 3 tabs:

### Tab 1: General Chat
- Existing conversational AI (unchanged from v1)
- Telemetry bar showing model, backend, subagents, search status
- Starter cards for quick actions

### Tab 2: Resume Tailor
- Left column: Resume upload (PDF/DOCX/TXT/MD) + paste fallback
- Right column: JD input (paste or URL) + GitHub username
- Single "Tailor My Resume" button
- Status progress: Parsing → Analysing → Tailoring → Quality Check → Done
- Results: Preview + ATS score + download buttons (PDF, DOCX, MD)
- "Prepare for Interview" follow-up button

### Tab 3: Job Search
- Input fields: Role, Location, Experience, Type
- "Search Jobs" button
- Results displayed as formatted text with apply links
- Download button for offline review

---

## Trade-offs & Future Improvements

### Current Trade-offs

| Decision | Trade-off | Potential Improvement |
|---|---|---|
| Free-tier models only | Rate limits (60 req/hr GitHub, limited LLM throughput) | Add paid tier option for power users |
| Tavily for JD scraping | Can't scrape all pages (authentication walls) | Direct job board API integrations |
| WeasyPrint for PDF | Requires system libraries | Switch to `weasyprint` via Docker or use `fpdf2` |
| Sequential pipeline | Slower than parallel execution | Parallelise JD analysis + GitHub fetch (independent steps) |
| Prompt-based freshness | No guarantee of 3-day filter accuracy | Use job board APIs with date parameters |

### Feature Roadmap

- [ ] **Resume version history** — track multiple tailored versions
- [ ] **A/B resume testing** — generate 2 variants, let user pick
- [ ] **Cover letter generator** — using same JD analysis
- [ ] **LinkedIn profile optimiser** — tailor headline + summary
- [ ] **Excel export for job search** — structured spreadsheet with all fields
- [ ] **Batch tailoring** — one resume → multiple JDs
- [ ] **OAuth login** — save user profile and resume history
- [ ] **Direct apply** — submit applications from within the app

---

## Author

- **Viplove Thakran** ([@Viplove0114](https://github.com/Viplove0114))
- **Email**: viplovethakran4@gmail.com
