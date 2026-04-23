"""3-에이전트 다중 시뮬레이션 통합 테스트.

Peter + Judas + Caiaphas를 SimulationWorld에서 실행한다.
"""

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
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule, LoveRule
from engine.rules.physical import FatigueRule, HungerRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.world import SimulationWorld

# 도메인 타입 등록
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


def _load_3_agents():
    """3 에이전트 상태를 로드한다."""
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    return peter, judas, caiaphas


def _load_behavior_profiles():
    """행동 프로파일을 로드한다."""
    return {
        "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
    }


class TestThreeAgentSimulation:
    def test_runs_to_completion(self):
        """3-에이전트 500 tick 시뮬레이션이 완주한다."""
        peter, judas, caiaphas = _load_3_agents()
        triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
        profiles = _load_behavior_profiles()

        config = SimulationConfig(
            max_tick=500,
            initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            triggers=triggers,
            state_noise_scale=0.05,
        )

        result = SimulationWorld(
            config, _rule_engine(), behavior_profiles=profiles,
        ).run(seed=42)

        assert "peter" in result.final_states
        assert "judas" in result.final_states
        assert "caiaphas" in result.final_states
        assert result.final_states["peter"].tick == 500

    def test_seed_reproducibility(self):
        """시드 재현성 확인."""
        peter, judas, caiaphas = _load_3_agents()
        triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
        profiles = _load_behavior_profiles()

        config = SimulationConfig(
            max_tick=100,
            initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            triggers=triggers,
            state_noise_scale=0.05,
        )

        r1 = SimulationWorld(config, _rule_engine(), behavior_profiles=profiles).run(seed=77)
        r2 = SimulationWorld(config, _rule_engine(), behavior_profiles=profiles).run(seed=77)

        assert r1.final_states["peter"].emotions.fear == r2.final_states["peter"].emotions.fear
        assert r1.final_states["judas"].emotions.fear == r2.final_states["judas"].emotions.fear

    def test_different_seeds_vary(self):
        """다른 시드면 다른 결과."""
        peter, judas, caiaphas = _load_3_agents()
        profiles = _load_behavior_profiles()

        config = SimulationConfig(
            max_tick=100,
            initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            state_noise_scale=0.05,
        )

        results = []
        for seed in range(5):
            r = SimulationWorld(config, _rule_engine(), behavior_profiles=profiles).run(seed=seed)
            results.append(r.final_states["judas"].emotions.fear)

        # 5개의 시드에서 적어도 2개의 다른 값
        assert len(set(results)) > 1

    def test_trigger_fires_with_deadline(self):
        """arrest_trigger가 deadline=400에 발동한다 (조건 미충족 시)."""
        peter, judas, caiaphas = _load_3_agents()
        triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")

        config = SimulationConfig(
            max_tick=500,
            initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            triggers=triggers,
            state_noise_scale=0.01,
        )

        result = SimulationWorld(config, _rule_engine()).run(seed=42)

        # arrest_trigger는 deadline=400이므로 최소 1회 발동
        arrest_triggers = [t for t in result.fired_triggers if t["trigger_id"] == "arrest_trigger"]
        assert len(arrest_triggers) >= 1

    def test_judas_actions_recorded(self):
        """유다의 자발적 행동이 기록된다."""
        peter, judas, caiaphas = _load_3_agents()
        profiles = _load_behavior_profiles()

        config = SimulationConfig(
            max_tick=50,
            initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            state_noise_scale=0.05,
        )

        result = SimulationWorld(
            config, _rule_engine(), behavior_profiles=profiles,
        ).run(seed=42)

        judas_actions = result.action_histories.get("judas", [])
        assert len(judas_actions) > 0
        action_ids = {a.chosen_action for a in judas_actions}
        # 유다는 follow, question, withdraw 중 하나 이상을 수행해야 함
        assert len(action_ids) >= 1

    def test_caiaphas_actions_recorded(self):
        """가야바의 자발적 행동이 기록된다."""
        peter, judas, caiaphas = _load_3_agents()
        profiles = _load_behavior_profiles()

        config = SimulationConfig(
            max_tick=50,
            initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            state_noise_scale=0.05,
        )

        result = SimulationWorld(
            config, _rule_engine(), behavior_profiles=profiles,
        ).run(seed=42)

        caiaphas_actions = result.action_histories.get("caiaphas", [])
        assert len(caiaphas_actions) > 0

    def test_domain_state_preserved(self):
        """도메인 상태가 시뮬레이션 전반에 걸쳐 유지된다."""
        peter, judas, caiaphas = _load_3_agents()

        config = SimulationConfig(
            max_tick=10,
            initial_state=peter,
            initial_states=[peter, judas, caiaphas],
        )

        result = SimulationWorld(config, _rule_engine()).run(seed=42)

        # 도메인 상태가 여전히 존재
        assert result.final_states["peter"].domain_state is not None
        assert result.final_states["judas"].domain_state is not None
        assert result.final_states["caiaphas"].domain_state is not None

    def test_peter_voluntary_actions(self):
        """Peter의 자발적 행동이 기록된다."""
        peter, judas, caiaphas = _load_3_agents()
        profiles = _load_behavior_profiles()

        config = SimulationConfig(
            max_tick=100,
            initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            state_noise_scale=0.05,
        )

        result = SimulationWorld(
            config, _rule_engine(), behavior_profiles=profiles,
        ).run(seed=42)

        peter_actions = result.action_histories.get("peter", [])
        assert len(peter_actions) > 0
        action_ids = {a.chosen_action for a in peter_actions}
        # follow_closely는 거의 항상 수행됨
        assert "follow_closely" in action_ids

    def test_all_three_agents_act(self):
        """3 에이전트 모두 행동을 수행한다."""
        peter, judas, caiaphas = _load_3_agents()
        profiles = _load_behavior_profiles()

        config = SimulationConfig(
            max_tick=50,
            initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            state_noise_scale=0.05,
        )

        result = SimulationWorld(
            config, _rule_engine(), behavior_profiles=profiles,
        ).run(seed=42)

        for aid in ["peter", "judas", "caiaphas"]:
            actions = result.action_histories.get(aid, [])
            assert len(actions) > 0, f"{aid} has no actions"
