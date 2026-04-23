"""CrowdLayer — Layer 5 aggregate crowd density (Spike 1A).

Update equation (per reviewer #1: explicit dynamics) ::

    density(t+1) = clamp(
        baseline
        + (density(t) - baseline) * exp(-dt_days / tau_days)     # decay
        + pilgrim_influx_target(t) * inflow_weight               # arrival
        + N(0, sigma_daily)                                       # noise
    , min=baseline, max=ceiling)

Term-by-term rationale:

- **Decay** (reviewer #2: saturation + delay). Without new pilgrims the
  density relaxes back to ``baseline`` with e-folding time ``tau_days``.
  This is the "brake" between the calendar layer and the crowd layer: even a
  step-up in pilgrim-target does not produce an instantaneous spike; the
  system integrates over ``tau_days``.
- **Influx** (reviewer #7: causal consistency). ``pilgrim_influx_target`` is
  non-negative by construction (Gaussian superposition with non-negative
  amplitude), so higher calendar-level influx deterministically raises the
  drift term. The test suite pins this monotonicity.
- **Noise** (flatline-avoidance + reviewer #3 success criterion #5). Each
  layer derives its own RNG from ``ctx.rng_seed`` so the calendar remains
  deterministic while the crowd admits per-seed variation.
- **Clamp** (reviewer #6: runaway detection). ``ceiling`` is the hard upper
  bound. The layer reports ``clamp_hits`` on each tick that hits the ceiling,
  which the runaway detector aggregates across a run.

Time constant: tau_days (default 3.5) — e-folding days toward baseline.
Observation output: CrowdState.crowd_density (consumed by future Layer 3
roman_alertness in Spike 1C, and by agent EnvironmentState.crowd_pressure
in Spike 2).
"""

from __future__ import annotations

import math
import random
from typing import Any

from world.core.layer import LayerContext
from world.core.world_state import CrowdState


class CrowdLayer:
    """Layer 5 — aggregate crowd density driven by calendar pilgrim influx."""

    layer_id = "crowd"

    def __init__(self) -> None:
        self.baseline: float = 1.0
        self.ceiling: float = 10.0
        self.tau_days: float = 3.5
        self.inflow_weight: float = 0.30
        self.sigma_daily: float = 0.05
        # Bookkeeping: last_rate is used by the runaway detector for its
        # "sudden change" warning. Layer owns only its own diagnostics.
        self._clamp_hits = 0
        self._rate_limit_hits = 0
        self._runaway_warnings = 0
        # `last_density_update_delta` is the most recent per-tick change,
        # exposed read-only for the runaway detector.
        self.last_density_update_delta: float = 0.0

    # ------------------------------------------------------------------
    # Layer protocol

    def initial_state(self, config: dict[str, Any]) -> CrowdState:
        self.baseline = float(config.get("baseline_density", 1.0))
        self.ceiling = float(config.get("density_ceiling", 10.0))
        self.tau_days = float(config.get("tau_days", 3.5))
        self.inflow_weight = float(config.get("inflow_weight", 0.30))
        self.sigma_daily = float(config.get("sigma_daily", 0.05))
        start_density = float(config.get("initial_density", self.baseline))
        # Clamp initial density within legal range to avoid bootstrap NaNs.
        start_density = max(self.baseline, min(self.ceiling, start_density))
        return CrowdState(
            crowd_density=start_density,
            baseline_density=self.baseline,
            density_ceiling=self.ceiling,
            peak_density_observed=start_density,
            overflow_pressure=0.0,
        )

    def tick(self, state: CrowdState, ctx: LayerContext) -> CrowdState:
        prev = state.crowd_density
        calendar = ctx.world_snapshot.calendar
        influx = max(0.0, calendar.pilgrim_influx_target)
        dt = max(0.0, ctx.dt_days)

        decay_factor = math.exp(-dt / self.tau_days) if self.tau_days > 0 else 0.0
        drift_toward_baseline = self.baseline + (prev - self.baseline) * decay_factor
        drift_from_influx = influx * self.inflow_weight * dt

        # Per-layer RNG substream: calendar tick + seed so crowd has its own
        # deterministic per-seed noise without colliding with other layers.
        rng = random.Random(
            hash(("crowd", int(ctx.rng_seed), int(ctx.tick_index))) & 0xFFFFFFFF
        )
        noise = rng.gauss(0.0, self.sigma_daily * max(self.baseline, 1.0)) * dt

        candidate = drift_toward_baseline + drift_from_influx + noise

        clamp_hit = candidate > self.ceiling or candidate < self.baseline
        new_density = max(self.baseline, min(self.ceiling, candidate))
        if clamp_hit:
            self._clamp_hits += 1

        # A-2: overflow_pressure tracks pre-clamp excess above the ceiling.
        # This lets Spike 2+ agents perceive "city is overfull — no room
        # inside the walls" without needing to know the clamp implementation.
        # When the candidate was below the floor the field stays at 0.
        overflow_pressure = max(0.0, candidate - self.ceiling)

        self.last_density_update_delta = new_density - prev
        peak = max(state.peak_density_observed, new_density)
        return CrowdState(
            crowd_density=new_density,
            baseline_density=self.baseline,
            density_ceiling=self.ceiling,
            peak_density_observed=peak,
            overflow_pressure=overflow_pressure,
        )

    # ------------------------------------------------------------------
    # Diagnostics exposed to the runaway detector / tests.

    @property
    def clamp_hits(self) -> int:
        return self._clamp_hits

    @property
    def rate_limit_hits(self) -> int:
        return self._rate_limit_hits

    @property
    def runaway_warnings(self) -> int:
        return self._runaway_warnings

    def note_runaway_warning(self) -> None:
        self._runaway_warnings += 1

    def note_rate_limit(self) -> None:
        self._rate_limit_hits += 1

    def describe_dynamics(self) -> dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "update_rule": (
                "density(t+1) = clamp("
                "baseline + (density(t)-baseline)*exp(-dt/tau) "
                "+ influx*w*dt + N(0,sigma*dt), baseline, ceiling)"
            ),
            "tau_days": self.tau_days,
            "inflow_weight": self.inflow_weight,
            "baseline": self.baseline,
            "ceiling": self.ceiling,
            "sigma_daily": self.sigma_daily,
            "causal_dependencies": ["calendar.pilgrim_influx_target"],
        }
