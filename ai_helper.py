"""
ai_helper.py — PawPal+ AI Engine
Uses Retrieval-Augmented Generation (RAG):
  1. Retrieve relevant knowledge chunks from PET_KNOWLEDGE
  2. Use retrieved context to build a grounded, specific response
  3. Log every query for traceability
"""

from datetime import datetime

PET_KNOWLEDGE = [
    {
        "topic": "feeding_puppy",
        "keywords": ["puppy", "feed", "feeding", "food", "diet", "eat", "nutrition"],
        "text": (
            "Puppies should be fed 3–4 times daily with high-quality puppy food. "
            "Avoid chocolate, onions, grapes, and human junk food — these are toxic to dogs."
        ),
    },
    {
        "topic": "cat_sneezing",
        "keywords": ["sneeze", "sneezing", "cold", "allergy", "flu", "nasal", "discharge"],
        "text": (
            "Cat sneezing can be caused by allergies, dust, or upper respiratory infections. "
            "Occasional sneezing is normal; persistent sneezing with discharge warrants a vet visit."
        ),
    },
    {
        "topic": "dog_exercise",
        "keywords": ["walk", "exercise", "run", "activity", "play", "outdoor", "outside", "energy"],
        "text": (
            "Dogs need 20–60 minutes of daily exercise depending on breed and age. "
            "High-energy breeds (Huskies, Labs) need more; smaller or senior dogs need less. "
            "Mental stimulation — puzzle toys, training — counts too."
        ),
    },
    {
        "topic": "emergency_symptoms",
        "keywords": [
            "emergency", "vomit", "not eating", "lethargic", "collapse",
            "seizure", "difficulty breathing", "bloody stool", "puke",
            "throwup", "unresponsive", "not responding", "pale gums",
        ],
        "text": (
            "⚠️ EMERGENCY: If your pet collapses, has seizures, bleeds heavily, "
            "cannot breathe, or has pale/white gums — go to an emergency vet immediately. "
            "Do not wait for a regular appointment."
        ),
    },
    {
        "topic": "grooming_care",
        "keywords": ["bath", "groom", "fur", "clean", "hair", "brush", "nails", "ears", "shampoo", "mat"],
        "text": (
            "Regular grooming prevents skin issues. Brush dogs and cats weekly to remove loose fur. "
            "Bathe every 1–3 months with pet-safe shampoo. Trim nails every 3–4 weeks. "
            "Clean ears regularly to prevent yeast or bacterial infections."
        ),
    },
    {
        "topic": "vaccination",
        "keywords": ["vaccine","vaccinated", "vaccination", "shot", "rabies", "booster", "distemper", "bordetella", "feline leukemia"],
        "text": (
            "Core vaccines for dogs include rabies, distemper, and parvovirus. "
            "Core vaccines for cats include rabies and FVRCP. "
            "Booster schedules vary — your vet will set a reminder. Keep records up to date."
        ),
    },
    {
        "topic": "behavior_training",
        "keywords": ["train", "behavior", "aggressive", "bite", "obedience", "commands", "sit", "stay", "leash", "reinforcement"],
        "text": (
            "Positive reinforcement (treats + praise) is the most effective training method. "
            "Start with simple commands: sit, stay, come. Keep sessions short (5–10 min). "
            "Avoid punishment — it increases anxiety and can cause aggression."
        ),
    },
    {
        "topic": "hydration",
        "keywords": ["water", "drink", "hydration", "dehydrated", "thirsty", "dry mouth", "urine"],
        "text": (
            "Fresh, clean water should always be available. "
            "Signs of dehydration: dry/sticky gums, skin tenting, dark urine, lethargy. "
            "Wet food can supplement hydration, especially for cats who naturally drink little."
        ),
    },
    {
        "topic": "sleep_needs",
        "keywords": ["sleep", "tired", "rest", "nap", "sleeping", "resting", "bed", "bedtime", "exhausted"],
        "text": (
            "Adult dogs sleep 12–14 hours a day; cats up to 16 hours. "
            "Puppies and kittens need even more. "
            "Sudden changes in sleep (too much or too little) can indicate illness — consult a vet."
        ),
    },
    {
        "topic": "vet_care",
        "keywords": ["vet", "doctor", "clinic", "checkup", "veterinarian", "appointment", "visit", "annual", "physical", "preventive"],
        "text": (
            "Adult pets should have a wellness exam once a year; seniors (7+) twice a year. "
            "Puppies and kittens need more frequent visits in their first year. "
            "Preventive care catches issues early and costs less than treating advanced disease."
        ),
    },
    {
        "topic": "dental_care",
        "keywords": ["teeth", "dental", "breath", "tooth", "tartar", "brush teeth", "mouth", "gum", "bad breath"],
        "text": (
            "Dental disease is one of the most common pet health issues. "
            "Brush your pet's teeth 2–3 times a week with pet-safe toothpaste. "
            "Dental chews and water additives can help. Annual professional cleanings may be needed."
        ),
    },
    {
        "topic": "parasite_prevention",
        "keywords": ["flea", "tick", "worm", "heartworm", "parasite", "mite", "lice", "mange", "dewormer"],
        "text": (
            "Use vet-recommended flea, tick, and heartworm preventatives year-round. "
            "Check for ticks after outdoor activities. "
            "Annual fecal tests catch intestinal worms early. Never use dog flea products on cats."
        ),
    },
]


