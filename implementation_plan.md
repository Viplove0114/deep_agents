# Deep Agents → ATS Resume Tailor — Final Plan (v3)

> **Nothing will be built until you say go.**

---

## Core Concept

A career tool with two modes: **General Chat** (existing) + **Career Mode** (new tab).

Career Mode workflow:

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUTS                              │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │ Upload Resume│  │ Paste JD or  │  │ GitHub Links      │ │
│  │ PDF/DOCX/    │  │ Paste JD URL │  │ (optional)        │ │
│  │ TXT/MD       │  │ LinkedIn,    │  │                   │ │
│  │              │  │ Naukri, etc. │  │                   │ │
│  └──────────────┘  └──────────────┘  └───────────────────┘ │
│                                                             │
│              ┌─────────────────────┐                        │
│              │ ✦ Tailor My Resume  │                        │
│              └─────────┬───────────┘                        │
└────────────────────────┼────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  AGENT PIPELINE                             │
│                                                             │
│  Gemma 4 31B ──► Parse resume into structured sections      │
│                                                             │
│  Qwen 3.8 27B ─► Deep JD analysis (keywords, gaps, skills) │
│                                                             │
│  Gemini 3.8 Flash ► Rewrite bullets, optimize keywords      │
│  DeepSeek V4 Flash► Polish technical sections               │
│                                                             │
│  Quality Judge ──► Reviews output: "Is this accurate?       │
│                    Any hallucinated content? ATS score?"     │
└─────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    RESULTS                                  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Preview: Tailored resume in clean markdown          │   │
│  │ ATS Score: 87% ███████████░░░                       │   │
│  │ Matched Keywords: [Python] [LangChain] [AWS] ...    │   │
│  │ Missing Keywords: [Kubernetes] [Terraform]          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ ⬇ Download   │  │ ⬇ Download   │                        │
│  │    PDF       │  │    DOCX      │                        │
│  └──────────────┘  └──────────────┘                        │
│                                                             │
│  ┌──────────────────────────┐                               │
│  │ 🎯 Prepare for Interview │                               │
│  └──────────────────────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

### Separate Feature: Job Search

```
┌──────────────────────────────────────────┐
│  Job Search Mode                         │
│                                          │
│  Role: [AI Engineer         ]            │
│  Experience: [2-4 years     ]            │
│  Location: [Remote / Bangalore]          │
│  Type: [Full-time           ]            │
│                                          │
│  ┌─────────────────────┐                 │
│  │ 🔍 Search Jobs      │                 │
│  └─────────┬───────────┘                 │
│            ▼                             │
│  Searches: LinkedIn, Naukri, Indeed,     │
│  Greenhouse, Lever, company career pages │
│            ▼                             │
│  ┌─────────────────────┐                 │
│  │ ⬇ Download Excel    │                 │
│  │   (with apply links)│                 │
│  └─────────────────────┘                 │
└──────────────────────────────────────────┘
```

---

## Models (All Others Removed)

| Model | Provider | Model ID | Role |
|---|---|---|---|
| **Qwen 3.8 27B** | OpenRouter | `qwen/qwen3.8-27b` | Default orchestrator. Deep JD gap analysis (thinking mode) |
| **Gemini 3.8 Flash** | Google AI Studio | `gemini-3.8-flash` | Fast reasoning, bullet rewriting, research, interview prep |
| **Gemma 4 31B** | Google AI Studio | `gemma-4-31b-it` | Document parsing (PDF/DOCX), multimodal understanding |
| **DeepSeek V4 Flash** | OpenRouter | `deepseek/deepseek-v4-flash-0731` | Technical CV sections, coding terminology accuracy |

### Dependencies

```
langchain-google-genai    # Gemini 3.8 Flash + Gemma 4 31B
langchain-openrouter      # Qwen 3.8 27B + DeepSeek V4 Flash
```

**Removed:** `langchain-groq`, `langchain-openai`

### API Keys Needed (all free)

| Key | Where to Get |
|---|---|
| `GOOGLE_API_KEY` | https://aistudio.google.com/apikey |
| `OPENROUTER_API_KEY` | https://openrouter.ai/keys |
| `TAVILY_API_KEY` | Already have |

