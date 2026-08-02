"""
app.py
------
Streamlit UI for PawPal+. Connects the frontend inputs to the
backend logic defined in pawpal_system.py.

Run with:  streamlit run app.py
"""

import json
import streamlit as st
from datetime import date, timedelta
from pathlib import Path
from pawpal_system import Owner, Pet, Task, Scheduler
from ai_advisor import ask_advisor

DATA_FILE = Path(__file__).parent / "data" / "users.json"


def load_all_users() -> list:
    """Return list of user dicts from data/users.json, or [] if missing/corrupt."""
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8")).get("users", [])
    except (json.JSONDecodeError, KeyError):
        return []


def species_emoji(species: str) -> str:
    return {"dog": "🐕", "cat": "🐱", "rabbit": "🐇", "bird": "🦜", "fish": "🐠", "hamster": "🐹"}.get(species.lower(), "🐾")


def task_emoji(name: str) -> str:
    n = name.lower()
    if "walk" in n:   return "🚶"
    if "feed" in n:   return "🍽️"
    if "med" in n:    return "💊"
    if "vet" in n:    return "🏥"
    if "groom" in n:  return "✂️"
    if "play" in n:   return "🎾"
    return "📋"


def next_saturday() -> date:
    today = date.today()
    days_ahead = (5 - today.weekday()) % 7
    return today + timedelta(days=days_ahead if days_ahead else 7)


def add_business_days(start: date, n: int) -> date:
    current = start
    added = 0
    while added < n:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Mon–Fri only
            added += 1
    return current


def task_due_date(frequency: str) -> date:
    if frequency == "weekly":
        return next_saturday()
    if frequency == "once":
        return add_business_days(date.today(), 3)
    return date.today()


