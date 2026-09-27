"""
Deep Agents — Career Intelligence Platform.

A dual-mode Streamlit application:
  • **General Chat** — Multi-model conversational AI with subagents & tools.
  • **Career Mode** — ATS resume tailoring, job search, and interview prep.

Launch with:  streamlit run app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
import streamlit as st

# Ensure src/ is on sys.path for Streamlit Cloud deployment
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Bootstrap environment before any other deep_agents imports
from deep_agents.config import load_environment, get_available_models, get_model_id, get_model_for_role

load_environment()

from deep_agents.agents.factory import create_agent_instance
from deep_agents.agents.subagents import get_default_subagents, get_career_subagents
from deep_agents.backends.factory import BACKEND_OPTIONS
from deep_agents.context.memory import create_checkpointer, generate_thread_id, make_thread_config
from deep_agents.context.prompts import PROMPT_OPTIONS, get_system_prompt, load_agents_md, CAREER_COPILOT_PROMPT
from deep_agents.context.skills import load_skills_from_directory, get_default_skills_dir
from deep_agents.tools.search import create_web_search_tool, create_job_search_tool
from deep_agents.tools.resume_parser import parse_resume_file, SUPPORTED_EXTENSIONS
from deep_agents.tools.job_extractor import create_job_extractor_tool
from deep_agents.tools.github_analyzer import create_github_analyzer_tool
from deep_agents.tools.resume_exporter import export_resume


# ══════════════════════════════════════════════════════════════════════════════
#  Page Config
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Deep Agents — Career Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  CSS Styling
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<style>
    /* ── Reset & Typography ── */
    html, body, [class*="st-"], .stMarkdown, .stText, p, div, span, button, input, textarea {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ── Global Dark Canvas ── */
    .stApp {
        background-color: #08090e !important;
        background-image:
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 45%),
            radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.10) 0px, transparent 45%),
            radial-gradient(at 50% 100%, rgba(236, 72, 153, 0.05) 0px, transparent 45%) !important;
        background-attachment: fixed !important;
        color: #f1f5f9 !important;
    }

    #MainMenu, footer, header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* ── Glassmorphic Sidebar ── */
    section[data-testid="stSidebar"] {
        background: rgba(12, 14, 23, 0.88) !important;
        backdrop-filter: blur(28px) !important;
        -webkit-backdrop-filter: blur(28px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 4px 0 30px rgba(0, 0, 0, 0.4) !important;
    }
    section[data-testid="stSidebar"] div.block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    /* ── Brand ── */
    .brand-container {
        display: flex; align-items: center; gap: 12px;
        padding: 6px 0 16px 0; margin-bottom: 8px;
    }
    .brand-icon {
        width: 38px; height: 38px; border-radius: 12px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.25rem; font-weight: 800; color: white;
        box-shadow: 0 0 20px -3px rgba(99, 102, 241, 0.6);
    }
    .brand-text {
        font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;
    }
    .brand-tag {
        display: inline-block; font-size: 0.65rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.06em;
        padding: 2px 8px; border-radius: 9999px;
        background: rgba(99, 102, 241, 0.2); color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.4); margin-left: 6px;
    }

    .sidebar-section-title {
        font-size: 0.8rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.08em; color: #94a3b8;
        margin-top: 14px; margin-bottom: 8px;
        display: flex; align-items: center; gap: 6px;
    }

    /* ── Inputs & Selects ── */
    div[data-baseweb="select"] > div {
        background: rgba(20, 23, 38, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important; color: #f8fafc !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: rgba(99, 102, 241, 0.4) !important;
    }
    div[data-testid="stRadio"] label {
        color: #cbd5e1 !important; font-size: 0.9rem !important; font-weight: 500 !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important; font-weight: 600 !important;
        font-size: 0.9rem !important; padding: 0.55rem 1.25rem !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        box-shadow: 0 6px 22px rgba(99, 102, 241, 0.5) !important;
        transform: translateY(-2px) !important;
    }

    /* ── Chat Messages ── */
    div[data-testid="stChatMessage"] {
        background: rgba(18, 21, 35, 0.65) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 18px !important; padding: 20px 24px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 8px 28px -6px rgba(0, 0, 0, 0.35) !important;
    }
    div[data-testid="stChatMessageAvatar"] {
        background: linear-gradient(135deg, #312e81 0%, #4c1d95 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        background: rgba(26, 30, 52, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important; color: #cbd5e1 !important;
        font-size: 0.85rem !important; font-weight: 600 !important;
    }

    /* ── Chat Input ── */
    div[data-testid="stChatInput"] {
        border-radius: 26px !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        background: rgba(17, 20, 34, 0.9) !important;
        backdrop-filter: blur(24px) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5) !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: rgba(129, 140, 248, 0.65) !important;
    }
    div[data-testid="stChatInput"] textarea { color: #f8fafc !important; }
    div[data-testid="stChatInput"] textarea::placeholder { color: #64748b !important; }

    /* ── Score Bar ── */
    .score-bar-bg {
        background: rgba(255, 255, 255, 0.08); border-radius: 8px;
        height: 24px; width: 100%; position: relative; overflow: hidden;
    }
    .score-bar-fill {
        height: 100%; border-radius: 8px;
        background: linear-gradient(90deg, #ef4444 0%, #f59e0b 40%, #22c55e 80%);
        transition: width 0.5s ease;
    }
    .score-label {
        position: absolute; right: 10px; top: 2px;
        font-size: 0.8rem; font-weight: 700; color: #fff;
    }

    /* ── Keyword Tags ── */
    .kw-matched {
        display: inline-block; padding: 3px 10px; border-radius: 8px;
        font-size: 0.78rem; font-weight: 600; margin: 2px 4px 2px 0;
        background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3);
        color: #86efac;
    }
    .kw-missing {
        display: inline-block; padding: 3px 10px; border-radius: 8px;
        font-size: 0.78rem; font-weight: 600; margin: 2px 4px 2px 0;
        background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3);
        color: #fcd34d;
    }

    /* ── Hero ── */
    .hero-container { text-align: center; padding: 3rem 1rem 2rem 1rem; }
    .hero-badge {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 6px 14px; border-radius: 9999px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #a5b4fc; font-size: 0.82rem; font-weight: 700; margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 2.75rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.15;
        background: linear-gradient(135deg, #ffffff 10%, #c7d2fe 50%, #f472b6 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.75rem;
    }
    .hero-subtitle {
        color: #94a3b8; font-size: 1.05rem; max-width: 600px;
        margin: 0 auto 2.5rem auto; line-height: 1.5;
    }

    /* ── Scrollbars ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.12); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(99, 102, 241, 0.4); }

    /* ── Tab Styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background: rgba(18, 21, 35, 0.5);
        border-radius: 16px;
        padding: 4px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px; padding: 10px 24px;
        font-weight: 600; font-size: 0.9rem;
        color: #94a3b8 !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.2) !important;
        color: #c7d2fe !important;
        border: 1px solid rgba(99, 102, 241, 0.35) !important;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  Session State
# ══════════════════════════════════════════════════════════════════════════════

_SESSION_DEFAULTS = {
    "messages": [],
    "thread_id": None,
    "checkpointer": None,
    "agent_files": {},
    "agent_dirty": True,
    "pending_prompt": None,
    # Career Mode state
    "career_resume_text": "",
    "career_resume_filename": "",
    "career_jd_text": "",
    "career_result": None,
    "career_processing": False,
}

for key, default in _SESSION_DEFAULTS.items():
    if key not in st.session_state:
        if key == "thread_id":
            st.session_state[key] = generate_thread_id()
        elif key == "checkpointer":
            st.session_state[key] = create_checkpointer()
        else:
            st.session_state[key] = default


# ══════════════════════════════════════════════════════════════════════════════
#  Sidebar
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div class="brand-container">
        <div class="brand-icon">✦</div>
        <div>
            <div style="display: flex; align-items: center;">
                <span class="brand-text">Deep Agents</span>
                <span class="brand-tag">v3.0</span>
            </div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">Career Intelligence Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Model Engine
    st.markdown('<div class="sidebar-section-title">⚡ Model Engine</div>', unsafe_allow_html=True)
    model_names = list(get_available_models().keys())
    selected_model = st.selectbox(
        "Model Engine", model_names, index=0,
        key="model_select", label_visibility="collapsed",
    )

    # Context Mode
    st.markdown('<div class="sidebar-section-title">🧠 Context & Prompting</div>', unsafe_allow_html=True)
    context_mode = st.radio(
        "Context Mode",
        list(PROMPT_OPTIONS.keys()) + ["AGENTS.md File", "Skills (from disk)"],
        index=0, key="context_select", label_visibility="collapsed",
    )

    # Backend
    st.markdown('<div class="sidebar-section-title">💾 Persistent Backend</div>', unsafe_allow_html=True)
    backend_display = st.radio(
        "Backend", list(BACKEND_OPTIONS.keys()),
        index=0, key="backend_select", label_visibility="collapsed",
    )

    # Subagents & Tools
    st.markdown('<div class="sidebar-section-title">🔗 Subagents & Tools</div>', unsafe_allow_html=True)
    enable_subagents = st.toggle("Enable Autonomous Subagents", value=True, key="subagent_toggle")
    subagent_tier = "Both (Light & Deep Structured)"
    if enable_subagents:
        subagent_tier = st.selectbox(
            "Subagent Tier",
            ["Both (Light & Deep Structured)", "Deep Structured Only", "Light Research Only", "Career Agents"],
            index=0, key="subagent_tier_select",
        )
    enable_web_search = st.toggle("Enable Web Search", value=True, key="search_toggle")

    # Session
    st.markdown('<div class="sidebar-section-title">🧵 Session</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
         border-radius: 10px; padding: 8px 12px; font-family: 'JetBrains Mono', monospace;
         font-size: 0.78rem; color: #94a3b8; margin-bottom: 12px;">
        ID: <span style="color: #a5b4fc;">{st.session_state.thread_id[:12]}…</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✦  New Conversation", use_container_width=True):
        for key in ["messages", "agent_files", "career_resume_text", "career_resume_filename",
                     "career_jd_text", "career_result"]:
            st.session_state[key] = "" if isinstance(_SESSION_DEFAULTS.get(key), str) else _SESSION_DEFAULTS.get(key)
        st.session_state.thread_id = generate_thread_id()
        st.session_state.checkpointer = create_checkpointer()
        st.session_state.pending_prompt = None
        st.session_state.career_processing = False
        st.rerun()

    # API key status
    missing_keys = [k for k in ("GOOGLE_API_KEY", "OPENROUTER_API_KEY") if not os.getenv(k)]
    if missing_keys:
        st.sidebar.warning(
            f"⚠️ **Missing Keys:** {', '.join(missing_keys)}\n\n"
            "Add them under **Settings → Secrets** on Streamlit Cloud."
        )
    if not os.getenv("GROQ_API_KEY"):
        st.sidebar.info(
            "💡 **Groq key not set** — fallback disabled.\n\n"
            "Add `GROQ_API_KEY` for automatic failover when OpenRouter is down."
        )


# ══════════════════════════════════════════════════════════════════════════════
#  Agent Builder
# ══════════════════════════════════════════════════════════════════════════════

def _build_agent(career_mode: bool = False):
    """Construct the agent from current sidebar selections."""
    model_id = get_model_id(selected_model)
    backend_key = BACKEND_OPTIONS[backend_display]

    # Tools
    tools = []
    if enable_web_search:
        tools.append(create_web_search_tool())
    if career_mode:
        tools.append(create_job_extractor_tool())
        tools.append(create_github_analyzer_tool())
        tools.append(create_job_search_tool())

    # System prompt / context
    system_prompt = ""
    files_seed: dict = {}

    if career_mode:
        system_prompt = CAREER_COPILOT_PROMPT
        # Load career skills
        skills_dir = get_default_skills_dir()
        skills_files = load_skills_from_directory(skills_dir)
        if skills_files:
            files_seed.update(skills_files)
    elif context_mode in PROMPT_OPTIONS:
        system_prompt = get_system_prompt(context_mode)
    elif context_mode == "AGENTS.md File":
        agents_md = load_agents_md()
        if agents_md:
            system_prompt = "Follow the operating guidelines in /projects/AGENTS.md"
            files_seed["/projects/AGENTS.md"] = {"content": agents_md}
        else:
            system_prompt = "You are a helpful assistant."
    elif context_mode == "Skills (from disk)":
        skills_dir = get_default_skills_dir()
        skills_files = load_skills_from_directory(skills_dir)
        if skills_files:
            files_seed.update(skills_files)
            system_prompt = "You have access to skill files under /skills/. Read the relevant SKILL.md before answering."
        else:
            system_prompt = "You are a helpful assistant."

    # Subagents
    subagents = None
    if enable_subagents:
        if career_mode:
            subagents = get_career_subagents(tools=tools if tools else None)
        else:
            tier_map = {
                "Both (Light & Deep Structured)": "both",
                "Deep Structured Only": "deep",
                "Light Research Only": "light",
                "Career Agents": "career",
            }
            subagents = get_default_subagents(
                tools=tools if tools else None,
                mode=tier_map.get(subagent_tier, "both"),
            )

    agent, store = create_agent_instance(
        model_id=model_id, tools=tools, system_prompt=system_prompt,
        backend_type=backend_key, checkpointer=st.session_state.checkpointer,
        subagents=subagents,
    )
    return agent, store, files_seed


# ══════════════════════════════════════════════════════════════════════════════
#  Main Tabs
# ══════════════════════════════════════════════════════════════════════════════

tab_chat, tab_career, tab_jobs = st.tabs(["💬 General Chat", "📄 Resume Tailor", "🔍 Job Search"])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1: General Chat (existing functionality)
# ══════════════════════════════════════════════════════════════════════════════

with tab_chat:
    # Telemetry bar
    subagent_label = subagent_tier.split(" ")[0] if enable_subagents else "Off"
    st.markdown(f"""
    <div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 8px 16px;
         background: rgba(18, 21, 35, 0.5); border: 1px solid rgba(255,255,255,0.06);
         border-radius: 16px; margin-bottom: 20px;">
        <div class="telemetry-chip highlight"><span style="width:7px;height:7px;border-radius:50%;background:#10b981;display:inline-block;"></span> Ready</div>
        <div class="telemetry-chip">⚡ {selected_model}</div>
        <div class="telemetry-chip">🔗 Subagents: {subagent_label}</div>
        <div class="telemetry-chip">🌐 Search: {'On' if enable_web_search else 'Off'}</div>
    </div>
    """, unsafe_allow_html=True)

    # Welcome hero
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="hero-container">
            <div class="hero-badge">✦ Autonomous Multi-Turn Intelligence</div>
            <div class="hero-title">Where should we begin?</div>
            <div class="hero-subtitle">
                Equipped with persistent memory, virtual filesystems, web search,
                and specialised subagents for research and career intelligence.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔬  Deep Research\n\nInvestigate a topic with structured findings", use_container_width=True, key="s1"):
                st.session_state.pending_prompt = "Perform deep research on recent breakthroughs in AI agents and return structured findings."
                st.rerun()
            if st.button("⚡  Quick Fact Check\n\nGet a fast, concise answer", use_container_width=True, key="s2"):
                st.session_state.pending_prompt = "Explain concisely how LangGraph checkpointers maintain state and thread persistence."
                st.rerun()
        with col2:
            if st.button("💻  Architecture Plan\n\nDesign a system with concrete code", use_container_width=True, key="s3"):
                st.session_state.pending_prompt = "Design a production-grade async microservice architecture with FastAPI, Celery, and Redis."
                st.rerun()
            if st.button("📄  Career Mode →\n\nTailor your resume, find jobs", use_container_width=True, key="s4"):
                st.rerun()

    # Chat history
    for msg in st.session_state.messages:
        avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg.get("tool_calls"):
                with st.expander(f"⚡ Tools ({len(msg['tool_calls'])} executed)", expanded=False):
                    for tc in msg["tool_calls"]:
                        st.code(f"{tc['name']}({tc.get('args', {})})", language="python")
            if msg.get("files"):
                with st.expander(f"📁 Files ({len(msg['files'])} changed)", expanded=False):
                    for fp, fc in msg["files"].items():
                        st.markdown(f"**`{fp}`**")
                        preview = fc.get("content", "") if isinstance(fc, dict) else str(fc)
                        if isinstance(preview, str):
                            st.code(preview[:500] + ("…" if len(preview) > 500 else ""), language="text")

    # Chat input
    user_input = st.chat_input("Ask anything, plan tasks, or trigger research…")
    if st.session_state.pending_prompt and not user_input:
        user_input = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Synthesizing response…"):
                try:
                    agent, store, files_seed = _build_agent(career_mode=False)
                    invoke_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    invoke_payload: dict = {"messages": invoke_messages}
                    combined_files = {**st.session_state.agent_files, **files_seed}
                    if combined_files:
                        invoke_payload["files"] = combined_files
                    config = make_thread_config(st.session_state.thread_id)
                    result = agent.invoke(invoke_payload, config=config)

                    last_msg = result["messages"][-1]
                    raw_content = last_msg.content
                    if isinstance(raw_content, list):
                        text_parts = [b["text"] if isinstance(b, dict) and b.get("type") == "text" else str(b) for b in raw_content if isinstance(b, (dict, str))]
                        response_text = "\n\n".join(text_parts) if text_parts else str(raw_content)
                    else:
                        response_text = str(raw_content)

                    tool_calls_display = []
                    for m in result["messages"]:
                        if hasattr(m, "tool_calls") and m.tool_calls:
                            for tc in m.tool_calls:
                                tool_calls_display.append({"name": tc.get("name", "?"), "args": tc.get("args", {})})

                    result_files = result.get("files", {})
                    if result_files:
                        st.session_state.agent_files.update(result_files)

                    st.markdown(response_text)
                    if tool_calls_display:
                        with st.expander(f"⚡ Tools ({len(tool_calls_display)} executed)", expanded=False):
                            for tc in tool_calls_display:
                                st.code(f"{tc['name']}({tc['args']})", language="python")

                    assistant_msg = {"role": "assistant", "content": response_text}
                    if tool_calls_display:
                        assistant_msg["tool_calls"] = tool_calls_display
                    if result_files:
                        assistant_msg["files"] = result_files
                    st.session_state.messages.append(assistant_msg)

                except Exception as e:
                    error_text = f"❌ **Error:** {e}"
                    st.error(error_text)
                    st.session_state.messages.append({"role": "assistant", "content": error_text})


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2: Resume Tailor (Career Mode)
# ══════════════════════════════════════════════════════════════════════════════

with tab_career:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0 1rem 0;">
        <div class="hero-badge">✦ ATS Resume Tailoring Engine</div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.3rem;">
            Tailor your resume to any job
        </div>
        <div style="color: #94a3b8; font-size: 0.9rem;">
            Upload resume + paste JD → get an ATS-optimised resume with match score
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Input Section ---
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("##### 📄 Your Resume")
        uploaded_file = st.file_uploader(
            "Upload resume", type=["pdf", "docx", "txt", "md"],
            key="resume_upload", label_visibility="collapsed",
        )
        if uploaded_file:
            file_bytes = uploaded_file.read()
            parsed = parse_resume_file(file_bytes, uploaded_file.name)
            st.session_state.career_resume_text = parsed
            st.session_state.career_resume_filename = uploaded_file.name
            word_count = len(parsed.split())
            st.success(f"✅ **{uploaded_file.name}** loaded — {word_count} words extracted")

        resume_paste = st.text_area(
            "Or paste your resume here",
            height=150, key="resume_paste_area",
            placeholder="Paste your resume text here if you don't have a file…",
        )
        if resume_paste.strip() and not uploaded_file:
            st.session_state.career_resume_text = resume_paste
            st.session_state.career_resume_filename = "pasted_resume.txt"

    with col_right:
        st.markdown("##### 📋 Job Description")
        jd_input = st.text_area(
            "Paste the JD or a URL (LinkedIn, Naukri, Indeed, etc.)",
            height=150, key="jd_input_area",
            placeholder="Paste the full job description here…\n\nOr paste a URL like:\nhttps://linkedin.com/jobs/view/...\nhttps://naukri.com/job-listings-...",
        )

        st.markdown("##### 🐙 GitHub (optional)")
        github_input = st.text_input(
            "GitHub username or repo URLs",
            key="github_input",
            placeholder="e.g. Viplove0114 or https://github.com/user/repo",
        )

    # --- Action Button ---
    st.markdown("")

    has_resume = bool(st.session_state.career_resume_text)
    has_jd = bool(jd_input.strip())

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        tailor_clicked = st.button(
            "✦  Tailor My Resume",
            use_container_width=True, key="tailor_btn",
            disabled=not (has_resume and has_jd),
        )

    if not has_resume and not has_jd:
        st.info("📤 Upload your resume and paste a job description to get started.")
    elif not has_resume:
        st.warning("📄 Please upload or paste your resume.")
    elif not has_jd:
        st.warning("📋 Please paste the job description or JD URL.")

    # --- Processing ---
    if tailor_clicked and has_resume and has_jd:
        with st.status("🔄 Tailoring your resume…", expanded=True) as status:
            try:
                st.write("🔍 Parsing resume…")
                agent, store, files_seed = _build_agent(career_mode=True)

                # Build the career prompt
                career_prompt = f"""RESUME TAILORING REQUEST:

