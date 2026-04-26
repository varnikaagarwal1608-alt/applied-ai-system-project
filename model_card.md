# Model Card — PawPal+

> Standardized reflection document covering AI collaboration, biases, and testing results.

---

## Project Identity

**Project name:** PawPal+  
**Base project:** PawPal (Modules 2) — a rule-based pet care scheduler  
**Extension:** Retrieval-Augmented Generation (RAG) AI advisor + automated test harness  
**Author:** Varnika Agarwal  
**Repository:** https://github.com/varnikaagarwal1608-alt/applied-ai-system-project

---

## Intended Use

PawPal+ is designed to help everyday pet owners manage their pet care routines and get grounded AI advice. It is intended for personal, non-medical use. It is **not** a substitute for professional veterinary care.

**Primary users:** Pet owners managing daily schedules for one or more pets  
**Out-of-scope uses:** Medical diagnosis, emergency triage, or professional veterinary guidance

---

## AI Feature: Retrieval-Augmented Generation (RAG)

The system uses a keyword-scored RAG pipeline implemented in `ai_helper.py`:

1. **Intent detection** — classifies the query into categories (emergency, feeding, exercise, health, grooming, etc.)
2. **Guardrail** — emergency queries bypass retrieval and return an immediate warning
3. **Retrieval** — searches `PET_KNOWLEDGE` (12 curated topics) by keyword overlap score
4. **Augmented response** — top-3 matching chunks are used to build the response; the answer is grounded in retrieved content, not generated freely
5. **Confidence scoring** — score computed from chunk count and keyword match strength (0.25–0.97)
6. **Logging** — every query is logged with timestamp, intent, confidence, and chunk count

This means the AI never answers from nothing — every response is traceable back to a specific knowledge source.

---

## Limitations and Biases

**Knowledge base bias:**  
The knowledge base was written manually and reflects general Western pet care norms. It covers dogs and cats primarily and may not apply to exotic pets, regional veterinary practices, or non-English-speaking contexts.

**Keyword matching limitations:**  
The retrieval system uses exact substring matching. It can miss synonyms (e.g., "pup" vs "puppy"), handle typos poorly, and occasionally mis-classify intent (e.g., "vaccinated" was classified as "general" instead of "health" because the keyword "vaccine" wasn't present in the query).

**Confidence scoring is heuristic:**  
Confidence is based on how many chunks were retrieved and their keyword scores — not calibrated against ground-truth labels. A high confidence score means strong keyword overlap, not factual correctness.

**No memory between sessions:**  
The system does not remember previous conversations or build a user profile over time.

---

## Misuse Potential and Prevention

| Risk | Mitigation |
|---|---|
| User relies on AI instead of a vet | Every response ends with a vet disclaimer |
| Emergency symptoms dismissed | Emergency guardrail fires immediately, bypassing retrieval |
| Low-confidence answer mistaken for fact | Confidence score displayed on every response with color-coded warning |
| Harmful advice on unknown topics | Unknown queries return 0.25 confidence and explicitly direct to a vet |

---

## Testing Results

Testing was conducted via an automated test harness (`test_pawpal.py`) and live manual testing in the Streamlit UI.

**Automated results:**

| Category | Tests | Result |
|---|---|---|
| RAG Retrieval | 5 | 5/5 passed |
| Intent Detection | 5 | 5/5 passed |
| Agent Pipeline | 8 | 8/8 passed |
| Scheduler | 6 | 6/6 passed |
| **Total** | **24** | **24/24 (100%)** |

**Confidence score summary:**
- Emergency queries: 0.97 (high — guardrail fires correctly)
- Well-matched queries: 0.65–0.80 (moderate — grounded responses)
- Unknown queries: 0.25 (low — correctly flags uncertainty)

**Bugs found and fixed during manual testing:**
1. `generate_schedule()` missing `return` statement — schedule always returned `None`
2. All tasks added to first pet only — fixed by name-based pet lookup
3. `detect_conflicts()` crashed on `None` times — fixed by filtering timed tasks only
4. Recurring tasks duplicated on every Streamlit rerun — fixed with existence check before adding
5. Same conflict appeared multiple times — fixed with identity-based deduplication

**What didn't work as expected:**  
The "General" intent was broader than expected. "My dog is not vaccinated" was classified as General instead of Health, because "vaccin" wasn't in the health intent keyword list. This is a known limitation of keyword-based intent detection.

---

## AI Collaboration

**How AI was used during development:**  
AI assistance was used throughout the project for structuring the RAG pipeline, writing the test harness, debugging Streamlit session state issues, and drafting documentation.

**One helpful suggestion:**  
When building the RAG pipeline, the suggestion to separate `retrieve_info`, `detect_intent`, and `compute_confidence` into three distinct functions made the code significantly easier to test individually. Each function could be unit-tested in isolation, which directly led to catching the intent classification bug.

**One flawed suggestion:**  
An early suggestion to use `re.findall` for keyword matching introduced false positives — for example, the word "play" would match inside "display", causing incorrect topic retrieval. Replacing it with simple `word in query_lower` substring matching resolved this cleanly.

---

## What This Project Taught Me

Building PawPal+ taught me that RAG doesn't require a vector database or external API to be meaningful — even a simple keyword-scored retrieval system produces noticeably better, more grounded answers than a free-form response. The biggest insight was how much the *structure* of the pipeline matters: separating retrieval, intent detection, and confidence scoring made the system testable, debuggable, and explainable in a way that a monolithic function never could have been.

I also learned that testing reveals assumptions. Several bugs only appeared during live use — things that looked correct in isolation (like `mark_complete()`) broke in the context of Streamlit's rerun model. Writing a test harness before finding those bugs would have caught them earlier.

---

## Future Improvements

- Replace keyword matching with semantic embeddings (e.g., sentence-transformers + FAISS) for better synonym handling
- Add multi-source retrieval — pull from uploaded documents or a vet FAQ database
- Persist owner/pet/task data across sessions using a lightweight database (SQLite)
- Add a feedback button so users can rate AI responses, enabling human evaluation over time
- Expand the knowledge base to cover more species and regional vet guidelines