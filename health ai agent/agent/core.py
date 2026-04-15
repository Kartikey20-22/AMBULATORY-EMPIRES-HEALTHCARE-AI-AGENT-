"""
Main Ambulatory Care Agent — orchestrates Gemini LLM, triage, and module routing.
"""
from __future__ import annotations

from google import genai
from google.genai import types

from config import GOOGLE_API_KEY, GEMINI_MODEL, MAX_HISTORY_TURNS
from agent.prompts import SYSTEM_PROMPT, VITALS_ANALYSIS_PROMPT, WELCOME_MESSAGE
from agent.triage import TriageEngine, TriageResult, CareRoute
from agent.memory import PatientSession, VitalsReading, SessionStore, store


class AmbulatoryCareAgent:
    """
    Core healthcare navigation agent powered by Google Gemini.

    Usage:
        agent = AmbulatoryCareAgent()
        session = agent.new_session()
        response = agent.chat(session, "I have knee pain and may need surgery")
    """

    def __init__(self) -> None:
        self._client = None  # Lazy-init: only created when LLM is needed
        self._model = GEMINI_MODEL
        self._triage = TriageEngine()
        self._session_store: SessionStore = store

    def _get_client(self) -> genai.Client:
        """Lazily initialize the Gemini client."""
        if self._client is None:
            self._client = genai.Client(api_key=GOOGLE_API_KEY)
        return self._client

    # ── Session management ───────────────────────────────────────────────────

    def new_session(self) -> PatientSession:
        return self._session_store.create_session()

    def get_session(self, session_id: str) -> PatientSession | None:
        return self._session_store.get_session(session_id)

    def welcome_message(self) -> str:
        return WELCOME_MESSAGE

    # ── Core chat ────────────────────────────────────────────────────────────

    def chat(self, session: PatientSession, user_message: str) -> dict:
        """
        Process a user message and return a structured response.

        Returns:
            {
                "reply": str,
                "triage": TriageResult,
                "session_id": str,
                "routed_data": dict | None,
            }
        """
        # 1. Run triage
        triage: TriageResult = self._triage.triage(user_message)
        session.last_triage_route = triage.route.value

        if triage.is_emergency:
            session.alerts_triggered.append(f"EMERGENCY: {user_message[:80]}")

        # 2. Pull module context to enrich the prompt
        routed_data = self._get_module_context(triage, session, user_message)

        # 3. Build contextual user message with triage context injected
        enriched_message = self._build_enriched_message(user_message, triage, routed_data)

        # 4. Record user turn in session
        session.add_message("user", user_message, triage_route=triage.route.value)

        # 5. Build Gemini contents with history
        history = session.get_history_for_gemini(MAX_HISTORY_TURNS)
        # Remove the last entry (current user message) since we'll add enriched version
        if history and history[-1]["role"] == "user":
            history = history[:-1]

        # Build contents list: history + current enriched message
        contents = []
        for msg in history:
            contents.append(
                types.Content(
                    role=msg["role"],
                    parts=[types.Part.from_text(text=p["text"]) for p in msg["parts"]],
                )
            )
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=enriched_message)],
            )
        )

        response = self._get_client().models.generate_content(
            model=self._model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )
        reply_text = response.text

        # 6. Record model turn
        session.add_message("model", reply_text)

        return {
            "reply": reply_text,
            "triage": triage,
            "session_id": session.session_id,
            "routed_data": routed_data,
        }

    # ── Vitals analysis ──────────────────────────────────────────────────────

    def analyze_vitals(self, session: PatientSession, vitals: VitalsReading) -> dict:
        """
        Analyze a vitals reading, store it, and return clinical assessment.
        """
        from config import VITALS_THRESHOLDS
        import json

        session.add_vitals(vitals)

        vitals_json = json.dumps(vitals.to_dict(), indent=2)
        thresholds_json = json.dumps(VITALS_THRESHOLDS, indent=2)

        prompt = VITALS_ANALYSIS_PROMPT.format(
            vitals_json=vitals_json,
            thresholds_json=thresholds_json,
        )

        response = self._get_client().models.generate_content(
            model=self._model,
            contents=prompt,
        )
        analysis = response.text

        # Detect emergency keywords in analysis
        is_critical = any(w in analysis.lower() for w in ["emergency", "call 911", "immediate"])
        if is_critical:
            session.alerts_triggered.append(f"VITALS_ALERT: {vitals.timestamp.isoformat()}")

        return {
            "analysis": analysis,
            "is_critical": is_critical,
            "vitals": vitals.to_dict(),
            "session_id": session.session_id,
        }

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _get_module_context(
        self, triage: TriageResult, session: PatientSession, message: str
    ) -> dict | None:
        """Pull relevant module data to enrich the LLM prompt."""
        from modules.outpatient import get_preop_checklist, find_asc_centers
        from modules.hospital_at_home import get_rpm_recommendations, get_trend_summary
        from modules.retail_health import find_retail_clinic, get_screening_schedule

        try:
            if triage.route == CareRoute.ASC:
                # Try to extract procedure from keywords
                procedure = triage.keywords[0] if triage.keywords else "general procedure"
                zip_code = session.zip_code or "00000"
                return {
                    "type": "asc",
                    "centers": find_asc_centers(zip_code, procedure),
                    "preop_checklist": get_preop_checklist(procedure),
                }

            elif triage.route == CareRoute.HOME_MONITORING:
                condition = triage.keywords[0] if triage.keywords else "chronic condition"
                trend = get_trend_summary(session.vitals_history)
                return {
                    "type": "home_monitoring",
                    "rpm_guide": get_rpm_recommendations(condition),
                    "vitals_trend": trend,
                }

            elif triage.route == CareRoute.RETAIL:
                zip_code = session.zip_code or "00000"
                return {
                    "type": "retail",
                    "clinics": find_retail_clinic(zip_code, triage.keywords[:2]),
                }

        except Exception:
            pass
        return None

    def _build_enriched_message(
        self, user_message: str, triage: TriageResult, routed_data: dict | None
    ) -> str:
        """Inject triage + module context into the user message for Gemini."""
        import json

        parts = [user_message]
        parts.append(
            f"\n\n[SYSTEM TRIAGE CONTEXT — do not repeat verbatim to user]\n"
            f"Route: {triage.route.value} | Confidence: {triage.confidence:.0%}\n"
            f"Reasoning: {triage.reasoning}\n"
            f"Matched keywords: {', '.join(triage.keywords) if triage.keywords else 'N/A'}"
        )
        if routed_data:
            parts.append(
                f"\n[MODULE DATA]\n{json.dumps(routed_data, indent=2, default=str)}"
            )
        return "".join(parts)
