"""StoryCandidate model — Stage 6 (creator-facing card).

Per `docs/WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md` §6.

A StoryCandidate is the *creator-facing* artifact that sits one layer above
StoryThread. StoryThread is a data structure ("which moments are linked");
StoryCandidate is a card a creator can choose ("what could this become?").

Plan §10.2 forbids: completed novel prose / dialogue / screenplay / over-
narrated emotion. Plan §10.2 allows: one-line premise, arc summary,
turning-point summaries, adaptation hooks, creative-use suggestions.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TurningPoint:
    """One narratively prominent moment within a thread.

    Selected by the TurningPoint selector (Stage 6 / Phase C). A frozen
    record so the same selector run always produces the same set.
    """
    tick: int
    moment_ids: tuple[str, ...]
    label: str                        # e.g. "authority pressure spike"
    summary: str                      # one-line, neutral, source-grounded
    provenance: str = "source_inferred"

    def to_dict(self) -> dict:
        return {
            "tick": self.tick,
            "moment_ids": list(self.moment_ids),
            "label": self.label,
            "summary": self.summary,
            "provenance": self.provenance,
        }


@dataclass(frozen=True)
class StoryCandidate:
    """Creator-facing card built from a StoryThread + IdentityResolver."""
    story_candidate_id: str
    source_thread_id: str
    title: str
    one_line_premise: str
    main_characters: tuple[str, ...]
    supporting_characters_or_groups: tuple[str, ...]
    core_conflict: str
    arc_summary: str
    key_turning_points: tuple[TurningPoint, ...]
    relationship_dynamics: tuple[str, ...]
    world_pressure_context: tuple[str, ...]
    unresolved_question: str
    usable_formats: tuple[str, ...]
    adaptation_hooks: dict[str, str]    # format → one-line hook
    evidence_summary: str
    provenance_summary: dict[str, int]
    risk_notes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.story_candidate_id:
            raise ValueError("story_candidate_id required")
        if not self.source_thread_id:
            raise ValueError("source_thread_id required")
        if not self.title:
            raise ValueError("title required")

    def to_dict(self) -> dict:
        return {
            "story_candidate_id": self.story_candidate_id,
            "source_thread_id": self.source_thread_id,
            "title": self.title,
            "one_line_premise": self.one_line_premise,
            "main_characters": list(self.main_characters),
            "supporting_characters_or_groups": list(self.supporting_characters_or_groups),
            "core_conflict": self.core_conflict,
            "arc_summary": self.arc_summary,
            "key_turning_points": [tp.to_dict() for tp in self.key_turning_points],
            "relationship_dynamics": list(self.relationship_dynamics),
            "world_pressure_context": list(self.world_pressure_context),
            "unresolved_question": self.unresolved_question,
            "usable_formats": list(self.usable_formats),
            "adaptation_hooks": dict(self.adaptation_hooks),
            "evidence_summary": self.evidence_summary,
            "provenance_summary": dict(self.provenance_summary),
            "risk_notes": list(self.risk_notes),
        }
