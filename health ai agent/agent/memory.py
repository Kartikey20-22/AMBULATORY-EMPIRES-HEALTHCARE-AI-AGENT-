"""
Patient session memory — stores conversation history, vitals, and preferences.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class VitalsReading:
    """A single vitals measurement."""
    timestamp: datetime
    heart_rate: float | None = None
    blood_pressure_systolic: float | None = None
    blood_pressure_diastolic: float | None = None
    oxygen_saturation: float | None = None
    blood_glucose: float | None = None
    temperature: float | None = None
    respiratory_rate: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "heart_rate": self.heart_rate,
            "blood_pressure_systolic": self.blood_pressure_systolic,
            "blood_pressure_diastolic": self.blood_pressure_diastolic,
            "oxygen_saturation": self.oxygen_saturation,
            "blood_glucose": self.blood_glucose,
            "temperature": self.temperature,
            "respiratory_rate": self.respiratory_rate,
        }


@dataclass
class Message:
    """A single conversation turn."""
    role: str          # "user" or "model"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    triage_route: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "parts": [{"text": self.content}],
        }


@dataclass
class PatientSession:
    """In-memory session for one patient conversation."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    # Conversation history
    messages: list[Message] = field(default_factory=list)

    # Patient context (populated as conversation progresses)
    age: int | None = None
    gender: str | None = None
    zip_code: str | None = None
    conditions: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)

    # Vitals history (for Hospital-at-Home)
    vitals_history: list[VitalsReading] = field(default_factory=list)

    # Routing context
    last_triage_route: str | None = None
    alerts_triggered: list[str] = field(default_factory=list)

    def add_message(self, role: str, content: str, triage_route: str | None = None) -> None:
        self.messages.append(Message(role=role, content=content, triage_route=triage_route))

    def add_vitals(self, reading: VitalsReading) -> None:
        self.vitals_history.append(reading)

    def get_history_for_gemini(self, max_turns: int = 20) -> list[dict]:
        """Return last N turns formatted for Gemini API."""
        recent = self.messages[-max_turns:]
        return [m.to_dict() for m in recent]

    def get_latest_vitals(self) -> VitalsReading | None:
        return self.vitals_history[-1] if self.vitals_history else None

    def summary(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "message_count": len(self.messages),
            "last_route": self.last_triage_route,
            "alerts": self.alerts_triggered,
            "conditions": self.conditions,
        }


class SessionStore:
    """Simple in-memory session registry."""

    def __init__(self) -> None:
        self._sessions: dict[str, PatientSession] = {}

    def create_session(self) -> PatientSession:
        session = PatientSession()
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> PatientSession | None:
        return self._sessions.get(session_id)

    def get_or_create(self, session_id: str | None) -> PatientSession:
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]
        return self.create_session()

    def list_sessions(self) -> list[dict]:
        return [s.summary() for s in self._sessions.values()]


# Singleton store
store = SessionStore()
