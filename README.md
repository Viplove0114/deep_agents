# ✦ Deep Agents — Autonomous Multi-Agent Conversational AI

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![DeepAgents](https://img.shields.io/badge/Engine-DeepAgents%20%7C%20LangGraph-6366f1.svg)](https://github.com/langchain-ai/deepagents)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Model-Groq%20%7C%20OpenAI-f55036.svg)](https://groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A production-grade, modular framework and modern conversational AI platform featuring multi-model orchestration, persistent graph checkpointers, pluggable storage backends, skills-based context engineering, and autonomous two-tier subagent delegation with Pydantic-structured outputs.

---

### 🚀 Live Interactive Demo
Try the deployed application directly on Streamlit Cloud:
👉 **[https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/](https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/)**

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Architecture & Design Highlights](#-architecture--design-highlights)
- [System Capabilities](#-system-capabilities)
  - [1. Model Engine Selection](#1-model-engine-selection)
  - [2. Context Engineering & Memory](#2-context-engineering--memory)
  - [3. Pluggable Backends](#3-pluggable-backends)
  - [4. Two-Tier Autonomous Subagents](#4-two-tier-autonomous-subagents)
  - [5. Modern Conversational Web UI](#5-modern-conversational-web-ui)
- [Project Layout](#-project-layout)
- [Local Installation & Setup](#-local-installation--setup)
- [Streamlit Cloud Deployment](#-streamlit-cloud-deployment)
- [Notebook Experiments Reference](#-notebook-experiments-reference)
- [License & Authors](#-license--authors)

---

## 🌟 Overview

**Deep Agents** consolidates core agentic AI patterns—originally developed across experimental Jupyter notebooks—into a professional, modular Python package under `src/deep_agents/`. It couples these agent primitives with a sleek, state-of-the-art **Streamlit conversational AI web interface** inspired by modern AI products like ChatGPT, Claude, and Gemini.

The system is designed from the ground up for **resilient multi-turn workflows**:
- Delegates simple vs. complex queries dynamically between **Light** and **Deep Structured Research** subagents.
- Executes real-time web searches using the **Tavily API**.
- Preserves multi-turn state and threads using **LangGraph MemorySaver** checkpointers.
- Mounts virtual filesystems, loads custom **`AGENTS.md`** operating manuals, and injects on-demand **Skills** from disk.

---

## 🏛️ Architecture & Design Highlights

```
                       ┌─────────────────────────────────────┐
                       │     Streamlit Modern Web App        │
                       │             (app.py)                │
                       └──────────────────┬──────────────────┘
                                          │ User Query & Sidebar Controls
                                          ▼
                       ┌─────────────────────────────────────┐
                       │     Unified Agent Factory           │
                       │    (create_agent_instance)          │
                       └──────────┬──────────────────────────┘
                                  │
         ┌────────────────────────┼─────────────────────────┐
         │                        │                         │
         ▼                        ▼                         ▼
┌──────────────────┐    ┌──────────────────┐     ┌──────────────────┐
│  Model Engine    │    │ Context & Memory │     │ Pluggable Storage│
│ • Qwen 3.8-27B   │    │ • System Prompts │     │ • StateBackend   │
│ • Compound Mini  │    │ • AGENTS.md File │     │ • Filesystem     │
│ • GPT-5.4 / 5.5  │    │ • Skills on Disk │     │ • StoreBackend   │
│                  │    │ • LangGraph Saver│     │                  │
└──────────────────┘    └──────────────────┘     └──────────────────┘
                                  │
                                  ▼
                       ┌─────────────────────────────────────┐
                       │    Autonomous Subagent Delegation   │
                       └──────────┬──────────────────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
      ┌─────────────────────┐           ┌─────────────────────┐
      │  Light Researcher   │           │   Deep Researcher   │
      │ • Fast factual look-│           │ • Exhaustive search │
      │   ups & brief ans.  │           │ • Multi-angle verif.│
      │ • Concise synthesis │           │ • Pydantic Output:  │
      │                     │           │   ResearchFindings  │
      └─────────────────────┘           └─────────────────────┘
```

---

## ⚡ System Capabilities

### 1. Model Engine Selection
- **Qwen 3.8-27B (Groq)** — Default lightning-fast open-weights reasoning model.
- **Groq Compound Mini** — High-efficiency model optimized for low-latency agent loops.
- **GPT-5.4 & GPT-5.5 (OpenAI)** — Advanced frontier models for complex multi-hop reasoning.
- Transparent syntax normalization between `provider:model` and `provider/model` delimiters.

### 2. Context Engineering & Memory
- **Curated System Prompts**: Toggle between General Assistant, Code Specialist, and Research Analyst profiles.
- **`AGENTS.md` Memory**: Loads `/projects/AGENTS.md` as persistent system context guiding architectural conventions and runtime protocols.
- **Modular Skills System**: Scans `/projects/skills/` for `SKILL.md` specifications (e.g., Python specialist, Report writer) and mounts them into the agent's virtual memory on demand.
- **Thread Checkpointing**: Utilizes LangGraph `MemorySaver` to preserve conversation history across turns with unique thread IDs.

### 3. Pluggable Backends
- **State Backend (`state`)**: Default in-memory ephemeral virtual filesystem carried within agent delta channels.
- **Filesystem Backend (`filesystem`)**: Maps virtual workspace files directly to sandboxed local directories.
- **Store Backend (`store`)**: Employs LangGraph's persistent KV-store protocol for cross-thread memory.

### 4. Two-Tier Autonomous Subagents
The parent agent automatically delegates tasks using the `task` tool based on query depth:
- **`light-researcher`**: Used for fast, brief lookups, fact verification, and quick summaries without heavy multi-step loops.
- **`deep-researcher`**: Dedicated in-depth researcher that synthesizes multi-source findings into a validated **Pydantic schema**:
  ```python
  class ResearchFindings(BaseModel):
      summary: str       # Comprehensive synthesis of findings
      key_points: list   # Key takeaways and discovered evidence
      sources: list      # URLs and documents consulted
      confidence: float  # Score from 0.0 to 1.0 reflecting evidence strength
  ```

### 5. Modern Conversational Web UI
- **Obsidian Dark Theme**: Cosmic dark gradient (`#08090e`) with ambient violet/rose glows and glassmorphic panels (`backdrop-filter: blur(28px)`).
- **Typography**: Refined fonts powered by **Plus Jakarta Sans** and **JetBrains Mono**.
- **Real-Time Telemetry Bar**: Pinned status indicator showing live model engine, active backend, subagent tier, and search status.
- **Interactive Starter Cards**: Clickable suggestion cards to instantly launch deep research, code planning, fact checks, or file creation tasks.
- **Tool Inspection Drawers**: Expandable cards revealing underlying tool execution arguments and file modification previews.

---

## 📁 Project Layout

```text
deep_agents/
├── app.py                          # Streamlit modern conversational AI application
├── requirements.txt                # Production dependency manifest
├── pyproject.toml                  # Python package configuration (uv-compatible)
├── README.md                       # Complete documentation & deployment guide
├── .gitignore                      # Git ignore rules (protects .env & secrets)
│
├── src/
│   └── deep_agents/
│       ├── __init__.py             # Public API exports
│       ├── config.py               # Environment loader (.env + st.secrets) & model map
│       ├── agents/
│       │   ├── __init__.py         # Agents package init
│       │   ├── factory.py          # Unified create_agent_instance graph builder
│       │   └── subagents.py        # Two-tier light & deep structured subagents
│       ├── backends/
│       │   ├── __init__.py         # Backends package init
│       │   └── factory.py          # State, Filesystem, and Store backend factory
│       ├── context/
│       │   ├── __init__.py         # Context package init
│       │   ├── memory.py           # LangGraph checkpointers & thread utilities
│       │   ├── prompts.py          # System prompt templates & AGENTS.md reader
│       │   └── skills.py           # SKILL.md file loader & virtual tree generator
│       └── tools/
│           ├── __init__.py         # Tools package init
│           └── search.py           # Tavily web search tool factory
│
├── projects/                       # Context engineering assets
│   ├── AGENTS.md                   # Sample agent architecture & operating manual
│   └── skills/                     # Skill directories mounted into agent filesystem
│       ├── python/SKILL.md         # Python development skill
│       └── report-writer/SKILL.md  # Structured markdown report skill
│
└── deep_agent_experiments/         # Source Jupyter exploratory notebooks
    ├── 1-basicsdeepagent.ipynb     # Agent basics & tool invocation
    ├── 2-contextengineering.ipynb  # Memory, AGENTS.md & skill files
    ├── 3-backends.ipynb            # State, Filesystem & Store backends
    └── 4-subagents.ipynb           # Declarative subagents & structured outputs
```

---

## 💻 Local Installation & Setup

### 1. Prerequisites
- **Python 3.11+** installed.
- [uv](https://github.com/astral-sh/uv) (recommended) or standard `pip` / `venv`.

### 2. Clone the Repository
```bash
git clone https://github.com/Viplove0114/deep_agents.git
cd deep_agents
```

### 3. Create & Activate Virtual Environment
Using `uv`:
```bash
uv venv
.venv\Scripts\activate      # On Windows
# source .venv/bin/activate # On macOS / Linux
uv pip install -r requirements.txt
```

Or using standard `venv`:
```bash
python -m venv .venv
.venv\Scripts\activate      # On Windows
# source .venv/bin/activate # On macOS / Linux
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
# Primary fast model provider
GROQ_API_KEY=your_groq_api_key_here

# Optional frontier model provider
OPENAI_API_KEY=your_openai_api_key_here

# Web search tool provider
TAVILY_API_KEY=your_tavily_api_key_here
```

### 5. Launch the Web Application
```bash
streamlit run app.py
```
Open your browser to **`http://localhost:8501`**.

---

## ☁️ Streamlit Cloud Deployment

The application is natively configured to run on **Streamlit Community Cloud** without committing secret keys or `.env` files:

1. **Fork or Push** your repository to GitHub (ensure `.env` is omitted; our `.gitignore` protects it automatically).
2. Visit **[share.streamlit.io](https://share.streamlit.io)** and connect your GitHub account.
3. Click **"New App"**:
   - **Repository**: `YourUsername/deep_agents`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Expand **Advanced Settings → Secrets** and insert your API keys in TOML format:
   ```toml
   GROQ_API_KEY = "gsk_..."
   OPENAI_API_KEY = "sk-..."
   TAVILY_API_KEY = "tvly-..."
   ```
5. Click **Deploy**. The app will launch with live telemetry, subagent delegation, and search enabled.

🔗 **Live Deployment:** [https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/](https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/)

---

## 🔬 Notebook Experiments Reference

The `deep_agent_experiments/` directory preserves the initial research and prototypes:

| Notebook | Topic | Refactored Destination |
| :--- | :--- | :--- |
| `1-basicsdeepagent.ipynb` | Deep agent initialization, basic system prompts, internet search | `src/deep_agents/tools/search.py`, `src/deep_agents/config.py` |
| `2-contextengineering.ipynb` | Multi-turn memory, LangGraph checkpointers, `AGENTS.md`, and skills | `src/deep_agents/context/prompts.py`, `memory.py`, `skills.py` |
| `3-backends.ipynb` | Comparing `StateBackend`, `FilesystemBackend`, and `StoreBackend` | `src/deep_agents/backends/factory.py` |
| `4-subagents.ipynb` | Subagent declaration, model routing, and Pydantic structured output | `src/deep_agents/agents/subagents.py`, `factory.py` |

---

## 👤 Author & License

- **Author**: Viplove Thakran ([@Viplove0114](https://github.com/Viplove0114))
- **Email**: viplovethakran4@gmail.com
- **Live App**: [https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/](https://viplove0114-deep-agents-app-bdkxjk.streamlit.app/)
- **License**: MIT License
