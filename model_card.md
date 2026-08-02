# Model Card — PawPal+ AI Care Advisor

**Project:** PawPal+ — Applied AI Pet Care Scheduler
**Course:** AI110 | Foundations of AI Engineering — Module 4
**AI model used in the product:** `claude-haiku-4-5-20251001` (Anthropic)
**AI model used to build the product:** Claude Code (`claude-sonnet-4-6`) via Anthropic Claude Code CLI

---

## How AI Was Used to Build This Project

Claude Code was used throughout development as an active coding partner — not just for boilerplate, but for design decisions, algorithm choices, and debugging:

- **Backend design** — Drafted the `Task`, `Pet`, `Owner`, `Scheduler` class hierarchy and recommended Python dataclasses for clean field defaults and zero-boilerplate constructors
- **Algorithm implementation** — Wrote `detect_group_walks()` and `detect_overlap_conflicts()` from natural-language descriptions of the intended behavior
- **UI scaffolding** — Built the 5-step Streamlit flow, session state management, and the 3-state color rendering system
- **Data design** — Designed the `data/users.json` schema and the 19-task seed dataset, intentionally placing tasks to showcase all 3 detection states (group walk, exact conflict, duration overlap)
- **AI integration** — Designed the RAG context builder, Claude API call pattern, prompt template, and interaction logger

All code was reviewed and approved by the human developer before committing. Final decisions on features, data design, and UI behavior were made by the human.

---

## Helpful AI Suggestion

**Suggestion:** Use in-memory context injection instead of a vector store.

When designing the AI advisor, the AI recommended formatting the owner's entire schedule as plain text and injecting it directly into the Claude prompt — no vector database needed. This was the right call: a single owner's schedule (5 pets, ~20 tasks) fits comfortably in one prompt, and skipping the vector store kept the system runnable with just a Python venv and an API key.

**Example context block injected into every advisor prompt:**
```
Owner: Abhishek
Pets: Chintu (dog), Pintu (dog), Chinni (cat)

Chintu's tasks:
  - Morning Walk at 07:00 (30 min, high priority, daily)
  - Feeding at 07:30 (10 min, high priority, daily)
  - Grooming at 10:00 (45 min, medium priority, weekly)
  ...

Scheduling conflicts detected:
  - Overlap: Chintu Grooming (10:00, 45 min) overlaps Pintu Vet Checkup (10:30, 60 min)
```

The model answers using real names, times, and conflict details from this context — not generic pet-care advice.

---

## Flawed AI Suggestion — Overridden by Human Judgment

**The flaw:** The AI's initial conflict detection flagged same-species walks at the same time as scheduling errors.

When two dogs (Chintu and Pintu) both had a "Morning Walk" scheduled at 07:00, the AI-generated conflict detector flagged both rows in orange ⚠ with the message *"Conflict at 07:00 — delete one task to resolve."* The AI treated any two tasks sharing a time slot as a problem. It had no concept of the difference between a genuine conflict (two incompatible tasks) and a cooperative scenario (two dogs walking together).

**How it was caught:** The human developer (Abhishek) loaded the saved profile and immediately saw Chintu and Pintu's morning and evening walks highlighted as errors. The banner told him to delete one of the walks — the opposite of the intended experience. Walking two dogs together is a feature, not a bug.

**How it was fixed:** The human directed the AI to implement 3-state rendering:

| State | Color | Meaning |
|-------|-------|---------|
| Normal | — | No overlap |
| Conflict | Orange ⚠ | Different-species tasks at the same time, or overlapping durations |
| Group walk | Blue 🐾 | Same-species pets with a walk at the same slot — cooperative, not a problem |

This required a new `Scheduler.detect_group_walks()` method in the backend and updated rendering logic in both the Step 3 task list and the Step 4 schedule table. The conflict banner was split into a blue info section (group walks) and an orange warning section (real conflicts).

**The lesson:** The AI's mechanical approach — any time-slot collision is a conflict — was logically consistent but domain-ignorant. The human's real-world understanding of what pet care actually looks like was necessary to catch and correct it.

---

**Second flawed suggestion: conflict messages contained no pet names**

The AI-generated `detect_conflicts()` produced messages like:

```
Conflict at 08:00 on 2026-07-31: 'Feeding' and 'Feeding'
```

This is technically correct — there is a conflict at 08:00 — but operationally useless. The owner cannot act on it without knowing *which* pets are involved. With five pets on the schedule, "Feeding and Feeding" gives no information about where to look or what to change.

The human noticed this immediately when loading the saved profile and pointed out that the message should name the pets. The fix was to store `(pet_name, task_name)` in the conflict tracker instead of just `task_name`, producing:

```
Conflict at 08:00 on 2026-07-31: 'Feeding' (Pintu) and 'Feeding' (Chinni)
```

The AI optimized for detecting the conflict. The human optimized for the owner being able to resolve it. Both matter; the AI only delivered one.

---

## Human-Directed Feature Expansion

Beyond catching flaws, the human developer directed feature additions that extended the AI's correct baseline implementation:

**Adding a weekly overview on top of the daily schedule**

The AI correctly built Step 4 as a daily schedule — the primary use case, showing only today's tasks sorted by priority. This was working as intended.

The human then recognized that weekly-frequency tasks (grooming, vet checkups, tank cleaning) have a specific day they happen — the next Saturday — and that a pet owner would benefit from seeing the full week at a glance, not just today. This became Step 5: a separate weekly view where daily tasks show on today's date and weekly tasks are placed on the next Saturday, with a Date column making the spread visible.

The AI's Step 4 implementation was correct. Step 5 was a human-directed addition, not a correction — an example of iterative feature expansion through conversation rather than fixing an error.

