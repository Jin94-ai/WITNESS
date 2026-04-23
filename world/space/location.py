"""Location — named places an agent can occupy (Spike 5 Phase 5C).

A ``Location`` is a lightweight immutable descriptor. 6 canonical
AD-30 locations are provided via ``default_locations()`` — content
packs may extend but the Spike 5 Part 1 scope uses these six.

- ``temple``            — public, high crowd + economy, moderate surveillance
- ``upper_room``        — private, inside Jerusalem, very low surveillance
- ``gethsemane``        — outskirt, low crowd, low surveillance
- ``praetorium``        — Roman seat, very high surveillance
- ``bethany``           — suburb of Jerusalem, low surveillance
- ``galilee_distant``   — far away, long transit cost, almost no surveillance

The three per-location scalars are normalised to [0, 1] so the values
can be averaged or weighted against agent percepts without scale
conflict.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

LocationId = Literal[
    "temple", "upper_room", "gethsemane",
    "praetorium", "bethany", "galilee_distant",
    # Reserved non-location placeholder (agent in motion between places).
    "transit",
]


# --- Region grouping -----------------------------------------------------
# Same-region moves cost less than cross-region moves. Jerusalem + its
# immediate suburbs form one region; galilee_distant is its own region.

_REGIONS: dict[str, str] = {
    "temple": "jerusalem",
    "upper_room": "jerusalem",
    "gethsemane": "jerusalem",
    "praetorium": "jerusalem",
    "bethany": "jerusalem_suburb",
    "galilee_distant": "galilee",
    "transit": "transit",
}


@dataclass(frozen=True)
class Location:
    """Immutable named place with population / surveillance / economy signals."""

    location_id: str
    crowd_density: float
    surveillance_level: float
    economic_activity: float
    region: str

    def __post_init__(self) -> None:
        for name, value in (
            ("crowd_density", self.crowd_density),
            ("surveillance_level", self.surveillance_level),
            ("economic_activity", self.economic_activity),
        ):
            if not (0.0 <= value <= 1.0):
                raise ValueError(
                    f"Location '{self.location_id}' {name}={value} outside [0,1]",
                )


def default_locations() -> dict[str, Location]:
    """Return the 6 canonical AD-30 locations keyed by location_id."""
    specs: list[tuple[str, float, float, float]] = [
        # id, crowd, surveillance, economy
        ("temple",          0.9, 0.55, 0.85),
        ("upper_room",      0.1, 0.05, 0.10),
        ("gethsemane",      0.1, 0.05, 0.05),
        ("praetorium",      0.4, 0.95, 0.40),
        ("bethany",         0.2, 0.10, 0.15),
        ("galilee_distant", 0.15, 0.02, 0.35),
    ]
    return {
        lid: Location(
            location_id=lid,
            crowd_density=cd,
            surveillance_level=sv,
            economic_activity=ec,
            region=_REGIONS[lid],
        )
        for lid, cd, sv, ec in specs
    }


def region_of(location_id: str) -> str:
    """Return the region label a location_id belongs to."""
    return _REGIONS.get(location_id, "unknown")
