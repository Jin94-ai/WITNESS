"""Spike 4 Phase 4B: BatchInterventionRunner tests."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import (
    ConfusionRule,
    FearResponseRule,
    GriefRule,
    HopeRule,
    LoveRule,
)
from engine.rules.temporal import HomeostasisRule
from world.core.world_config import WorldConfig
from world.intervention.batch import (
    METRIC_NAMES,
    BatchInterventionRunner,
    ExperimentResult,
)
from world.intervention.spec import InterventionSpec

ROOT = Path(__file__).resolve().parent.parent.parent
CONTENT = ROOT / "content"
WORLD_CFG_PATH = CONTENT / "worlds" / "jerusalem_ad30" / "world_config.json"


_domains_registered = False


def _register_domains() -> None:
    global _domains_registered
    if _domains_registered:
        return
    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
    register_domain_type("political_calculation", PoliticalCalculationState)
    register_domain_type("crowd_dynamics", CrowdDynamicsState)
    _domains_registered = True


def _load_world_config() -> WorldConfig:
    payload = json.loads(WORLD_CFG_PATH.read_text(encoding="utf-8"))
    return replace(WorldConfig.from_json(payload), rng_seed=0)


def _make_sim_config(agent_ids: list[str]) -> SimulationConfig:
    states = [
        load_agent_state(CONTENT / aid / "initial_state.json")
        for aid in agent_ids
    ]
    triggers = load_triggers(CONTENT / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT / "peter" / "hazard_events.json")
    return SimulationConfig(
        initial_state=states[0], initial_states=states,
        triggers=triggers, hazard_events=hazards,
        state_noise_scale=0.02, max_tick=12,
        events=[], interventions=[],
    )


def _rule_engine() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(), HomeostasisRule(),
    ])


def _profiles(agent_ids: list[str]):
    return {
        aid: load_behavior_profile(CONTENT / aid / "behavior_profile.json")
        for aid in agent_ids
    }


@pytest.fixture(scope="module")
def domains_registered():
    _register_domains()


# ----------------------------------------------------------------------
# Smoke.

def test_batch_runner_produces_experiment_result(domains_registered) -> None:
    agent_ids = ["peter", "judas", "caiaphas", "crowd"]
    runner = BatchInterventionRunner(
        world_config_base=_load_world_config(),
        sim_config_base=_make_sim_config(agent_ids),
        rule_engine=_rule_engine(),
        behavior_profiles=_profiles(agent_ids),
    )
    spec = InterventionSpec(
        intervention_id="halve_pharisees",
        faction_influence_scale={"pharisees": 0.5},
    )
    result = runner.run_experiment(spec, n_seeds=2, n_days=20)
    assert isinstance(result, ExperimentResult)
    assert result.n_seeds == 2
    assert result.n_days == 20
    assert result.control.label == "control"
    assert result.intervention.label == "intervention"
    assert len(result.control.per_seed) == 2
    assert len(result.intervention.per_seed) == 2


def test_null_intervention_produces_bit_identical_arms(domains_registered) -> None:
    """An empty spec → control and intervention arms must match seed-by-seed."""
    agent_ids = ["peter", "judas", "caiaphas", "crowd"]
    runner = BatchInterventionRunner(
        world_config_base=_load_world_config(),
        sim_config_base=_make_sim_config(agent_ids),
        rule_engine=_rule_engine(),
        behavior_profiles=_profiles(agent_ids),
    )
    null_spec = InterventionSpec(intervention_id="noop")
    result = runner.run_experiment(null_spec, n_seeds=2, n_days=15)

    for cs, ix in zip(result.control.per_seed, result.intervention.per_seed):
        assert cs.seed == ix.seed
        assert cs.metrics == ix.metrics


def test_agent_remove_judas_shrinks_rumours(domains_registered) -> None:
    """Judas removal should kill the rumour pipeline (Phase 3C/3D finding)."""
    agent_ids = ["peter", "judas", "caiaphas", "crowd"]
    runner = BatchInterventionRunner(
        world_config_base=_load_world_config(),
        sim_config_base=_make_sim_config(agent_ids),
        rule_engine=_rule_engine(),
        behavior_profiles=_profiles(agent_ids),
    )
    spec = InterventionSpec(
        intervention_id="remove_judas_via_batch", agent_remove=["judas"],
    )
    result = runner.run_experiment(spec, n_seeds=2, n_days=30)
    ctrl_rumours = result.control.aggregate["rumors_seeded_mean"]
    int_rumours = result.intervention.aggregate["rumors_seeded_mean"]
    assert ctrl_rumours > 0, "control should seed rumours"
    assert int_rumours == 0, "intervention (no Judas) should have 0 rumours"


def test_comparison_has_expected_metric_keys(domains_registered) -> None:
    agent_ids = ["peter", "judas", "caiaphas", "crowd"]
    runner = BatchInterventionRunner(
        world_config_base=_load_world_config(),
        sim_config_base=_make_sim_config(agent_ids),
        rule_engine=_rule_engine(),
        behavior_profiles=_profiles(agent_ids),
    )
    spec = InterventionSpec(
        intervention_id="halve_pharisees",
        faction_influence_scale={"pharisees": 0.5},
    )
    result = runner.run_experiment(spec, n_seeds=2, n_days=20)
    # All metrics with both-arm data must have comparison stats.
    for name in METRIC_NAMES:
        has_ctrl = any(
            s.metrics.get(name) is not None for s in result.control.per_seed
        )
        has_int = any(
            s.metrics.get(name) is not None for s in result.intervention.per_seed
        )
        if has_ctrl and has_int:
            assert name in result.comparison
            entry = result.comparison[name]
            assert set(entry.keys()) == {
                "control_mean", "intervention_mean", "mean_delta",
                "cohens_d", "permutation_p_value",
            }


def test_experiment_result_serialises_to_dict(domains_registered) -> None:
    agent_ids = ["peter", "judas", "caiaphas", "crowd"]
    runner = BatchInterventionRunner(
        world_config_base=_load_world_config(),
        sim_config_base=_make_sim_config(agent_ids),
        rule_engine=_rule_engine(),
        behavior_profiles=_profiles(agent_ids),
    )
    spec = InterventionSpec(intervention_id="x", agent_remove=["judas"])
    result = runner.run_experiment(spec, n_seeds=2, n_days=15)
    d = result.as_dict()
    assert d["intervention_id"] == "x"
    assert d["n_seeds"] == 2
    assert "control" in d and "intervention" in d
    # round-trip through JSON to ensure serialisability.
    s = json.dumps(d)
    assert '"intervention_id": "x"' in s
