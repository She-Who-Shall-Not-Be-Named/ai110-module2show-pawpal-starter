from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


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
        """Mark this activity as completed."""
        self.completed = True

    def is_due_today(self) -> bool:
        """Return True if this activity is scheduled for today's date."""
        return self.time.date() == datetime.today().date()


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

    def add_task(self, activity: Activity) -> None:
        """Add an activity to this pet and link the pet back to the activity."""
        activity.pet = self
        self._tasks.append(activity)

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
        """Add a pet to this owner's list."""
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
        """Return all tasks across all pets that are scheduled for today."""
        return [t for t in self.owner.get_all_tasks() if t.is_due_today()]

    def get_tasks_by_priority(self) -> List[Activity]:
        """Return all tasks sorted from highest to lowest priority."""
        return sorted(self.owner.get_all_tasks(), key=lambda t: t.priority, reverse=True)

    def get_pending_tasks(self) -> List[Activity]:
        """Return all incomplete tasks across all pets."""
        return [t for t in self.owner.get_all_tasks() if not t.completed]

    def get_todays_schedule(self) -> List[Activity]:
        """Return today's incomplete tasks sorted by priority then time."""
        todays = [t for t in self.get_todays_tasks() if not t.completed]
        return sorted(todays, key=lambda t: (-(t.priority), t.time))