---

## Phase 1: Config & Dependencies

### [MODIFY] `src/deep_agents/config.py`

- Replace `AVAILABLE_MODELS` with the 4 models above
- Change `DEFAULT_MODEL` to `"openrouter:qwen/qwen3.8-27b"`
- Add `GOOGLE_API_KEY` and `OPENROUTER_API_KEY` to `load_environment()`
- Add a `MODEL_ROLES` dict mapping task → model for smart routing:
  ```python
  MODEL_ROLES = {
      "orchestrator": "openrouter:qwen/qwen3.8-27b",
      "document_parsing": "google_genai:gemma-4-31b-it",
      "fast_reasoning": "google_genai:gemini-3.8-flash",
      "coding_accuracy": "openrouter:deepseek/deepseek-v4-flash-0731",
  }
  ```

### [MODIFY] `pyproject.toml` & `requirements.txt`

Add:
```
langchain-google-genai
langchain-openrouter
pymupdf                # PDF parsing
python-docx            # DOCX parsing + export
weasyprint             # Markdown → PDF export
markdown               # Markdown → HTML
openpyxl               # Excel export for job search results
```

Remove: `langchain-groq`, `langchain-openai`

### [NEW] `packages.txt` (root of project)

Required for Streamlit Cloud to install WeasyPrint's system dependencies:
```
libpango-1.0-0
libpangocairo-1.0-0
libpangoft2-1.0-0
libffi-dev
shared-mime-info
```

### [MODIFY] `.env`

```env
TAVILY_API_KEY=your-existing-key
GOOGLE_API_KEY=your-google-ai-studio-key
OPENROUTER_API_KEY=your-openrouter-key
```

---

## Phase 2: Tools (5 tools)

### [NEW] `src/deep_agents/tools/resume_parser.py`

**Reads uploaded resumes in any format → clean structured text.**

- `.pdf` → uses `pymupdf` (fitz) to extract text
- `.docx` → uses `python-docx` to extract paragraphs
- `.txt` / `.md` → plain read
- Returns extracted text + instructs the LLM to structure it into `ResumeProfile` (Pydantic model with: name, email, skills, experience, education, projects, etc.)
- The LLM (Gemma 4 31B) does the intelligent structuring — the tool just handles file format conversion to text

### [NEW] `src/deep_agents/tools/job_extractor.py`

**Scrapes JD from a URL OR accepts pasted text.**

- Takes a URL (LinkedIn, Naukri, Indeed, Greenhouse, Lever, company careers page)
- Uses Tavily API to fetch and extract page content
- Returns clean JD text for the LLM to analyze
- Also accepts raw pasted JD text (pass-through mode)
- Pydantic model: `JobPosting` (company, role, location, required_skills, nice_to_have, responsibilities, experience_level, application_url)

### [NEW] `src/deep_agents/tools/github_analyzer.py`

**Fetches GitHub repos and creates resume-ready bullet points.**

- Takes a GitHub username OR individual repo URLs
- Uses public GitHub REST API (no auth needed)
- Extracts: repo names, descriptions, languages, stars, README highlights
- Formats as project bullet points ready to inject into resume
- Saves analysis to virtual filesystem

### [NEW] `src/deep_agents/tools/resume_exporter.py`

**Converts tailored markdown resume → downloadable PDF and DOCX.**

- **PDF:** Markdown → HTML (via `markdown` lib) → styled PDF (via `weasyprint`)
  - Uses a built-in ATS-optimized CSS template:
    - Single-column, top-to-bottom flow
    - Font: Calibri (primary), Arial (fallback) — 11pt body, 14pt headings
    - Margins: 1 inch (2.54cm) all sides
    - No graphics, no tables, no text boxes
    - Clean section dividers (thin lines)
    - Reverse-chronological order
    - Page size: A4
- **DOCX:** Builds a Word document via `python-docx`
  - Same clean formatting as PDF
  - Proper Word styles so the user can easily edit after download

### [MODIFY] `src/deep_agents/tools/search.py`

Keep existing `create_web_search_tool()`. Add:

