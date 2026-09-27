# Deep Agents — Career Suite Build Tracker

## Phase 1: Config & Dependencies ✅
- [x] Update `config.py` — 4 models with correct IDs, MODEL_ROLES, env vars
- [x] Update `pyproject.toml` — new deps, remove old
- [x] Update `requirements.txt` — same
- [x] Create `packages.txt` — WeasyPrint system deps for Streamlit Cloud
- [x] Update `.env` — placeholder keys

## Phase 2: Tools ✅
- [x] `resume_parser.py` — PDF/DOCX/TXT/MD parser + ResumeProfile model
- [x] `job_extractor.py` — URL scraper + paste JD + JobPosting model
- [x] `github_analyzer.py` — GitHub profile/repo analyzer + GitHubProfile model
- [x] `resume_exporter.py` — PDF + DOCX export with ATS template
- [x] `search.py` — added job_search_tool (3-day freshness filter)
- [x] `tools/__init__.py` — all exports

## Phase 3: Subagents (one at a time)
- [ ] JD Analyzer subagent + `JDAnalysis` model
- [ ] Resume Tailor subagent + `TailoredResume` model
- [ ] Job Scout subagent + `JobSearchResults` model
- [ ] Interview Coach subagent + `InterviewPrep` model
- [ ] Quality Judge subagent + `QualityVerdict` model
- [ ] Update `get_default_subagents()` with `mode="career"`
- [ ] Update `agents/__init__.py` exports

## Phase 4: Skills
- [ ] `ats-resume/SKILL.md`
- [ ] `interview-prep/SKILL.md`

## Phase 5: Career Copilot Prompt
- [ ] Add `CAREER_COPILOT_PROMPT` to `prompts.py`

## Phase 6: UI
- [ ] Career Mode tab in `app.py`
- [ ] Resume upload + JD input + GitHub input
- [ ] Results preview + ATS score + download buttons
- [ ] Job Search tab
- [ ] Clean up — hide raw code/tool calls in Career Mode

## Phase 7: Documentation
- [ ] Update existing `README.md`
- [ ] Create `CAREER_MODE.md` — full career mode documentation
