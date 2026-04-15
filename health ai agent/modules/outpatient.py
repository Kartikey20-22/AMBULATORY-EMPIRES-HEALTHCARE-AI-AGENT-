"""
Outpatient Surge Module — ASC finder, pre-op & post-op guidance.
"""
from __future__ import annotations

# ── Sample ASC database ──────────────────────────────────────────────────────
_ASC_DATABASE = [
    {
        "id": "asc_001",
        "name": "ClearView Ambulatory Surgery Center",
        "address": "1230 Wellness Blvd, Suite 100",
        "city": "Austin", "state": "TX", "zip": "78701",
        "phone": "(512) 555-0101",
        "specialties": ["orthopedic", "spine", "general", "eye"],
        "procedures": ["knee replacement", "hip replacement", "cataract", "hernia", "colonoscopy"],
        "accreditation": "AAAHC",
        "operating_hours": "Mon–Fri 6:00 AM – 6:00 PM",
        "same_day_discharge": True,
        "avg_cost_savings": "52%",
        "rating": 4.8,
        "insurance_accepted": ["Medicare", "Blue Cross", "Aetna", "United Health", "Cigna"],
    },
    {
        "id": "asc_002",
        "name": "Meridian Day Surgery Institute",
        "address": "4500 Outpatient Way",
        "city": "Dallas", "state": "TX", "zip": "75201",
        "phone": "(214) 555-0202",
        "specialties": ["orthopedic", "gastroenterology", "urology", "ophthalmology"],
        "procedures": ["joint replacement", "endoscopy", "colonoscopy", "cataract", "kidney stone"],
        "accreditation": "Joint Commission",
        "operating_hours": "Mon–Sat 7:00 AM – 7:00 PM",
        "same_day_discharge": True,
        "avg_cost_savings": "48%",
        "rating": 4.7,
        "insurance_accepted": ["Medicare", "Medicaid", "Humana", "Blue Shield", "Oscar"],
    },
    {
        "id": "asc_003",
        "name": "PrecisionCare Surgical Partners",
        "address": "890 Ambulatory Ave",
        "city": "Chicago", "state": "IL", "zip": "60601",
        "phone": "(312) 555-0303",
        "specialties": ["ENT", "plastic surgery", "dermatology", "pain management"],
        "procedures": ["tonsillectomy", "skin lesion", "biopsy", "carpal tunnel", "pain block"],
        "accreditation": "AAAHC",
        "operating_hours": "Mon–Fri 7:00 AM – 5:00 PM",
        "same_day_discharge": True,
        "avg_cost_savings": "55%",
        "rating": 4.9,
        "insurance_accepted": ["Blue Cross", "Aetna", "United Health", "Cigna", "Molina"],
    },
]

# ── Pre-op checklists ────────────────────────────────────────────────────────
_PREOP_CHECKLISTS: dict[str, list[str]] = {
    "default": [
        "✅ Confirm your procedure date and arrival time with the surgical center",
        "✅ Do NOT eat or drink anything (including water) for 8 hours before surgery",
        "✅ Arrange a responsible adult to drive you home — you cannot drive after anesthesia",
        "✅ Have someone stay with you for the first 24 hours post-procedure",
        "✅ Share a complete medication list with your surgical team",
        "✅ Stop blood thinners (aspirin, warfarin, etc.) as directed by your surgeon",
        "✅ Shower the night before with antibacterial soap if provided",
        "✅ Leave valuables and jewelry at home",
        "✅ Bring photo ID and insurance card",
        "✅ Wear loose, comfortable clothing that's easy to remove",
        "✅ Fill prescription for post-op pain medications before surgery day",
        "✅ Prepare a comfortable recovery space at home before leaving",
    ],
    "cataract": [
        "✅ Arrange a driver — vision will be blurry immediately after surgery",
        "✅ Pick up prescribed eye drops before surgery day",
        "✅ Do not wear eye makeup or face cream on surgery day",
        "✅ Take your regular medications with a small sip of water unless told otherwise",
        "✅ Bring sunglasses for after surgery (sensitivity to light is common)",
        "✅ Do not eat or drink for 4–6 hours before surgery",
        "✅ Confirm insurance pre-authorization with the center",
    ],
    "knee replacement": [
        "✅ Complete pre-operative physical therapy as recommended",
        "✅ Arrange your home for recovery: grab bars, raised toilet seat, clear pathways",
        "✅ Prepare a ground-floor sleeping area if possible",
        "✅ Learn to use crutches or walker before surgery",
        "✅ Stop NSAIDs (ibuprofen, naproxen) 1 week before surgery",
        "✅ Do not shave the surgical leg — the center will prep the area",
        "✅ Fill prescriptions for pain medication, blood clot prevention, and antibiotics",
        "✅ Arrange physical therapy appointments post-surgery in advance",
    ],
    "colonoscopy": [
        "✅ Follow low-fiber diet for 3–5 days before the procedure",
        "✅ Day before: clear liquid diet only (broth, water, clear juice, jello)",
        "✅ Complete the prescribed bowel prep solution the evening before",
        "✅ Arrange a driver home — sedation means no driving for 24 hours",
        "✅ Stop iron supplements and blood thinners as instructed",
        "✅ You may take most regular medications with a small sip of water",
    ],
}

