# PawPal+ — Applied AI Pet Care Scheduler

> **Final project for AI110 | Foundations of AI Engineering — Module 4**
> Built on top of [ai110-module2show-pawpal-starter](https://github.com/abhishek-dhall/ai110-module2show-pawpal-starter), which established the four-class scheduling backend (`Task`, `Pet`, `Owner`, `Scheduler`) and a working Streamlit UI. This final project extends that foundation with an AI-powered care advisor, smarter conflict detection, group walk recognition, and persistent user profiles.

**PawPal+** is a pet care scheduling app for owners with multiple pets. It builds a conflict-checked daily schedule across all your animals, spots problems before they happen — two pets booked at the same time, a walk that runs into a vet appointment — and lets you ask a built-in AI advisor plain-English questions about your pets' day. Your profile saves between sessions, so there is no setup the second time you open it.

---

## What it does

### 📅 Scheduling

PawPal+ treats every pet's routine as a first-class schedule. Add tasks with a name, time, duration, priority (high / medium / low), and frequency (once / daily / weekly), and the app does the rest.

- **Daily view** — One click shows only today's tasks sorted by priority then time. High-priority items surface first so nothing urgent gets buried under routine chores.
- **Weekly view** — An expanded view places daily tasks on today's date and weekly tasks (grooming, vet checkups) on their next occurrence, giving you a full picture of the week ahead.
- **Recurring tasks** — Mark a task complete and the next occurrence is created automatically — tomorrow for daily tasks, seven days out for weekly ones. One-time tasks disappear after completion.
- **Downloadable schedules** — Generate a clean HTML schedule for any view and download it as a printable file — the kind of thing you tape to the fridge.

### ⚠️ Conflict detection

Scheduling multiple pets by hand is error-prone. PawPal+ runs two conflict detectors on every update and renders results in three distinct states so you always know what you're looking at.

- **Exact conflict → orange ⚠** — Two tasks sharing the same time slot are flagged immediately, with both pet names in the warning so you know exactly what to fix.
- **Duration-overlap → orange ⚠** — A 30-min walk at 07:30 and a vet appointment at 08:00 overlap even though their start times differ. PawPal+ catches this too, not just exact clashes.
- **Group walk → blue 🐾** — Two dogs both scheduled for a morning walk at 07:00 is not a conflict — it's good planning. Same-species pets with a walk at the same slot are highlighted blue instead of orange, with no warning to resolve.
- **Inline edit to resolve** — Click ✏️ on any task to change its time directly in the row. No need to delete and re-add just to shift a feeding by 15 minutes.

### 🤖 AI Care Advisor

The advisor answers natural-language questions about your pets' schedule using your actual data — not generic advice. It knows your pets' names, their tasks, what's overdue, and what conflicts exist right now.

- **Grounded answers** — Every question is answered using the live schedule as context. Ask *"What's most urgent for Chintu today?"* and the response references Chintu's real tasks and times, not a template.
- **Conflict-aware** — The advisor sees the same conflict data the UI shows, so it can explain what's overlapping and suggest specific fixes (e.g. "move Pintu's feeding to 07:45").
- **Interaction log** — Every question and answer is saved to `logs/advisor_log.txt` with a timestamp, giving you a record of advice over time.
- **Evaluation harness** — `eval_advisor.py` runs 5 predefined questions and checks each response for expected keywords, verifying the advisor stays grounded as the schedule changes.

### ✨ Setup & usability

- **Saved profiles** — Owner and pet data persists in `data/users.json`. One click at startup restores everything — no re-entering names or pets each session.
- **Collapsible setup** — The Add a Pet and Add a Task panels collapse once your data is loaded, so the daily schedule is front and centre when you open the app. Expand either panel any time to make changes.
- **Smart emoji labels** — Species icons (🐕 🐈 🐇 🦜 🐠 🐹) and task-type icons (🚶 walk, 🍽️ feed, 💊 meds, 🏥 vet, ✂️ groom, 🎾 play) are inferred automatically from pet species and task name — no manual tagging needed.

---

## Getting started

```bash
# 1. Clone and create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# 2. Set your Anthropic API key (needed for the AI advisor in Step 6)
cp .env.example .env
# Open .env and set: ANTHROPIC_API_KEY=your-key-here

# 3. Launch the app
streamlit run app.py          # opens http://localhost:8501
```

> The app works fully without an API key — the AI advisor (Step 6) will show a warning if the key is missing, but all scheduling features remain available.

---

## 📸 Demo Walkthrough

**Step 1 — Load your profile or set your name**
If saved user data is found, the app shows a "Load [name]'s data" button. One click restores your owner profile and all pets — skip re-entering everything every session.

![Owner welcome screen](demo/1-pet-owner-welcome-screen.png)

---

**Step 2 — Add a pet**
Enter a pet name and species (dog, cat, rabbit, bird, fish, hamster, or other), then click **Add pet**. All added pets appear above the form.

![Pet saved](demo/2-saved-a-pet.png)

---

**Step 3 — Add tasks**
Select which pet, fill in the task name, time (HH:MM), duration, priority, and frequency, then click **Add task**. Each task row has ✏️ edit, ✅ complete, and 🗑 delete buttons.

![Adding first task](demo/3-add-task1.png)

---

**Conflict highlight — orange ⚠**
Tasks sharing the same time slot are flagged in orange. The conflict banner tells you to edit the time or delete a task to resolve.

![Conflicting task shown in orange](demo/4-add-conflicting-task.png)

---

**Group walk highlight — blue 🐾**
Same-species pets with a walk at the same time slot turn blue — cooperative scheduling, not a conflict.

![Group walk shown in blue](demo/5-add-conflicting-task.png)

---

**Edit to resolve**
Click ✏️ on a conflicting task to change its time inline — no need to delete and re-add.

![Inline edit to resolve conflict](demo/6-delete-taks-add-newtaks-no-conflcit.png)

---

**Step 4 — Generate today's schedule**
One click filters to tasks due today and produces a clean daily view sorted by priority then time. Conflicting rows stay orange; group walk rows show blue. No date column needed — everything is today.

**Step 5 — Generate the weekly schedule**
Shows all tasks across the week — daily tasks on today's date, weekly tasks on the next Saturday — with a Date column so you can see at a glance what's coming up. Sorted by date first, then priority.

**Step 6 — Ask your AI advisor**
Type a plain-English question. The advisor reads your current schedule and responds with grounded, specific advice.

![AI advisor answering a scheduling question](demo/7-ai-advisor-response.png)

---

## 🤖 Sample AI Advisor Interactions

> These are real outputs from the live app with Abhishek's pets (Chintu 🐕, Pintu 🐕, Chinni 🐈) loaded.

**Q: What's most urgent for my dogs today?**
```
Based on your schedule, here are the high-priority tasks due today for Chintu and Pintu:

Daily High-Priority Tasks:
1. Morning Walk – 07:00 (30 min) – Both dogs
2. Feeding – 07:30 (Chintu) & 08:00 (Pintu) – 10 min each
3. Evening Walk – 18:00 (25 min) – Both dogs

Good news: You can do the morning and evening walks together since both dogs need them at the same time!

Upcoming High-Priority:
- Pintu's Vet Checkup – due 2026-08-05 at 10:30 (60 min)

The daily walks and feeding are your most time-sensitive items today.
```

**Q: Can Chintu and Pintu do their morning walk together?**
```
Yes! Chintu and Pintu can do their morning walk together. Both are scheduled for a
morning walk at 07:00 for 30 minutes on a daily basis. Since they're both dogs,
a group walk is practical and efficient. This would actually resolve the scheduling
conflict at that time slot.

Suggestion: Schedule them as a combined "Morning Walk (Chintu & Pintu)" at 07:00
for 30 minutes daily instead of two separate tasks.
```

**Q: Are there any scheduling conflicts I should fix?**
```
Yes, there are 3 scheduling conflicts to address:

1. 07:00 – Morning Walk (Chintu & Pintu)
   Both dogs are scheduled simultaneously for 30 minutes.
   Fix: This is actually fine! A group walk with both dogs together works well.

2. 18:00 – Evening Walk (Chintu & Pintu)
   Both dogs scheduled simultaneously for 25 minutes.
   Fix: Again, a group walk works here too.

3. 08:00 – Feeding (Pintu & Chinni)
   Pintu (dog) and Chinni (cat) feeding overlap.
   Fix: Move one feeding time — shift Pintu's feeding to 07:45 (right after his
   morning walk ends at 07:30) or Chinni's feeding to 08:15.

Summary: The dog walks can stay as group walks, but adjust one of the 08:00
feedings by 15–30 minutes.
```

---

## 🧪 Testing

```bash
python -m pytest tests/test_pawpal.py -v
```

```
============================= 25 passed in 0.10s ==============================
```

**25 / 25 passing** (target: 20+ ✓). The two new Scheduler methods added in this project — `detect_group_walks()` and `detect_overlap_conflicts()` — each have 3–4 dedicated test cases covering the positive case, the negative case, and edge cases.

**What the tests cover:**
- **Sorting** — chronological HH:MM order; priority sort (high → medium → low), time as tiebreaker
- **Exact conflict detection** — duplicate time slots flagged with both pet names (e.g. `'Feeding' (Pintu) and 'Feeding' (Chinni)`)
- **Duration-overlap detection** — overlapping time windows caught even with different start times; touching-but-not-overlapping tasks are not flagged
- **Group walk recognition** — same-species + walk at same slot → group walk; different species or different time → not flagged
- **Recurrence** — daily/weekly tasks create next occurrence after completion; `once` tasks do not
- **Filter by status and by pet** — case-insensitive; returns empty list on no match
- **Task removal** — `remove_task()` returns `True` on match, `False` when name or time doesn't match
- **Edge cases** — empty pet list, already-completed task, different-date tasks that share a time do not false-alarm

AI advisor responses are verified via `eval_advisor.py` (keyword-check harness, 5/5 passing) and `logs/advisor_log.txt` (timestamped interaction log) rather than unit tests — LLM output is non-deterministic and checked by behaviour, not exact string match.

---

## 🏗️ Architecture

### System overview

Full Mermaid source: [`diagrams/architecture.mmd`](diagrams/architecture.mmd)
Full UML class diagram: [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd)

Five modules work together:

| Module | Role |
|--------|------|
| `pawpal_system.py` | Core backend — `Task`, `Pet`, `Owner`, `Scheduler` classes |
| `app.py` | Streamlit UI — 6-step flow connecting user input to backend logic |
| `ai_advisor.py` | AI integration — builds schedule context, calls Claude API, logs interactions |
| `data/users.json` | Persistent user profiles — owner name and pet roster across sessions |
| `logs/advisor_log.txt` | Interaction log — every AI query and response with timestamp |

UML diagrams: [`diagrams/uml.mmd`](diagrams/uml.mmd) (initial design) and [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd) (final implementation with new Scheduler methods).

---

## 🧩 Design Decisions

- **HH:MM string for time, not datetime** — Keeps the data model simple and lets Python's default string sort order handle chronological sorting correctly for times within a single day. A full `datetime` object would be necessary for multi-day scheduling but adds complexity that isn't needed here.
- **JSON for user profiles, not a database** — A flat JSON file is readable, version-controllable, and has zero infrastructure dependencies. For a single-user scheduling tool, a database would be over-engineering.
- **Two conflict detectors, not one** — `detect_conflicts()` (exact match) was in Module 2 and all its tests pass. `detect_overlap_conflicts()` was added as an enhancement without touching the original — they run side by side, each catching what the other misses.
- **3-state rendering, not binary conflict/no-conflict** — The initial AI-generated implementation flagged any two tasks sharing a time slot as a conflict (orange ⚠). Human review caught that two dogs walking together at the same time is cooperative scheduling, not a problem. This required a third state — blue 🐾 for group walks — and a new `detect_group_walks()` method. The AI's purely mechanical approach needed domain knowledge from the human to get right. Full write-up in [`model_card.md`](model_card.md).
- **Claude Haiku for the AI advisor** — Fast response times and low cost make it practical for interactive Q&A in a scheduling tool. The context window is small enough (one owner's schedule) that a larger model adds no benefit.
- **RAG via in-memory context, not a vector store** — The owner's full schedule is small enough to format as plain text and inject directly into the prompt. A vector database would be necessary only if the context grew to thousands of tasks.

---

## 🛡️ Reliability & Guardrails

The system includes three layers of reliability protection.

### Input validation — API key guard

If `ANTHROPIC_API_KEY` is not set, the advisor fails safely with an actionable message instead of throwing an unhandled exception:

| Input | Behavior | Result shown to user |
|-------|----------|---------------------|
| Question sent, no API key in `.env` | `ask_advisor()` checks env before calling API | `"ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key, then restart the app."` |
| Question sent, key present | Claude is called with schedule context | Grounded answer referencing real pet names and times |
| Empty question submitted | Streamlit `st.form` blocks submission | Submit button disabled until text is entered |

### Output guardrail — system prompt scope restriction

The system prompt explicitly instructs the model to answer only from the provided schedule data:

> *"Answer questions based only on the data provided in the schedule above. If a question cannot be answered from the schedule data, say so clearly rather than guessing."*

This prevents the model from drifting into generic pet-care advice when the user's schedule is the authoritative source.

### Evaluation script — `eval_advisor.py`

A test harness that runs 5 predefined questions through the live advisor and checks each response for expected keywords:

```
Test 3: Identifies the 08:00 feeding conflict with pet names
  Q: Are there any scheduling conflicts I should fix?
  A: Yes, there are 3 scheduling conflicts to address...
     08:00 – Feeding (Pintu & Chinni)
  PASS — keywords matched: ['08:00', 'feeding', 'pintu', 'chinni']
```

Run: `python eval_advisor.py` — prints a scored summary; saves full output to `logs/eval_log.txt`.
Full 5/5 eval run is shown in the [Stretch Features](#-stretch-features) section below.

---

## 🚀 Stretch Features

### RAG-Powered Context

The AI advisor uses **Retrieval-Augmented Generation (RAG)** to ground every response in the owner's live schedule. Rather than answering from general pet-care knowledge, the system builds a structured context block at query time and injects it into the Claude prompt as the user message preamble:

```
Today's date: Sunday, August 02, 2026
Owner: Abhishek
Pets: Chintu (dog), Pintu (dog), Chinni (cat)

Chintu's tasks:
  - Morning Walk at 07:00 (30 min, high priority, daily, due 2026-08-02)
  - Feeding at 07:30 (10 min, high priority, daily, due 2026-08-02)
  ...

Scheduling conflicts detected:
  - Overlap: Feeding (Pintu) and Feeding (Chinni) at 08:00 on 2026-08-02
```

The model is told to answer only from this context, not from general knowledge. This means responses reference real pet names, real times, and real conflicts — not generic advice.

### AI Advisor Test Harness

`eval_advisor.py` is an automated evaluation script that runs the live advisor against 5 pre-defined questions and checks each response for expected keywords. It loads the real user profile, calls `ask_advisor()`, and prints a pass/fail scored summary.

Run it from the project root:

```bash
python eval_advisor.py
```

**Eval output (2026-08-02 run):**

```
============================================================
PawPal+ AI Advisor — Evaluation Harness
============================================================
Profile loaded: Abhishek — 3 pets, 15 tasks

Test 1: Identifies high-priority dog tasks with pet names
  Q: What is most urgent for my dogs today?
  PASS — keywords matched: ['chintu', 'pintu', 'walk', 'feeding', 'high']

Test 2: Recognises group walk opportunity at 07:00
  Q: Can Chintu and Pintu do their morning walk together?
  PASS — keywords matched: ['together', '07:00', 'group']

Test 3: Identifies the 08:00 feeding conflict with pet names
  Q: Are there any scheduling conflicts I should fix?
  PASS — keywords matched: ['08:00', 'feeding', 'pintu', 'chinni']

Test 4: Returns Chinni's specific tasks
  Q: What tasks are scheduled for Chinni today?
  PASS — keywords matched: ['chinni', 'feeding', 'litter']

Test 5: Finds upcoming vet appointments across pets
  Q: Which pet has a vet appointment coming up?
  PASS — keywords matched: ['vet', 'pintu', 'chinni']

============================================================
Results: 5/5 passed

  ✓  Identifies high-priority dog tasks with pet names
  ✓  Recognises group walk opportunity at 07:00
  ✓  Identifies the 08:00 feeding conflict with pet names
  ✓  Returns Chinni's specific tasks
  ✓  Finds upcoming vet appointments across pets
============================================================
All tests passed — advisor is grounded in schedule data.
```

Full eval log saved to `logs/eval_log.txt`. The harness skips tests gracefully if the API key is missing, making it safe to run in offline environments.

---

## 💭 Reflection

### How AI was used during development

Claude Code was the primary development partner throughout this project — not just for writing boilerplate, but for design decisions and algorithm choices. It drafted the `Task`/`Pet`/`Owner`/`Scheduler` class hierarchy, implemented `detect_group_walks()` and `detect_overlap_conflicts()` from natural-language descriptions, built the 6-step Streamlit flow, and designed the RAG context builder and prompt template. Every change was reviewed and approved before committing. Final decisions on features, data design, and UI behavior were made by the human developer.

### One helpful AI suggestion

**Use in-memory context injection instead of a vector store.** The AI recommended formatting the owner's full schedule as plain text and injecting it directly into the Claude prompt — no vector database, no embeddings. This was the right call: a single owner's schedule fits in one prompt, and skipping the vector store kept the system runnable with just a Python venv and an API key.

### One flawed AI suggestion

**Group walks flagged as conflicts.** The AI's initial conflict detector flagged any two tasks sharing a time slot as an error — so Chintu and Pintu's morning walk at 07:00 showed as a red ⚠ "Conflict — delete one task to resolve." The AI had no concept of cooperative scheduling. The human developer caught this immediately when loading the saved profile: two dogs walking together is a feature, not a bug. The fix required a new `detect_group_walks()` method and a third rendering state (blue 🐾 for group walks), which the AI could not have initiated on its own.

### System limitations

- Single-user, single-session — no multi-user support or server-side persistence
- HH:MM string time — cannot handle tasks crossing midnight or reason about time zones
- AI advisor responses are not deterministic — same question may produce different answers
- Group walk detection relies on the word "walk" in the task name — "outdoor exercise" is not recognised
- Western pet care bias in the underlying model — advice may not reflect non-Western norms or unusual species

> Full responsible-AI analysis — including three flawed suggestions, potential misuse scenarios, and what surprised us testing AI reliability — is in [`model_card.md`](model_card.md).
