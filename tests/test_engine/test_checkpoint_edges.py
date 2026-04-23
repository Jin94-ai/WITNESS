"""Checkpoint evaluator edge branches."""

from engine.core.state import AgentState, EmotionalState
from engine.core.world import SimulationConfig
from engine.simulation.checkpoint import (
    Checkpoint,
    CheckpointCondition,
    evaluate_checkpoint,
)


def _state(fear: float = 5.0) -> AgentState:
    return AgentState(agent_id="x", emotions=EmotionalState(fear=fear))


class TestSimulationConfigMultiAgent:
    def test_is_multi_agent_true(self):
        """2개 이상 agent → multi_agent (line 74)."""
        config = SimulationConfig(
            initial_state=_state(),
            initial_states=[_state(), AgentState(agent_id="y")],
        )
        assert config.is_multi_agent is True

    def test_is_multi_agent_false_with_single(self):
        config = SimulationConfig(initial_state=_state())
        assert config.is_multi_agent is False


class TestCheckpointEvaluateEdges:
    def test_unknown_condition_type(self):
        """condition_type이 알 수 없으면 fail + 메시지 (line 123)."""
        # Pydantic Literal이 감시 안 하도록 우회: dict로 직접 생성
        cp = Checkpoint(
            checkpoint_id="unknown_cond", tick=10, description="test",
            conditions=[CheckpointCondition.model_validate({
                "condition_type": "state_range",
                "params": {"field_path": "emotions.fear", "min": 0},
            })],
        )
        # override condition_type via model_copy
        cond = cp.conditions[0]
        cond_mutated = cond.__class__.model_construct(
            condition_type="UNKNOWN_TYPE",  # type: ignore[arg-type]
            params=cond.params,
        )
        cp = cp.model_copy(update={"conditions": [cond_mutated]})
        result = evaluate_checkpoint(cp, {10: _state()}, [])
        assert result.passed is False
        assert "unknown" in result.details.lower() or "type" in result.details.lower()

    def test_state_range_no_state_at_tick(self):
        """state_history가 비어있으면 no state at tick 반환 (line 179)."""
        cp = Checkpoint(
            checkpoint_id="x", tick=500, description="",
            conditions=[CheckpointCondition(
                condition_type="state_range",
                params={"field_path": "emotions.fear", "min": 0, "max": 10},
            )],
        )
        result = evaluate_checkpoint(cp, {}, [])
        assert result.passed is False
        assert "no state" in result.details

    def test_state_range_field_not_found(self):
        """field 경로 미존재 → field not found (line 183)."""
        cp = Checkpoint(
            checkpoint_id="x", tick=5, description="",
            conditions=[CheckpointCondition(
                condition_type="state_range",
                params={"field_path": "nonexistent.field", "min": 0, "max": 10},
            )],
        )
        result = evaluate_checkpoint(cp, {5: _state()}, [])
        assert result.passed is False
        assert "not found" in result.details

    def test_state_comparison_non_numeric(self):
        """두 field 중 하나가 non-numeric → non-numeric comparison (line 216)."""
        cp = Checkpoint(
            checkpoint_id="x", tick=5, description="",
            conditions=[CheckpointCondition(
                condition_type="state_comparison",
                params={
                    "field_a": "emotions.fear",
                    "field_b": "agent_id",  # string
                    "operator": "gt",
                },
            )],
        )
        result = evaluate_checkpoint(cp, {5: _state()}, [])
        assert result.passed is False
        assert "non-numeric" in result.details
