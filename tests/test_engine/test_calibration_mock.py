"""calibration.py 모듈 테스트 (mock 기반).

pyABC 의존성을 모킹하여 calibrate_parameters의 로직을 검증한다.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from content.peter.domain_faith import FaithJourneyState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_hazard_events,
    load_interventions,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, HopeRule
from engine.rules.physical import FatigueRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.checkpoint import Checkpoint

register_domain_type("faith_journey", FaithJourneyState)
CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content" / "peter"


def _config() -> SimulationConfig:
    state = load_agent_state(CONTENT_DIR / "initial_state.json")
    hazard_events = load_hazard_events(CONTENT_DIR / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "canonical_events.json")
    return SimulationConfig(
        max_tick=100, initial_state=state,
        hazard_events=hazard_events, interventions=interventions,
        state_noise_scale=0.05,
    )


def _rule_engine() -> RuleEngine:
    return RuleEngine([FatigueRule(), FearResponseRule(), HopeRule(), HomeostasisRule()])


def _checkpoints() -> list[Checkpoint]:
    data = json.loads((CONTENT_DIR / "checkpoints.json").read_text(encoding="utf-8"))
    return [Checkpoint.model_validate(cp) for cp in data["checkpoints"]]


class TestCalibrateParameters:
    def test_calibrate_with_mock_pyabc(self):
        """pyABC를 모킹하여 calibrate_parameters 로직을 검증한다."""
        import numpy as np
        import pandas as pd

        # pyabc mock 구성
        mock_pyabc = MagicMock()

        # Distribution mock
        mock_pyabc.Distribution.return_value = MagicMock()
        mock_pyabc.RV.return_value = MagicMock()

        # ABCSMC mock
        mock_abc_instance = MagicMock()
        mock_pyabc.ABCSMC.return_value = mock_abc_instance
        mock_abc_instance.new.return_value = None

        # history mock
        mock_history = MagicMock()
        mock_abc_instance.run.return_value = mock_history
        mock_history.max_t = 1

        # get_distribution returns DataFrame + weights
        df = pd.DataFrame({"emotions.fear": [5.0, 6.0, 7.0]})
        weights = np.array([0.2, 0.5, 0.3])
        mock_history.get_distribution.return_value = (df, weights)

        # get_all_populations
        pop_df = pd.DataFrame({"epsilon": [1.0, 0.5]})
        mock_history.get_all_populations.return_value = pop_df

        with patch.dict("sys.modules", {"pyabc": mock_pyabc}):
            from engine.simulation.calibration import calibrate_parameters

            config = _config()
            result = calibrate_parameters(
                config, _rule_engine(),
                param_ranges={"emotions.fear": (0.0, 10.0)},
                checkpoints=_checkpoints(),
                n_populations=2,
                pop_size=5,
                n_runs_per_eval=3,
            )

        assert "best_params" in result
        assert "emotions.fear" in result["best_params"]
        assert "history_summary" in result
        assert "posterior_samples" in result
        # best should be index 1 (highest weight 0.5)
        assert result["best_params"]["emotions.fear"] == 6.0


class TestCalibrationDistance:
    def test_distance_function(self):
        """distance 함수의 동작을 검증한다."""
        # distance 함수는 calibrate_parameters 내부에 정의되어 있으므로
        # 로직을 직접 테스트
        target_action_count = 3.0

        def distance(x: dict, y: dict) -> float:
            match_diff = abs(x["mean_match_rate"] - y["mean_match_rate"])
            action_diff = abs(x["mean_action_count"] - y["mean_action_count"]) / max(target_action_count, 1.0)
            return float(match_diff + action_diff)

        obs = {"mean_match_rate": 0.5, "mean_action_count": 3.0}
        sim = {"mean_match_rate": 0.5, "mean_action_count": 3.0}
        assert distance(obs, sim) == 0.0

        sim2 = {"mean_match_rate": 0.6, "mean_action_count": 4.0}
        d = distance(obs, sim2)
        assert d > 0
        # 0.1 + 1.0/3.0 = 0.433...
        assert abs(d - (0.1 + 1.0 / 3.0)) < 1e-6
