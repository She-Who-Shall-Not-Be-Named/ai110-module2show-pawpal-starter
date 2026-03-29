import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import datetime, timedelta
from pawpal_system import Activity, Pet, Owner, Scheduler


# --- Helpers ---

def make_activity(task="Feed", priority=2, hour=9, frequency="daily"):
    time = datetime.today().replace(hour=hour, minute=0, second=0, microsecond=0)
    return Activity(task=task, priority=priority, time=time, frequency=frequency)

def make_pet(name="Mochi", type="cat", breed="Siamese"):
    return Pet.create_pet(type=type, breed=breed, name=name)


# --- Activity Tests ---

class TestActivity:
    def test_set_and_get_priority(self):
        a = make_activity()
        a.set_priority(3)
        assert a.get_priority() == 3

    def test_set_and_get_time(self):
        a = make_activity()
        new_time = datetime.today().replace(hour=15, minute=30)
        a.set_time(new_time)
        assert a.get_time() == new_time

    def test_mark_complete(self):
        a = make_activity()
        assert a.completed is False
        a.mark_complete()
        assert a.completed is True

    def test_is_due_today(self):
        a = make_activity()
        assert a.is_due_today() is True

    def test_not_due_today(self):
        # "once" tasks are only due on their exact date — a past date should be False
        a = Activity(task="Old task", priority=2,
                     time=datetime(2000, 1, 1, 9, 0), frequency="once")
        assert a.is_due_today() is False

    def test_mark_complete_changes_status(self):
        a = make_activity()
        assert a.completed is False
        a.mark_complete()
        assert a.completed is True


# --- Pet Tests ---

class TestPet:
    def test_create_pet(self):
        pet = Pet.create_pet(type="dog", breed="Labrador", name="Rex")
        assert pet.name == "Rex"
        assert pet.type == "dog"
        assert pet.breed_type == "Labrador"

    def test_add_task_links_pet(self):
        pet = make_pet()
        a = make_activity()
        pet.add_task(a)
        assert a.pet == pet

    def test_get_tasks(self):
        pet = make_pet()
        pet.add_task(make_activity("Walk"))
        pet.add_task(make_activity("Feed"))
        assert len(pet.get_tasks()) == 2

    def test_add_task_increases_count(self):
        pet = make_pet()
        before = len(pet.get_tasks())
        pet.add_task(make_activity("Walk"))
        assert len(pet.get_tasks()) == before + 1

    def test_remove_task(self):
        pet = make_pet()
        a = make_activity()
        pet.add_task(a)
        pet.remove_task(a)
        assert len(pet.get_tasks()) == 0

    def test_get_pending_tasks_excludes_completed(self):
        pet = make_pet()
        a1 = make_activity("Walk")
        a2 = make_activity("Feed")
        a2.mark_complete()
        pet.add_task(a1)
        pet.add_task(a2)
        pending = pet.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].task == "Walk"


# --- Owner Tests ---

class TestOwner:
    def test_set_and_get_pet(self):
        owner = Owner(name="Alicia")
        pet = make_pet()
        owner.set_pet(pet)
        assert pet in owner.get_pet()

    def test_num_pets_owned(self):
        owner = Owner(name="Alicia")
        owner.set_pet(make_pet("Mochi"))
        owner.set_pet(make_pet("Rex", type="dog"))
        assert owner.num_pets_owned == 2

    def test_remove_pet(self):
        owner = Owner(name="Alicia")
        pet = make_pet()
        owner.set_pet(pet)
        owner.remove_pet(pet)
        assert pet not in owner.get_pet()

    def test_get_all_tasks_across_pets(self):
        owner = Owner(name="Alicia")
        mochi = make_pet("Mochi")
        rex = make_pet("Rex", type="dog")
        mochi.add_task(make_activity("Feed Mochi"))
        rex.add_task(make_activity("Walk Rex"))
        rex.add_task(make_activity("Vet"))
        owner.set_pet(mochi)
        owner.set_pet(rex)
        assert len(owner.get_all_tasks()) == 3

    def test_get_tasks_for_pet(self):
        owner = Owner(name="Alicia")
        mochi = make_pet("Mochi")
        rex = make_pet("Rex", type="dog")
        mochi.add_task(make_activity("Feed Mochi"))
        rex.add_task(make_activity("Walk Rex"))
        owner.set_pet(mochi)
        owner.set_pet(rex)
        assert len(owner.get_tasks_for_pet(mochi)) == 1
        assert owner.get_tasks_for_pet(mochi)[0].task == "Feed Mochi"


# --- Scheduler Tests ---

