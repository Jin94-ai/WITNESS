"""Inhibitor rule 실제 SimulationWorld 파이프라인 통합 (v1.2 Iter 26).

unit test (test_inhibitor_rules.py)는 rule.apply()를 직접 호출.
여기서는 실제 PhasedSimulationWorld를 돌려 inhibitor가 tick 루프 내에서
RuleContext.dt_hours를 올바르게 받아 감쇄를 적용하는지 확인한다.

reviewer (Gemini) 지적 대응: 3년 모델에서 감쇄 없이 환멸만 쌓이면
1년 차에 조기 배반. 이 테스트는 inhibitor가 pipeline에서 제대로 작동함을
증명한다 (+ dt_hours phase-variable 확인).
"""

from engine.core.phase import Phase, PhaseExitCondition
from engine.core.state import AgentState, EmotionalState, SlowState
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.rules.inhibitor import FieldAttenuationRule
from engine.simulation.phased_world import (
    PhasedMultiAgentResult,
    PhasedSimulationWorld,
)


def _agent(aid: str, *, awe: float = 0.0, trust_scar: float = 0.0) -> AgentState:
    return AgentState(
        agent_id=aid,
        emotions=EmotionalState(awe=awe),
        slow_state=SlowState(trust_scar=trust_scar),
    )


