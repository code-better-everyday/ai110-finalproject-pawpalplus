"""
eval_advisor.py
---------------
Test harness for the PawPal+ AI care advisor.
Runs the advisor on predefined inputs and checks responses against
expected keywords. Prints a pass/fail summary.

Usage:
    python eval_advisor.py
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from pawpal_system import Owner, Pet, Task, Scheduler
from ai_advisor import ask_advisor

# ── Load owner profile from saved data ───────────────────────────────────────

def load_owner() -> Owner:
    data = json.loads(Path("data/users.json").read_text(encoding="utf-8"))
    user_data = data["users"][0]
    owner = Owner(user_data["name"])

    def due(freq):
        today = date.today()
        if freq == "weekly":
            days = (5 - today.weekday()) % 7
            return today + timedelta(days=days if days else 7)
        if freq == "once":
            current = today; added = 0
            while added < 3:
                current += timedelta(days=1)
                if current.weekday() < 5: added += 1
            return current
        return today

    for p in user_data["pets"]:
        pet = Pet(p["name"], p["species"])
        for t in p.get("tasks", []):
            freq = t.get("frequency", "daily")
            pet.add_task(Task(
                t["name"], t["scheduled_time"], t["duration_minutes"],
                t["priority"], freq, due_date=due(freq)
            ))
        owner.add_pet(pet)
    return owner

# ── Test cases: (question, expected_keywords, description) ───────────────────

TEST_CASES = [
    (
        "What is most urgent for my dogs today?",
        ["chintu", "pintu", "walk", "feeding", "high"],
        "Identifies high-priority dog tasks with pet names",
    ),
    (
        "Can Chintu and Pintu do their morning walk together?",
        ["together", "07:00", "group"],
        "Recognises group walk opportunity at 07:00",
    ),
    (
        "Are there any scheduling conflicts I should fix?",
        ["08:00", "feeding", "pintu", "chinni"],
        "Identifies the 08:00 feeding conflict with pet names",
    ),
    (
        "What tasks are scheduled for Chinni today?",
        ["chinni", "feeding", "litter"],
        "Returns Chinni's specific tasks",
    ),
    (
        "Which pet has a vet appointment coming up?",
        ["vet", "pintu", "chinni"],
        "Finds upcoming vet appointments across pets",
    ),
]

# ── Runner ────────────────────────────────────────────────────────────────────

def run_eval():
    print("=" * 60)
    print("PawPal+ AI Advisor — Evaluation Harness")
    print("=" * 60)

    try:
        owner = load_owner()
    except Exception as e:
        print(f"ERROR loading profile: {e}")
        sys.exit(1)

    print(f"Profile loaded: {owner.name} — {len(owner.pets)} pets, "
          f"{sum(p.task_count() for p in owner.pets)} tasks\n")

    passed = 0
    results = []

    for i, (question, keywords, description) in enumerate(TEST_CASES, 1):
        print(f"Test {i}: {description}")
        print(f"  Q: {question}")

        answer = ask_advisor(owner, question)

        if answer.startswith("ANTHROPIC_API_KEY") or answer.startswith("AI advisor") or answer.startswith("Advisor error"):
            print(f"  ✗ SKIP — API error: {answer[:60]}")
            results.append((description, "SKIP", [], answer[:60]))
            continue

        answer_lower = answer.lower()
        matched   = [kw for kw in keywords if kw.lower() in answer_lower]
        missing   = [kw for kw in keywords if kw.lower() not in answer_lower]
        success   = len(missing) == 0

        if success:
            passed += 1
            status = "PASS"
        else:
            status = "FAIL"

        print(f"  A: {answer[:120].strip()}{'...' if len(answer) > 120 else ''}")
        print(f"  {status} — keywords matched: {matched}"
              + (f" | missing: {missing}" if missing else ""))
        print()
        results.append((description, status, matched, missing))

    # ── Summary ───────────────────────────────────────────────────────────────
    total  = len(TEST_CASES)
    skipped = sum(1 for _, s, _, _ in results if s == "SKIP")
    ran    = total - skipped

    print("=" * 60)
    print(f"Results: {passed}/{ran} passed"
          + (f"  ({skipped} skipped — API unavailable)" if skipped else ""))
    print()
    for desc, status, matched, missing in results:
        icon = "✓" if status == "PASS" else ("–" if status == "SKIP" else "✗")
        print(f"  {icon}  {desc}")
    print("=" * 60)

    if passed == ran and ran > 0:
        print("All tests passed — advisor is grounded in schedule data.")
    elif passed >= ran * 0.6:
        print("Most tests passed — advisor responses are broadly correct.")
    else:
        print("Several tests failed — review context or keyword expectations.")

if __name__ == "__main__":
    run_eval()
