from pawpal_system import Owner, Pet, Task, Scheduler

# Create an owner
owner = Owner("Alice", available_time=120, preferences={})

# Create two pets
dog = Pet("Buddy", "Dog", 5)
cat = Pet("Mittens", "Cat", 3)

# Link pets to the owner
owner.add_pet(dog)
owner.add_pet(cat)

# Add tasks to pets
dog.add_task(Task("Walk", 30, "HIGH", "daily", time="10:00"))
dog.add_task(Task("Feed", 15, "MEDIUM", "daily", time="08:00"))
cat.add_task(Task("Play", 45, "LOW", "daily", time="09:00"))
dog.add_task(Task("Vet Visit", 20, "HIGH", "daily", time="10:00"))

# Initialize scheduler with the owner
scheduler = Scheduler(owner)

# Generate today's schedule
scheduler.generate_schedule()

# Print a readable plan
print(scheduler.explain_plan())


# TEST sorting
scheduler.tasks_list = owner.get_all_tasks()
scheduler.sort_by_time()

print("\nSorted by time:")
for t in scheduler.tasks_list:
    print(t.time, t.name)

# TEST filtering
print("\nTasks for Buddy:")
for t in scheduler.filter_by_pet("Buddy"):
    print(t.name)

print("\nIncomplete tasks:")
for t in scheduler.filter_completed(False):
    print(t.name)

# TEST conflicts
conflicts = scheduler.detect_conflicts()
print("\nConflicts:")
for t1, t2 in conflicts:
    print(f"{t1.name} conflicts with {t2.name} at {t1.time}")