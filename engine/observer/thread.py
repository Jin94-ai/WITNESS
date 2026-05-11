"""Thread models — MomentLink + StoryThread (Narrative Mining Phase 2-3).

Per `docs/WITNESS_NARRATIVE_MINING_PLAN.md` §4.3, §4.4.

Pure dataclasses. Linking logic and thread building live in
`engine.observer.thread_builder`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


# ---------------------------------------------------------------------------
# MomentLink — pairwise edge in the moment graph
# ---------------------------------------------------------------------------

LinkType = Literal[
    "same_agent",            # share at least one agent id
    "same_group",            # share at least one group id
    "same_relationship",     # reserved (engine doesn't yet emit relationship deltas)
    "same_pressure",         # share at least one pressure axis
    "same_conflict_axis",    # share a conflict_marker / signal family
    "causal_order",          # A's signals plausibly enable B's preconditions
    "temporal_continuity",   # close in tick distance, no other link required
]


@dataclass(frozen=True)
class MomentLink:
    """Edge connecting two moments in the link graph.

    Frozen — links are observation records, not mutable state.
    """
    source_moment_id: str
    target_moment_id: str
    link_type: LinkType
    weight: float
    rationale: str

    def __post_init__(self) -> None:
        if not (0.0 <= self.weight <= 1.0):
            raise ValueError(
                f"MomentLink weight {self.weight} outside [0, 1]"
            )
        if self.source_moment_id == self.target_moment_id:
            raise ValueError(
                f"MomentLink: source == target ({self.source_moment_id})"
            )

    def to_dict(self) -> dict:
        return {
            "source": self.source_moment_id,
            "target": self.target_moment_id,
            "type": self.link_type,
            "weight": round(self.weight, 3),
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MomentLink":
        return cls(
            source_moment_id=d["source"],
            target_moment_id=d["target"],
            link_type=d["type"],
            weight=d["weight"],
            rationale=d.get("rationale", ""),
        )


# ---------------------------------------------------------------------------
# StoryThread — connected component / path in the moment graph (Phase 3)
# ---------------------------------------------------------------------------

ArcDirection = Literal[
    "stability_to_breakdown",
    "fear_to_withdrawal",
    "trust_to_distance",
    "loyalty_to_betrayal_risk",
    "confusion_to_commitment",
    "isolation_to_dependence",
    "tension_to_collective_action",
    "unknown",
]


@dataclass(frozen=True)
class StoryThread:
    """A narrative-grade sequence of moments connected by shared context.

    Frozen. Provenance is `source_inferred` — thread membership is a rule
    application over Moments and links, not raw observation.
    """
    thread_id: str
    title: str
    main_agents: tuple[str, ...]
    supporting_agents: tuple[str, ...] = field(default_factory=tuple)
    groups: tuple[str, ...] = field(default_factory=tuple)
    core_conflict: str = "unknown"
    arc_direction: ArcDirection = "unknown"
    moment_ids: tuple[str, ...] = field(default_factory=tuple)
    start_tick: int = 0
    end_tick: int = 0
    pressure_history: tuple[str, ...] = field(default_factory=tuple)
    relationship_drift: tuple[str, ...] = field(default_factory=tuple)
    unresolved_question: str = ""
    story_potential_score: float = 0.0
    usable_as: tuple[str, ...] = field(default_factory=tuple)
    provenance: str = "source_inferred"

    def __post_init__(self) -> None:
        if self.start_tick > self.end_tick:
            raise ValueError(
                f"StoryThread {self.thread_id}: start_tick {self.start_tick} > "
                f"end_tick {self.end_tick}"
            )
        if not (0.0 <= self.story_potential_score <= 1.0):
            raise ValueError(
                f"StoryThread {self.thread_id}: score {self.story_potential_score} "
                f"outside [0, 1]"
            )
        if len(self.moment_ids) < 1:
            raise ValueError(
                f"StoryThread {self.thread_id}: moment_ids must be non-empty"
            )

    def to_dict(self) -> dict:
        return {
            "thread_id": self.thread_id,
            "title": self.title,
            "main_agents": list(self.main_agents),
            "supporting_agents": list(self.supporting_agents),
            "groups": list(self.groups),
            "core_conflict": self.core_conflict,
            "arc_direction": self.arc_direction,
            "moment_ids": list(self.moment_ids),
            "start_tick": self.start_tick,
            "end_tick": self.end_tick,
            "pressure_history": list(self.pressure_history),
            "relationship_drift": list(self.relationship_drift),
            "unresolved_question": self.unresolved_question,
            "story_potential_score": round(self.story_potential_score, 3),
            "usable_as": list(self.usable_as),
            "provenance": self.provenance,
        }
