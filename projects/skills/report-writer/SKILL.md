---
name: report-writer
description: Report writing skill. After answering any user query, generate a structured markdown report and save it as a file using the write_file tool.
license: MIT
metadata:
  version: "1.0"
  author: deepagentscourse
---

# Report Writer Skill

This is a **post-answer** skill: after you finish answering ANY substantive
user query, generate a structured report of what was asked, what you did,
and what you concluded — and save it to a file with the `write_file` tool.

## When to Use
- ALWAYS after producing a final answer to a substantive question
- When the user explicitly asks for a report, summary document, or saved output
- After research tasks, code generation tasks, or multi-step workflows
- Skip only for trivial exchanges (greetings, clarifying questions)

## Quick Standards
- Reports are markdown files saved under `/reports/`
- File name: kebab-case topic slug + `-report.md`
- Always include: Question, Approach, Key Findings, Answer, Sources/Tools Used
- Keep the report self-contained — readable without the chat transcript
