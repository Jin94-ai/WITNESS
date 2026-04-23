"""Multi-agent trajectory export + UMAP clustering 테스트."""

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
    load_interventions,
    load_triggers,
    register_domain_type,
)
from engine.io.trajectory import multi_dataset_to_feature_matrix, multi_result_to_record
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.analysis import cluster_trajectories
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run_ensemble(n_seeds=20):
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT_DIR / "crowd" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
    profiles = {
        "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
        "crowd": load_behavior_profile(CONTENT_DIR / "crowd" / "behavior_profile.json"),
    }
    config = SimulationConfig(
        max_tick=300, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )
    return [SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=s)
            for s in range(n_seeds)]


class TestMultiTrajectory:
    def test_multi_result_to_record(self):
        """MultiAgentResult를 레코드로 변환한다."""
        results = _run_ensemble(n_seeds=3)
        record = multi_result_to_record(results[0])

        assert "seed" in record
        assert "peter_fear" in record
        assert "judas_fear" in record
        assert "trigger_ticks" in record
        assert "n_hazard_events" in record

    def test_feature_matrix(self):
        """feature matrix가 올바르게 생성된다."""
        results = _run_ensemble(n_seeds=5)
        records = [multi_result_to_record(r) for r in results]
        matrix, names = multi_dataset_to_feature_matrix(records)

        assert len(matrix) == 5
        assert len(names) > 0
        assert all(len(row) == len(names) for row in matrix)
        print(f"\nFeature matrix: {len(matrix)} rows x {len(names)} features")
        print(f"Features: {names[:10]}...")

    @pytest.mark.slow
    def test_umap_clustering(self):
        """Multi-agent 데이터에 UMAP 클러스터링이 작동한다."""
        results = _run_ensemble(n_seeds=15)
        records = [multi_result_to_record(r) for r in results]
        matrix, names = multi_dataset_to_feature_matrix(records)

        cluster_result = cluster_trajectories(matrix, min_cluster_size=3)

        print(f"\nClustering: {cluster_result['n_clusters']} clusters, "
              f"noise={cluster_result['noise_ratio']:.1%}")
        assert "labels" in cluster_result
        assert len(cluster_result["labels"]) == 15
