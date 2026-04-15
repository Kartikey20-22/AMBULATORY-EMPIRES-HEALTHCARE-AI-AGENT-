"""
Clinical triage engine — routes patient queries to the right care setting.
Uses rule-based fast path + LLM fallback for complex cases.
"""
from __future__ import annotations

import json
import re
from enum import Enum
from dataclasses import dataclass

from google import genai

from config import GOOGLE_API_KEY, GEMINI_MODEL
from agent.prompts import TRIAGE_PROMPT


class CareRoute(str, Enum):
    EMERGENCY = "EMERGENCY"
    ASC = "ASC"
    HOME_MONITORING = "HOME_MONITORING"
    RETAIL = "RETAIL"
    UNKNOWN = "UNKNOWN"


@dataclass
class TriageResult:
    route: CareRoute
    confidence: float
    reasoning: str
    keywords: list[str]
    method: str  # "rule_based" | "llm"

    @property
    def is_emergency(self) -> bool:
        return self.route == CareRoute.EMERGENCY

    def display(self) -> str:
        icons = {
            CareRoute.EMERGENCY: "🚨",
            CareRoute.ASC: "🏥",
            CareRoute.HOME_MONITORING: "🏠",
            CareRoute.RETAIL: "🏪",
            CareRoute.UNKNOWN: "❓",
        }
        return (
            f"{icons[self.route]} **Care Route: {self.route.value}** "
            f"(confidence: {self.confidence:.0%})\n"
            f"_{self.reasoning}_"
        )


# ── Rule-based keyword maps ──────────────────────────────────────────────────

_EMERGENCY_KEYWORDS = [
    "chest pain", "can't breathe", "cannot breathe", "difficulty breathing",
    "stroke", "face drooping", "arm weakness", "slurred speech",
    "unconscious", "unresponsive", "severe allergic", "anaphylaxis",
    "uncontrolled bleeding", "heart attack", "911", "emergency",
    "severe trauma", "overdose", "seizure", "choking",
]

_ASC_KEYWORDS = [
    "knee replacement", "hip replacement", "joint replacement",
    "cataract", "hernia", "laparoscop", "colonoscopy", "endoscopy",
    "skin lesion", "biopsy", "outpatient surgery", "day surgery",
    "orthopedic", "carpal tunnel", "tonsil", "gallbladder",
    "spine surgery", "back surgery",
]

_HOME_MONITORING_KEYWORDS = [
    "heart failure", "congestive", "chf",
    "diabetes", "glucose", "blood sugar", "insulin",
    "blood pressure", "hypertension",
    "copd", "emphysema", "chronic bronchitis",
    "oxygen level", "oxygen saturation", "pulse ox",
    "wearable", "monitor", "remote monitoring", "rpm",
    "after discharge", "just got home from hospital", "post-discharge",
    "weight gain", "shortness of breath at home",
]

_RETAIL_KEYWORDS = [
    "cold", "flu", "sore throat", "strep", "ear infection",
    "uti", "urinary tract", "cough", "runny nose",
    "vaccine", "vaccination", "flu shot", "physical", "annual",
    "prescription refill", "refill", "medication refill",
    "preventive", "screening", "mammogram", "cholesterol",
    "wound care", "cut", "minor injury",
    "pharmacy", "cvs", "walgreens", "clinic near me",
]


def _match_keywords(text: str, keywords: list[str]) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in keywords if kw in text_lower]


class TriageEngine:
    """Classifies patient queries into a CareRoute."""

    def __init__(self) -> None:
        self._client = None  # Lazy-init: only created when LLM fallback is needed
        self._model = GEMINI_MODEL

    def _get_client(self) -> genai.Client:
        """Lazily initialize the Gemini client."""
        if self._client is None:
            self._client = genai.Client(api_key=GOOGLE_API_KEY)
        return self._client

    def triage(self, message: str) -> TriageResult:
        """Primary triage — rule-based fast path, LLM fallback."""
        # Fast path: emergency check first (safety critical)
        emerg_matches = _match_keywords(message, _EMERGENCY_KEYWORDS)
        if emerg_matches:
            return TriageResult(
                route=CareRoute.EMERGENCY,
                confidence=0.98,
                reasoning="Keywords indicate a potential emergency situation requiring immediate care.",
                keywords=emerg_matches,
                method="rule_based",
            )

        # Score each route
        scores = {
            CareRoute.ASC: len(_match_keywords(message, _ASC_KEYWORDS)),
            CareRoute.HOME_MONITORING: len(_match_keywords(message, _HOME_MONITORING_KEYWORDS)),
            CareRoute.RETAIL: len(_match_keywords(message, _RETAIL_KEYWORDS)),
        }

        max_score = max(scores.values())
        if max_score >= 1:
            best_route = max(scores, key=lambda r: scores[r])
            matched_kw = _match_keywords(message, {
                CareRoute.ASC: _ASC_KEYWORDS,
                CareRoute.HOME_MONITORING: _HOME_MONITORING_KEYWORDS,
                CareRoute.RETAIL: _RETAIL_KEYWORDS,
            }[best_route])
            return TriageResult(
                route=best_route,
                confidence=min(0.6 + max_score * 0.1, 0.95),
                reasoning=self._rule_reasoning(best_route),
                keywords=matched_kw,
                method="rule_based",
            )

        # Fallback: ask Gemini
        return self._llm_triage(message)

    def _rule_reasoning(self, route: CareRoute) -> str:
        reasons = {
            CareRoute.ASC: "Procedure matches Ambulatory Surgery Center capabilities for outpatient surgery.",
            CareRoute.HOME_MONITORING: "Condition is suitable for Remote Patient Monitoring and Hospital-at-Home program.",
            CareRoute.RETAIL: "Concern is appropriate for a retail health clinic or pharmacy-based care.",
        }
        return reasons.get(route, "Routed based on symptom analysis.")

    def _llm_triage(self, message: str) -> TriageResult:
        """Ask Gemini to classify when rule-based doesn't match."""
        prompt = TRIAGE_PROMPT.format(message=message)
        try:
            response = self._get_client().models.generate_content(
                model=self._model,
                contents=prompt,
            )
            text = response.text.strip()
            # Extract JSON from response
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                data = json.loads(match.group())
                route_str = data.get("route", "UNKNOWN").upper()
                # Map HOME_MONITORING from prompt
                route_map = {
                    "HOME_MONITORING": CareRoute.HOME_MONITORING,
                    "EMERGENCY": CareRoute.EMERGENCY,
                    "ASC": CareRoute.ASC,
                    "RETAIL": CareRoute.RETAIL,
                }
                route = route_map.get(route_str, CareRoute.UNKNOWN)
                return TriageResult(
                    route=route,
                    confidence=float(data.get("confidence", 0.5)),
                    reasoning=data.get("reasoning", "LLM-based triage assessment."),
                    keywords=data.get("keywords", []),
                    method="llm",
                )
        except Exception:
            pass

        return TriageResult(
            route=CareRoute.RETAIL,
            confidence=0.4,
            reasoning="Unable to classify precisely — routing to retail health for assessment.",
            keywords=[],
            method="fallback",
        )
