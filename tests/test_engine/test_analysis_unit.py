"""Analysis pure-function unit tests (no simulation required, fast).

Previously compute_aggregate was only exercised via slow batch tests.
"""

from engine.core.state import AgentState, EmotionalState
from engine.simulation.analysis import AggregateStats, compute_aggregate
from engine.simulation.checkpoint import ActionRecord, CheckpointResult
from engine.simulation.runner import SimulationResult


def _result(
    match_rate: float,
    actions: list[tuple[int, str, str]],  # (tick, event_id, action)
    checkpoint_pass: list[tuple[str, bool]] | None = None,
) -> SimulationResult:
    return SimulationResult(
        seed=0,
        final_state=AgentState(agent_id="x", emotions=EmotionalState()),
        action_history=[
            ActionRecord(tick=t, event_id=ev, chosen_action=a)
            for t, ev, a in actions
        ],
        checkpoint_results=[
            CheckpointResult(checkpoint_id=cid, passed=p)
            for cid, p in (checkpoint_pass or [])
        ],
        canonical_match_rate=match_rate,
    )


class TestComputeAggregate:
    def test_empty_results(self):
        agg = compute_aggregate([])
        assert isinstance(agg, AggregateStats)
        assert agg.n_runs == 0
        assert agg.match_rates == []
        assert agg.mean_match_rate == 0.0
        assert agg.std_match_rate == 0.0
        assert agg.checkpoint_pass_rates == {}
        assert agg.action_frequency == {}

    def test_single_run_no_stdev(self):
        agg = compute_aggregate([_result(match_rate=0.8, actions=[])])
        assert agg.n_runs == 1
        assert agg.mean_match_rate == 0.8
        assert agg.std_match_rate == 0.0  # n=1이면 stdev=0

    def test_match_rate_mean_and_stdev(self):
        results = [
            _result(match_rate=0.5, actions=[]),
            _result(match_rate=0.7, actions=[]),
            _result(match_rate=0.9, actions=[]),
        ]
        agg = compute_aggregate(results)
        assert agg.n_runs == 3
        assert abs(agg.mean_match_rate - 0.7) < 1e-9
        assert agg.std_match_rate > 0

    def test_action_frequency_aggregates_by_event(self):
        r1 = _result(0.5, actions=[
            (1, "storm", "hide"),
            (2, "storm", "hide"),
            (3, "voluntary", "pray"),
        ])
        r2 = _result(0.5, actions=[
            (1, "storm", "flee"),
            (2, "voluntary", "pray"),
        ])
        agg = compute_aggregate([r1, r2])
        assert agg.action_frequency["storm"] == {"hide": 2, "flee": 1}
        assert agg.action_frequency["voluntary"] == {"pray": 2}

    def test_checkpoint_pass_rates(self):
        r1 = _result(0.5, actions=[],
                     checkpoint_pass=[("cp1", True), ("cp2", False)])
        r2 = _result(0.5, actions=[],
                     checkpoint_pass=[("cp1", True), ("cp2", True)])
        r3 = _result(0.5, actions=[],
                     checkpoint_pass=[("cp1", False), ("cp2", True)])
        agg = compute_aggregate([r1, r2, r3])
        # cp1: 2/3, cp2: 2/3
        assert abs(agg.checkpoint_pass_rates["cp1"] - 2/3) < 1e-9
        assert abs(agg.checkpoint_pass_rates["cp2"] - 2/3) < 1e-9
