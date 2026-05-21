"""Narrative Opportunity — Phase 4 model.

Per `docs/WITNESS_NARRATIVE_MINING_PLAN.md` §3.3.

A NarrativeOpportunity is a *creator-facing* abstraction over a StoryThread:
short logline, creative-use tags, and the unresolved question. The data
layer (StoryThread) carries technical evidence; this layer carries the
choosable summary.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from engine.observer.thread import StoryThread

OpportunityRank = Literal["strong", "usable", "weak", "hold"]


@dataclass(frozen=True)
class NarrativeOpportunity:
    thread_id: str
    title: str
    logline: str
    core_conflict: str
    arc_direction: str
    unresolved_question: str
    creative_uses: tuple[str, ...]
    score: float
    rank: OpportunityRank
    main_agents: tuple[str, ...] = field(default_factory=tuple)
    groups: tuple[str, ...] = field(default_factory=tuple)
    start_tick: int = 0
    end_tick: int = 0
    moment_count: int = 0

    def to_dict(self) -> dict:
        return {
            "thread_id": self.thread_id,
            "title": self.title,
            "logline": self.logline,
            "core_conflict": self.core_conflict,
            "arc_direction": self.arc_direction,
            "unresolved_question": self.unresolved_question,
            "creative_uses": list(self.creative_uses),
            "score": round(self.score, 3),
            "rank": self.rank,
            "main_agents": list(self.main_agents),
            "groups": list(self.groups),
            "start_tick": self.start_tick,
            "end_tick": self.end_tick,
            "moment_count": self.moment_count,
        }


# ---------------------------------------------------------------------------
# Logline templates by core_conflict (deterministic, no LLM)
# ---------------------------------------------------------------------------

_LOGLINE_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival":
        "Central agents stay in place under rising pressure until survival "
        "instinct begins to outweigh loyalty.",
    "trust_vs_self_protection":
        "Trust between agents erodes as protective distance widens.",
    "collective_fear_vs_scapegoating":
        "Group fear concentrates into blame, looking for a target.",
    "control_vs_exposure":
        "Authority intensifies its watch as suspicion spreads through the crowd.",
    "identity_vs_failure":
        "An agent's hope falters and shame rises in the same arc.",
    "uncertainty_vs_commitment":
        "Pressure stays on without a commitment moment — drift continues.",
    "atmosphere_vs_action":
        "The world's mood shifts but no decisive action follows.",
    "unknown":
        "An unresolved sequence of pressure and state change.",
}


def _rank_for_score(score: float) -> OpportunityRank:
    if score >= 0.80:
        return "strong"
    if score >= 0.60:
        return "usable"
    if score >= 0.40:
        return "weak"
    return "hold"


def from_thread(t: StoryThread) -> NarrativeOpportunity:
    return NarrativeOpportunity(
        thread_id=t.thread_id,
        title=t.title,
        logline=_LOGLINE_BY_CONFLICT.get(t.core_conflict, _LOGLINE_BY_CONFLICT["unknown"]),
        core_conflict=t.core_conflict,
        arc_direction=t.arc_direction,
        unresolved_question=t.unresolved_question,
        creative_uses=t.usable_as,
        score=t.story_potential_score,
        rank=_rank_for_score(t.story_potential_score),
        main_agents=t.main_agents,
        groups=t.groups,
        start_tick=t.start_tick,
        end_tick=t.end_tick,
        moment_count=len(t.moment_ids),
    )
