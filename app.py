from ai_helper import run_pawpal_agent

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ---------------------
# Initialize Owner
# ---------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        available_time=240,
        preferences={}
    )
owner = st.session_state.owner

# ---------------------
# Welcome & Scenario
# ---------------------
st.markdown(
    """
Welcome to **PawPal+** — your AI-powered pet care planning assistant!
Add your pets, schedule their daily tasks, and ask our RAG-powered AI for expert advice.
"""
)

with st.expander("ℹ️ About PawPal+", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant that helps you:
- 🐾 Manage tasks for one or more pets
- 🗓️ Generate conflict-aware daily schedules
- 🤖 Get AI-powered advice using Retrieval-Augmented Generation (RAG)
"""
    )

st.divider()

# ---------------------
# Add Pet & Tasks
# ---------------------
st.subheader("🐶 Add a Pet & Tasks")
owner_name = st.text_input("Owner name", value=owner.name)

# Show existing pets so user knows what names are already registered
if owner.pets:
    st.caption("**Existing pets:** " + " | ".join(f"🐾 {p.name} ({p.type})" for p in owner.pets))
    st.caption("Type an existing pet's name below to add tasks to them, or type a new name to create a new pet.")

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a task. This feeds directly into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)

task_time = st.text_input("Scheduled time (HH:MM)", value="08:00")

if st.button("➕ Add task"):
    # Validate time format
    try:
        h, m = task_time.split(":")
        assert 0 <= int(h) <= 23 and 0 <= int(m) <= 59
    except Exception:
        st.error("Please enter a valid time in HH:MM format (e.g. 08:30)")
        st.stop()

    # Find existing pet by name, or create a new one
    existing = [p for p in owner.pets if p.name.lower() == pet_name.lower()]
    if existing:
        new_pet = existing[0]
    else:
        new_pet = Pet(name=pet_name, type=species, age=1)
        owner.add_pet(new_pet)
        st.info(f"🐾 New pet '{new_pet.name}' added!")

    new_task = Task(
        name=task_title,
        duration=int(duration),
        priority=priority.upper(),
        frequency=frequency,
        pet=new_pet,
        time=task_time,
    )
    new_pet.add_task(new_task)
    st.success(f"✅ Added task '{new_task.name}' to pet '{new_pet.name}' at {task_time} ({frequency})")

# ---------------------
# Display current pets & tasks
# ---------------------
st.subheader("📋 Current Pets & Tasks")
if not owner.pets:
    st.info("No pets added yet. Use the form above to get started!")
else:
    for pet in owner.pets:
        st.write(f"**{pet.name} ({pet.type})**")
        for t in pet.get_tasks():
            st.write(
                f"- {t.name} ({t.priority}) — {t.duration} mins | "
                f"Time: {t.time or 'N/A'} | "
                f"Completed: {t.completed} | "
                f"Frequency: {t.frequency} | "
                f"Next Due: {t.due_date if t.due_date else 'N/A'}"
            )

st.divider()

# ---------------------
# Generate Schedule
# ---------------------
st.subheader("🗓️ Build Schedule")
st.caption("Generate your daily schedule and check for conflicts.")

if st.button("⚡ Generate schedule"):
    if not owner.pets:
        st.warning("Add a pet first!")
    else:
        scheduler = Scheduler(owner=owner)
        st.session_state.schedule = scheduler.generate_schedule()
        st.session_state.scheduler = scheduler

if "schedule" in st.session_state and st.session_state.schedule:
    st.markdown("### Today's Schedule")
    for i, t in enumerate(st.session_state.schedule):
        col_check, col_info = st.columns([1, 6])
        with col_check:
            checked = st.checkbox(
                "Done",
                value=t.completed,
                key=f"task_complete_{i}"
            )
            if checked and not t.completed:
                t.mark_complete()
                st.success(f"✅ '{t.name}' marked complete!")
                st.rerun()
        with col_info:
            status = "~~" if t.completed else ""
            st.markdown(
                f"{status}**{t.name}** — {t.pet.name if t.pet else 'Unknown'} "
                f"| {t.priority} | {t.duration} min | {t.time or 'N/A'}{status}"
            )

    conflicts = st.session_state.scheduler.detect_conflicts()
    if conflicts:
        st.warning("⚠️ Conflicts detected!")
        for t1, t2 in conflicts:
            st.warning(f"'{t1.name}' overlaps with '{t2.name}' for {t1.pet.name}")
    else:
        st.success("No conflicts detected! ✅")

# ---------------------
# Real-time Conflict Checker
# ---------------------
with st.expander("🔍 Check for conflicts (real-time)"):
    if owner.pets:
        scheduler = Scheduler(owner)
        scheduler.generate_schedule()
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for t1, t2 in conflicts:
                st.warning(
                    f"Conflict: '{t1.name}' ({t1.pet.name}) overlaps with "
                    f"'{t2.name}' ({t2.pet.name})"
                )
        else:
            st.success("No conflicts detected!")
    else:
        st.info("Add pets and tasks first.")

st.divider()

# ---------------------
# Ask PawPal AI  (RAG-powered)
# ---------------------
st.subheader("🤖 Ask PawPal AI")
st.caption("Powered by Retrieval-Augmented Generation (RAG) — answers are grounded in our pet knowledge base.")

query = st.text_input("Ask a pet care question:", placeholder="e.g. How often should I walk my dog?")

if st.button("🔍 Get AI Advice"):
    if not query.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Retrieving knowledge and generating advice..."):
            answer, confidence, intent = run_pawpal_agent(query)

        st.markdown(answer)
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Detected Intent", intent.capitalize())
        with col_b:
            st.metric("Confidence Score", f"{confidence:.0%}")

        # Visual confidence bar
        if confidence >= 0.75:
            st.success(f"High confidence response ({confidence:.0%})")
        elif confidence >= 0.5:
            st.info(f"Moderate confidence ({confidence:.0%}) — consider verifying with a vet")
        else:
            st.warning(f"Low confidence ({confidence:.0%}) — please consult a veterinarian")
            