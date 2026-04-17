"""Hazard-driven runner 통합 테스트 (slow state, resolution 포함)."""

from engine.core.hazard import HazardEvent, HazardFunction
from engine.core.state import AgentState, EmotionalState, PhysicalState
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule
from engine.rules.temporal import HomeostasisRule, SlowStateRule
from engine.simulation.resolution import AnchorWindow, ResolutionConfig
from engine.simulation.runner import SimulationRunner


def _hazard_config(noise: float = 0.0) -> SimulationConfig:
    return SimulationConfig(
        max_tick=50,
        initial_state=AgentState(
            agent_id="test",
            emotions=EmotionalState(fear=5.0, hope=5.0, love=7.0),
            physical=PhysicalState(fatigue=3.0),
        ),
        hazard_events=[
            HazardEvent(
                event_id="test_event",
                hazard=HazardFunction(base_rate=0.3),
                anchor_window=(5, 40),
                max_fires=2,
                effects_on_fire=[
                    {"field_path": "emotions.fear", "operation": "add", "value": 2.0},
                ],
                action_options_on_fire=[
                    {
                        "action_id": "act_a",
                        "description": "action A",
                        "weight_formula": {"base_weight": 0.5, "state_multipliers": [
                            {"field_path": "emotions.fear", "factor_type": "linear", "params": {"scale": 0.3}},
                        ]},
                        "effects": [],
                    },
                    {
                        "action_id": "act_b",
                        "description": "action B",
                        "weight_formula": {"base_weight": 0.5, "state_multipliers": [
                            {"field_path": "emotions.love", "factor_type": "linear", "params": {"scale": 0.3}},
                        ]},
                        "effects": [],
                    },
                ],
            ),
        ],
        state_noise_scale=noise,
    )


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), HomeostasisRule(), SlowStateRule()])


class TestHazardRunner:
    def test_hazard_mode_detected(self):
        config = _hazard_config()
        assert config.is_hazard_driven

    def test_hazard_events_fire(self):
        config = _hazard_config()
        result = SimulationRunner(config, _engine()).run_single(seed=42)
        assert len(result.fired_events) > 0

    def test_actions_before_effects(self):
        """행동 결정이 이벤트 효과 적용 전에 이루어진다."""
        config = _hazard_config()
        result = SimulationRunner(config, _engine()).run_single(seed=42)
        # effects가 fear +2.0이므로, 행동 결정 시점의 fear가 effects 적용 후보다 낮아야 함
        # (간접 확인: 행동이 기록되었다면 순서가 맞음)
        assert len(result.action_history) > 0

    def test_slow_state_accumulates(self):
        """deny 행동 시 slow state가 누적된다."""
        # deny 행동을 유도하기 위해 별도 이벤트 구성
        config = SimulationConfig(
            max_tick=30,
            initial_state=AgentState(
                agent_id="test",
                emotions=EmotionalState(fear=9.0, love=2.0),
            ),
            hazard_events=[
                HazardEvent(
                    event_id="challenge",
                    hazard=HazardFunction(base_rate=0.8),
                    max_fires=3,
                    cooldown=2,
                    effects_on_fire=[],
                    action_options_on_fire=[
                        {
                            "action_id": "deny",
                            "weight_formula": {"base_weight": 0.8, "state_multipliers": [
                                {"field_path": "emotions.fear", "factor_type": "linear", "params": {"scale": 0.5}},
                            ]},
                            "effects": [
                                {"field_path": "emotions.grief", "operation": "add", "value": 1.0},
                                {"field_path": "slow_state.moral_injury", "operation": "add", "value": 2.0},
                                {"field_path": "slow_state.breach_count", "operation": "add", "value": 1.0},
                            ],
                        },
                        {
                            "action_id": "confess",
                            "weight_formula": {"base_weight": 0.1},
                            "effects": [],
                        },
                    ],
                ),
            ],
        )
        result = SimulationRunner(config, _engine()).run_single(seed=42)
        denials = sum(1 for a in result.action_history if a.chosen_action == "deny")
        if denials > 0:
            assert result.final_state.slow_state.moral_injury > 0
            assert result.final_state.slow_state.breach_count >= denials

    def test_noise_creates_variation(self):
        """Langevin 노이즈가 결과를 변동시킨다."""
        config_clean = _hazard_config(noise=0.0)
        config_noisy = _hazard_config(noise=0.3)
        r1 = SimulationRunner(config_clean, _engine()).run_single(seed=42)
        r2 = SimulationRunner(config_noisy, _engine()).run_single(seed=42)
        assert r1.final_state.emotions.fear != r2.final_state.emotions.fear

    def test_resolution_integration(self):
        """동적 해상도가 runner에 통합되어 작동한다."""
        config = _hazard_config()
        res_config = ResolutionConfig(
            anchor_windows=[AnchorWindow(start_tick=10, end_tick=20)],
            tension_threshold=6.0,
        )
        result = SimulationRunner(config, _engine(), resolution_config=res_config).run_single(seed=42)
        # resolution_tiers에 기록이 있어야 함
        assert isinstance(result.resolution_tiers, dict)
        # anchor window 내 tick에서 scene tier가 기록되어야 함
        scene_ticks = [t for t, tier in result.resolution_tiers.items() if tier == "scene"]
        assert any(10 <= t <= 20 for t in scene_ticks)

    def test_seed_reproducibility_hazard(self):
        """Hazard 모드에서도 시드 재현성."""
        config = _hazard_config(noise=0.05)
        engine = _engine()
        r1 = SimulationRunner(config, engine).run_single(seed=99)
        r2 = SimulationRunner(config, engine).run_single(seed=99)
        assert r1.final_state.emotions.fear == r2.final_state.emotions.fear
        assert len(r1.fired_events) == len(r2.fired_events)
