"""InterventionEngine — apply an ``InterventionSpec`` to world+sim configs.

Spike 4 Phase 4A. The engine:

1. **Deep-copies** the incoming WorldConfig and SimulationConfig.
2. Applies each intervention primitive in a documented order.
3. Returns the mutated pair alongside a report of primitives applied.

The originals are never mutated. An empty spec (``is_null()``) returns
deep copies that are structurally identical to the inputs so the
control-vs-intervention contrast uses identical apparatus when the
intervention is "do nothing".

Primitives are applied in a fixed order so that interactions between
primitives (e.g. `faction_remove` happens before `faction_influence_scale`)
are reproducible:

  1. Remove agents / factions (destructive, affects following fields).
  2. Add factions (before scaling so new ones can also be scaled).
  3. Scale faction influence / rumour / hazard / calendar values.
  4. Override politics thresholds.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field, replace

from engine.core.world import SimulationConfig
from world.core.world_config import WorldConfig
from world.intervention.spec import InterventionSpec


@dataclass(frozen=True)
class InterventionReport:
    """Audit log of what the engine actually changed."""

    intervention_id: str
    primitives_applied: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def mark(self, name: str) -> "InterventionReport":
        return replace(self, primitives_applied=[*self.primitives_applied, name])

    def warn(self, msg: str) -> "InterventionReport":
        return replace(self, warnings=[*self.warnings, msg])


class InterventionEngine:
    """Apply an InterventionSpec to a (WorldConfig, SimulationConfig) pair."""

    def apply(
        self,
        spec: InterventionSpec,
        world_config: WorldConfig,
        base_config: SimulationConfig,
    ) -> tuple[WorldConfig, SimulationConfig, InterventionReport]:
        world = copy.deepcopy(world_config)
        base = base_config.model_copy(deep=True)
        report = InterventionReport(intervention_id=spec.intervention_id)

        if spec.is_null():
            return world, base, report.mark("null_control")

        # --- 1. Destructive removals first.
        if spec.agent_remove:
            new_states = [
                s for s in base.initial_states if s.agent_id not in spec.agent_remove
            ]
            if len(new_states) == len(base.initial_states):
                report = report.warn(
                    f"agent_remove={spec.agent_remove} matched no agents",
                )
            base = base.model_copy(update={
                "initial_states": new_states,
                "initial_state": new_states[0] if new_states else base.initial_state,
            })
            report = report.mark("agent_remove")

        if spec.faction_remove:
            factions = world.factions_config.get("factions", {})
            removed: list[str] = []
            for fid in spec.faction_remove:
                if fid in factions:
                    factions.pop(fid)
                    removed.append(fid)
            if removed:
                world.factions_config["factions"] = factions
                report = report.mark("faction_remove")
            if set(spec.faction_remove) - set(removed):
                report = report.warn(
                    f"faction_remove requested {spec.faction_remove} "
                    f"but only {removed} present",
                )

        # --- 2. Additions.
        if spec.faction_add:
            factions = world.factions_config.get("factions", {})
            for fid, fc in spec.faction_add.items():
                factions[fid] = dict(fc)
            world.factions_config["factions"] = factions
            report = report.mark("faction_add")

        # --- 3. Scalar scaling.
        if spec.faction_influence_scale:
            factions = world.factions_config.get("factions", {})
            scaled: list[str] = []
            for fid, scale in spec.faction_influence_scale.items():
                if fid in factions:
                    for key in ("initial_influence", "target_influence"):
                        if key in factions[fid]:
                            factions[fid][key] = float(factions[fid][key]) * scale
                    scaled.append(fid)
            if scaled:
                world.factions_config["factions"] = factions
                report = report.mark("faction_influence_scale")

        if spec.rumor_spread_rate_scale is not None:
            rumors = world.rumors_config
            current = float(rumors.get("spread_rate_per_day", 0.05))
            rumors["spread_rate_per_day"] = current * spec.rumor_spread_rate_scale
            report = report.mark("rumor_spread_rate_scale")

        if spec.rumor_credibility_decay_scale is not None:
            rumors = world.rumors_config
            current = float(rumors.get("credibility_decay_per_day", 0.02))
            rumors["credibility_decay_per_day"] = (
                current * spec.rumor_credibility_decay_scale
            )
            report = report.mark("rumor_credibility_decay_scale")

        if spec.hazard_rate_scale is not None:
            scale = float(spec.hazard_rate_scale)
            new_hazards = []
            for h in base.hazard_events:
                h_copy = h.model_copy(deep=True)
                if h_copy.hazard is not None:
                    # Scale the full hazard contribution, not just base_rate.
                    # In most Witness content the state-dependent ``factors``
                    # dominate over ``base_rate`` by an order of magnitude, so
                    # scaling only base_rate left the effective rate almost
                    # unchanged. Scale both primitives to match user intent
                    # "halve the hazard pipeline".
                    h_copy.hazard.base_rate = h_copy.hazard.base_rate * scale
                    for factor in h_copy.hazard.factors:
                        factor.weight = factor.weight * scale
                new_hazards.append(h_copy)
            base = base.model_copy(update={"hazard_events": new_hazards})
            report = report.mark("hazard_rate_scale")

        if spec.passover_amplitude_scale is not None:
            cal = world.calendar_config
            current = float(cal.get("passover_amplitude", 10.0))
            cal["passover_amplitude"] = current * spec.passover_amplitude_scale
            report = report.mark("passover_amplitude_scale")

        # --- 4. Politics overrides.
        if spec.crowd_trigger_threshold_override is not None:
            world.politics_config["crowd_trigger_threshold"] = float(
                spec.crowd_trigger_threshold_override,
            )
            report = report.mark("crowd_trigger_threshold_override")

        if spec.pilate_bonus_override is not None:
            world.politics_config["pilate_bonus"] = float(
                spec.pilate_bonus_override,
            )
            report = report.mark("pilate_bonus_override")

        if spec.pilate_approach_lead_days_override is not None:
            world.politics_config["pilate_approach_lead_days"] = int(
                spec.pilate_approach_lead_days_override,
            )
            report = report.mark("pilate_approach_lead_days_override")

        return world, base, report

    def apply_to_world_only(
        self, spec: InterventionSpec, world_config: WorldConfig,
    ) -> tuple[WorldConfig, InterventionReport]:
        """Shortcut when only the world is mutated (no agent changes)."""
        base = _stub_base_config()
        world, _, report = self.apply(spec, world_config, base)
        return world, report


def _stub_base_config() -> SimulationConfig:
    """Minimal SimulationConfig for world-only intervention calls."""
    from engine.core.state import AgentState
    stub = AgentState(agent_id="stub_for_intervention_world_only")
    return SimulationConfig(initial_state=stub, max_tick=1)
