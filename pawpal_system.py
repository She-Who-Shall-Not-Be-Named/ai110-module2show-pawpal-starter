from dataclasses import dataclass, field
from datetime import datetime, timedelta
from itertools import combinations
from typing import Dict, List, Optional


@dataclass
class Activity:
    task: str
    priority: int          # 1=low, 2=medium, 3=high
    time: datetime
    frequency: str         # "once", "daily", "weekly", "monthly"
    completed: bool = False
    pet: Optional["Pet"] = None

    def set_priority(self, priority: int) -> None:
        """Set the priority level of this activity."""
        self.priority = priority

    def get_priority(self) -> int:
        """Return the current priority level of this activity."""
        return self.priority

    def set_time(self, time: datetime) -> None:
        """Update the scheduled time for this activity."""
        self.time = time

    def get_time(self) -> datetime:
        """Return the scheduled datetime for this activity."""
        return self.time

    def mark_complete(self) -> None:
        """
        Mark this activity as completed.
        For daily and weekly tasks, automatically schedules the next occurrence
        on the same pet.
        """
        self.completed = True
        if self.frequency in ("daily", "weekly") and self.pet:
            delta     = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
            next_task = Activity(
                task=self.task,
                priority=self.priority,
                time=self.time + delta,
                frequency=self.frequency,
            )
            try:
                self.pet.add_task(next_task)
            except ValueError:
                pass  # next occurrence already exists — skip

    def is_due_today(self) -> bool:
        """
        Return True if this activity should occur today, respecting frequency.
        - once:    only on the exact scheduled date
        - daily:   any day on or after the start date
        - weekly:  same weekday as the start date, on or after it
        - monthly: same day-of-month as the start date, on or after it
        """
        today = datetime.today().date()
        task_date = self.time.date()
        if self.frequency == "once":
            return task_date == today
        elif self.frequency == "daily":
            return task_date <= today
        elif self.frequency == "weekly":
            return task_date <= today and self.time.weekday() == datetime.today().weekday()
        elif self.frequency == "monthly":
            return task_date <= today and self.time.day == datetime.today().day
        return False

    def is_one_time_high_priority(self) -> bool:
        """Return True for one-time high-priority tasks like vet appointments."""
        return self.frequency == "once" and self.priority == 3

    def urgency_score(self) -> float:
        """
        Calculate a numeric urgency score combining priority and time proximity.

        Base score is priority * 10 (so High=30, Medium=20, Low=10).
        A time-proximity boost is added for tasks coming up soon:
            - Due within 30 minutes : +4
            - Due within 2 hours    : +2
            - Overdue or far away   :  0

        Returns:
            float: Higher score = should appear earlier in the schedule.
        """
        now = datetime.now()
        task_time_today = self.time.replace(
            year=now.year, month=now.month, day=now.day
        )
        minutes_until = (task_time_today - now).total_seconds() / 60
        base = self.priority * 10
        if 0 <= minutes_until <= 30:
            boost = 4
        elif 0 <= minutes_until <= 120:
            boost = 2
        else:
            boost = 0
        return base + boost


@dataclass
class Pet:
    type: str
    breed_type: str
    name: str
    _tasks: List[Activity] = field(default_factory=list)

    @classmethod
    def create_pet(cls, type: str, breed: str, name: str) -> "Pet":
        """Create and return a new Pet instance."""
        return cls(type=type, breed_type=breed, name=name)

    def add_task(self, activity: Activity, conflict_window_minutes: int = 15) -> Optional[str]:
        """
        Add an activity to this pet and link the pet back to the activity.

        Returns:
            None         — task added successfully.
            warning str  — task was added but overlaps an existing task within
                           conflict_window_minutes (lightweight warning, no crash).
            "duplicate"  — task silently skipped; identical task already exists.
        """
        # Duplicate guard: same task name and same scheduled time
        for existing in self._tasks:
            if existing.task == activity.task and existing.time == activity.time:
                return "duplicate"

        # Conflict check: add the task but return a warning string instead of raising
        warning = None
        window  = timedelta(minutes=conflict_window_minutes)
        for existing in self._tasks:
            if abs(existing.time - activity.time) < window:
                warning = (
                    f"Warning: '{activity.task}' at {activity.time.strftime('%I:%M %p')} "
                    f"overlaps '{existing.task}' at {existing.time.strftime('%I:%M %p')} "
                    f"for {self.name}."
                )
                break

        activity.pet = self
        self._tasks.append(activity)
        return warning

    def remove_task(self, activity: Activity) -> None:
        """Remove an activity from this pet's task list."""
        self._tasks.remove(activity)

    def get_tasks(self) -> List[Activity]:
        """Return all tasks assigned to this pet."""
        return self._tasks

    def get_pending_tasks(self) -> List[Activity]:
        """Return only tasks that have not yet been completed."""
        return [t for t in self._tasks if not t.completed]


@dataclass
class Owner:
    name: str
    _pets: List[Pet] = field(default_factory=list)

    @property
    def num_pets_owned(self) -> int:
        """Return the number of pets this owner has."""
        return len(self._pets)

    def set_pet(self, pet: Pet) -> None:
        """Add a pet, skipping silently if already registered."""
        if pet not in self._pets:
            self._pets.append(pet)

    def get_pet(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        return self._pets

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's list."""
        self._pets.remove(pet)

    def get_all_tasks(self) -> List[Activity]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self._pets for task in pet.get_tasks()]

    def get_tasks_for_pet(self, pet: Pet) -> List[Activity]:
        """Return all tasks assigned to a specific pet."""
        return pet.get_tasks()


