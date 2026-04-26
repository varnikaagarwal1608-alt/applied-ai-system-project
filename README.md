# 🐾 PawPal+

> An AI-powered pet care planning assistant with Retrieval-Augmented Generation (RAG)

---

## Original Project Summary

PawPal+ began as a rule-based pet care scheduler (Modules 1–3). The original system allowed a pet owner to register pets, define tasks with priority and frequency, and generate a conflict-aware daily schedule. It represented owners, pets, and tasks as Python dataclasses and used a priority-sort algorithm to fit tasks within the owner's available time.

---

## Title & Summary

**PawPal+** is a full-stack pet care planning assistant that combines:

- A **scheduling engine** that builds a daily task plan based on priority, duration, and available time
- A **conflict detector** that flags overlapping scheduled tasks
- A **RAG-powered AI advisor** that retrieves grounded, topic-specific pet care advice from a curated knowledge base

The system is designed for everyday pet owners who want one place to manage their pet's routine and get reliable AI guidance — without replacing a veterinarian.

---

## Architecture Overview

```
User Input (Streamlit UI)
        │
        ├──► Scheduler Pipeline
        │         │
        │    pawpal_system.py
        │    Owner → Pets → Tasks
        │         │
        │    Scheduler.generate_schedule()
        │    Scheduler.detect_conflicts()
        │         │
        │    Schedule Table + Conflict Warnings
        │
        └──► RAG AI Pipeline (ai_helper.py)
                  │
             detect_intent(query)
                  │
            [emergency?] ──► Guardrail response (skip retrieval)
                  │
             retrieve_info(query)        ← keyword-scored retrieval
             (searches PET_KNOWLEDGE)
                  │
             top-3 chunks selected
                  │
             response = grounded answer  ← augmented with retrieved context
             confidence = f(chunks, score)
                  │
             Response + Intent + Confidence → UI
```

**Components:**

| File | Role |
|---|---|
| `app.py` | Streamlit UI — user-facing interface |
| `pawpal_system.py` | Data models: Owner, Pet, Task, Scheduler |
| `ai_helper.py` | RAG engine: retrieval, intent detection, confidence scoring, logging |
| `test_pawpal.py` | Automated test harness (24 tests across all components) |

**Data flow:** User inputs a query → intent is detected → knowledge base is searched → top matching chunks are retrieved → response is built from retrieved context → confidence is computed and displayed.

---

## Setup Instructions

### Requirements

- Python 3.10+
- pip

### Install dependencies

```bash
pip install streamlit
```

### Run the app

```bash
streamlit run app.py
```

### Run the tests

```bash
python test_pawpal.py
```

No API keys required. All AI logic runs locally using the built-in knowledge base.

---

## Sample Interactions

### 1. Adding multiple pets

**Input:** Owner "Jordaiana" adds a dog named Mochi and a cat named Mocha, each with their own tasks (e.g., "Morning walk" for Mochi, "breakie" and "play" for Mocha).

**Output (Current Pets & Tasks section):**
```
Mochi (dog)
- Morning walk (HIGH) — 20 mins | Time: 08:00 | Completed: False | Frequency: once

Mocha (cat)
- breakie (HIGH) — 20 mins | Time: 08:00 | Completed: False | Frequency: daily
- play (MEDIUM) — 30 mins | Time: 10:00 | Completed: False | Frequency: daily
```

---

### 2. Schedule generation with mark-complete checkboxes

**Input:** Owner clicks **Generate schedule** after adding tasks for both pets.

**Output:**
```
Today's Schedule
☑ Done  ~~Morning walk — Mochi | HIGH | 20 min | 08:00~~   ← checked = completed
☑ Done  ~~breakie — Mocha | HIGH | 20 min | 08:00~~        ← checked = completed
☐ Done  play — Mocha | MEDIUM | 30 min | 10:00             ← unchecked = pending

⚠️ Conflicts detected!
'Morning walk' (Mochi) overlaps with 'breakie' (Mocha)
```
Tasks marked complete show with strikethrough. The scheduler respects the owner's available time (240 min default) and sorts by priority (HIGH first).

