# PawPal+ Final Project — Implementation Overview

**Deadline:** Monday, August 3rd, 2026 at 1:59 AM CDT  
**Base project:** Module 2 — `ai110-module2show-pawpal-starter`  
**Final project dir:** `ai110-finalproject-pawpalplus`

---

## What We're Building

Extending PawPal+ from a pure scheduling tool into an applied AI system. Three additions on top of the solid Module 2 foundation:

### 1. RAG-Powered AI Care Advisor (core AI requirement)
A Claude-powered chat built into the Streamlit app. The owner types a natural-language question and Claude answers using the *actual* schedule data as context — not generic pet advice.

- `ai_advisor.py` — builds context from Owner/Pet/Task state, calls Claude API, logs every interaction
- Integrated into `app.py` as Step 5
- Questions like: *"What's most urgent today?"*, *"Is Pintu overdue for meds?"*, *"Help me resolve the 08:00 conflict"*

### 2. Group Walk Feature (designed in Module 2 reflection, never coded)
If 2+ pets of the **same species** both have a "walk" task at the same time slot, that's cooperative scheduling — not a conflict. The UI should show blue 🐾 instead of orange ⚠.

- New `Scheduler.detect_group_walks()` in `pawpal_system.py`
- 3-state rendering in UI: normal | conflict (orange ⚠) | group walk (blue 🐾)

### 3. Duration-Overlap Conflict Detection (noted limitation in Module 2)
Current system only catches exact HH:MM clashes. A 30-min walk at 07:30 and a 60-min vet at 07:45 is a real conflict — it goes undetected today.

- New `Scheduler.detect_overlap_conflicts()` in `pawpal_system.py`
- Works alongside existing `detect_conflicts()` (exact match)

---

## Folder Structure

```
ai110-finalproject-pawpalplus/
├── planning/                   ← our design docs (not graded)
│   ├── overview.md             ← this file
│   ├── rag_design.md           ← RAG advisor design notes
│   └── submission_checklist.md ← grading checklist
│
├── diagrams/                   ← REQUIRED by assignment
│   ├── architecture.mmd        ← system architecture (Mermaid source)
│   └── uml_final.mmd           ← updated class diagram
│
├── assets/                     ← REQUIRED by assignment
│   └── architecture.png        ← exported PNG
│
├── logs/                       ← runtime output
│   └── advisor_log.txt         ← timestamped AI query/response log
│
├── demo/                       ← screenshots from Module 2
├── tests/
│   └── test_pawpal.py          ← 14 existing + new tests (target 20+)
│
├── app.py                      ← +Step 5 (AI advisor)
├── main.py                     ← unchanged CLI demo
├── pawpal_system.py            ← +detect_group_walks(), +detect_overlap_conflicts()
├── ai_advisor.py               ← NEW
├── README.md                   ← full rewrite per spec
├── model_card.md               ← NEW (required responsible-AI reflection)
├── requirements.txt            ← +anthropic>=0.25
└── .env.example                ← ANTHROPIC_API_KEY placeholder
```

---

## Execution Order

1. Copy source files from Module 2 project
2. Add `detect_group_walks()` + `detect_overlap_conflicts()` to `pawpal_system.py`
3. Extend test suite to cover new methods (target 20+ tests passing)
4. Build `ai_advisor.py` (context builder + Claude API call + logger)
5. Wire Step 5 into `app.py`
6. Write `diagrams/architecture.mmd` + update `diagrams/uml_final.mmd`
7. Write `model_card.md`
8. Rewrite `README.md` with sample AI interactions (fenced code blocks)
9. Smoke test: run app, ask 3 questions, paste outputs into README
10. Final commit + push

---

---

## Session Log — 2026-07-28 (Day 1)

### ✅ Done today

| # | What | File(s) touched |
|---|------|----------------|
| 1 | Created final project repo with full folder structure | `ai110-finalproject-pawpalplus/` |
| 2 | Copied all Module 2 source files, initialized git, first commit | all root files |
| 3 | Created venv, installed requirements, ran baseline app | `.venv/` |
| 4 | Created 3 planning docs | `planning/overview.md`, `rag_design.md`, `submission_checklist.md` |
| 5 | JSON data persistence — seed file + "Load saved data" UI at Step 1 | `data/users.json`, `app.py` |
| 6 | Species dropdown fix — added rabbit, bird, fish, hamster | `app.py` |
| 7 | `Scheduler.detect_group_walks()` — same-species walk at same slot = group walk | `pawpal_system.py` |
| 8 | `Scheduler.detect_overlap_conflicts()` — flags duration overlaps, not just exact time clashes | `pawpal_system.py` |
| 9 | Copied README from Module 2, removed CLI output, added all required sections with `[TODO]` placeholders | `README.md` |

---

## What Still Needs to Be Done

Work through these in order — each builds on the last:

### 🔲 1. Extend the test suite — `tests/test_pawpal.py` (30 min)
- Add 6+ new tests covering `detect_group_walks()` and `detect_overlap_conflicts()`
- Target: 20+ tests, all passing
- Run: `python -m pytest tests/ -v` and paste the output into the `README.md` testing section

