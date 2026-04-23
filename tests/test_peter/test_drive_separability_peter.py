"""Peter scenario drive-action separability (Iter 65).

Stage 2 PyTorch 학습 feasibility 증거:
    현재 12-feature + FixedProjectionEncoder 조합으로 Peter multi-agent run의
    action class가 drive 공간에서 구별 가능(Fisher-style ratio >= 1.0).

이 수치가 낮으면 Stage 2 학습이 수렴하기 어려운 feature set이라는 경고.
정규 벤치마크 (10 seeds × 300 tick): separability ≈ 1.93.
여기 테스트는 3 seeds × 100 tick 축약판으로 regression guard만 수행.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.latent_drive import FixedProjectionEncoder
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_events,
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
from engine.simulation.drive_training import (
    collect_trajectories,
    trajectories_to_samples,
)
from engine.simulation.training_samples import (
    compute_drive_action_diagnostics,
    drive_class_separability,
)
from engine.simulation.world import SimulationWorld

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


@pytest.fixture(scope="module")
def _setup():
    for t, c in [
        ("faith_journey", FaithJourneyState),
        ("betrayal_psychology", BetrayalPsychologyState),
        ("political_calculation", PoliticalCalculationState),
        ("crowd_dynamics", CrowdDynamicsState),
    ]:
        register_domain_type(t, c)
    return None


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(), HomeostasisRule(),
    ])


def _run_peter(seed: int, max_tick: int = 100):
    peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    cai = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
    events = load_events(CONTENT / "peter" / "canonical_events.json")
    triggers = load_triggers(CONTENT / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT / "peter" / "hazard_events.json")
    profiles = {
        "peter": load_behavior_profile(CONTENT / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT / "caiaphas" / "behavior_profile.json"),
        "crowd": load_behavior_profile(CONTENT / "crowd" / "behavior_profile.json"),
    }
    config = SimulationConfig(
        initial_state=peter,
        initial_states=[peter, judas, cai, crowd],
        max_tick=max_tick, state_noise_scale=0.02,
        events=events, triggers=triggers, hazard_events=hazards,
    )
    return SimulationWorld(config, _rules(), behavior_profiles=profiles).run(seed=seed)


@pytest.fixture(scope="module")
def peter_diagnostics(_setup):
    results = collect_trajectories(_run_peter, n_runs=3)
    samples = trajectories_to_samples(results)
    enc = FixedProjectionEncoder(dim=5, seed=0)
    return compute_drive_action_diagnostics(samples, enc)


class TestPeterDriveSeparability:
    def test_multiple_actions_observed(self, peter_diagnostics):
        """4-agent Peter run이 충분히 다양한 action을 생성."""
        assert len(peter_diagnostics) >= 5

    def test_separability_above_feasibility_threshold(self, peter_diagnostics):
        """Stage 2 학습 feasibility 신호 — 0보다 확실히 큼.

        Full benchmark (10 seeds × 300 tick): ≈ 1.93.
        축약 (3 seeds × 100 tick): >= 0.5 여유 기준.
        """
        sep = drive_class_separability(peter_diagnostics)
        assert sep >= 0.5, (
            f"separability={sep:.3f}, feature set may not support Stage 2 learning"
        )

    def test_action_diagnostics_have_drive_mean_variance(self, peter_diagnostics):
        """Top action의 drive_mean이 0 벡터가 아님 (projection 정상)."""
        top = peter_diagnostics[0]
        assert any(abs(m) > 0.01 for m in top.drive_mean)
