"""Cross-economy coordinator — Spike 5 Part 2 Phase 5D.3.

Three independent economy sub-layers:

1. ``EconomyLayer`` (staple_price, legacy Spike 1B) — unchanged.
2. ``TempleEconomyLayer`` (Phase 5D.1) — fee / sacrifice / crowd_frustration.
3. ``TaxationLayer`` (Phase 5D.2) — collection_intensity / activity.

The coordinator exposes the *indirect channels* between them and between
the economy and the agent/faction layers:

- temple_economy.crowd_frustration → jesus_movement.sympathy
- taxation.collection_intensity → zealots.militancy + crowd_frustration
- staple_price spikes → general_discontent (rumour spawn rate)

It does NOT run a single unified tick — each sub-layer keeps its own
tick to honor Rule #9 (no same-tick feedback). The coordinator only
exposes *read channels* that a downstream layer (factions / rumours /
agents) may consume on the next substep.
"""

from __future__ import annotations

from dataclasses import dataclass

from world.economy.taxation import TaxationLayer, TaxationState
from world.economy.temple_economy import TempleEconomyLayer, TempleEconomyState


@dataclass(frozen=True)
class EconomyChannels:
    """Aggregate of every indirect channel this tick exposes to downstream
    layers. Must be consumed *next* substep.
    """

    temple_to_jesus_sympathy: float
    taxation_to_zealot_militancy: float
    taxation_to_crowd_frustration: float
    staple_to_discontent: float


class CrossEconomyCoordinator:
    """Read-only aggregator: pulls channels from each sub-layer per tick."""

    def __init__(
        self,
        *,
        temple: TempleEconomyLayer,
        taxation: TaxationLayer,
        discontent_price_ref: float = 1.0,
        discontent_slope: float = 0.12,
    ) -> None:
        self.temple = temple
        self.taxation = taxation
        self.discontent_price_ref = discontent_price_ref
        self.discontent_slope = discontent_slope

    def snapshot_channels(
        self,
        *,
        temple_state: TempleEconomyState,
        taxation_state: TaxationState,
        staple_price: float,
    ) -> EconomyChannels:
        discontent = max(
            0.0,
            (staple_price - self.discontent_price_ref) * self.discontent_slope,
        )
        return EconomyChannels(
            temple_to_jesus_sympathy=self.temple.frustration_channel(temple_state),
            taxation_to_zealot_militancy=self.taxation.zealot_militancy_channel(
                taxation_state,
            ),
            taxation_to_crowd_frustration=self.taxation.crowd_frustration_channel(
                taxation_state,
            ),
            staple_to_discontent=discontent,
        )
