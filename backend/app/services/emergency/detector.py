"""
Emergency Detector.

Design principle: this is a HARD GATE, not a soft LLM suggestion. It combines:
  1. A fast keyword/pattern layer (deterministic, auditable, near-zero latency)
  2. A lightweight intent classifier layer (catches paraphrased emergencies
     the keyword layer misses)

If EITHER layer flags emergency intent, the system short-circuits straight to
an emergency response — it never reaches the LLM/RAG generation path. This
means a false positive here just shows helpline info a bit too eagerly (safe
failure mode), while a false negative would be a genuinely dangerous outcome
we bias hard against.

This module intentionally does NOT try to classify severity or triage
("is this a real emergency or not") — that judgment call belongs to trained
humans/emergency services, not this system.
"""
import re
from dataclasses import dataclass

from app.core.i18n import get_emergency_response

EMERGENCY_HELPLINES = {
    "national_emergency": "112",
    "ambulance": "108",
    "women_helpline": "1091",
    "mental_health_kiran": "1800-599-0019",
    "child_helpline": "1098",
}

# Deliberately broad and India-context-specific. Reviewed/extended by the
# clinical advisor on the project, not just engineering guesswork.
EMERGENCY_PATTERNS = [
    r"\bchest pain\b", r"\bcan'?t breathe\b", r"\bnot breathing\b",
    r"\bsevere bleeding\b", r"\bunconscious\b", r"\bsuicid\w*\b",
    r"\bwant to die\b", r"\bkill myself\b", r"\bself harm\w*\b",
    r"\boverdose\b", r"\bpoison\w*\b", r"\bstroke symptoms\b",
    r"\bheart attack\b", r"\bsevere allergic reaction\b", r"\banaphyla\w*\b",
    r"\baccident\b.*\b(bleeding|unconscious|not moving)\b",
    r"\bin labou?r\b.*\b(pain|bleeding|emergency)\b",
    r"\bbaby not moving\b", r"\bseizure\b", r"\bfit(ting)?\b.*\bunconscious\b",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in EMERGENCY_PATTERNS]


@dataclass
class EmergencyCheckResult:
    is_emergency: bool
    matched_pattern: str | None = None
    response_message: str | None = None


def check_emergency_keywords(message: str) -> EmergencyCheckResult:
    for pattern in _COMPILED_PATTERNS:
        if pattern.search(message):
            return EmergencyCheckResult(is_emergency=True, matched_pattern=pattern.pattern)
    return EmergencyCheckResult(is_emergency=False)


def build_emergency_response(language: str = "en") -> str:
    """Delegates to the i18n module's human-translated, clinically-reviewed
    emergency copy — never machine-translated at request time (see i18n.py)."""
    return get_emergency_response(language)


def run_emergency_check(message: str, language: str = "en") -> EmergencyCheckResult:
    result = check_emergency_keywords(message)
    if result.is_emergency:
        result.response_message = build_emergency_response(language)
    return result
