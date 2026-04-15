"""
Hospital-at-Home Module — Remote Patient Monitoring, wearables, trends.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any


# ── RPM device guides by condition ──────────────────────────────────────────
_RPM_GUIDES: dict[str, dict] = {
    "heart failure": {
        "condition": "Congestive Heart Failure (CHF)",
        "devices": [
            {"name": "Smart Weight Scale", "frequency": "Every morning before eating", "alert_threshold": "Gain of 2+ lbs in 24hrs or 5 lbs in 1 week"},
            {"name": "Blood Pressure Cuff (connected)", "frequency": "Twice daily", "alert_threshold": "Systolic >160 mmHg or <90 mmHg"},
            {"name": "Pulse Oximeter", "frequency": "3× daily", "alert_threshold": "O2 sat <92%"},
            {"name": "ECG Patch / Smartwatch", "frequency": "Continuous", "alert_threshold": "Irregular rhythm, HR <50 or >120 bpm"},
        ],
        "daily_checklist": [
            "☀️ Morning: Weigh yourself, record in app",
            "📊 Check blood pressure (aim: <130/80)",
            "🩺 Check oxygen saturation (aim: ≥95%)",
            "💊 Take medications at same time daily",
            "🧂 Limit sodium to <2,000mg/day",
            "💧 Track fluid intake (restrict to 1.5–2L/day if advised)",
            "🏃 Log any shortness of breath, ankle swelling, or fatigue",
        ],
        "red_flags": [
            "Sudden weight gain of 2+ lbs overnight",
            "Worsening shortness of breath, especially lying flat",
            "New or worsening ankle/leg swelling",
            "Dizziness or fainting",
            "Irregular heartbeat you can feel",
        ],
        "app_integrations": ["Apple Health", "Google Fit", "Epic MyChart", "Withings Health Mate"],
    },
    "diabetes": {
        "condition": "Diabetes Management",
        "devices": [
            {"name": "Continuous Glucose Monitor (CGM)", "frequency": "Real-time continuous", "alert_threshold": "Glucose <70 mg/dL (hypo) or >250 mg/dL (hyper)"},
            {"name": "Blood Pressure Cuff", "frequency": "Daily", "alert_threshold": "Systolic >130 mmHg"},
            {"name": "Smart Insulin Pen", "frequency": "Per prescription schedule", "alert_threshold": "Missed dose alert"},
            {"name": "Activity Tracker / Smartwatch", "frequency": "Continuous", "alert_threshold": "Less than 150 min moderate activity/week"},
        ],
        "daily_checklist": [
            "📊 Check CGM reading before meals and at bedtime",
            "💉 Administer insulin per scheduled doses",
            "🥗 Log meals via nutrition app",
            "🏃 30 minutes moderate activity (with provider clearance)",
            "👣 Check feet daily for cuts, sores, or redness",
            "💧 Stay hydrated — aim for 8 glasses water",
            "⚖️ Weigh yourself weekly",
        ],
        "red_flags": [
            "Blood glucose <70 mg/dL (take 15g fast-acting carbs immediately)",
            "Blood glucose >300 mg/dL with symptoms",
            "Signs of hypoglycemia: shakiness, sweating, confusion",
            "Signs of DKA: fruity breath, nausea, rapid breathing",
            "Foot wound that doesn't heal in 24-48 hours",
        ],
        "app_integrations": ["Dexcom Clarity", "LibreView", "mySugr", "One Drop"],
    },
    "hypertension": {
        "condition": "Hypertension (High Blood Pressure) Management",
        "devices": [
            {"name": "Validated BP Cuff (upper arm)", "frequency": "Twice daily − morning & evening", "alert_threshold": "Systolic >160 or <90 mmHg"},
            {"name": "Smartwatch (heart rate)", "frequency": "Continuous", "alert_threshold": "Resting HR >100 bpm sustained"},
        ],
        "daily_checklist": [
            "🌅 Morning BP check before coffee or medications",
            "💊 Take antihypertensive medication at same time daily",
            "🧂 Low sodium diet (<1,500 mg/day ideal)",
            "🏃 30 minutes aerobic activity 5 days/week",
            "🍷 Limit alcohol (≤1 drink/day for women, ≤2 for men)",
            "🌙 Evening BP check and log readings",
            "😌 Stress management: breathing exercises, meditation",
        ],
        "red_flags": [
            "BP reading ≥180/120 mmHg — hypertensive crisis (call 911)",
            "Sudden severe headache with very high BP",
            "Vision changes (blurred or double vision)",
            "Chest pain or pressure",
            "Shortness of breath at rest",
        ],
        "app_integrations": ["Omron Connect", "QardioArm", "Apple Health", "HeartAdvisor"],
    },
    "copd": {
        "condition": "COPD Management",
        "devices": [
            {"name": "Pulse Oximeter", "frequency": "3–4× daily", "alert_threshold": "O2 sat <88% for 2 consecutive readings"},
            {"name": "Spirometer (home)", "frequency": "Daily", "alert_threshold": "FEV1 drops >15% from personal best"},
            {"name": "Connected Inhaler Sensor", "frequency": "Per prescription", "alert_threshold": "Rescue inhaler use >2×/week"},
        ],
        "daily_checklist": [
            "🌬️ Morning: Pursed-lip breathing exercises (5 min)",
            "💊 Take LABA/LAMA inhalers morning and evening",
            "📊 Log oxygen saturation reading",
            "🏃 Gentle walking or pulmonary rehab exercises",
            "💧 Drink 6–8 glasses water (thins mucus)",
            "🚭 Avoid smoke, dust, and air pollutants",
            "🌡️ Note any worsening cough, sputum, or breathlessness",
        ],
        "red_flags": [
            "O2 saturation falling below 88%",
            "Significant increase in breathlessness",
            "Change in color or amount of sputum",
            "Chest tightness not relieved by rescue inhaler",
            "Confusion or unusual drowsiness",
        ],
        "app_integrations": ["Propeller Health", "AsthmaMD", "Apple Health", "MyCOPD"],
    },
}

_DEFAULT_RPM = {
    "condition": "Chronic Disease Remote Monitoring",
    "devices": [
        {"name": "Blood Pressure Cuff", "frequency": "Daily", "alert_threshold": "Systolic >160 or <90"},
        {"name": "Pulse Oximeter", "frequency": "Daily", "alert_threshold": "O2 sat <92%"},
        {"name": "Digital Thermometer", "frequency": "If symptomatic", "alert_threshold": "Temp >100.4°F"},
    ],
    "daily_checklist": [
        "📊 Record your vitals in the app daily",
        "💊 Take all medications as prescribed",
        "📞 Contact your care team if you feel worse",
    ],
    "red_flags": [
        "Significant worsening of your condition",
        "New or unexpected symptoms",
        "Side effects from medications",
    ],
    "app_integrations": ["Apple Health", "Google Fit", "Epic MyChart"],
}


def get_rpm_recommendations(condition: str) -> dict:
    """Return RPM device setup and daily protocol for a condition."""
    condition_lower = condition.lower()
    for key, guide in _RPM_GUIDES.items():
        if key in condition_lower or condition_lower in key:
            return guide
    return _DEFAULT_RPM


def analyze_vitals(vitals_dict: dict[str, Any]) -> dict:
    """
    Rule-based vitals analysis returning status per metric.
    Returns a dict with per-metric status and an overall alert level.
    """
    from config import VITALS_THRESHOLDS

    results = {}
    alert_level = "NORMAL"

    for metric, thresholds in VITALS_THRESHOLDS.items():
        value = vitals_dict.get(metric)
        if value is None:
            continue

        mn, mx = thresholds["min"], thresholds["max"]
        unit = thresholds["unit"]

        if value < mn:
            status = "LOW"
            diff = mn - value
            severity = "CRITICAL" if diff > (mx - mn) * 0.3 else "WARNING"
        elif value > mx:
            status = "HIGH"
            diff = value - mx
            severity = "CRITICAL" if diff > (mx - mn) * 0.3 else "WARNING"
        else:
            status = "NORMAL"
            severity = "NORMAL"

        results[metric] = {
            "value": value,
            "unit": unit,
            "status": status,
            "severity": severity,
            "normal_range": f"{mn}–{mx} {unit}",
        }

        if severity == "CRITICAL" and alert_level != "EMERGENCY":
            alert_level = "ALERT"
        elif severity == "WARNING" and alert_level == "NORMAL":
            alert_level = "MONITOR"

    # Special rule: chest-related critical combo
    if (
        results.get("oxygen_saturation", {}).get("severity") == "CRITICAL"
        and results.get("heart_rate", {}).get("severity") in ("WARNING", "CRITICAL")
    ):
        alert_level = "EMERGENCY"

    return {"metrics": results, "overall_alert": alert_level}


def get_trend_summary(vitals_history: list) -> dict:
    """
    Analyze historical vitals to detect trends.
    Returns summary with trend direction per metric.
    """
    if len(vitals_history) < 2:
        return {"trend": "insufficient_data", "readings": len(vitals_history)}

    metrics_over_time: dict[str, list[float]] = {}
    for reading in vitals_history:
        d = reading.to_dict()
        for key, val in d.items():
            if key != "timestamp" and val is not None:
                metrics_over_time.setdefault(key, []).append(float(val))

    trends = {}
    for metric, values in metrics_over_time.items():
        if len(values) >= 2:
            delta = values[-1] - values[0]
            pct_change = (delta / values[0] * 100) if values[0] != 0 else 0
            direction = "improving" if abs(pct_change) < 5 else ("worsening" if pct_change > 5 else "improving")
            trends[metric] = {
                "first": values[0],
                "latest": values[-1],
                "change_pct": round(pct_change, 1),
                "direction": direction,
            }

    return {"trend": "analyzed", "readings": len(vitals_history), "metrics": trends}


def get_wearable_setup_guide(device_type: str) -> list[str]:
    """Return setup instructions for common wearable devices."""
    guides = {
        "cgm": [
            "1. Clean and dry insertion site (back of upper arm or abdomen)",
            "2. Insert sensor using applicator — press firmly for 5 seconds",
            "3. Scan with phone/reader to activate (warm-up: 1 hour for Libre, 2 hours for Dexcom)",
            "4. Calibrate if required (some CGMs are factory-calibrated)",
            "5. Set high/low glucose alerts in the companion app",
            "6. Ensure Bluetooth is enabled for real-time streaming",
            "7. Replace sensor every 10–14 days depending on device",
        ],
        "blood pressure": [
            "1. Sit quietly for 5 minutes before measuring",
            "2. Place cuff on left upper arm, 1 inch above elbow crease",
            "3. Cuff should be snug but not tight — you should slip 2 fingers under",
            "4. Keep arm at heart level, resting on a flat surface",
            "5. Do not talk or move during measurement",
            "6. Take 2 readings 1 minute apart; average the results",
            "7. Sync to your health app via Bluetooth",
        ],
        "pulse oximeter": [
            "1. Ensure fingertip is warm and nail polish-free",
            "2. Clip device on index or middle finger",
            "3. Hold still and breathe normally for 30 seconds",
            "4. Record both SpO2 (%) and pulse rate (bpm)",
            "5. Alert your care team if O2 sat falls below 92%",
        ],
        "ecg patch": [
            "1. Clean and dry skin area on chest (left side, below collarbone)",
            "2. Peel adhesive backing and apply patch firmly",
            "3. Download the companion app and pair via Bluetooth",
            "4. Start monitoring session in the app",
            "5. Wear continuously for prescribed duration (24 hrs to 14 days)",
            "6. Avoid excessive moisture — cover during showering if waterproofing not confirmed",
            "7. Return patch by prepaid mail after wear period",
        ],
    }
    device_lower = device_type.lower()
    for key in guides:
        if key in device_lower:
            return guides[key]
    return ["Contact your care team for specific device setup instructions."]
