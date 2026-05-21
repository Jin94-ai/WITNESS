"""Moment — Narrative Mining Layer Phase 1.

Per `docs/WITNESS_NARRATIVE_MINING_PLAN.md` §3.1, §4.1.

Moment is a unit of *narratively meaningful change* observed at a single tick
or short tick range. It is broader than a Candidate: a Candidate is "a
notable event"; a Moment is "a change that could become part of a story".

ABSOLUTE Rules (additive):
    - Rule #1: no person hardcoding. agent_id comes from data.
    - Rule #6: existing Observer / Candidate API is not modified.
    - Provenance: every Moment carries a class label.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

MomentType = Literal[
    "agent_state_shift",      # 인물 상태 변화 (fear/hope/dominant_state)
    "relationship_drift",     # 관계 변화 (engine doesn't yet emit, reserved)
    "group_tension_shift",    # 집단 긴장 변화 (group.tension / dominant_mode)
    "world_pressure_shift",   # 세계 압력 변화 (crowd_mood / authority / blame)
    "choice_pattern",         # 반복 선택 / 행동 경향 (engine-action level, reserved)
    "conflict_marker",        # 갈등 축이 드러나는 순간 (multi-signal)
    "event_ripple",           # 사건 이후 여파 (active_events 후속)
    "unresolved_thread",      # 미해결 상태 지속 (sustained pressure)
]

ProvenanceClass = Literal[
    "source_derived",
    "source_inferred",
    "not_used",
]


@dataclass(frozen=True)
class Moment:
    """A narratively meaningful change at a tick or tick range.

    Frozen to enforce immutability — Moments are observation records, not
    mutable state. To "update" a Moment, replace it (dataclasses.replace).
    """
    moment_id: str
    tick: int
    tick_range: tuple[int, int]
    moment_type: MomentType
    agents: tuple[str, ...] = field(default_factory=tuple)
    groups: tuple[str, ...] = field(default_factory=tuple)
    events: tuple[str, ...] = field(default_factory=tuple)
    pressures: tuple[str, ...] = field(default_factory=tuple)
    signals: tuple[str, ...] = field(default_factory=tuple)
    summary: str = ""
    salience_score: float = 0.0
    provenance: ProvenanceClass = "source_derived"

    def __post_init__(self) -> None:
        if self.tick_range[0] > self.tick_range[1]:
            raise ValueError(
                f"Moment {self.moment_id}: tick_range[0] ({self.tick_range[0]}) "
                f"must be ≤ tick_range[1] ({self.tick_range[1]})"
            )
        if not (self.tick_range[0] <= self.tick <= self.tick_range[1]):
            raise ValueError(
                f"Moment {self.moment_id}: tick {self.tick} outside range {self.tick_range}"
            )
        if not (0.0 <= self.salience_score <= 1.0):
            raise ValueError(
                f"Moment {self.moment_id}: salience_score {self.salience_score} outside [0, 1]"
            )

    def to_dict(self) -> dict:
        """Serialize for JSON dump (tuples → lists for JSON compat)."""
        return {
            "moment_id": self.moment_id,
            "tick": self.tick,
            "tick_range": list(self.tick_range),
            "moment_type": self.moment_type,
            "agents": list(self.agents),
            "groups": list(self.groups),
            "events": list(self.events),
            "pressures": list(self.pressures),
            "signals": list(self.signals),
            "summary": self.summary,
            "salience_score": round(self.salience_score, 3),
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Moment":
        return cls(
            moment_id=d["moment_id"],
            tick=d["tick"],
            tick_range=tuple(d["tick_range"]),
            moment_type=d["moment_type"],
            agents=tuple(d.get("agents", [])),
            groups=tuple(d.get("groups", [])),
            events=tuple(d.get("events", [])),
            pressures=tuple(d.get("pressures", [])),
            signals=tuple(d.get("signals", [])),
            summary=d.get("summary", ""),
            salience_score=d.get("salience_score", 0.0),
            provenance=d.get("provenance", "source_derived"),
        )
