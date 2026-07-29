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

## What's Unchanged from Module 2

- `Task`, `Pet`, `Owner`, `Scheduler` core classes — keep as-is
- `main.py` CLI demo — keep
- `demo/` screenshots — keep
- `diagrams/uml.mmd` (initial design) — keep
- All 14 existing tests — keep, extend
