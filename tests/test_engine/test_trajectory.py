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


class TestPrivateHelpers:
    def test_series_stats_empty(self):
        from engine.io.trajectory import _series_stats
        s = _series_stats([])
        assert s == {"mean": 0.0, "max": 0.0, "min": 0.0, "std": 0.0, "auc": 0.0}

    def test_series_stats_values(self):
        from engine.io.trajectory import _series_stats
        s = _series_stats([1.0, 2.0, 3.0])
        assert s["mean"] == 2.0
        assert s["max"] == 3.0
        assert s["min"] == 1.0
        assert s["std"] > 0
        assert s["auc"] == 6.0

    def test_find_event_tick_found(self):
        from engine.io.trajectory import _find_event_tick
        record = {"fired_events": {"arrest": 150}}
        assert _find_event_tick(record, "arrest") == 150

    def test_find_event_tick_missing(self):
        from engine.io.trajectory import _find_event_tick
        record = {"fired_events": {}}
        assert _find_event_tick(record, "arrest") == -1

    def test_state_at_tick_empty_series(self):
        from engine.io.trajectory import _state_at_tick
        assert _state_at_tick([], target_tick=10, field="fear") == 0.0

    def test_state_at_tick_closest(self):
        from engine.io.trajectory import _state_at_tick
        series = [
            {"tick": 5, "fear": 1.0},
            {"tick": 15, "fear": 3.0},
            {"tick": 30, "fear": 7.0},
        ]
        assert _state_at_tick(series, target_tick=14, field="fear") == 3.0
        assert _state_at_tick(series, target_tick=25, field="fear") == 7.0

    def test_multi_dataset_to_feature_matrix_empty(self):
        from engine.io.trajectory import multi_dataset_to_feature_matrix
        matrix, names = multi_dataset_to_feature_matrix([])
        assert matrix == [] and names == []

    def test_multi_result_record_emits_match_rate(self):
        """canonical_match_rates가 있으면 record에 per-agent match_rate 추가."""
        from types import SimpleNamespace

        from engine.io.trajectory import multi_result_to_record
        fake = SimpleNamespace(
            seed=0,
            final_states={},
            action_histories={},
            fired_triggers=[],
            fired_events=[],
            canonical_match_rates={"peter": 0.75, "judas": 0.50},
        )
        rec = multi_result_to_record(fake)
        assert rec["peter_match_rate"] == 0.75
        assert rec["judas_match_rate"] == 0.50
