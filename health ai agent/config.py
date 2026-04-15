"""
Ambulatory Empires Healthcare AI Agent - Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Gemini ──────────────────────────────────────────────
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# ── Agent ────────────────────────────────────────────────
AGENT_NAME: str = os.getenv("AGENT_NAME", "AmbulatoryCareAgent")
MAX_HISTORY_TURNS: int = int(os.getenv("MAX_HISTORY_TURNS", "20"))
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

# ── API ──────────────────────────────────────────────────
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))

# ── Vitals Thresholds ────────────────────────────────────
VITALS_THRESHOLDS = {
    "heart_rate":     {"min": 60,  "max": 100, "unit": "bpm"},
    "blood_pressure_systolic":  {"min": 90,  "max": 120, "unit": "mmHg"},
    "blood_pressure_diastolic": {"min": 60,  "max": 80,  "unit": "mmHg"},
    "oxygen_saturation": {"min": 95, "max": 100, "unit": "%"},
    "blood_glucose":  {"min": 70,  "max": 180, "unit": "mg/dL"},
    "temperature":    {"min": 97.0,"max": 99.5, "unit": "°F"},
    "respiratory_rate": {"min": 12, "max": 20, "unit": "breaths/min"},
}
