"""Tests for engine/world/spatial/ (Phase 3)."""

from __future__ import annotations

import re
from pathlib import Path

from engine.world.spatial import Location, SpatialRegistry


def _sample_locations() -> list[Location]:
    return [
        Location(
            location_id="public_square",
            name="Public Square",
            tags=["public", "outdoor"],
            visibility=0.9, concealment=0.1,
            crowdability=0.9, authority_reach=0.5,
            escape_routes=["street", "market"],
        ),
        Location(
            location_id="private_dwelling",
            name="Private Dwelling",
            tags=["private", "indoor"],
            visibility=0.2, concealment=0.8,
            crowdability=0.2, authority_reach=0.1,
            escape_routes=["street"],
        ),
        Location(
            location_id="authority_court",
            name="Authority Court",
            tags=["authority", "public"],
            visibility=0.9, concealment=0.0,
            crowdability=0.5, authority_reach=0.95,
            escape_routes=[],
        ),
        Location(
            location_id="street",
            name="Street",
            tags=["public", "outdoor"],
            visibility=0.6, concealment=0.3,
            crowdability=0.7, authority_reach=0.4,
            escape_routes=["public_square", "private_dwelling", "market"],
        ),
        Location(
            location_id="market",
            name="Market",
            tags=["public", "commercial"],
            visibility=0.8, concealment=0.2,
            crowdability=0.9, authority_reach=0.4,
            escape_routes=["public_square", "street"],
        ),
        Location(
            location_id="shore",
            name="Shore",
            tags=["outdoor", "water"],
            visibility=0.5, concealment=0.2,
            crowdability=0.3, authority_reach=0.1,
            escape_routes=["street"],
        ),
    ]


# -----------------------------------------------------------------
# Basic CRUD
# -----------------------------------------------------------------

def test_registry_empty() -> None:
    r = SpatialRegistry()
    assert r.count() == 0


def test_add_and_get_location() -> None:
    r = SpatialRegistry(_sample_locations())
    assert r.count() == 6
    loc = r.get("public_square")
    assert loc.visibility == 0.9


def test_get_unknown_raises() -> None:
    r = SpatialRegistry(_sample_locations())
    import pytest
    with pytest.raises(KeyError):
        r.get("atlantis")


# -----------------------------------------------------------------
# Agent placement
# -----------------------------------------------------------------

def test_place_agent() -> None:
    r = SpatialRegistry(_sample_locations())
    r.place("agent_01", "public_square")
    assert r.where("agent_01") == "public_square"
    assert "agent_01" in r.agents_at("public_square")


def test_place_replaces_prior() -> None:
    r = SpatialRegistry(_sample_locations())
    r.place("agent_01", "public_square")
    r.place("agent_01", "market")
    assert r.where("agent_01") == "market"
    assert "agent_01" not in r.agents_at("public_square")
    assert "agent_01" in r.agents_at("market")


# -----------------------------------------------------------------
# Movement
# -----------------------------------------------------------------

def test_move_between_adjacent_ok() -> None:
    r = SpatialRegistry(_sample_locations())
    r.place("agent_01", "public_square")
    assert r.move("agent_01", "street") is True
    assert r.where("agent_01") == "street"


def test_move_to_non_adjacent_fails() -> None:
    r = SpatialRegistry(_sample_locations())
    r.place("agent_01", "public_square")
    # public_square escape_routes = [street, market]; shore not in there
    assert r.move("agent_01", "shore") is False
    assert r.where("agent_01") == "public_square"


def test_move_noop_same_location() -> None:
    r = SpatialRegistry(_sample_locations())
    r.place("agent_01", "street")
    assert r.move("agent_01", "street") is True


def test_unplaced_move_places_directly() -> None:
    r = SpatialRegistry(_sample_locations())
    assert r.move("agent_01", "shore") is True
    assert r.where("agent_01") == "shore"


# -----------------------------------------------------------------
# Affordance checks
# -----------------------------------------------------------------

