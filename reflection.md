# PawPal+ Project Reflection

## 1. System Design

Users should be able to:
- Add a pet and register it to their account
- Add, edit, and remove care tasks with time, priority, and frequency
- View a daily schedule sorted by urgency
- Be warned when tasks conflict
- Mark tasks complete and have recurring ones auto-schedule themselves

**a. Initial design**

The initial UML included three classes:

**Owner**
- `self.name` — name of owner
- `self.num_pets_owned` — how many pets they own
- `self.pet_name` — names of pets
- `set_pet()`, `get_pet()`, `remove_pet()`, `set_task()`, `get_task()`, `remove_task()`

**Pet**
- `self.type` — cat, dog, bird, etc.
- `self.breed_type` — breed
- `self.name` — pet's name
- `create_pet(type, breed, name)`

**Activity**
- `self.task` — task description
- `self.priority` — priority level
- `self.time` — scheduled time as a string
- `set_priority()`, `get_priority()`, `set_time()`, `get_time()`

Each class was responsible for its own data. Owner held tasks directly alongside pets, and Activity had no connection back to the pet it belonged to.

**b. Design changes**

Yes, the design changed significantly during implementation.

`create_pet` was converted to a `@classmethod` since constructing a Pet from an existing instance made no sense. `Activity` gained an optional `pet: Pet` field to capture which pet a task belongs to, closing the missing link between the two classes. `time` was changed from `str` to `datetime` so scheduling logic could compare and sort times without string-parsing bugs. On `Owner`, `pet_name: List[str]` was removed since `_pets` already holds `Pet` objects with a `.name` attribute. `num_pets_owned` became a `@property` returning `len(self._pets)` so the count stays accurate automatically.

`Activity` gained `frequency` and `completed` fields. `Pet` took ownership of its own task list. `Owner` dropped its flat `_tasks` list and instead aggregates tasks across all pets via `get_all_tasks()`. A new `Scheduler` class was added as the brain of the system — taking an `Owner` and providing sort, filter, conflict detection, and daily-view logic so that scheduling behavior stays out of both the data classes and the UI.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:

1. **Time** — tasks are sorted chronologically so the owner sees what comes first in the day
2. **Priority** — high-priority tasks (priority=3) rank above medium and low ones in the default sort
3. **Urgency** — a composite score (`urgency_score()`) that combines base priority with time proximity, so a medium-priority task due in 10 minutes can outrank a high-priority task due in 6 hours

Priority and time were chosen as the most important constraints because they are the two things a pet owner actually has to make decisions about — some tasks genuinely cannot be skipped (medication, feeding), and time determines what needs to happen *now* vs. later in the day.

**b. Tradeoffs**

The scheduler compares task **start times only** — it has no concept of how long a task takes. Two tasks scheduled 20 minutes apart are treated as non-conflicting even if a vet appointment lasts 90 minutes and overlaps everything scheduled after it.

This is a reasonable tradeoff because:
- Most household pet tasks (feeding, brushing, medication) are short and point-in-time by nature
- Adding a `duration` field to every `Activity` would require owners to estimate times they rarely think about, adding friction to the UI
- The `window_minutes` parameter in `get_conflicts()` partially compensates — setting a window of 60 or 90 minutes catches likely overlaps without needing true duration data

The cost is that a long task like a vet visit won't automatically block the surrounding time slots. A future iteration could add an optional `duration_minutes` field to `Activity` that defaults to `0`, making duration-aware conflict detection opt-in rather than required.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used throughout every phase of the project:

- **Design brainstorming** — asking "what small algorithms could make this scheduler smarter for a pet owner" surfaced ideas like urgency scoring, duplicate guards, and frequency-aware due dates that I hadn't considered
- **Implementation** — generating method stubs and iterating on them (e.g., the conflict detection loop, the recurrence logic in `mark_complete()`)
- **Refactoring** — the `get_conflicts()` nested loop was simplified to `itertools.combinations` after asking how the method could be made more Pythonic
- **Testing** — drafting the full pytest suite, including edge cases like empty pets, duplicate guards, and the `test_not_due_today` bug fix
- **UI polish** — identifying that `st.success()` + `st.rerun()` caused messages to flash and disappear, and replacing with `st.toast()`

