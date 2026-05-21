"""Story Viability Scoring — Stage D.

Per `docs/WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md` §8.

100-point weighted score across 8 positive factors and 2 penalty factors,
mapped to 4 grades:
    80-100  strong_viable     — ready for scene/episode work
    65-79   viable_with_gaps  — usable, needs context fill
    50-64   weak_seed         — idea seed only
    0-49    not_viable        — not a story candidate
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.observer.scene_brief import SceneBrief
from engine.observer.story_candidate import StoryCandidate
from engine.observer.treatment import Treatment

# Weights (plan §8.2 verbatim)
W_CHARACTER         = 20
W_CONFLICT          = 20
W_PRESSURE_ACCUM    = 15
W_TURNING_POINT     = 15
W_RELATIONSHIP      = 10
W_UNRESOLVED_HOOK   = 10
W_CROSS_SEED        = 5
W_ADAPTATION_RANGE  = 5
W_MISSING_PENALTY   = -10
W_OVER_INFERENCE    = -10


@dataclass(frozen=True)
class ViabilityScore:
    candidate_id: str
    score: float
    grade: str                     # "strong_viable" / "viable_with_gaps" / "weak_seed" / "not_viable"
    factor_breakdown: dict[str, float]
    penalty_breakdown: dict[str, float]
    notes: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "score": round(self.score, 2),
            "grade": self.grade,
            "factor_breakdown": {k: round(v, 3) for k, v in self.factor_breakdown.items()},
            "penalty_breakdown": {k: round(v, 3) for k, v in self.penalty_breakdown.items()},
            "notes": list(self.notes),
        }


# ---------------------------------------------------------------------------
# Per-factor calculators (each returns 0.0–1.0)
# ---------------------------------------------------------------------------

def _character_clarity(c: StoryCandidate) -> float:
    if not c.main_characters:
        return 0.0
    main = c.main_characters[0]
    if main.startswith("agent_") and "(" in main:
        return 0.5  # archetype fallback like "agent_03 (loyal_under_pressure)"
    if main.startswith("agent_"):
        return 0.0  # raw ID
    return 1.0


def _conflict_clarity(c: StoryCandidate, brief: SceneBrief) -> float:
    if c.core_conflict == "unknown":
        return 0.0
    if brief.internal_pressure and brief.external_pressure:
        return 1.0
    return 0.5


def _pressure_accumulation(c: StoryCandidate) -> float:
    n = sum(c.provenance_summary.values())
    if n >= 10:
        return 1.0
    if n >= 5:
        return 0.7
    if n >= 3:
        return 0.4
    return 0.0


def _turning_point_strength(c: StoryCandidate) -> float:
    labels = {tp.label for tp in c.key_turning_points}
    strong = {"co-occurring pressure", "sustained pressure begins", "world pressure shift"}
    overlap = labels & strong
    if len(overlap) >= 2:
        return 1.0
    if c.key_turning_points:
        return 0.6
    return 0.0


def _relationship_context(c: StoryCandidate) -> float:
    if not c.relationship_dynamics:
        return 0.0
    # Named relationship dynamics (Peter ↔ John, etc.)
    has_named = any(
        "↔" in line and any(name not in {"the central agent", "the group"}
                             for name in line.split("↔"))
        for line in c.relationship_dynamics
    )
    if has_named:
        return 1.0
    return 0.6


def _unresolved_hook(c: StoryCandidate) -> float:
    if c.unresolved_question and "?" in c.unresolved_question:
        return 1.0
    if "lingers" in c.arc_summary.lower() or "unresolved" in c.arc_summary.lower():
        return 0.5
    return 0.0


def _cross_seed_robustness(cross_seed_freq: int | None) -> float:
    if cross_seed_freq is None:
        return 0.0
    if cross_seed_freq >= 5:
        return 1.0
    if cross_seed_freq == 4:
        return 0.8
    if cross_seed_freq == 3:
        return 0.6
    return 0.0


def _adaptation_range(c: StoryCandidate) -> float:
    formats = set(c.adaptation_hooks.keys())
    # Map specific format keys to coarse media classes
    media_classes: set[str] = set()
    for f in formats:
        if "film" in f or "drama" in f or "documentary" in f:
            media_classes.add("film")
        if "novel" in f or "short_story" in f:
            media_classes.add("novel")
        if "game" in f:
            media_classes.add("game")
    n = len(media_classes)
    if n >= 3:
        return 1.0
    if n == 2:
        return 0.7
    if n == 1:
        return 0.3
    return 0.0


def _missing_context_penalty(brief: SceneBrief) -> float:
    """Penalty for missing fields in scene brief."""
    n = len(brief.missing_fields)
    if n >= 3:
        return 1.0
    if n >= 1:
        return 0.5
    return 0.0


def _over_inference_penalty(brief: SceneBrief, treatment: Treatment) -> float:
    """Penalty for risky-looking phrases in brief / treatment text.

    Uses keyword detection. Risky tokens: explicit emotion narration verbs
    that could imply dialogue or action beyond pressure shifts.
    """
    risky_tokens = (
        "weeping", "crying", "shouting", "whispered", "screamed",
        "embraced", "kissed", "stabbed", "fled to",
    )
    fulltext = " ".join([
        brief.starting_state, brief.pressure_enters,
        brief.turning_point, brief.ending_state,
        treatment.act_1_setup, treatment.act_2_pressure_build,
        treatment.act_3_turn_consequence, treatment.end_hook,
    ]).lower()
    hits = sum(1 for t in risky_tokens if t in fulltext)
    if hits >= 2:
        return 1.0
    if hits == 1:
        return 0.5
    return 0.0


# ---------------------------------------------------------------------------
# Top-level scorer
# ---------------------------------------------------------------------------

def _grade(score: float) -> str:
    if score >= 80:
        return "strong_viable"
    if score >= 65:
        return "viable_with_gaps"
    if score >= 50:
        return "weak_seed"
    return "not_viable"


def score_candidate(
    candidate: StoryCandidate,
    brief: SceneBrief,
    treatment: Treatment,
    *,
    cross_seed_frequency: int | None = None,
) -> ViabilityScore:
    factors = {
        "character_clarity":      _character_clarity(candidate),
        "conflict_clarity":       _conflict_clarity(candidate, brief),
        "pressure_accumulation":  _pressure_accumulation(candidate),
        "turning_point_strength": _turning_point_strength(candidate),
        "relationship_context":   _relationship_context(candidate),
        "unresolved_hook":        _unresolved_hook(candidate),
        "cross_seed_robustness":  _cross_seed_robustness(cross_seed_frequency),
        "adaptation_range":       _adaptation_range(candidate),
    }
    penalties = {
        "missing_context_penalty": _missing_context_penalty(brief),
        "over_inference_penalty":  _over_inference_penalty(brief, treatment),
    }

    score = (
        W_CHARACTER         * factors["character_clarity"]
        + W_CONFLICT          * factors["conflict_clarity"]
        + W_PRESSURE_ACCUM    * factors["pressure_accumulation"]
        + W_TURNING_POINT     * factors["turning_point_strength"]
        + W_RELATIONSHIP      * factors["relationship_context"]
        + W_UNRESOLVED_HOOK   * factors["unresolved_hook"]
        + W_CROSS_SEED        * factors["cross_seed_robustness"]
        + W_ADAPTATION_RANGE  * factors["adaptation_range"]
        + W_MISSING_PENALTY   * penalties["missing_context_penalty"]
        + W_OVER_INFERENCE    * penalties["over_inference_penalty"]
    )
    score = max(0.0, min(100.0, score))
    grade = _grade(score)

    notes: list[str] = []
    if factors["character_clarity"] < 1.0:
        notes.append("character clarity below maximum (archetype fallback or raw ID)")
    if penalties["missing_context_penalty"] > 0:
        notes.append(f"scene brief missing fields: {', '.join(brief.missing_fields)}")
    if penalties["over_inference_penalty"] > 0:
        notes.append("risky phrasing detected (possible over-inference)")
    if factors["cross_seed_robustness"] == 0.0 and cross_seed_frequency is None:
        notes.append("cross-seed data not provided")

    return ViabilityScore(
        candidate_id=candidate.story_candidate_id,
        score=score,
        grade=grade,
        factor_breakdown=factors,
        penalty_breakdown=penalties,
        notes=tuple(notes),
    )