def test_flee_requires_escape_route() -> None:
    r = SpatialRegistry(_sample_locations())
    # Place in location with escape routes
    r.place("agent_01", "public_square")
    ok, _ = r.is_action_affordable("agent_01", "flee")
    assert ok

    # Place in authority_court (no escape routes)
    r.place("agent_02", "authority_court")
    ok, reason = r.is_action_affordable("agent_02", "flee")
    assert not ok
    assert "escape" in reason


def test_hide_requires_concealment() -> None:
    r = SpatialRegistry(_sample_locations())
    # private_dwelling has concealment 0.8
    r.place("agent_01", "private_dwelling")
    ok, _ = r.is_action_affordable("agent_01", "stay_hiding")
    assert ok

    # public_square has concealment 0.1
    r.place("agent_02", "public_square")
    ok, reason = r.is_action_affordable("agent_02", "stay_hiding")
    assert not ok
    assert "concealment" in reason


def test_draw_sword_blocked_in_authority() -> None:
    r = SpatialRegistry(_sample_locations())
    r.place("agent_01", "authority_court")  # authority_reach=0.95
    ok, reason = r.is_action_affordable("agent_01", "draw_sword")
    assert not ok
    assert "authority" in reason


def test_draw_sword_ok_in_private() -> None:
    r = SpatialRegistry(_sample_locations())
    r.place("agent_01", "private_dwelling")  # authority_reach=0.1
    ok, _ = r.is_action_affordable("agent_01", "draw_sword")
    assert ok


def test_jump_into_sea_requires_water() -> None:
    r = SpatialRegistry(_sample_locations())
    r.place("agent_01", "shore")  # has water tag
    ok, _ = r.is_action_affordable("agent_01", "jump_into_sea")
    assert ok

    r.place("agent_02", "market")  # no water tag
    ok, reason = r.is_action_affordable("agent_02", "jump_into_sea")
    assert not ok
    assert "water" in reason


def test_unlisted_action_allowed() -> None:
    """Actions not in affordance table default to allowed."""
    r = SpatialRegistry(_sample_locations())
    r.place("agent_01", "authority_court")
    ok, _ = r.is_action_affordable("agent_01", "pray")
    assert ok


# -----------------------------------------------------------------
# Tags + reachability
# -----------------------------------------------------------------

def test_location_has_tag() -> None:
    r = SpatialRegistry(_sample_locations())
    shore = r.get("shore")
    assert shore.has_tag("water")
    assert not shore.has_tag("indoor")


def test_role_reachability_default_full() -> None:
    loc = Location(location_id="x")
    # No reachability specified → default 1.0 for any role
    assert loc.is_reachable_by_role("outsider") == 1.0
    assert loc.is_reachable_by_role("priest") == 1.0


def test_role_reachability_explicit() -> None:
    loc = Location(
        location_id="restricted",
        reachability={"priest": 1.0, "outsider": 0.1},
    )
    assert loc.is_reachable_by_role("priest") == 1.0
    assert loc.is_reachable_by_role("outsider") == 0.1


# -----------------------------------------------------------------
# Affordance summary
# -----------------------------------------------------------------

def test_affordance_summary() -> None:
    r = SpatialRegistry(_sample_locations())
    summary = r.get("public_square").affordance_summary()
    assert "visibility" in summary
    assert summary["escape_routes_count"] == 2.0


# -----------------------------------------------------------------
# Rule #1
# -----------------------------------------------------------------

def test_spatial_module_no_person_hardcoding() -> None:
    banned = ["peter", "jesus", "judas", "caiaphas", "pilate"]
    root = Path(__file__).resolve().parents[2]
    for py in (root / "engine" / "world" / "spatial").glob("*.py"):
        src = py.read_text(encoding="utf-8").lower()
        for b in banned:
            if re.search(rf"\b{b}\b", src):
                raise AssertionError(f"{py.name} contains '{b}' -- Rule #1")
