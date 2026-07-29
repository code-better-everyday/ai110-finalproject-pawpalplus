# RAG Advisor Design — PawPal+

## What RAG means here

"RAG" (Retrieval-Augmented Generation) in PawPal+ means: before asking Claude a question, we inject the owner's **actual schedule data** as context. Claude's response is grounded in real data — the owner's name, pets, tasks, times, priorities, and any detected conflicts — rather than generic pet care advice.

This is "retrieval" in the lightweight sense: instead of a vector database, we retrieve directly from the in-memory `Owner` object that Streamlit holds in session state.

---

## Context Building (`build_context`)

The function formats the current Owner/Pet/Task state into a readable text block:

```
Owner: Jordan
Pets: Mochi (dog), Luna (cat)

Mochi's tasks:
  - Morning walk | 07:30 | 30 min | high priority | daily
  - Evening walk  | 18:00 | 30 min | high priority | daily
  - Flea meds     | 09:00 | 5 min  | medium priority | weekly

Luna's tasks:
  - Feeding        | 08:00 | 10 min | high priority | daily
  - Vet appointment| 09:00 | 60 min | high priority | once   ← CONFLICT

Conflicts detected:
  ! Conflict at 09:00 on 2026-07-28: 'Flea meds' and 'Vet appointment'
```

This block is prepended to every user question as part of the user message.

---

## System Prompt

```
You are PawPal+, a friendly and practical pet care scheduling assistant.
You have been given the owner's current pet care schedule above.
Answer questions based only on the data provided — do not make up pets, tasks, or times that aren't listed.
Be concise and helpful. If there is a scheduling conflict, acknowledge it and suggest a fix.
If asked about something not in the schedule, say so rather than guessing.
```

---

## API Call Flow

```python
def ask_advisor(owner: Owner, question: str) -> str:
    context = build_context(owner)
    user_message = f"{context}\n\nQuestion: {question}"
    
    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",   # fast + cheap for a scheduling assistant
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )
    answer = response.content[0].text
    log_interaction(question, answer)
    return answer
```

**Model choice:** `claude-haiku-4-5-20251001` — fast responses, low cost, sufficient for schedule Q&A.  
**max_tokens:** 512 — enough for a helpful answer, prevents runaway output.

---

## Logging

Every call appends to `logs/advisor_log.txt`:

```
[2026-07-28 20:15:32] Q: What's most urgent today?
[2026-07-28 20:15:33] A: Mochi's Morning walk at 07:30 is your highest priority task...
---
```

The `logs/` directory is created automatically if it doesn't exist.

---

## Error Handling / Guardrails

- If `ANTHROPIC_API_KEY` is not set → show a Streamlit warning, do not crash
- If the API call fails (network, rate limit) → catch exception, show user-friendly error, log the failure
- If owner has no pets or no tasks → context says so; Claude responds accordingly
- `max_tokens=512` caps response length

---

## Sample Interactions (for README)

**Q: "What's most urgent today?"**
```
Based on your schedule, Mochi's Morning walk at 07:30 is your first high-priority task.
Luna's Feeding at 08:00 is also high priority. I also notice a scheduling conflict at 09:00
between Mochi's Flea meds and Luna's Vet appointment — you'll need to resolve that before
generating today's plan.
```

**Q: "Is there anything I can combine to save time?"**
```
If Mochi and another dog were both scheduled for walks at the same time, you could do a
group walk. Currently, Mochi's Morning walk (07:30) and Evening walk (18:00) don't overlap
with any of Luna's tasks, so there's no obvious combination — but you could reschedule Luna's
Feeding to 07:30 to pair it with the walk if that works for your morning routine.
```

**Q: "Help me fix the 09:00 conflict"**
```
You have a conflict at 09:00 on 2026-07-28 between Mochi's 'Flea meds' (5 min, weekly) and
Luna's 'Vet appointment' (60 min, once). Since the vet appointment is a one-time, high-priority
event, I'd suggest moving Mochi's Flea meds to 10:30 or later — after the vet visit wraps up.
Use the Delete button next to the Flea meds task, then re-add it at the new time.
```
