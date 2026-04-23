"""Phase boundary agent introduction 테스트 (v1.2 Iter 17).

Phase N에는 없던 agent가 Phase N+1의 agents_active에 있으면
config.initial_states에서 fallback 로드되어 등장.

예: 소명(Peter만) → 갈릴리 사역(Peter + Judas, 12 사도 택정 시점).
"""

from engine.core.phase import Phase, PhaseExitCondition, PhaseHandoffSpec
from engine.core.state import AgentState, EmotionalState
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.rules.temporal import HomeostasisRule
from engine.simulation.phased_world import (
    PhasedMultiAgentResult,
    PhasedSimulationWorld,
)


def _agent(aid: str, fear: float = 5.0) -> AgentState:
    return AgentState(agent_id=aid, emotions=EmotionalState(fear=fear))


def _rules() -> RuleEngine:
    return RuleEngine([HomeostasisRule()])


class TestAgentIntroductionAtPhaseBoundary:
    def test_new_agent_introduced_at_phase_2(self):
        """Phase 1은 solo, Phase 2는 추가 agent 포함."""
        alpha = _agent("alpha", fear=5.0)
        beta = _agent("beta", fear=8.0)  # Phase 2에서 등장
        config = SimulationConfig(
            initial_state=alpha,
            initial_states=[alpha, beta],  # 전체 agents 풀
            max_tick=100,
            state_noise_scale=0.0,
            phases=[
                Phase(
                    phase_id="phase1_solo",
                    agents_active=["alpha"],  # alpha만
                    exit_condition=PhaseExitCondition(max_tick=5),
                    handoff_to_next=PhaseHandoffSpec(),
                ),
                Phase(
                    phase_id="phase2_two",
                    agents_active=["alpha", "beta"],  # beta 새로 등장
                    exit_condition=PhaseExitCondition(max_tick=5),
                ),
            ],
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)
        assert isinstance(result, PhasedMultiAgentResult)

        # Phase 1 결과에는 alpha만
        p1 = result.per_phase_results["phase1_solo"]
        assert "alpha" in p1.final_states
        assert "beta" not in p1.final_states

        # Phase 2 결과에는 alpha + beta 둘 다
        p2 = result.per_phase_results["phase2_two"]
        assert "alpha" in p2.final_states
        assert "beta" in p2.final_states

    def test_introduced_agent_keeps_config_initial_values(self):
        """새로 등장한 agent는 config.initial_states의 원본 값 사용."""
        alpha = _agent("alpha", fear=5.0)
        beta = _agent("beta", fear=8.5)
        config = SimulationConfig(
            initial_state=alpha,
            initial_states=[alpha, beta],
            max_tick=100,
            state_noise_scale=0.0,
            phases=[
                Phase(
                    phase_id="solo",
                    agents_active=["alpha"],
                    exit_condition=PhaseExitCondition(max_tick=1),
                    handoff_to_next=PhaseHandoffSpec(),
                ),
                Phase(
                    phase_id="with_beta",
                    agents_active=["alpha", "beta"],
                    exit_condition=PhaseExitCondition(max_tick=1),
                ),
            ],
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        # beta가 Phase 2 시작 시 initial value (fear=8.5) 근처
        # HomeostasisRule이 fear를 3으로 감쇄시키지만 1 tick에서는 영향 미미
        p2 = result.per_phase_results["with_beta"]
        # beta가 실제로 존재
        assert "beta" in p2.final_states
        # fear 값이 초기값 8.5 가까이 (1 tick에서 크게 변하지 않음)
        assert p2.final_states["beta"].emotions.fear > 7.0

    def test_agent_only_in_later_phase_present(self):
        """한 phase만 특정 agent가 있는 경우."""
        alpha = _agent("alpha")
        beta = _agent("beta")
        gamma = _agent("gamma")
        config = SimulationConfig(
            initial_state=alpha,
            initial_states=[alpha, beta, gamma],
            max_tick=100,
            state_noise_scale=0.0,
            phases=[
                Phase(
                    phase_id="a_only",
                    agents_active=["alpha"],
                    exit_condition=PhaseExitCondition(max_tick=2),
                    handoff_to_next=PhaseHandoffSpec(),
                ),
                Phase(
                    phase_id="a_and_gamma",
                    agents_active=["alpha", "gamma"],  # beta는 여전히 없음
                    exit_condition=PhaseExitCondition(max_tick=2),
                ),
            ],
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        # Phase 1: alpha만
        assert list(result.per_phase_results["a_only"].final_states.keys()) == ["alpha"]
        # Phase 2: alpha + gamma (beta 없음)
        p2_keys = set(result.per_phase_results["a_and_gamma"].final_states.keys())
        assert p2_keys == {"alpha", "gamma"}

    def test_backward_compat_agents_active_none(self):
        """agents_active=None인 phase는 carry-forward만 (신규 agent 도입 없음)."""
        alpha = _agent("alpha")
        beta = _agent("beta")
        config = SimulationConfig(
            initial_state=alpha,
            initial_states=[alpha, beta],  # beta는 config에 있지만
            max_tick=100,
            state_noise_scale=0.0,
            phases=[
                Phase(
                    phase_id="solo",
                    agents_active=["alpha"],  # alpha만
                    exit_condition=PhaseExitCondition(max_tick=2),
                    handoff_to_next=PhaseHandoffSpec(),
                ),
                Phase(
                    phase_id="default_unchanged",
                    # agents_active=None → current_states carry만
                    exit_condition=PhaseExitCondition(max_tick=2),
                ),
            ],
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        # Phase 2 agents_active=None이면 Phase 1에서 carry된 agent만 (alpha만)
        p2_keys = set(result.per_phase_results["default_unchanged"].final_states.keys())
        assert p2_keys == {"alpha"}
        # beta는 소개되지 않음


class TestIntroductionPlusHandoff:
    """기존 agent의 state는 handoff 적용, 새 agent는 config initial 그대로."""

    def test_combined_carry_and_introduce(self):
        alpha = _agent("alpha", fear=3.0)
        beta = _agent("beta", fear=9.0)
        config = SimulationConfig(
            initial_state=alpha,
            initial_states=[alpha, beta],
            max_tick=100,
            state_noise_scale=0.0,
            phases=[
                Phase(
                    phase_id="phase1",
                    agents_active=["alpha"],
                    exit_condition=PhaseExitCondition(max_tick=10),
                    # 명시적 handoff: alpha의 fear 그대로 전달
                    handoff_to_next=PhaseHandoffSpec(),
                ),
                Phase(
                    phase_id="phase2_with_beta",
                    agents_active=["alpha", "beta"],
                    exit_condition=PhaseExitCondition(max_tick=1),
                ),
            ],
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        p2 = result.per_phase_results["phase2_with_beta"]
        # alpha의 fear는 Phase 1에서 homeostat 영향 (3.0 근처 유지)
        assert 2.5 <= p2.final_states["alpha"].emotions.fear <= 4.0
        # beta는 config.initial_states 그대로 (fear=9.0 근처)
        # Phase 2 1 tick만 실행 → homeostat 영향 미미
        assert p2.final_states["beta"].emotions.fear > 8.0
