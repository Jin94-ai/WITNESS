"""analysis.py 커버리지 보완 테스트.

sobol_sensitivity, detect_bifurcation(action_count) 경로를 커버한다.
"""

import json
from pathlib import Path

import pytest

from content.peter.domain_faith import FaithJourneyState
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
from engine.simulation.analysis import detect_bifurcation, sobol_sensitivity
from engine.simulation.checkpoint import Checkpoint

register_domain_type("faith_journey", FaithJourneyState)
CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content" / "peter"


def _rule_engine() -> RuleEngine:
    return RuleEngine([
        FatigueRule(), HungerRule(),
        FearResponseRule(), HopeRule(), GriefRule(), LoveRule(),
        HomeostasisRule(),
    ])


def _config() -> SimulationConfig:
    state = load_agent_state(CONTENT_DIR / "initial_state.json")
    hazard_events = load_hazard_events(CONTENT_DIR / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "canonical_events.json")
    return SimulationConfig(
        max_tick=200, initial_state=state,
        hazard_events=hazard_events, interventions=interventions,
        state_noise_scale=0.05,
    )


def _checkpoints() -> list[Checkpoint]:
    data = json.loads((CONTENT_DIR / "checkpoints.json").read_text(encoding="utf-8"))
    return [Checkpoint.model_validate(cp) for cp in data["checkpoints"]]


@pytest.mark.slow
class TestSobolSensitivity:
    def test_sobol_runs(self):
        """Sobol 전역 민감도 분석이 실행된다."""
        config = _config()
        result = sobol_sensitivity(
            config, _rule_engine(),
            param_ranges={
                "emotions.fear": (0.0, 10.0),
                "emotions.hope": (0.0, 10.0),
            },
            n_samples=8,
            checkpoints=_checkpoints(),
            outcome_action="deny",
        )

        assert "S1" in result
        assert "ST" in result
        assert len(result["S1"]) == 2
        assert "emotions.fear" in result["S1"]
        assert "emotions.hope" in result["S1"]
        assert "param_names" in result
        assert result["param_names"] == ["emotions.fear", "emotions.hope"]

    def test_sobol_values_are_float(self):
        """Sobol 결과값이 float이다."""
        config = _config()
        result = sobol_sensitivity(
            config, _rule_engine(),
            param_ranges={"emotions.fear": (0.0, 10.0)},
            n_samples=8,
            checkpoints=_checkpoints(),
        )

        for name in result["S1"]:
            assert isinstance(result["S1"][name], float)
            assert isinstance(result["ST"][name], float)


@pytest.mark.slow
class TestBifurcationActionCount:
    def test_action_count_outcome(self):
        """detect_bifurcation에서 action_count: outcome_fn 경로."""
        config = _config()
        result = detect_bifurcation(
            config, _rule_engine(),
            param_path="emotions.fear",
            values=[2.0, 5.0, 8.0],
            outcome_fn="action_count:deny",
            n_runs_per_value=5,
            checkpoints=_checkpoints(),
        )

        assert len(result["means"]) == 3
        assert len(result["stds"]) == 3
        assert "bifurcation_candidates" in result

    def test_unknown_outcome_fn_fallback(self):
        """알 수 없는 outcome_fn은 canonical_match_rate로 폴백."""
        config = _config()
        result = detect_bifurcation(
            config, _rule_engine(),
            param_path="emotions.fear",
            values=[3.0, 7.0],
            outcome_fn="unknown_metric",
            n_runs_per_value=3,
            checkpoints=_checkpoints(),
        )

        assert len(result["means"]) == 2
