"""
Retail Health Module — Pharmacy clinics, employer hubs, preventive care guidance.
"""
from __future__ import annotations

# ── Sample retail clinic database ────────────────────────────────────────────
_RETAIL_CLINICS = [
    {
        "id": "rc_001",
        "name": "CVS MinuteClinic",
        "type": "Pharmacy Clinic",
        "address": "1500 Main Street",
        "city": "Austin", "state": "TX", "zip": "78701",
        "phone": "(512) 555-1001",
        "hours": "Mon–Fri 8 AM–8 PM, Sat–Sun 9 AM–5 PM",
        "services": [
            "Annual physicals", "Vaccinations", "Flu shots", "COVID-19 testing",
            "UTI treatment", "Strep testing", "Blood pressure checks",
            "Cholesterol screening", "Diabetes monitoring", "Wound care",
            "Prescription refills", "TB testing",
        ],
        "providers": ["Nurse Practitioners", "Physician Assistants"],
        "wait_time_avg_min": 15,
        "cost_vs_urgent_care_savings": "45%",
        "telehealth_available": True,
        "insurance_accepted": ["Most major insurance", "Medicare Part B", "Medicaid"],
        "rating": 4.5,
    },
    {
        "id": "rc_002",
        "name": "Walgreens Health Clinic",
        "type": "Pharmacy Clinic",
        "address": "2200 Oak Avenue",
        "city": "Chicago", "state": "IL", "zip": "60601",
        "phone": "(312) 555-2002",
        "hours": "Mon–Fri 7 AM–9 PM, Sat–Sun 8 AM–6 PM",
        "services": [
            "Annual wellness visits", "Immunizations (40+ vaccines)", "Minor acute care",
            "Chronic disease management", "Lab work", "EKG",
            "Medication therapy management", "Preventive screenings",
        ],
        "providers": ["Nurse Practitioners", "Pharmacists (MTM)", "Physician Assistants"],
        "wait_time_avg_min": 10,
        "cost_vs_urgent_care_savings": "55%",
        "telehealth_available": True,
        "insurance_accepted": ["Most major insurance", "Medicare", "Medicaid", "Cash pay"],
        "rating": 4.6,
    },
    {
        "id": "rc_003",
        "name": "Amazon Clinic (Virtual)",
        "type": "Virtual Retail Health",
        "address": "Online / App",
        "city": "Nationwide", "state": "USA", "zip": "00000",
        "phone": "App-based",
        "hours": "24/7 asynchronous messaging; video visits available",
        "services": [
            "Common cold treatment", "UTI treatment", "Allergies", "Acid reflux",
            "Pink eye", "Skin conditions", "Prescription renewals",
        ],
        "providers": ["Licensed physicians", "Nurse Practitioners"],
        "wait_time_avg_min": 5,
        "cost_vs_urgent_care_savings": "60%",
        "telehealth_available": True,
        "insurance_accepted": ["Self-pay transparent pricing", "HSA/FSA eligible"],
        "rating": 4.4,
    },
    {
        "id": "rc_004",
        "name": "Walmart Health Center",
        "type": "Employer/Retail Hub",
        "address": "5000 Supercenter Drive",
        "city": "Dallas", "state": "TX", "zip": "75201",
        "phone": "(214) 555-3003",
        "hours": "Mon–Fri 8 AM–8 PM, Sat 9 AM–5 PM",
        "services": [
            "Primary care visits", "Behavioral health", "Dental", "Vision",
            "Lab services", "X-ray", "Vaccinations", "Chronic disease management",
            "Nutrition counseling",
        ],
        "providers": ["Primary care physicians", "Behavioral health counselors", "Dentists"],
        "wait_time_avg_min": 20,
        "cost_vs_urgent_care_savings": "50%",
        "telehealth_available": True,
        "insurance_accepted": ["Most major insurance", "Self-pay from $20"],
        "rating": 4.3,
    },
]

# ── Preventive screening schedules ───────────────────────────────────────────
_SCREENING_SCHEDULES: dict[str, list[dict]] = {
    "adult_general": [
        {"screening": "Blood Pressure Check", "frequency": "Every visit / annually", "start_age": 18},
        {"screening": "Cholesterol (lipid panel)", "frequency": "Every 4–6 years", "start_age": 35},
        {"screening": "Blood Glucose / Diabetes", "frequency": "Every 3 years", "start_age": 35},
        {"screening": "Colorectal Cancer (colonoscopy)", "frequency": "Every 10 years", "start_age": 45},
        {"screening": "Vision Exam", "frequency": "Every 2 years", "start_age": 18},
        {"screening": "Dental Checkup", "frequency": "Every 6 months", "start_age": 18},
    ],
    "women": [
        {"screening": "Mammogram", "frequency": "Annually", "start_age": 40},
        {"screening": "Pap Smear / Cervical Cancer Screening", "frequency": "Every 3 years (w/ HPV co-test every 5 years after 30)", "start_age": 21},
        {"screening": "Bone Density (DEXA scan)", "frequency": "Every 2 years", "start_age": 65},
        {"screening": "Breast Cancer Gene Testing (BRCA)", "frequency": "Once if family history", "start_age": 30},
    ],
    "men": [
        {"screening": "Prostate Cancer (PSA)", "frequency": "Discuss with provider annually", "start_age": 50},
        {"screening": "Abdominal Aortic Aneurysm (ultrasound)", "frequency": "Once", "start_age": 65},
        {"screening": "Testicular Self-Exam", "frequency": "Monthly", "start_age": 18},
    ],
    "over_65": [
        {"screening": "Fall Risk Assessment", "frequency": "Annually", "start_age": 65},
        {"screening": "Cognitive Assessment", "frequency": "Annually", "start_age": 65},
        {"screening": "Shingles Vaccine", "frequency": "Once", "start_age": 50},
        {"screening": "Pneumococcal Vaccine", "frequency": "Once", "start_age": 65},
        {"screening": "Hearing Test", "frequency": "Every 3 years", "start_age": 60},
    ],
}

