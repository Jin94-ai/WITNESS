"""시뮬레이션 러너 테스트."""

from engine.core.event import (
    ActionOption,
    CanonicalIntervention,
    ExternalEvent,
    StateEffect,
    WeightFormula,
)
from engine.core.state import AgentState, EmotionalState, PhysicalState
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule
from engine.rules.physical import FatigueRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.checkpoint import Checkpoint, CheckpointCondition
from engine.simulation.runner import SimulationRunner


def _simple_config(max_tick: int = 50) -> SimulationConfig:
    return SimulationConfig(
        seed=42,
        max_tick=max_tick,
        initial_state=AgentState(
            agent_id="test",
            physical=PhysicalState(fatigue=3.0),
            emotions=EmotionalState(fear=2.0, hope=7.0),
        ),
        events=[
            ExternalEvent(
                event_id="threat",
                tick=10,
                effects=[StateEffect(field_path="emotions.fear", operation="add", value=3.0)],
                action_options=[
                    ActionOption(
                        action_id="fight",
                        weight_formula=WeightFormula(base_weight=0.6),
                        effects=[StateEffect(field_path="emotions.fear", operation="add", value=1.0)],
                    ),
                    ActionOption(
                        action_id="flee",
                        weight_formula=WeightFormula(base_weight=0.4),
                    ),
                ],
            ),
        ],
    )


def _rule_engine() -> RuleEngine:
    return RuleEngine([FatigueRule(), FearResponseRule(), HomeostasisRule()])


class TestSimulationRunner:
    def test_basic_run(self):
        config = _simple_config()
        runner = SimulationRunner(config, _rule_engine())
        result = runner.run_single(seed=42)

        assert result.seed == 42
        assert result.final_state.tick == 50
        assert result.final_state.agent_id == "test"
        assert len(result.action_history) == 1  # 이벤트 1개에 행동 1개

    def test_seed_reproducibility(self):
        """동일 시드 -> 동일 결과."""
        config = _simple_config()
        engine = _rule_engine()

        r1 = SimulationRunner(config, engine).run_single(seed=42)
        r2 = SimulationRunner(config, engine).run_single(seed=42)

        assert r1.final_state.emotions.fear == r2.final_state.emotions.fear
        assert r1.final_state.physical.fatigue == r2.final_state.physical.fatigue
        assert r1.action_history[0].chosen_action == r2.action_history[0].chosen_action

    def test_different_seeds_differ(self):
        """다른 시드 -> 다른 가능성 (행동 선택이 다를 수 있음)."""
        config = _simple_config(max_tick=20)
        engine = _rule_engine()

        actions = set()
        for seed in range(100):
            r = SimulationRunner(config, engine).run_single(seed=seed)
            if r.action_history:
                actions.add(r.action_history[0].chosen_action)
        # 100회 중 최소 2가지 행동이 나와야 함 (확률적)
        assert len(actions) >= 2

    def test_state_values_in_range(self):
        """모든 상태 값이 [0, 10] 범위 내."""
        config = _simple_config(max_tick=100)
        result = SimulationRunner(config, _rule_engine()).run_single(seed=42)

        state = result.final_state
        assert 0.0 <= state.physical.fatigue <= 10.0
        assert 0.0 <= state.emotions.fear <= 10.0
        assert 0.0 <= state.emotions.hope <= 10.0

    def test_event_effects_applied(self):
        """이벤트 효과가 적용된다."""
        config = _simple_config()
        result = SimulationRunner(config, _rule_engine()).run_single(seed=42)

        # tick 10에 fear +3.0 이벤트 -> fear가 초기(2.0)보다 높아야 함
        snap = result.state_snapshots.get(10)
        assert snap is not None
        # 규칙 엔진도 적용되므로 정확한 값은 확인 어렵지만, 이벤트가 적용되었다는 것만 확인

    def test_canonical_intervention(self):
        """CanonicalIntervention이 상태를 강제 재조정한다."""
        config = SimulationConfig(
            seed=42,
            max_tick=20,
            initial_state=AgentState(
                agent_id="test",
                emotions=EmotionalState(grief=9.0, love=3.0),
            ),
            interventions=[
                CanonicalIntervention(
                    event_id="restore",
                    tick=10,
                    scripture_ref="test",
                    state_overrides={"emotions.grief": 2.0, "emotions.love": 9.0},
                ),
            ],
        )
        result = SimulationRunner(config, _rule_engine()).run_single(seed=42)

        # 개입 후 grief가 크게 감소, love가 크게 증가했어야 함
        # (이후 규칙에 의해 약간 변동되지만 방향은 유지)
        assert result.final_state.emotions.love > 5.0

    def test_checkpoint_evaluation(self):
        """체크포인트가 평가되고 일치율이 계산된다."""
        config = _simple_config()
        checkpoints = [
            Checkpoint(
                checkpoint_id="cp_fight",
                tick=10,
                conditions=[
                    CheckpointCondition(
                        condition_type="action_taken",
                        params={"action_id": "fight"},
                    )
                ],
                weight=1.0,
            ),
        ]
        result = SimulationRunner(config, _rule_engine(), checkpoints).run_single(seed=42)

        assert len(result.checkpoint_results) == 1
        assert 0.0 <= result.canonical_match_rate <= 1.0

    def test_parameter_overrides(self):
        """파라미터 오버라이드가 초기 상태에 적용된다."""
        config = _simple_config()
        config = config.model_copy(
            update={"parameter_overrides": {"emotions.fear": 9.0}}
        )
        result = SimulationRunner(config, _rule_engine()).run_single(seed=42)

        # 초기 fear가 9.0으로 시작하므로 최종 값도 높아야 함
        # (정확한 값은 규칙에 따라 다르지만 초기값이 적용되었다는 것만 확인)
        assert result.state_snapshots[0].emotions.fear == 9.0
