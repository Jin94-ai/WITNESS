"""다중 에이전트 배치 실행 + 집계 분석 테스트."""

from pathlib import Path

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.analysis import compute_multi_aggregate
from engine.simulation.batch import run_multi_batch

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _rule_engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), HopeRule(), HomeostasisRule()])


class TestMultiBatch:
    def test_run_multi_batch(self):
        """다중 에이전트 배치가 실행된다."""
        peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
        judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
        triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
        profiles = {
            "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
        }

        config = SimulationConfig(
            max_tick=100,
            initial_state=peter,
            initial_states=[peter, judas],
            triggers=triggers,
            state_noise_scale=0.05,
        )

        results = run_multi_batch(
            config, _rule_engine(), n_runs=5,
            behavior_profiles=profiles,
        )

        assert len(results) == 5
        for r in results:
            assert "peter" in r.final_states
            assert "judas" in r.final_states


class TestMultiAggregate:
    def test_compute_aggregate(self):
        """다중 에이전트 배치 집계가 작동한다."""
        peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
        judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
        caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
        triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
        profiles = {
            "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
            "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
            "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
        }

        config = SimulationConfig(
            max_tick=200,
            initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            triggers=triggers,
            state_noise_scale=0.05,
        )

        results = run_multi_batch(
            config, _rule_engine(), n_runs=5,
            behavior_profiles=profiles,
        )

        agg = compute_multi_aggregate(results)

        assert agg["n_runs"] == 5
        assert "judas" in agg["agent_action_frequencies"]
        assert "caiaphas" in agg["agent_action_frequencies"]
        assert "trigger_frequencies" in agg
        assert "trigger_tick_stats" in agg

        print(f"\nTrigger frequencies: {agg['trigger_frequencies']}")
        print(f"Judas actions: {agg['agent_action_frequencies'].get('judas', {})}")

    def test_empty_results(self):
        """빈 결과에 대해 안전하게 동작."""
        agg = compute_multi_aggregate([])
        assert agg["n_runs"] == 0
