"""Light disciple agents — John, James, Thomas (Phase 5B).

Each carries 4 axes (theological_understanding, confusion_resistance,
political_sensitivity, rumour_trust_bias) + 4 action weights
(witness, discuss, follow, react_political). Loaded from the shared
``light_disciples.json`` pack.

Design intent (spec §3.3 — graded proximity foundation):
- John: theology-heavy, witnesses often → strong jesus_movement path
- James: politically sensitive → zealot-leaning reaction
- Thomas: low rumour-trust, evidence-seeking → slow to share

Three disciples, same event → three different responses. Behavior tests
in ``tests/test_world/test_light_disciples.py`` pin the differentiation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from world.agents.base import (
    BaseWorldAgent,
    WorldActionDecision,
    WorldAgentContext,
)

_EMITTERS: dict[str, list[str]] = {
    "witness": ["faction_influence_jesus_movement", "rumor_seed"],
    "discuss": [],  # internal, no world effect
    "follow": [],
    "react_political": ["political_tension_signal"],
}


@dataclass(frozen=True)
class DiscipleProfile:
    agent_id: str
    theological_understanding: float
    confusion_resistance: float
    political_sensitivity: float
    rumour_trust_bias: float
    action_weights: dict[str, float]


@dataclass(frozen=True)
class DiscipleOutcome:
    decision: WorldActionDecision
    considered_weights: dict[str, float] = field(default_factory=dict)
    profile: DiscipleProfile | None = None


class _BaseDisciple:
    """Shared implementation of the Light disciple adapter."""

    agent_id: str = "disciple"

    def __init__(self, profile: DiscipleProfile) -> None:
        self.profile = profile
        self.agent_id = profile.agent_id

    def decide(self, ctx: WorldAgentContext) -> WorldActionDecision:
        return self.decide_with_outcome(ctx).decision

    def decide_with_outcome(self, ctx: WorldAgentContext) -> DiscipleOutcome:
        weights = dict(self.profile.action_weights)
        # Contextual tilting:
        # - Low event understanding → discuss ↑ (especially for Thomas)
        event_understanding = float(
            ctx.agent_state_digest.get("event_understanding", 1.0)
        )
        if event_understanding < 0.5:
            weights["discuss"] = weights.get("discuss", 0.0) + (1.0 - event_understanding) * 2.0

        # - High political_tension → react_political ↑ weighted by sensitivity
        political_tension = float(
            ctx.agent_state_digest.get("political_tension", 0.0)
        )
        weights["react_political"] = (
            weights.get("react_political", 0.0)
            + political_tension * self.profile.political_sensitivity * 2.0
        )

        # - Witness spikes when Jesus co-located and theology is high
        if "jesus" in ctx.co_located_agents:
            weights["witness"] = (
                weights.get("witness", 0.0)
                + self.profile.theological_understanding * 1.5
            )

        action_id = max(weights.items(), key=lambda kv: (kv[1], -ord(kv[0][0])))[0]
        effects = self._emit(action_id)
        return DiscipleOutcome(
            decision=WorldActionDecision(action_id=action_id, world_effects=effects),
            considered_weights=weights,
            profile=self.profile,
        )

    @staticmethod
    def _emit(action_id: str) -> dict[str, float]:
        channels = _EMITTERS.get(action_id, [])
        return {ch: 1.0 for ch in channels}

    @classmethod
    def _load_profile(cls, disciples_path: Path | str, key: str) -> DiscipleProfile:
        payload = json.loads(Path(disciples_path).read_text(encoding="utf-8"))
        entry = payload[key]
        return DiscipleProfile(
            agent_id=entry["agent_id"],
            theological_understanding=float(entry.get("theological_understanding", 0.5)),
            confusion_resistance=float(entry.get("confusion_resistance", 0.5)),
            political_sensitivity=float(entry.get("political_sensitivity", 0.5)),
            rumour_trust_bias=float(entry.get("rumour_trust_bias", 0.5)),
            action_weights=dict(entry.get("action_weights", {})),
        )


class JohnAgent(_BaseDisciple):
    @classmethod
    def from_disciples_path(cls, path: Path | str) -> "JohnAgent":
        return cls(cls._load_profile(path, "john"))


class JamesAgent(_BaseDisciple):
    @classmethod
    def from_disciples_path(cls, path: Path | str) -> "JamesAgent":
        return cls(cls._load_profile(path, "james"))


class ThomasAgent(_BaseDisciple):
    @classmethod
    def from_disciples_path(cls, path: Path | str) -> "ThomasAgent":
        return cls(cls._load_profile(path, "thomas"))


# Protocol sanity (each constructed with a default profile at import).
_john = JohnAgent(DiscipleProfile(
    agent_id="john", theological_understanding=0.8, confusion_resistance=0.7,
    political_sensitivity=0.3, rumour_trust_bias=0.6, action_weights={"discuss": 1.0},
))
_: BaseWorldAgent = _john