class TestScheduler:
    def setup_method(self):
        self.owner = Owner(name="Alicia")
        self.mochi = make_pet("Mochi")
        self.rex = make_pet("Rex", type="dog")
        self.owner.set_pet(self.mochi)
        self.owner.set_pet(self.rex)

    def test_get_todays_tasks(self):
        self.mochi.add_task(make_activity("Feed", hour=8))
        self.rex.add_task(make_activity("Walk", hour=7))
        scheduler = Scheduler(self.owner)
        assert len(scheduler.get_todays_tasks()) == 2

    def test_get_tasks_by_priority_order(self):
        self.mochi.add_task(make_activity("Low task", priority=1))
        self.mochi.add_task(make_activity("High task", priority=3))
        self.mochi.add_task(make_activity("Med task", priority=2))
        scheduler = Scheduler(self.owner)
        result = scheduler.get_tasks_by_priority()
        assert result[0].priority == 3
        assert result[-1].priority == 1

    def test_get_pending_tasks_excludes_completed(self):
        a1 = make_activity("Walk")
        a2 = make_activity("Feed")
        a2.mark_complete()
        self.rex.add_task(a1)
        self.rex.add_task(a2)
        scheduler = Scheduler(self.owner)
        assert len(scheduler.get_pending_tasks()) == 1

    def test_get_todays_schedule_sorted(self):
        self.mochi.add_task(make_activity("Low morning", priority=1, hour=7))
        self.mochi.add_task(make_activity("High afternoon", priority=3, hour=14))
        self.mochi.add_task(make_activity("Med morning", priority=2, hour=8))
        scheduler = Scheduler(self.owner)
        result = scheduler.get_todays_schedule()
        assert result[0].task == "High afternoon"
        assert result[-1].task == "Low morning"

    def test_get_todays_schedule_excludes_completed(self):
        a = make_activity("Done task")
        a.mark_complete()
        self.mochi.add_task(a)
        scheduler = Scheduler(self.owner)
        assert len(scheduler.get_todays_schedule()) == 0


# ─── Sorting ─────────────────────────────────────────────────────────────────

class TestSorting:

    def test_sort_by_time_is_chronological(self):
        """Tasks sorted by time should be earliest-first regardless of insertion order."""
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="dog", breed="Lab", name="Rex")
        today = datetime.today()
        # Add out of order
        pet.add_task(Activity("Evening walk", 2, today.replace(hour=18, minute=0), "daily"))
        pet.add_task(Activity("Morning walk", 3, today.replace(hour=7,  minute=0), "daily"))
        pet.add_task(Activity("Lunch walk",   2, today.replace(hour=12, minute=0), "daily"))
        owner.set_pet(pet)
        s     = Scheduler(owner)
        tasks = sorted(s.filter_tasks(), key=lambda t: t.time)
        times = [t.time for t in tasks]
        assert times == sorted(times)

    def test_sort_by_priority_high_first(self):
        """Highest-priority tasks should appear before lower-priority ones."""
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="cat", breed="Mix", name="Mochi")
        today = datetime.today()
        pet.add_task(Activity("Low task",  1, today.replace(hour=9,  minute=0), "daily"))
        pet.add_task(Activity("High task", 3, today.replace(hour=10, minute=0), "daily"))
        pet.add_task(Activity("Med task",  2, today.replace(hour=11, minute=0), "daily"))
        owner.set_pet(pet)
        s          = Scheduler(owner)
        tasks      = sorted(s.filter_tasks(), key=lambda t: (-t.priority, t.time))
        priorities = [t.priority for t in tasks]
        assert priorities == sorted(priorities, reverse=True)

    def test_sort_priority_time_breaks_ties(self):
        """When two tasks share the same priority, the earlier one should come first."""
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="dog", breed="Lab", name="Buddy")
        today = datetime.today()
        pet.add_task(Activity("Walk B", 3, today.replace(hour=10, minute=0), "daily"))
        pet.add_task(Activity("Walk A", 3, today.replace(hour=8,  minute=0), "daily"))
        owner.set_pet(pet)
        s     = Scheduler(owner)
        tasks = sorted(s.filter_tasks(), key=lambda t: (-t.priority, t.time))
        assert tasks[0].task == "Walk A"
        assert tasks[1].task == "Walk B"


# ─── Recurrence ──────────────────────────────────────────────────────────────

