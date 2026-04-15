"""
Ambulatory Empires Healthcare AI Agent — FastAPI REST Server
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from agent.core import AmbulatoryCareAgent
from agent.memory import VitalsReading, store

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Ambulatory Empires Healthcare AI Agent",
    description="AI-powered healthcare navigation for the 2026 ambulatory care ecosystem.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single agent instance (thread-safe with session isolation)
_agent = AmbulatoryCareAgent()


# ── Request / Response models ────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Patient's message")
    session_id: str | None = Field(None, description="Existing session ID (optional)")


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    care_route: str
    confidence: float
    reasoning: str
    keywords: list[str]
    routed_data: Any = None


class VitalsRequest(BaseModel):
    session_id: str | None = None
    heart_rate: float | None = None
    blood_pressure_systolic: float | None = None
    blood_pressure_diastolic: float | None = None
    oxygen_saturation: float | None = None
    blood_glucose: float | None = None
    temperature: float | None = None
    respiratory_rate: float | None = None


class VitalsResponse(BaseModel):
    analysis: str
    is_critical: bool
    overall_alert: str
    vitals: dict
    session_id: str


class TriageRequest(BaseModel):
    message: str


class ClinicSearchRequest(BaseModel):
    zip_code: str = "00000"
    services: list[str] = []


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, tags=["health"])
async def root():
    """Redirect to the dashboard or show API info."""
    html = """
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=/docs">
    <title>Ambulatory Empires Healthcare Agent</title></head>
    <body><p>Redirecting to API docs...</p></body></html>
    """
    return HTMLResponse(content=html)


@app.get("/health", tags=["health"])
async def health_check():
    """API health check."""
    return {"status": "healthy", "agent": "AmbulatoryCareAgent", "timestamp": datetime.now().isoformat()}


@app.get("/welcome", tags=["agent"])
async def welcome():
    """Return the welcome message and start a new session."""
    session = _agent.new_session()
    return {
        "welcome_message": _agent.welcome_message(),
        "session_id": session.session_id,
    }


@app.post("/chat", response_model=ChatResponse, tags=["agent"])
async def chat(request: ChatRequest):
    """
    Send a message to the healthcare AI agent.
    Handles triage, routing, and LLM response generation.
    """
    session = store.get_or_create(request.session_id)
    try:
        result = _agent.chat(session, request.message)
        triage = result["triage"]
        return ChatResponse(
            reply=result["reply"],
            session_id=result["session_id"],
            care_route=triage.route.value,
            confidence=triage.confidence,
            reasoning=triage.reasoning,
            keywords=triage.keywords,
            routed_data=result.get("routed_data"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vitals", response_model=VitalsResponse, tags=["hospital-at-home"])
async def submit_vitals(request: VitalsRequest):
    """
    Submit patient vitals for analysis.
    Returns clinical assessment and alert level.
    """
    session = store.get_or_create(request.session_id)
    vitals = VitalsReading(
        timestamp=datetime.now(),
        heart_rate=request.heart_rate,
        blood_pressure_systolic=request.blood_pressure_systolic,
        blood_pressure_diastolic=request.blood_pressure_diastolic,
        oxygen_saturation=request.oxygen_saturation,
        blood_glucose=request.blood_glucose,
        temperature=request.temperature,
        respiratory_rate=request.respiratory_rate,
    )

    from modules.hospital_at_home import analyze_vitals
    rule_analysis = analyze_vitals({
        k: v for k, v in request.dict().items()
        if k not in ("session_id",) and v is not None
    })

    result = _agent.analyze_vitals(session, vitals)
    return VitalsResponse(
        analysis=result["analysis"],
        is_critical=result["is_critical"],
        overall_alert=rule_analysis.get("overall_alert", "NORMAL"),
        vitals=result["vitals"],
        session_id=session.session_id,
    )


@app.post("/triage", tags=["agent"])
async def triage_only(request: TriageRequest):
    """
    Run triage on a message without generating an agent reply.
    Useful for quick care route classification.
    """
    from agent.triage import TriageEngine
    engine = TriageEngine()
    result = engine.triage(request.message)
    return {
        "route": result.route.value,
        "confidence": result.confidence,
        "reasoning": result.reasoning,
        "keywords": result.keywords,
        "method": result.method,
        "is_emergency": result.is_emergency,
    }


@app.post("/clinics/retail", tags=["retail-health"])
async def find_retail_clinics(request: ClinicSearchRequest):
    """Find retail health clinics for given zip code and services."""
    from modules.retail_health import find_retail_clinic
    clinics = find_retail_clinic(request.zip_code, request.services)
    return {"zip_code": request.zip_code, "clinics": clinics, "count": len(clinics)}


@app.post("/clinics/asc", tags=["outpatient"])
async def find_asc(zip_code: str = "00000", procedure: str = "general"):
    """Find Ambulatory Surgery Centers for a procedure."""
    from modules.outpatient import find_asc_centers, get_cost_comparison
    centers = find_asc_centers(zip_code, procedure)
    cost_comparison = get_cost_comparison(procedure)
    return {
        "zip_code": zip_code,
        "procedure": procedure,
        "centers": centers,
        "cost_comparison": cost_comparison,
    }


@app.get("/sessions/{session_id}", tags=["session"])
async def get_session_info(session_id: str):
    """Retrieve session summary."""
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.summary()


@app.get("/rpm/guide/{condition}", tags=["hospital-at-home"])
async def get_rpm_guide(condition: str):
    """Get RPM device setup and daily monitoring protocol for a condition."""
    from modules.hospital_at_home import get_rpm_recommendations
    return get_rpm_recommendations(condition)


@app.get("/screenings", tags=["retail-health"])
async def get_screenings(age: int | None = None, gender: str | None = None):
    """Get recommended preventive screenings."""
    from modules.retail_health import get_screening_schedule
    return {"screenings": get_screening_schedule(age, gender)}


@app.get("/preop/{procedure}", tags=["outpatient"])
async def get_preop(procedure: str):
    """Get pre-operative preparation checklist."""
    from modules.outpatient import get_preop_checklist, get_postop_guide
    return {
        "procedure": procedure,
        "preop_checklist": get_preop_checklist(procedure),
        "postop_guide": get_postop_guide(procedure),
    }
