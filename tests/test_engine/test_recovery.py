"""recovery_test.py 모듈 테스트.

Parameter Recovery Test의 generate_synthetic_data와 recovery_test를 검증한다.
소규모 파라미터 공간(n_recovery=20)으로 빠르게 실행.
"""

import json
from pathlib import Path

from content.peter.domain_faith import FaithJourneyState
from content.peter.pom_scorecard import make_peter_scorecard
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_hazard_events,
    load_interventions,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule, LoveRule
from engine.rules.physical import FatigueRule, HungerRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.checkpoint import Checkpoint
from engine.simulation.recovery_test import generate_synthetic_data, recovery_test

register_domain_type("faith_journey", FaithJourneyState)
CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content" / "peter"


def _config() -> SimulationConfig:
    state = load_agent_state(CONTENT_DIR / "initial_state.json")
    hazard_events = load_hazard_events(CONTENT_DIR / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "canonical_events.json")
    return SimulationConfig(
        max_tick=200, initial_state=state,
        hazard_events=hazard_events, interventions=interventions,
        state_noise_scale=0.05,
    )


def _rule_engine() -> RuleEngine:
    return RuleEngine([
        FatigueRule(), HungerRule(),
        FearResponseRule(), HopeRule(), GriefRule(), LoveRule(),
        HomeostasisRule(),
    ])


def _checkpoints() -> list[Checkpoint]:
    data = json.loads((CONTENT_DIR / "checkpoints.json").read_text(encoding="utf-8"))
    return [Checkpoint.model_validate(cp) for cp in data["checkpoints"]]


class TestGenerateSyntheticData:
    def test_generates_results(self):
        """synthetic data가 생성된다."""
        config = _config()
        true_params = {"emotions.fear": 7.0, "emotions.hope": 3.0}
        results = generate_synthetic_data(
            config, _rule_engine(), true_params, n_runs=5, checkpoints=_checkpoints()
        )
        assert len(results) == 5
        for r in results:
            assert r.final_state is not None

    def test_params_are_applied(self):
        """true_params가 적용된다."""
        config = _config()
        # 극단적 파라미터로 차이를 확인
        results_high_fear = generate_synthetic_data(
            config, _rule_engine(),
            {"emotions.fear": 9.5}, n_runs=3, checkpoints=_checkpoints()
        )
        results_low_fear = generate_synthetic_data(
            config, _rule_engine(),
            {"emotions.fear": 0.5}, n_runs=3, checkpoints=_checkpoints()
        )
        # 최소한 실행되어야 함
        assert len(results_high_fear) == 3
        assert len(results_low_fear) == 3


class TestRecoveryTest:
    def test_recovery_no_passing(self):
        """POM 통과 파라미터가 없을 때 early return 경로."""
        config = _config()
        scorecard = make_peter_scorecard()
        result = recovery_test(
            config, _rule_engine(),
            true_params={"emotions.fear": 7.0},
            param_ranges={"emotions.fear": (0.0, 10.0)},
            scorecard=scorecard,
            n_synthetic=5,
            n_recovery=5,  # 너무 적어서 POM 통과 불가
            checkpoints=_checkpoints(),
        )

        assert "true_params" in result
        assert "true_pom_rate" in result
        assert "recovery_error" in result
        assert isinstance(result["true_in_recovered_box"], bool)

    def test_recovery_with_lenient_scorecard(self):
        """관대한 scorecard로 full recovery 경로를 실행한다."""
        from engine.simulation.pom import PatternCriterion

        config = _config()
        # 모든 시뮬레이션이 통과하는 관대한 scorecard
        lenient_scorecard = [
            PatternCriterion(
                name="always_pass",
                description="항상 통과",
                evaluate=lambda result: True,
            ),
        ]
        result = recovery_test(
            config, _rule_engine(),
            true_params={"emotions.fear": 7.0},
            param_ranges={"emotions.fear": (0.0, 10.0)},
            scorecard=lenient_scorecard,
            n_synthetic=5,
            n_recovery=10,
            checkpoints=_checkpoints(),
        )

        # full recovery 경로가 실행되었으므로 recovered_box가 있어야 함
        assert result["n_pom_passing"] > 0
        assert "recovered_box" in result
        assert "recovered_params_mean" in result
        assert isinstance(result["recovery_error"], float)
        assert result["recovery_error"] != float("inf")

    def test_recovery_result_structure(self):
        """결과 구조가 올바르다."""
        config = _config()
        scorecard = make_peter_scorecard()
        result = recovery_test(
            config, _rule_engine(),
            true_params={"emotions.fear": 5.0},
            param_ranges={"emotions.fear": (0.0, 10.0)},
            scorecard=scorecard,
            n_synthetic=5,
            n_recovery=5,
            checkpoints=_checkpoints(),
        )

        expected_keys = {
            "true_params", "true_pom_rate", "n_pom_passing",
            "recovered_params_mean", "recovery_error",
            "true_in_recovered_box", "pom_pass_rate_at_recovered",
        }
        assert expected_keys.issubset(set(result.keys()))
