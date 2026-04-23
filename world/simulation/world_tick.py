"""WorldTick — sequential per-layer tick orchestrator (Spike 1A + 1B + 1C + 1D).

Layer tick order (each layer sees only layers already updated *this* tick):

    1. Calendar  (Layer 1)   — deterministic, feast + pilgrim influx target.
    2. Crowd     (Layer 5)   — reads Calendar.
    3. Economy   (Layer 2)   — reads Calendar.pilgrim_influx_target (3-day IIR).
    4. Politics  (Layer 3)   — reads Calendar + Crowd (threshold on density).

The ordering reflects the causal arrows documented in WORLD_DESIGN.md §3.1.
No layer in Spike 1 reads *forward*; every cross-layer dependency flows from
a lower-numbered layer in this tick order to a higher-numbered one.

ABSOLUTE RULE #9 (WORLD_DESIGN.md §8) — **no same-tick feedback**: a layer
reads only layers that have already been updated *this tick*, or values from
a previous tick. Circular dependencies require an explicit 1-tick delay
(``@prev_tick`` on the dependency string). The invariant is enforced by
``tests/test_world/test_layer_dag.py::test_tick_order_is_a_dag`` and by the
sequential dispatch below.

Reviewer-driven design notes:

- **#4 variable dt**: every tick takes ``dt_days`` from WorldConfig. Fixed at
  1.0 in Spike 1; variable in Spike 2+.
- **#6 runaway detection**: per-variable deltas on monitored fields
  (crowd_density, staple_price, roman_alertness) are handed to the detector.
- **#5 aggregation interface**: ``aggregated_effects`` flows through every
  LayerContext, empty in Spike 1, produced by ``SyncLayer.drain_aggregated``
  in Spike 2+.
"""

from __future__ import annotations

from typing import Any

from world.core.layer import LayerContext
from world.core.world_config import WorldConfig
from world.core.world_state import (
    EconomyState,
    FactionState,
    LayerTelemetry,
    PoliticsState,
    RumorState,
    WorldState,
)
from world.economy.economy import EconomyLayer
from world.environment.calendar import CalendarLayer
from world.factions.factions import FactionLayer
from world.politics.politics import PoliticsLayer
from world.simulation.runaway_detector import RunawayDetector
from world.social.crowd import CrowdLayer
from world.social.rumors import RumorLayer


