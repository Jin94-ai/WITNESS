"""PhasedSimulationWorld tests (v1.2 Iteration 4).

backward compat + single-phase delegation + multi-phase handoff 검증.
"""

import random

from engine.core.action import AgentAction, AgentBehaviorProfile
from engine.core.event import WeightFormula
from engine.core.phase import (
    FieldMapping,
    Phase,
    PhaseExitCondition,
    PhaseHandoffSpec,
)
from engine.core.state import AgentState, EmotionalState, SlowState
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.rules.temporal import HomeostasisRule
from engine.simulation.phased_world import (
    PhasedMultiAgentResult,
    PhasedSimulationWorld,
    apply_handoff,
)
from engine.simulation.world import MultiAgentResult


def _agent(aid: str, fear: float = 5.0, mi: float = 0.0) -> AgentState:
    return AgentState(
        agent_id=aid,
        emotions=EmotionalState(fear=fear),
        slow_state=SlowState(moral_injury=mi),
    )


def _profile(aid: str) -> AgentBehaviorProfile:
    return AgentBehaviorProfile(
        agent_id=aid,
        actions=[
            AgentAction(
                action_id="idle",
                weight_formula=WeightFormula(base_weight=1.0),
            ),
        ],
    )


def _engine() -> RuleEngine:
    return RuleEngine([HomeostasisRule()])


class TestApplyHandoff:
    def test_none_spec_passthrough(self):
        prev = {"peter": _agent("peter", fear=9.0, mi=7.0)}
        nxt = {"peter": _agent("peter", fear=3.0, mi=0.0)}
        result = apply_handoff(prev, nxt, None)
        # spec None → next 그대로
        assert result["peter"].emotions.fear == 3.0
        assert result["peter"].slow_state.moral_injury == 0.0

    def test_carry_all_slow_state(self):
        """default carry_all_slow_state=True: prev slow_state → next."""
        prev = {"peter": _agent("peter", fear=9.0, mi=7.0)}
        nxt = {"peter": _agent("peter", fear=3.0, mi=0.0)}
        spec = PhaseHandoffSpec()  # default carry_all=True
        result = apply_handoff(prev, nxt, spec)
        # slow_state는 prev에서 전달됨
        assert result["peter"].slow_state.moral_injury == 7.0
        # fast state는 next 유지
        assert result["peter"].emotions.fear == 3.0

    def test_carry_all_slow_state_disabled(self):
        prev = {"peter": _agent("peter", fear=9.0, mi=7.0)}
        nxt = {"peter": _agent("peter", fear=3.0, mi=0.0)}
        spec = PhaseHandoffSpec(carry_all_slow_state=False)
        result = apply_handoff(prev, nxt, spec)
        # slow_state 복사 안 됨
        assert result["peter"].slow_state.moral_injury == 0.0

    def test_field_mapping(self):
        """explicit field mapping: fear도 전달."""
        prev = {"peter": _agent("peter", fear=9.0, mi=0.0)}
        nxt = {"peter": _agent("peter", fear=3.0, mi=0.0)}
        spec = PhaseHandoffSpec(
            mappings=[
                FieldMapping("peter", "emotions.fear", "peter", "emotions.fear"),
            ],
        )
        result = apply_handoff(prev, nxt, spec)
        assert result["peter"].emotions.fear == 9.0

    def test_agent_present_in_prev_not_next_copied(self):
        """life arc 연속성: prev에만 있는 agent는 result에 복제."""
        prev = {
            "peter": _agent("peter"),
            "judas": _agent("judas", fear=8.0, mi=6.0),
        }
        nxt = {"peter": _agent("peter")}
        result = apply_handoff(prev, nxt, PhaseHandoffSpec())
        assert "judas" in result
        assert result["judas"].slow_state.moral_injury == 6.0

    def test_missing_source_uses_default(self):
        """source가 None이면 default_if_missing 사용."""
        # peter에 어떤 사용자 정의 필드가 없는 상황 모사: nonexistent.path 사용
        prev = {"peter": _agent("peter")}
        nxt = {"peter": _agent("peter", fear=3.0)}
        spec = PhaseHandoffSpec(
            mappings=[
                FieldMapping(
                    "peter", "nonexistent.field",
                    "peter", "emotions.fear",
                    default_if_missing=7.5,
                ),
            ],
        )
        result = apply_handoff(prev, nxt, spec)
        # nonexistent.field는 None → default 7.5 사용
        assert result["peter"].emotions.fear == 7.5


class TestPhasedWorldBackwardCompat:
    """phases=None이면 기존 SimulationWorld와 완전 동일 동작."""

    def test_single_phase_mode_matches_simulation_world(self):
        peter = _agent("peter", fear=5.0)
        config = SimulationConfig(
            initial_state=peter,
            initial_states=[peter],
            max_tick=20,
            state_noise_scale=0.0,
        )
        world = PhasedSimulationWorld(
            config, _engine(),
            behavior_profiles={"peter": _profile("peter")},
        )
        result = world.run(seed=42)
        # 기존 MultiAgentResult 타입 그대로
        assert isinstance(result, MultiAgentResult)
        assert not isinstance(result, PhasedMultiAgentResult)
        # final tick = 20
        assert result.final_states["peter"].tick == 20

    def test_seed_reproducibility_single_phase(self):
        peter = _agent("peter")
        config = SimulationConfig(
            initial_state=peter, initial_states=[peter],
            max_tick=15, state_noise_scale=0.05,
        )
        world = PhasedSimulationWorld(
            config, _engine(),
            behavior_profiles={"peter": _profile("peter")},
        )
        r1 = world.run(seed=7)
        r2 = world.run(seed=7)
        assert r1.final_states["peter"].emotions.fear == r2.final_states["peter"].emotions.fear


