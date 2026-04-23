"""BarabbasAgent — Light agent (Phase 5B).

Canonical activation: Barabbas is only active on specific day indices
(default: day 14, the trial scene). Outside those days ``decide``
returns an ``idle`` no-op.

When active, Barabbas contributes a zealot-side variable into the
crowd-choice context via the ``zealot_reputation_signal`` channel.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from world.agents.base import (
    BaseWorldAgent,
    WorldActionDecision,
    WorldAgentContext,
)

ImprisonmentStatus = Literal["imprisoned", "released", "escaped"]


@dataclass(frozen=True)
class BarabbasState:
    imprisonment_status: ImprisonmentStatus = "imprisoned"
    zealot_reputation: float = 0.7


@dataclass(frozen=True)
class BarabbasOutcome:
    decision: WorldActionDecision
    active: bool
    considered_weights: dict[str, float] = field(default_factory=dict)


class BarabbasAgent:
    agent_id: str = "barabbas"

    def __init__(self, *, world_profile: dict[str, Any] | None = None) -> None:
        self.world_profile = world_profile or {}
        init = self.world_profile.get("initial_state", {})
        self.state = BarabbasState(
            imprisonment_status=init.get("imprisonment_status", "imprisoned"),
            zealot_reputation=float(init.get("zealot_reputation", 0.7)),
        )
        self._active_days = [
            int(d) for d in self.world_profile.get("canonical_activation_days", [])
        ]
        self._action_weights: dict[str, float] = self.world_profile.get(
            "action_weights", {}
        )

    @classmethod
    def from_world_profile_path(cls, path: Path | str) -> "BarabbasAgent":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(world_profile=payload)

    def decide(self, ctx: WorldAgentContext) -> WorldActionDecision:
        return self.decide_with_outcome(ctx).decision

    def decide_with_outcome(self, ctx: WorldAgentContext) -> BarabbasOutcome:
        if ctx.day_index not in self._active_days:
            return BarabbasOutcome(
                decision=WorldActionDecision(
                    action_id="idle",
                    world_effects={},
                    meta={"reason": "outside_activation_days"},
                ),
                active=False,
                considered_weights={"idle": 1.0},
            )
        # Active. Pick highest-weighted action.
        weights = dict(self._action_weights) or {"wait_for_release": 1.0}
        action_id = max(weights.items(), key=lambda kv: (kv[1], -ord(kv[0][0])))[0]
        effects = {
            "zealot_reputation_signal": self.state.zealot_reputation,
            "crowd_choice_variable": 1.0,
        }
        return BarabbasOutcome(
            decision=WorldActionDecision(
                action_id=action_id, world_effects=effects,
                meta={"activation": "canonical", "day_index": ctx.day_index},
            ),
            active=True,
            considered_weights=weights,
        )


_: BaseWorldAgent = BarabbasAgent()
