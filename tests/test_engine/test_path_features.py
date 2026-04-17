"""Path feature 추출 테스트 (trajectory.py dataset_to_path_features)."""

import json
import random
from pathlib import Path

from content.peter.domain_faith import FaithJourneyState
from engine.core.world import SimulationConfig
from engine.io.loader import load_agent_state, load_hazard_events, load_interventions, register_domain_type
from engine.io.trajectory import dataset_to_path_features, result_to_record
from engine.rules.base import RuleEngine
from engine.rules.emotional import ConfusionRule, FearResponseRule, GriefRule, HopeRule, LoveRule
from engine.rules.physical import FatigueRule, HealthRule, HungerRule
from engine.rules.social import GroupIsolationRule, RelationshipDecayRule
from engine.rules.temporal import CircadianRule, HighStressConsequenceRule, HomeostasisRule, SlowStateRule
from engine.simulation.runner import SimulationRunner

register_domain_type("faith_journey", FaithJourneyState)
CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content" / "peter"


def _engine() -> RuleEngine:
    return RuleEngine([
        FatigueRule(), HungerRule(), HealthRule(),
        FearResponseRule(), HopeRule(), GriefRule(), ConfusionRule(), LoveRule(),
        RelationshipDecayRule(), GroupIsolationRule(),
        HomeostasisRule(), SlowStateRule(), HighStressConsequenceRule(), CircadianRule(),
    ])


def _run_batch(n: int = 10) -> list[dict]:
    state = load_agent_state(CONTENT_DIR / "initial_state.json")
    hazard_events = load_hazard_events(CONTENT_DIR / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "canonical_events.json")
    engine = _engine()
    rng = random.Random(42)
    records = []
    for i in range(n):
        overrides = {"emotions.fear": rng.uniform(0, 10), "emotions.love": rng.uniform(0, 10)}
        config = SimulationConfig(
            max_tick=500, initial_state=state, hazard_events=hazard_events,
            interventions=interventions, state_noise_scale=0.05, parameter_overrides=overrides,
        )
        r = SimulationRunner(config, engine).run_single(seed=i)
        records.append(result_to_record(r, overrides))
    return records


class TestPathFeatures:
    def test_basic_extraction(self):
        """path feature가 추출된다."""
        records = _run_batch(10)
        matrix, names = dataset_to_path_features(records)
        assert len(matrix) == 10
        assert len(names) > 10  # 다수의 feature
        assert all(len(row) == len(names) for row in matrix)

    def test_features_are_numeric(self):
        """모든 feature 값이 숫자다."""
        records = _run_batch(5)
        matrix, _ = dataset_to_path_features(records)
        for row in matrix:
            for val in row:
                assert isinstance(val, (int, float))

    def test_pivot_event_customizable(self):
        """pivot_event를 바꿀 수 있다."""
        records = _run_batch(5)
        matrix1, names1 = dataset_to_path_features(records, pivot_event="arrest")
        matrix2, names2 = dataset_to_path_features(records, pivot_event="gethsemane")
        # feature 이름이 다름
        assert any("arrest" in n for n in names1)
        assert any("gethsemane" in n for n in names2)

    def test_slow_state_in_features(self):
        """slow_state feature가 포함된다."""
        records = _run_batch(5)
        _, names = dataset_to_path_features(records)
        assert any("slow_" in n for n in names)

    def test_action_counts_dynamic(self):
        """행동 카운트가 데이터에서 자동 탐지된다."""
        records = _run_batch(10)
        _, names = dataset_to_path_features(records)
        # 적어도 하나의 action_count feature
        assert any("action_" in n for n in names)
