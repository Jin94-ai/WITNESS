"""WorldConfig + WorldEffect aggregation interface.

``WorldConfig`` is the serialised payload loaded from ``content/worlds/.../``:
calendar anchors, feast schedule, crowd baseline / ceiling / response
parameters, seed, total tick count, ``dt_days``, etc. Layers receive only the
sub-dict they need.

``WorldEffect`` + ``WorldEffectChannel`` + ``AggregationMode`` are the
**interface** for Spike 2's agent-to-world bridge (reviewer point #5). In
Spike 1A the bridge is unused: ``LayerContext.aggregated_effects`` is always
empty. We still freeze the shape now so that Spike 2 does not have to retrofit
the calendar / crowd layers.

Aggregation semantics (each channel picks one):

- ``sum``: add every sub-step effect. Use for rumour-seed counts, shouts.
- ``mean``: average across sub-steps. Use for sentiment-like fields.
- ``max``: keep the worst / loudest effect. Use for shock-style signals.
- ``threshold``: fire only if at least one sub-step exceeds the threshold.
  Use for cross-layer trigger-style coupling ("any agent threw a stone").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AggregationMode(str, Enum):
    SUM = "sum"
    MEAN = "mean"
    MAX = "max"
    THRESHOLD = "threshold"


@dataclass(frozen=True)
class WorldEffectChannel:
    """A single named channel by which agent actions modify the world.

    Concrete channels are registered in Spike 2. Spike 1A only stores the
    shape so content packs can declare channels without the bridge existing.
    """

    channel_id: str
    aggregation: AggregationMode
    default: float = 0.0
    threshold: float | None = None

    def aggregate(self, values: list[float]) -> float:
        if not values:
            return self.default
        if self.aggregation is AggregationMode.SUM:
            return sum(values)
        if self.aggregation is AggregationMode.MEAN:
            return sum(values) / len(values)
        if self.aggregation is AggregationMode.MAX:
            return max(values)
        if self.aggregation is AggregationMode.THRESHOLD:
            if self.threshold is None:
                raise ValueError(
                    f"channel {self.channel_id}: THRESHOLD aggregation "
                    "requires a numeric threshold",
                )
            return 1.0 if any(v >= self.threshold for v in values) else 0.0
        raise ValueError(f"unknown aggregation: {self.aggregation}")


@dataclass(frozen=True)
class WorldEffect:
    """Single emitted effect from one agent sub-step. Spike 2+ only.

    Kept in Spike 1A as a placeholder so the bridge can land without breaking
    existing callers. ``value`` is written into the channel's aggregator by
    the sync layer.
    """

    channel_id: str
    value: float
    origin_agent: str


@dataclass(frozen=True)
class WorldConfig:
    """Top-level world configuration, loaded from a JSON content pack."""

    world_id: str
    total_ticks: int
    dt_days: float
    rng_seed: int

    calendar_config: dict[str, Any] = field(default_factory=dict)
    """Sub-dict fed to Layer 1 (CalendarLayer.initial_state)."""

    crowd_config: dict[str, Any] = field(default_factory=dict)
    """Sub-dict fed to Layer 5 (CrowdLayer.initial_state)."""

    economy_config: dict[str, Any] = field(default_factory=dict)
    """Sub-dict fed to Layer 2 (EconomyLayer.initial_state) — Spike 1B+."""

    politics_config: dict[str, Any] = field(default_factory=dict)
    """Sub-dict fed to Layer 3 (PoliticsLayer.initial_state) — Spike 1C+."""

    factions_config: dict[str, Any] = field(default_factory=dict)
    """Sub-dict fed to Layer 4 (FactionLayer.initial_state) — Spike 3+."""

    rumors_config: dict[str, Any] = field(default_factory=dict)
    """Sub-dict fed to Layer 5 RumorLayer — Spike 3 Phase 3C+."""

    effect_channels: list[WorldEffectChannel] = field(default_factory=list)
    """Declared Spike 2 channels. Spike 1A ignores the aggregator itself."""

    runaway_limits: dict[str, float] = field(default_factory=dict)
    """Per-variable ceilings used by the runaway detector."""

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> "WorldConfig":
        channels = [
            WorldEffectChannel(
                channel_id=c["channel_id"],
                aggregation=AggregationMode(c["aggregation"]),
                default=float(c.get("default", 0.0)),
                threshold=(
                    float(c["threshold"]) if c.get("threshold") is not None
                    else None
                ),
            )
            for c in payload.get("effect_channels", [])
        ]
        return cls(
            world_id=payload["world_id"],
            total_ticks=int(payload["total_ticks"]),
            dt_days=float(payload.get("dt_days", 1.0)),
            rng_seed=int(payload.get("rng_seed", 0)),
            calendar_config=payload.get("calendar_config", {}),
            crowd_config=payload.get("crowd_config", {}),
            economy_config=payload.get("economy_config", {}),
            politics_config=payload.get("politics_config", {}),
            factions_config=payload.get("factions_config", {}),
            rumors_config=payload.get("rumors_config", {}),
            effect_channels=channels,
            runaway_limits=payload.get("runaway_limits", {}),
        )
