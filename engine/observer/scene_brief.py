"""Scene Brief — Stage B (Story Viability Validation).

Per `docs/WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md` §6.

Converts a StoryCandidate into a *Scene Brief* — a 6-section structured
description that a creator can read and decide "could I actually write
this scene?". Templates are deterministic, populated from source-derived
candidate fields.

Plan §6 forbidden:
    - dialogue / over-narrated emotion / fabricated events / locations
Plan §6 allowed:
    - mapping pressure to neutral phrases (already done by IdentityResolver)
    - using the candidate's own premise / arc / turning points verbatim
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.observer.story_candidate import StoryCandidate

# Pressure family → external vs internal classification
_EXTERNAL_PRESSURES = {
    "authority_vigilance", "public_suspicion", "blame_concentration",
    "group_tension", "crowd_mood",
}
_INTERNAL_PRESSURES = {"fear", "hope", "shame_self", "confusion", "grief", "love", "awe"}


# Scene-question template per core_conflict (plan §6 verbatim)
_SCENE_QUESTION_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival":            "Will {main} stay loyal when survival pressure rises?",
    "uncertainty_vs_commitment":      "Will {main} commit despite uncertainty?",
    "control_vs_exposure":            "Will control hold as exposure risk increases?",
    "collective_fear_vs_scapegoating": "Who becomes the target when fear concentrates?",
    "identity_vs_failure":             "Can {main} preserve identity under visible failure?",
    "trust_vs_self_protection":        "Will {main} keep trusting when distance feels safer?",
    "atmosphere_vs_action":            "Does the changed atmosphere translate into action?",
}
_SCENE_QUESTION_FALLBACK = "What does this pressure pattern lead {main} toward?"


@dataclass(frozen=True)
class SceneBrief:
    candidate_id: str
    main_character: str
    supporting_context: tuple[str, ...]
    core_conflict: str
    scene_question: str
    external_pressure: tuple[str, ...]
    internal_pressure: tuple[str, ...]
    group_world_context: tuple[str, ...]
    starting_state: str
    pressure_enters: str
    turning_point: str
    ending_state: str
    do_not_add: tuple[str, ...]      # creative constraint (negative)
    must_preserve: tuple[str, ...]   # creative constraint (positive)
    source_derived_count: int
    source_inferred_count: int
    completeness: str                # "complete" / "scene_brief_incomplete"
    missing_fields: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "main_character": self.main_character,
            "supporting_context": list(self.supporting_context),
            "core_conflict": self.core_conflict,
            "scene_question": self.scene_question,
            "external_pressure": list(self.external_pressure),
            "internal_pressure": list(self.internal_pressure),
            "group_world_context": list(self.group_world_context),
            "starting_state": self.starting_state,
            "pressure_enters": self.pressure_enters,
            "turning_point": self.turning_point,
            "ending_state": self.ending_state,
            "do_not_add": list(self.do_not_add),
            "must_preserve": list(self.must_preserve),
            "source_derived_count": self.source_derived_count,
            "source_inferred_count": self.source_inferred_count,
            "completeness": self.completeness,
            "missing_fields": list(self.missing_fields),
        }


# ---------------------------------------------------------------------------
# Field extraction from candidate
# ---------------------------------------------------------------------------

def _classify_pressures(pressures: list[str]) -> tuple[list[str], list[str]]:
    ext = [p for p in pressures if p in _EXTERNAL_PRESSURES]
    int_ = [p for p in pressures if p in _INTERNAL_PRESSURES]
    return ext, int_


def _flatten_pressures_from_candidate(c: StoryCandidate) -> list[str]:
    """Pull all pressure mentions from world_pressure_context phrases.

    Phrases are like 'authority pressure closes in' / 'fear intensifies'.
    We map them back to the underlying pressure name via a reverse table.
    """
    reverse = {
        "fear intensifies":            "fear",
        "fear eases":                  "fear",
        "hope steadies":               "hope",
        "resolve weakens":             "hope",
        "shame accumulates":           "shame_self",
        "shame relaxes":               "shame_self",
        "authority pressure closes in":"authority_vigilance",
        "authority pressure recedes":  "authority_vigilance",
        "public suspicion rises":      "public_suspicion",
        "public suspicion settles":    "public_suspicion",
        "blame begins to concentrate": "blame_concentration",
        "blame disperses":             "blame_concentration",
        "group tension sharpens":      "group_tension",
        "group tension softens":       "group_tension",
        "crowd mood shifts":           "crowd_mood",
    }
    out: list[str] = []
    for phrase in c.world_pressure_context:
        p = reverse.get(phrase)
        if p and p not in out:
            out.append(p)
    # Also pull from arc_summary tokens (cheap)
    for phrase, pressure in reverse.items():
        if phrase in c.arc_summary and pressure not in out:
            out.append(pressure)
    return out


def _starting_state(c: StoryCandidate) -> str:
    if c.key_turning_points:
        first = c.key_turning_points[0]
        return f"{c.main_characters[0] if c.main_characters else 'the central agent'} " \
               f"at tick {first.tick}: {first.label} ({first.summary})"
    return (
        f"{c.main_characters[0] if c.main_characters else 'the central agent'} "
        f"in {c.supporting_characters_or_groups[-1] if c.supporting_characters_or_groups else 'the world'} "
        f"under {c.core_conflict}"
    )


def _pressure_enters(c: StoryCandidate) -> str:
    if not c.world_pressure_context:
        return f"pressure pattern: {c.arc_summary}"
    return "; ".join(c.world_pressure_context)


def _turning_point_summary(c: StoryCandidate) -> str:
    """Pick the strongest turning point — preference order:
    co-occurring pressure > sustained pressure begins > world pressure shift > first.
    """
    if not c.key_turning_points:
        return ""
    priority = [
        "co-occurring pressure",
        "sustained pressure begins",
        "world pressure shift",
    ]
    for label in priority:
        for tp in c.key_turning_points:
            if tp.label == label:
                return f"t{tp.tick} ({tp.label}): {tp.summary}"
    tp = c.key_turning_points[0]
    return f"t{tp.tick} ({tp.label}): {tp.summary}"


def _ending_state(c: StoryCandidate) -> str:
    """Final state inferred from arc_summary + unresolved_question."""
    arc_tail = c.arc_summary.split("→")[-1].strip() if "→" in c.arc_summary else c.arc_summary
    return f"ending state — {arc_tail}; question still open: {c.unresolved_question}"


_DO_NOT_ADD_BASE: tuple[str, ...] = (
    "no dialogue lines",
    "no specific physical actions beyond pressure shifts",
    "no events not present in source moments",
    "no location descriptions beyond group context",
    "no new characters",
    "no historical / scriptural details not in observer dump",
)

_MUST_PRESERVE_BASE: tuple[str, ...] = (
    "main character identity from candidate.main_characters",
    "core_conflict label from candidate",
    "tick ordering of turning points",
    "provenance class on every claim",
    "unresolved_question as the scene's exit hook",
)


# ---------------------------------------------------------------------------
# Top-level builder
# ---------------------------------------------------------------------------

def build_scene_brief(c: StoryCandidate) -> SceneBrief:
    main = c.main_characters[0] if c.main_characters else ""
    pressures = _flatten_pressures_from_candidate(c)
    ext, int_ = _classify_pressures(pressures)

    question_template = _SCENE_QUESTION_BY_CONFLICT.get(
        c.core_conflict, _SCENE_QUESTION_FALLBACK
    )
    scene_question = question_template.format(main=main or "the central agent")

    starting = _starting_state(c)
    enters = _pressure_enters(c)
    turn = _turning_point_summary(c)
    ending = _ending_state(c)

    # Completeness check — plan §6 6 fields
    missing: list[str] = []
    if not main:
        missing.append("main_character")
    if not scene_question:
        missing.append("scene_question")
    if not int_:
        missing.append("internal_pressure")
    if not ext:
        missing.append("external_pressure")
    if not turn:
        missing.append("turning_point")
    if not ending:
        missing.append("ending_state")
    completeness = "scene_brief_incomplete" if missing else "complete"

    return SceneBrief(
        candidate_id=c.story_candidate_id,
        main_character=main or "(unnamed)",
        supporting_context=c.supporting_characters_or_groups,
        core_conflict=c.core_conflict,
        scene_question=scene_question,
        external_pressure=tuple(ext),
        internal_pressure=tuple(int_),
        group_world_context=c.world_pressure_context,
        starting_state=starting,
        pressure_enters=enters,
        turning_point=turn,
        ending_state=ending,
        do_not_add=_DO_NOT_ADD_BASE,
        must_preserve=_MUST_PRESERVE_BASE,
        source_derived_count=c.provenance_summary.get("source_derived", 0),
        source_inferred_count=c.provenance_summary.get("source_inferred", 0),
        completeness=completeness,
        missing_fields=tuple(missing),
    )
