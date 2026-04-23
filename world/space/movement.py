"""movement — cost model for agent relocation (Phase 5C).

Same-region (Jerusalem intra-city) moves cost 2 person-substeps.
Cross-region moves (to/from galilee_distant) cost 4 substeps. These
numbers come from Part 1 spec §3.2.2 and can be overridden via
``plan_move(..., override_cost=...)``.
"""

from __future__ import annotations

from world.space.location import region_of

MOVE_COST_SAME_REGION: int = 2
MOVE_COST_CROSS_REGION: int = 4


def plan_move(
    from_location: str, to_location: str, *, override_cost: int | None = None,
) -> int:
    """Return the number of substeps required for the move.

    Same location (including both 'transit'): 0 (no-op).
    Same region: ``MOVE_COST_SAME_REGION``.
    Cross-region: ``MOVE_COST_CROSS_REGION``.
    """
    if override_cost is not None:
        return max(0, int(override_cost))
    if from_location == to_location:
        return 0
    if from_location == "transit" or to_location == "transit":
        # Transit is not a valid destination; treat as same-region cost.
        return MOVE_COST_SAME_REGION
    if region_of(from_location) == region_of(to_location):
        return MOVE_COST_SAME_REGION
    return MOVE_COST_CROSS_REGION
