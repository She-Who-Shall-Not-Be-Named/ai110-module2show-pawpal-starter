# PawPal+ 🐾

A smart pet care scheduling app built with Python and Streamlit. PawPal+ helps busy pet owners stay on top of daily routines by automatically sorting, filtering, and conflict-checking tasks across multiple pets.

## Features

| Feature | Description |
|---|---|
| **Smart urgency sorting** | Tasks are ranked by priority *and* how soon they're due — a high-priority task due in 15 minutes floats above one due in 6 hours |
| **Flexible filtering** | Filter the schedule by pet, status (pending / completed / all), or any combination |
| **Recurring task auto-scheduling** | Marking a daily or weekly task complete automatically creates the next occurrence — no manual re-entry |
| **Conflict detection** | The scheduler scans every task pair and warns when two tasks for the same pet are scheduled too close together |
| **Conflict warnings in the UI** | Conflicts appear as expandable `st.warning` banners with plain-English descriptions — no crashes, no technical errors |
| **Frequency-aware due dates** | `once`, `daily`, `weekly`, and `monthly` tasks each apply their own logic for whether they appear today |
| **Per-pet summary** | A quick-glance panel at the bottom shows each pet's pending tasks for the day |
| **Overdue & upcoming alerts** | Separate banners surface tasks that have passed and tasks due within the next 2 hours |

## System Architecture

The final class diagram is in [`uml_final.md`](uml_final.md) (Mermaid.js format — paste into [mermaid.live](https://mermaid.live) to view).

Four classes, one responsibility each:

- **`Activity`** — a single task with time, priority, frequency, and completion state
- **`Pet`** — owns a list of Activities; enforces duplicate and conflict guards on add
- **`Owner`** — owns a list of Pets; aggregates tasks across all pets
- **`Scheduler`** — all sorting, filtering, conflict detection, and schedule-building logic

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

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest tests/test_pawpal.py -v
```

**What the tests cover (43 tests across 8 classes):**

| Class | What it verifies |
|---|---|
| `TestActivity` | Priority/time getters, `mark_complete`, `is_due_today` |
| `TestPet` | Task add/remove, pending filter, pet-task link |
| `TestOwner` | Pet registration, deduplication, cross-pet task aggregation |
| `TestScheduler` | Today's tasks, priority sort, completed exclusion |
| `TestSorting` | Chronological order, priority descending, tie-breaking by time |
| `TestRecurrence` | Daily → next day, weekly → next week, once → no recurrence, time-of-day preserved |
| `TestConflictDetection` | Exact clashes, same-pet vs cross-pet, warning strings, no false positives |
| `TestFiltering` | Filter by pet, by status, combined, no-arg returns all |
| `TestEdgeCases` | Empty pet, duplicate guard, overlap warning without crash, owner dedup |

**Confidence level: ★★★★☆**
Core scheduling logic (sorting, filtering, recurrence, conflict detection) is fully covered. The remaining gap is integration-level tests for the Streamlit UI layer and duration-aware conflict detection, which is documented as a known tradeoff in `reflection.md`.

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
