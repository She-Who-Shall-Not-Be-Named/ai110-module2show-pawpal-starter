# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ goes beyond a basic to-do list with several algorithmic improvements built into `pawpal_system.py`:

**Sorting**
- Tasks can be sorted by time, priority, or an *urgency score* that combines priority with time proximity — a high-priority task due in 20 minutes ranks above one due in 6 hours.

**Filtering**
- `Scheduler.filter_tasks(pet_name, completed)` returns any slice of tasks by pet and/or completion status. Both parameters are optional and composable — e.g., Rex's pending tasks only.

**Recurring task auto-scheduling**
- Marking a `daily` or `weekly` task complete automatically creates the next occurrence on the same pet using `timedelta`, so the owner never has to re-enter routine tasks.

**Conflict detection**
- `Scheduler.get_conflicts(window_minutes, same_pet_only)` uses `itertools.combinations` to scan every task pair and surface scheduling overlaps.
- By default only same-pet conflicts are flagged (walking Rex and feeding Mochi at the same time is fine).
- `Scheduler.get_conflict_warnings()` returns the same results as plain-English strings — no exceptions raised, program never crashes.

**Frequency-aware due-date logic**
- `Activity.is_due_today()` respects each task's frequency: `once` tasks appear only on their exact date, `daily` tasks appear every day from their start date onward, and `weekly`/`monthly` tasks match by weekday or day-of-month.

## Getting started

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