---

## Third Flawed AI Approach — Over-Engineering the Completion UI

**The flaw:** The AI rebuilt the schedule display around interactivity at the cost of readability.

When asked to add a ✅ mark-complete button per task row, the AI switched both the daily schedule (Step 4) and the weekly schedule (Step 5) from clean HTML tables to Streamlit column-based layouts. This was necessary — Streamlit HTML tables cannot hold buttons — but the AI made the change without flagging the trade-off: the chronological, print-friendly table that the owner had found most readable was gone, replaced by per-pet groupings optimised for interaction rather than at-a-glance scanning.

**How it was caught:** The human developer reviewed the result and recognised that the clean printable overview — the kind of schedule you tape to a fridge — had disappeared. Both the interactive completion flow and the scannable table were needed, not just one.

**How it was fixed:** Rather than reverting the interactive view, the human directed adding a "📄 Download schedule" button that regenerates the original HTML table as a standalone downloadable file. The file opens in any browser and prints cleanly to PDF. Both views now coexist: the interactive per-pet layout for marking tasks done inside the app, and the downloadable table for printing or sharing.

**The lesson:** AI optimises for the immediate feature request. When adding interactivity to a display component, it will rebuild the component around the interaction pattern without questioning whether the display format itself should be preserved. The human needs to hold the overall UX vision — "what does a person actually do with this?" — and push back when a local change degrades the whole experience.

---

## System Limitations and Biases

- **Single-user, single-session** — The app holds one owner's data in memory per browser session. There is no authentication, no multi-user support, and no server-side session persistence. A page refresh clears all manually-added tasks (saved profiles in `data/users.json` are reloaded, but in-session additions are lost).
- **HH:MM string time, not datetime** — Scheduled times are stored as strings. The system cannot handle tasks that cross midnight, reason about time zones, or calculate absolute timestamps.
- **No calendar view** — The weekly schedule (Step 5) shows tasks across today and next Saturday, but there is no multi-week calendar, no drag-and-drop rescheduling, and no ability to browse past or future weeks.
- **AI advisor responses are not deterministic** — The same question asked twice may produce different answers. Responses are verified manually via `logs/advisor_log.txt`, not by automated tests.
- **Context is not verified for completeness** — The advisor is told the current schedule via a text prompt. If the user hasn't finished entering all tasks, the advisor answers based on incomplete data without warning.
- **Conflict resolution is manual** — The app flags conflicts but resolves them only by deletion. It cannot suggest alternative times, negotiate between pets' needs, or auto-reschedule.
- **Group walk detection is name-based** — `detect_group_walks()` checks for the word "walk" in the task name. Tasks named "outdoor exercise" or "leash training" are not recognized as walks and won't qualify for the blue 🐾 treatment.
- **Western pet care bias** — The AI advisor's underlying model (Claude Haiku) was trained on internet-scale data that skews toward Western pet care norms. Advice about feeding schedules, vet visit frequency, and exercise routines may not reflect regional practices, cultural differences in pet ownership, or non-standard species. A hamster owner or a fish keeper may receive generic advice that does not apply to their pet.
- **Seed data bias** — The demo data (Chintu, Pintu, Chinni) reflects one specific pet owner's routine. The task names, times, and priorities baked into `data/users.json` shape what the advisor "sees" in demos — a grader testing with this data may get more grounded answers than a new user starting from scratch.

---

## Potential Misuse and Prevention

**Could the AI advisor be misused?**

Yes, in two ways:

1. **Privacy leakage** — Every question sent to the advisor includes the owner's full schedule as a text prompt, which is sent to Anthropic's API servers. If a user entered sensitive information in task names (medication details, personal health notes, private appointments), that data would leave the local app. The system has no guardrails against this.

2. **Prompt injection** — A malicious user could type a question designed to override the system prompt and make the advisor produce harmful or off-topic output (e.g. "Ignore all previous instructions and..."). The current system passes user input directly into the prompt with no sanitization.

**Prevention measures in place:**
- The system prompt explicitly instructs the model to answer only from the provided schedule data and refuse off-topic requests
- The API key is stored locally in `.env` and never committed to git — protecting the user's own account
- Schedule data is session-only and never persisted beyond `data/users.json` (which contains no sensitive fields)

**What would be added in a production version:**
- Input sanitization to strip prompt-injection patterns before sending to the API
- A warning in the UI advising users not to enter personal health or medical information in task names
- Rate limiting to prevent API abuse

---

## What Surprised Us Testing AI Reliability

**1. The advisor didn't know what day it was**
The biggest surprise was that the AI answered "I don't have today's date in your schedule data" even when the tasks clearly had `due_date: 2026-08-02`. The model could see the dates in the task list but had no anchor for what "today" meant. Injecting `Today's date: Sunday, August 02, 2026` as the first line of the context block fixed it immediately. It was a reminder that the model only knows what you explicitly tell it — it does not have ambient awareness of the environment the way a human would.

**2. Responses were helpful but assumed perfect data**
When asked "Are there any conflicts I should fix?", the advisor correctly identified the 08:00 feeding overlap between Pintu and Chinni and suggested a specific fix (move one feeding to 07:45). This was genuinely useful. But it gave the same quality of answer whether the owner had entered 3 tasks or 15 — it never flagged that the schedule looked incomplete or that important tasks might be missing. The model is confident by default; it does not express uncertainty about what it doesn't know.

**3. Group walk recognition worked without being told**
When both dogs had a Morning Walk at 07:00, the advisor correctly said they could walk together — it inferred the cooperative nature of the schedule from the pet species and task names without any explicit instruction. This was a pleasant surprise and reinforced why injecting rich context (pet names, species, task names) rather than just times and durations matters.
