"""Evidence Discipline Audit — Stage F.

Per `docs/WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md` §10.

Scans Scene Briefs and Treatments for forbidden over-inference:
    - dialogue / quote marks
    - specific actions not in source moments
    - location / time concretization
    - emotion-narration verbs beyond pressure shifts
    - scriptural / historical detail injection (loaded from content/, not hardcoded)

Marks each candidate as `pass` / `risky` / `audit_fail` and records the
phrases that triggered the flag.

Anchor-specific forbidden phrases live in
`content/anchors/{anchor_id}/audit_blocklist.json` (optional). Engine code
contains no hardcoded scenario-specific names.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from engine.observer.scene_brief import SceneBrief
from engine.observer.treatment import Treatment


# ---------------------------------------------------------------------------
# Forbidden tokens / patterns
# ---------------------------------------------------------------------------

# Hard fail: screenplay markers + multi-word dialogue indicators.
# We deliberately do NOT flag bare quote marks — system templates legitimately
# quote candidate fields (e.g. unresolved_question phrases). Dialogue would
# require a verb-of-saying followed by a quote (e.g. ‟<name> said, "..."‟).
_HARD_VIOLATIONS = (
    "EXT.", "INT.",                          # screenplay sluglines
    "FADE IN", "FADE OUT", "fade in", "fade out",
    "CUT TO:", "DISSOLVE TO:",
    "(weeping)", "(crying)", "(shouting)",   # screenplay parentheticals
)


# Heuristic dialogue pattern: a verb-of-saying + opening quote within 30 chars.
# This is checked separately so a bare quoted phrase ("system field") does not fail.
_SAYING_VERBS = (" said,", " whispered,", " shouted,", " replied,",
                 " answered,", " cried,", " murmured,")

# Risky: medium severity (not strictly forbidden but flag for human review)
_RISKY_TOKENS = (
    "weeping", "crying", "sobbing",
    "shouted", "shouting", "whispered", "screamed",
    "embraced", "kissed",
    "drew sword", "fled to", "ran toward",
    "kneel", "knelt down",                   # specific physical action
    "in the courtyard", "at the gate", "by the fire",  # specific location
    "at midnight", "at dawn", "before sunrise",         # specific time
    "the prophet", "the messiah",            # scriptural concretization
)

# Anchor-specific forbidden phrases live in
# content/anchors/{anchor_id}/audit_blocklist.json (loaded at runtime).
# Default empty — engine code stays content-agnostic.
_HISTORICAL_INJECTION_PATTERNS: tuple[str, ...] = ()


@dataclass(frozen=True)
class RiskyPhrase:
    phrase: str
    risk: str           # "high" / "medium" / "low"
    reason: str
    surface: str        # "scene_brief" / "treatment"


@dataclass(frozen=True)
class AuditResult:
    candidate_id: str
    scene_brief_audit: str          # "pass" / "audit_fail"
    treatment_audit: str            # "pass" / "audit_fail"
    overall: str                    # "pass" / "risky" / "audit_fail"
    violations: tuple[RiskyPhrase, ...]
    risky_phrases: tuple[RiskyPhrase, ...]

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "scene_brief_audit": self.scene_brief_audit,
            "treatment_audit": self.treatment_audit,
            "overall": self.overall,
            "violations": [
                {"phrase": v.phrase, "risk": v.risk,
                 "reason": v.reason, "surface": v.surface}
                for v in self.violations
            ],
            "risky_phrases": [
                {"phrase": r.phrase, "risk": r.risk,
                 "reason": r.reason, "surface": r.surface}
                for r in self.risky_phrases
            ],
        }


# ---------------------------------------------------------------------------
# Surface text aggregation
# ---------------------------------------------------------------------------

def _scene_brief_text(b: SceneBrief) -> str:
    return " | ".join([
        b.starting_state, b.pressure_enters, b.turning_point, b.ending_state,
        " ".join(b.do_not_add), " ".join(b.must_preserve),
    ])


def _treatment_text(t: Treatment) -> str:
    return " | ".join([
        t.premise, t.act_1_setup, t.act_2_pressure_build,
        t.act_3_turn_consequence, t.end_hook,
        " ".join(t.adaptation_notes.values()),
    ])


# ---------------------------------------------------------------------------
# Scanners
# ---------------------------------------------------------------------------

def _scan_for_violations(
    text: str, surface: str,
    extra_blocklist: tuple[str, ...] = (),
) -> list[RiskyPhrase]:
    out: list[RiskyPhrase] = []
    lower = text.lower()
    for token in _HARD_VIOLATIONS:
        if token in text:
            out.append(RiskyPhrase(
                phrase=token, risk="high",
                reason="forbidden — screenplay marker or screenplay parenthetical",
                surface=surface,
            ))
    for pattern in (*_HISTORICAL_INJECTION_PATTERNS, *extra_blocklist):
        if pattern.lower() in lower:
            out.append(RiskyPhrase(
                phrase=pattern, risk="high",
                reason="forbidden — plot prescription or scripture injection",
                surface=surface,
            ))
    # Dialogue heuristic: verb-of-saying followed shortly by an opening quote
    for verb in _SAYING_VERBS:
        i = lower.find(verb)
        if i >= 0:
            tail = text[i:i + 30 + len(verb)]
            if any(q in tail for q in ('"', "“", '«', "「")):
                out.append(RiskyPhrase(
                    phrase=verb.strip(), risk="high",
                    reason="forbidden — dialogue (verb-of-saying followed by quote)",
                    surface=surface,
                ))
    return out


def load_anchor_blocklist(
    anchor_id: str, content_root: Path | None = None,
) -> tuple[str, ...]:
    """Load anchor-specific forbidden phrases from
    content/anchors/{anchor_id}/audit_blocklist.json.

    Schema: {"forbidden_phrases": ["phrase 1", "phrase 2", ...]}
    Returns empty tuple if file is missing.
    """
    if content_root is None:
        content_root = Path("content")
    p = content_root / "anchors" / anchor_id / "audit_blocklist.json"
    if not p.exists():
        return ()
    payload = json.loads(p.read_text(encoding="utf-8"))
    return tuple(payload.get("forbidden_phrases", []))


def _scan_for_risky(text: str, surface: str) -> list[RiskyPhrase]:
    out: list[RiskyPhrase] = []
    lower = text.lower()
    for token in _RISKY_TOKENS:
        if token in lower:
            out.append(RiskyPhrase(
                phrase=token, risk="medium",
                reason="possible over-inference — verb / location / time beyond source",
                surface=surface,
            ))
    return out


# ---------------------------------------------------------------------------
# Top-level auditor
# ---------------------------------------------------------------------------

def audit_pair(
    brief: SceneBrief,
    treatment: Treatment,
    *,
    extra_blocklist: tuple[str, ...] = (),
) -> AuditResult:
    sb_text = _scene_brief_text(brief)
    tr_text = _treatment_text(treatment)

    sb_violations = _scan_for_violations(sb_text, "scene_brief", extra_blocklist)
    tr_violations = _scan_for_violations(tr_text, "treatment", extra_blocklist)
    sb_risky = _scan_for_risky(sb_text, "scene_brief")
    tr_risky = _scan_for_risky(tr_text, "treatment")

    sb_status = "audit_fail" if sb_violations else "pass"
    tr_status = "audit_fail" if tr_violations else "pass"

    if sb_violations or tr_violations:
        overall = "audit_fail"
    elif sb_risky or tr_risky:
        overall = "risky"
    else:
        overall = "pass"

    return AuditResult(
        candidate_id=brief.candidate_id,
        scene_brief_audit=sb_status,
        treatment_audit=tr_status,
        overall=overall,
        violations=tuple(sb_violations + tr_violations),
        risky_phrases=tuple(sb_risky + tr_risky),
    )
