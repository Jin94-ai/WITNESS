"""체크포인트 시스템 테스트."""

from engine.core.state import AgentState, EmotionalState
from engine.simulation.checkpoint import (
    ActionRecord,
    Checkpoint,
    CheckpointCondition,
    CheckpointResult,
    compute_match_rate,
    evaluate_checkpoint,
)


def _state(tick: int = 0, **emo_kwargs) -> AgentState:
    return AgentState(
        agent_id="test",
        tick=tick,
        emotions=EmotionalState(**emo_kwargs),
    )


class TestEvaluateCheckpoint:
    def test_action_taken_pass(self):
        cp = Checkpoint(
            checkpoint_id="test",
            tick=170,
            conditions=[
                CheckpointCondition(
                    condition_type="action_taken",
                    params={"action_id": "deny", "min_count": 3, "at_tick_range": [160, 175]},
                )
            ],
        )
        actions = [
            ActionRecord(tick=163, event_id="e1", chosen_action="deny"),
            ActionRecord(tick=166, event_id="e2", chosen_action="deny"),
            ActionRecord(tick=170, event_id="e3", chosen_action="deny"),
        ]
        result = evaluate_checkpoint(cp, {}, actions)
        assert result.passed

    def test_action_taken_fail(self):
        cp = Checkpoint(
            checkpoint_id="test",
            tick=170,
            conditions=[
                CheckpointCondition(
                    condition_type="action_taken",
                    params={"action_id": "deny", "min_count": 3},
                )
            ],
        )
        actions = [
            ActionRecord(tick=163, event_id="e1", chosen_action="deny"),
            ActionRecord(tick=166, event_id="e2", chosen_action="confess"),
        ]
        result = evaluate_checkpoint(cp, {}, actions)
        assert not result.passed

    def test_state_range_pass(self):
        cp = Checkpoint(
            checkpoint_id="test",
            tick=175,
            conditions=[
                CheckpointCondition(
                    condition_type="state_range",
                    params={"field_path": "emotions.grief", "min": 8.0},
                )
            ],
        )
        history = {175: _state(tick=175, grief=9.5)}
        result = evaluate_checkpoint(cp, history, [])
        assert result.passed

    def test_state_range_fail(self):
        cp = Checkpoint(
            checkpoint_id="test",
            tick=175,
            conditions=[
                CheckpointCondition(
                    condition_type="state_range",
                    params={"field_path": "emotions.grief", "min": 8.0},
                )
            ],
        )
        history = {175: _state(tick=175, grief=5.0)}
        result = evaluate_checkpoint(cp, history, [])
        assert not result.passed

    def test_closest_tick(self):
        """정확한 tick이 없으면 가장 가까운 이전 tick 사용."""
        cp = Checkpoint(
            checkpoint_id="test",
            tick=175,
            conditions=[
                CheckpointCondition(
                    condition_type="state_range",
                    params={"field_path": "emotions.grief", "min": 8.0},
                )
            ],
        )
        history = {170: _state(tick=170, grief=9.0)}
        result = evaluate_checkpoint(cp, history, [])
        assert result.passed

    def test_multiple_conditions_all_must_pass(self):
        cp = Checkpoint(
            checkpoint_id="test",
            tick=360,
            conditions=[
                CheckpointCondition(
                    condition_type="state_range",
                    params={"field_path": "emotions.love", "min": 7.0},
                ),
                CheckpointCondition(
                    condition_type="state_range",
                    params={"field_path": "emotions.grief", "max": 5.0},
                ),
            ],
        )
        # love=9, grief=3 -> 둘 다 통과
        history = {360: _state(tick=360, love=9.0, grief=3.0)}
        assert evaluate_checkpoint(cp, history, []).passed

        # love=9, grief=7 -> grief 조건 실패
        history = {360: _state(tick=360, love=9.0, grief=7.0)}
        assert not evaluate_checkpoint(cp, history, []).passed


