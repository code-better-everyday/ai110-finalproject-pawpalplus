# PawPal+ Project Reflection

## 1. System Design

- You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## 3 core features 
- Add a pet and their tasks and needs
- schedule a task or care item for any pet based on time and calendar availabiliy 
- See today and weekly schgedule of task define for today based on time availabaility and pet care that is important 




**Assumptions**

- **Single owner per session** — the app supports one owner at a time. The Owner is created from the name entered in the UI and stored in session state for the duration of the app session. There is no login or multi-user system.
- **Time as a string** — `scheduled_time` is stored as a plain "HH:MM" string rather than a full datetime object. This keeps the data simple and is sufficient for sorting with a lambda and detecting exact-time conflicts.
- **Date separate from time** — `due_date` is stored as a `date` object (not combined into a datetime). A task is fully identified by its `due_date` + `scheduled_time` together.
- **Priority and frequency as strings** — both are plain strings ("low"/"medium"/"high" and "once"/"daily"/"weekly") rather than enums, to keep the code approachable at this stage.
- **Conflict detection by exact time match** — two tasks conflict if they share the same `scheduled_time` on the same `due_date`. Overlapping durations are not checked in the core design.
- **All pets belong to one owner** — there is no concept of shared pets between owners in this design.
- **Owner name is unique per session** — the app treats the owner name entered in the UI as the single user identity. There is no authentication or duplicate-name detection.
- **Pet name is unique per owner** — each pet added to an owner is assumed to have a distinct name. The app does not prevent two pets with the same name, but filtering and display logic assumes names are unique.

---

**a. Initial design**

I designed a four-class system where each class has a single, clear responsibility.

- **Task** — represents one care activity. It stores the task name, scheduled time (HH:MM format), duration in minutes, priority (low/medium/high), frequency (once/daily/weekly), completion status, and due date. It can mark itself complete and describe itself as a string.

- **Pet** — stores a pet's name and species, and owns a list of Tasks. It is responsible for adding new tasks and reporting how many tasks it has.

- **Owner** — manages a list of Pets. It acts as the top-level container and can retrieve all tasks across every pet in one call.

- **Scheduler** — the "brain" of the system. It takes an Owner and is responsible for all scheduling intelligence: retrieving the full schedule, sorting tasks by time, filtering by completion status or pet name, detecting time conflicts, and handling recurring task logic.

**b. Design changes**

Yes, one relationship in the UML changed during the design review.

The initial diagram used a `1..*` (one-to-many) relationship between Owner and Pet, meaning an Owner had to have at least one Pet. I changed this to `0..*` (zero-to-many) because in real usage an Owner is created first and pets are added afterward. Requiring at least one pet at creation time would make the system harder to use and less realistic.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two main constraints: **scheduled time** and **completion status**.

- Scheduled time is the primary constraint — tasks are sorted chronologically so the owner sees what needs to happen first. A pet care schedule is inherently time-driven (morning walk before evening walk, feeding at a consistent time).
- Completion status is used for filtering — the owner can view only what still needs to be done, reducing noise from already-completed tasks.
- Frequency (daily/weekly/once) drives recurrence logic — daily tasks automatically reappear the next day when marked complete.

Priority was collected as an attribute but is not yet used as a sort key. Time ordering felt more natural for a daily schedule view; priority-based sorting is noted as a future enhancement.

**b. Tradeoffs**

The scheduler detects conflicts by **exact time match** (same HH:MM on the same date) rather than checking whether task durations overlap.

For example, a 30-minute walk at 07:30 and a 60-minute vet appointment at 07:30 are flagged as a conflict — but a 30-minute walk at 07:30 and a 60-minute appointment at 07:45 are not, even though they overlap in real time.

This is a reasonable tradeoff for this scenario because: pet care tasks are typically planned at fixed times rather than back-to-back, duration overlap detection would require more complex interval logic, and the simpler check still catches the most common mistake (accidentally scheduling two things at the exact same time).

In testing, the UI allowed adding the same task twice at the same time, which triggered a conflict warning as expected — confirming the detection logic works correctly. This also highlighted the need for a duplicate guard in the UI (planned for Phase 6).