# ── Vaccine schedule ─────────────────────────────────────────────────────────
_VACCINE_SCHEDULE = {
    "annual": ["Influenza (flu shot)"],
    "every_5_years": ["Tdap/Td booster"],
    "once_in_lifetime": ["Shingles (Zoster) at age 50+", "Pneumococcal at age 65"],
    "as_needed": ["COVID-19 updated booster", "Hepatitis A", "Hepatitis B", "HPV (through age 26)", "MMR if not immune"],
}

# ── Appropriate vs. inappropriate uses ──────────────────────────────────────
_APPROPRIATE_FOR_RETAIL = [
    "Colds, flu, and upper respiratory infections",
    "Sore throat and strep testing",
    "Ear infections",
    "Urinary tract infections (UTI)",
    "Pink eye (conjunctivitis)",
    "Minor skin rashes or infections",
    "Vaccinations and immunizations",
    "Annual physicals and wellness visits",
    "Blood pressure monitoring and medication refills",
    "Diabetes check-ins and glucose monitoring",
    "Cholesterol screening",
    "Minor cuts and wound care",
    "Pregnancy tests",
    "STI testing",
    "Simple headaches and migraines (if diagnosed)",
]

_NOT_APPROPRIATE_FOR_RETAIL = [
    "Chest pain or suspected heart attack → Call 911",
    "Stroke symptoms → Call 911",
    "Severe difficulty breathing → Call 911",
    "Severe allergic reactions → Call 911",
    "Complex surgical consultations → See a specialist",
    "Mental health crises → Call 988 Crisis Lifeline",
    "Broken bones needing imaging → Urgent care or ER",
    "Conditions requiring blood work beyond basic panels",
]


def find_retail_clinic(zip_code: str, services: list[str] | None = None) -> list[dict]:
    """
    Return retail clinics matching service needs.
    In production, this would use a geolocation + provider directory API.
    """
    if not services:
        return _RETAIL_CLINICS[:2]

    matched = []
    for clinic in _RETAIL_CLINICS:
        clinic_services_lower = [s.lower() for s in clinic["services"]]
        if any(
            any(req.lower() in s for s in clinic_services_lower)
            for req in services
        ):
            matched.append(clinic)

    return matched if matched else _RETAIL_CLINICS[:2]


def get_screening_schedule(age: int | None, gender: str | None) -> list[dict]:
    """Return applicable preventive screenings for age/gender."""
    schedule = list(_SCREENING_SCHEDULES["adult_general"])

    if gender and gender.lower() in ("female", "f", "woman"):
        schedule += _SCREENING_SCHEDULES["women"]
    elif gender and gender.lower() in ("male", "m", "man"):
        schedule += _SCREENING_SCHEDULES["men"]

    if age and age >= 65:
        schedule += _SCREENING_SCHEDULES["over_65"]

    if age:
        schedule = [s for s in schedule if s.get("start_age", 0) <= age]

    return schedule


def is_appropriate_for_retail(concern: str) -> dict:
    """Check if a health concern is appropriate for a retail clinic."""
    concern_lower = concern.lower()
    appropriate = any(kw in concern_lower for kw in [
        "cold", "flu", "cough", "sore throat", "strep", "ear", "uti", "urinary",
        "vaccine", "vaccination", "physical", "refill", "prescription",
        "check", "screening", "wound", "cut", "rash",
    ])
    not_appropriate = any(kw in concern_lower for kw in [
        "chest pain", "stroke", "can't breathe", "allergic", "bleeding",
        "broken", "fracture", "surgery",
    ])

    if not_appropriate:
        return {
            "appropriate": False,
            "reason": "This condition requires higher-acuity care — please seek urgent care or emergency services.",
            "redirect": "EMERGENCY or HOSPITAL",
        }
    elif appropriate:
        return {
            "appropriate": True,
            "reason": "This concern is well-suited for a retail health clinic — fast, affordable, and convenient.",
            "services": _APPROPRIATE_FOR_RETAIL[:5],
        }
    else:
        return {
            "appropriate": True,
            "reason": "Retail clinics can provide an initial assessment and refer you if needed.",
            "services": _APPROPRIATE_FOR_RETAIL[:3],
        }


def get_vaccine_schedule() -> dict:
    return _VACCINE_SCHEDULE
