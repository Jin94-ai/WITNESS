"""Targeted coverage for ``InterventionEngine`` primitives that the main
regression suite does not exercise.

Rule #10 guard: these tests construct ``InterventionSpec`` directly in
memory. No new intervention JSON files are added to ``content/``; the
three existing (``remove_judas``, ``hazard_half``, ``lenient_pilate``)
remain the only persisted interventions.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

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
    return SimulationConfig(
        initial_state=peter, initial_states=[peter, judas], max_tick=12,
    )


# ---------------------------------------------------------------------
# faction_add (lines 97-102).

def test_faction_add_injects_new_faction() -> None:
    spec = InterventionSpec(
        intervention_id="add_samaritan_bloc",
        faction_add={
            "samaritans": {
                "initial_influence": 0.2, "target_influence": 0.3,
                "growth_rate": 0.05, "initial_militancy": 0.1,
                "roman_stance": "neutral",
            },
        },
    )
    eng = InterventionEngine()
    new_world, _, report = eng.apply(spec, _load_world_config(), _make_base_config())

    factions = new_world.factions_config["factions"]
    assert "samaritans" in factions
    assert factions["samaritans"]["initial_influence"] == 0.2
    assert "faction_add" in report.primitives_applied


# ---------------------------------------------------------------------
# rumor_spread_rate_scale (lines 118-122).

def test_rumor_spread_rate_scale_multiplies_current() -> None:
    world = _load_world_config()
    baseline = float(world.rumors_config.get("spread_rate_per_day", 0.05))
    spec = InterventionSpec(
        intervention_id="rumor_fast", rumor_spread_rate_scale=2.0,
    )
    eng = InterventionEngine()
    new_world, _, report = eng.apply(spec, world, _make_base_config())

    assert new_world.rumors_config["spread_rate_per_day"] == baseline * 2.0
    assert "rumor_spread_rate_scale" in report.primitives_applied
    # Original untouched.
    assert world.rumors_config["spread_rate_per_day"] == baseline


# ---------------------------------------------------------------------
# rumor_credibility_decay_scale (lines 124-130).

def test_rumor_credibility_decay_scale_multiplies_current() -> None:
    world = _load_world_config()
    baseline = float(world.rumors_config.get("credibility_decay_per_day", 0.02))
    spec = InterventionSpec(
        intervention_id="rumor_sticky", rumor_credibility_decay_scale=0.5,
    )
    eng = InterventionEngine()
    new_world, _, report = eng.apply(spec, world, _make_base_config())

    assert new_world.rumors_config["credibility_decay_per_day"] == baseline * 0.5
    assert "rumor_credibility_decay_scale" in report.primitives_applied


# ---------------------------------------------------------------------
# passover_amplitude_scale (lines 151-155).

def test_passover_amplitude_scale_multiplies_current() -> None:
    world = _load_world_config()
    baseline = float(world.calendar_config.get("passover_amplitude", 10.0))
    spec = InterventionSpec(
        intervention_id="muted_passover", passover_amplitude_scale=0.3,
    )
    eng = InterventionEngine()
    new_world, _, report = eng.apply(spec, world, _make_base_config())

    assert new_world.calendar_config["passover_amplitude"] == baseline * 0.3
    assert "passover_amplitude_scale" in report.primitives_applied


# ---------------------------------------------------------------------
# apply_to_world_only + _stub_base_config (lines 178-191).

def test_apply_to_world_only_short_circuits_with_stub_base() -> None:
    """World-only interventions don't require passing a SimulationConfig."""
    spec = InterventionSpec(
        intervention_id="world_only_rumor", rumor_spread_rate_scale=1.5,
    )
    eng = InterventionEngine()
    world_before = _load_world_config()
    baseline = float(world_before.rumors_config["spread_rate_per_day"])

    new_world, report = eng.apply_to_world_only(spec, world_before)

    assert new_world.rumors_config["spread_rate_per_day"] == baseline * 1.5
    assert "rumor_spread_rate_scale" in report.primitives_applied


def test_apply_to_world_only_handles_null_spec() -> None:
    """Null spec goes through the stub path too and marks null_control."""
    eng = InterventionEngine()
    _, report = eng.apply_to_world_only(
        InterventionSpec(intervention_id="world_only_null"),
        _load_world_config(),
    )
    assert "null_control" in report.primitives_applied