---

### 3. RAG AI Advisor — vaccination query

**Input:** "My dog is not vaccinated"

**Output:**
```
🐾 PawPal AI Advice (based on 1 knowledge source(s))

📌 [Vaccination]
Core vaccines for dogs include rabies, distemper, and parvovirus.
Core vaccines for cats include rabies and FVRCP.
Booster schedules vary — your vet will set a reminder. Keep records up to date.

⚠️ Always consult a licensed veterinarian for medical decisions.

Detected Intent: General    Confidence Score: 70%
ℹ️ Moderate confidence (70%) — consider verifying with a vet
```

---

### 4. RAG AI Advisor — emergency guardrail

**Input:** "My dog collapsed and won't respond"

**Output:**
```
⚠️ Emergency Detected

Please contact a veterinarian or emergency animal clinic immediately.
Do not wait — time-sensitive symptoms can be life-threatening.

🔴 Signs requiring urgent care: collapse, seizures, difficulty breathing,
pale/white gums, heavy bleeding, or complete refusal to eat for 24+ hours.

Detected Intent: Emergency    Confidence Score: 97%
```

---

### 5. Low-confidence / unknown query

**Input:** "What's the best Netflix show for pets?"

**Output:**
```
🐾 I don't have specific information on that topic in my knowledge base.

For the best advice, please consult a licensed veterinarian.
You can also try rephrasing your question — e.g., mention the species, symptom, or task.

Detected Intent: General    Confidence Score: 25%
⚠️ Low confidence — please consult a veterinarian
```

---

## Design Decisions

**Why keyword-based RAG instead of embedding/vector search?**
The knowledge base is small (12 curated topics) and covers well-defined pet care domains. Keyword overlap scoring is transparent, fast, and requires no external API or vector database. For a larger knowledge base, replacing `retrieve_info` with a vector store (e.g., FAISS + sentence-transformers) would be a natural next step.

**Why a guardrail for emergencies?**
Emergency situations require immediate action, not a retrieval delay. Bypassing the RAG pipeline for emergency intent ensures the user gets an urgent, unambiguous response every time — regardless of what the knowledge base contains.

**Trade-offs:**
- Keyword matching can miss synonyms (e.g., "pup" vs. "puppy"). A semantic embedding model would handle this better.
- Confidence scoring is heuristic (based on chunk count and keyword score), not calibrated against ground-truth labels. A labeled evaluation set would improve this.
- The scheduler uses a greedy priority-sort algorithm, which is optimal for independent tasks but doesn't handle dependencies (e.g., "bath before vet visit").

---

## Testing Summary

Testing was conducted in two ways: a `test_pawpal.py` automated test harness (run with `python test_pawpal.py`) and live manual testing in the Streamlit UI.

**Automated test harness covers 24 checks across 4 categories:**

| Category | Tests | What's Checked |
|---|---|---|
| RAG Retrieval | 5 | Keyword match, multi-chunk results, empty/unknown query |
| Intent Detection | 5 | Emergency, feeding, exercise, grooming, general |
| Agent Pipeline | 8 | Full response tuple, emergency guardrail, low confidence fallback, health query |
| Scheduler | 6 | Schedule generation, time budget constraint, priority ordering, conflict detection |

To run the tests yourself:
```bash
python test_pawpal.py
```

