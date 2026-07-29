"""
main.py
-------
CLI demo script for PawPal+. Verifies that backend logic in
pawpal_system.py works correctly before connecting it to the UI.

Run with:  python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import date

# ── Setup: one owner, two pets ────────────────────────────────────────────────
owner = Owner(name="Jordan")

mochi = Pet(name="Mochi", species="dog")
luna  = Pet(name="Luna",  species="cat")

# Tasks for Mochi
mochi.add_task(Task("Morning walk",    "07:30", 30, "high",   "daily"))
mochi.add_task(Task("Evening walk",    "18:00", 30, "high",   "daily"))
mochi.add_task(Task("Flea medication", "09:00", 5,  "medium", "weekly"))

# Tasks for Luna
luna.add_task(Task("Feeding",  "08:00", 10, "high",   "daily"))
luna.add_task(Task("Grooming", "11:00", 20, "medium", "weekly"))

# Intentional conflict: Luna's vet visit at 09:00 clashes with Mochi's flea meds
luna.add_task(Task("Vet appointment", "09:00", 60, "high", "once"))

owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler(owner)

# ── Section 1: Today's schedule sorted by time ────────────────────────────────
print(f"\n{'='*50}")
print(f"  Today's Schedule for {owner.name}")
print(f"  Date: {date.today()}")
print(f"{'='*50}")

for pet_name, task in scheduler.sort_by_time():
    print(f"  [{pet_name:<6}]  {task}")

# ── Section 2: Conflict detection ────────────────────────────────────────────
conflicts = scheduler.detect_conflicts()
print(f"\n--- Conflict Check ---")
if conflicts:
    print("  Conflicts detected:")
    for warning in conflicts:
        print(f"  ! {warning}")
else:
    print("  No scheduling conflicts.")

# ── Section 3: Recurring task demo ───────────────────────────────────────────
print(f"\n--- Recurring Task Demo ---")
morning_walk = mochi.tasks[0]
print(f"  Before: {morning_walk}")
print(f"  Marking '{morning_walk.name}' complete and scheduling next occurrence...")

morning_walk.mark_complete()
scheduler.handle_recurrence(morning_walk, mochi)

# The last task in mochi's list is now the next day's walk
next_walk = mochi.tasks[-1]
print(f"  After:  {morning_walk}")
print(f"  Next:   {next_walk} (due: {next_walk.due_date})")

# ── Section 4: Filter demo ───────────────────────────────────────────────────
print(f"\n--- Filter: Incomplete tasks only ---")
for pet_name, task in scheduler.filter_by_status(completed=False):
    print(f"  [{pet_name:<6}]  {task}")

print(f"\n--- Filter: Mochi's tasks only ---")
for pet_name, task in scheduler.filter_by_pet("Mochi"):
    print(f"  [{pet_name:<6}]  {task}")

print(f"\n{'='*50}\n")
