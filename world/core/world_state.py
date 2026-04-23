"""WorldState — immutable composite of every layer's state slice.

Spike 1A carries only two substantive slices:

- :class:`CalendarState` (Layer 1) — day index within a Hebrew month cycle.
- :class:`CrowdState` (Layer 5) — aggregate crowd density in Jerusalem.

Later spikes append economy / politics / factions slices without touching the
two slices defined here. Frozen dataclasses + ``with_*`` replacement helpers
keep the whole state hashable and safe to pass into ``LayerContext``.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Literal

FeastName = Literal[
    "none",
    "passover",
    "unleavened_bread",
    "firstfruits",
    "shavuot",
]


@dataclass(frozen=True)
class CalendarState:
    """Layer 1 — Jewish calendar slice."""

    day_index: int
    """Day offset from simulation start (0-based)."""

    hebrew_month: str
    """'nisan' / 'iyyar' / 'sivan' for Spike 1A's 90-day window."""

    day_of_month: int
    """1..30 within the Hebrew month."""

    is_shabbat: bool
    """Shabbat recurrence — every 7 days from the anchor."""

    active_feast: FeastName
    """Currently-active multi-day feast window."""

    days_to_next_passover: int
    """Days until the upcoming Passover (≥0). Clamps at 0 after Passover."""

    pilgrim_influx_target: float
    """Per-day pilgrim headcount arriving *today* (normalised unit-scaled)."""


@dataclass(frozen=True)
class CrowdState:
    """Layer 5 — aggregate social signal slice."""

    crowd_density: float
    """Current crowd density (0..ceiling). See ``crowd.py`` for equation."""

    baseline_density: float
    """Resident-population floor; decay target when no pilgrim influx."""

    density_ceiling: float
    """Hard upper bound enforced by clamp + logged as runaway indicator."""

    peak_density_observed: float
    """Max density seen across the run so far (diagnostic only)."""

    overflow_pressure: float = 0.0
    """Pre-clamp excess above ``density_ceiling``. Zero when the clamp did
    not fire this tick. Spike 2+ agents may perceive this as "no room left
    inside the city walls" — see docs/world/SPIKE_1_REVIEW.md Q2."""


@dataclass(frozen=True)
class EconomyState:
    """Layer 2 — economic slice (Spike 1B).

    Spike 1B tracks only staple_price. Later spikes add temple_revenue,
    tax_burden, trade_activity, poverty_rate (WORLD_DESIGN.md §3.2 Layer 2).
    """

    staple_price: float
    """Current staple (grain) price (price_floor..price_ceiling)."""

    price_floor: float
    """Baseline price — decay target when no demand shock."""

    price_ceiling: float
    """Hard upper bound. Logged as runaway indicator when hit."""

    demand_pressure_3d_avg: float
    """3-day rolling average of pilgrim influx, buffers the price response
    (reviewer #2 delay). Price at t+1 reads this, not the instantaneous
    pilgrim count."""


PilateLocation = Literal["caesarea", "jerusalem"]


RomanStance = Literal["cooperative", "neutral", "resistant"]


@dataclass(frozen=True)
class FactionSnapshot:
    """Layer 4 — one organised group (bloc) as of one tick (Spike 3 Phase 3A).

    Tier 3 "statistical agent" — the bloc has scalar influence and
    militancy, not a Pydantic AgentState. Per WORLD_DESIGN.md §3.1,
    Layer 4 represents *organised groups*; Layer 5 holds *population
    fields* (rumours, crowd density).

    Spike 3 Phase 3A: independent dynamics only — each faction drifts
    toward its ``target_influence`` with decay, under stochastic
    fluctuation. Cross-layer feedback (crowd → zealot militancy,
    rumour → jesus_movement) is added in Phase 3B.
    """

    faction_id: str
    influence: float
    militancy: float
    roman_stance: RomanStance
    target_influence: float
    growth_rate: float


@dataclass(frozen=True)
class FactionState:
    """Layer 4 — collection of factions indexed by id."""

    factions: dict[str, FactionSnapshot] = field(default_factory=dict)

    def get(self, faction_id: str) -> FactionSnapshot | None:
        return self.factions.get(faction_id)