=== USER'S RESUME ===
{st.session_state.career_resume_text}

=== JOB DESCRIPTION ===
{jd_input}
"""
                if github_input.strip():
                    career_prompt += f"\n=== GITHUB ===\n{github_input.strip()}\n"

                career_prompt += """
=== INSTRUCTIONS ===
Execute the full resume tailoring pipeline:
1. Analyse the JD using the jd-analyzer subagent
2. Tailor the resume using the resume-tailor subagent
3. Run quality check using the quality-judge subagent
4. Present: tailored resume content, ATS score, matched/missing keywords, and changes made

REMEMBER: NEVER add content not in the original resume. Flag missing skills, don't fabricate them.
"""

                st.write("📋 Analysing job description…")
                invoke_payload = {
                    "messages": [{"role": "user", "content": career_prompt}],
                }
                combined_files = {**st.session_state.agent_files, **files_seed}
                if combined_files:
                    invoke_payload["files"] = combined_files

                config = make_thread_config(st.session_state.thread_id)

                st.write("✍️ Tailoring resume…")
                result = agent.invoke(invoke_payload, config=config)

                st.write("🔎 Quality check…")

                # Extract response
                last_msg = result["messages"][-1]
                raw_content = last_msg.content
                if isinstance(raw_content, list):
                    text_parts = [b["text"] if isinstance(b, dict) and b.get("type") == "text" else str(b) for b in raw_content if isinstance(b, (dict, str))]
                    response_text = "\n\n".join(text_parts) if text_parts else str(raw_content)
                else:
                    response_text = str(raw_content)

                st.session_state.career_result = response_text

                result_files = result.get("files", {})
                if result_files:
                    st.session_state.agent_files.update(result_files)

                status.update(label="✅ Resume tailored successfully!", state="complete")

            except Exception as e:
                status.update(label=f"❌ Error: {e}", state="error")
                st.error(f"Something went wrong: {e}")

    # --- Results Display ---
    if st.session_state.career_result:
        st.markdown("---")
        st.markdown("### 📊 Results")

        # Display the tailored result
        st.markdown(st.session_state.career_result)

        # Download buttons
        st.markdown("---")
        st.markdown("##### ⬇️ Download Tailored Resume")

        dl_col1, dl_col2, dl_col3 = st.columns([1, 1, 1])

        try:
            exports = export_resume(st.session_state.career_result)

            with dl_col1:
                st.download_button(
                    label="📥 Download PDF",
                    data=exports["pdf"],
                    file_name="tailored_resume.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            with dl_col2:
                st.download_button(
                    label="📥 Download DOCX",
                    data=exports["docx"],
                    file_name="tailored_resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
        except Exception as e:
            st.warning(f"⚠️ Export error: {e}. The preview above can still be copied manually.")

        with dl_col3:
            st.download_button(
                label="📥 Download Markdown",
                data=st.session_state.career_result,
                file_name="tailored_resume.md",
                mime="text/markdown",
                use_container_width=True,
            )

        # Interview prep button
        st.markdown("")
        col_ip1, col_ip2, col_ip3 = st.columns([1, 2, 1])
        with col_ip2:
            if st.button("🎯  Prepare for Interview", use_container_width=True, key="interview_btn"):
                with st.spinner("Generating interview preparation…"):
                    try:
                        agent, store, files_seed = _build_agent(career_mode=True)
                        interview_prompt = (
                            f"Based on the job description I just tailored my resume for, "
                            f"generate comprehensive interview preparation.\n\n"
                            f"JOB DESCRIPTION:\n{jd_input}\n\n"
                            f"Generate: technical questions, behavioral questions (STAR method), "
                            f"system design topics, a study plan, and salary negotiation tips."
                        )
                        payload = {"messages": [{"role": "user", "content": interview_prompt}]}
                        config = make_thread_config(st.session_state.thread_id)
                        result = agent.invoke(payload, config=config)
                        last_msg = result["messages"][-1]
                        raw = last_msg.content
                        if isinstance(raw, list):
                            parts = [b["text"] if isinstance(b, dict) and b.get("type") == "text" else str(b) for b in raw if isinstance(b, (dict, str))]
                            interview_text = "\n\n".join(parts)
                        else:
                            interview_text = str(raw)
                        st.markdown("---")
                        st.markdown("### 🎯 Interview Preparation")
                        st.markdown(interview_text)
                    except Exception as e:
                        st.error(f"Interview prep error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3: Job Search
# ══════════════════════════════════════════════════════════════════════════════

with tab_jobs:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0 1rem 0;">
        <div class="hero-badge">🔍 Job Search Intelligence</div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.3rem;">
            Find your next role
        </div>
        <div style="color: #94a3b8; font-size: 0.9rem;">
            Search across LinkedIn, Naukri, Indeed & more — latest postings only
        </div>
    </div>
    """, unsafe_allow_html=True)

    jcol1, jcol2 = st.columns(2)
    with jcol1:
        job_role = st.text_input("🎯 Role", placeholder="e.g. AI Engineer, Backend Developer", key="job_role")
        job_location = st.text_input("📍 Location", placeholder="e.g. Remote, Bangalore, San Francisco", key="job_location")
    with jcol2:
        job_experience = st.selectbox("📊 Experience", ["Any", "Fresher", "Junior (1-3 yrs)", "Mid (3-6 yrs)", "Senior (6+ yrs)"], key="job_exp")
        job_type = st.selectbox("💼 Type", ["Full-time", "Part-time", "Contract", "Internship", "Any"], key="job_type")

    jbtn1, jbtn2, jbtn3 = st.columns([1, 2, 1])
    with jbtn2:
        search_clicked = st.button(
            "🔍  Search Jobs", use_container_width=True,
            key="search_jobs_btn", disabled=not job_role.strip(),
        )

    if not job_role.strip():
        st.info("Enter a role to start searching.")

    if search_clicked and job_role.strip():
        with st.status("🔍 Searching across job boards…", expanded=True) as status:
            try:
                st.write("Searching LinkedIn, Naukri, Indeed…")
                agent, store, files_seed = _build_agent(career_mode=True)

                exp_text = "" if job_experience == "Any" else job_experience
                type_text = "" if job_type == "Any" else job_type

                search_prompt = (
                    f"Search for the latest job openings (not older than 3 days) with these criteria:\n\n"
                    f"- Role: {job_role}\n"
                    f"- Location: {job_location or 'Any'}\n"
                    f"- Experience: {exp_text or 'Any'}\n"
                    f"- Type: {type_text or 'Full-time'}\n\n"
                    f"Search across LinkedIn, Naukri, Indeed, Greenhouse, and Lever.\n"
                    f"Present results as a clean table with: Company, Role, Location, Source, Apply Link.\n"
                    f"Only include REAL postings with verifiable URLs."
                )

                payload = {"messages": [{"role": "user", "content": search_prompt}]}
                combined = {**st.session_state.agent_files, **files_seed}
                if combined:
                    payload["files"] = combined
                config = make_thread_config(st.session_state.thread_id)

                st.write("Evaluating job fit…")
                result = agent.invoke(payload, config=config)

                last_msg = result["messages"][-1]
                raw = last_msg.content
                if isinstance(raw, list):
                    parts = [b["text"] if isinstance(b, dict) and b.get("type") == "text" else str(b) for b in raw if isinstance(b, (dict, str))]
                    job_results_text = "\n\n".join(parts)
                else:
                    job_results_text = str(raw)

                status.update(label="✅ Search complete!", state="complete")

                st.markdown("---")
                st.markdown("### 📋 Job Search Results")
                st.markdown(job_results_text)

                # Excel download
                st.markdown("")
                excol1, excol2, excol3 = st.columns([1, 2, 1])
                with excol2:
                    st.download_button(
                        label="📥 Download Results (Markdown)",
                        data=job_results_text,
                        file_name="job_search_results.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )

            except Exception as e:
                status.update(label=f"❌ Error: {e}", state="error")
                st.error(f"Job search error: {e}")