**`create_job_search_tool()`** — Specialized job search wrapper:
- Takes: role, experience level, location, job type (remote/onsite/hybrid)
- Searches across job boards via Tavily
- Returns structured results
- Pairs with the Job Scout subagent to save results to Excel

### [MODIFY] `src/deep_agents/tools/__init__.py`

Export all new tool factories.

---

## Phase 3: Subagents (5 subagents)

### Existing (keep as-is)
- `create_light_research_subagent()` — still useful for general chat mode
- `create_structured_research_subagent()` — still useful for general chat mode

### [NEW] Career Subagents

#### 1. `create_jd_analyzer_subagent()`

| Property | Value |
|---|---|
| **Model** | Qwen 3.8 27B (thinking mode — deep analysis) |
| **Purpose** | Deep analysis of JD: extract required/nice-to-have skills, experience level, domain, key phrases to mirror, ATS keywords |
| **Output** | `JDAnalysis` Pydantic model |
| **Anti-hallucination** | "Only extract information explicitly stated in the JD. Do NOT infer or add requirements that are not mentioned." |

#### 2. `create_resume_tailor_subagent()`

| Property | Value |
|---|---|
| **Model** | Gemini 3.8 Flash (rewriting) + DeepSeek V4 Flash (technical sections) |
| **Purpose** | Takes master resume + JD analysis → ATS-optimized tailored resume |
| **Output** | `TailoredResume` Pydantic model (ats_score, matched_keywords, missing_keywords, tailored_content) |
| **Anti-hallucination** | "NEVER add skills, experiences, projects, or achievements that are not present in the user's original resume. You may ONLY rephrase, reorder, and optimize existing content. If a JD keyword doesn't match the user's background, flag it as 'missing' — do NOT fabricate experience to fill the gap." |

#### 3. `create_job_scout_subagent()`

| Property | Value |
|---|---|
| **Model** | Gemini 3.8 Flash (fast search + analysis) |
| **Purpose** | Searches for jobs matching user's criteria across LinkedIn, Naukri, Indeed, Greenhouse, Lever. Saves results to Excel. |
| **Output** | `JobSearchResults` Pydantic model (list of postings with apply links) |
| **Tools** | `job_search`, `web_search` |
| **Anti-hallucination** | "Only include real job postings with verifiable URLs. Do NOT generate fictional job listings." |

#### 4. `create_interview_coach_subagent()`

| Property | Value |
|---|---|
| **Model** | Gemini 3.8 Flash (research + generation) |
| **Purpose** | Generates interview prep: technical questions, behavioral questions, system design topics, company research, study plan |
| **Output** | `InterviewPrep` Pydantic model |
| **Tools** | `web_search` |
| **Anti-hallucination** | "Base company insights on real, verifiable information. Clearly distinguish between confirmed facts and reasonable assumptions." |

#### 5. `create_quality_judge_subagent()` — LLM-as-Judge

| Property | Value |
|---|---|
| **Model** | Qwen 3.8 27B (deep reasoning) |
| **Purpose** | Reviews output from every other subagent and validates quality |
| **Checks** | Hallucination detection (is anything fabricated?), ATS compliance (single-column? keywords present?), completeness (all sections filled?), accuracy (technical terms correct?) |
| **Output** | `QualityVerdict` Pydantic model (passed: bool, score: float, issues: list, suggestions: list) |
| **Anti-hallucination** | "Compare every claim in the tailored resume against the original master resume. Flag any skill, project, or experience that does not appear in the original." |

### Pipeline Flow

```
User Input
    │
    ├── Resume ──► Gemma 4 31B (parse) ──► structured resume
    ├── JD ──────► Qwen 3.8 27B (analyze) ──► JD analysis
    └── GitHub ──► GitHub API ──► project bullets
                         │
                         ▼
              Resume Tailor Subagent
           (Gemini 3.8 Flash + DeepSeek V4)
                         │
                         ▼
              Quality Judge Subagent ◄── "Is this accurate?"
              (Qwen 3.8 27B)            "Any hallucinations?"
                    │                    "ATS score?"
                    ▼
              ┌─── PASS ──► Show preview + download
              └─── FAIL ──► Fix issues, re-tailor, re-judge
```