class Scheduler:
    def __init__(self, owner: Owner):
        """Initialize the scheduler with an Owner to manage."""
        self.owner = owner

    def get_todays_tasks(self) -> List[Activity]:
        """Return all tasks across all pets that are due today."""
        return [t for t in self.owner.get_all_tasks() if t.is_due_today()]

    def get_tasks_by_priority(self) -> List[Activity]:
        """Return all tasks sorted by priority (desc) then time (asc)."""
        return sorted(self.owner.get_all_tasks(), key=lambda t: (-t.priority, t.time))

    def get_pending_tasks(self) -> List[Activity]:
        """Return all incomplete tasks across all pets."""
        return [t for t in self.owner.get_all_tasks() if not t.completed]

    def get_todays_schedule(self) -> List[Activity]:
        """Return today's incomplete tasks sorted by urgency score (desc) then time (asc)."""
        todays = [t for t in self.get_todays_tasks() if not t.completed]
        return sorted(todays, key=lambda t: (-t.urgency_score(), t.time))

    def get_overdue_tasks(self) -> List[Activity]:
        """Return incomplete tasks whose scheduled time has already passed today."""
        now = datetime.now()
        return [
            t for t in self.get_todays_tasks()
            if not t.completed and t.time < now
        ]

    def get_upcoming_tasks(self, hours: int = 2) -> List[Activity]:
        """Return incomplete tasks scheduled within the next `hours` hours."""
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)
        return [
            t for t in self.get_todays_tasks()
            if not t.completed and now <= t.time <= cutoff
        ]

    def get_summary_by_pet(self) -> Dict[str, List[Activity]]:
        """Return {pet_name: [today's pending tasks sorted by time]} for each pet."""
        summary: Dict[str, List[Activity]] = {}
        for pet in self.owner.get_pet():
            tasks = [t for t in pet.get_tasks() if t.is_due_today() and not t.completed]
            if tasks:
                summary[pet.name] = sorted(tasks, key=lambda t: t.time)
        return summary

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Activity]:
        """
        Return tasks filtered by pet name and/or completion status.

        Args:
            pet_name:  If given, only return tasks belonging to that pet.
            completed: If True, return only completed tasks.
                       If False, return only pending tasks.
                       If None, return tasks regardless of status.
        """
        tasks = self.owner.get_all_tasks()

        if pet_name is not None:
            tasks = [t for t in tasks if t.pet and t.pet.name == pet_name]

        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]

        return tasks

    def get_conflicts(
        self,
        window_minutes: int = 0,
        same_pet_only: bool = True,
    ) -> List[tuple]:
        """
        Return all pairs of tasks whose scheduled times overlap.

        Args:
            window_minutes: Tasks are considered conflicting when the gap
                            between their times is <= this value.
                            Use 0 to flag only exact same-time clashes.
            same_pet_only:  If True (default), only flag conflicts where both
                            tasks belong to the same pet — two different pets
                            being cared for at the same time is not a conflict.
                            Set to False to also surface cross-pet overlaps.

        Returns a list of (task_a, task_b) tuples, each pair reported once.
        """
        tasks    = self.owner.get_all_tasks()
        window   = timedelta(minutes=window_minutes)

        return [
            (a, b) for a, b in combinations(tasks, 2)
            if (not same_pet_only or a.pet == b.pet)
            and abs(a.time - b.time) <= window
        ]

    def get_conflict_warnings(
        self,
        window_minutes: int = 0,
        same_pet_only: bool = True,
    ) -> List[str]:
        """
        Return human-readable warning strings for every conflicting task pair.

        Wraps get_conflicts() and formats each pair into a sentence describing
        which pets and tasks are involved and how far apart they are scheduled.
        Never raises — safe to call at any point without crashing the program.

        Args:
            window_minutes: Passed through to get_conflicts(). Tasks whose
                            scheduled times are within this many minutes of each
                            other are considered conflicting.
            same_pet_only:  If True (default), only same-pet conflicts are
                            reported. Set to False to include cross-pet overlaps.

        Returns:
            List[str]: One warning string per conflicting pair, or an empty
                       list if no conflicts are found.
        """
        warnings = []
        for a, b in self.get_conflicts(window_minutes=window_minutes, same_pet_only=same_pet_only):
            gap       = int(abs((a.time - b.time).total_seconds()) / 60)
            pet_a     = a.pet.name if a.pet else "?"
            pet_b     = b.pet.name if b.pet else "?"
            gap_str   = "same time" if gap == 0 else f"{gap} min apart"
            pet_str   = f"{pet_a}" if pet_a == pet_b else f"{pet_a} and {pet_b}"
            warnings.append(
                f"⚠ Conflict ({pet_str}, {gap_str}): "
                f"'{a.task}' at {a.get_time().strftime('%I:%M %p')} "
                f"vs '{b.task}' at {b.get_time().strftime('%I:%M %p')}"
            )
        return warnings

    def generate_next_occurrences(self) -> List[Activity]:
        """
        For each recurring task, return a new Activity for the next scheduled instance.
        Does NOT register them — caller decides whether to add them.
        """
        next_tasks: List[Activity] = []
        for task in self.owner.get_all_tasks():
            if task.frequency == "daily":
                next_time = task.time + timedelta(days=1)
            elif task.frequency == "weekly":
                next_time = task.time + timedelta(weeks=1)
            elif task.frequency == "monthly":
                next_time = task.time + timedelta(days=30)
            else:
                continue  # "once" tasks do not recur
            next_tasks.append(Activity(
                task=task.task,
                priority=task.priority,
                time=next_time,
                frequency=task.frequency,
            ))
        return next_tasks
