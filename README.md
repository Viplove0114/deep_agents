# ✦ Deep Agents — Career Intelligence & Multi-Agent AI Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![DeepAgents](https://img.shields.io/badge/Engine-DeepAgents%20%7C%20LangGraph-6366f1.svg)](https://github.com/langchain-ai/deepagents)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Models](https://img.shields.io/badge/Models-Qwen%20%7C%20Gemini%20%7C%20Gemma-10b981.svg)](https://openrouter.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A production-grade, multi-agent AI platform with **dual operating modes**: a general-purpose conversational AI and a **Career Intelligence Suite** that tailors resumes to beat ATS systems, searches for jobs across 6+ platforms, and generates interview preparation — all orchestrated by specialised LLM agents with zero-hallucination protocols.

---

### 🚀 Live Demo

👉 **[https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/](https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/)**

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [System Capabilities](#-system-capabilities)
  - [General Chat Mode](#1-general-chat-mode)
  - [Career Mode — Resume Tailor](#2-career-mode--resume-tailor)
  - [Career Mode — Job Search](#3-career-mode--job-search)
  - [Career Mode — Interview Coach](#4-career-mode--interview-coach)
  - [Multi-Model Routing](#5-multi-model-routing)
- [Project Layout](#-project-layout)
- [Local Setup](#-local-installation--setup)
- [Cloud Deployment](#-streamlit-cloud-deployment)
- [Career Mode Deep Dive](#-career-mode-deep-dive)
- [Notebook Experiments](#-notebook-experiments-reference)
- [License & Author](#-license--author)

---

## 🌟 Overview

**Deep Agents** is a dual-mode AI platform built on [LangGraph](https://github.com/langchain-ai/langgraph):

| Mode | Purpose |
|---|---|
| **💬 General Chat** | Multi-model conversational AI with research subagents, web search, virtual filesystems, and persistent memory |
| **📄 Resume Tailor** | Upload resume + paste JD → ATS-optimised tailored resume with match score, PDF/DOCX export |
| **🔍 Job Search** | Search LinkedIn, Naukri, Indeed, Greenhouse, Lever for jobs posted in the last 3 days |

### What makes it different?

- **5 specialised career subagents** — each with a dedicated LLM and structured Pydantic output
- **Smart model routing** — the right LLM for each task (parsing, analysis, rewriting, coding, judging)
- **Zero-hallucination protocol** — 7 non-negotiable rules enforced by a Quality Judge subagent
- **ATS-optimised templates** — single-column, Calibri 11pt, Google XYZ bullet format
- **Professional modular codebase** — enterprise-grade package structure under `src/deep_agents/`

---

## 🏛️ Architecture

```
                         ┌─────────────────────────────────────────┐
                         │    Streamlit UI — 3 Tabs                │
                         │   💬 Chat  │  📄 Resume  │  🔍 Jobs    │
                         └──────────────────┬──────────────────────┘
                                            │
                         ┌──────────────────┴──────────────────────┐
                         │         Agent Factory + Router          │
                         │     (General Mode / Career Mode)        │
                         └──────────────────┬──────────────────────┘
                                            │
          ┌─────────────────────────────────┼─────────────────────────────────┐
          │                                 │                                 │
          ▼                                 ▼                                 ▼
┌───────────────────┐           ┌───────────────────┐            ┌───────────────────┐
│   3 LLM Engines   │           │  Context Layer     │            │  Storage Layer    │
│                   │           │                   │            │                   │
│ • Qwen 3.8 27B    │           │ • Career Copilot  │            │ • StateBackend    │
│   (orchestrate)   │           │   System Prompt   │            │ • FilesystemBack. │
│ • Gemini 3.8 Flash│           │ • ATS Resume Skill│            │ • StoreBackend    │
│   (fast rewrite)  │           │ • Interview Skill │            │ • LangGraph Saver │
│ • Gemma 4 31B     │           │ • AGENTS.md       │            │                   │
│   (doc parsing)   │           │ • Thread Memory   │            │                   │
└───────────────────┘           └───────────────────┘            └───────────────────┘
                                            │
              ┌─────────────────────────────┼────────────────────────────┐
              │            Career Subagent Pipeline                      │
              └─────────────────────────────┼────────────────────────────┘
                                            │
     ┌──────────┬──────────┬────────────┬───┴────────┐
     ▼          ▼          ▼            ▼            ▼
┌─────────┐┌─────────┐┌──────────┐┌──────────┐┌───────────┐
│   JD    ││ Resume  ││  Job     ││Interview ││ Quality   │
│Analyzer ││ Tailor  ││  Scout   ││  Coach   ││  Judge    │
│         ││         ││          ││          ││           │
│Qwen 3.8 ││Gemini   ││Gemini    ││Gemini    ││Qwen 3.8  │
│  27B    ││3.8 Flash││3.8 Flash ││3.8 Flash ││  27B     │
│         ││         ││          ││          ││           │
│JDAnalysis│TailoredR.│JobSearch  │Interview  │QualityVer.│
│(14 flds)││(8 flds) ││Results   ││  Prep    ││  dict    │
└─────────┘└─────────┘└──────────┘└──────────┘└───────────┘
```

---

## ⚡ System Capabilities

### 1. General Chat Mode

The original conversational AI with:
- **Two-tier research subagents** — Light Researcher (fast lookups) + Deep Researcher (structured `ResearchFindings`)
- **Tavily web search** — real-time internet access
- **Persistent memory** — LangGraph MemorySaver checkpointers
- **Virtual filesystem** — read/write files during conversations
- **Skills system** — load domain-specific instructions from disk
- **Multiple context modes** — system prompts, AGENTS.md, Skills

### 2. Career Mode — Resume Tailor

The flagship feature. A 7-step pipeline:

| Step | What Happens | Agent Used |
|---|---|---|
| 1. Parse Resume | Extract text from PDF/DOCX/TXT/MD | `resume_parser` tool |
| 2. Extract JD | Scrape URL (LinkedIn/Naukri/Indeed) or process pasted text | `job_extractor` tool |
| 3. Analyse JD | Deep extraction of skills, keywords, tech stack, flags | JD Analyzer (Qwen 3.8 27B) |
| 4. GitHub Data | Fetch repos, languages, stars → resume bullet points | `github_analyzer` tool |
| 5. Tailor Resume | Rewrite bullets (Google XYZ), maximise ATS keywords | Resume Tailor (Gemini 3.8 Flash) |
| 6. Quality Check | Hallucination detection, ATS compliance, completeness | Quality Judge (Qwen 3.8 27B) |
| 7. Export | Preview + download as PDF, DOCX, or Markdown | `resume_exporter` tool |

### 3. Career Mode — Job Search

- Search across **LinkedIn, Naukri, Indeed, Greenhouse, Lever, Wellfound**
- **3-day freshness filter** — only recent postings
- **Fit scoring** — Hard Skills (40%) + Experience (30%) + Domain (20%) + Stack (10%)
- Results with direct **apply links**
- Download results for offline review

### 4. Career Mode — Interview Coach

- Company research (tech stack, engineering blog, Glassdoor)
- 8–10 technical questions tailored to the role
- 5 behavioral questions with **STAR method** answer angles
- 3 system design topics based on company products
- **4-week study plan** (fundamentals → company-specific → mock interviews)
- Salary negotiation tips

### 5. Multi-Model Routing

Each task is routed to the optimal LLM:

| Model | Provider | Role |
|---|---|---|
| **Qwen 3.8 27B** | OpenRouter (free) | Orchestration, deep JD analysis, quality judging, technical accuracy |
| **Gemini 3.8 Flash** | Google AI Studio | Fast rewriting, interview prep, job search |
| **Gemma 4 31B** | Google AI Studio | PDF/DOCX parsing, multimodal understanding |

---

## 📁 Project Layout

```text
deep_agents/
├── app.py                              # Streamlit app — 3 tabs (Chat, Resume, Jobs)
├── requirements.txt                    # Production dependencies
├── pyproject.toml                      # Package config (v2.0)
├── packages.txt                        # System deps for Streamlit Cloud (WeasyPrint)
├── .env                                # API keys (gitignored)
├── README.md                           # This file
├── CAREER_MODE.md                      # Career Mode technical documentation
│
├── src/deep_agents/
│   ├── __init__.py
│   ├── config.py                       # 4 models, MODEL_ROLES, env loader
│   │
│   ├── agents/
│   │   ├── __init__.py                 # All agent exports
│   │   ├── factory.py                  # create_agent_instance() graph builder
│   │   └── subagents.py               # 2 research + 5 career subagents
│   │
│   ├── backends/
│   │   ├── __init__.py
│   │   └── factory.py                  # State, Filesystem, Store backends
│   │
│   ├── context/
│   │   ├── __init__.py
│   │   ├── memory.py                   # LangGraph checkpointer + thread utils
│   │   ├── prompts.py                  # System prompts + CAREER_COPILOT_PROMPT
│   │   └── skills.py                   # SKILL.md loader
│   │
│   └── tools/
│       ├── __init__.py                 # All tool exports
│       ├── search.py                   # web_search + job_search tools
│       ├── resume_parser.py            # PDF/DOCX/TXT/MD → ResumeProfile
│       ├── job_extractor.py            # URL/text → JobPosting
│       ├── github_analyzer.py          # GitHub API → resume bullet points
│       └── resume_exporter.py          # Markdown → PDF (WeasyPrint) + DOCX
│
├── projects/
│   ├── AGENTS.md                       # Agent operating manual
│   └── skills/
│       ├── python/SKILL.md             # Python development skill
│       ├── report-writer/SKILL.md      # Report writing skill
│       ├── ats-resume/SKILL.md         # ATS resume optimisation rules
│       └── interview-prep/SKILL.md     # Interview preparation framework
│
└── deep_agent_experiments/             # Original Jupyter notebooks
    ├── 1-basicsdeepagent.ipynb
    ├── 2-contextengineering.ipynb
    ├── 3-backends.ipynb
    └── 4-subagents.ipynb
```

---

## 💻 Local Installation & Setup

### Prerequisites
- **Python 3.11+**
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`

### Install

```bash
git clone https://github.com/Viplove0114/deep_agents.git
cd deep_agents

# Using uv (recommended)
uv venv && .venv\Scripts\activate
uv pip install -r requirements.txt

# Or using pip
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
```

### Configure API Keys

Create `.env` in the project root:

```env
# Required — at least one model provider
GOOGLE_API_KEY=your_google_ai_studio_key
OPENROUTER_API_KEY=your_openrouter_key

# Required — for web search and job search
TAVILY_API_KEY=your_tavily_key
```

| Key | Where to Get It | Cost |
|---|---|---|
| `GOOGLE_API_KEY` | [aistudio.google.dev](https://aistudio.google.dev/) | Free tier |
| `OPENROUTER_API_KEY` | [openrouter.ai/keys](https://openrouter.ai/keys) | Free models available |
| `TAVILY_API_KEY` | [tavily.com](https://tavily.com/) | 1000 free searches/month |

### Launch

```bash
streamlit run app.py
```

Open **`http://localhost:8501`** → you'll see three tabs: Chat, Resume Tailor, Job Search.

---

## ☁️ Streamlit Cloud Deployment

1. Push to GitHub (`.env` is gitignored).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New App**.
3. Set `app.py` as the main file.
4. Under **Advanced Settings → Secrets**, add:
   ```toml
   GOOGLE_API_KEY = "your_key"
   OPENROUTER_API_KEY = "your_key"
   TAVILY_API_KEY = "tvly-..."
   ```
5. The `packages.txt` file auto-installs WeasyPrint system dependencies.

🔗 **Live:** [https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/](https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/)

---

## 📄 Career Mode Deep Dive

For comprehensive technical documentation of the Career Intelligence Suite, including:
- Design rationale for each component
- Model routing decisions
- Anti-hallucination protocol details
- ATS template design choices
- Pydantic schema documentation

See **[CAREER_MODE.md](CAREER_MODE.md)**.

---

## 🔬 Notebook Experiments Reference

| Notebook | Topic | Refactored To |
|---|---|---|
| `1-basicsdeepagent.ipynb` | Agent basics, tool invocation | `tools/search.py`, `config.py` |
| `2-contextengineering.ipynb` | Memory, AGENTS.md, skills | `context/prompts.py`, `memory.py`, `skills.py` |
| `3-backends.ipynb` | State, Filesystem, Store backends | `backends/factory.py` |
| `4-subagents.ipynb` | Subagent declaration, structured output | `agents/subagents.py`, `factory.py` |

---

## 👤 License & Author

- **Author**: Viplove Thakran ([@Viplove0114](https://github.com/Viplove0114))
- **Email**: viplovethakran4@gmail.com
- **Live App**: [https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/](https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/)
- **License**: MIT License
