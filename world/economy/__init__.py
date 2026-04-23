"""Layer 2 — economy sub-layers.

- :class:`EconomyLayer` — Spike 1B staple_price (legacy).
- :class:`TempleEconomyLayer` — Spike 5 Part 2 Phase 5D.1.
- :class:`TaxationLayer` — Spike 5 Part 2 Phase 5D.2.
- :class:`CrossEconomyCoordinator` — Spike 5 Part 2 Phase 5D.3.
"""

from world.economy.cross_economy import CrossEconomyCoordinator, EconomyChannels
from world.economy.economy import EconomyLayer
from world.economy.taxation import TaxationInputs, TaxationLayer, TaxationState
from world.economy.temple_economy import (
    TempleEconomyInputs,
    TempleEconomyLayer,
    TempleEconomyState,
)

__all__ = [
    "EconomyLayer",
    "TempleEconomyLayer",
    "TempleEconomyState",
    "TempleEconomyInputs",
    "TaxationLayer",
    "TaxationState",
    "TaxationInputs",
    "CrossEconomyCoordinator",
    "EconomyChannels",
]
