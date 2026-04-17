"""Trajectory 데이터셋 저장/로드 테스트."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from engine.core.event import ActionOption, ExternalEvent, StateEffect, WeightFormula
from engine.core.state import AgentState, EmotionalState
from engine.core.world import SimulationConfig
from engine.io.trajectory import (
    dataset_to_feature_matrix,
    load_trajectory_dataset,
    result_to_record,
    save_trajectory_dataset,
)
from engine.rules.base import RuleEngine
from engine.rules.temporal import HomeostasisRule
from engine.simulation.runner import SimulationRunner


def _simple_result() -> "SimulationRunner":
    config = SimulationConfig(
        seed=42, max_tick=20,
        initial_state=AgentState(agent_id="test", emotions=EmotionalState(fear=5.0)),
        events=[ExternalEvent(
            event_id="e1", tick=10,
            effects=[StateEffect(field_path="emotions.fear", operation="add", value=2.0)],
            action_options=[
                ActionOption(action_id="act_a", weight_formula=WeightFormula(base_weight=0.5)),
                ActionOption(action_id="act_b", weight_formula=WeightFormula(base_weight=0.5)),
            ],
        )],
    )
    runner = SimulationRunner(config, RuleEngine([HomeostasisRule()]))
    return runner.run_single(seed=42)


class TestResultToRecord:
    def test_basic(self):
        result = _simple_result()
        record = result_to_record(result, {"emotions.fear": 5.0})
        assert record["seed"] == 42
        assert "canonical_match_rate" in record
        assert "event_sequence" in record
        assert "state_series" in record
        assert "final_state" in record
        assert record["params"] == {"emotions.fear": 5.0}

    def test_serializable(self):
        result = _simple_result()
        record = result_to_record(result)
        json_str = json.dumps(record, ensure_ascii=False)
        restored = json.loads(json_str)
        assert restored["seed"] == 42


class TestSaveLoad:
    def test_roundtrip(self):
        result = _simple_result()
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.jsonl"
            save_trajectory_dataset([result, result], path)
            loaded = load_trajectory_dataset(path)
            assert len(loaded) == 2
            assert loaded[0]["seed"] == 42


class TestFeatureMatrix:
    def test_conversion(self):
        result = _simple_result()
        records = [result_to_record(result) for _ in range(5)]
        matrix, names = dataset_to_feature_matrix(records)
        assert len(matrix) == 5
        assert len(names) == 10
        assert "canonical_match_rate" in names
        assert "final_fear" in names
