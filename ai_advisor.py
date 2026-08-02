"""
ai_advisor.py
-------------
RAG-powered AI care advisor for PawPal+.
Builds a context block from the owner's live schedule, calls Claude,
and logs every interaction to logs/advisor_log.txt.
"""

import os
from datetime import datetime
from pathlib import Path

from pawpal_system import Owner, Scheduler

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import anthropic
    _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
except ImportError:
    _client = None

SYSTEM_PROMPT = (
    "You are PawPal+, a friendly and practical pet care scheduling assistant. "
    "You have been given the owner's current pet care schedule above. "
    "Answer questions based only on the data provided — do not invent pets, tasks, or times "
    "that are not listed. Be concise. If there is a scheduling conflict, acknowledge it and "
    "suggest a concrete fix. If asked about something not in the schedule, say so clearly "
    "rather than guessing."
)

LOG_FILE = Path(__file__).parent / "logs" / "advisor_log.txt"


def build_context(owner: Owner) -> str:
    """Format the owner's full schedule into a readable text block for the prompt."""
    scheduler = Scheduler(owner)
    today = datetime.now().strftime("%A, %B %d, %Y")
    pet_summary = ", ".join(f"{p.name} ({p.species})" for p in owner.pets)
    lines = [
        f"Today's date: {today}",
        f"Owner: {owner.name}",
        f"Pets: {pet_summary}",
        "",
    ]

    for pet in owner.pets:
        lines.append(f"{pet.name}'s tasks:")
        if not pet.tasks:
            lines.append("  (no tasks scheduled)")
        else:
            for t in sorted(pet.tasks, key=lambda x: (str(x.due_date), x.scheduled_time)):
                lines.append(
                    f"  - {t.name} | {t.scheduled_time} | {t.duration_minutes} min"
                    f" | {t.priority} priority | {t.frequency} | due {t.due_date}"
                )
        lines.append("")

    conflicts = scheduler.detect_conflicts()
    overlaps  = scheduler.detect_overlap_conflicts()
    group_walks = scheduler.detect_group_walks()

    if conflicts or overlaps:
        lines.append("Scheduling conflicts detected:")
        for issue in conflicts + overlaps:
            lines.append(f"  ! {issue}")
        lines.append("")

    if group_walks:
        lines.append("Group walks (same-species pets at the same time — not a conflict):")
        for gw in group_walks:
            lines.append(f"  * {gw}")
        lines.append("")

    return "\n".join(lines)


def log_interaction(question: str, answer: str) -> None:
    """Append a timestamped Q&A pair to logs/advisor_log.txt."""
    LOG_FILE.parent.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] Q: {question}\n")
        f.write(f"[{ts}] A: {answer}\n")
        f.write("---\n")


def ask_advisor(owner: Owner, question: str) -> str:
    """
    Call Claude Haiku with the owner's schedule as context and return the response.
    Logs every interaction. Returns an error string (never raises) on failure.
    """
    if _client is None:
        return "AI advisor unavailable — run: pip install anthropic"

    if not os.environ.get("ANTHROPIC_API_KEY", ""):
        return (
            "ANTHROPIC_API_KEY is not set. "
            "Copy .env.example to .env and add your key, then restart the app."
        )

    context = build_context(owner)
    user_message = f"{context}\n\nQuestion: {question}"

    try:
        response = _client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        answer = response.content[0].text
    except Exception as exc:
        answer = f"Advisor error — {exc}"
        log_interaction(question, f"ERROR: {exc}")
        return answer

    log_interaction(question, answer)
    return answer
