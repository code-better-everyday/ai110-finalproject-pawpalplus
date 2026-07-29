"""
app.py
------
Streamlit UI for PawPal+. Connects the frontend inputs to the
backend logic defined in pawpal_system.py.

Run with:  streamlit run app.py
"""

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler


def species_emoji(species: str) -> str:
    return {"dog": "🐕", "cat": "🐈", "rabbit": "🐇", "bird": "🦜", "fish": "🐠", "hamster": "🐹"}.get(species.lower(), "🐾")


def task_emoji(name: str) -> str:
    n = name.lower()
    if "walk" in n:   return "🚶"
    if "feed" in n:   return "🍽️"
    if "med" in n:    return "💊"
    if "vet" in n:    return "🏥"
    if "groom" in n:  return "✂️"
    if "play" in n:   return "🎾"
    return "📋"


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

st.markdown(
    """
    <div style="text-align:center;padding:16px 0 8px 0;">
        <div style="font-size:2.8rem;letter-spacing:10px;">🐕 🐈 🐇 🦜 🐹 🐠</div>
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
    # Owner not yet set — show input
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
        for key in ["owner", "pet_count", "add_count"]:
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
st.subheader("Step 2: Add a Pet")

if "pet_count" not in st.session_state:
    st.session_state.pet_count = 0

pk = st.session_state.pet_count  # key suffix to reset pet fields after add

if owner.pets:
    # Show existing pets
    st.markdown("**Your pets:**")
    for p in owner.pets:
        st.write(f"  {species_emoji(p.species)} {p.name} ({p.species})")
    st.markdown("---")

pet_name = st.text_input(
    "Pet name", value="", placeholder="Enter your pet's name",
    key=f"pet_name_{pk}"
)
species = st.selectbox("Species", ["dog", "cat", "other"], key=f"species_{pk}")

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
    st.stop()

st.divider()

# ── Step 3: Add Tasks ──────────────────────────────────────────────────────────
st.subheader("Step 3: Add a Task")

# Let user pick which pet to assign the task to
pet_names  = [p.name for p in owner.pets]
chosen_pet = st.selectbox("Assign to pet", pet_names)
pet        = next(p for p in owner.pets if p.name == chosen_pet)

# Counter key to reset task fields after each successful add
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
        # Duplicate guard: warn if same name + time already exists for this pet
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
            ))
            st.session_state.add_count += 1  # resets task fields
            st.success(f"Added '{task_title}' to {pet.name}'s schedule!")
            st.rerun()

# Show current tasks with a Delete button per row
if pet.task_count() > 0:
    st.markdown(f"**{pet.name}'s tasks ({pet.task_count()} total):**")

    # Find which (scheduled_time, due_date) slots have conflicts across all pets
    seen_slots: dict = {}
    conflict_slots: set = set()
    for p in owner.pets:
        for task in p.tasks:
            slot_key = (task.scheduled_time, str(task.due_date))
            if slot_key in seen_slots:
                conflict_slots.add(slot_key)
            else:
                seen_slots[slot_key] = task.name

    for i, t in enumerate(pet.tasks):
        col_time, col_task, col_dur, col_pri, col_freq, col_del = st.columns([1, 2, 1, 1, 1, 1])
        is_conflict = (t.scheduled_time, str(t.due_date)) in conflict_slots
        if is_conflict:
            col_time.markdown(
                f'<span style="color:#FF6B00;font-weight:bold">{t.scheduled_time} ⚠</span>',
                unsafe_allow_html=True,
            )
            col_task.markdown(
                f'<span style="color:#FF6B00;font-weight:bold">{task_emoji(t.name)} {t.name}</span>',
                unsafe_allow_html=True,
            )
        else:
            col_time.write(t.scheduled_time)
            col_task.write(f"{task_emoji(t.name)} {t.name}")
        col_dur.write(f"{t.duration_minutes} min")
        col_pri.write(t.priority)
        col_freq.write(t.frequency)
        if col_del.button("Delete", key=f"del_{i}_{t.name}_{t.scheduled_time}"):
            pet.remove_task(t.name, t.scheduled_time)
            st.rerun()
else:
    st.info(f"No tasks yet for {pet.name}. Add one above.")

st.divider()

# ── Step 4: Generate Schedule ─────────────────────────────────────────────────
st.subheader("Step 4: Generate Today's Schedule")

if st.button("Generate schedule"):
    all_tasks = owner.get_all_tasks()
    if not all_tasks:
        st.warning("No tasks added yet. Add at least one task first.")
    else:
        scheduler = Scheduler(owner)

        sorted_tasks = scheduler.sort_by_priority_then_time()
        st.markdown(f"**Schedule for {owner.name} — sorted by priority, then time:**")

        # Identify conflicting time slots to highlight rows
        seen_slots: dict = {}
        conflict_slots: set = set()
        for p_name, task in sorted_tasks:
            slot_key = (task.scheduled_time, str(task.due_date))
            if slot_key in seen_slots:
                conflict_slots.add(slot_key)
            else:
                seen_slots[slot_key] = task.name

        rows_html = ""
        for p_name, task in sorted_tasks:
            is_conflict = (task.scheduled_time, str(task.due_date)) in conflict_slots
            row_bg    = "background-color:#FFF3E0;" if is_conflict else ""
            cell_style = f'style="{row_bg}color:#FF6B00;font-weight:bold;padding:6px 10px;"' if is_conflict else 'style="padding:6px 10px;"'
            pet_obj = next((p for p in owner.pets if p.name == p_name), None)
            p_emoji = species_emoji(pet_obj.species) if pet_obj else "🐾"
            rows_html += (
                f"<tr>"
                f"<td {cell_style}>{task.scheduled_time}{' ⚠' if is_conflict else ''}</td>"
                f"<td {cell_style}>{p_emoji} {p_name}</td>"
                f"<td {cell_style}>{task_emoji(task.name)} {task.name}</td>"
                f"<td {cell_style}>{task.duration_minutes}</td>"
                f"<td {cell_style}>{task.priority}</td>"
                f"<td {cell_style}>{task.frequency}</td>"
                f"</tr>"
            )

        th = 'style="text-align:left;padding:6px 10px;border-bottom:2px solid #ddd;"'
        st.markdown(
            f"""
            <table style="width:100%;border-collapse:collapse;font-size:14px;">
                <thead>
                    <tr>
                        <th {th}>Time</th>
                        <th {th}>Pet</th>
                        <th {th}>Task</th>
                        <th {th}>Duration (min)</th>
                        <th {th}>Priority</th>
                        <th {th}>Frequency</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            """,
            unsafe_allow_html=True,
        )

        conflicts = scheduler.detect_conflicts()
        if conflicts:
            conflict_lines = "".join(f"<li>{c}</li>" for c in conflicts)
            st.markdown(
                f"""
                <div style="background-color:#FF6B00;color:white;padding:12px 16px;
                            border-radius:8px;margin-top:8px;">
                    <strong>⚠ Scheduling conflicts detected — delete one task below to resolve:</strong>
                    <ul style="margin:6px 0 0 0;">{conflict_lines}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.success("No scheduling conflicts.")