class WorldTick:
    """Sequential per-layer world-tick progressor."""

    def __init__(
        self,
        *,
        calendar_layer: CalendarLayer,
        crowd_layer: CrowdLayer,
        config: WorldConfig,
        economy_layer: EconomyLayer | None = None,
        politics_layer: PoliticsLayer | None = None,
        faction_layer: FactionLayer | None = None,
        rumor_layer: RumorLayer | None = None,
        runaway_detector: RunawayDetector | None = None,
    ) -> None:
        self.calendar_layer = calendar_layer
        self.crowd_layer = crowd_layer
        self.economy_layer = economy_layer
        self.politics_layer = politics_layer
        self.faction_layer = faction_layer
        self.rumor_layer = rumor_layer
        self.config = config
        self.runaway_detector = runaway_detector or self._default_detector()
        self.tick_index: int = 0

    def _default_detector(self) -> RunawayDetector:
        limits = self.config.runaway_limits
        max_per_day: dict[str, float] = {
            "crowd_density": limits.get("crowd_density_max_per_day", 3.0),
        }
        ceilings: dict[str, float] = {
            "crowd_density": limits.get(
                "crowd_density_ceiling", self.crowd_layer.ceiling,
            ),
        }
        if self.economy_layer is not None:
            max_per_day["staple_price"] = limits.get(
                "staple_price_max_per_day", 2.5,
            )
            ceilings["staple_price"] = limits.get(
                "staple_price_ceiling", self.economy_layer.price_ceiling,
            )
        if self.politics_layer is not None:
            max_per_day["roman_alertness"] = limits.get(
                "roman_alertness_max_per_day", 3.0,
            )
            ceilings["roman_alertness"] = limits.get(
                "roman_alertness_ceiling", self.politics_layer.alertness_ceiling,
            )
        return RunawayDetector(
            max_abs_delta_per_day=max_per_day, ceilings=ceilings,
        )

    # ------------------------------------------------------------------
    # Orchestration

    def initial_world_state(self) -> WorldState:
        cal = self.calendar_layer.initial_state(self.config.calendar_config)
        crowd = self.crowd_layer.initial_state(self.config.crowd_config)
        econ: EconomyState | None = None
        pol: PoliticsState | None = None
        fac: FactionState | None = None
        rum: RumorState | None = None
        telem: dict[str, LayerTelemetry] = {
            self.calendar_layer.layer_id: LayerTelemetry(),
            self.crowd_layer.layer_id: LayerTelemetry(),
        }
        if self.economy_layer is not None:
            econ_cfg = getattr(self.config, "economy_config", None) or {}
            econ = self.economy_layer.initial_state(econ_cfg)
            telem[self.economy_layer.layer_id] = LayerTelemetry()
        if self.politics_layer is not None:
            pol_cfg = getattr(self.config, "politics_config", None) or {}
            pol = self.politics_layer.initial_state(pol_cfg)
            telem[self.politics_layer.layer_id] = LayerTelemetry()
        if self.rumor_layer is not None:
            rum_cfg = getattr(self.config, "rumors_config", None) or {}
            rum = self.rumor_layer.initial_state(rum_cfg)
            telem[self.rumor_layer.layer_id] = LayerTelemetry()
        if self.faction_layer is not None:
            fac_cfg = getattr(self.config, "factions_config", None) or {}
            fac = self.faction_layer.initial_state(fac_cfg)
            telem[self.faction_layer.layer_id] = LayerTelemetry()
        self.tick_index = 0
        return WorldState(
            calendar=cal, crowd=crowd, economy=econ, politics=pol,
            factions=fac, rumors=rum,
            telemetry=telem,
        )

    def tick(
        self,
        state: WorldState,
        aggregated: dict[str, float] | None = None,
    ) -> WorldState:
        aggregated_effects = dict(aggregated or {})

        # --- Layer 1: calendar --------------------------------------------
        ctx = self._ctx(state, aggregated_effects)
        new_cal = self.calendar_layer.tick(state.calendar, ctx)
        state = state.with_calendar(new_cal)

        # --- Layer 5: crowd -----------------------------------------------
        ctx = self._ctx(state, aggregated_effects)
        prev_crowd = state.crowd.crowd_density
        new_crowd = self.crowd_layer.tick(state.crowd, ctx)
        state = state.with_crowd(new_crowd)

        # --- Layer 2: economy (optional) ----------------------------------
        prev_price: float | None = None
        new_econ: EconomyState | None = None
        if self.economy_layer is not None and state.economy is not None:
            ctx = self._ctx(state, aggregated_effects)
            prev_price = state.economy.staple_price
            new_econ = self.economy_layer.tick(state.economy, ctx)
            state = state.with_economy(new_econ)

        # --- Layer 3: politics (optional) ---------------------------------
        prev_alert: float | None = None
        new_pol: PoliticsState | None = None
        if self.politics_layer is not None and state.politics is not None:
            ctx = self._ctx(state, aggregated_effects)
            prev_alert = state.politics.roman_alertness
            new_pol = self.politics_layer.tick(state.politics, ctx)
            state = state.with_politics(new_pol)

        # --- Layer 5 rumors (optional, before factions so Phase 3C+ edges are same-tick) -
        new_rum: RumorState | None = None
        if self.rumor_layer is not None and state.rumors is not None:
            ctx = self._ctx(state, aggregated_effects)
            new_rum = self.rumor_layer.tick(state.rumors, ctx)
            state = state.with_rumors(new_rum)

        # --- Layer 4: factions (optional) ---------------------------------
        new_fac: FactionState | None = None
        if self.faction_layer is not None and state.factions is not None:
            ctx = self._ctx(state, aggregated_effects)
            new_fac = self.faction_layer.tick(state.factions, ctx)
            state = state.with_factions(new_fac)

        # --- Runaway detection --------------------------------------------
        samples: dict[str, float] = {"crowd_density": new_crowd.crowd_density}
        deltas: dict[str, float] = {
            "crowd_density": new_crowd.crowd_density - prev_crowd,
        }
        if new_econ is not None and prev_price is not None:
            samples["staple_price"] = new_econ.staple_price
            deltas["staple_price"] = new_econ.staple_price - prev_price
        if new_pol is not None and prev_alert is not None:
            samples["roman_alertness"] = new_pol.roman_alertness
            deltas["roman_alertness"] = new_pol.roman_alertness - prev_alert
        self.runaway_detector.observe(
            tick_index=self.tick_index,
            dt_days=self.config.dt_days,
            samples=samples,
            deltas=deltas,
        )

        # --- Telemetry roll-up --------------------------------------------
        telem = dict(state.telemetry)
        telem[self.crowd_layer.layer_id] = LayerTelemetry(
            runaway_warnings=self.crowd_layer.runaway_warnings,
            clamp_hits=self.crowd_layer.clamp_hits,
            rate_limit_hits=self.crowd_layer.rate_limit_hits,
        )
        telem.setdefault(self.calendar_layer.layer_id, LayerTelemetry())
        if self.economy_layer is not None:
            telem[self.economy_layer.layer_id] = LayerTelemetry(
                clamp_hits=self.economy_layer.clamp_hits,
            )
        if self.politics_layer is not None:
            telem[self.politics_layer.layer_id] = LayerTelemetry(
                clamp_hits=self.politics_layer.clamp_hits,
            )
        if self.faction_layer is not None:
            telem[self.faction_layer.layer_id] = LayerTelemetry(
                clamp_hits=self.faction_layer.clamp_hits,
            )
        if self.rumor_layer is not None:
            telem[self.rumor_layer.layer_id] = LayerTelemetry()

        next_state = WorldState(
            calendar=state.calendar, crowd=state.crowd,
            economy=state.economy, politics=state.politics,
            factions=state.factions, rumors=state.rumors,
            telemetry=telem,
        )
        self.tick_index += 1
        return next_state

    # ------------------------------------------------------------------
    # Helpers.

    def _ctx(
        self, state: WorldState, aggregated_effects: dict[str, float],
    ) -> LayerContext:
        return LayerContext(
            tick_index=self.tick_index,
            dt_days=self.config.dt_days,
            world_snapshot=state,
            rng_seed=self.config.rng_seed,
            aggregated_effects=aggregated_effects,
        )

    def describe(self) -> dict[str, Any]:
        desc: dict[str, Any] = {
            "tick_index": self.tick_index,
            "calendar": self.calendar_layer.describe_dynamics(),
            "crowd": self.crowd_layer.describe_dynamics(),
            "runaway_report": self.runaway_detector.report.as_dict(),
        }
        if self.economy_layer is not None:
            desc["economy"] = self.economy_layer.describe_dynamics()
        if self.politics_layer is not None:
            desc["politics"] = self.politics_layer.describe_dynamics()
        if self.faction_layer is not None:
            desc["factions"] = self.faction_layer.describe_dynamics()
        if self.rumor_layer is not None:
            desc["rumors"] = self.rumor_layer.describe_dynamics()
        return desc
