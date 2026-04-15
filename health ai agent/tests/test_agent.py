"""
Unit tests for the Ambulatory Empires Healthcare AI Agent.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Triage engine tests ──────────────────────────────────────────────────────
from agent.triage import TriageEngine, CareRoute


@pytest.fixture
def triage_engine():
    return TriageEngine()


def test_triage_emergency_chest_pain(triage_engine):
    result = triage_engine.triage("I have chest pain and can't breathe")
    assert result.route == CareRoute.EMERGENCY
    assert result.confidence >= 0.9
    assert result.method == "rule_based"


def test_triage_emergency_stroke(triage_engine):
    result = triage_engine.triage("My father has face drooping and arm weakness suddenly")
    assert result.route == CareRoute.EMERGENCY
    assert result.is_emergency is True


def test_triage_asc_knee(triage_engine):
    result = triage_engine.triage("I need a knee replacement surgery")
    assert result.route == CareRoute.ASC


def test_triage_asc_cataract(triage_engine):
    result = triage_engine.triage("I have cataracts and need the procedure done")
    assert result.route == CareRoute.ASC


def test_triage_home_monitoring_heart_failure(triage_engine):
    result = triage_engine.triage("I have heart failure and need monitoring at home")
    assert result.route == CareRoute.HOME_MONITORING


def test_triage_home_monitoring_diabetes(triage_engine):
    result = triage_engine.triage("My blood sugar has been fluctuating, I need glucose monitoring help")
    assert result.route == CareRoute.HOME_MONITORING


def test_triage_retail_cold(triage_engine):
    result = triage_engine.triage("I have a bad cold and sore throat")
    assert result.route == CareRoute.RETAIL


def test_triage_retail_vaccine(triage_engine):
    result = triage_engine.triage("I need my flu shot and annual physical")
    assert result.route == CareRoute.RETAIL


# ── Memory / session tests ────────────────────────────────────────────────────
from agent.memory import PatientSession, VitalsReading, SessionStore
from datetime import datetime


def test_session_creation():
    store = SessionStore()
    session = store.create_session()
    assert session.session_id is not None
    assert len(session.messages) == 0


def test_session_message_tracking():
    store = SessionStore()
    session = store.create_session()
    session.add_message("user", "Hello")
    session.add_message("model", "Hi! How can I help?")
    assert len(session.messages) == 2
    assert session.messages[0].role == "user"
    assert session.messages[1].role == "model"


def test_session_vitals():
    store = SessionStore()
    session = store.create_session()
    vitals = VitalsReading(
        timestamp=datetime.now(),
        heart_rate=75.0,
        oxygen_saturation=98.0,
    )
    session.add_vitals(vitals)
    assert len(session.vitals_history) == 1
    assert session.get_latest_vitals().heart_rate == 75.0


def test_get_or_create_existing():
    store = SessionStore()
    session = store.create_session()
    retrieved = store.get_or_create(session.session_id)
    assert retrieved.session_id == session.session_id


# ── Outpatient module tests ───────────────────────────────────────────────────
from modules.outpatient import find_asc_centers, get_preop_checklist, get_postop_guide, get_cost_comparison


def test_find_asc_centers_knee():
    centers = find_asc_centers("78701", "knee replacement")
    assert len(centers) >= 1
    assert all("id" in c for c in centers)


def test_preop_checklist_default():
    checklist = get_preop_checklist("general procedure")
    assert len(checklist) >= 5
    assert any("eat" in item.lower() or "fast" in item.lower() for item in checklist)


def test_preop_checklist_cataract():
    checklist = get_preop_checklist("cataract")
    assert len(checklist) >= 3
    assert any("eye" in item.lower() or "vision" in item.lower() or "drops" in item.lower() for item in checklist)


def test_cost_comparison_knee():
    comparison = get_cost_comparison("knee replacement")
    assert comparison["hospital"] > comparison["asc"]
    assert comparison["savings"] > 0


# ── Hospital-at-Home module tests ─────────────────────────────────────────────
from modules.hospital_at_home import get_rpm_recommendations, analyze_vitals, get_trend_summary


def test_rpm_heart_failure():
    guide = get_rpm_recommendations("heart failure")
    assert "devices" in guide
    assert len(guide["devices"]) >= 2
    assert "daily_checklist" in guide
    assert "red_flags" in guide


def test_rpm_diabetes():
    guide = get_rpm_recommendations("diabetes")
    assert "CGM" in str(guide["devices"]) or "glucose" in guide["condition"].lower()


def test_vitals_analysis_normal():
    result = analyze_vitals({
        "heart_rate": 72.0,
        "blood_pressure_systolic": 118.0,
        "blood_pressure_diastolic": 78.0,
        "oxygen_saturation": 98.0,
    })
    assert result["overall_alert"] == "NORMAL"
    assert result["metrics"]["heart_rate"]["status"] == "NORMAL"


def test_vitals_analysis_high_bp():
    result = analyze_vitals({
        "blood_pressure_systolic": 175.0,
        "blood_pressure_diastolic": 95.0,
    })
    assert result["overall_alert"] in ("MONITOR", "ALERT", "EMERGENCY")
    assert result["metrics"]["blood_pressure_systolic"]["status"] == "HIGH"


def test_vitals_analysis_low_o2():
    result = analyze_vitals({"oxygen_saturation": 88.0})
    assert result["metrics"]["oxygen_saturation"]["status"] == "LOW"
    assert result["metrics"]["oxygen_saturation"]["severity"] in ("WARNING", "CRITICAL")


# ── Retail health module tests ────────────────────────────────────────────────
from modules.retail_health import find_retail_clinic, get_screening_schedule, is_appropriate_for_retail


def test_find_retail_clinics():
    clinics = find_retail_clinic("78701", ["vaccination"])
    assert len(clinics) >= 1


def test_screening_schedule_woman_40():
    schedule = get_screening_schedule(40, "female")
    screenings = [s["screening"] for s in schedule]
    assert "Mammogram" in screenings


def test_screening_schedule_man_65():
    schedule = get_screening_schedule(65, "male")
    screenings = [s["screening"] for s in schedule]
    assert any("Prostate" in s or "Fall" in s or "Cognitive" in s for s in screenings)


def test_appropriate_for_retail_cold():
    result = is_appropriate_for_retail("I have a cold and sore throat")
    assert result["appropriate"] is True


def test_not_appropriate_for_retail_chest_pain():
    result = is_appropriate_for_retail("I have severe chest pain")
    assert result["appropriate"] is False