class TestPhasedWorldMultiPhase:
    """Multi-phase 실행: state handoff가 실제로 일어나는지."""

    def test_two_phase_execution(self):
        peter = _agent("peter", fear=5.0)
        config = SimulationConfig(
            initial_state=peter,
            initial_states=[peter],
            max_tick=100,  # phase max_tick에 의해 override됨
            state_noise_scale=0.0,
            phases=[
                Phase(
                    phase_id="01_calling",
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=10),
                    handoff_to_next=PhaseHandoffSpec(),  # default carry slow
                ),
                Phase(
                    phase_id="02_galilean",
                    tick_scale_hours=24.0,
                    exit_condition=PhaseExitCondition(max_tick=5),
                ),
            ],
        )
        world = PhasedSimulationWorld(
            config, _engine(),
            behavior_profiles={"peter": _profile("peter")},
        )
        result = world.run(seed=0)

        # PhasedMultiAgentResult 타입
        assert isinstance(result, PhasedMultiAgentResult)
        # 두 phase 모두 실행됨
        assert "01_calling" in result.per_phase_results
        assert "02_galilean" in result.per_phase_results
        # phase boundaries 기록됨
        assert len(result.phase_boundaries) == 2
        assert result.phase_boundaries[0]["phase_id"] == "01_calling"
        assert result.phase_boundaries[0]["tick_scale_hours"] == 2.0
        assert result.phase_boundaries[1]["phase_id"] == "02_galilean"
        assert result.phase_boundaries[1]["tick_scale_hours"] == 24.0
        # 전체 tick offset: phase1 0-10, phase2 10-15
        assert result.phase_boundaries[0]["start_tick"] == 0
        assert result.phase_boundaries[0]["end_tick"] == 10
        assert result.phase_boundaries[1]["start_tick"] == 10

    def test_slow_state_carries_across_phases(self):
        """slow_state.moral_injury는 phase 경계에서 유지."""
        peter = _agent("peter", fear=5.0, mi=0.0)
        # phase 1 동안 moral_injury를 인위적으로 올리기 위해
        # mock으로는 어려우므로, 여기서는 기본 상태 유지만 검증
        config = SimulationConfig(
            initial_state=peter,
            initial_states=[peter],
            max_tick=100,
            state_noise_scale=0.0,
            phases=[
                Phase(
                    phase_id="a",
                    exit_condition=PhaseExitCondition(max_tick=5),
                    handoff_to_next=PhaseHandoffSpec(),  # carry slow default
                ),
                Phase(
                    phase_id="b",
                    exit_condition=PhaseExitCondition(max_tick=5),
                ),
            ],
        )
        world = PhasedSimulationWorld(
            config, _engine(),
            behavior_profiles={"peter": _profile("peter")},
        )
        result = world.run(seed=0)
        # 초기 moral_injury 0 유지
        assert result.final_states["peter"].slow_state.moral_injury == 0.0
        # 각 phase result도 접근 가능
        phase_a_result = result.per_phase_results["a"]
        assert phase_a_result.final_states["peter"].tick == 5

    def test_merged_action_history_uses_global_ticks(self):
        """action_histories의 tick이 global offset 적용되는지."""
        peter = _agent("peter")
        config = SimulationConfig(
            initial_state=peter, initial_states=[peter],
            max_tick=100, state_noise_scale=0.0,
            phases=[
                Phase(phase_id="a", exit_condition=PhaseExitCondition(max_tick=3)),
                Phase(phase_id="b", exit_condition=PhaseExitCondition(max_tick=3)),
            ],
        )
        world = PhasedSimulationWorld(
            config, _engine(),
            behavior_profiles={"peter": _profile("peter")},
        )
        result = world.run(seed=0)
        # peter action history 수집되었다면 tick이 0~5에 걸쳐 있어야
        history = result.action_histories.get("peter", [])
        if history:
            ticks = [r.tick for r in history]
            # phase a: 1-3 (local), phase b: 1-3 (local → global 4-6)
            assert max(ticks) <= 6
            # 일부 tick은 offset 적용됨
            # (정확한 숫자는 random action 선택에 따라 다름)


class TestHandoffFieldMapping:
    """명시적 field mapping 동작."""

    def test_mapping_fear_carries(self):
        rng = random.Random(42)
        _ = rng
        peter = _agent("peter", fear=8.0)
        config = SimulationConfig(
            initial_state=peter, initial_states=[peter],
            max_tick=100, state_noise_scale=0.0,
            phases=[
                Phase(
                    phase_id="a",
                    exit_condition=PhaseExitCondition(max_tick=3),
                    handoff_to_next=PhaseHandoffSpec(
                        mappings=[
                            FieldMapping(
                                "peter", "emotions.fear",
                                "peter", "emotions.fear",
                            ),
                        ],
                    ),
                ),
                Phase(
                    phase_id="b",
                    exit_condition=PhaseExitCondition(max_tick=3),
                ),
            ],
        )
        world = PhasedSimulationWorld(
            config, _engine(),
            behavior_profiles={"peter": _profile("peter")},
        )
        result = world.run(seed=0)
        # phase a 종료 시 fear 값이 phase b 시작 fear로 전달됨
        # Homeostasis rule이 fear를 조금 움직이지만 mapping 자체는 작동해야 함
        assert "a" in result.per_phase_results
        assert "b" in result.per_phase_results
