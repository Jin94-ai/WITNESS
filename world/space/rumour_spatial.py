"""Spatial rumour propagation helpers (Phase 5C).

Spec §3.2.3:
- same-location listeners: **1.5×** the base rate
- cross-location listeners: **0.3×**, and *only* if a transit agent is
  physically moving between the two locations (they carry the rumour).

These helpers return multiplicative factors. The existing
``world.social.rumors.RumorLayer`` stays the single authority on
intensity update; this module only gives the locality factor so the
layer can blend spatial information without a rewrite.

ABSOLUTE RULE #6: we do not touch the existing RumorLayer public API.
``spatial_propagation_factor`` is a pure function — any layer that
wants to opt in calls it.
"""

from __future__ import annotations

from dataclasses import dataclass

from world.space.position import SpatialState

# Multipliers from the spec.
SAME_LOCATION_BONUS: float = 1.5
CROSS_LOCATION_BONUS_WITH_CARRIER: float = 0.3
CROSS_LOCATION_BONUS_NO_CARRIER: float = 0.0


@dataclass(frozen=True)
class SpatialRumourParams:
    """Tunable multipliers for spatial rumour propagation."""

    same_location_factor: float = SAME_LOCATION_BONUS
    cross_with_carrier_factor: float = CROSS_LOCATION_BONUS_WITH_CARRIER
    cross_without_carrier_factor: float = CROSS_LOCATION_BONUS_NO_CARRIER


def spatial_propagation_factor(
    spatial: SpatialState,
    source_agent: str,
    target_agent: str,
    *,
    params: SpatialRumourParams | None = None,
) -> float:
    """Return the multiplicative factor for rumour propagation between
    ``source_agent`` and ``target_agent``.

    Rules:
    - both at the same location   ⇒ ``same_location_factor`` (1.5)
    - different locations + someone in transit between them
                                  ⇒ ``cross_with_carrier_factor`` (0.3)
    - different locations, no transit carrier
                                  ⇒ ``cross_without_carrier_factor`` (0.0)

    If either agent is unknown to ``spatial``, returns 1.0 (passthrough
    — spatial state is not yet tracking them, so don't modify the
    existing rumour rate).
    """
    p = params or SpatialRumourParams()
    src_loc = spatial.where(source_agent)
    tgt_loc = spatial.where(target_agent)
    if src_loc is None or tgt_loc is None:
        return 1.0
    if src_loc == "transit" or tgt_loc == "transit":
        # Sender in transit can emit; target must be settled to receive.
        # If both ends are transit, treat as no-carrier case.
        if src_loc == "transit" and tgt_loc != "transit":
            return p.cross_with_carrier_factor
        return p.cross_without_carrier_factor
    if src_loc == tgt_loc:
        return p.same_location_factor
    # Different settled locations — need a transit carrier between them.
    carriers = [
        aid for aid, pos in spatial.positions.items()
        if pos.is_in_transit
        and pos.destination in (src_loc, tgt_loc)
    ]
    if carriers:
        return p.cross_with_carrier_factor
    return p.cross_without_carrier_factor


def visible_state_for(spatial: SpatialState, agent_id: str, location_map: dict) -> dict:
    """Return the sub-state an agent can directly observe from its current
    location. Other-location information must arrive via rumour.

    ``location_map`` maps location_id → Location object.
    Return dict has keys: ``location``, ``crowd_density``,
    ``surveillance_level``, ``economic_activity`` (all None if unknown).
    """
    loc_id = spatial.where(agent_id)
    if loc_id is None or loc_id == "transit" or loc_id not in location_map:
        return {
            "location": loc_id,
            "crowd_density": None,
            "surveillance_level": None,
            "economic_activity": None,
        }
    loc = location_map[loc_id]
    return {
        "location": loc_id,
        "crowd_density": loc.crowd_density,
        "surveillance_level": loc.surveillance_level,
        "economic_activity": loc.economic_activity,
    }
