"""SimulationConfig.phases + tick_scale_hours 테스트 (v1.2 Iteration 3)."""

from engine.core.phase import Phase, PhaseExitCondition
from engine.core.state import AgentState, EmotionalState
from engine.core.world import SimulationConfig


def _state() -> AgentState:
    return AgentState(agent_id="test", emotions=EmotionalState())


class TestTickScaleHours:
    def test_default_2_hours(self):
        """기본 2.0 = v0.5 scenario 호환."""
        cfg = SimulationConfig(initial_state=_state())
        assert cfg.tick_scale_hours == 2.0

    def test_override(self):
        cfg = SimulationConfig(initial_state=_state(), tick_scale_hours=24.0)
        assert cfg.tick_scale_hours == 24.0


class TestPhasesField:
    def test_default_none(self):
        """기본 None = 단일 phase 모드 (기존 동작)."""
        cfg = SimulationConfig(initial_state=_state())
        assert cfg.phases is None
        assert cfg.is_phase_linked is False

    def test_single_phase(self):
        cfg = SimulationConfig(
            initial_state=_state(),
            phases=[Phase(phase_id="01_calling", tick_scale_hours=2.0)],
        )
        assert cfg.is_phase_linked is True
        assert cfg.phases is not None
        assert len(cfg.phases) == 1

    def test_multiple_phases(self):
        cfg = SimulationConfig(
            initial_state=_state(),
            phases=[
                Phase(
                    phase_id="01_calling",
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=84),
                ),
                Phase(
                    phase_id="02_galilean",
                    tick_scale_hours=24.0,
                    exit_condition=PhaseExitCondition(max_tick=540),
                ),
                Phase(
                    phase_id="05_passion",
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=500),
                ),
            ],
        )
        assert cfg.is_phase_linked is True
        assert len(cfg.phases) == 3
        # 각 phase 다른 tick_scale
        assert cfg.phases[0].tick_scale_hours == 2.0
        assert cfg.phases[1].tick_scale_hours == 24.0
        assert cfg.phases[2].tick_scale_hours == 2.0

    def test_empty_list_still_not_phase_linked(self):
        """빈 리스트는 phase-linked로 간주 안 함 (안전)."""
        cfg = SimulationConfig(initial_state=_state(), phases=[])
        assert cfg.is_phase_linked is False


class TestBackwardCompat:
    def test_legacy_config_unchanged(self):
        """기존 단일 phase 모드 설정은 그대로 작동."""
        cfg = SimulationConfig(
            initial_state=_state(),
            max_tick=500,
            state_noise_scale=0.05,
        )
        # 기존 속성 모두 접근 가능
        assert cfg.max_tick == 500
        assert cfg.state_noise_scale == 0.05
        assert cfg.is_hazard_driven is False
        assert cfg.is_multi_agent is False
        assert cfg.is_phase_linked is False
        # v1.2 신규 필드 기본값
        assert cfg.tick_scale_hours == 2.0
        assert cfg.phases is None