---

## Phase 4: Skills (2 skills)

### [NEW] `projects/skills/ats-resume/SKILL.md`

ATS resume optimization rules:
- Single-column layout, no tables/graphics/text boxes
- Fonts: Calibri or Arial, 11pt body, 14pt headings
- Standard sections: Summary → Experience → Projects → Education → Skills → Certifications
- Reverse-chronological order within each section
- Google XYZ bullet format: "Accomplished [X] as measured by [Y], by doing [Z]"
- Mirror exact keywords from the JD
- Action verbs: Architected, Engineered, Optimized, Deployed, Reduced, Increased
- **NEVER fabricate content — only rephrase and optimize existing information**

### [NEW] `projects/skills/interview-prep/SKILL.md`

Interview preparation rules:
- STAR method: Situation → Task → Action → Result (quantified)
- System design framework: Requirements → Estimation → API → Data Model → Architecture → Trade-offs
- Company research checklist: tech blog, GitHub, Glassdoor, recent news, tech stack
- Study plan: Week 1-2 fundamentals, Week 3 company-specific, Week 4 mock interviews

---

## Phase 5: Career Copilot Prompt

### [MODIFY] `src/deep_agents/context/prompts.py`

Add `CAREER_COPILOT_PROMPT`:

```
You are an ATS Resume Tailoring Copilot. Your workflow:

1. Parse the user's uploaded resume using the resume parser tool
2. If user provided a JD URL → use job_extractor to scrape it
   If user pasted JD text → use it directly  
3. Analyze the JD using the JD Analyzer subagent (Qwen 3.8 27B)
4. If GitHub links provided → fetch project data using github_analyzer
5. Tailor the resume using the Resume Tailor subagent
6. Send the result to the Quality Judge for verification
7. If Judge passes → show preview with ATS score + download options
   If Judge fails → fix issues and re-tailor
8. If user asks → generate interview prep using Interview Coach

CRITICAL ANTI-HALLUCINATION RULES:
- NEVER add skills, projects, experiences, or achievements that are NOT in the user's original resume
- NEVER fabricate metrics, numbers, or company names
- You may REPHRASE and OPTIMIZE existing content, but NEVER INVENT new content
- If a JD requires a skill the user doesn't have, flag it as "missing" — do NOT pretend they have it
- The Quality Judge will catch any fabricated content — do not try to bypass it

Model routing:
- Gemma 4 31B → document parsing (PDF/DOCX extraction)
- Qwen 3.8 27B → deep JD analysis + quality judging
- Gemini 3.8 Flash → fast rewriting + interview prep
- DeepSeek V4 Flash → technical/coding section accuracy
```

---

## Phase 6: UI (Clean & Simple)

### [MODIFY] `app.py`

**Two tabs:** General Chat | Career Mode

#### Career Mode Tab — Clean Layout

```
┌─────────────────────────────────────────────┐
│  📄 Upload Resume                           │
│  [Choose file: PDF, DOCX, TXT, MD]          │
│  ✅ Resume loaded (2 pages, 847 words)      │
├─────────────────────────────────────────────┤
│  📋 Job Description                         │
│  ┌─ Paste JD text ──────────────────────┐   │
│  │                                      │   │
│  └──────────────────────────────────────┘   │
│  OR                                         │
│  🔗 JD URL: [https://linkedin.com/jobs/...]│
├─────────────────────────────────────────────┤
│  🐙 GitHub (optional): [username or URLs]   │
├─────────────────────────────────────────────┤
│  ┌───────────────────────────────┐          │
│  │    ✦  Tailor My Resume       │          │
│  └───────────────────────────────┘          │
└─────────────────────────────────────────────┘
```

#### Results — Preview Before Download

