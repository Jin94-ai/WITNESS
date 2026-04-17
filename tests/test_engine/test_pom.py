"""POM (Pattern-Oriented Modeling) 테스트."""

from engine.core.state import AgentState, EmotionalState, SlowState
from engine.simulation.checkpoint import ActionRecord
from content.peter.pom_scorecard import make_peter_scorecard
from engine.simulation.pom import (
    PatternCriterion,
    evaluate_pom,
    pom_filter,
)
from engine.simulation.runner import SimulationResult


def _mock_result(
    arrest_action: str = "follow_at_distance",
    n_denials: int = 3,
    grief_peak: float = 9.0,
    moral_injury: float = 5.0,
    identity_shift: float = -2.0,
    hope: float = 5.0,
) -> SimulationResult:
    actions = []
    if arrest_action:
        actions.append(ActionRecord(tick=150, event_id="arrest", chosen_action=arrest_action))
    for i in range(n_denials):
        actions.append(ActionRecord(tick=160 + i, event_id="denial_challenge", chosen_action="deny"))

    state_snapshots = {
        0: AgentState(agent_id="test"),
        170: AgentState(agent_id="test", emotions=EmotionalState(grief=grief_peak)),
        500: AgentState(
            agent_id="test",
            emotions=EmotionalState(hope=hope, grief=2.0),
            slow_state=SlowState(
                moral_injury=moral_injury,
                identity_shift=identity_shift,
            ),
        ),
    }

    return SimulationResult(
        seed=42,
        final_state=state_snapshots[500],
        state_snapshots=state_snapshots,
        action_history=actions,
    )


class TestPOMScorecard:
    def test_canonical_peter_passes_all(self):
        """정경 베드로 패턴이 모든 기준을 통과한다."""
        scorecard = make_peter_scorecard()
        result = _mock_result(
            arrest_action="draw_sword",
            n_denials=3,
            grief_peak=9.5,
            moral_injury=6.0,
            identity_shift=-3.0,
            hope=5.0,
        )
        evaluation = evaluate_pom(result, scorecard)
        assert all(evaluation.values()), f"Failed: {[k for k, v in evaluation.items() if not v]}"

    def test_fled_fails_no_flee(self):
        """도주한 run은 no_flee 패턴 실패."""
        scorecard = make_peter_scorecard()
        result = _mock_result(arrest_action="flee", n_denials=0)
        evaluation = evaluate_pom(result, scorecard)
        assert not evaluation["no_flee"]
        assert not evaluation["sword_drawn"]

    def test_no_denial_fails_triple(self):
        """부인 0회는 triple_denial 실패."""
        scorecard = make_peter_scorecard()
        result = _mock_result(n_denials=0)
        evaluation = evaluate_pom(result, scorecard)
        assert not evaluation["triple_denial"]

    def test_low_grief_fails(self):
        """슬픔이 낮으면 grief_peak 실패."""
        scorecard = make_peter_scorecard()
        result = _mock_result(grief_peak=3.0)
        evaluation = evaluate_pom(result, scorecard)
        assert not evaluation["grief_peak"]


class TestPOMFilter:
    def test_filter_counts(self):
        """필터가 통과/실패를 올바르게 카운트한다."""
        scorecard = make_peter_scorecard()
        results = [
            _mock_result(arrest_action="draw_sword", n_denials=3, grief_peak=9.0,
                         moral_injury=5.0, identity_shift=-2.0, hope=5.0),
            _mock_result(arrest_action="flee", n_denials=0, grief_peak=2.0,
                         moral_injury=0.0, identity_shift=0.0, hope=3.0),
        ]
        summary = pom_filter(results, scorecard)
        assert summary["n_total"] == 2
        assert summary["n_all_pass"] == 1
        assert summary["all_pass_rate"] == 0.5

    def test_min_patterns(self):
        """min_patterns으로 완화된 필터."""
        scorecard = make_peter_scorecard()
        result = _mock_result(arrest_action="follow_at_distance", n_denials=3,
                              grief_peak=9.0, moral_injury=5.0, identity_shift=-2.0, hope=5.0)
        summary = pom_filter([result], scorecard, min_patterns=5)
        assert summary["n_min_pass"] == 1  # sword_drawn 실패해도 6/7 통과
