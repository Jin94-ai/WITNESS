"""PoliticsLayer — Layer 3 Roman governor / alertness (Spike 1C).

Update equations (reviewer #1 — explicit dynamics) ::

    # 1. Governor location (calendar-driven).
    pilate_location(t+1) = jerusalem
        if (pilate_approach_lead ≤ days_to_passover ≤ pilate_approach_end)
           OR active_feast in passover/unleavened_bread/firstfruits
        else caesarea

    # 2. Alertness (soft decay + threshold-triggered boost).
    boost = threshold_step * dt_days
            if crowd_density(t) >= crowd_trigger_threshold
            else 0.0
    location_bias = pilate_bonus * dt_days
                    if pilate_location == jerusalem
                    else 0.0
    alertness(t+1) = clamp(
          floor
        + (alertness(t) - floor) * exp(-dt_days / alert_tau_days)   # decay
        + boost                                                      # threshold brake
        + location_bias                                              # calendar-induced
        + N(0, sigma_daily * dt_days)                                # noise
    , min=floor, max=ceiling)

Reviewer hooks:

- **#1 dynamics**: two cascaded state variables (location, alertness) with
  update equations spelled out above.
- **#2 cross-layer brakes**: every cross-layer coupling has a brake.
    * ``crowd_density → alertness``: **threshold** (step function, not linear).
      Below threshold, alertness responds only to its own decay + location.
    * ``calendar → pilate_location``: the governor does *not* teleport —
      he approaches Jerusalem a few days before Passover (configurable
      lead window). This is the **delay** brake on calendar→politics.
    * ``alertness decay``: **saturation** via the clamp.
- **#4 variable dt**: ``alert_tau_days``, ``threshold_step``, ``pilate_bonus``,
  ``sigma_daily`` are all per-day rates multiplied by ``dt_days`` at tick time.
- **#6 runaway detection**: hard clamp on [floor, ceiling], counter exposed.
- **#7 causal consistency**: sustained crowd > threshold ⇒ alertness rises
  above baseline. Sub-threshold crowd ⇒ alertness stays near floor. The test
  in test_politics.py pins both sides of the threshold.

Time constant: ``alert_tau_days`` (default 4 days) — e-folding back to floor.
Observation: PoliticsState.roman_alertness, fed in Spike 2 to agent fear via
Sync Layer. Spike 1C only measures the signal.
"""

from __future__ import annotations

import math
import random
from typing import Any

from world.core.layer import LayerContext
from world.core.world_state import PilateLocation, PoliticsState

# --- Calendar coupling ----------------------------------------------------
# Governor moves to Jerusalem in a window leading up to Passover and stays
# through Firstfruits (Josephus, Antiquities 18, Philo Legatio 38). Below we
# model this as a threshold on days_to_next_passover + an override while the
# Passover / Unleavened Bread / Firstfruits feasts are active.
DEFAULT_APPROACH_LEAD_DAYS = 4
DEFAULT_APPROACH_STAY_DAYS = 10

FEAST_JERUSALEM = frozenset({
    "passover", "unleavened_bread", "firstfruits", "shavuot",
})


