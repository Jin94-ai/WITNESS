"""분석 파이프라인 테스트: 클러스터링, 분기점 탐지."""

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
from engine.io.trajectory import dataset_to_feature_matrix, result_to_record
from engine.rules.base import RuleEngine
from engine.rules.emotional import ConfusionRule, FearResponseRule, GriefRule, HopeRule, LoveRule
from engine.rules.physical import FatigueRule, HealthRule, HungerRule
from engine.rules.social import GroupIsolationRule, RelationshipDecayRule
from engine.rules.temporal import CircadianRule, HomeostasisRule
from engine.simulation.analysis import (
    cluster_trajectories,
    detect_bifurcation,
    morris_sensitivity,
)
from engine.simulation.batch import run_batch
from engine.simulation.checkpoint import Checkpoint

register_domain_type("faith_journey", FaithJourneyState)
CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content" / "peter"


def _rule_engine() -> RuleEngine:
    return RuleEngine([
        FatigueRule(), HungerRule(), HealthRule(),
        FearResponseRule(), HopeRule(), GriefRule(), ConfusionRule(), LoveRule(),
        RelationshipDecayRule(), GroupIsolationRule(),
        HomeostasisRule(), CircadianRule(),
    ])


def _hazard_config() -> SimulationConfig:
    state = load_agent_state(CONTENT_DIR / "initial_state.json")
    hazard_events = load_hazard_events(CONTENT_DIR / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "canonical_events.json")
    return SimulationConfig(
        max_tick=500, initial_state=state,
        hazard_events=hazard_events, interventions=interventions,
        state_noise_scale=0.05,
    )


def _checkpoints() -> list[Checkpoint]:
    data = json.loads((CONTENT_DIR / "checkpoints.json").read_text(encoding="utf-8"))
    return [Checkpoint.model_validate(cp) for cp in data["checkpoints"]]


@pytest.mark.slow
class TestClusterTrajectories:
    def test_clustering_runs(self):
        """50회 결과를 클러스터링할 수 있다."""
        config = _hazard_config()
        results = run_batch(config, _rule_engine(), 50, _checkpoints())
        records = [result_to_record(r) for r in results]
        matrix, names = dataset_to_feature_matrix(records)

        cluster_result = cluster_trajectories(matrix, min_cluster_size=3)

        print("\n=== Clustering (50 runs) ===")
        print(f"N clusters: {cluster_result['n_clusters']}")
        print(f"Noise ratio: {cluster_result['noise_ratio']:.1%}")

        assert "labels" in cluster_result
        assert len(cluster_result["labels"]) == 50
        assert "embedding_2d" in cluster_result


class TestMorrisSensitivity:
    def test_morris_runs(self):
        """Morris 스크리닝이 실행된다."""
        config = _hazard_config()
        result = morris_sensitivity(
            config, _rule_engine(),
            param_ranges={
                "emotions.fear": (0.0, 10.0),
                "emotions.hope": (0.0, 10.0),
                "physical.fatigue": (0.0, 10.0),
            },
            n_trajectories=4,
            checkpoints=_checkpoints(),
        )

        print("\n=== Morris Sensitivity ===")
        for name, mu in result["mu_star"].items():
            print(f"  {name}: mu*={mu:.3f}, sigma={result['sigma'][name]:.3f}")

        assert "mu_star" in result
        assert len(result["mu_star"]) == 3


class TestBifurcation:
    def test_detect_bifurcation(self):
        """분기점 탐지가 실행된다."""
        config = _hazard_config()
        result = detect_bifurcation(
            config, _rule_engine(),
            param_path="emotions.fear",
            values=[1.0, 3.0, 5.0, 7.0, 9.0],
            n_runs_per_value=10,
            checkpoints=_checkpoints(),
        )

        print("\n=== Bifurcation Detection (fear) ===")
        for i, val in enumerate(result["param_values"]):
            print(f"  fear={val:.0f}: mean={result['means'][i]:.2f}, std={result['stds'][i]:.2f}")
        if result["bifurcation_candidates"]:
            print(f"  Candidates: {result['bifurcation_candidates']}")

        assert len(result["param_values"]) == 5
        assert len(result["means"]) == 5