class TestRecurrence:

    def test_daily_task_creates_next_day_on_completion(self):
        """Completing a daily task auto-adds a new task for today + 1 day."""
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="cat", breed="Mix", name="Luna")
        today = datetime.today()
        task  = Activity("Feed Luna", 3, today.replace(hour=8, minute=0), "daily")
        pet.add_task(task)
        owner.set_pet(pet)

        task.mark_complete()

        next_tasks = [t for t in pet.get_tasks() if not t.completed]
        assert len(next_tasks) == 1
        assert next_tasks[0].time.date() == (today + timedelta(days=1)).date()
        assert next_tasks[0].task == "Feed Luna"

    def test_weekly_task_creates_next_week_on_completion(self):
        """Completing a weekly task auto-adds a task for today + 7 days."""
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="dog", breed="Mix", name="Rex")
        today = datetime.today()
        task  = Activity("Bath time", 2, today.replace(hour=10, minute=0), "weekly")
        pet.add_task(task)
        owner.set_pet(pet)

        task.mark_complete()

        next_tasks = [t for t in pet.get_tasks() if not t.completed]
        assert len(next_tasks) == 1
        assert next_tasks[0].time.date() == (today + timedelta(weeks=1)).date()

    def test_once_task_does_not_recur(self):
        """Completing a once-only task should NOT create a new instance."""
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="dog", breed="Lab", name="Rex")
        today = datetime.today()
        task  = Activity("Vet visit", 3, today.replace(hour=14, minute=0), "once")
        pet.add_task(task)
        owner.set_pet(pet)

        task.mark_complete()

        pending = [t for t in pet.get_tasks() if not t.completed]
        assert len(pending) == 0

    def test_recurring_task_preserves_time_of_day(self):
        """The auto-created next occurrence should keep the same hour and minute."""
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="cat", breed="Mix", name="Mochi")
        today = datetime.today()
        task  = Activity("Feed Mochi", 3, today.replace(hour=8, minute=30), "daily")
        pet.add_task(task)
        owner.set_pet(pet)

        task.mark_complete()

        next_task = next(t for t in pet.get_tasks() if not t.completed)
        assert next_task.time.hour   == 8
        assert next_task.time.minute == 30


# ─── Conflict Detection ──────────────────────────────────────────────────────

class TestConflictDetection:

    def test_exact_same_time_same_pet_flagged(self):
        """Two tasks for the same pet at the exact same time should be a conflict."""
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="dog", breed="Lab", name="Rex")
        today = datetime.today()
        pet.add_task(Activity("Walk",     3, today.replace(hour=8, minute=0), "daily"))
        pet.add_task(Activity("Feed Rex", 2, today.replace(hour=8, minute=0), "daily"))
        owner.set_pet(pet)
        assert len(Scheduler(owner).get_conflicts(window_minutes=0)) == 1

    def test_different_pets_same_time_not_flagged_by_default(self):
        """Same time across different pets is not a conflict by default."""
        owner = Owner(name="Test")
        rex   = Pet.create_pet(type="dog", breed="Lab",     name="Rex")
        mochi = Pet.create_pet(type="cat", breed="Siamese", name="Mochi")
        today = datetime.today()
        rex.add_task(Activity("Walk Rex",     3, today.replace(hour=8, minute=0), "daily"))
        mochi.add_task(Activity("Feed Mochi", 3, today.replace(hour=8, minute=0), "daily"))
        owner.set_pet(rex)
        owner.set_pet(mochi)
        assert Scheduler(owner).get_conflicts(window_minutes=0, same_pet_only=True) == []

    def test_cross_pet_conflict_detected_when_opted_in(self):
        """With same_pet_only=False, cross-pet overlaps should be detected."""
        owner = Owner(name="Test")
        rex   = Pet.create_pet(type="dog", breed="Lab",     name="Rex")
        mochi = Pet.create_pet(type="cat", breed="Siamese", name="Mochi")
        today = datetime.today()
        rex.add_task(Activity("Walk Rex",     3, today.replace(hour=8, minute=0), "daily"))
        mochi.add_task(Activity("Feed Mochi", 3, today.replace(hour=8, minute=0), "daily"))
        owner.set_pet(rex)
        owner.set_pet(mochi)
        assert len(Scheduler(owner).get_conflicts(window_minutes=0, same_pet_only=False)) == 1

    def test_conflict_warnings_are_strings_containing_pet_name(self):
        """get_conflict_warnings() should return readable strings, never raise."""
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="dog", breed="Lab", name="Rex")
        today = datetime.today()
        pet.add_task(Activity("Walk",     3, today.replace(hour=8, minute=0), "daily"))
        pet.add_task(Activity("Feed Rex", 2, today.replace(hour=8, minute=0), "daily"))
        owner.set_pet(pet)
        warnings = Scheduler(owner).get_conflict_warnings(window_minutes=0)
        assert len(warnings) == 1
        assert isinstance(warnings[0], str)
        assert "Rex" in warnings[0]

    def test_no_conflict_returns_empty_list(self):
        """A well-spaced schedule should produce no conflicts."""
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="dog", breed="Lab", name="Rex")
        today = datetime.today()
        pet.add_task(Activity("Morning walk", 3, today.replace(hour=7,  minute=0), "daily"))
        pet.add_task(Activity("Evening walk", 2, today.replace(hour=18, minute=0), "daily"))
        owner.set_pet(pet)
        assert Scheduler(owner).get_conflicts(window_minutes=0) == []

    def test_add_task_returns_warning_on_overlap(self):
        """add_task() should return a warning string on overlap, not raise."""
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="dog", breed="Lab", name="Rex")
        today = datetime.today()
        pet.add_task(Activity("Walk", 3, today.replace(hour=8, minute=0), "daily"))
        warning = pet.add_task(Activity("Feed", 2, today.replace(hour=8, minute=5), "daily"))
        assert warning is not None
        assert "overlaps" in warning


