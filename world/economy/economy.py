"""EconomyLayer — Layer 2 staple_price dynamics (Spike 1B).

Update equation (reviewer #1 — explicit dynamics) ::

    demand_3d(t+1) = 0.66 * demand_3d(t) + 0.34 * pilgrim_influx(t)   # 3-day IIR avg
    price(t+1)    = clamp(
        price_floor
        + (price(t) - price_floor) * exp(-dt_days / price_tau_days)    # mean reversion
        + demand_3d(t+1) * demand_weight * dt_days                     # demand shock (delayed)
        + N(0, sigma_daily * dt_days)                                  # noise
    , min=price_floor, max=price_ceiling)

Reviewer hooks:

- **#1 dynamics**: the update is a two-step (demand IIR → price) cascade with
  every constant documented in the module. ``describe_dynamics()`` returns the
  same values for test introspection.
- **#2 cross-layer brakes**: a 3-day IIR average on pilgrim influx is the
  *delay*. Price does not spike on the same day a pilgrim wave arrives —
  it integrates over a ~3-day window. Saturation comes from the clamp.
- **#4 variable dt**: ``price_tau_days`` + ``sigma_daily`` + ``demand_weight``
  are all rate constants (per day) that the update multiplies by ``dt_days``.
- **#6 runaway detection**: the price is clamped to [price_floor, price_ceiling]
  and each clamp is counted via ``clamp_hits``.
- **#7 causal consistency test**: higher pilgrim influx ⇒ higher price after
  the 3-day lag. The corresponding test in test_economy.py pins this.

Time constant: ``price_tau_days`` (default 5 days) — e-folding back to floor
after the demand pulse ends.
Observation: EconomyState.staple_price, fed in Spike 2 to agent economic
pressure via Sync Layer.
"""

from __future__ import annotations

import math
import random
from typing import Any

from world.core.layer import LayerContext
from world.core.world_state import EconomyState


class EconomyLayer:
    """Layer 2 — staple_price (grain) dynamics driven by pilgrim demand."""

    layer_id = "economy"

    def __init__(self) -> None:
        self.price_floor: float = 1.0
        self.price_ceiling: float = 10.0
        self.price_tau_days: float = 5.0
        self.demand_weight: float = 0.08
        self.demand_memory: float = 0.66  # IIR coefficient on previous avg
        self.sigma_daily: float = 0.03
        self._clamp_hits = 0
        self.last_price_delta: float = 0.0

    # ------------------------------------------------------------------
    # Layer protocol

    def initial_state(self, config: dict[str, Any]) -> EconomyState:
        self.price_floor = float(config.get("price_floor", 1.0))
        self.price_ceiling = float(config.get("price_ceiling", 10.0))
        self.price_tau_days = float(config.get("price_tau_days", 5.0))
        self.demand_weight = float(config.get("demand_weight", 0.08))
        self.demand_memory = float(config.get("demand_memory", 0.66))
        self.sigma_daily = float(config.get("sigma_daily", 0.03))
        initial_price = float(config.get("initial_price", self.price_floor))
        initial_price = max(self.price_floor, min(self.price_ceiling, initial_price))
        return EconomyState(
            staple_price=initial_price,
            price_floor=self.price_floor,
            price_ceiling=self.price_ceiling,
            demand_pressure_3d_avg=0.0,
        )

    def tick(self, state: EconomyState, ctx: LayerContext) -> EconomyState:
        prev_price = state.staple_price
        influx = max(0.0, ctx.world_snapshot.calendar.pilgrim_influx_target)
        dt = max(0.0, ctx.dt_days)

        # IIR-filtered demand: the reviewer #2 brake.
        new_demand = (
            self.demand_memory * state.demand_pressure_3d_avg
            + (1.0 - self.demand_memory) * influx
        )

        decay = math.exp(-dt / self.price_tau_days) if self.price_tau_days > 0 else 0.0
        drift_to_floor = self.price_floor + (prev_price - self.price_floor) * decay
        demand_shock = new_demand * self.demand_weight * dt

        rng = random.Random(
            hash(("economy", int(ctx.rng_seed), int(ctx.tick_index))) & 0xFFFFFFFF,
        )
        noise = rng.gauss(0.0, self.sigma_daily) * dt

        candidate = drift_to_floor + demand_shock + noise
        clamp_hit = candidate > self.price_ceiling or candidate < self.price_floor
        new_price = max(self.price_floor, min(self.price_ceiling, candidate))
        if clamp_hit:
            self._clamp_hits += 1

        self.last_price_delta = new_price - prev_price
        return EconomyState(
            staple_price=new_price,
            price_floor=self.price_floor,
            price_ceiling=self.price_ceiling,
            demand_pressure_3d_avg=new_demand,
        )

    # ------------------------------------------------------------------
    # Diagnostics

    @property
    def clamp_hits(self) -> int:
        return self._clamp_hits

    def describe_dynamics(self) -> dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "update_rule": (
                "demand_3d(t+1) = memory*demand_3d(t) + (1-memory)*influx(t); "
                "price(t+1) = clamp(floor + (price(t)-floor)*exp(-dt/tau) "
                "+ demand_3d*w*dt + N(0,sigma*dt), floor, ceiling)"
            ),
            "price_tau_days": self.price_tau_days,
            "demand_weight": self.demand_weight,
            "demand_memory": self.demand_memory,
            "price_floor": self.price_floor,
            "price_ceiling": self.price_ceiling,
            "sigma_daily": self.sigma_daily,
            "causal_dependencies": ["calendar.pilgrim_influx_target"],
            "brake_type": "delay (3-day IIR) + saturation (clamp)",
        }
