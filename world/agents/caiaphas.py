"""CaiaphasAgent — Full world-side agent with hub role (Phase 5B).

Hub = Caiaphas's actions emit into BOTH Pharisees and Sadducees channels
simultaneously (for most actions). This is the structural foundation for
future graded-control experiments: an intervention that removes Caiaphas
would split into pharisees/sadducees responses through their shared hub,
not a clean single-faction cut.

State:
- ``sanhedrin_authority`` — influence within the Sanhedrin
- ``roman_relationship`` — closeness to Rome (too close → pharisees friction)
- ``theological_anxiety`` — pressure from the Jesus movement's influence

Actions:
- ``convene_sanhedrin`` (hub): pharisees_alignment + sadducees_alignment
- ``appeal_to_rome``         : pilate_pressure_boost
- ``temple_decree``          : temple_economy_price_adjust + sadducees_alignment
- ``confront_movement``      : jesus_movement_penalty + authority_threat + pharisees_alignment
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

# Multi-channel emitters. Hub actions name BOTH pharisees and sadducees.
_ACTION_EMITTERS: dict[str, list[tuple[str, str]]] = {
    "convene_sanhedrin": [
        ("faction_influence_pharisees", "convene_pharisees_boost"),
        ("faction_influence_sadducees", "convene_sadducees_boost"),
    ],
    "appeal_to_rome": [
        ("pilate_political_pressure", "appeal_pilate_pressure_boost"),
    ],
    "temple_decree": [
        ("temple_economy_price_adjust", "temple_decree_price_adjust"),
        ("faction_influence_sadducees", "convene_sadducees_boost"),
    ],
    "confront_movement": [
        ("faction_influence_jesus_movement", "confront_jesus_movement_penalty"),
        ("authority_threat", "confront_authority_threat"),
        ("faction_influence_pharisees", "convene_pharisees_boost"),
    ],
}


@dataclass(frozen=True)
class CaiaphasState:
    sanhedrin_authority: float = 0.7
    roman_relationship: float = 0.6
    theological_anxiety: float = 0.3


@dataclass(frozen=True)
class CaiaphasAgentOutcome:
    decision: WorldActionDecision
    considered_weights: dict[str, float] = field(default_factory=dict)
    state_after: CaiaphasState | None = None


class CaiaphasAgent:
    """Hub agent — actions fan out into multiple faction channels."""

    agent_id: str = "caiaphas"

    def __init__(self, *, world_profile: dict[str, Any] | None = None) -> None:
        self.world_profile = world_profile or {}
        init = self.world_profile.get("initial_state", {})
        self.state = CaiaphasState(
            sanhedrin_authority=float(init.get("sanhedrin_authority", 0.7)),
            roman_relationship=float(init.get("roman_relationship", 0.6)),
            theological_anxiety=float(init.get("theological_anxiety", 0.3)),
        )
        self._weights: dict[str, float] = self.world_profile.get("world_weights", {})
        self._influence: dict[str, float] = self.world_profile.get("influence_paths", {})
        self._hub: dict[str, list[str]] = self.world_profile.get("hub_channels", {})

    @classmethod
    def from_world_profile_path(cls, path: Path | str) -> "CaiaphasAgent":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(world_profile=payload)

    # ------------------------------------------------------------------
    def decide(self, ctx: WorldAgentContext) -> WorldActionDecision:
        return self.decide_with_outcome(ctx).decision

    def decide_with_outcome(self, ctx: WorldAgentContext) -> CaiaphasAgentOutcome:
        weights = self._compute_weights(ctx)
        action_id = max(weights.items(), key=lambda kv: (kv[1], -ord(kv[0][0])))[0]
        effects = self._emit_effects(action_id)
        return CaiaphasAgentOutcome(
            decision=WorldActionDecision(action_id=action_id, world_effects=effects),
            considered_weights=weights,
            state_after=self.state,
        )

    # ------------------------------------------------------------------
    def _compute_weights(self, ctx: WorldAgentContext) -> dict[str, float]:
        w = {
            "convene_sanhedrin": float(self._weights.get("convene_sanhedrin_base", 1.0)),
            "appeal_to_rome": float(self._weights.get("appeal_to_rome_base", 0.5)),
            "temple_decree": float(self._weights.get("temple_decree_base", 1.2)),
            "confront_movement": float(self._weights.get("confront_movement_base", 0.8)),
        }

        # convene_sanhedrin ↑ when theological_anxiety high.
        anxiety_thr = float(self._weights.get("convene_anxiety_threshold", 0.6))
        if self.state.theological_anxiety >= anxiety_thr:
            w["convene_sanhedrin"] += self.state.theological_anxiety * 3.0

        # appeal_to_rome ↑ when jesus_movement.influence high (via context).
        jm_influence = float(ctx.agent_state_digest.get("jesus_movement_influence", 0.0))
        appeal_thr = float(self._weights.get("appeal_jesus_movement_threshold", 4.0))
        if jm_influence >= appeal_thr:
            w["appeal_to_rome"] += (jm_influence - appeal_thr) * 0.5

        # confront_movement ↑ when jesus_movement active + pharisees colocated.
        confront_thr = float(self._weights.get("confront_jesus_movement_threshold", 3.5))
        if jm_influence >= confront_thr:
            w["confront_movement"] += (jm_influence - confront_thr) * 0.8

        # temple_decree ↑ when sanhedrin authority is intact.
        authority_thr = float(self._weights.get("temple_decree_authority_threshold", 0.5))
        if self.state.sanhedrin_authority >= authority_thr:
            w["temple_decree"] += self.state.sanhedrin_authority * 1.0

        return w

    def _emit_effects(self, action_id: str) -> dict[str, float]:
        specs = _ACTION_EMITTERS.get(action_id, [])
        out: dict[str, float] = {}
        for channel_id, param_key in specs:
            mag = float(self._influence.get(param_key, 0.5))
            out[channel_id] = out.get(channel_id, 0.0) + mag
        return out

    # ------------------------------------------------------------------
    def describe_influence_paths(self) -> dict[str, list[str]]:
        return {
            action: [ch for ch, _ in specs]
            for action, specs in _ACTION_EMITTERS.items()
        }

    def hub_reaches(self, faction_id: str) -> list[str]:
        """Which actions touch ``faction_id``'s influence channel?

        Used by the hub-role behavior test + future graded-control
        analyses. The hub property is: ≥2 actions emit into pharisees
        AND ≥2 actions emit into sadducees.
        """
        channel = f"faction_influence_{faction_id}"
        return [
            action for action, specs in _ACTION_EMITTERS.items()
            if any(ch == channel for ch, _ in specs)
        ]


_: BaseWorldAgent = CaiaphasAgent()
