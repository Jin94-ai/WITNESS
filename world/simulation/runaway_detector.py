"""RunawayDetector — reviewer #6 safety net.

Responsibilities:

- Enforce per-variable absolute ceilings declared in ``WorldConfig.runaway_limits``
  by counting clamps.
- Flag *rate-of-change* excursions: if a monitored variable moves by more than
  ``max_abs_delta_per_day * dt_days`` in one tick, log a warning. Rate-limit
  itself is soft; we do not clamp the value — we annotate the telemetry so the
  demo + tests can assert the warning count.
- Emit structured log lines that the demo captures to stdout and that tests
  can pattern-match.

The detector is stateless beyond a per-run ``warnings`` log and a cheap
counter, so runs do not accumulate state across seeds.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("world.runaway")


@dataclass
class RunawayReport:
    warnings: list[str] = field(default_factory=list)
    rate_limit_hits: int = 0
    ceiling_hits: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "warnings_count": len(self.warnings),
            "rate_limit_hits": self.rate_limit_hits,
            "ceiling_hits": self.ceiling_hits,
            # Keep last 10 warnings only — tests grep on substrings.
            "recent_warnings": self.warnings[-10:],
        }


class RunawayDetector:
    """Monitor world variables for unsafe growth and emit warnings."""

    def __init__(
        self,
        *,
        max_abs_delta_per_day: dict[str, float] | None = None,
        ceilings: dict[str, float] | None = None,
    ) -> None:
        self.max_abs_delta_per_day = max_abs_delta_per_day or {}
        self.ceilings = ceilings or {}
        self.report = RunawayReport()

    # ------------------------------------------------------------------
    # Per-tick monitoring API used by WorldTick.

    def observe(
        self, tick_index: int, dt_days: float, samples: dict[str, float],
        deltas: dict[str, float],
    ) -> None:
        """Record one tick's variable values + per-tick deltas.

        - ``samples``: variable_name -> current value.
        - ``deltas``: variable_name -> change since previous tick.
        """
        for name, value in samples.items():
            ceiling = self.ceilings.get(name)
            if ceiling is not None and value >= ceiling:
                self.report.ceiling_hits += 1
                msg = (
                    f"[runaway] t={tick_index} {name}={value:.3f} "
                    f"hit ceiling {ceiling:.3f}"
                )
                self.report.warnings.append(msg)
                logger.warning(msg)

        for name, delta in deltas.items():
            limit = self.max_abs_delta_per_day.get(name)
            if limit is None:
                continue
            effective_limit = abs(limit) * max(dt_days, 1e-6)
            if abs(delta) > effective_limit:
                self.report.rate_limit_hits += 1
                msg = (
                    f"[runaway] t={tick_index} {name} Δ={delta:+.3f} "
                    f"exceeds per-day limit {abs(limit):.3f}"
                )
                self.report.warnings.append(msg)
                logger.warning(msg)
