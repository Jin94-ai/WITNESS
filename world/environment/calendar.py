"""CalendarLayer — Layer 1 Hebrew calendar (Spike 1A).

Models a ~90-day window starting at Nisan 1. Spike 1A tracks only:

- Nisan / Iyyar / Sivan month labels and day-of-month.
- Shabbat recurrence (every 7 days from an anchor).
- Named feasts that matter for the crowd dynamics this spike tests:
    * Passover               — Nisan 14 (single-day peak)
    * Unleavened Bread       — Nisan 15–21 (7-day window)
    * Firstfruits            — Nisan 16 (overlaps Unleavened Bread)
    * Shavuot / Pentecost    — Sivan 6 (50 days from Firstfruits, Lev 23:15-16)
- Pilgrim-influx target per day: superposition of two asymmetric Gaussians
  peaked at Passover and Shavuot.

Update rule (per reviewer #1):

    day_index     ← day_index + 1                       every tick (dt=1)
    day_of_month, hebrew_month  ← month arithmetic
    is_shabbat    ← (day_index - shabbat_anchor) % 7 == 0
    active_feast  ← feast window membership (see _feast_at)
    pilgrim_influx_target(d) =
          amp_p * exp(-0.5 ((d - p) / sig_p_{pre,post})^2)        [Passover]
        + amp_s * exp(-0.5 ((d - s) / sig_s_{pre,post})^2)        [Shavuot]

Time constant: 1 day per tick (dt_days fixed at 1.0 for Spike 1A).
Observation outputs: CalendarState (fed into CrowdLayer via LayerContext).

This layer has no own stochasticity: given the same anchor, the calendar
slice is deterministic. Stochasticity enters through the crowd layer and is
seeded from LayerContext.rng_seed.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from world.core.layer import LayerContext
from world.core.world_state import CalendarState, FeastName

# --- Hebrew month layout for the Spike 1A 90-day window -------------------
# Nisan 30 + Iyyar 29 + Sivan 30 = 89 days, rounded to 90 for the demo.
# Biblical/rabbinic lengths (see Mishnah Arakhin 2:2) — not claiming calendar
# astronomical precision, only that the named days land in the right slots
# for the feast tests.
NISAN_LEN = 30
IYYAR_LEN = 29
SIVAN_LEN = 30


MONTHS = (
    ("nisan", NISAN_LEN),
    ("iyyar", IYYAR_LEN),
    ("sivan", SIVAN_LEN),
)


# --- Feast anchor days within the Nisan-1-origin window -------------------
# All offsets are 0-based day_index values assuming day_index 0 == Nisan 1.
PASSOVER_DAY = 13          # Nisan 14
UNLEAVENED_START = 14      # Nisan 15
UNLEAVENED_END = 20        # Nisan 21 (inclusive)
FIRSTFRUITS_DAY = 15       # Nisan 16
SHAVUOT_DAY = 64           # Sivan 6  ( = Firstfruits + 49 )


def _month_for_day(day_index: int) -> tuple[str, int]:
    """Return (month_name, day_of_month_1based) for a 0-based day index."""
    remaining = day_index
    for name, length in MONTHS:
        if remaining < length:
            return name, remaining + 1
        remaining -= length
    # Past the 3-month window: clamp to Sivan 30 for Spike 1A.
    return "sivan", SIVAN_LEN


def _feast_at(day_index: int) -> FeastName:
    if day_index == PASSOVER_DAY:
        return "passover"
    if day_index == FIRSTFRUITS_DAY:
        return "firstfruits"
    if UNLEAVENED_START <= day_index <= UNLEAVENED_END:
        return "unleavened_bread"
    if day_index == SHAVUOT_DAY:
        return "shavuot"
    return "none"


@dataclass
class _InfluxProfile:
    peak_day: int
    amplitude: float
    sigma_pre: float
    sigma_post: float

    def contribution(self, day_index: int) -> float:
        offset = day_index - self.peak_day
        sigma = self.sigma_pre if offset < 0 else self.sigma_post
        if sigma <= 0:
            return 0.0
        return self.amplitude * math.exp(-0.5 * (offset / sigma) ** 2)


class CalendarLayer:
    """Layer 1 implementation: calendar + feast + pilgrim-influx target.

    Parameters are taken from ``WorldConfig.calendar_config`` JSON:

    - ``shabbat_anchor_day_index``: int, the day_index of the first Shabbat.
      AD 30 tradition: Nisan 15 (day_index 14) was the weekly Shabbat, so the
      default is 14.
    - ``passover_amplitude``: peak pilgrim-target at Passover (unitless).
    - ``passover_sigma_pre`` / ``passover_sigma_post``: Gaussian widths
      controlling the ramp-up / decay around Passover.
    - ``shavuot_amplitude`` + ``shavuot_sigma_*``: same for Shavuot.
    """

    layer_id = "calendar"

    def __init__(self, shabbat_anchor_day_index: int = 14) -> None:
        # Default anchor chosen so that Passover (Nisan 14) falls on the day
        # before a Shabbat — the common AD-30 chronology.
        self.shabbat_anchor = shabbat_anchor_day_index
        self._profiles: list[_InfluxProfile] = []

    # ------------------------------------------------------------------
    # Layer protocol

    def initial_state(self, config: dict[str, Any]) -> CalendarState:
        self.shabbat_anchor = int(
            config.get("shabbat_anchor_day_index", self.shabbat_anchor),
        )
        self._profiles = [
            _InfluxProfile(
                peak_day=PASSOVER_DAY,
                amplitude=float(config.get("passover_amplitude", 10.0)),
                sigma_pre=float(config.get("passover_sigma_pre", 4.5)),
                sigma_post=float(config.get("passover_sigma_post", 3.0)),
            ),
            _InfluxProfile(
                peak_day=SHAVUOT_DAY,
                amplitude=float(config.get("shavuot_amplitude", 4.0)),
                sigma_pre=float(config.get("shavuot_sigma_pre", 4.0)),
                sigma_post=float(config.get("shavuot_sigma_post", 3.0)),
            ),
        ]
        return self._state_at(0)

    def tick(self, state: CalendarState, ctx: LayerContext) -> CalendarState:
        advance = max(1, int(round(ctx.dt_days)))
        next_day = state.day_index + advance
        return self._state_at(next_day)

    # ------------------------------------------------------------------
    # Helpers (also used by tests through describe_dynamics)

    def pilgrim_influx(self, day_index: int) -> float:
        if not self._profiles:
            return 0.0
        return sum(p.contribution(day_index) for p in self._profiles)

    def _state_at(self, day_index: int) -> CalendarState:
        month, dom = _month_for_day(day_index)
        is_shabbat = (day_index - self.shabbat_anchor) % 7 == 0
        feast = _feast_at(day_index)
        days_to_passover = max(0, PASSOVER_DAY - day_index)
        return CalendarState(
            day_index=day_index,
            hebrew_month=month,
            day_of_month=dom,
            is_shabbat=is_shabbat,
            active_feast=feast,
            days_to_next_passover=days_to_passover,
            pilgrim_influx_target=self.pilgrim_influx(day_index),
        )

    def describe_dynamics(self) -> dict[str, Any]:
        """Returned to tests / demo to verify documented dynamics."""
        return {
            "layer_id": self.layer_id,
            "dt_days": 1.0,
            "deterministic": True,
            "feast_days": {
                "passover": PASSOVER_DAY,
                "firstfruits": FIRSTFRUITS_DAY,
                "unleavened_bread_range": [UNLEAVENED_START, UNLEAVENED_END],
                "shavuot": SHAVUOT_DAY,
            },
            "shabbat_anchor": self.shabbat_anchor,
            "pilgrim_profiles": [
                {
                    "peak_day": p.peak_day,
                    "amplitude": p.amplitude,
                    "sigma_pre": p.sigma_pre,
                    "sigma_post": p.sigma_post,
                }
                for p in self._profiles
            ],
        }
