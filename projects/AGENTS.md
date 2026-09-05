# Agents.md — Deep Agents Context File

---

## 1. What is a Deep Agent?

A **deep agent** is an agent designed for complex, multi-step, long-horizon
tasks. Unlike a simple tool-calling loop (LLM → tool → LLM → answer), a deep
agent is built on **LangGraph** and ships with four architectural pillars,
inspired by applications like Claude Code, Deep Research, and Manus:

1. **Planning** — an explicit todo-list tool the agent uses to break a task
   into steps and track progress.
2. **File System (Context Offloading)** — virtual file tools so the agent can
   store large intermediate results outside the chat context window.
3. **Subagents** — the ability to spawn specialized child agents with their
   own isolated context, tools, and prompts.
4. **Detailed System Prompt** — a long, carefully engineered prompt that
   teaches the agent *when* and *how* to use the capabilities above.

---

## 2. Operating Guidelines for the Agent

When you (the deep agent) are invoked and this file is in your context:

1. **Plan first.** For any task with more than ~2 steps, call `write_todos`
   before doing work, and keep statuses updated.
2. **Offload aggressively.** Write raw research output and long drafts to
   files; keep the conversation lean.
3. **Delegate wisely.** Use subagents for deep-dive research or independent
   subtasks; give them a crisp, self-contained instruction.
4. **One source of truth.** Treat this `Agents.md` as the authoritative
   description of your own architecture and conventions — prefer it over
   assumptions.
5. **Final answers** should synthesize from your files/notes, cite sources
   when research was involved, and be concise.