The most effective prompts were specific and behavioral: *"implement a method that filters tasks by completion status or pet name"* produced cleaner, more targeted code than vague requests. Asking *"what are the UI bugs and unprofessional issues"* and letting AI audit the app was more efficient than reviewing it line by line manually.

**b. Judgment and verification**

One moment where I modified an AI suggestion: when conflict detection was first implemented, `Pet.add_task()` raised a `ValueError` when a scheduling conflict was detected. This caused the program to crash when a conflicting task was added. The AI-generated version treated it as a hard error.

I pushed back on this because a pet scheduling app should never crash on user input — conflicts are expected and normal. The fix was to change `add_task()` to return a warning string instead of raising, and add `Scheduler.get_conflict_warnings()` as a separate method for scanning the full schedule. This kept the program running while still surfacing the issue clearly.

I verified the change by running `main.py` end-to-end with deliberately conflicting tasks and confirming `"Program completed without crashing."` printed at the end, then writing tests in `TestConflictDetection` that assert no exceptions are raised.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers 43 tests across 8 classes:

- **Sorting** — tasks added out of chronological order are correctly returned sorted by time, then by priority, with time breaking ties between equal-priority tasks
- **Recurrence** — `daily` tasks auto-schedule for the next day on completion, `weekly` for next week, `once` tasks produce no next occurrence, and the time-of-day is preserved exactly
- **Conflict detection** — exact same-time same-pet clashes are flagged; cross-pet overlaps are correctly ignored by default and detected when opted in; warning strings are non-empty and contain the pet name
- **Filtering** — `filter_tasks()` correctly isolates by pet name, by status, and by both combined; no-arg call returns everything
- **Edge cases** — an empty pet returns empty lists from all scheduler methods; adding a duplicate task returns `"duplicate"` and does not increase the task count; owner deduplication prevents the same pet being registered twice

These tests matter because the scheduler's value depends entirely on correctness — wrong sort order, missed recurrence, or false conflict warnings would make the app less trustworthy than a paper list.

**b. Confidence**

**★★★★☆ — High confidence in the logic layer, partial coverage of the UI layer.**

All core scheduling behaviors (sort, filter, recurrence, conflict detection, frequency-aware due dates) have direct test coverage and pass. The remaining gap is the Streamlit UI — `app.py` is not tested automatically, so interactions like the "Mark done" button triggering a toast notification and a rerun are verified manually only. The known tradeoff (start-time-only conflict detection) is the most likely source of a missed real-world conflict.

Next edge cases to test:
- Monthly task recurrence crossing a month boundary (e.g., Jan 31 → Feb 28)
- `generate_next_occurrences()` with a mix of all four frequency types
- Marking a task complete when the next occurrence already exists (duplicate guard on recurrence)

---

## 5. Reflection

**a. What went well**

The separation between the data layer (`Activity`, `Pet`, `Owner`) and the logic layer (`Scheduler`) worked well from the start and stayed clean throughout. Because `Scheduler` holds all the sorting, filtering, and conflict logic, adding new features — like `filter_tasks()` or `get_conflict_warnings()` — never required touching the data classes. The UI (`app.py`) stayed thin and readable because it delegates everything to `Scheduler` rather than reimplementing logic inline.

**b. What you would improve**

The biggest limitation is that tasks have no duration. Every task is treated as instantaneous, which means the conflict detection window is a rough approximation rather than a real overlap check. In a next iteration, I would add an optional `duration_minutes: int = 0` field to `Activity` and update `get_conflicts()` to check whether two tasks' time windows actually overlap rather than just comparing start times.

I would also persist the schedule to a file or database. Right now all data lives in Streamlit session state and resets when the app restarts, which makes it impractical as a real daily tool.

**c. Key takeaway**

The most important thing I learned is that AI tools are most valuable when you already have a clear design. When I gave the AI a specific, well-scoped method to implement — *"add a method to Scheduler that returns conflicting task pairs using itertools.combinations"* — it produced clean, correct code immediately. When I asked open-ended questions early in the project, the suggestions were sometimes architecturally wrong (like putting scheduling logic directly in `Pet` instead of `Scheduler`).

Being the lead architect means deciding *where* behavior belongs before asking AI to implement it. The AI can write the code faster than I can, but it cannot decide that conflict detection belongs in `Scheduler` rather than `Pet` — that judgment requires understanding the whole system. The clearer my design decisions were, the better the AI's output became.
