"""PilateAgent — Full world-side agent (Phase 5B).

State: ``alertness``, ``political_pressure``, ``wife_dream_influence``.
Actions: ``delay_judgment`` / ``consult_rome`` / ``wash_hands`` /
``order_action``.

Faction linkage:
- direct: ``factions.romans``
- indirect via Caiaphas: ``factions.pharisees``
- indirect via taxation: ``factions.zealots``

Design notes:
- The ``lenient_pilate`` intervention currently in Spike 4 translates to
  a ``political_pressure`` override (low value). The intervention JSON
  stays as-is; downstream runners may read pilate state from this
  agent instead of from the old politics layer. Backwards-compat is
  the runner's responsibility, not this file's (per Rule #6 we don't
  touch engine/).
- Canonical constraints short-circuit free choice just like JesusAgent.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from world.agents.base import (
    BaseWorldAgent,
    WorldActionDecision,
    WorldAgentContext,
)

# Multi-path emitter: every action fans out into 0+ world-effect channels.
_ACTION_EMITTERS: dict[str, list[tuple[str, str | None]]] = {
    "delay_judgment": [
        ("political_pressure_relief", "delay_political_pressure_relief"),
    ],
    "consult_rome": [
        ("political_pressure_relief", "consult_political_pressure_delay"),
    ],
    "wash_hands": [
        # Canonical-only action. Symbolic — no direct world effect beyond
        # the canonical timeline mark itself.
    ],
    "order_action": [
        ("roman_alertness_boost", "order_roman_alertness_boost"),
        ("taxation_intensity_pressure", "order_taxation_intensity_pressure"),
    ],
}


@dataclass(frozen=True)
class PilateState:
    """Mutable-ish state snapshot for Pilate. Kept lightweight — the
    world runner owns the real state; this is the adapter's view."""

    alertness: float = 0.3
    political_pressure: float = 0.4
    wife_dream_influence: float = 0.0


@dataclass(frozen=True)
class PilateAgentOutcome:
    decision: WorldActionDecision
    considered_weights: dict[str, float] = field(default_factory=dict)
    canonical_fired: bool = False
    state_after: PilateState | None = None


class PilateAgent:
    """Full world-side Pilate agent (BaseWorldAgent Protocol)."""

    agent_id: str = "pilate"

    def __init__(
        self, *, world_profile: dict[str, Any] | None = None,
    ) -> None:
        self.world_profile = world_profile or {}
        init = self.world_profile.get("initial_state", {})
        self.state = PilateState(
            alertness=float(init.get("alertness", 0.3)),
            political_pressure=float(init.get("political_pressure", 0.4)),
            wife_dream_influence=float(init.get("wife_dream_influence", 0.0)),
        )
        self._weights: dict[str, float] = self.world_profile.get("world_weights", {})
        self._influence: dict[str, float] = self.world_profile.get("influence_paths", {})
        self._canonical: list[dict[str, Any]] = self.world_profile.get(
            "canonical_constraints", []
        )

    # ------------------------------------------------------------------
    @classmethod
    def from_world_profile_path(cls, path: Path | str) -> "PilateAgent":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(world_profile=payload)

    # ------------------------------------------------------------------
    def decide(self, ctx: WorldAgentContext) -> WorldActionDecision:
        return self.decide_with_outcome(ctx).decision

    def decide_with_outcome(self, ctx: WorldAgentContext) -> PilateAgentOutcome:
        # 1. Apply canonical state effects (wife dream) before action pick.
        forced = self._canonical_lookup(ctx.day_index)
        new_state = self.state
        if forced is not None and "state_effect" in forced:
            new_state = self._apply_state_effect(new_state, forced["state_effect"])

        # 2. Canonical forced action (wash_hands).
        if forced is not None and forced.get("forced_action"):
            action_id = forced["forced_action"]
            effects = self._emit_effects(action_id)
            return PilateAgentOutcome(
                decision=WorldActionDecision(
                    action_id=action_id, world_effects=effects,
                    meta={"canonical_id": forced.get("canonical_id")},
                ),
                considered_weights={action_id: 1.0},
                canonical_fired=True,
                state_after=new_state,
            )

        # 3. Free decision.
        weights = self._compute_weights(new_state, ctx)
        action_id = self._pick_highest(weights)
        effects = self._emit_effects(action_id)
        return PilateAgentOutcome(
            decision=WorldActionDecision(action_id=action_id, world_effects=effects),
            considered_weights=weights,
            canonical_fired=False,
            state_after=new_state,
        )

    # ------------------------------------------------------------------
    def _compute_weights(
        self, state: PilateState, ctx: WorldAgentContext,
    ) -> dict[str, float]:
        base = {
            "delay_judgment": float(self._weights.get("delay_judgment_base", 1.5)),
            "consult_rome": float(self._weights.get("consult_rome_base", 0.8)),
            "wash_hands": float(self._weights.get("wash_hands_base", 0.3)),
            "order_action": float(self._weights.get("order_action_base", 1.0)),
        }

        # delay_judgment ↑ when political_pressure high.
        delay_thr = float(self._weights.get("delay_pressure_threshold", 0.6))
        if state.political_pressure >= delay_thr:
            base["delay_judgment"] += state.political_pressure * 2.0

        # consult_rome ↑ when pressure is very high (need cover).
        consult_thr = float(self._weights.get("consult_pressure_threshold", 0.7))
        if state.political_pressure >= consult_thr:
            base["consult_rome"] += state.political_pressure * float(
                self._weights.get("alertness_consult_factor", 0.5)
            )

        # order_action ↑ when alertness above threshold (need force).
        order_thr = float(self._weights.get("order_alertness_threshold", 0.7))
        if state.alertness >= order_thr:
            base["order_action"] += state.alertness * float(
                self._weights.get("alertness_roman_factor", 2.0)
            )

        # wife_dream_influence: bias wash_hands + delay_judgment.
        if state.wife_dream_influence > 0.5:
            base["wash_hands"] += state.wife_dream_influence * 2.0
            base["delay_judgment"] += state.wife_dream_influence * 1.0

        return base

    @staticmethod
    def _pick_highest(weights: dict[str, float]) -> str:
        return max(weights.items(), key=lambda kv: (kv[1], -ord(kv[0][0])))[0]

    def _emit_effects(self, action_id: str) -> dict[str, float]:
        specs = _ACTION_EMITTERS.get(action_id, [])
        out: dict[str, float] = {}
        for channel_id, param_key in specs:
            mag = 1.0 if param_key is None else float(
                self._influence.get(param_key, 0.5)
            )
            out[channel_id] = out.get(channel_id, 0.0) + mag
        return out

    def _canonical_lookup(self, day_index: int) -> dict[str, Any] | None:
        for entry in self._canonical:
            if int(entry.get("day_index", -1)) == day_index:
                return entry
        return None

    @staticmethod
    def _apply_state_effect(
        state: PilateState, effect: dict[str, float],
    ) -> PilateState:
        return PilateState(
            alertness=float(effect.get("alertness", state.alertness)),
            political_pressure=float(effect.get(
                "political_pressure", state.political_pressure
            )),
            wife_dream_influence=float(effect.get(
                "wife_dream_influence", state.wife_dream_influence
            )),
        )

    # ------------------------------------------------------------------
    def describe_influence_paths(self) -> dict[str, list[str]]:
        return {
            action: [ch for ch, _ in specs]
            for action, specs in _ACTION_EMITTERS.items()
        }


# Runtime-protocol sanity.
_: BaseWorldAgent = PilateAgent()
