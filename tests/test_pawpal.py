import pytest
from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import datetime, timedelta

def test_mark_complete_sets_true():
    task = Task(task_id="t1", description="Test", time="10:00", duration=10, priority="low", frequency="once")
    assert not task.is_complete
    task.mark_complete()
    assert task.is_complete

def test_add_task_increases_count():
    pet = Pet(name="Buddy", species="dog", age=4)
    initial_count = len(pet.tasks)
    task = Task(task_id="t2", description="Feed", time="08:00", duration=5, priority="medium", frequency="daily")
    pet.add_task(task)
    assert len(pet.tasks) == initial_count + 1

def test_sort_by_time_returns_chronological_order():
    pet = Pet(name="Buddy", species="dog", age=4)
    t1 = Task(task_id="t1", description="Breakfast", time="08:00", duration=10, priority="low", frequency="once")
    t2 = Task(task_id="t2", description="Walk", time="07:30", duration=30, priority="medium", frequency="once")
    t3 = Task(task_id="t3", description="Dinner", time="18:00", duration=10, priority="high", frequency="once")
    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)
    owner = Owner(name="Alice", pets=[pet])
    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()
    assert [t.description for t in sorted_tasks] == ["Walk", "Breakfast", "Dinner"]

def test_handle_recurring_tasks_creates_next_day_task():
    pet = Pet(name="Buddy", species="dog", age=4)
    today = datetime.now().date()
    task = Task(task_id="t1", description="Feed", time="08:00", duration=5, priority="medium", frequency="daily", is_complete=True, due_date=today.strftime("%Y-%m-%d"))
    pet.add_task(task)
    owner = Owner(name="Alice", pets=[pet])
    scheduler = Scheduler(owner)
    new_tasks = scheduler.handle_recurring_tasks()
    assert len(new_tasks) == 1
    new_task = new_tasks[0][1]
    expected_due_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    assert new_task.due_date == expected_due_date
    assert new_task.is_complete is False
    assert new_task.frequency == "daily"
    assert new_task.description == "Feed"

def test_detect_conflicts_flags_same_time():
    pet = Pet(name="Buddy", species="dog", age=4)
    t1 = Task(task_id="t1", description="Feed", time="09:00", duration=10, priority="high", frequency="once")
    t2 = Task(task_id="t2", description="Walk", time="09:00", duration=30, priority="medium", frequency="once")
    pet.add_task(t1)
    pet.add_task(t2)
    owner = Owner(name="Alice", pets=[pet])
    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert any("Feed" in c and "Walk" in c for c in conflicts)
