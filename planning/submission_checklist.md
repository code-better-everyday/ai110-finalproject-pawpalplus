# Submission Checklist — PawPal+ Final Project

**Due:** Monday, August 3rd, 2026 at 1:59 AM CDT

---

## Required Files

- [ ] `README.md` — complete per spec (see sections below)
- [ ] `model_card.md` — responsible-AI reflection
- [ ] `diagrams/architecture.mmd` — Mermaid source file (not just PNG)
- [ ] `diagrams/uml_final.mmd` — updated class diagram
- [ ] `assets/` folder exists (even if just a placeholder)
- [ ] `ai_advisor.py` — Claude integration working
- [ ] `logs/advisor_log.txt` — populated after running the app
- [ ] `requirements.txt` — includes `anthropic>=0.25` and `python-dotenv`
- [ ] `.env.example` — shows `ANTHROPIC_API_KEY=your-key-here` (real key NEVER committed)
- [ ] `.gitignore` — includes `.env` and `logs/`

---

## README.md Must Include

- [ ] Reference to original Module 2 project (`ai110-module2show-pawpal-starter`)
- [ ] 2-3 sentence summary of what Module 2 built
- [ ] Title + summary of final project
- [ ] Architecture overview (link to `diagrams/architecture.mmd`)
- [ ] Setup instructions (venv, pip install, ANTHROPIC_API_KEY, streamlit run)
- [ ] 2-3 sample AI advisor interactions as **fenced code blocks** (not screenshots)
- [ ] Design decisions + trade-offs
- [ ] Testing summary (X/Y tests passing, what was tested)
- [ ] Brief reflection on what this taught about AI

---

## model_card.md Must Include

- [ ] How AI (Claude Code) was used to build this project
- [ ] One **helpful** AI suggestion with example
- [ ] One **flawed** AI suggestion and how it was caught/fixed
- [ ] System limitations (single-owner session, exact-time conflict detection, no auth, etc.)

---

## Code Quality

- [ ] App runs: `streamlit run app.py` — no crashes
- [ ] CLI runs: `python main.py` — no crashes
- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] Target: 20+ tests (14 existing + 6+ new)
- [ ] `ai_advisor.py` handles missing API key gracefully (error message, not crash)
- [ ] Logging writes to `logs/advisor_log.txt`

---

## GitHub

- [ ] Repo is **public**
- [ ] Multiple meaningful commits (not just one big dump)
- [ ] Final push before deadline
- [ ] Commit history is clean and shows progression

---

## New Features Built

- [ ] `Scheduler.detect_group_walks()` implemented and tested
- [ ] `Scheduler.detect_overlap_conflicts()` implemented and tested
- [ ] `ai_advisor.py` — `build_context()`, `ask_advisor()`, `log_interaction()`
- [ ] Step 5 in `app.py` — AI advisor chat UI
- [ ] 3-state task rendering (normal / orange conflict / blue group walk)