---

## 3. AI Collaboration

**a. How you used AI**

I used an AI coding assistant (Claude Code) throughout all six phases of this project. The most effective uses were:

- **System design brainstorming** — I described the PawPal+ scenario and asked the AI to help identify the four main classes (Task, Pet, Owner, Scheduler) and their responsibilities before writing any code.
- **Scaffolding class stubs** — Once the UML was drafted, I asked the AI to generate Python class stubs using `@dataclass`, which gave me a clean starting structure to build on.
- **Debugging runtime errors** — When the CLI output crashed due to a Unicode encoding error on Windows (`✓` and `○` symbols), I described the error and the AI quickly identified the cause and suggested ASCII replacements (`[x]` / `[ ]`).
- **Generating test cases** — I asked the AI to draft tests for specific behaviors (sorting, conflict detection, recurrence) and explained each test before accepting it, rather than accepting the full suite blindly.

The most helpful types of prompts were specific and concrete: "Given this class design, what edge cases should I test for `handle_recurrence`?" worked much better than "write me tests."

**c. Using separate sessions for different phases**

I used separate AI chat sessions for different phases of the project — the main implementation (classes, backend logic, UI) was built across the core sessions, and the test suite (Phase 5) was written in a dedicated separate session focused only on testing `pawpal_system.py`.

This separation helped in two concrete ways. First, the testing session started with a clean context — the AI was not carrying assumptions from earlier design decisions, so it approached the test cases from the perspective of "what should this code guarantee?" rather than "what did we just write?" This surfaced edge cases (like `once` tasks not recurring, or `filter_by_pet` with no match returning an empty list) that might have been glossed over in a session already loaded with implementation context. Second, keeping testing separate enforced the CLI-first discipline: before opening the test session, all backend logic had already been verified to run correctly through `main.py`, so the tests were validating a known-working system rather than debugging and testing simultaneously. The separation made each session's purpose clear — build in one, verify in another — which is closer to how real software teams work.

**b. Judgment and verification**

When the AI generated the initial UML diagram, it used a `1..*` (one-to-many) relationship between Owner and Pet — meaning an owner must have at least one pet at creation time. I noticed this did not match real usage: in the app, an owner is created first and pets are added afterward. I changed the relationship to `0..*` (zero-to-many) and documented this as a design change in section 1b.

I verified the fix by tracing through the actual `Owner` dataclass — its `pets` field defaults to an empty list, which confirms that zero pets is a valid starting state. The AI's diagram was logically reasonable but did not account for the temporal order of object creation in the UI flow.

A second example came during UI testing. After the AI connected the "Add task" button to the backend, I tested the app in the browser and noticed several usability problems the AI did not anticipate:

- **Duplicate tasks**: clicking "Add task" twice silently added the same task twice at the same time, creating a false conflict. I directed the AI to add a duplicate guard that checks name + scheduled_time before adding.
- **Fields not clearing**: after adding a task or pet, all input fields stayed filled with the previous values. I directed the AI to use a session state counter as a widget key suffix, which forces Streamlit to re-render the inputs blank after each successful add.
- **Owner field stays editable**: the initial design kept the owner name as a plain text input forever. I directed the AI to change it so that once the owner name is confirmed, the field is replaced with a "Welcome, [Name]!" message and locked — the user can only change it via a separate "Change owner" button that resets the whole session.
- **No clear flow between owner → pet → task**: the initial UI had all three sections visible at once with pre-filled values. I directed the AI to restructure it into four numbered steps (Set owner → Add a pet → Add a task → Generate schedule), with each section only appearing once the previous step is complete.

These were all discovered by manually using the app — the AI produced code that was technically correct but was not usable without human testing and redirection.

A fifth example came when I directed the AI to highlight the actual conflicting task rows in orange directly in the task list, rather than only showing a generic warning message after generating the schedule. The AI's default was to display conflicts as a text warning at the bottom of the page — the user would have to mentally match the warning text to the correct task row. I directed the AI to detect conflict slots inline during task rendering and apply orange-colored text to the time and task name of any conflicting row, so the user can see at a glance which specific tasks clash. This required computing conflict slots before the render loop (comparing all pets' tasks by scheduled_time + due_date) rather than relying on the Scheduler's string output. The orange conflict message banner was also added as a secondary cue with an instruction to delete a conflicting task to resolve it.

