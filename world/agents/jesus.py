"""JesusAgent — world-layer adapter for the Jesus content agent (Phase 5A).

Composes three things:

1. **Content profile** (``content/jesus/behavior_profile.json``) —
   existing engine-compatible ``AgentBehaviorProfile``. Spike 5 Part 1
   does not drive this through the Person Engine; it is loaded so Peter
   and the rest can *see* Jesus actions via visible_signal when they
   co-locate. Part 2 will integrate execution.

2. **World profile** (``content/worlds/jerusalem_ad30/jesus_profile.json``) —
   per-world tuning (action base weights, bonus thresholds) + the
   canonical_constraints list. Constraints are **hard overrides** on
   specific day_indices; everywhere else the agent is free.

3. **Multi-path influence emitter** (Phase 5A §4.2.2). Every action
   emits 0+ ``WorldEffect`` channel values:

   - ``teach``    → ``faction_influence_jesus_movement`` (direct)
                    + ``rumor_seed`` (low intensity)
   - ``heal``     → ``rumor_seed`` (HIGH intensity)
                    + ``faction_influence_jesus_movement`` (crowd testimony)
   - ``confront`` → ``authority_threat`` (pharisees/caiaphas path)
                    + ``rumor_seed`` (low intensity)
   - ``withdraw`` → (no world effect — fatigue recovery only)
   - ``bless``    → ``faction_influence_jesus_movement`` (disciple witness)

   The explicit multiplicity is the structural insurance against the
   ``remove_jesus`` scenario later collapsing jesus_movement to a
   single point: disciple witness + crowd testimony paths survive
   without jesus as long as disciple agents still act.

Spike 5 Part 1 scope: the class is stand-alone (no runtime integration
yet). Part 2 wires it into ``IntegratedWorldRunner`` substeps.
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

# ---------------------------------------------------------------------
# Public outcome type.

@dataclass(frozen=True)
class JesusAgentOutcome:
    """Inspectable per-decide output used by tests + Part 2 runner."""

    decision: WorldActionDecision
    considered_weights: dict[str, float] = field(default_factory=dict)
    canonical_fired: bool = False
    influence_paths_activated: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------
# Emitter lookup — single source of truth for the multi-path fan-out.

_ACTION_EMITTERS: dict[str, list[tuple[str, str | None]]] = {
    # action_id: list of (channel_id, magnitude_param_key_or_None_for_constant_1.0)
    "teach": [
        ("faction_influence_jesus_movement", "teach_direct_boost"),
        ("rumor_seed", None),  # magnitude 1.0 (constant)
    ],
    "heal": [
        ("rumor_seed", None),
        ("faction_influence_jesus_movement", "crowd_testimony_rumor_intensity"),
    ],
    "confront": [
        ("authority_threat", None),
        ("rumor_seed", None),
    ],
    "withdraw": [],
    "bless": [
        ("faction_influence_jesus_movement", "disciple_witness_rumor_intensity"),
    ],
}


# ---------------------------------------------------------------------
# JesusAgent.

class JesusAgent:
    """Jesus as a world-side adapter (satisfies ``BaseWorldAgent``)."""

    agent_id: str = "jesus"

    def __init__(
        self,
        *,
        world_profile: dict[str, Any] | None = None,
        content_profile_actions: list[str] | None = None,
    ) -> None:
        self.world_profile = world_profile or {}
        self.content_profile_actions = content_profile_actions or [
            "teach", "heal", "confront", "withdraw", "bless",
        ]
        self._weights_cfg: dict[str, float] = self.world_profile.get(
            "world_weights", {},
        )
        self._influence_cfg: dict[str, float] = self.world_profile.get(
            "influence_paths", {},
        )
        self._canonical: list[dict[str, Any]] = self.world_profile.get(
            "canonical_constraints", [],
        )

    # ----- factory -------------------------------------------------------

    @classmethod
    def from_world_profile_path(cls, path: Path | str) -> "JesusAgent":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(world_profile=payload)

    # ----- main decide ---------------------------------------------------

    def decide(self, ctx: WorldAgentContext) -> WorldActionDecision:
        outcome = self.decide_with_outcome(ctx)
        return outcome.decision

    def decide_with_outcome(self, ctx: WorldAgentContext) -> JesusAgentOutcome:
        # 1. Canonical constraint short-circuit.
        forced = self._canonical_lookup(ctx.day_index)
        if forced is not None:
            action_id = forced.get("forced_action", "teach")
            effects = self._emit_effects(action_id)
            return JesusAgentOutcome(
                decision=WorldActionDecision(
                    action_id=action_id,
                    world_effects=effects,
                    meta={
                        "canonical_id": forced.get("canonical_id"),
                        "forced_location": forced.get("forced_location"),
                    },
                ),
                considered_weights={action_id: 1.0},
                canonical_fired=True,
                influence_paths_activated=list(effects.keys()),
            )

        # 2. Free decision — compute per-action weights from context.
        weights = self._compute_weights(ctx)
        action_id = self._pick_highest(weights)
        effects = self._emit_effects(action_id)
        return JesusAgentOutcome(
            decision=WorldActionDecision(
                action_id=action_id, world_effects=effects,
            ),
            considered_weights=weights,
            canonical_fired=False,
            influence_paths_activated=list(effects.keys()),
        )

    # ----- weight computation --------------------------------------------

    def _compute_weights(self, ctx: WorldAgentContext) -> dict[str, float]:
        base = {
            "teach": float(self._weights_cfg.get("teach_base", 3.0)),
            "heal": float(self._weights_cfg.get("heal_base", 1.5)),
            "confront": float(self._weights_cfg.get("confront_base", 1.0)),
            "withdraw": float(self._weights_cfg.get("withdraw_base", 1.0)),
            "bless": float(self._weights_cfg.get("bless_base", 0.8)),
        }

        # withdraw: crowd OR fatigue high.
        crowd_thr = float(self._weights_cfg.get("withdraw_crowd_threshold", 0.7))
        if ctx.crowd_density_here >= crowd_thr:
            base["withdraw"] += 2.5
        fatigue = float(ctx.agent_state_digest.get("fatigue", 0.0))
        fatigue_thr = float(self._weights_cfg.get("withdraw_fatigue_threshold", 6.0))
        if fatigue >= fatigue_thr:
            base["withdraw"] += 2.0

        # confront: pharisees/caiaphas co-located.
        colocated = set(ctx.co_located_agents)
        if colocated & {"caiaphas", "pharisees"}:
            base["confront"] += float(
                self._weights_cfg.get("confront_pharisee_colocate_bonus", 2.5),
            )

        # teach: disciple understanding low.
        understanding = float(ctx.agent_state_digest.get("disciple_understanding", 10.0))
        thr = float(self._weights_cfg.get("disciple_understanding_threshold", 5.0))
        if understanding < thr:
            base["teach"] += float(
                self._weights_cfg.get("teach_low_understanding_bonus", 2.0),
            )

        # heal: suffering agent at same location.
        suffering = float(ctx.agent_state_digest.get("colocated_suffering", 0.0))
        heal_thr = float(self._weights_cfg.get("heal_suffering_trigger_threshold", 5.0))
        if suffering >= heal_thr:
            base["heal"] += 2.0

        return base

    @staticmethod
    def _pick_highest(weights: dict[str, float]) -> str:
        # Deterministic: highest weight; ties broken by action_id alphabetical.
        return max(weights.items(), key=lambda kv: (kv[1], -ord(kv[0][0])))[0]

    # ----- emitter -------------------------------------------------------

    def _emit_effects(self, action_id: str) -> dict[str, float]:
        specs = _ACTION_EMITTERS.get(action_id, [])
        result: dict[str, float] = {}
        for channel_id, param_key in specs:
            if param_key is None:
                magnitude = 1.0
            else:
                magnitude = float(self._influence_cfg.get(param_key, 0.5))
            result[channel_id] = result.get(channel_id, 0.0) + magnitude
        return result

    # ----- canonical helpers ---------------------------------------------

    def _canonical_lookup(self, day_index: int) -> dict[str, Any] | None:
        for entry in self._canonical:
            if int(entry.get("day_index", -1)) == day_index:
                return entry
        return None

    # ----- introspection -------------------------------------------------

    def describe_influence_paths(self) -> dict[str, list[str]]:
        """Return per-action list of channels it emits into. Used by
        ``test_jesus_influence_reaches_factions_via_multiple_paths``."""
        return {
            action: [ch for ch, _ in specs]
            for action, specs in _ACTION_EMITTERS.items()
        }


# ---------------------------------------------------------------------
# Protocol conformance sanity (runtime_checkable — just a safety net).

_: BaseWorldAgent = JesusAgent(world_profile={})
