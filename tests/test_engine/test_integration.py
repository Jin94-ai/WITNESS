"""통합 테스트. 전체 파이프라인 검증."""

import json
from pathlib import Path

from content.peter.domain_faith import FaithJourneyState
from engine.core.world import SimulationConfig
from engine.io.loader import load_agent_state, load_events, load_interventions, register_domain_type
from engine.rules.base import RuleEngine
from engine.rules.emotional import ConfusionRule, FearResponseRule, GriefRule, HopeRule, LoveRule
from engine.rules.physical import FatigueRule, HealthRule, HungerRule
from engine.rules.social import GroupIsolationRule, RelationshipDecayRule
from engine.rules.temporal import CircadianRule, HomeostasisRule
from engine.simulation.runner import SimulationRunner

register_domain_type("faith_journey", FaithJourneyState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content" / "peter"


def _full_rule_engine() -> RuleEngine:
    return RuleEngine([
        FatigueRule(),
        HungerRule(),
        HealthRule(),
        FearResponseRule(),
        HopeRule(),
        GriefRule(),
        ConfusionRule(),
        LoveRule(),
        RelationshipDecayRule(),
        GroupIsolationRule(),
        HomeostasisRule(),
        CircadianRule(),
    ])


def _load_full_config() -> SimulationConfig:
    state = load_agent_state(CONTENT_DIR / "initial_state.json")
    json.loads((CONTENT_DIR / "canonical_events.json").read_text(encoding="utf-8"))
    events = load_events(CONTENT_DIR / "canonical_events.json")
    interventions = load_interventions(CONTENT_DIR / "canonical_events.json")
    return SimulationConfig(
        seed=42,
        max_tick=500,
        initial_state=state,
        events=events,
        interventions=interventions,
    )


class TestFullSimulation:
    def test_500_tick_completes(self):
        """500 tick 시뮬레이션이 에러 없이 완주한다."""
        config = _load_full_config()
        runner = SimulationRunner(config, _full_rule_engine())
        result = runner.run_single(seed=42)

        assert result.final_state.tick == 500
        assert result.seed == 42

    def test_all_values_in_range(self):
        """모든 상태 값이 [0, 10] 범위 내."""
        config = _load_full_config()
        result = SimulationRunner(config, _full_rule_engine()).run_single(seed=42)

        state = result.final_state
        for field in ("fatigue", "hunger", "health"):
            val = getattr(state.physical, field)
            assert 0.0 <= val <= 10.0, f"physical.{field}={val} out of range"

        for field in ("fear", "hope", "grief", "confusion", "love"):
            val = getattr(state.emotions, field)
            assert 0.0 <= val <= 10.0, f"emotions.{field}={val} out of range"

    def test_seed_reproducibility(self):
        """동일 시드 -> 동일 최종 상태."""
        config = _load_full_config()
        engine = _full_rule_engine()

        r1 = SimulationRunner(config, engine).run_single(seed=42)
        r2 = SimulationRunner(config, engine).run_single(seed=42)

        assert r1.final_state.emotions.fear == r2.final_state.emotions.fear
        assert r1.final_state.physical.fatigue == r2.final_state.physical.fatigue
        assert len(r1.action_history) == len(r2.action_history)
        for a1, a2 in zip(r1.action_history, r2.action_history):
            assert a1.chosen_action == a2.chosen_action

    def test_actions_recorded(self):
        """이벤트에 행동 선택지가 있으면 행동이 기록된다."""
        config = _load_full_config()
        result = SimulationRunner(config, _full_rule_engine()).run_single(seed=42)

        # canonical_events.json에 action_options가 있는 이벤트가 다수
        assert len(result.action_history) > 0

    def test_intervention_applied(self):
        """디베랴 회복 개입(요 21:15-17) 후 love가 높아진다."""
        config = _load_full_config()
        result = SimulationRunner(config, _full_rule_engine()).run_single(seed=42)

        # tick 358에 개입 -> love 9.0으로 강제 설정 -> 이후 약간 감쇠
        assert result.final_state.emotions.love > 4.0