**Actual test output:**
```
── RAG Retrieval Tests ──
  ✅ PASS  Dog exercise retrieval  (top topic = dog_exercise)
  ✅ PASS  Feeding + emergency retrieval  (1 chunk(s) returned)
  ✅ PASS  Dental care retrieval  (top topic = grooming_care)
  ✅ PASS  No match returns empty list  (0 chunk(s))
  ✅ PASS  Parasite retrieval  (top topic = parasite_prevention)

── Intent Detection Tests ──
  ✅ PASS  Emergency intent
  ✅ PASS  Feeding intent
  ✅ PASS  Exercise intent
  ✅ PASS  Grooming intent
  ✅ PASS  General intent

── Agent Pipeline Tests ──
  ✅ PASS  Normal query returns 3-tuple
  ✅ PASS  Normal query confidence >= 0.5  (confidence=0.80)
  ✅ PASS  Normal query has content
  ✅ PASS  Emergency intent detected
  ✅ PASS  Emergency confidence >= 0.9  (confidence=0.97)
  ✅ PASS  Emergency response warns user
  ✅ PASS  Unknown query confidence <= 0.4  (confidence=0.25)
  ✅ PASS  Health query retrieves info
  ✅ PASS  Health answer mentions vet

── Scheduler Tests ──
  ✅ PASS  Schedule generated (not None)
  ✅ PASS  Schedule respects available time  (total=90 min / 120 available)
  ✅ PASS  HIGH priority task included
  ✅ PASS  Conflict detected between Walk & Play  (1 conflict(s) found)
  ✅ PASS  No false-positive conflicts

════════════════════════════════════════════════
  Results: 24/24 tests passed  (100%)
  🎉 All tests passed!
════════════════════════════════════════════════
```

**Bugs found and fixed during live manual testing:**

1. `generate_schedule()` had no `return` statement — schedule always came back `None` and nothing displayed. Fixed by adding `return self.daily_plan`.
2. All tasks were added to the first pet regardless of the name typed in the UI. Fixed by looking up pets by name before creating a new one.
3. `detect_conflicts()` crashed when `task.time` was `None`. Fixed by filtering to only timed tasks before running overlap checks.
4. Recurring tasks multiplied on every Streamlit rerun because `mark_complete()` added a new task each time. Fixed by checking if the next occurrence already exists before adding it.
5. The same conflict appeared multiple times because duplicate task objects were being compared. Fixed by deduplicating the task list by object identity before running conflict checks.

**What worked well:** The RAG intent detection correctly classified emergency queries and fired the guardrail every time. Confidence scoring was directionally accurate — high for well-matched multi-chunk queries, low for unknown topics. The scheduler correctly prioritized HIGH tasks and respected the available time budget.

**What didn't work as expected:** The "General" intent was broader than expected — "My dog is not vaccinated" was classified as General instead of Health, because "vaccin" keywords weren't in the health intent map. This is a known limitation of keyword-based intent detection.

---

## Reflection & Ethics

**Limitations and biases:**
The knowledge base was written manually and reflects general Western pet care norms. It may not cover all breeds, regional vet practices, or non-English-speaking contexts. Keyword matching can fail on phrasing variations or typos.

**Misuse potential:**
A user could rely on the AI instead of seeking real veterinary care. The system mitigates this by: (a) always appending a vet disclaimer, (b) firing a guardrail for emergency intent, and (c) displaying low confidence scores when knowledge is insufficient.

**What surprised me during testing:**
The confidence scoring worked well directionally — emergencies scored highest (0.97), well-matched queries scored mid-range (0.65–0.80), and unknown queries correctly scored low (0.25). I was surprised how often multi-keyword queries retrieved 2–3 relevant chunks, which boosted both the confidence and the response quality noticeably.

**Collaboration with AI:**
One instance where AI gave a helpful suggestion: when structuring the RAG pipeline, the suggestion to separate `retrieve_info`, `detect_intent`, and `compute_confidence` into distinct functions made the code far easier to test individually. One instance where AI's suggestion was flawed: an early suggestion to use `re.findall` for keyword matching introduced false positives (e.g., "play" matching "display"). Replacing it with exact substring matching on the lowercased query resolved this cleanly.

---

## File Structure

```
pawpal/
├── app.py              # Streamlit UI
├── ai_helper.py        # RAG engine (retrieval, intent, confidence, logging)
├── pawpal_system.py    # Data models: Owner, Pet, Task, Scheduler
├── test_pawpal.py      # Automated test harness
└── README.md           # This file
```