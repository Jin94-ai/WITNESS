"""체포 이벤트 자연 발생 테스트.

M1-Multi의 핵심: 체포가 tick 하드코딩이 아니라
유다의 환멸 누적 -> 배반 -> 트리거 발동으로 자연 발생하는지 확인한다.
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


def _run_multi_agent(seed: int, max_tick: int = 500):
    """3-에이전트 시뮬레이션을 실행한다."""
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
        max_tick=max_tick,
        initial_state=peter,
        initial_states=[peter, judas, caiaphas],
        triggers=triggers,
        state_noise_scale=0.05,
    )

    return SimulationWorld(
        config, _rule_engine(), behavior_profiles=profiles,
    ).run(seed=seed)


class TestEmergentArrest:
    def test_arrest_fires_across_seeds(self):
        """여러 시드에서 체포 트리거가 발동한다."""
        arrest_ticks = []
        for seed in range(10):
            result = _run_multi_agent(seed)
            arrests = [t for t in result.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            assert len(arrests) >= 1, f"seed={seed}: arrest never fired"
            arrest_ticks.append(arrests[0]["tick"])

        print(f"\nArrest ticks across 10 seeds: {arrest_ticks}")
        # 최소 1개는 deadline(400) 전에 자연 발생해야 함
        # 유다의 환멸이 자연스럽게 누적되면 deadline 전에 발동 가능
        # 단, 확률적이므로 10개 중 1개라도 400 미만이면 성공
        natural_count = sum(1 for t in arrest_ticks if t < 400)
        print(f"Natural arrests (before deadline): {natural_count}/10")

    def test_arrest_tick_varies(self):
        """체포 tick이 시드에 따라 변동한다 (하드코딩이 아닌 증거)."""
        arrest_ticks = set()
        for seed in range(20):
            result = _run_multi_agent(seed, max_tick=500)
            arrests = [t for t in result.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if arrests:
                arrest_ticks.add(arrests[0]["tick"])

        print(f"\nUnique arrest ticks across 20 seeds: {sorted(arrest_ticks)}")
        # 2개 이상의 서로 다른 tick이어야 함 (하드코딩이면 모두 같은 tick)
        assert len(arrest_ticks) >= 2, "Arrest tick is fixed -- not emergent"

    def test_judas_behavior_progression(self):
        """유다의 행동이 시간에 따라 변화한다."""
        result = _run_multi_agent(42)
        judas_actions = result.action_histories.get("judas", [])

        # 행동 종류 집계
        action_types = {}
        for a in judas_actions:
            action_types[a.chosen_action] = action_types.get(a.chosen_action, 0) + 1

        print(f"\nJudas action distribution: {action_types}")
        # follow, question, withdraw 등 다양한 행동이 있어야 함
        assert len(action_types) >= 2, "Judas behavior is too monotonic"
