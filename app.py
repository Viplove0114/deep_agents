"""
Deep Agents — Modern Conversational AI Platform.

A sleek, state-of-the-art chat interface featuring:
  • Model Engine Selection (Qwen 3.8-27B, Compound Mini, GPT-5.4/5.5)
  • Context Engineering Modes (System Prompts, AGENTS.md, Disk Skills)
  • Resilient Backends (State Memory, Virtual Filesystem, Store)
  • Two-Tier Autonomous Subagents (Light & Deep Structured Research)
  • Glassmorphic Dark Aesthetics with Micro-interactions & Status Telemetry

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
from deep_agents.config import load_environment, get_available_models, get_model_id

load_environment()

from deep_agents.agents.factory import create_agent_instance
from deep_agents.agents.subagents import get_default_subagents
from deep_agents.backends.factory import BACKEND_OPTIONS
from deep_agents.context.memory import create_checkpointer, generate_thread_id, make_thread_config
from deep_agents.context.prompts import PROMPT_OPTIONS, get_system_prompt, load_agents_md
from deep_agents.context.skills import load_skills_from_directory, get_default_skills_dir
from deep_agents.tools.search import create_web_search_tool


# Page configuration
st.set_page_config(
    page_title="Deep Agents — Conversational AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Modern UI / CSS styling injection
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

    /* Hide default Streamlit clutter */
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

    /* ── Sidebar Brand ── */
    .brand-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 6px 0 16px 0;
        margin-bottom: 8px;
    }
    .brand-icon {
        width: 38px;
        height: 38px;
        border-radius: 12px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        font-weight: 800;
        color: white;
        box-shadow: 0 0 20px -3px rgba(99, 102, 241, 0.6);
    }
    .brand-text {
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .brand-tag {
        display: inline-block;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 2px 8px;
        border-radius: 9999px;
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.4);
        margin-left: 6px;
    }

    /* ── Sidebar Section Cards ── */
    .sidebar-section-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        margin-top: 14px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* ── Inputs & Selects ── */
    div[data-baseweb="select"] > div {
        background: rgba(20, 23, 38, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        transition: all 0.2s ease !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: rgba(99, 102, 241, 0.4) !important;
        box-shadow: 0 0 12px -2px rgba(99, 102, 241, 0.2) !important;
    }

    /* ── Radio & Toggles ── */
    div[data-testid="stRadio"] label {
        color: #cbd5e1 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    
    /* ── Modern Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.55rem 1.25rem !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        box-shadow: 0 6px 22px rgba(99, 102, 241, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* ── Chat Messages ── */
    div[data-testid="stChatMessage"] {
        background: rgba(18, 21, 35, 0.65) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 18px !important;
        padding: 20px 24px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 8px 28px -6px rgba(0, 0, 0, 0.35) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    div[data-testid="stChatMessage"]:hover {
        border-color: rgba(99, 102, 241, 0.25) !important;
        box-shadow: 0 10px 32px -4px rgba(0, 0, 0, 0.45) !important;
    }

    /* Avatar styling */
    div[data-testid="stChatMessageAvatar"] {
        background: linear-gradient(135deg, #312e81 0%, #4c1d95 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3) !important;
    }

    /* ── Modern Expanders for Tools ── */
    .streamlit-expanderHeader {
        background: rgba(26, 30, 52, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #cbd5e1 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        padding: 10px 16px !important;
        margin-top: 10px !important;
        transition: all 0.2s ease !important;
    }
    .streamlit-expanderHeader:hover {
        background: rgba(38, 43, 74, 0.7) !important;
        border-color: rgba(99, 102, 241, 0.35) !important;
    }
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        background: rgba(14, 16, 28, 0.65) !important;
        padding: 14px !important;
    }

    /* ── Floating Chat Input Dock ── */
    div[data-testid="stChatInput"] {
        border-radius: 26px !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        background: rgba(17, 20, 34, 0.9) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(99, 102, 241, 0.12) !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: rgba(129, 140, 248, 0.65) !important;
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.6), 0 0 24px -2px rgba(99, 102, 241, 0.4) !important;
    }
    div[data-testid="stChatInput"] textarea {
        color: #f8fafc !important;
        font-size: 0.98rem !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
    }

    /* ── Telemetry Pill Bar ── */
    .telemetry-bar {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: rgba(18, 21, 35, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }
    .telemetry-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.07);
        color: #cbd5e1;
    }
    .telemetry-chip.highlight {
        background: rgba(99, 102, 241, 0.15);
        border-color: rgba(99, 102, 241, 0.35);
        color: #c7d2fe;
    }
    .live-pulse {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 8px #10b981;
        display: inline-block;
        animation: pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    @keyframes pulse-ring {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.9); }
    }

    /* ── Starter Cards Grid ── */
    .hero-container {
        text-align: center;
        padding: 3rem 1rem 2rem 1rem;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 9999px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #a5b4fc;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 2.75rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.15;
        background: linear-gradient(135deg, #ffffff 10%, #c7d2fe 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.75rem;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        max-width: 600px;
        margin: 0 auto 2.5rem auto;
        line-height: 1.5;
    }

    /* ── Scrollbars ── */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.12);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99, 102, 241, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# Session-state initialisation
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = generate_thread_id()
if "checkpointer" not in st.session_state:
    st.session_state.checkpointer = create_checkpointer()
if "agent_files" not in st.session_state:
    st.session_state.agent_files = {}
if "agent_dirty" not in st.session_state:
    st.session_state.agent_dirty = True
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# Sidebar Controls
with st.sidebar:
    # Modern Brand Header
    st.markdown("""
    <div class="brand-container">
        <div class="brand-icon">✦</div>
        <div>
            <div style="display: flex; align-items: center;">
                <span class="brand-text">Deep Agents</span>
                <span class="brand-tag">v2.5</span>
            </div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">Autonomous Multi-Agent AI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. Model Engine Section
    st.markdown('<div class="sidebar-section-title">⚡ Model Engine</div>', unsafe_allow_html=True)
    model_names = list(get_available_models().keys())
    selected_model = st.selectbox(
        "Model Engine",
        model_names,
        index=0,
        key="model_select",
        label_visibility="collapsed",
    )

    # 2. Context Engineering Section
    st.markdown('<div class="sidebar-section-title">🧠 Context & Prompting</div>', unsafe_allow_html=True)
    context_mode = st.radio(
        "Context Mode",
        list(PROMPT_OPTIONS.keys()) + ["AGENTS.md File", "Skills (from disk)"],
        index=0,
        key="context_select",
        label_visibility="collapsed",
    )

    # 3. Memory & Backend Section
    st.markdown('<div class="sidebar-section-title">💾 Persistent Backend</div>', unsafe_allow_html=True)
    backend_display = st.radio(
        "Backend Architecture",
        list(BACKEND_OPTIONS.keys()),
        index=0,
        key="backend_select",
        label_visibility="collapsed",
    )

    # 4. Subagents & Tools Section
    st.markdown('<div class="sidebar-section-title">🔗 Subagents & Tools</div>', unsafe_allow_html=True)
    enable_subagents = st.toggle("Enable Autonomous Subagents", value=True, key="subagent_toggle")
    subagent_tier = "Both (Light & Deep Structured)"
    if enable_subagents:
        subagent_tier = st.selectbox(
            "Subagent Delegation Tier",
            [
                "Both (Light & Deep Structured)",
                "Deep Structured Only",
                "Light Research Only",
            ],
            index=0,
            key="subagent_tier_select",
        )
    enable_web_search = st.toggle("Enable Tavily Web Search", value=True, key="search_toggle")

    # Thread & Session Controls
    st.markdown('<div class="sidebar-section-title">🧵 Session Telemetry</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        padding: 8px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #94a3b8;
        margin-bottom: 12px;
    ">
        ID: <span style="color: #a5b4fc;">{st.session_state.thread_id[:12]}…</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✦  Start New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = generate_thread_id()
        st.session_state.checkpointer = create_checkpointer()
        st.session_state.agent_files = {}
        st.session_state.agent_dirty = True
        st.session_state.pending_prompt = None
        st.rerun()

    # Cloud Secrets status reminder
    if not (os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")):
        st.sidebar.warning(
            "⚠️ **API Keys Not Detected**\n\n"
            "If running on Streamlit Cloud, add your keys under **Settings → Secrets**."
        )


# Agent builder (cached until settings change)
def _build_agent():
    """Construct the agent from current sidebar selections."""
    model_id = get_model_id(selected_model)
    backend_key = BACKEND_OPTIONS[backend_display]

    # Tools
    tools = []
    if enable_web_search:
        tools.append(create_web_search_tool())

    # System prompt / context
    system_prompt = ""
    files_seed: dict = {}

    if context_mode in PROMPT_OPTIONS:
        system_prompt = get_system_prompt(context_mode)
    elif context_mode == "AGENTS.md File":
        agents_md = load_agents_md()
        if agents_md:
            system_prompt = "Follow the operating guidelines in /projects/AGENTS.md"
            files_seed["/projects/AGENTS.md"] = {"content": agents_md}
        else:
            system_prompt = "You are a helpful assistant."
            st.sidebar.warning("⚠️ `projects/AGENTS.md` not found. Using default prompt.")
    elif context_mode == "Skills (from disk)":
        skills_dir = get_default_skills_dir()
        skills_files = load_skills_from_directory(skills_dir)
        if skills_files:
            files_seed.update(skills_files)
            system_prompt = (
                "You have access to skill files under /skills/. "
                "Read the relevant SKILL.md before answering domain questions."
            )
        else:
            system_prompt = "You are a helpful assistant."
            st.sidebar.warning(f"⚠️ No skills found in `{skills_dir}`. Using default prompt.")

    # Subagents
    subagents = None
    if enable_subagents:
        tier_mode_map = {
            "Both (Light & Deep Structured)": "both",
            "Deep Structured Only": "deep",
            "Light Research Only": "light",
        }
        selected_mode = tier_mode_map.get(subagent_tier, "both")
        subagents = get_default_subagents(
            tools=tools if tools else None,
            mode=selected_mode,
        )

    # Build compiled deep agent
    agent, store = create_agent_instance(
        model_id=model_id,
        tools=tools,
        system_prompt=system_prompt,
        backend_type=backend_key,
        checkpointer=st.session_state.checkpointer,
        subagents=subagents,
    )

    return agent, store, files_seed


# Main Workspace Area

# Top telemetry live status bar
subagent_label = subagent_tier.split(" ")[0] if enable_subagents else "Off"
st.markdown(f"""
<div class="telemetry-bar">
    <div class="telemetry-chip highlight">
        <span class="live-pulse"></span>
        <span>Ready</span>
    </div>
    <div class="telemetry-chip">
        <span>⚡</span> <span>{selected_model}</span>
    </div>
    <div class="telemetry-chip">
        <span>💾</span> <span>Backend: {backend_display.split(" ")[0]}</span>
    </div>
    <div class="telemetry-chip">
        <span>🔗</span> <span>Subagents: {subagent_label}</span>
    </div>
    <div class="telemetry-chip">
        <span>🌐</span> <span>Search: {'Enabled' if enable_web_search else 'Off'}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# Render Welcome Hero & Starter Cards if no messages yet
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">✦ Autonomous Multi-Turn Intelligence</div>
        <div class="hero-title">Where should we begin?</div>
        <div class="hero-subtitle">
            Equipped with persistent thread memory, virtual filesystems, real-time search,
            and specialized subagents for light lookups and deep research.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Starter cards grid (2 columns x 2 rows)
    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🔬  Deep Topic Research\n\nInvestigate recent advancements in quantum computing architectures and synthesize findings.",
            use_container_width=True,
            key="starter_research",
        ):
            st.session_state.pending_prompt = "Perform deep research on recent breakthroughs in quantum computing architectures and return structured findings."
            st.rerun()

        if st.button(
            "⚡  Quick Fact Verification\n\nExplain how LangGraph checkpoints preserve state across multi-turn agent conversations.",
            use_container_width=True,
            key="starter_langgraph",
        ):
            st.session_state.pending_prompt = "Explain concisely how LangGraph checkpointers (like MemorySaver) maintain state and thread persistence."
            st.rerun()

    with col2:
        if st.button(
            "💻  System Architecture Plan\n\nDesign an event-driven microservice system with FastAPI, Celery, and Redis streams.",
            use_container_width=True,
            key="starter_arch",
        ):
            st.session_state.pending_prompt = "Design a production-grade async microservice architecture with FastAPI, Celery, and Redis. Provide concrete code and components."
            st.rerun()

        if st.button(
            "📁  Filesystem & Tool Execution\n\nCreate a project specification file in /notes/spec.md with goals and milestones.",
            use_container_width=True,
            key="starter_files",
        ):
            st.session_state.pending_prompt = "Use your write_file tool to create `/notes/spec.md` with an executive summary and milestone roadmap for this project."
            st.rerun()


# Render chat conversation history
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    tool_info = msg.get("tool_calls")
    files_info = msg.get("files")

    avatar_icon = "🧑‍💻" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar_icon):
        st.markdown(content)

        if tool_info:
            with st.expander(f"⚡ Tool Operations ({len(tool_info)} executed)", expanded=False):
                for tc in tool_info:
                    st.code(f"{tc['name']}({tc.get('args', {})})", language="python")

        if files_info:
            with st.expander(f"📁 Modified Files ({len(files_info)} changed)", expanded=False):
                for fp, fc in files_info.items():
                    st.markdown(f"**`{fp}`**")
                    preview = fc.get("content", "") if isinstance(fc, dict) else str(fc)
                    if isinstance(preview, str):
                        st.code(preview[:500] + ("…" if len(preview) > 500 else ""), language="text")


# Chat input handling (from text input or starter card click)
user_input = st.chat_input("Ask anything, plan tasks, or trigger subagent research…")

if st.session_state.pending_prompt and not user_input:
    user_input = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if user_input:
    # 1. Append & render user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)

    # 2. Build agent and execute
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Synthesizing response & orchestrating tools…"):
            try:
                agent, store, files_seed = _build_agent()

                # Prepare invocation messages
                invoke_messages = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
                invoke_payload: dict = {"messages": invoke_messages}

                # Seed files (skills, AGENTS.md, or carry forward state files)
                combined_files = {**st.session_state.agent_files, **files_seed}
                if combined_files:
                    invoke_payload["files"] = combined_files

                # Thread config for checkpointer
                config = make_thread_config(st.session_state.thread_id)

                # Invoke the compiled agent graph
                result = agent.invoke(invoke_payload, config=config)

                # Extract response
                last_msg = result["messages"][-1]
                raw_content = last_msg.content

                if isinstance(raw_content, list):
                    text_parts = []
                    for block in raw_content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(block["text"])
                        elif isinstance(block, str):
                            text_parts.append(block)
                    response_text = "\n\n".join(text_parts) if text_parts else str(raw_content)
                else:
                    response_text = str(raw_content)

                # Extract tool call telemetry
                tool_calls_display = []
                for msg in result["messages"]:
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            tool_calls_display.append({
                                "name": tc.get("name", "unknown"),
                                "args": tc.get("args", {}),
                            })

                # Capture state backend files
                result_files = result.get("files", {})
                if result_files:
                    st.session_state.agent_files.update(result_files)

                # Render assistant output
                st.markdown(response_text)

                if tool_calls_display:
                    with st.expander(f"⚡ Tool Operations ({len(tool_calls_display)} executed)", expanded=False):
                        for tc in tool_calls_display:
                            st.code(f"{tc['name']}({tc['args']})", language="python")

                if result_files:
                    with st.expander(f"📁 Modified Files ({len(result_files)} changed)", expanded=False):
                        for fp, fc in result_files.items():
                            st.markdown(f"**`{fp}`**")
                            preview = fc.get("content", "") if isinstance(fc, dict) else str(fc)
                            if isinstance(preview, str):
                                st.code(preview[:500] + ("…" if len(preview) > 500 else ""), language="text")

                # Persist to session
                assistant_msg: dict = {
                    "role": "assistant",
                    "content": response_text,
                }
                if tool_calls_display:
                    assistant_msg["tool_calls"] = tool_calls_display
                if result_files:
                    assistant_msg["files"] = result_files

                st.session_state.messages.append(assistant_msg)

            except Exception as e:
                error_text = f"❌ **Execution Error:** {e}"
                st.error(error_text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_text,
                })
