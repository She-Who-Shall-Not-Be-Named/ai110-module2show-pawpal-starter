# PawPal+ — Final Class Diagram

Render this diagram at [mermaid.live](https://mermaid.live) or in any Markdown viewer with Mermaid support.

```mermaid
classDiagram
    class Activity {
        +str task
        +int priority
        +datetime time
        +str frequency
        +bool completed
        +Pet pet
        +set_priority(priority: int) None
        +get_priority() int
        +set_time(time: datetime) None
        +get_time() datetime
        +mark_complete() None
        +is_due_today() bool
        +is_one_time_high_priority() bool
        +urgency_score() float
    }

    class Pet {
        +str type
        +str breed_type
        +str name
        -List~Activity~ _tasks
        +create_pet(type, breed, name)$ Pet
        +add_task(activity, window_minutes) str
        +remove_task(activity) None
        +get_tasks() List~Activity~
        +get_pending_tasks() List~Activity~
    }

    class Owner {
        +str name
        -List~Pet~ _pets
        +num_pets_owned int
        +set_pet(pet) None
        +get_pet() List~Pet~
        +remove_pet(pet) None
        +get_all_tasks() List~Activity~
        +get_tasks_for_pet(pet) List~Activity~
    }

    class Scheduler {
        +Owner owner
        +get_todays_tasks() List~Activity~
        +get_tasks_by_priority() List~Activity~
        +get_pending_tasks() List~Activity~
        +get_todays_schedule() List~Activity~
        +get_overdue_tasks() List~Activity~
        +get_upcoming_tasks(hours) List~Activity~
        +get_summary_by_pet() Dict
        +filter_tasks(pet_name, completed) List~Activity~
        +get_conflicts(window_minutes, same_pet_only) List~tuple~
        +get_conflict_warnings(window_minutes, same_pet_only) List~str~
        +generate_next_occurrences() List~Activity~
    }

    Owner "1" *-- "0..*" Pet : owns
    Pet "1" *-- "0..*" Activity : has
    Activity "0..1" --> "1" Pet : belongs to
    Scheduler "1" --> "1" Owner : manages
```

## Changes from initial design

| Initial | Final | Reason |
|---|---|---|
| `Activity.time: str` | `Activity.time: datetime` | Enables sorting and arithmetic (`timedelta`) without parsing |
| No `frequency` field | `Activity.frequency: str` | Required for recurring task logic |
| No `completed` field | `Activity.completed: bool` | Needed to track done/pending state |
| `Activity.mark_complete()` sets a flag | Also auto-schedules next occurrence | Recurrence logic belongs on the task itself |
| `Owner` held a flat `_tasks` list | Removed — tasks live on `Pet` | Avoids duplication; `get_all_tasks()` aggregates across pets |
| No `Scheduler` class | `Scheduler` added | Keeps sort/filter/conflict logic out of data classes and UI |
| No conflict detection | `get_conflicts()` + `get_conflict_warnings()` | Pet owners need to know when they've double-booked a pet |
| No `filter_tasks()` | `Scheduler.filter_tasks(pet_name, completed)` | UI needs composable filtering without duplicating logic |
