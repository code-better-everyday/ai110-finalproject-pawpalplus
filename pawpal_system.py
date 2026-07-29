"""
pawpal_system.py
----------------
Core backend logic for PawPal+. Defines the four main classes:
  - Task     : a single pet care activity
  - Pet      : a pet that owns a list of tasks
  - Owner    : the user who owns one or more pets
  - Scheduler: the brain that organizes and analyzes tasks across all pets
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class Task:
    """
    Represents a single pet care activity.

    Attributes:
        name             : human-readable task name (e.g. "Morning walk")
        scheduled_time   : time of day in "HH:MM" format (used for sorting)
        duration_minutes : how long the task takes in minutes
        priority         : importance level — "low", "medium", or "high"
        frequency        : how often it recurs — "once", "daily", or "weekly"
        completed        : True if the task has been done for this occurrence
        due_date         : the calendar date this task is scheduled for
    """

    name: str
    scheduled_time: str          # "HH:MM" — kept as string for easy lambda sorting
    duration_minutes: int
    priority: str                # "low" | "medium" | "high"
    frequency: str               # "once" | "daily" | "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Set this task's completed status to True."""
        self.completed = True

    def __str__(self) -> str:
        """Return a readable one-line summary of the task for CLI display."""
        status = "[x]" if self.completed else "[ ]"
        return (
            f"{status} {self.scheduled_time} | {self.name} "
            f"({self.duration_minutes} min) [{self.priority}] [{self.frequency}]"
        )


@dataclass
class Pet:
    """
    Represents a pet owned by the user.

    Attributes:
        name    : the pet's name
        species : type of animal (e.g. "dog", "cat")
        tasks   : list of Task objects assigned to this pet
    """

    name: str
    species: str
    tasks: list = field(default_factory=list)  # starts empty; tasks added via add_task()

    def add_task(self, task: Task) -> None:
        """Append a Task to this pet's task list."""
        self.tasks.append(task)

    def task_count(self) -> int:
        """Return the total number of tasks assigned to this pet."""
        return len(self.tasks)

    def remove_task(self, name: str, scheduled_time: str) -> bool:
        """Remove a task matching name and scheduled_time. Returns True if removed."""
        for task in self.tasks:
            if task.name == name and task.scheduled_time == scheduled_time:
                self.tasks.remove(task)
                return True
        return False


@dataclass
class Owner:
    """
    Represents the pet owner (one per app session).

    Attributes:
        name : the owner's name, entered in the UI
        pets : list of Pet objects belonging to this owner
    """

    name: str
    pets: list = field(default_factory=list)  # starts empty; pets added via add_pet()

    def add_pet(self, pet: Pet) -> None:
        """Append a Pet to this owner's pet list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list:
        """
        Return a flat list of (pet_name, task) tuples across every pet.
        Used by Scheduler to access all tasks in one call.
        """
        result = []
        for pet in self.pets:
            for task in pet.tasks:
                result.append((pet.name, task))
        return result


class Scheduler:
    """
    The scheduling brain for PawPal+.

    Takes an Owner and provides methods to retrieve, sort, filter,
    and analyze tasks across all of the owner's pets.
    """

    def __init__(self, owner: Owner) -> None:
        """Store a reference to the owner whose tasks we manage."""
        self.owner = owner

    def get_schedule(self) -> list:
        """Return all (pet_name, task) tuples from the owner's pets."""
        return self.owner.get_all_tasks()

    def sort_by_time(self) -> list:
        """Return all tasks sorted chronologically by scheduled_time (HH:MM string sort)."""
        return sorted(self.get_schedule(), key=lambda x: x[1].scheduled_time)

    def sort_by_priority_then_time(self) -> list:
        """Return tasks sorted by priority (high first) then by scheduled_time within each tier."""
        order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            self.get_schedule(),
            key=lambda x: (order.get(x[1].priority, 99), x[1].scheduled_time),
        )

    def filter_by_status(self, completed: bool) -> list:
        """Return only tasks that match the given completion status (True or False)."""
        return [
            (pet, task) for pet, task in self.get_schedule()
            if task.completed == completed
        ]

    def filter_by_pet(self, pet_name: str) -> list:
        """Return only tasks belonging to the named pet (case-insensitive match)."""
        return [
            (pet, task) for pet, task in self.get_schedule()
            if pet.lower() == pet_name.lower()
        ]

    def detect_conflicts(self) -> list:
        """
        Check for tasks scheduled at the exact same time on the same date.
        Returns a list of warning strings (empty list means no conflicts).
        Uses exact HH:MM match — overlapping durations are not checked.
        """
        seen = {}      # maps (scheduled_time, due_date) -> first task name at that slot
        warnings = []

        for pet, task in self.get_schedule():
            key = (task.scheduled_time, task.due_date)
            if key in seen:
                # Two tasks share the same time slot — flag it as a conflict
                warnings.append(
                    f"Conflict at {task.scheduled_time} on {task.due_date}: "
                    f"'{seen[key]}' and '{task.name}'"
                )
            else:
                seen[key] = task.name

        return warnings

    def handle_recurrence(self, task: Task, pet: Pet) -> None:
        """
        When a recurring task is marked complete, create the next occurrence.
        Daily tasks advance due_date by 1 day; weekly tasks by 7 days.
        'once' tasks are not re-created — they are one-off activities.
        """
        if not task.completed or task.frequency == "once":
            return

        # Calculate the next due date based on frequency
        if task.frequency == "daily":
            next_date = task.due_date + timedelta(days=1)
        elif task.frequency == "weekly":
            next_date = task.due_date + timedelta(weeks=1)
        else:
            return

        # Create a fresh (uncompleted) task for the next occurrence
        next_task = Task(
            name=task.name,
            scheduled_time=task.scheduled_time,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            frequency=task.frequency,
            completed=False,
            due_date=next_date,
        )
        pet.add_task(next_task)
