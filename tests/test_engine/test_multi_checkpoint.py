"""다중 에이전트 시뮬레이션에서 체크포인트 평가 테스트.

Peter의 체크포인트가 multi-agent 모드에서도 평가되는지 확인한다.
"""

import json
from pathlib import Path

from content.caiaphas.domain_politics import PoliticalCalculationState
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
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule, LoveRule
from engine.rules.physical import FatigueRule, HungerRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.checkpoint import Checkpoint
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _rule_engine() -> RuleEngine:
    return RuleEngine([
        FatigueRule(), HungerRule(),
        FearResponseRule(), HopeRule(), GriefRule(), LoveRule(),
        HomeostasisRule(),
    ])


def _load_peter_checkpoints() -> list[Checkpoint]:
    data = json.loads((CONTENT_DIR / "peter" / "checkpoints.json").read_text(encoding="utf-8"))
    return [Checkpoint.model_validate(cp) for cp in data["checkpoints"]]


class TestMultiAgentCheckpoint:
    def test_peter_checkpoints_evaluated(self):
        """Peter의 체크포인트가 multi-agent 모드에서 평가된다."""
        peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
        judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
        caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
        triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
        profiles = {
            "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
            "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
            "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
        }
        peter_hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
        interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
        peter_cps = _load_peter_checkpoints()

        config = SimulationConfig(
            max_tick=500,
            initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            hazard_events=peter_hazards,
            interventions=interventions,
            triggers=triggers,
            state_noise_scale=0.05,
        )

        result = SimulationWorld(
            config, _rule_engine(),
            behavior_profiles=profiles,
            checkpoints={"peter": peter_cps},
        ).run(seed=42)

        # 체크포인트 결과가 존재
        assert "peter" in result.checkpoint_results
        assert len(result.checkpoint_results["peter"]) > 0

        # 정경 일치율이 계산됨
        assert "peter" in result.canonical_match_rates
        rate = result.canonical_match_rates["peter"]
        print(f"\nMulti-agent Peter canonical_match_rate: {rate:.2%}")
        assert 0.0 <= rate <= 1.0

    def test_checkpoint_across_seeds(self):
        """여러 시드에서 Peter 정경 일치율 분포."""
        peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
        judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
        caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
        triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
        profiles = {
            "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
            "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
            "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
        }
        peter_hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
        interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
        peter_cps = _load_peter_checkpoints()

        config = SimulationConfig(
            max_tick=500,
            initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            hazard_events=peter_hazards,
            interventions=interventions,
            triggers=triggers,
            state_noise_scale=0.05,
        )

        rates = []
        for seed in range(10):
            result = SimulationWorld(
                config, _rule_engine(),
                behavior_profiles=profiles,
                checkpoints={"peter": peter_cps},
            ).run(seed=seed)
            rates.append(result.canonical_match_rates.get("peter", 0.0))

        import statistics
        mean_rate = statistics.mean(rates)
        print(f"\nMulti-agent Peter match rates (10 seeds): {[f'{r:.2%}' for r in rates]}")
        print(f"Mean: {mean_rate:.2%}")

        # 적어도 일부 체크포인트가 통과해야 함
        assert mean_rate > 0.0

    def test_no_checkpoint_agent_skipped(self):
        """체크포인트가 없는 에이전트는 건너뛴다."""
        peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
        judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")

        config = SimulationConfig(
            max_tick=10,
            initial_state=peter,
            initial_states=[peter, judas],
        )

        result = SimulationWorld(
            config, _rule_engine(),
            checkpoints={},  # 빈 체크포인트
        ).run(seed=42)

        assert len(result.checkpoint_results) == 0
        assert len(result.canonical_match_rates) == 0