### 🔲 2. Wire 3-state rendering in `app.py` Step 3 + Step 4 (30 min)
- Step 3 task list and Step 4 schedule table currently show 2 states (normal / orange ⚠)
- Add **blue 🐾 group walk** as a third state using `Scheduler.detect_group_walks()`
- Also wire **overlap conflict** warnings into the Step 4 conflict banner

### 🔲 3. Mark-complete + recurrence in `app.py` Step 3 (20 min)
- Add a ✓ checkbox per task row
- On check: call `task.mark_complete()` then `scheduler.handle_recurrence(task, pet)`
- Backend already coded — just needs to be wired to the UI

### 🔲 4. Build `ai_advisor.py` (60 min)
- See `planning/rag_design.md` for full design
- Key functions: `build_context(owner)`, `ask_advisor(owner, question)`, `log_interaction(q, a)`
- Model: `claude-haiku-4-5-20251001`, max_tokens=512
- Add `anthropic>=0.25` and `python-dotenv` to `requirements.txt`
- Create `.env.example` with `ANTHROPIC_API_KEY=your-key-here`
- Create `.env` locally with real key (already gitignored)

### 🔲 5. Wire Step 5 into `app.py` (20 min)
- Text input for question → call `ask_advisor(owner, question)` → display response
- Handle missing API key gracefully (Streamlit warning, no crash)
- Take a screenshot of Step 5 in action for the README

### 🔲 6. Run the app, ask 3 real questions, paste outputs into README (20 min)
- Load Abhishek's profile, add tasks for Chintu/Pintu/Chinni
- Ask 3 natural-language questions and capture the AI responses
- Paste as fenced code blocks into the `[TODO]` sections in `README.md`

### 🔲 7. Write `diagrams/architecture.mmd` (20 min)
- Mermaid flowchart: User → Streamlit UI → Scheduler / AI Advisor → Claude API → Logger
- Also update `diagrams/uml_final.mmd` to include the 2 new Scheduler methods

### 🔲 8. Write `model_card.md` (30 min)
- How Claude Code was used to build this project
- One helpful AI suggestion (with example)
- One flawed AI suggestion and how it was caught/fixed
- System limitations

### 🔲 9. Final checks before submission (30 min)
- `streamlit run app.py` — smoke test all 5 steps end to end
- `python -m pytest tests/ -v` — all 20+ tests green
- Create public GitHub repo → push → verify commit history looks clean
- Check every box in `planning/submission_checklist.md`
- **Deadline: Monday August 3rd, 1:59 AM CDT**

---

## Session Log — 2026-07-31 (Day 2)

### ✅ Done today

| # | What | File(s) touched |
|---|------|----------------|
| 1 | 3-state conflict rendering — group walks shown in blue 🐾, real conflicts in orange ⚠ | `app.py`, `pawpal_system.py` |
| 2 | Conflict messages now include pet names — "Feeding (Pintu) and Feeding (Chinni)" | `pawpal_system.py` |
| 3 | Today's date added to Step 4 daily schedule header | `app.py` |
| 4 | Weekly schedule (Step 5) added — daily tasks on today, weekly on next Saturday, once tasks 3 business days out | `app.py` |
| 5 | Both schedules stay on screen simultaneously via `show_daily` / `show_weekly` session flags | `app.py` |
| 6 | Step 2 (Add a Pet) and Step 3 (Add a Task) made collapsible with counts in expander headers | `app.py` |
| 7 | Test suite extended from 14 to 25 tests, all passing | `tests/test_pawpal.py` |
| 8 | `ai_advisor.py` built — RAG context builder, Claude API call (`claude-haiku-4-5-20251001`), interaction logger | `ai_advisor.py` |
| 9 | AI advisor wired into app as Step 6 | `app.py` |
| 10 | `model_card.md` created with 3 flawed AI suggestions, 1 helpful suggestion, system limitations | `model_card.md` |
| 11 | README updated — testing section filled with real pytest output, Design Decisions expanded | `README.md` |
| 12 | ✅ Mark-complete button per task in Step 3, Step 4 (daily), and Step 5 (weekly) — grey strikethrough on completion, recurrence triggered | `app.py` |
| 13 | "X/Y done" counts per pet in daily and weekly schedule headers | `app.py` |
| 14 | 📄 Download schedule button (HTML → printable PDF) added inline next to each generate button | `app.py` |
| 15 | Model card updated with third flawed AI case: over-engineering completion UI vs. preserving readable HTML table | `model_card.md` |

### 📋 Remaining Before Submission (revisit tomorrow)

| Priority | Task |
|----------|------|
| HIGH | Run app with real API key → ask 3 questions → paste outputs into README `[TODO]` blocks |
| HIGH | Create public GitHub repo, push, verify commit history is meaningful and multiple |
| HIGH | Final smoke test: all 6 steps end-to-end, 25 tests green |
| HIGH | Check every box in `planning/submission_checklist.md` |
| MED | `diagrams/architecture.mmd` — Mermaid flowchart of system architecture |
| MED | Update `diagrams/uml_final.mmd` with new Scheduler methods |
| LOW | Demo screenshot of Step 6 (AI advisor) for README |

---

## What's Unchanged from Module 2

- `Task`, `Pet`, `Owner`, `Scheduler` core classes — keep as-is
- `main.py` CLI demo — keep
- `demo/` screenshots — keep
- `diagrams/uml.mmd` (initial design) — keep
- All 14 existing tests — keep, extend
