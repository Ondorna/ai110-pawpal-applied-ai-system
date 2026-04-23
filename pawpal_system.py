from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    task_id: str
    description: str
    time: str                  # "HH:MM"
    duration: int              # min
    priority: str              # "low" / "medium" / "high"
    frequency: str             # "once" / "daily" / "weekly"
    is_complete: bool = False
    due_date: Optional[str] = None       # "YYYY-MM-DD"

    def mark_complete(self):
        self.is_complete = True

    def reschedule(self, new_time: str):
        self.time = new_time


@dataclass
class Pet:
    name: str
    species: str               # "dog" / "cat" / "other"
    age: int
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, task_id: str):
        self.tasks = [task for task in self.tasks if task.task_id != task_id]

    def get_tasks(self):
        return self.tasks


@dataclass
class Owner:
    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet):
        self.pets.append(pet)

    def remove_pet(self, pet_name: str):
        self.pets = [pet for pet in self.pets if pet.name != pet_name]

    def get_pet_tasks(self, pet_name: Optional[str] = None):
        if pet_name is None:
            all_tasks = []
            for pet in self.pets:
                all_tasks.extend(pet.get_tasks())
            return all_tasks
        else:
            for pet in self.pets:
                if pet.name == pet_name:
                    return pet.get_tasks()
            return []

    def save_to_json(self, filepath: str):
        """
        Saves all owner, pet, and task data to a JSON file.
        """
        import json
        def task_to_dict(task):
            return {
                'task_id': task.task_id,
                'description': task.description,
                'time': task.time,
                'duration': task.duration,
                'priority': task.priority,
                'frequency': task.frequency,
                'is_complete': task.is_complete,
                'due_date': task.due_date
            }
        def pet_to_dict(pet):
            return {
                'name': pet.name,
                'species': pet.species,
                'age': pet.age,
                'tasks': [task_to_dict(t) for t in pet.tasks]
            }
        data = {
            'name': self.name,
            'pets': [pet_to_dict(p) for p in self.pets]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_from_json(filepath: str):
        """
        Loads owner, pet, and task data from a JSON file and restores the objects.
        Returns an Owner instance.
        """
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        owner = Owner(name=data['name'])
        for pet_data in data.get('pets', []):
            pet = Pet(
                name=pet_data['name'],
                species=pet_data['species'],
                age=pet_data['age']
            )
            for task_data in pet_data.get('tasks', []):
                task = Task(
                    task_id=task_data['task_id'],
                    description=task_data['description'],
                    time=task_data['time'],
                    duration=task_data['duration'],
                    priority=task_data['priority'],
                    frequency=task_data['frequency'],
                    is_complete=task_data.get('is_complete', False),
                    due_date=task_data.get('due_date')
                )
                pet.add_task(task)
            owner.add_pet(pet)
        return owner


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def get_daily_schedule(self):
        tasks = self.owner.get_pet_tasks()
        return self.sort_by_time(tasks)

    def sort_by_time(self, tasks=None):
        if tasks is None:
            tasks = self.owner.get_pet_tasks()
        return sorted(tasks, key=lambda t: t.time)

    def sort_by_priority(self, tasks=None):
        """
        Sort tasks by priority: high first, then medium, then low.
        """
        if tasks is None:
            tasks = self.owner.get_pet_tasks()
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        return sorted(tasks, key=lambda t: priority_order.get(t.priority, 3))

    def filter_tasks(self, pet_name: Optional[str] = None, is_complete: Optional[bool] = None):
        # Updated: filter by both pet_name and is_complete if provided
        tasks = self.owner.get_pet_tasks(pet_name)
        if is_complete is not None:
            tasks = [task for task in tasks if task.is_complete == is_complete]
        return tasks

    def detect_conflicts(self):
        # Returns warning messages for tasks scheduled at the same time
        tasks = self.owner.get_pet_tasks()
        time_map = {}
        conflicts = []
        for task in tasks:
            if task.time in time_map:
                conflicts.append(f"Conflict: '{task.description}' and '{time_map[task.time].description}' are both scheduled at {task.time}.")
            else:
                time_map[task.time] = task
        return conflicts

    def handle_recurring_tasks(self):
        # Handles recurring tasks using timedelta for daily/weekly frequencies
        from datetime import datetime, timedelta
        new_tasks = []
        today = datetime.now().date()
        for pet in self.owner.pets:
            for task in pet.get_tasks():
                if task.is_complete and task.frequency in ("daily", "weekly"):
                    if task.frequency == "daily":
                        next_due_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
                    else:
                        next_due_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")
                    new_task = Task(
                        task_id=task.task_id + "_recurring",
                        description=task.description,
                        time=task.time,
                        duration=task.duration,
                        priority=task.priority,
                        frequency=task.frequency,
                        is_complete=False,
                        due_date=next_due_date
                    )
                    new_tasks.append((pet, new_task))
        for pet, task in new_tasks:
            pet.add_task(task)
        return new_tasks

    def find_next_available_slot(self, duration: int) -> str:
        """
        Finds the next available time slot in the day that has no task scheduled, given a duration in minutes.
        Returns the start time as "HH:MM" string. Assumes the day starts at 06:00 and ends at 22:00.
        """
        from datetime import datetime, timedelta
        tasks = self.sort_by_time()
        day_start = datetime.strptime("06:00", "%H:%M")
        day_end = datetime.strptime("22:00", "%H:%M")
        # Build list of (start, end) for all tasks
        intervals = []
        for t in tasks:
            start = datetime.strptime(t.time, "%H:%M")
            end = start + timedelta(minutes=t.duration)
            intervals.append((start, end))
        # Check before first task
        current = day_start
        for start, end in intervals:
            if (start - current).total_seconds() / 60 >= duration:
                return current.strftime("%H:%M")
            current = max(current, end)
        # Check after last task
        if (day_end - current).total_seconds() / 60 >= duration:
            return current.strftime("%H:%M")
        return None

    def weighted_sort(self, tasks=None):
        """
        Sorts tasks by a weighted score combining priority and time.
        High priority = 3 points, medium = 2, low = 1. Earlier time = higher score.
        Returns tasks sorted by weighted score descending.
        """
        if tasks is None:
            tasks = self.owner.get_pet_tasks()
        priority_score = {'high': 3, 'medium': 2, 'low': 1}
        def score(t):
            # Earlier time = higher score, so subtract minutes from 1440 (max minutes in a day)
            h, m = map(int, t.time.split(":"))
            time_score = 1440 - (h * 60 + m)
            return priority_score.get(t.priority, 0) * 10000 + time_score
        return sorted(tasks, key=score, reverse=True)