# ── Post-op guides ───────────────────────────────────────────────────────────
_POSTOP_GUIDES: dict[str, list[str]] = {
    "default": [
        "🏠 Rest at home for the first 24–48 hours",
        "💊 Take prescribed pain medications as directed; don't wait for severe pain",
        "🧊 Apply ice packs for 20 minutes every 2 hours to reduce swelling",
        "🩺 Attend all scheduled follow-up appointments",
        "⚠️ Call your surgeon immediately for: fever >101.5°F, severe swelling, wound opening, or unusual pain",
        "🚫 No driving until cleared by your surgeon",
        "🍽️ Start with clear liquids; advance diet as tolerated",
        "💧 Stay well hydrated",
        "📱 Use the provided telehealth portal for non-emergency questions",
    ],
    "cataract": [
        "💊 Use prescribed eye drops exactly as directed for full duration",
        "🚫 Do NOT rub or press on your eye",
        "😎 Wear the protective eye shield while sleeping for 1 week",
        "🏃 Avoid strenuous activity, swimming, or dusty environments for 2 weeks",
        "🚗 Vision may be blurry — no driving until your surgeon approves (usually 24–48 hrs)",
        "📞 Call immediately if: sudden vision loss, severe eye pain, or flashing lights",
        "🗓️ Schedule follow-up week 1, month 1, and month 3",
    ],
    "knee replacement": [
        "🦵 Begin prescribed physical therapy exercises on day 1 if directed",
        "❄️ Ice and elevate leg 3–4 times/day (20 min sessions) for first 2 weeks",
        "🩸 Wear compression stockings as prescribed to prevent blood clots",
        "⚠️ Watch for DVT signs: calf pain, redness, swelling — go to ER immediately",
        "🚶 Walk with assistive device as instructed — do NOT skip PT",
        "💊 Take blood clot prevention medication (aspirin or anticoagulant) as prescribed",
        "🛁 Keep incision dry until cleared by surgeon",
        "🗓️ Full recovery typically 3–6 months; most patients walk unaided by 6 weeks",
    ],
}


def find_asc_centers(zip_code: str, procedure: str) -> list[dict]:
    """
    Return relevant ASC centers for a procedure.
    In production, this would query a real provider database.
    """
    procedure_lower = procedure.lower()
    matched = []
    for center in _ASC_DATABASE:
        if any(p in procedure_lower or procedure_lower in p for p in center["procedures"]):
            matched.append(center)
    return matched if matched else _ASC_DATABASE[:2]  # Fallback: first 2


def get_preop_checklist(procedure: str) -> list[str]:
    """Return pre-operative checklist for a procedure."""
    procedure_lower = procedure.lower()
    for key in _PREOP_CHECKLISTS:
        if key != "default" and key in procedure_lower:
            return _PREOP_CHECKLISTS[key]
    return _PREOP_CHECKLISTS["default"]


def get_postop_guide(procedure: str) -> list[str]:
    """Return post-operative recovery guide."""
    procedure_lower = procedure.lower()
    for key in _POSTOP_GUIDES:
        if key != "default" and key in procedure_lower:
            return _POSTOP_GUIDES[key]
    return _POSTOP_GUIDES["default"]


def get_cost_comparison(procedure: str) -> dict:
    """Return cost comparison: ASC vs hospital."""
    comparisons = {
        "knee replacement": {"hospital": 35000, "asc": 16000, "savings": 54},
        "cataract": {"hospital": 3500, "asc": 1500, "savings": 57},
        "colonoscopy": {"hospital": 2800, "asc": 1200, "savings": 57},
        "hernia": {"hospital": 8000, "asc": 3500, "savings": 56},
        "default": {"hospital": 10000, "asc": 4500, "savings": 55},
    }
    procedure_lower = procedure.lower()
    for key in comparisons:
        if key != "default" and key in procedure_lower:
            return comparisons[key]
    return comparisons["default"]