A sixth example came when I noticed that the conflict warning had no resolution path — the app would show "Conflict at 09:00" but gave the user no way to act on it. The AI had not anticipated this gap. I directed the AI to add a `remove_task()` method to the `Pet` class and replace the static task table in the UI with interactive rows, each with a "Delete" button. On click, the task is removed from the pet's list and the UI refreshes, so the user can immediately re-check the schedule. The UML diagrams were also updated to document `remove_task()` as a first-class method. This shows that human oversight is needed not just at code review time, but when using the app as a real user would.

---

## 4. Testing and Verification

**a. What you tested**

We identified 5 core behaviors to verify in `pawpal_system.py`:

| # | Behavior | Method |
|---|----------|--------|
| 1 | Tasks sort chronologically by time | `sort_by_time()` |
| 2 | Two tasks at the same time/date trigger a conflict warning | `detect_conflicts()` |
| 3 | A `daily` task marked complete spawns a new task for tomorrow | `handle_recurrence()` |
| 4 | `filter_by_status(completed=False)` returns only incomplete tasks | `filter_by_status()` |
| 5 | `filter_by_pet("mochi")` matches `"Mochi"` (case-insensitive) | `filter_by_pet()` |

These behaviors are the core scheduling contract — if any one of them is broken, the app produces a wrong or misleading schedule for the owner.

**b. Confidence**

Edge cases identified and tested in `test_pawpal.py`:

- **Pet with no tasks** — `sort_by_time()` and `detect_conflicts()` should return empty lists, not crash
- **`once` task after `mark_complete`** — `handle_recurrence()` must NOT create a next occurrence
- **Two tasks at the exact same time** — conflict warning should appear with both task names
- **`weekly` task recurrence** — new task's `due_date` should be exactly 7 days later, not 1
- **Task already completed** — calling `mark_complete()` twice should stay `True`, not break

---

## 5. Reflection

**a. What went well**

The "CLI-first" workflow worked extremely well. Building and verifying all four classes in `pawpal_system.py` through `main.py` before touching the Streamlit UI meant that by the time I connected the backend to the frontend, I already knew the logic was correct. The test suite also caught real behavior early — for example, the `handle_recurrence` test confirmed that `once` tasks correctly do not create a next occurrence, which would have been easy to miss.

**b. What you would improve**

If I had another iteration, I would redesign the conflict detection to check for overlapping durations rather than just exact time matches. A 30-minute walk at 07:30 and a 60-minute vet appointment at 07:45 are a real conflict in practice, but the current system would not flag them.

The next planned enhancement is a **Group Walk** feature — a domain-specific scheduling rule I designed but did not yet implement. The idea: if two or more pets share the same species AND both have a task with "walk" in the name scheduled at the same time, that should NOT be flagged as a conflict. Instead the UI would highlight those rows in blue with a "🐾 Group Walk" badge, because multiple dogs (or multiple cats) going for a walk together at the same time is actually good planning, not a mistake. The current conflict detection is species-blind — it flags any two tasks at the same time slot as a problem, regardless of whether they could share the activity.

Implementing this would require a new `Scheduler.detect_group_walks()` method that groups tasks by time slot, checks whether all tasks in that slot share the same species and contain "walk", and returns those slots separately from true conflicts. The UI would then render three states instead of two: conflict (orange ⚠), group walk (blue 🐾), and normal. This feature is fully designed and ready to build — it was a human-directed idea that came from thinking about what a real pet owner would actually want, not from the code itself.

**c. Key takeaway**

The most important thing I learned is that AI is most useful when you stay in the role of the architect. When I gave the AI a specific, well-scoped question — "how should the Scheduler retrieve tasks from the Owner?" — the output was precise and immediately usable. When I accepted suggestions without reading them carefully, I introduced problems I had to fix later (like the `1..*` UML relationship or the Unicode symbols that crashed on Windows). The human's job is to define the structure and verify the output, not just accept it.