class TestInhibitorInPhasedWorld:
    def test_attenuation_applied_each_tick_with_dt(self):
        alpha = _agent("alpha", awe=8.0)
        beta = _agent("beta", trust_scar=5.0)
        config = SimulationConfig(
            initial_state=alpha,
            initial_states=[alpha, beta],
            max_tick=100,
            state_noise_scale=0.0,
            phases=[
                Phase(
                    phase_id="single",
                    agents_active=["alpha", "beta"],
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=10),
                ),
            ],
        )
        engine = RuleEngine([
            FieldAttenuationRule(
                subject_agent_id="beta",
                target_field_path="slow_state.trust_scar",
                trigger_agent_id="alpha",
                trigger_field_path="emotions.awe",
                trigger_threshold=5.0,
                attenuation_per_hour=0.1,
            ),
        ])
        world = PhasedSimulationWorld(config, engine)
        result = world.run(seed=0)
        assert isinstance(result, PhasedMultiAgentResult)

        beta_final = result.final_states["beta"]
        # 10 tick × 2h × 0.1/h = 2.0 감쇄 → 3.0
        assert abs(beta_final.slow_state.trust_scar - 3.0) < 1e-6

    def test_attenuation_scales_with_tick_scale(self):
        """같은 실제 hours라면 tick_scale 달라도 동일한 감쇄 결과."""
        alpha = _agent("alpha", awe=8.0)
        beta = _agent("beta", trust_scar=5.0)
        engine = RuleEngine([
            FieldAttenuationRule(
                subject_agent_id="beta",
                target_field_path="slow_state.trust_scar",
                trigger_agent_id="alpha",
                trigger_field_path="emotions.awe",
                trigger_threshold=5.0,
                attenuation_per_hour=0.1,
            ),
        ])

        # 2h/tick × 24 tick = 48h
        config_dense = SimulationConfig(
            initial_state=alpha, initial_states=[alpha, beta],
            max_tick=100, state_noise_scale=0.0,
            phases=[Phase(
                phase_id="dense", agents_active=["alpha", "beta"],
                tick_scale_hours=2.0,
                exit_condition=PhaseExitCondition(max_tick=24),
            )],
        )
        # 24h/tick × 2 tick = 48h
        config_sparse = SimulationConfig(
            initial_state=alpha, initial_states=[alpha, beta],
            max_tick=100, state_noise_scale=0.0,
            phases=[Phase(
                phase_id="sparse", agents_active=["alpha", "beta"],
                tick_scale_hours=24.0,
                exit_condition=PhaseExitCondition(max_tick=2),
            )],
        )
        r_dense = PhasedSimulationWorld(config_dense, engine).run(seed=0)
        r_sparse = PhasedSimulationWorld(config_sparse, engine).run(seed=0)

        # 둘 다 48h × 0.1/h = 4.8 감쇄 → 0.2
        dense_final = r_dense.final_states["beta"].slow_state.trust_scar
        sparse_final = r_sparse.final_states["beta"].slow_state.trust_scar
        assert abs(dense_final - sparse_final) < 1e-6
        assert abs(dense_final - 0.2) < 1e-6

    def test_no_attenuation_when_trigger_below_threshold(self):
        alpha = _agent("alpha", awe=2.0)  # below threshold 5.0
        beta = _agent("beta", trust_scar=5.0)
        config = SimulationConfig(
            initial_state=alpha, initial_states=[alpha, beta],
            max_tick=100, state_noise_scale=0.0,
            phases=[Phase(
                phase_id="single", agents_active=["alpha", "beta"],
                tick_scale_hours=2.0,
                exit_condition=PhaseExitCondition(max_tick=10),
            )],
        )
        engine = RuleEngine([
            FieldAttenuationRule(
                subject_agent_id="beta",
                target_field_path="slow_state.trust_scar",
                trigger_agent_id="alpha",
                trigger_field_path="emotions.awe",
                trigger_threshold=5.0,
                attenuation_per_hour=0.1,
            ),
        ])
        result = PhasedSimulationWorld(config, engine).run(seed=0)
        # 감쇄 안 됨
        assert result.final_states["beta"].slow_state.trust_scar == 5.0

    def test_attenuation_floors_at_min_value(self):
        alpha = _agent("alpha", awe=8.0)
        beta = _agent("beta", trust_scar=0.5)
        config = SimulationConfig(
            initial_state=alpha, initial_states=[alpha, beta],
            max_tick=100, state_noise_scale=0.0,
            phases=[Phase(
                phase_id="single", agents_active=["alpha", "beta"],
                tick_scale_hours=2.0,
                exit_condition=PhaseExitCondition(max_tick=50),
            )],
        )
        engine = RuleEngine([
            FieldAttenuationRule(
                subject_agent_id="beta",
                target_field_path="slow_state.trust_scar",
                trigger_agent_id="alpha",
                trigger_field_path="emotions.awe",
                trigger_threshold=5.0,
                attenuation_per_hour=0.5,
                min_target_value=0.1,
            ),
        ])
        result = PhasedSimulationWorld(config, engine).run(seed=0)
        # 많이 감쇄되어도 floor 0.1
        assert result.final_states["beta"].slow_state.trust_scar == 0.1

    def test_multi_phase_dt_hours_switch(self):
        """phase 경계에서 dt_hours가 바뀌어도 감쇄량이 phase별 정확."""
        alpha = _agent("alpha", awe=8.0)
        beta = _agent("beta", trust_scar=10.0)
        engine = RuleEngine([
            FieldAttenuationRule(
                subject_agent_id="beta",
                target_field_path="slow_state.trust_scar",
                trigger_agent_id="alpha",
                trigger_field_path="emotions.awe",
                trigger_threshold=5.0,
                attenuation_per_hour=0.05,
            ),
        ])
        config = SimulationConfig(
            initial_state=alpha, initial_states=[alpha, beta],
            max_tick=200, state_noise_scale=0.0,
            phases=[
                Phase(
                    phase_id="p1", agents_active=["alpha", "beta"],
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=10),
                ),  # 20h × 0.05 = 1.0
                Phase(
                    phase_id="p2", agents_active=["alpha", "beta"],
                    tick_scale_hours=24.0,
                    exit_condition=PhaseExitCondition(max_tick=2),
                ),  # 48h × 0.05 = 2.4
            ],
        )
        result = PhasedSimulationWorld(config, engine).run(seed=0)
        # 총 감쇄 3.4 → 6.6
        # 단, handoff가 slow_state carry-all이므로 Phase 1 끝 상태 → Phase 2 시작
        final = result.final_states["beta"].slow_state.trust_scar
        assert abs(final - 6.6) < 1e-6