class TestComputeMatchRate:
    def test_all_pass(self):
        cps = [
            Checkpoint(checkpoint_id="a", tick=1, conditions=[], weight=1.0),
            Checkpoint(checkpoint_id="b", tick=2, conditions=[], weight=2.0),
        ]
        results = [
            CheckpointResult(checkpoint_id="a", passed=True),
            CheckpointResult(checkpoint_id="b", passed=True),
        ]
        assert compute_match_rate(results, cps) == 1.0

    def test_partial_pass(self):
        cps = [
            Checkpoint(checkpoint_id="a", tick=1, conditions=[], weight=1.0),
            Checkpoint(checkpoint_id="b", tick=2, conditions=[], weight=1.0),
        ]
        results = [
            CheckpointResult(checkpoint_id="a", passed=True),
            CheckpointResult(checkpoint_id="b", passed=False),
        ]
        assert compute_match_rate(results, cps) == 0.5

    def test_weighted(self):
        cps = [
            Checkpoint(checkpoint_id="a", tick=1, conditions=[], weight=1.0),
            Checkpoint(checkpoint_id="b", tick=2, conditions=[], weight=3.0),
        ]
        results = [
            CheckpointResult(checkpoint_id="a", passed=True),
            CheckpointResult(checkpoint_id="b", passed=False),
        ]
        # 1.0 / 4.0 = 0.25
        assert compute_match_rate(results, cps) == 0.25

    def test_empty(self):
        assert compute_match_rate([], []) == 0.0


class TestStateComparison:
    """state_comparison 조건 테스트."""

    def test_gt_comparison(self):
        cp = Checkpoint(
            checkpoint_id="test",
            tick=100,
            conditions=[
                CheckpointCondition(
                    condition_type="state_comparison",
                    params={"field_a": "emotions.love", "field_b": "emotions.fear", "operator": "gt"},
                )
            ],
        )
        history = {100: _state(tick=100, love=8.0, fear=3.0)}
        assert evaluate_checkpoint(cp, history, []).passed

    def test_lt_comparison(self):
        cp = Checkpoint(
            checkpoint_id="test",
            tick=100,
            conditions=[
                CheckpointCondition(
                    condition_type="state_comparison",
                    params={"field_a": "emotions.fear", "field_b": "emotions.love", "operator": "lt"},
                )
            ],
        )
        history = {100: _state(tick=100, fear=2.0, love=7.0)}
        assert evaluate_checkpoint(cp, history, []).passed

    def test_eq_comparison(self):
        cp = Checkpoint(
            checkpoint_id="test",
            tick=100,
            conditions=[
                CheckpointCondition(
                    condition_type="state_comparison",
                    params={"field_a": "emotions.fear", "field_b": "emotions.hope", "operator": "eq"},
                )
            ],
        )
        history = {100: _state(tick=100, fear=5.0, hope=5.0)}
        assert evaluate_checkpoint(cp, history, []).passed

    def test_missing_field(self):
        cp = Checkpoint(
            checkpoint_id="test",
            tick=100,
            conditions=[
                CheckpointCondition(
                    condition_type="state_comparison",
                    params={"field_a": "nonexistent", "field_b": "emotions.fear"},
                )
            ],
        )
        history = {100: _state(tick=100)}
        assert not evaluate_checkpoint(cp, history, []).passed

    def test_no_state(self):
        cp = Checkpoint(
            checkpoint_id="test",
            tick=100,
            conditions=[
                CheckpointCondition(
                    condition_type="state_comparison",
                    params={"field_a": "emotions.fear", "field_b": "emotions.love"},
                )
            ],
        )
        assert not evaluate_checkpoint(cp, {}, []).passed


class TestActionTakenEdgeCases:
    def test_no_tick_range(self):
        """tick_range 없으면 모든 tick에서 카운트."""
        cp = Checkpoint(
            checkpoint_id="test",
            tick=200,
            conditions=[
                CheckpointCondition(
                    condition_type="action_taken",
                    params={"action_id": "deny", "min_count": 2},
                )
            ],
        )
        actions = [
            ActionRecord(tick=50, event_id="e1", chosen_action="deny"),
            ActionRecord(tick=300, event_id="e2", chosen_action="deny"),
        ]
        assert evaluate_checkpoint(cp, {}, actions).passed
