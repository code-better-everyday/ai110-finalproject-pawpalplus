from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import date, timedelta


def test_task_mark_complete():
    """Calling mark_complete() should set completed to True."""
    task = Task("Morning walk", "07:30", 30, "high", "daily")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_pet_task_count_increases_on_add():
    """Adding a task to a Pet should increase its task count by 1."""
    pet = Pet("Mochi", "dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Feeding", "08:00", 10, "high", "daily"))
    assert pet.task_count() == 1
    pet.add_task(Task("Grooming", "11:00", 20, "medium", "weekly"))
    assert pet.task_count() == 2


# ── Core behavior 1: sort_by_time ─────────────────────────────────────────────

def test_sort_by_time_orders_chronologically():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Evening walk", "18:00", 30, "high",   "daily"))
    pet.add_task(Task("Morning walk", "07:30", 30, "high",   "daily"))
    pet.add_task(Task("Feeding",      "12:00", 10, "medium", "daily"))
    owner.add_pet(pet)

    times = [t.scheduled_time for _, t in Scheduler(owner).sort_by_time()]
    assert times == sorted(times)


def test_sort_by_time_empty_pet():
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "dog"))
    assert Scheduler(owner).sort_by_time() == []


# ── Core behavior 2: detect_conflicts ────────────────────────────────────────

def test_detect_conflicts_same_time_flags_warning():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    today = date.today()
    pet.add_task(Task("Walk",     "09:00", 30, "high", "daily", due_date=today))
    pet.add_task(Task("Vet visit","09:00", 60, "high", "once",  due_date=today))
    owner.add_pet(pet)

    conflicts = Scheduler(owner).detect_conflicts()
    assert len(conflicts) == 1
    assert "09:00" in conflicts[0]


def test_detect_conflicts_different_times_no_warning():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk",    "07:30", 30, "high",   "daily"))
    pet.add_task(Task("Feeding", "08:30", 10, "medium", "daily"))
    owner.add_pet(pet)

    assert Scheduler(owner).detect_conflicts() == []


# ── Core behavior 3: handle_recurrence ───────────────────────────────────────

def test_handle_recurrence_daily_creates_next_day():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    task = Task("Morning walk", "07:30", 30, "high", "daily")
    pet.add_task(task)
    owner.add_pet(pet)

    task.mark_complete()
    Scheduler(owner).handle_recurrence(task, pet)

    assert pet.task_count() == 2
    next_task = pet.tasks[-1]
    assert next_task.due_date == task.due_date + timedelta(days=1)
    assert next_task.completed is False


def test_handle_recurrence_weekly_creates_seven_days_later():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    task = Task("Grooming", "11:00", 20, "medium", "weekly")
    pet.add_task(task)
    owner.add_pet(pet)

    task.mark_complete()
    Scheduler(owner).handle_recurrence(task, pet)

    assert pet.tasks[-1].due_date == task.due_date + timedelta(weeks=1)


def test_handle_recurrence_once_does_not_add_task():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    task = Task("Vet visit", "09:00", 60, "high", "once")
    pet.add_task(task)
    owner.add_pet(pet)

    task.mark_complete()
    Scheduler(owner).handle_recurrence(task, pet)

    assert pet.task_count() == 1  # no new task added


# ── Core behavior 4: filter_by_status ────────────────────────────────────────

def test_filter_by_status_returns_only_incomplete():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk",    "07:30", 30, "high",   "daily", completed=True))
    pet.add_task(Task("Feeding", "08:00", 10, "medium", "daily", completed=False))
    owner.add_pet(pet)

    result = Scheduler(owner).filter_by_status(completed=False)
    assert len(result) == 1
    assert result[0][1].name == "Feeding"


# ── Core behavior 5: filter_by_pet ───────────────────────────────────────────

def test_filter_by_pet_case_insensitive():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna  = Pet("Luna",  "cat")
    mochi.add_task(Task("Walk",    "07:30", 30, "high", "daily"))
    luna.add_task( Task("Feeding", "08:00", 10, "high", "daily"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    result = Scheduler(owner).filter_by_pet("mochi")
    assert len(result) == 1
    assert result[0][1].name == "Walk"


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_mark_complete_twice_stays_true():
    task = Task("Walk", "07:30", 30, "high", "daily")
    task.mark_complete()
    task.mark_complete()
    assert task.completed is True


def test_handle_recurrence_not_complete_does_nothing():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    task = Task("Walk", "08:00", 30, "high", "daily")
    pet.add_task(task)
    owner.add_pet(pet)

    Scheduler(owner).handle_recurrence(task, pet)  # task NOT marked complete
    assert pet.task_count() == 1


def test_filter_by_pet_no_match_returns_empty():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "07:30", 30, "high", "daily"))
    owner.add_pet(pet)

    assert Scheduler(owner).filter_by_pet("Buddy") == []
