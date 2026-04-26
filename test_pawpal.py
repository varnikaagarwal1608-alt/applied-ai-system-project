"""
test_pawpal.py — PawPal+ Test Harness
======================================
Runs automated tests across:
  - RAG retrieval (retrieve_info)
  - Intent detection (detect_intent)
  - Full agent pipeline (run_pawpal_agent)
  - Scheduler logic (generate_schedule, detect_conflicts)

Usage:
    python test_pawpal.py

Prints a pass/fail summary with confidence scores where applicable.
"""

import sys
from ai_helper import retrieve_info, detect_intent, run_pawpal_agent
from pawpal_system import Owner, Pet, Task, Scheduler

PASS = "✅ PASS"
FAIL = "❌ FAIL"
results = []


def check(name: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    msg = f"  {status}  {name}"
    if detail:
        msg += f"  ({detail})"
    print(msg)
    results.append((name, condition))


# ────────────────────────────────────────────
# 1. RAG RETRIEVAL TESTS
# ────────────────────────────────────────────
print("\n── RAG Retrieval Tests ──")

retrieved = retrieve_info("how often should I walk my dog")
check(
    "Dog exercise retrieval",
    any("dog_exercise" == r["topic"] for r in retrieved),
    f"top topic = {retrieved[0]['topic'] if retrieved else 'none'}"
)

retrieved = retrieve_info("my puppy won't eat")
check(
    "Feeding + emergency retrieval",
    len(retrieved) >= 1,
    f"{len(retrieved)} chunk(s) returned"
)

retrieved = retrieve_info("how do I brush my cat's teeth")
check(
    "Dental care retrieval",
    any("dental_care" == r["topic"] for r in retrieved),
    f"top topic = {retrieved[0]['topic'] if retrieved else 'none'}"
)

retrieved = retrieve_info("xyzzy frobnicator")
check(
    "No match returns empty list",
    len(retrieved) == 0,
    f"{len(retrieved)} chunk(s)"
)

retrieved = retrieve_info("flea tick heartworm prevention")
check(
    "Parasite retrieval",
    any("parasite_prevention" == r["topic"] for r in retrieved),
    f"top topic = {retrieved[0]['topic'] if retrieved else 'none'}"
)


# ────────────────────────────────────────────
# 2. INTENT DETECTION TESTS
# ────────────────────────────────────────────
print("\n── Intent Detection Tests ──")

check("Emergency intent", detect_intent("my dog collapsed and won't respond") == "emergency")
check("Feeding intent",   detect_intent("what should I feed my puppy?") == "feeding")
check("Exercise intent",  detect_intent("how long should I walk my dog?") == "exercise")
check("Grooming intent",  detect_intent("how do I brush my cat's fur?") == "grooming")
check("General intent",   detect_intent("how do I take care of a fish") == "general")


# ────────────────────────────────────────────
# 3. FULL AGENT PIPELINE TESTS
# ────────────────────────────────────────────
print("\n── Agent Pipeline Tests ──")

# 3a. Normal query returns answer + confidence + intent
answer, conf, intent = run_pawpal_agent("how often should I walk my dog?")
check("Normal query returns 3-tuple",  isinstance(answer, str) and isinstance(conf, float) and isinstance(intent, str))
check("Normal query confidence >= 0.5", conf >= 0.5, f"confidence={conf:.2f}")
check("Normal query has content",       len(answer) > 20)

# 3b. Emergency guardrail fires
answer, conf, intent = run_pawpal_agent("my dog collapsed and is unresponsive")
check("Emergency intent detected",      intent == "emergency")
check("Emergency confidence >= 0.9",    conf >= 0.9, f"confidence={conf:.2f}")
check("Emergency response warns user",  "emergency" in answer.lower() or "vet" in answer.lower())

# 3c. Unknown query returns low confidence
answer, conf, intent = run_pawpal_agent("xyzzy frobnicator")
check("Unknown query confidence <= 0.4", conf <= 0.4, f"confidence={conf:.2f}")

# 3d. RAG grounding — answer should reference retrieved topic
answer, conf, intent = run_pawpal_agent("my cat keeps sneezing and has nasal discharge")
check("Health query retrieves info",     conf > 0.3)
check("Health answer mentions vet",      "vet" in answer.lower())


# ────────────────────────────────────────────
# 4. SCHEDULER TESTS
# ────────────────────────────────────────────
print("\n── Scheduler Tests ──")

owner = Owner("Test Owner", available_time=120, preferences={})
dog = Pet("Buddy", "Dog", 3)
owner.add_pet(dog)

t1 = Task("Walk",  30, "HIGH",   "daily", time="09:00", pet=dog)
t2 = Task("Feed",  15, "MEDIUM", "daily", time="08:00", pet=dog)
t3 = Task("Play",  45, "LOW",    "daily", time="09:15", pet=dog)  # conflicts with Walk
dog.add_task(t1)
dog.add_task(t2)
dog.add_task(t3)

scheduler = Scheduler(owner)
schedule = scheduler.generate_schedule()

check("Schedule generated (not None)", schedule is not None)
check(
    "Schedule respects available time",
    sum(t.duration for t in schedule) <= owner.available_time,
    f"total={sum(t.duration for t in schedule)} min / {owner.available_time} available"
)

# HIGH priority task should be in schedule
high_tasks = [t for t in schedule if t.priority == "HIGH"]
check("HIGH priority task included", len(high_tasks) >= 1)

# Conflict detection: test directly using detect_conflicts on known overlapping tasks
# Walk 09:00-09:30 vs Play 09:15-10:00 — force them into daily_plan directly
owner_c = Owner("Conflict Test", available_time=200, preferences={})
dog_c = Pet("Rex", "Dog", 2)
owner_c.add_pet(dog_c)
tc1 = Task("Walk", 30, "HIGH", "daily", time="09:00", pet=dog_c)
tc2 = Task("Play", 45, "LOW",  "daily", time="09:15", pet=dog_c)
dog_c.add_task(tc1)
dog_c.add_task(tc2)
sched_c = Scheduler(owner_c)
sched_c.generate_schedule()
conflicts = sched_c.detect_conflicts()
check("Conflict detected between Walk & Play", len(conflicts) >= 1,
      f"{len(conflicts)} conflict(s) found")

# No conflicts when times don't overlap
owner2 = Owner("Owner 2", available_time=120, preferences={})
dog2 = Pet("Rex", "Dog", 2)
owner2.add_pet(dog2)
ta = Task("Walk", 20, "HIGH",   "daily", time="08:00", pet=dog2)
tb = Task("Feed", 10, "MEDIUM", "daily", time="09:00", pet=dog2)
dog2.add_task(ta)
dog2.add_task(tb)
sched2 = Scheduler(owner2)
sched2.generate_schedule()
check("No false-positive conflicts", len(sched2.detect_conflicts()) == 0)


# ────────────────────────────────────────────
# SUMMARY
# ────────────────────────────────────────────
print("\n" + "═" * 48)
passed = sum(1 for _, ok in results if ok)
total  = len(results)
pct    = 100 * passed // total
print(f"  Results: {passed}/{total} tests passed  ({pct}%)")
if passed == total:
    print("  🎉 All tests passed!")
else:
    failed = [name for name, ok in results if not ok]
    print(f"  Failed tests: {', '.join(failed)}")
print("═" * 48)

sys.exit(0 if passed == total else 1)