def generate_schedule_html(owner, mode: str = "daily") -> str:
    today = date.today()
    scheduler = Scheduler(owner)
    priority_order = {"high": 0, "medium": 1, "low": 2}

    if mode == "daily":
        tasks = [(p, t) for p, t in scheduler.sort_by_priority_then_time()
                 if t.due_date == today]
        title = f"Daily Schedule — {owner.name} — {today.strftime('%A, %B %d, %Y')}"
        headers = ["Time", "Pet", "Task", "Duration (min)", "Priority", "Frequency", "Status"]
        rows = []
        for p_name, t in tasks:
            pet_obj = next((p for p in owner.pets if p.name == p_name), None)
            p_emoji = species_emoji(pet_obj.species) if pet_obj else "🐾"
            status = "✅ Done" if t.completed else "⏳ Pending"
            rows.append(("completed" if t.completed else "", [
                t.scheduled_time,
                f"{p_emoji} {p_name}",
                f"{task_emoji(t.name)} {t.name}",
                str(t.duration_minutes),
                t.priority,
                t.frequency,
                status,
            ]))
    else:
        tasks = sorted(
            scheduler.get_schedule(),
            key=lambda x: (x[1].due_date, priority_order.get(x[1].priority, 99), x[1].scheduled_time),
        )
        title = (
            f"Weekly Schedule — {owner.name} — "
            f"{today.strftime('%B %d')} → {next_saturday().strftime('%B %d, %Y')}"
        )
        headers = ["Date", "Time", "Pet", "Task", "Duration (min)", "Priority", "Frequency", "Status"]
        rows = []
        for p_name, t in tasks:
            pet_obj = next((p for p in owner.pets if p.name == p_name), None)
            p_emoji = species_emoji(pet_obj.species) if pet_obj else "🐾"
            due_label = t.due_date.strftime("%a %b %d")
            if t.due_date == today:
                due_label += " · today"
            status = "✅ Done" if t.completed else "⏳ Pending"
            rows.append(("completed" if t.completed else "", [
                due_label,
                t.scheduled_time,
                f"{p_emoji} {p_name}",
                f"{task_emoji(t.name)} {t.name}",
                str(t.duration_minutes),
                t.priority,
                t.frequency,
                status,
            ]))

    header_cells = "".join(f"<th>{h}</th>" for h in headers)
    body_rows = "".join(
        f'<tr class="{cls}">{"".join(f"<td>{c}</td>" for c in cells)}</tr>'
        for cls, cells in rows
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
  body{{font-family:Arial,sans-serif;font-size:13px;margin:32px;color:#222}}
  h1{{font-size:18px;margin-bottom:18px}}
  table{{border-collapse:collapse;width:100%}}
  th{{background:#2c3e50;color:#fff;padding:9px 13px;text-align:left;font-size:12px;letter-spacing:.4px}}
  td{{padding:7px 13px;border-bottom:1px solid #e0e0e0}}
  tr:nth-child(even) td{{background:#fafafa}}
  tr.completed td{{color:#bbb;text-decoration:line-through}}
  @media print{{body{{margin:18px}}tr:nth-child(even) td{{background:none}}}}
</style>
</head>
<body>
<h1>{title}</h1>
<table>
<thead><tr>{header_cells}</tr></thead>
<tbody>{body_rows}</tbody>
</table>
</body>
</html>"""


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

st.markdown(
    """
    <div style="text-align:center;padding:16px 0 8px 0;">
        <div style="font-size:2.8rem;letter-spacing:10px;">🐕 🐱 🐇 🦜 🐹 🐠</div>
        <p style="font-size:1.05rem;color:#666;margin-top:6px;">
            Your all-in-one pet care planner — schedules, reminders, and happy pets.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ── Step 1: Owner Setup ────────────────────────────────────────────────────────
st.subheader("Step 1: Hey there, Pet Parent! Let's keep your furry family happy and on schedule.")

if "owner" not in st.session_state:
    st.session_state.owner = None

if st.session_state.owner is None:
    # ── Saved profiles ─────────────────────────────────────────────────────────
    saved_users = load_all_users()
    if saved_users:
        st.markdown("**Welcome back! We found saved profiles:**")
        for user_data in saved_users:
            pet_summary = "  •  ".join(
                f"{species_emoji(p['species'])} {p['name']} ({p['species']})"
                for p in user_data["pets"]
            )
            st.info(f"**{user_data['name']}** — {pet_summary}")
            if st.button(f"Load {user_data['name']}'s data", key=f"load_{user_data['name']}"):
                restored_owner = Owner(name=user_data["name"])
                for p in user_data["pets"]:
                    pet = Pet(name=p["name"], species=p["species"])
                    for t in p.get("tasks", []):
                        freq = t["frequency"]
                        pet.add_task(Task(
                            name=t["name"],
                            scheduled_time=t["scheduled_time"],
                            duration_minutes=t["duration_minutes"],
                            priority=t["priority"],
                            frequency=freq,
                            due_date=task_due_date(freq),
                        ))
                    restored_owner.add_pet(pet)
                st.session_state.owner = restored_owner
                st.rerun()
        st.markdown("— or start fresh —")

    # ── Manual entry ───────────────────────────────────────────────────────────
    owner_name = st.text_input("Your name", value="", placeholder="Enter your name")
    if st.button("Set owner"):
        if not owner_name.strip():
            st.warning("Please enter your name first.")
        else:
            st.session_state.owner = Owner(name=owner_name.strip())
            st.rerun()
else:
    # Owner confirmed — lock the field and greet them
    st.success(f"Welcome, {st.session_state.owner.name}! Let's plan care for your pet.")
    if st.button("Change owner"):
        # Reset everything when owner changes
        for key in ["owner", "pet_count", "add_count", "show_daily", "show_weekly"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

st.divider()

# Only show the rest of the app once an owner is set
if st.session_state.owner is None:
    st.info("Enter your name above to get started.")
    st.stop()

owner = st.session_state.owner

# ── Step 2: Add a Pet ──────────────────────────────────────────────────────────
_pet_label = "Step 2: Add a Pet" + (f" — {len(owner.pets)} added" if owner.pets else "")
with st.expander(_pet_label, expanded=not bool(owner.pets)):
    if "pet_count" not in st.session_state:
        st.session_state.pet_count = 0

    pk = st.session_state.pet_count  # key suffix to reset pet fields after add

    if owner.pets:
        st.markdown("**Your pets:**")
        for p in owner.pets:
            st.write(f"  {species_emoji(p.species)} {p.name} ({p.species})")
        st.markdown("---")

    pet_name = st.text_input(
        "Pet name", value="", placeholder="Enter your pet's name",
        key=f"pet_name_{pk}"
    )
    species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "fish", "hamster", "other"], key=f"species_{pk}")

    if st.button("Add pet"):
        if not pet_name.strip():
            st.warning("Please enter a pet name.")
        else:
            new_pet = Pet(name=pet_name.strip(), species=species)
            owner.add_pet(new_pet)
            st.session_state.pet_count += 1  # resets pet name field
            st.success(f"Added {pet_name}! Add a new pet — yay! 🐾")
            st.rerun()

    if not owner.pets:
        st.info("No pets yet. Add your first pet above.")

if not owner.pets:
    st.stop()

st.divider()

# ── Step 3: Add Tasks ──────────────────────────────────────────────────────────
_total_tasks   = sum(p.task_count() for p in owner.pets)
_pending_total = sum(1 for p in owner.pets for t in p.tasks if not t.completed)
_task_label = f"Step 3: Add a Task — {_pending_total} pending / {_total_tasks} total"
with st.expander(_task_label, expanded=False):
    pet_names  = [p.name for p in owner.pets]
    chosen_pet = st.selectbox("Assign to pet", pet_names)
    pet        = next(p for p in owner.pets if p.name == chosen_pet)

    if "add_count" not in st.session_state:
        st.session_state.add_count = 0

    k = st.session_state.add_count

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title     = st.text_input("Task name",    value="", placeholder="e.g. Morning walk...", key=f"title_{k}")
    with col2:
        scheduled_time = st.text_input("Time (HH:MM)", value="", placeholder="e.g. 08:00",          key=f"time_{k}")
    with col3:
        duration       = st.number_input("Duration (min)", min_value=1, max_value=240, value=20,     key=f"dur_{k}")
    with col4:
        priority       = st.selectbox("Priority", ["low", "medium", "high"], index=2,               key=f"pri_{k}")

    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"], key=f"freq_{k}")

    if st.button("Add task"):
        if not task_title.strip():
            st.warning("Please enter a task name.")
        elif not scheduled_time.strip():
            st.warning("Please enter a scheduled time (HH:MM).")
        else:
            duplicate = [t for t in pet.tasks
                         if t.name.lower() == task_title.strip().lower()
                         and t.scheduled_time == scheduled_time.strip()]
            if duplicate:
                st.warning(f"'{task_title}' at {scheduled_time} already exists for {pet.name}. Duplicate not added.")
            else:
                pet.add_task(Task(
                    name=task_title.strip(),
                    scheduled_time=scheduled_time.strip(),
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=frequency,
                    due_date=task_due_date(frequency),
                ))
                st.session_state.add_count += 1
                st.success(f"Added '{task_title}' to {pet.name}'s schedule!")
                st.rerun()

    if pet.task_count() > 0:
        _pending_pet = sum(1 for t in pet.tasks if not t.completed)
        st.markdown(f"**{pet.name}'s tasks — {_pending_pet} pending / {pet.task_count()} total:**")
        _sched = Scheduler(owner)

        seen_slots: dict = {}
        conflict_slots: set = set()
        for p in owner.pets:
            for task in p.tasks:
                slot_key = (task.scheduled_time, str(task.due_date))
                if slot_key in seen_slots:
                    conflict_slots.add(slot_key)
                else:
                    seen_slots[slot_key] = task.name

        walk_slots: dict = {}
        for p in owner.pets:
            for task in p.tasks:
                if "walk" in task.name.lower():
                    key = (task.scheduled_time, str(task.due_date))
                    walk_slots.setdefault(key, []).append((p.name, p.species))
        group_walk_keys: set = {
            k for k, entries in walk_slots.items()
            if len(entries) >= 2 and len({e[1] for e in entries}) == 1
        }

        for i, t in enumerate(pet.tasks):
            slot_key = (t.scheduled_time, str(t.due_date))
            is_group_walk = slot_key in group_walk_keys
            is_conflict   = slot_key in conflict_slots and not is_group_walk
            edit_key = f"editing_{pet.name}_{i}_{t.name}"

            if st.session_state.get(edit_key):
                # ── Edit mode ────────────────────────────────────────────────
                ec1, ec2, ec3, ec4, ec5 = st.columns([1, 2.5, 1, 0.7, 0.7])
                new_time = ec1.text_input("Time", value=t.scheduled_time, key=f"et_{edit_key}", label_visibility="collapsed")
                ec2.markdown(f"✏️ **{task_emoji(t.name)} {t.name}**")
                new_dur  = ec3.number_input("Min", value=t.duration_minutes, min_value=1, max_value=480, key=f"ed_{edit_key}", label_visibility="collapsed")
                if ec4.button("💾", key=f"save_{edit_key}", help="Save changes"):
                    import re
                    if not re.match(r"^\d{2}:\d{2}$", new_time.strip()):
                        st.warning("Time must be HH:MM format (e.g. 07:45)")
                    else:
                        t.scheduled_time = new_time.strip()
                        t.duration_minutes = int(new_dur)
                        st.session_state[edit_key] = False
                        st.rerun()
                if ec5.button("✕", key=f"cancel_{edit_key}", help="Cancel"):
                    st.session_state[edit_key] = False
                    st.rerun()
            elif t.completed:
                # ── Completed row ─────────────────────────────────────────────
                col_time, col_task, col_dur, col_pri, col_freq, col_done, col_del = st.columns([1, 2, 1, 1, 1, 1, 1])
                col_time.markdown(f'<span style="color:#bbb;text-decoration:line-through">{t.scheduled_time}</span>', unsafe_allow_html=True)
                col_task.markdown(f'<span style="color:#bbb;text-decoration:line-through">{task_emoji(t.name)} {t.name}</span>', unsafe_allow_html=True)
                col_dur.markdown(f'<span style="color:#bbb">{t.duration_minutes} min</span>', unsafe_allow_html=True)
                col_pri.markdown(f'<span style="color:#bbb">{t.priority}</span>', unsafe_allow_html=True)
                col_freq.markdown(f'<span style="color:#bbb">{t.frequency}</span>', unsafe_allow_html=True)
                col_done.write("✅")
                if col_del.button("🗑", key=f"del_{i}_{t.name}_{t.scheduled_time}", help="Delete task"):
                    pet.remove_task(t.name, t.scheduled_time)
                    st.rerun()
            else:
                # ── Normal / conflict / group-walk row ────────────────────────
                col_time, col_task, col_dur, col_pri, col_freq, col_edit, col_done, col_del = st.columns([1, 2, 1, 1, 1, 0.7, 0.7, 0.7])
                if is_group_walk:
                    col_time.markdown(f'<span style="color:#1565C0;font-weight:bold">{t.scheduled_time} 🐾</span>', unsafe_allow_html=True)
                    col_task.markdown(f'<span style="color:#1565C0;font-weight:bold">{task_emoji(t.name)} {t.name}</span>', unsafe_allow_html=True)
                elif is_conflict:
                    col_time.markdown(f'<span style="color:#FF6B00;font-weight:bold">{t.scheduled_time} ⚠</span>', unsafe_allow_html=True)
                    col_task.markdown(f'<span style="color:#FF6B00;font-weight:bold">{task_emoji(t.name)} {t.name}</span>', unsafe_allow_html=True)
                else:
                    col_time.write(t.scheduled_time)
                    col_task.write(f"{task_emoji(t.name)} {t.name}")
                col_dur.write(f"{t.duration_minutes} min")
                col_pri.write(t.priority)
                col_freq.write(t.frequency)
                if col_edit.button("✏️", key=f"edit_{i}_{t.name}_{t.scheduled_time}", help="Edit time / duration"):
                    st.session_state[edit_key] = True
                    st.rerun()
                if col_done.button("✅", key=f"done_{i}_{t.name}_{t.scheduled_time}", help="Mark as done"):
                    t.mark_complete()
                    _sched.handle_recurrence(t, pet)
                    st.rerun()
                if col_del.button("🗑", key=f"del_{i}_{t.name}_{t.scheduled_time}", help="Delete task"):
                    pet.remove_task(t.name, t.scheduled_time)
                    st.rerun()
    else:
        st.info(f"No tasks yet for {pet.name}. Add one above.")

st.divider()

# ── Step 4: Generate Daily Schedule ──────────────────────────────────────────
st.subheader("Step 4: Generate Daily Schedule")

if "show_daily" not in st.session_state:
    st.session_state.show_daily = False

_col_gen4, _col_dl4 = st.columns([1, 2])
with _col_gen4:
    if st.button("Generate daily schedule"):
        st.session_state.show_daily = True
with _col_dl4:
    if st.session_state.show_daily and owner.get_all_tasks():
        st.download_button(
            "📄 Download daily schedule (open → Ctrl+P → PDF)",
            data=generate_schedule_html(owner, "daily").encode("utf-8"),
            file_name=f"daily_schedule_{date.today()}.html",
            mime="text/html",
        )

if st.session_state.show_daily:
    all_tasks = owner.get_all_tasks()
    if not all_tasks:
        st.warning("No tasks added yet. Add at least one task first.")
    else:
        scheduler = Scheduler(owner)
        today = date.today()
        daily_tasks = [(p, t) for p, t in scheduler.sort_by_priority_then_time()
                       if t.due_date == today]
        today_label = today.strftime("%A, %B %d, %Y")
        st.markdown(f"**Daily Schedule for {owner.name} — {today_label}:**")

        if not daily_tasks:
            st.info("No tasks scheduled for today.")
        else:
            seen_slots: dict = {}
            conflict_slots: set = set()
            for p_name, task in daily_tasks:
                slot_key = (task.scheduled_time, str(task.due_date))
                if slot_key in seen_slots:
                    conflict_slots.add(slot_key)
                else:
                    seen_slots[slot_key] = task.name

            walk_slots: dict = {}
            for p in owner.pets:
                for task in p.tasks:
                    if "walk" in task.name.lower() and task.due_date == today:
                        key = (task.scheduled_time, str(task.due_date))
                        walk_slots.setdefault(key, []).append((p.name, p.species))
            group_walk_keys: set = {
                k for k, entries in walk_slots.items()
                if len(entries) >= 2 and len({e[1] for e in entries}) == 1
            }

            pets_today = list(dict.fromkeys(p for p, _ in daily_tasks))
            for pet_name in pets_today:
                pet_obj = next((p for p in owner.pets if p.name == pet_name), None)
                pet_tasks_today = [t for p, t in daily_tasks if p == pet_name]
                done_count = sum(1 for t in pet_tasks_today if t.completed)
                p_emoji = species_emoji(pet_obj.species) if pet_obj else "🐾"
                st.markdown(f"**{p_emoji} {pet_name} — {done_count}/{len(pet_tasks_today)} done today**")

                h1, h2, h3, h4, h5, h6 = st.columns([1, 2.5, 0.8, 1, 1, 0.7])
                h1.markdown("**Time**"); h2.markdown("**Task**"); h3.markdown("**Min**")
                h4.markdown("**Priority**"); h5.markdown("**Freq**"); h6.markdown("**Done**")

                for i, t in enumerate(pet_tasks_today):
                    slot_key = (t.scheduled_time, str(t.due_date))
                    is_group_walk = slot_key in group_walk_keys
                    is_conflict   = slot_key in conflict_slots and not is_group_walk
                    c1, c2, c3, c4, c5, c6 = st.columns([1, 2.5, 0.8, 1, 1, 0.7])

                    if t.completed:
                        c1.markdown(f'<span style="color:#bbb;text-decoration:line-through">{t.scheduled_time}</span>', unsafe_allow_html=True)
                        c2.markdown(f'<span style="color:#bbb;text-decoration:line-through">{task_emoji(t.name)} {t.name}</span>', unsafe_allow_html=True)
                        c3.markdown(f'<span style="color:#bbb">{t.duration_minutes}</span>', unsafe_allow_html=True)
                        c4.markdown(f'<span style="color:#bbb">{t.priority}</span>', unsafe_allow_html=True)
                        c5.markdown(f'<span style="color:#bbb">{t.frequency}</span>', unsafe_allow_html=True)
                        c6.write("✅")
                    else:
                        if is_group_walk:
                            c1.markdown(f'<span style="color:#1565C0;font-weight:bold">{t.scheduled_time} 🐾</span>', unsafe_allow_html=True)
                            c2.markdown(f'<span style="color:#1565C0;font-weight:bold">{task_emoji(t.name)} {t.name}</span>', unsafe_allow_html=True)
                        elif is_conflict:
                            c1.markdown(f'<span style="color:#FF6B00;font-weight:bold">{t.scheduled_time} ⚠</span>', unsafe_allow_html=True)
                            c2.markdown(f'<span style="color:#FF6B00;font-weight:bold">{task_emoji(t.name)} {t.name}</span>', unsafe_allow_html=True)
                        else:
                            c1.write(t.scheduled_time)
                            c2.write(f"{task_emoji(t.name)} {t.name}")
                        c3.write(t.duration_minutes)
                        c4.write(t.priority)
                        c5.write(t.frequency)
                        if c6.button("✅", key=f"d4_{pet_name}_{i}_{t.scheduled_time}", help="Mark done"):
                            t.mark_complete()
                            scheduler.handle_recurrence(t, pet_obj)
                            st.rerun()

                st.markdown("---")

            today_str = str(today)
            group_walks = [g for g in scheduler.detect_group_walks() if today_str in g]
            real_conflicts = [
                c for c in scheduler.detect_conflicts()
                if today_str in c
                and not any(f"at {t}" in c and f"on {d}" in c for t, d in group_walk_keys)
            ]
            overlap_warnings = [w for w in scheduler.detect_overlap_conflicts() if today_str in w]

            if group_walks:
                gw_lines = "".join(f"<li>{g}</li>" for g in group_walks)
                st.markdown(
                    f"""
                    <div style="background-color:#E3F2FD;color:#1565C0;padding:12px 16px;
                                border-radius:8px;margin-top:8px;">
                        <strong>🐾 Group walks — same-species pets walking together (not a conflict):</strong>
                        <ul style="margin:6px 0 0 0;">{gw_lines}</ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if real_conflicts or overlap_warnings:
                warn_lines = "".join(f"<li>{w}</li>" for w in real_conflicts + overlap_warnings)
                st.markdown(
                    f"""
                    <div style="background-color:#FF6B00;color:white;padding:12px 16px;
                                border-radius:8px;margin-top:8px;">
                        <strong>⚠ Scheduling conflicts detected — edit the time or delete a task below to resolve:</strong>
                        <ul style="margin:6px 0 0 0;">{warn_lines}</ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            elif not group_walks:
                st.success("No scheduling conflicts today.")
            else:
                st.success("No scheduling conflicts — group walks are cooperative, not conflicts.")

st.divider()

# ── Step 5: Generate Weekly Schedule ─────────────────────────────────────────
st.subheader("Step 5: Generate Weekly Schedule")

if "show_weekly" not in st.session_state:
    st.session_state.show_weekly = False

_col_gen5, _col_dl5 = st.columns([1, 2])
with _col_gen5:
    if st.button("Generate weekly schedule"):
        st.session_state.show_weekly = True
with _col_dl5:
    if st.session_state.show_weekly and owner.get_all_tasks():
        st.download_button(
            "📄 Download weekly schedule (open → Ctrl+P → PDF)",
            data=generate_schedule_html(owner, "weekly").encode("utf-8"),
            file_name=f"weekly_schedule_{date.today()}.html",
            mime="text/html",
        )

if st.session_state.show_weekly:
    all_tasks = owner.get_all_tasks()
    if not all_tasks:
        st.warning("No tasks added yet. Add at least one task first.")
    else:
        scheduler = Scheduler(owner)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        weekly_tasks = sorted(
            scheduler.get_schedule(),
            key=lambda x: (x[1].due_date, priority_order.get(x[1].priority, 99), x[1].scheduled_time),
        )
        week_of = date.today().strftime("%B %d, %Y")
        sat_label = next_saturday().strftime("%B %d")
        st.markdown(f"**Weekly Schedule for {owner.name} — {week_of} → {sat_label}:**")

        seen_slots: dict = {}
        conflict_slots: set = set()
        for p_name, task in weekly_tasks:
            slot_key = (task.scheduled_time, str(task.due_date))
            if slot_key in seen_slots:
                conflict_slots.add(slot_key)
            else:
                seen_slots[slot_key] = task.name

        walk_slots: dict = {}
        for p in owner.pets:
            for task in p.tasks:
                if "walk" in task.name.lower():
                    key = (task.scheduled_time, str(task.due_date))
                    walk_slots.setdefault(key, []).append((p.name, p.species))
        group_walk_keys: set = {
            k for k, entries in walk_slots.items()
            if len(entries) >= 2 and len({e[1] for e in entries}) == 1
        }

        pets_weekly = list(dict.fromkeys(p for p, _ in weekly_tasks))
        for pet_name in pets_weekly:
            pet_obj = next((p for p in owner.pets if p.name == pet_name), None)
            pet_tasks_week = [t for p, t in weekly_tasks if p == pet_name]
            done_count = sum(1 for t in pet_tasks_week if t.completed)
            p_emoji = species_emoji(pet_obj.species) if pet_obj else "🐾"
            st.markdown(f"**{p_emoji} {pet_name} — {done_count}/{len(pet_tasks_week)} done this week**")

            h1, h2, h3, h4, h5, h6, h7 = st.columns([1.2, 1, 2, 0.8, 1, 1, 0.7])
            h1.markdown("**Date**"); h2.markdown("**Time**"); h3.markdown("**Task**")
            h4.markdown("**Min**"); h5.markdown("**Priority**"); h6.markdown("**Freq**"); h7.markdown("**Done**")

            for i, t in enumerate(pet_tasks_week):
                slot_key = (t.scheduled_time, str(t.due_date))
                is_group_walk = slot_key in group_walk_keys
                is_conflict   = slot_key in conflict_slots and not is_group_walk
                c1, c2, c3, c4, c5, c6, c7 = st.columns([1.2, 1, 2, 0.8, 1, 1, 0.7])

                due_label = t.due_date.strftime("%a %b %d")
                if t.due_date == date.today():
                    due_label += " · today"

                if t.completed:
                    c1.markdown(f'<span style="color:#bbb;text-decoration:line-through">{due_label}</span>', unsafe_allow_html=True)
                    c2.markdown(f'<span style="color:#bbb;text-decoration:line-through">{t.scheduled_time}</span>', unsafe_allow_html=True)
                    c3.markdown(f'<span style="color:#bbb;text-decoration:line-through">{task_emoji(t.name)} {t.name}</span>', unsafe_allow_html=True)
                    c4.markdown(f'<span style="color:#bbb">{t.duration_minutes}</span>', unsafe_allow_html=True)
                    c5.markdown(f'<span style="color:#bbb">{t.priority}</span>', unsafe_allow_html=True)
                    c6.markdown(f'<span style="color:#bbb">{t.frequency}</span>', unsafe_allow_html=True)
                    c7.write("✅")
                else:
                    if is_group_walk:
                        c1.markdown(f'<span style="color:#1565C0;font-weight:bold">{due_label}</span>', unsafe_allow_html=True)
                        c2.markdown(f'<span style="color:#1565C0;font-weight:bold">{t.scheduled_time} 🐾</span>', unsafe_allow_html=True)
                        c3.markdown(f'<span style="color:#1565C0;font-weight:bold">{task_emoji(t.name)} {t.name}</span>', unsafe_allow_html=True)
                    elif is_conflict:
                        c1.markdown(f'<span style="color:#FF6B00;font-weight:bold">{due_label}</span>', unsafe_allow_html=True)
                        c2.markdown(f'<span style="color:#FF6B00;font-weight:bold">{t.scheduled_time} ⚠</span>', unsafe_allow_html=True)
                        c3.markdown(f'<span style="color:#FF6B00;font-weight:bold">{task_emoji(t.name)} {t.name}</span>', unsafe_allow_html=True)
                    else:
                        c1.write(due_label)
                        c2.write(t.scheduled_time)
                        c3.write(f"{task_emoji(t.name)} {t.name}")
                    c4.write(t.duration_minutes)
                    c5.write(t.priority)
                    c6.write(t.frequency)
                    if c7.button("✅", key=f"d5_{pet_name}_{i}_{t.scheduled_time}_{t.due_date}", help="Mark done"):
                        t.mark_complete()
                        scheduler.handle_recurrence(t, pet_obj)
                        st.rerun()

            st.markdown("---")

        group_walks = scheduler.detect_group_walks()
        real_conflicts = [
            c for c in scheduler.detect_conflicts()
            if not any(f"at {t}" in c and f"on {d}" in c for t, d in group_walk_keys)
        ]
        overlap_warnings = scheduler.detect_overlap_conflicts()

        if group_walks:
            gw_lines = "".join(f"<li>{g}</li>" for g in group_walks)
            st.markdown(
                f"""
                <div style="background-color:#E3F2FD;color:#1565C0;padding:12px 16px;
                            border-radius:8px;margin-top:8px;">
                    <strong>🐾 Group walks — same-species pets walking together (not a conflict):</strong>
                    <ul style="margin:6px 0 0 0;">{gw_lines}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if real_conflicts or overlap_warnings:
            warn_lines = "".join(f"<li>{w}</li>" for w in real_conflicts + overlap_warnings)
            st.markdown(
                f"""
                <div style="background-color:#FF6B00;color:white;padding:12px 16px;
                            border-radius:8px;margin-top:8px;">
                    <strong>⚠ Scheduling conflicts detected — edit the time or delete a task below to resolve:</strong>
                    <ul style="margin:6px 0 0 0;">{warn_lines}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif not group_walks:
            st.success("No scheduling conflicts this week.")
        else:
            st.success("No scheduling conflicts — group walks are cooperative, not conflicts.")

st.divider()

# ── Step 6: AI Care Advisor ───────────────────────────────────────────────────
st.subheader("Step 6: Ask Your AI Care Advisor")
st.markdown(
    "Ask a plain-English question about your pets' schedule. "
    "The advisor reads your actual tasks and responds with specific, grounded advice."
)

with st.form("advisor_form"):
    question = st.text_input(
        "Your question",
        placeholder='e.g. "What\'s most urgent today?" or "Help me fix the 08:00 conflict"',
        key="advisor_question",
    )
    submitted = st.form_submit_button("Ask advisor")

if submitted:
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Thinking..."):
            answer = ask_advisor(owner, question.strip())
        if answer.startswith("ANTHROPIC_API_KEY") or answer.startswith("AI advisor"):
            st.warning(answer)
        else:
            st.markdown(f"**Answer:**\n\n{answer}")
