"""Spatial layer — Location affordance + agent location tracking.

Locations provide affordances (visibility / concealment / authority_reach / ...)
that modulate agent action availability.

Rule #1: location_id generic (e.g. "public_square", "private_dwelling");
scenario content에서 이름 바인딩.
"""

from engine.world.spatial.location import (
    Location,
    LocationTag,
)
from engine.world.spatial.spatial_registry import (
    SpatialRegistry,
)

__all__ = [
    "Location",
    "LocationTag",
    "SpatialRegistry",
]
