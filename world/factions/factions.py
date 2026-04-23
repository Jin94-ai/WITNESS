"""FactionLayer — Layer 4 organised-group dynamics (Spike 3 Phase 3A + 3B + 3D).

Each faction is a Tier-3 statistical bloc (per WORLD_DESIGN_v1.1 §1.2) —
scalar influence + militancy, not an individual Agent.

**Phase 3A** — independent dynamics only (all factions, see below).
**Phase 3B** — first cross-layer edge: crowd → zealot militancy.

    zealot_militancy_boost(t) = militancy_step * dt_days
        if crowd.crowd_density(t) >= militancy_crowd_threshold
        else 0.0

**Phase 3D** (this loop) — second cross-layer edge: rumour → faction influence.

    rumor_influence_boost(fid, t) =
          rumor_gain_per_unit_intensity * rumors.active_intensity(t) * dt_days
        if fid in rumor_sensitive_factions else 0.0

Both edges are SAME-TICK (not @prev_tick) because WorldTick schedules
crowd (Layer 5 crowd) BEFORE factions, then rumors (Layer 5 rumors)
BEFORE factions, so both values are this-tick-fresh when factions reads.
The DAG invariant guards this ordering.
Brake type: threshold (crowd) + saturation on intensity contribution
(bounded by tau-decay back to target_influence) + clamp.

    influence(t+1) = clamp(
        target_influence
        + (influence(t) - target_influence) * exp(-dt_days / tau_influence)
        + growth_rate * dt_days
        + N(0, sigma_daily * dt_days)
    , 0.0, influence_ceiling)

    militancy(t+1) = clamp(
        militancy(t)
        + (militancy_step * dt   if is_zealot AND crowd >= threshold)
        + N(0, sigma_militancy * dt_days)
    , 0.0, 10.0)

Planned future Phase 3C edges (rumour layer needed first):
- politics.roman_alertness → faction roman_stance drift
- rumour.intensity         → faction influence amplification

Such edges MUST respect ABSOLUTE RULE #9 (@prev_tick if they would
create a cycle with Layer 5 rumours which read factions).

Reviewer hooks:

- **#1 dynamics**: update equations documented per field above;
  ``describe_dynamics()`` returns the same numbers.
- **#2 brakes**: saturation (clamp to [0, ceiling]) + exponential decay
  toward target (tau_influence). No cross-layer edges yet so no brakes
  needed in Phase 3A.
- **#3 success**: `tests/test_world/test_factions.py` pins (a) influence
  converges toward target without drift, (b) `describe_dynamics()`
  returns declared per-faction parameters.
- **#4 variable dt**: all per-day rates multiplied by dt_days at tick.
- **#6 runaway detection**: clamp + per-faction clamp counter.
- **#8 strict Phase 3A scope**: independent dynamics only, no cross-layer.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any

from world.core.layer import LayerContext
from world.core.world_state import FactionSnapshot, FactionState, RomanStance

DEFAULT_INFLUENCE_CEILING = 10.0


@dataclass
class _FactionParams:
    faction_id: str
    initial_influence: float
    initial_militancy: float
    initial_stance: RomanStance
    target_influence: float
    tau_influence: float
    growth_rate: float
    sigma_influence: float
    sigma_militancy: float


class FactionLayer:
    """Layer 4 — organised groups (Spike 3 Phase 3A)."""

    layer_id = "factions"

    def __init__(self) -> None:
        self.ceiling: float = DEFAULT_INFLUENCE_CEILING
        self._params: dict[str, _FactionParams] = {}
        self._clamp_hits = 0
        # Phase 3B crowd-threshold militancy boost (zealots-only by default).
        self.militancy_crowd_threshold: float = 5.0
        self.militancy_step: float = 0.15
        self.militancy_threshold_factions: frozenset[str] = frozenset({"zealots"})
        self._militancy_threshold_hits: int = 0
        # Phase 3D rumour → influence edge (jesus_movement-only by default).
        self.rumor_sensitive_factions: frozenset[str] = frozenset({"jesus_movement"})
        self.rumor_gain_per_unit_intensity: float = 0.05
        self._rumor_boost_applied_ticks: int = 0

    # ------------------------------------------------------------------
    # Layer protocol

    def initial_state(self, config: dict[str, Any]) -> FactionState:
        self.ceiling = float(config.get("influence_ceiling", DEFAULT_INFLUENCE_CEILING))
        self.militancy_crowd_threshold = float(
            config.get("militancy_crowd_threshold", 5.0),
        )
        self.militancy_step = float(config.get("militancy_step", 0.15))
        mt = config.get("militancy_threshold_factions")
        if mt is not None:
            self.militancy_threshold_factions = frozenset(mt)
        self._militancy_threshold_hits = 0
        # Phase 3D.
        rs = config.get("rumor_sensitive_factions")
        if rs is not None:
            self.rumor_sensitive_factions = frozenset(rs)
        self.rumor_gain_per_unit_intensity = float(
            config.get("rumor_gain_per_unit_intensity", 0.05),
        )
        self._rumor_boost_applied_ticks = 0
        self._params = {}
        snapshots: dict[str, FactionSnapshot] = {}
        factions_cfg = config.get("factions", {})
        if not factions_cfg:
            return FactionState(factions={})
        for fid, fc in factions_cfg.items():
            params = _FactionParams(
                faction_id=fid,
                initial_influence=float(fc.get("initial_influence", 1.0)),
                initial_militancy=float(fc.get("initial_militancy", 0.5)),
                initial_stance=fc.get("initial_roman_stance", "neutral"),
                target_influence=float(fc.get("target_influence", 1.0)),
                tau_influence=float(fc.get("tau_influence", 30.0)),
                growth_rate=float(fc.get("growth_rate", 0.0)),
                sigma_influence=float(fc.get("sigma_influence", 0.05)),
                sigma_militancy=float(fc.get("sigma_militancy", 0.02)),
            )
            self._params[fid] = params
            snapshots[fid] = FactionSnapshot(
                faction_id=fid,
                influence=max(0.0, min(self.ceiling, params.initial_influence)),
                militancy=max(0.0, min(10.0, params.initial_militancy)),
                roman_stance=params.initial_stance,
                target_influence=params.target_influence,
                growth_rate=params.growth_rate,
            )
        return FactionState(factions=snapshots)

    def tick(self, state: FactionState, ctx: LayerContext) -> FactionState:
        dt = max(0.0, ctx.dt_days)
        # Phase 3D: read rumour intensity once per tick (same-tick — rumors
        # layer is scheduled before factions).
        rumor_intensity = 0.0
        if ctx.world_snapshot.rumors is not None:
            rumor_intensity = ctx.world_snapshot.rumors.active_intensity()
        updated: dict[str, FactionSnapshot] = {}
        for fid, snap in state.factions.items():
            params = self._params.get(fid)
            if params is None:
                updated[fid] = snap
                continue

            # Influence: exponential drift + linear growth + noise + rumour boost.
            decay = (
                math.exp(-dt / params.tau_influence)
                if params.tau_influence > 0 else 0.0
            )
            drift = (
                params.target_influence
                + (snap.influence - params.target_influence) * decay
            )
            rng = random.Random(
                hash(("factions.inf", fid, int(ctx.rng_seed), int(ctx.tick_index)))
                & 0xFFFFFFFF,
            )
            rumor_boost = 0.0
            if (
                rumor_intensity > 0.0
                and fid in self.rumor_sensitive_factions
            ):
                rumor_boost = (
                    self.rumor_gain_per_unit_intensity * rumor_intensity * dt
                )
                self._rumor_boost_applied_ticks += 1
            influence = (
                drift
                + params.growth_rate * dt
                + rumor_boost
                + rng.gauss(0.0, params.sigma_influence) * dt
            )
            clamp_hit = influence > self.ceiling or influence < 0.0
            if clamp_hit:
                self._clamp_hits += 1
            influence = max(0.0, min(self.ceiling, influence))

            # Militancy: random walk + Phase 3B crowd-threshold boost (zealots).
            rng2 = random.Random(
                hash(("factions.mil", fid, int(ctx.rng_seed), int(ctx.tick_index)))
                & 0xFFFFFFFF,
            )
            militancy = snap.militancy + rng2.gauss(0.0, params.sigma_militancy) * dt
            crowd_density = ctx.world_snapshot.crowd.crowd_density
            if (
                fid in self.militancy_threshold_factions
                and crowd_density >= self.militancy_crowd_threshold
            ):
                militancy += self.militancy_step * dt
                self._militancy_threshold_hits += 1
            militancy = max(0.0, min(10.0, militancy))

            updated[fid] = FactionSnapshot(
                faction_id=fid,
                influence=influence,
                militancy=militancy,
                roman_stance=snap.roman_stance,  # static in Phase 3A
                target_influence=snap.target_influence,
                growth_rate=snap.growth_rate,
            )
        return FactionState(factions=updated)

    # ------------------------------------------------------------------
    # Diagnostics

    @property
    def clamp_hits(self) -> int:
        return self._clamp_hits

    @property
    def militancy_threshold_hits(self) -> int:
        return self._militancy_threshold_hits

    @property
    def rumor_boost_applied_ticks(self) -> int:
        return self._rumor_boost_applied_ticks

    def describe_dynamics(self) -> dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "phase": "3D_rumor_influence_edge",
            "update_rule": (
                "influence(t+1) = clamp("
                "target + (inf(t)-target)*exp(-dt/tau) "
                "+ growth*dt + rumor_boost*dt + N(0,sigma*dt)"
                ", 0, ceiling); "
                "militancy(t+1) = clamp("
                "mil(t) + N(0,sigma_mil*dt) + "
                "[mil_step*dt if is_threshold_faction and crowd>=mil_crowd_thr]"
                ", 0, 10); "
                "rumor_boost(fid) = "
                "rumor_gain * rumors.active_intensity * 1[fid in rumor_sensitive]"
            ),
            "influence_ceiling": self.ceiling,
            # Phase 3B + 3D: same-tick reads on crowd and rumors. Both
            # layers tick before factions in WorldTick.
            "causal_dependencies": ["crowd.crowd_density", "rumors.active_intensity"],
            "brake_type": (
                "saturation (clamp) + exponential drift toward target "
                "+ threshold (crowd>=mil_crowd_thr triggers zealot boost) "
                "+ bounded rumour-gain (decays via tau_influence when rumours fade)"
            ),
            "militancy_crowd_threshold": self.militancy_crowd_threshold,
            "militancy_step": self.militancy_step,
            "militancy_threshold_factions": sorted(self.militancy_threshold_factions),
            "rumor_sensitive_factions": sorted(self.rumor_sensitive_factions),
            "rumor_gain_per_unit_intensity": self.rumor_gain_per_unit_intensity,
            "factions": {
                fid: {
                    "target_influence": p.target_influence,
                    "tau_influence": p.tau_influence,
                    "growth_rate": p.growth_rate,
                    "initial_influence": p.initial_influence,
                    "initial_stance": p.initial_stance,
                }
                for fid, p in self._params.items()
            },
        }
