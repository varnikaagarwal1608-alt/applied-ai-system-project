from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date, timedelta
from itertools import combinations


# -------------------- Task --------------------
@dataclass
class Task:
    def __init__(self, name, duration, priority, frequency, description="", pet=None, completed=False, time=None, due_date=None):
        self.name = name
        self.description = description
        self.duration = duration
        self.priority = priority
        self.frequency = frequency
        self.pet = pet
        self.completed = completed
        self.time = time
        self.due_date = due_date or date.today()

    def mark_complete(self):
        self.completed = True
        if self.frequency.lower() in ["daily", "weekly"] and self.pet:
            next_date = self.due_date + timedelta(days=1 if self.frequency.lower() == "daily" else 7)
            # Only add next occurrence if it doesn't already exist
            already_exists = any(
                t.name == self.name and t.due_date == next_date and not t.completed
                for t in self.pet.tasks
            )
            if not already_exists:
                new_task = Task(
                    name=self.name,
                    duration=self.duration,
                    priority=self.priority,
                    frequency=self.frequency,
                    pet=self.pet,
                    completed=False,
                    time=self.time,
                    due_date=next_date
                )
                self.pet.add_task(new_task)

    def update_task(self, name=None, duration=None, priority=None, frequency=None):
        if name: self.name = name
        if duration: self.duration = duration
        if priority: self.priority = priority
        if frequency: self.frequency = frequency

    def get_details(self):
        return f"{self.name} ({self.priority}) - {self.duration} mins, Completed: {self.completed}"

    def is_recurring(self):
        return self.frequency.lower() in ["daily", "weekly"]


# -------------------- Pet --------------------
@dataclass
class Pet:
    name: str
    type: str
    age: int
    special_needs: Optional[str] = None
    owner: Optional["Owner"] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        task.pet = self
        self.tasks.append(task)

    def get_tasks(self):
        return self.tasks

    def update_info(self, name=None, type=None, age=None, special_needs=None):
        if name: self.name = name
        if type: self.type = type
        if age: self.age = age
        if special_needs: self.special_needs = special_needs


# -------------------- Owner --------------------
class Owner:
    def __init__(self, name: str, available_time: int, preferences: dict):
        self.name = name
        self.available_time = available_time
        self.preferences = preferences
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet):
        pet.owner = self
        self.pets.append(pet)

    def update_preferences(self, preferences: dict):
        self.preferences = preferences

    def get_available_time(self):
        return self.available_time

    def get_all_tasks(self):
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks


# -------------------- Scheduler --------------------
class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.daily_plan: List[Task] = []

    def sort_tasks_by_priority(self, tasks: List[Task]):
        priority_map = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
        return sorted(tasks, key=lambda t: (priority_map.get(t.priority.upper(), 4), t.time or ""))

    def generate_schedule(self) -> List[Task]:
        """Generate the daily schedule respecting available time, return the plan."""
        tasks = self.sort_tasks_by_priority(self.owner.get_all_tasks())
        remaining_time = self.owner.get_available_time()
        self.daily_plan = []

        for task in tasks:
            if task.duration <= remaining_time:
                self.daily_plan.append(task)
                remaining_time -= task.duration

        return self.daily_plan  # FIX: was missing return statement

    def check_constraints(self):
        total_duration = sum(task.duration for task in self.daily_plan)
        return total_duration <= self.owner.get_available_time()

    def explain_plan(self):
        explanation = "Today's schedule:\n"
        for task in self.daily_plan:
            explanation += f"- {task.get_details()} for pet {task.pet.name}\n"
        return explanation

    def sort_by_time(self):
        self.tasks_list.sort(key=lambda t: t.time or "")

    def filter_by_pet(self, pet_name):
        return [t for t in self.tasks_list if t.pet and t.pet.name == pet_name]

    def filter_completed(self, completed=True):
        return [t for t in self.tasks_list if t.completed == completed]

    def detect_conflicts(self) -> List[tuple]:
        """Detect overlapping tasks. Skips tasks with no time set."""
        def time_to_minutes(t: str) -> int:
            h, m = map(int, t.split(":"))
            return h * 60 + m

        timed_tasks = [t for t in self.daily_plan if t.time]
        conflicts = []
        for i in range(len(timed_tasks)):
            for j in range(i + 1, len(timed_tasks)):
                t1 = timed_tasks[i]
                t2 = timed_tasks[j]
                try:
                    start1 = time_to_minutes(t1.time)
                    end1 = start1 + t1.duration
                    start2 = time_to_minutes(t2.time)
                    end2 = start2 + t2.duration
                    if start1 < end2 and start2 < end1:
                        conflicts.append((t1, t2))
                except Exception:
                    continue
        return conflicts