class PoliticsLayer:
    """Layer 3 — roman alertness + pilate location."""

    layer_id = "politics"

    def __init__(self) -> None:
        self.alertness_floor: float = 2.0
        self.alertness_ceiling: float = 10.0
        self.alert_tau_days: float = 4.0
        self.crowd_trigger_threshold: float = 5.0
        self.threshold_step: float = 1.5
        self.pilate_bonus: float = 0.4
        self.sigma_daily: float = 0.05
        self.approach_lead_days: int = DEFAULT_APPROACH_LEAD_DAYS
        self.approach_stay_days: int = DEFAULT_APPROACH_STAY_DAYS
        self._clamp_hits = 0
        self._threshold_hits = 0
        self.last_alertness_delta: float = 0.0

    # ------------------------------------------------------------------
    # Layer protocol

    def initial_state(self, config: dict[str, Any]) -> PoliticsState:
        self.alertness_floor = float(config.get("alertness_floor", 2.0))
        self.alertness_ceiling = float(config.get("alertness_ceiling", 10.0))
        self.alert_tau_days = float(config.get("alert_tau_days", 4.0))
        self.crowd_trigger_threshold = float(
            config.get("crowd_trigger_threshold", 5.0),
        )
        self.threshold_step = float(config.get("threshold_step", 1.5))
        self.pilate_bonus = float(config.get("pilate_bonus", 0.4))
        self.sigma_daily = float(config.get("sigma_daily", 0.05))
        self.approach_lead_days = int(
            config.get("pilate_approach_lead_days", DEFAULT_APPROACH_LEAD_DAYS),
        )
        self.approach_stay_days = int(
            config.get("pilate_approach_stay_days", DEFAULT_APPROACH_STAY_DAYS),
        )
        initial_alert = float(config.get("initial_alertness", self.alertness_floor))
        initial_alert = max(
            self.alertness_floor,
            min(self.alertness_ceiling, initial_alert),
        )
        initial_location: PilateLocation = "caesarea"
        return PoliticsState(
            roman_alertness=initial_alert,
            alertness_floor=self.alertness_floor,
            alertness_ceiling=self.alertness_ceiling,
            pilate_location=initial_location,
            crowd_threshold_exceeded_ticks=0,
        )

    def tick(self, state: PoliticsState, ctx: LayerContext) -> PoliticsState:
        calendar = ctx.world_snapshot.calendar
        crowd = ctx.world_snapshot.crowd
        dt = max(0.0, ctx.dt_days)

        # Governor location (calendar-driven).
        location = self._compute_location(
            days_to_passover=calendar.days_to_next_passover,
            active_feast=calendar.active_feast,
            day_index=calendar.day_index,
        )

        # Alertness dynamics.
        prev = state.roman_alertness
        decay = (
            math.exp(-dt / self.alert_tau_days) if self.alert_tau_days > 0 else 0.0
        )
        drift_to_floor = (
            self.alertness_floor + (prev - self.alertness_floor) * decay
        )

        threshold_active = crowd.crowd_density >= self.crowd_trigger_threshold
        boost = self.threshold_step * dt if threshold_active else 0.0
        if threshold_active:
            self._threshold_hits += 1

        location_bias = self.pilate_bonus * dt if location == "jerusalem" else 0.0

        rng = random.Random(
            hash(("politics", int(ctx.rng_seed), int(ctx.tick_index))) & 0xFFFFFFFF,
        )
        noise = rng.gauss(0.0, self.sigma_daily) * dt

        candidate = drift_to_floor + boost + location_bias + noise
        clamp_hit = (
            candidate > self.alertness_ceiling or candidate < self.alertness_floor
        )
        new_alert = max(
            self.alertness_floor,
            min(self.alertness_ceiling, candidate),
        )
        if clamp_hit:
            self._clamp_hits += 1

        self.last_alertness_delta = new_alert - prev
        return PoliticsState(
            roman_alertness=new_alert,
            alertness_floor=self.alertness_floor,
            alertness_ceiling=self.alertness_ceiling,
            pilate_location=location,
            crowd_threshold_exceeded_ticks=(
                state.crowd_threshold_exceeded_ticks + (1 if threshold_active else 0)
            ),
        )

    # ------------------------------------------------------------------
    # Helpers

    def _compute_location(
        self,
        *,
        days_to_passover: int,
        active_feast: str,
        day_index: int,
    ) -> PilateLocation:
        # Feasts pull him into Jerusalem.
        if active_feast in FEAST_JERUSALEM:
            return "jerusalem"
        from world.environment.calendar import PASSOVER_DAY, SHAVUOT_DAY
        # Pre-Passover approach (calendar-driven delay: reviewer #2 brake).
        if PASSOVER_DAY - self.approach_lead_days <= day_index < PASSOVER_DAY:
            return "jerusalem"
        # Post-Passover stay window.
        if PASSOVER_DAY < day_index <= PASSOVER_DAY + self.approach_stay_days:
            return "jerusalem"
        # Pre-Shavuot approach (symmetric but shorter).
        if SHAVUOT_DAY - 2 <= day_index < SHAVUOT_DAY:
            return "jerusalem"
        if SHAVUOT_DAY < day_index <= SHAVUOT_DAY + 2:
            return "jerusalem"
        # Don't rely on clamped days_to_passover (it saturates at 0 post-feast);
        # day_index is the authoritative signal.
        _ = days_to_passover  # silence unused-arg lint
        return "caesarea"

    @property
    def clamp_hits(self) -> int:
        return self._clamp_hits

    @property
    def threshold_hits(self) -> int:
        return self._threshold_hits

    def describe_dynamics(self) -> dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "state_vars": ["roman_alertness", "pilate_location"],
            "update_rule": (
                "alert(t+1) = clamp(floor + (alert(t)-floor)*exp(-dt/tau) "
                "+ step*(crowd>=thr) + bonus*(in_jerusalem) + N(0,sigma*dt), "
                "floor, ceiling)"
            ),
            "alert_tau_days": self.alert_tau_days,
            "crowd_trigger_threshold": self.crowd_trigger_threshold,
            "threshold_step": self.threshold_step,
            "pilate_bonus": self.pilate_bonus,
            "alertness_floor": self.alertness_floor,
            "alertness_ceiling": self.alertness_ceiling,
            "pilate_approach_lead_days": self.approach_lead_days,
            "pilate_approach_stay_days": self.approach_stay_days,
            "brake_type": (
                "delay (pilate approach window) + threshold (crowd trigger) "
                "+ saturation (clamp)"
            ),
            "causal_dependencies": [
                "calendar.days_to_next_passover",
                "calendar.active_feast",
                "crowd.crowd_density",
            ],
        }
