import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import datetime
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
        a = make_activity()
        a.set_time(datetime(2000, 1, 1, 9, 0))
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
