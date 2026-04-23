"""Spike 4 Phase 4A: InterventionSpec + InterventionEngine unit tests."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from engine.core.state import AgentState
from engine.core.world import SimulationConfig
from world.core.world_config import WorldConfig
from world.intervention.engine import InterventionEngine
from world.intervention.spec import InterventionSpec

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT / "content" / "worlds" / "jerusalem_ad30" / "world_config.json"


def _load_world_config() -> WorldConfig:
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return replace(WorldConfig.from_json(payload), rng_seed=0)


def _make_base_config() -> SimulationConfig:
    peter = AgentState(agent_id="peter")
    judas = AgentState(agent_id="judas")
    caiaphas = AgentState(agent_id="caiaphas")
    crowd = AgentState(agent_id="crowd")
    return SimulationConfig(
        initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        max_tick=12,
    )


# ---------------------------------------------------------------------
# InterventionSpec.

def test_spec_is_null_for_empty_spec() -> None:
    spec = InterventionSpec(intervention_id="null_spec")
    assert spec.is_null() is True


def test_spec_not_null_with_any_primitive() -> None:
    spec = InterventionSpec(intervention_id="x", agent_remove=["judas"])
    assert spec.is_null() is False


def test_spec_from_json_preserves_known_fields() -> None:
    payload = {
        "intervention_id": "i1", "description": "test",
        "hazard_rate_scale": 0.5,
        "faction_remove": ["zealots"],
    }
    spec = InterventionSpec.from_json(payload)
    assert spec.intervention_id == "i1"
    assert spec.hazard_rate_scale == 0.5
    assert spec.faction_remove == ["zealots"]


def test_spec_from_json_forward_compat_unknown_fields() -> None:
    payload = {"intervention_id": "x", "novel_field": "future"}
    spec = InterventionSpec.from_json(payload)
    assert spec.extras["novel_field"] == "future"


def test_spec_load_from_disk(tmp_path: Path) -> None:
    path = tmp_path / "spec.json"
    path.write_text(json.dumps({
        "intervention_id": "disk_test",
        "hazard_rate_scale": 0.25,
    }), encoding="utf-8")
    spec = InterventionSpec.load(path)
    assert spec.hazard_rate_scale == 0.25


# ---------------------------------------------------------------------
# InterventionEngine — null identity.

def test_null_intervention_returns_deep_copies_no_changes() -> None:
    spec = InterventionSpec(intervention_id="null_ctrl")
    world = _load_world_config()
    base = _make_base_config()
    eng = InterventionEngine()
    new_world, new_base, report = eng.apply(spec, world, base)

    # Deep copy — different object identity.
    assert new_world is not world
    assert new_world.factions_config is not world.factions_config
    # Structurally identical.
    assert new_world.world_id == world.world_id
    assert new_world.factions_config == world.factions_config
    assert [s.agent_id for s in new_base.initial_states] == [
        s.agent_id for s in base.initial_states
    ]
    # Report marks the null path.
    assert "null_control" in report.primitives_applied


# ---------------------------------------------------------------------
# InterventionEngine — faction_remove.

def test_faction_remove_drops_the_faction() -> None:
    spec = InterventionSpec(
        intervention_id="remove_zealots", faction_remove=["zealots"],
    )
    world = _load_world_config()
    base = _make_base_config()
    eng = InterventionEngine()
    new_world, _, report = eng.apply(spec, world, base)

    assert "zealots" not in new_world.factions_config["factions"]
    assert "pharisees" in new_world.factions_config["factions"]
    # Original untouched.
    assert "zealots" in world.factions_config["factions"]
    assert "faction_remove" in report.primitives_applied


def test_faction_remove_unknown_id_warns() -> None:
    spec = InterventionSpec(
        intervention_id="remove_ghost", faction_remove=["ghost_sect"],
    )
    world = _load_world_config()
    base = _make_base_config()
    eng = InterventionEngine()
    _, _, report = eng.apply(spec, world, base)
    assert report.warnings  # we said ghost_sect but nothing removed
    assert "faction_remove" not in report.primitives_applied


# ---------------------------------------------------------------------
# InterventionEngine — faction_influence_scale.

def test_faction_influence_scale_halves_pharisees() -> None:
    spec = InterventionSpec(
        intervention_id="halve_pharisees",
        faction_influence_scale={"pharisees": 0.5},
    )
    world = _load_world_config()
    base = _make_base_config()
    orig_init = world.factions_config["factions"]["pharisees"]["initial_influence"]
    orig_target = world.factions_config["factions"]["pharisees"]["target_influence"]
    eng = InterventionEngine()
    new_world, _, _ = eng.apply(spec, world, base)
    nf = new_world.factions_config["factions"]["pharisees"]
    assert nf["initial_influence"] == pytest.approx(orig_init * 0.5)
    assert nf["target_influence"] == pytest.approx(orig_target * 0.5)
    # Original unchanged.
    assert (
        world.factions_config["factions"]["pharisees"]["initial_influence"]
        == orig_init
    )


# ---------------------------------------------------------------------
# InterventionEngine — agent_remove.

def test_agent_remove_drops_judas() -> None:
    spec = InterventionSpec(
        intervention_id="no_judas", agent_remove=["judas"],
    )
    world = _load_world_config()
    base = _make_base_config()
    eng = InterventionEngine()
    _, new_base, report = eng.apply(spec, world, base)
    ids = [s.agent_id for s in new_base.initial_states]
    assert "judas" not in ids
    assert set(ids) == {"peter", "caiaphas", "crowd"}
    assert "agent_remove" in report.primitives_applied


def test_agent_remove_unknown_id_warns_but_doesnt_crash() -> None:
    spec = InterventionSpec(
        intervention_id="no_nobody", agent_remove=["ghost_agent"],
    )
    world = _load_world_config()
    base = _make_base_config()
    eng = InterventionEngine()
    _, new_base, report = eng.apply(spec, world, base)
    # No agents dropped — same 4 agents still present.
    assert len(new_base.initial_states) == 4
    assert any("matched no agents" in w for w in report.warnings)


# ---------------------------------------------------------------------
# InterventionEngine — politics overrides.

def test_politics_overrides_apply_cleanly() -> None:
    spec = InterventionSpec(
        intervention_id="lenient_pilate",
        pilate_bonus_override=0.0,
        pilate_approach_lead_days_override=0,
        crowd_trigger_threshold_override=8.0,
    )
    world = _load_world_config()
    base = _make_base_config()
    eng = InterventionEngine()
    new_world, _, report = eng.apply(spec, world, base)

    assert new_world.politics_config["pilate_bonus"] == 0.0
    assert new_world.politics_config["pilate_approach_lead_days"] == 0
    assert new_world.politics_config["crowd_trigger_threshold"] == 8.0
    for p in ("pilate_bonus_override",
              "pilate_approach_lead_days_override",
              "crowd_trigger_threshold_override"):
        assert p in report.primitives_applied


# ---------------------------------------------------------------------
# InterventionEngine — hazard rate scaling.

def test_hazard_rate_scale_halves_base_rates() -> None:
    from engine.core.hazard import HazardEvent, HazardFunction
    from engine.core.state import AgentState
    from engine.core.world import SimulationConfig

    hazard = HazardEvent(
        event_id="test_hazard",
        hazard=HazardFunction(base_rate=0.4),
    )
    base = SimulationConfig(
        initial_state=AgentState(agent_id="x"),
        max_tick=10,
        hazard_events=[hazard],
    )
    spec = InterventionSpec(
        intervention_id="half_hazard", hazard_rate_scale=0.5,
    )
    world = _load_world_config()
    eng = InterventionEngine()
    _, new_base, report = eng.apply(spec, world, base)
    assert new_base.hazard_events[0].hazard.base_rate == pytest.approx(0.2)
    # Original unchanged.
    assert base.hazard_events[0].hazard.base_rate == pytest.approx(0.4)
    assert "hazard_rate_scale" in report.primitives_applied


# ---------------------------------------------------------------------
# InterventionEngine — multi-primitive composition.

def test_multiple_primitives_applied_in_one_spec() -> None:
    spec = InterventionSpec(
        intervention_id="compound",
        agent_remove=["judas"],
        faction_influence_scale={"jesus_movement": 0.25},
        hazard_rate_scale=0.8,
    )
    world = _load_world_config()
    base = _make_base_config()
    eng = InterventionEngine()
    _, new_base, report = eng.apply(spec, world, base)
    assert "agent_remove" in report.primitives_applied
    assert "faction_influence_scale" in report.primitives_applied
    # (no hazards in base; scale still runs without error)
    assert len(new_base.initial_states) == 3