@dataclass(frozen=True)
class Rumor:
    """One rumour in the population-level rumour graph (Layer 5, Spike 3 Phase 3C).

    Spread (0..1): fraction of the population that has heard the rumour.
    Credibility (0..1): how believable the rumour is right now.
    Age in days: how long since it was seeded. Rumours are garbage-collected
    when age exceeds a per-layer max_age_days.

    Spike 5 Part 1 additions (Phase 5C):
    - ``source_location``: where the rumour originated (e.g. "temple"). Used
      by ``spatial_propagation_factor`` to give a locality bonus/penalty.
    - ``age_in_substeps``: fine-grained age counter used by Spike 2+ agents
      who tick at substep resolution. Coexists with ``age_days``.
    """

    rumor_id: str
    content: str
    source_agent: str
    spread: float
    credibility: float
    age_days: float
    source_location: str | None = None
    age_in_substeps: int = 0


@dataclass(frozen=True)
class RumorState:
    """Layer 5 (rumour sub-state) — active rumours + bookkeeping."""

    rumors: tuple[Rumor, ...] = ()
    seeded_total: int = 0
    expired_total: int = 0

    def active_intensity(self) -> float:
        """Aggregate spread × credibility across active rumours (Phase 3C
        input to factions / agent percepts)."""
        if not self.rumors:
            return 0.0
        return sum(r.spread * r.credibility for r in self.rumors)


@dataclass(frozen=True)
class PoliticsState:
    """Layer 3 — Roman / temple politics slice (Spike 1C).

    Spike 1C tracks only:
    - ``roman_alertness``: governor + garrison vigilance (0..10).
    - ``pilate_location``: the governor moves to Jerusalem during the
      Passover window and returns to Caesarea after — a classic
      calendar-driven political datum (Josephus, Ant. 18).

    Later spikes add high_priest, sanhedrin, faction-driven pressure.
    """

    roman_alertness: float
    """Governor's alertness level (0..ceiling)."""

    alertness_floor: float
    """Decay target — background vigilance with no feast / no unrest."""

    alertness_ceiling: float
    """Hard upper bound."""

    pilate_location: PilateLocation
    """Governor's current location; feast windows pull him to Jerusalem."""

    crowd_threshold_exceeded_ticks: int
    """Tally of ticks the crowd density exceeded the alertness-trigger
    threshold. Used to document the threshold-triggered brake."""


@dataclass(frozen=True)
class LayerTelemetry:
    """Per-layer diagnostic counters exposed to the demo + tests.

    Used by the runaway detector and by the success-criteria checks. Keep it a
    flat structure so JSON dumps from the demo are grep-friendly.
    """

    runaway_warnings: int = 0
    clamp_hits: int = 0
    rate_limit_hits: int = 0


@dataclass(frozen=True)
class WorldState:
    """Immutable composite state snapshot of the world at one tick."""

    calendar: CalendarState
    crowd: CrowdState
    economy: "EconomyState | None" = None
    politics: "PoliticsState | None" = None
    factions: "FactionState | None" = None
    rumors: "RumorState | None" = None
    telemetry: dict[str, LayerTelemetry] = field(default_factory=dict)

    def with_calendar(self, calendar: CalendarState) -> "WorldState":
        return replace(self, calendar=calendar)

    def with_crowd(self, crowd: CrowdState) -> "WorldState":
        return replace(self, crowd=crowd)

    def with_economy(self, economy: "EconomyState") -> "WorldState":
        return replace(self, economy=economy)

    def with_politics(self, politics: "PoliticsState") -> "WorldState":
        return replace(self, politics=politics)

    def with_factions(self, factions: "FactionState") -> "WorldState":
        return replace(self, factions=factions)

    def with_rumors(self, rumors: "RumorState") -> "WorldState":
        return replace(self, rumors=rumors)

    def with_telemetry(self, layer_id: str, telem: LayerTelemetry) -> "WorldState":
        merged = dict(self.telemetry)
        merged[layer_id] = telem
        return replace(self, telemetry=merged)
