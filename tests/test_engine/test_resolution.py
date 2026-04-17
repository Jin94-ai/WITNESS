"""동적 해상도 시스템 테스트."""

from engine.core.state import AgentState, EmotionalState, PhysicalState
from engine.simulation.resolution import (
    AnchorWindow,
    ResolutionConfig,
    ResolutionEngine,
    ResolutionTier,
    compute_tension,
)


def _agent(**kwargs) -> AgentState:
    defaults = {"agent_id": "test"}
    defaults.update(kwargs)
    return AgentState(**defaults)


class TestComputeTension:
    def test_low_tension(self):
        agent = _agent(emotions=EmotionalState(fear=1.0, confusion=1.0, grief=1.0))
        assert compute_tension(agent) < 3.0

    def test_high_tension(self):
        agent = _agent(
            emotions=EmotionalState(fear=9.0, confusion=8.0, grief=8.0, love=8.0),
            physical=PhysicalState(fatigue=9.0),
        )
        assert compute_tension(agent) > 5.0

    def test_conflict_raises_tension(self):
        """love와 fear가 동시에 높으면 갈등으로 긴장 증가."""
        no_conflict = _agent(emotions=EmotionalState(fear=8.0, love=1.0))
        conflict = _agent(emotions=EmotionalState(fear=8.0, love=8.0))
        assert compute_tension(conflict) > compute_tension(no_conflict)


class TestResolutionEngine:
    def test_default_is_chronicle(self):
        engine = ResolutionEngine(ResolutionConfig())
        agent = _agent()
        assert engine.determine_tier(50, agent) == ResolutionTier.CHRONICLE

    def test_anchor_window_overrides(self):
        config = ResolutionConfig(
            anchor_windows=[AnchorWindow(start_tick=100, end_tick=120, tier=ResolutionTier.SCENE)]
        )
        engine = ResolutionEngine(config)
        agent = _agent()
        assert engine.determine_tier(110, agent) == ResolutionTier.SCENE
        assert engine.determine_tier(50, agent) == ResolutionTier.CHRONICLE

    def test_tension_triggers_scene(self):
        config = ResolutionConfig(tension_threshold=5.0)
        engine = ResolutionEngine(config)
        tense = _agent(
            emotions=EmotionalState(fear=9.0, confusion=8.0, grief=7.0),
            physical=PhysicalState(fatigue=8.0),
        )
        assert engine.determine_tier(50, tense) == ResolutionTier.SCENE

    def test_event_density_triggers_episode(self):
        config = ResolutionConfig(event_density_window=5, event_density_threshold=2)
        engine = ResolutionEngine(config)
        agent = _agent()
        engine.record_event(48)
        engine.record_event(49)
        assert engine.determine_tier(50, agent) == ResolutionTier.EPISODE

    def test_should_snapshot(self):
        engine = ResolutionEngine(ResolutionConfig())
        assert engine.should_snapshot(ResolutionTier.SCENE)
        assert engine.should_snapshot(ResolutionTier.EPISODE)
        assert not engine.should_snapshot(ResolutionTier.CHRONICLE)