```
┌─────────────────────────────────────────────┐
│  ATS Match Score: 87%  ████████████░░░      │
│                                             │
│  ✅ Matched: Python, LangChain, AWS, Docker │
│  ⚠️ Missing: Kubernetes, Terraform          │
├─────────────────────────────────────────────┤
│  Preview:                                   │
│  ┌────────────────────────────────────────┐ │
│  │  VIPLOVE THAKRAN                      │ │
│  │  viplovethakran4@gmail.com            │ │
│  │                                       │ │
│  │  PROFESSIONAL SUMMARY                 │ │
│  │  AI Engineer with 2+ years...         │ │
│  │  ...                                  │ │
│  └────────────────────────────────────────┘ │
├─────────────────────────────────────────────┤
│  ⬇ Download PDF    ⬇ Download DOCX         │
│                                             │
│  🎯 Prepare for Interview                   │
└─────────────────────────────────────────────┘
```

#### Job Search Tab (inside Career Mode)

```
┌─────────────────────────────────────────────┐
│  🔍 Job Search                              │
│                                             │
│  Role: [AI Engineer            ]            │
│  Experience: [2-4 years        ]            │
│  Location: [Remote / Bangalore ]            │
│  Type: [Full-time              ]            │
│                                             │
│  ┌───────────────────────────┐              │
│  │   🔍  Search Jobs         │              │
│  └───────────────────────────┘              │
│                                             │
│  Results: 23 jobs found                     │
│  ┌──────────────────────────────────────┐   │
│  │ Company    │ Role      │ Apply Link  │   │
│  │ Google     │ ML Eng    │ 🔗          │   │
│  │ Flipkart  │ AI Eng    │ 🔗          │   │
│  │ ...        │           │             │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  ⬇ Download Excel (with all apply links)    │
└─────────────────────────────────────────────┘
```

#### What gets hidden/cleaned up

- No raw tool call JSON/code visible in Career Mode
- No `"⚡ Tool Operations"` or `"📁 Modified Files"` expanders
- Progress shown as clean status messages ("Parsing resume...", "Analyzing JD...", "Tailoring...", "Quality check...")
- General Chat tab keeps existing behavior unchanged

---

## Files Summary

| Action | File | What |
|---|---|---|
| **MODIFY** | `config.py` | 4 models, model roles, env vars |
| **MODIFY** | `pyproject.toml` | New deps, remove old |
| **MODIFY** | `requirements.txt` | Same |
| **NEW** | `packages.txt` | WeasyPrint system deps for Streamlit Cloud |
| **MODIFY** | `.env` | Google + OpenRouter keys |
| **NEW** | `tools/resume_parser.py` | PDF/DOCX/TXT/MD parser |
| **NEW** | `tools/job_extractor.py` | URL scraper + paste JD |
| **NEW** | `tools/github_analyzer.py` | GitHub repo analyzer |
| **NEW** | `tools/resume_exporter.py` | PDF + DOCX export |
| **MODIFY** | `tools/search.py` | Add job_search_tool |
| **MODIFY** | `tools/__init__.py` | Exports |
| **MODIFY** | `agents/subagents.py` | 5 new subagents + Pydantic models |
| **MODIFY** | `agents/__init__.py` | Exports |
| **NEW** | `skills/ats-resume/SKILL.md` | ATS rules |
| **NEW** | `skills/interview-prep/SKILL.md` | Interview rules |
| **MODIFY** | `context/prompts.py` | Career Copilot prompt |
| **MODIFY** | `app.py` | Career Mode tab, clean UI |

**Total: 6 new files + 1 new packages.txt, 9 modified files**

---

## Anti-Hallucination Strategy (Baked Into Every Layer)

| Layer | How |
|---|---|
| **System Prompt** | Explicit rule: "NEVER add content not in the original resume" |
| **JD Analyzer** | "Only extract what is explicitly stated in the JD" |
| **Resume Tailor** | "ONLY rephrase/reorder. Flag missing skills, don't fabricate" |
| **Quality Judge** | Compares tailored resume line-by-line against original. Catches any fabrication |
| **Job Scout** | "Only include real postings with verifiable URLs" |
| **Interview Coach** | "Distinguish confirmed facts from assumptions" |

---

## No Open Questions

All previous questions have been answered:
- ✅ Resume template: Single-column, Calibri/Arial, ATS-optimized
- ✅ UI approach: Option B (keep general chat + Career Mode tab)
- ✅ PDF export: WeasyPrint + `packages.txt` for Streamlit Cloud
- ✅ Pipeline: Single-click with preview before download
