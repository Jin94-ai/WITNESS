"""Spike 5 Phase 5C — spatial model.

Locations + agent positions + movement cost + spatial rumour propagation.
No counterfactual experiments added (ABSOLUTE RULE #10). This module
gives the world "where" — the prerequisite for later diffusion analyses.
"""

from world.space.location import Location, default_locations
from world.space.movement import MOVE_COST_CROSS_REGION, MOVE_COST_SAME_REGION, plan_move
from world.space.position import AgentPosition, SpatialState
from world.space.rumour_spatial import (
    SpatialRumourParams,
    spatial_propagation_factor,
)

__all__ = [
    "Location",
    "default_locations",
    "AgentPosition",
    "SpatialState",
    "plan_move",
    "MOVE_COST_SAME_REGION",
    "MOVE_COST_CROSS_REGION",
    "SpatialRumourParams",
    "spatial_propagation_factor",
]