def retrieve_info(query: str) -> list[dict]:
    """
    RAG retrieval step: score each knowledge chunk by keyword overlap,
    return top matches sorted by relevance score (descending).
    Returns list of dicts with 'topic', 'text', and 'score'.
    """
    query_lower = query.lower()
    results = []

    for item in PET_KNOWLEDGE:
        score = sum(1 for kw in item["keywords"] if kw in query_lower)
        if score > 0:
            results.append({
                "topic": item["topic"],
                "text": item["text"],
                "score": score,
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results  # may be empty


INTENT_MAP = {
    "emergency":  ["emergency", "collapse", "not eating", "seizure", "bloody", "pale gums", "unresponsive"],
    "feeding":    ["feed", "food", "eat", "diet", "nutrition", "puppy food"],
    "exercise":   ["walk", "exercise", "play", "run", "activity", "outdoor"],
    "health":     ["sick", "sneeze", "vomit", "lethargic", "vet", "checkup", "vaccine"],
    "grooming":   ["bath", "groom", "brush", "nails", "fur", "shampoo"],
    "training":   ["train", "behavior", "sit", "stay", "aggressive", "bite"],
    "hydration":  ["water", "drink", "dehydrated", "thirsty"],
    "sleep":      ["sleep", "tired", "rest", "nap", "exhausted"],
    "dental":     ["teeth", "dental", "breath", "tartar"],
    "parasite":   ["flea", "tick", "worm", "heartworm", "parasite"],
}

def detect_intent(query: str) -> str:
    query_lower = query.lower()
    for intent, keywords in INTENT_MAP.items():
        if any(kw in query_lower for kw in keywords):
            return intent
    return "general"


def compute_confidence(retrieved: list[dict], intent: str) -> float:
    """
    Confidence is based on how many chunks were retrieved and their scores.
    Emergency intent always gets high confidence (guardrail fires).
    """
    if intent == "emergency":
        return 0.97
    if not retrieved:
        return 0.25
    top_score = retrieved[0]["score"]
    chunk_bonus = min(0.1 * len(retrieved), 0.3)  # up to +0.3 for multiple chunks
    base = 0.5 + (0.1 * top_score)
    return round(min(base + chunk_bonus, 0.95), 2)


def run_pawpal_agent(query: str) -> tuple[str, float, str]:
    """
    RAG pipeline:
      1. Detect intent
      2. Guardrail check (emergency bypass)
      3. Retrieve relevant knowledge chunks
      4. Augment response with retrieved context
      5. Log query + result

    Returns (response_text, confidence_score, intent)
    """

    # 1. Intent
    intent = detect_intent(query)

    # 2. Emergency guardrail — skip retrieval, respond immediately
    if intent == "emergency":
        response = (
            "⚠️ **Emergency Detected**\n\n"
            "Please contact a veterinarian or emergency animal clinic **immediately**.\n"
            "Do not wait — time-sensitive symptoms can be life-threatening.\n\n"
            "🔴 Signs requiring urgent care: collapse, seizures, difficulty breathing, "
            "pale/white gums, heavy bleeding, or complete refusal to eat for 24+ hours."
        )
        confidence = compute_confidence([], intent)
        _log(query, intent, confidence, chunks_used=1)
        return response, confidence, intent

    # 3. Retrieve
    retrieved = retrieve_info(query)

    # 4. Build RAG-grounded response
    if not retrieved:
        response = (
            "🐾 I don't have specific information on that topic in my knowledge base.\n\n"
            "For the best advice, please consult a licensed veterinarian. "
            "You can also try rephrasing your question — e.g., mention the species, symptom, or task."
        )
        confidence = compute_confidence([], intent)
        _log(query, intent, confidence, chunks_used=0)
        return response, confidence, intent

    # Use top-3 retrieved chunks to build context
    top_chunks = retrieved[:3]
    context_block = "\n\n".join(
        f"📌 [{chunk['topic'].replace('_', ' ').title()}]\n{chunk['text']}"
        for chunk in top_chunks
    )

    response = (
        f"🐾 **PawPal AI Advice** *(based on {len(top_chunks)} knowledge source(s))*\n\n"
        f"{context_block}\n\n"
        "---\n"
        "⚠️ *Always consult a licensed veterinarian for medical decisions.*"
    )

    confidence = compute_confidence(retrieved, intent)

    # 5. Log
    _log(query, intent, confidence, chunks_used=len(top_chunks))

    return response, confidence, intent


def _log(query: str, intent: str, confidence: float, chunks_used: int):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[{timestamp}] QUERY='{query}' | INTENT={intent} "
        f"| CONFIDENCE={confidence:.2f} | CHUNKS={chunks_used}"
    )