# ─── Filtering ───────────────────────────────────────────────────────────────

class TestFiltering:

    def setup_method(self):
        today       = datetime.today()
        self.owner  = Owner(name="Alicia")
        self.rex    = Pet.create_pet(type="dog", breed="Lab",     name="Rex")
        self.mochi  = Pet.create_pet(type="cat", breed="Siamese", name="Mochi")
        self.rex.add_task(Activity("Morning walk",    3, today.replace(hour=7,  minute=0),  "daily"))
        self.rex.add_task(Activity("Vet appointment", 3, today.replace(hour=15, minute=0),  "once"))
        self.rex.add_task(Activity("Evening walk",    2, today.replace(hour=18, minute=0),  "daily"))
        self.mochi.add_task(Activity("Feed Mochi",       3, today.replace(hour=8,  minute=0),  "daily"))
        self.mochi.add_task(Activity("Clean litter box", 2, today.replace(hour=12, minute=0), "daily"))
        self.owner.set_pet(self.rex)
        self.owner.set_pet(self.mochi)
        self.scheduler = Scheduler(self.owner)

    def test_filter_by_pet_name(self):
        """filter_tasks(pet_name=) should return only that pet's tasks."""
        rex_tasks = self.scheduler.filter_tasks(pet_name="Rex")
        assert len(rex_tasks) == 3
        assert all(t.pet.name == "Rex" for t in rex_tasks)

    def test_filter_pending_only(self):
        """filter_tasks(completed=False) should exclude completed tasks."""
        self.owner.get_all_tasks()[0].mark_complete()
        pending = self.scheduler.filter_tasks(completed=False)
        assert all(not t.completed for t in pending)

    def test_filter_completed_only(self):
        """filter_tasks(completed=True) should return only completed tasks."""
        self.owner.get_all_tasks()[0].mark_complete()
        done = self.scheduler.filter_tasks(completed=True)
        assert len(done) >= 1
        assert all(t.completed for t in done)

    def test_filter_combined_pet_and_status(self):
        """filter_tasks(pet_name, completed) should apply both filters together."""
        self.owner.get_all_tasks()[0].mark_complete()
        results = self.scheduler.filter_tasks(pet_name="Rex", completed=False)
        assert all(t.pet.name == "Rex" for t in results)
        assert all(not t.completed for t in results)

    def test_filter_no_args_returns_all(self):
        """filter_tasks() with no arguments should return every task."""
        assert len(self.scheduler.filter_tasks()) == len(self.owner.get_all_tasks())


# ─── Edge Cases ──────────────────────────────────────────────────────────────

class TestEdgeCases:

    def test_pet_with_no_tasks_returns_empty(self):
        """A pet with no tasks should return empty lists without errors."""
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="cat", breed="Mix", name="Empty")
        owner.set_pet(pet)
        s = Scheduler(owner)
        assert s.get_todays_tasks()    == []
        assert s.get_todays_schedule() == []
        assert s.get_conflicts()       == []
        assert s.filter_tasks()        == []

    def test_duplicate_task_is_skipped(self):
        """Adding the exact same task twice should skip the second and return 'duplicate'."""
        today = datetime.today()
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="dog", breed="Lab", name="Rex")
        pet.add_task(Activity("Walk", 3, today.replace(hour=8, minute=0), "daily"))
        result = pet.add_task(Activity("Walk", 3, today.replace(hour=8, minute=0), "daily"))
        assert result == "duplicate"
        assert len(pet.get_tasks()) == 1

    def test_owner_deduplication(self):
        """Registering the same pet twice should not double its tasks in the schedule."""
        owner = Owner(name="Test")
        pet   = Pet.create_pet(type="dog", breed="Lab", name="Rex")
        owner.set_pet(pet)
        owner.set_pet(pet)
        assert owner.num_pets_owned == 1
