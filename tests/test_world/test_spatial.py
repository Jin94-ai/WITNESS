"""Spike 5 Phase 5C — spatial model behavior tests.

Per spec §3.3, counterfactual tests are banned in this spike;
these are pure behavior tests of the new spatial primitives.
"""

from __future__ import annotations

import pytest

from world.space.location import Location, default_locations, region_of
from world.space.movement import (
    MOVE_COST_CROSS_REGION,
    MOVE_COST_SAME_REGION,
    plan_move,
)
from world.space.position import SpatialState
from world.space.rumour_spatial import (
    SAME_LOCATION_BONUS,
    SpatialRumourParams,
    spatial_propagation_factor,
    visible_state_for,
)

# ----------------------------------------------------------------------
# Location + region.

def test_default_locations_has_six_canonical_places() -> None:
    locs = default_locations()
    expected = {
        "temple", "upper_room", "gethsemane",
        "praetorium", "bethany", "galilee_distant",
    }
    assert set(locs.keys()) == expected


def test_location_scalars_in_unit_interval() -> None:
    for loc in default_locations().values():
        assert 0.0 <= loc.crowd_density <= 1.0
        assert 0.0 <= loc.surveillance_level <= 1.0
        assert 0.0 <= loc.economic_activity <= 1.0


def test_location_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        Location(
            location_id="bad", crowd_density=1.5,
            surveillance_level=0.5, economic_activity=0.5, region="test",
        )


def test_region_of_groups_jerusalem_locations() -> None:
    assert region_of("temple") == "jerusalem"
    assert region_of("praetorium") == "jerusalem"
    assert region_of("galilee_distant") == "galilee"
    assert region_of("bethany") == "jerusalem_suburb"


# ----------------------------------------------------------------------
# Movement cost.

def test_move_same_location_is_zero_cost() -> None:
    assert plan_move("temple", "temple") == 0


def test_move_within_jerusalem_is_same_region_cost() -> None:
    assert plan_move("temple", "praetorium") == MOVE_COST_SAME_REGION
    assert plan_move("upper_room", "gethsemane") == MOVE_COST_SAME_REGION


def test_move_to_galilee_is_cross_region_cost() -> None:
    assert plan_move("temple", "galilee_distant") == MOVE_COST_CROSS_REGION
    assert plan_move("galilee_distant", "praetorium") == MOVE_COST_CROSS_REGION


def test_agent_movement_takes_expected_substeps() -> None:
    """Spec test #5: named expected from spec §3.3 — movement cost."""
    state = SpatialState()
    state.place("pilate", "praetorium")
    # Short move: praetorium → temple (same region, 2 substeps).
    state.begin_move("pilate", "temple", cost_substeps=MOVE_COST_SAME_REGION)
    assert state.where("pilate") == "transit"
    state.advance_one_substep()
    assert state.where("pilate") == "transit"  # 1 substep left
    state.advance_one_substep()
    assert state.where("pilate") == "temple"  # arrived


def test_cross_region_move_takes_four_substeps() -> None:
    state = SpatialState()
    state.place("jesus", "galilee_distant")
    state.begin_move("jesus", "temple", cost_substeps=MOVE_COST_CROSS_REGION)
    for _ in range(MOVE_COST_CROSS_REGION - 1):
        state.advance_one_substep()
        assert state.where("jesus") == "transit"
    state.advance_one_substep()
    assert state.where("jesus") == "temple"


# ----------------------------------------------------------------------
# Visibility (information asymmetry).

def test_agent_at_temple_sees_temple_crowd_density() -> None:
    """Spec test #1."""
    state = SpatialState()
    state.place("peter", "temple")
    locs = default_locations()
    visible = visible_state_for(state, "peter", locs)
    assert visible["location"] == "temple"
    assert visible["crowd_density"] == pytest.approx(0.9)


def test_agent_at_gethsemane_cannot_see_praetorium_directly() -> None:
    """Spec test #2 — info asymmetry pin."""
    state = SpatialState()
    state.place("jesus", "gethsemane")
    state.place("pilate", "praetorium")
    locs = default_locations()
    jesus_view = visible_state_for(state, "jesus", locs)
    # Jesus sees gethsemane directly.
    assert jesus_view["location"] == "gethsemane"
    assert jesus_view["crowd_density"] == pytest.approx(0.1)
    # Jesus does NOT get praetorium's high surveillance directly from
    # visible_state_for — other-location info must travel via rumour.
    assert jesus_view["surveillance_level"] == pytest.approx(0.05)


# ----------------------------------------------------------------------
# Rumour spatial factor.

def test_rumour_propagates_faster_within_same_location() -> None:
    """Spec test #3."""
    state = SpatialState()
    state.place("peter", "temple")
    state.place("judas", "temple")
    factor = spatial_propagation_factor(state, "peter", "judas")
    assert factor == SAME_LOCATION_BONUS
    assert factor > 1.0


def test_rumour_reaches_distant_location_via_transit_agent() -> None:
    """Spec test #4 — transit carrier enables cross-location diffusion."""
    state = SpatialState()
    state.place("peter", "temple")
    state.place("pilate", "galilee_distant")
    # No carrier yet — factor is zero (full block).
    factor_no_carrier = spatial_propagation_factor(state, "peter", "pilate")
    assert factor_no_carrier == 0.0

    # Now a transit agent from temple toward galilee_distant:
    state.begin_move("messenger", "galilee_distant", cost_substeps=4)
    factor_with_carrier = spatial_propagation_factor(state, "peter", "pilate")
    assert 0.0 < factor_with_carrier < 1.0


def test_pilate_receives_galilee_news_with_delay() -> None:
    """Spec test #6. Proxy for 'delay' = need a transit carrier; without
    one the factor is 0 so the rumour doesn't cross at all."""
    state = SpatialState()
    state.place("pilate", "praetorium")
    state.place("jesus", "galilee_distant")
    # Without carrier.
    f = spatial_propagation_factor(state, "jesus", "pilate")
    assert f == 0.0
    # Once a messenger begins the cross-region journey, Pilate starts
    # receiving at reduced rate (0.3×).
    state.begin_move("john", "praetorium", cost_substeps=4)
    f2 = spatial_propagation_factor(state, "jesus", "pilate")
    assert f2 > 0.0 and f2 < 1.0


def test_custom_params_override_defaults() -> None:
    state = SpatialState()
    state.place("a", "temple")
    state.place("b", "temple")
    params = SpatialRumourParams(same_location_factor=3.0)
    factor = spatial_propagation_factor(state, "a", "b", params=params)
    assert factor == 3.0


# ----------------------------------------------------------------------
# Transit emitter semantics.

def test_transit_agent_can_emit_but_not_receive() -> None:
    state = SpatialState()
    state.place("peter", "temple")
    state.begin_move("judas", "praetorium", cost_substeps=2)
    # judas in transit, peter at temple. peter→judas: judas is transit,
    # per rules transit cannot receive cleanly (only emit).
    factor_to_transit = spatial_propagation_factor(state, "peter", "judas")
    assert factor_to_transit == 0.0
    # judas→peter: transit agent acts as emitter → reduced rate.
    factor_from_transit = spatial_propagation_factor(state, "judas", "peter")
    assert 0.0 < factor_from_transit < 1.0
