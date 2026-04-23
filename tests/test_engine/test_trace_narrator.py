"""Trace → narrative 렌더러 테스트.

TRACE_SCHEMA.md §3 / v2.0 Narrative Witness Layer preview.
"""

from types import SimpleNamespace

from engine.rendering.trace_emitter import TraceEvent
from engine.rendering.trace_narrator import (
    narrate_result,
    render_event_line,
    render_trace_timeline,
)
from engine.simulation.checkpoint import ActionRecord


class TestRenderEventLine:
    def test_action_with_visible_signal(self):
        ev = TraceEvent(
            tick=148, type="action_taken",
            payload={
                "agent": "judas", "action": "withdraw",
                "visible_signal": "유다가 말없이 일어났다.",
            },
        )
        line = render_event_line(ev)
        assert "148" in line
        assert "유다가 말없이 일어났다" in line

    def test_action_without_signal_fallback(self):
        ev = TraceEvent(
            tick=10, type="action_taken",
            payload={"agent": "peter", "action": "pray"},
        )
        line = render_event_line(ev)
        assert "peter" in line
        assert "pray" in line

    def test_trigger_fired_line(self):
        ev = TraceEvent(
            tick=152, type="trigger_fired",
            payload={"trigger_id": "arrest_trigger"},
        )
        line = render_event_line(ev)
        assert "152" in line
        assert "arrest_trigger" in line

    def test_bifurcation_line(self):
        ev = TraceEvent(
            tick=100, type="bifurcation_point",
            payload={"decision_window": [75, 120]},
        )
        line = render_event_line(ev)
        assert "분기점" in line
        assert "75" in line and "120" in line

    def test_belief_update_line(self):
        ev = TraceEvent(
            tick=90, type="belief_update",
            payload={
                "observer": "peter", "target": "judas",
                "trigger": "observed withdraw x3",
            },
        )
        line = render_event_line(ev)
        assert "peter" in line and "judas" in line

    def test_canonical_match_line(self):
        ev = TraceEvent(
            tick=210, type="canonical_match",
            payload={"checkpoint_id": "peter_denial_1", "passed": True},
        )
        line = render_event_line(ev)
        assert "peter_denial_1" in line
        assert "일치" in line

    def test_unknown_type_fallback(self):
        ev = TraceEvent(tick=5, type="mystery_event", payload={})
        line = render_event_line(ev)
        assert "mystery_event" in line


class TestRenderTraceTimeline:
    def test_empty_events(self):
        assert render_trace_timeline([]) == ""

    def test_chronological_ordering_preserved(self):
        events = [
            TraceEvent(tick=5, type="action_taken", payload={"agent": "a", "action": "x"}),
            TraceEvent(tick=10, type="action_taken", payload={"agent": "a", "action": "y"}),
            TraceEvent(tick=15, type="trigger_fired", payload={"trigger_id": "t"}),
        ]
        out = render_trace_timeline(events)
        assert out.index("tick    5") < out.index("tick   10")
        assert out.index("tick   10") < out.index("tick   15")

    def test_skip_repeats_collapses_same_action(self):
        events = [
            TraceEvent(tick=1, type="action_taken", payload={"agent": "a", "action": "pray"}),
            TraceEvent(tick=2, type="action_taken", payload={"agent": "a", "action": "pray"}),
            TraceEvent(tick=3, type="action_taken", payload={"agent": "a", "action": "pray"}),
            TraceEvent(tick=4, type="action_taken", payload={"agent": "a", "action": "follow"}),
        ]
        out = render_trace_timeline(events, skip_repeats=True)
        # 3 pray repetitions collapse to 1 line; follow gets its own line
        assert out.count("pray") == 1
        assert "follow" in out

    def test_skip_repeats_false_keeps_all(self):
        events = [
            TraceEvent(tick=1, type="action_taken", payload={"agent": "a", "action": "pray"}),
            TraceEvent(tick=2, type="action_taken", payload={"agent": "a", "action": "pray"}),
        ]
        out = render_trace_timeline(events, skip_repeats=False)
        assert out.count("pray") == 2

    def test_bifurcation_not_collapsed(self):
        events = [
            TraceEvent(tick=100, type="bifurcation_point", payload={"decision_window": [80, 120]}),
            TraceEvent(tick=105, type="action_taken", payload={"agent": "a", "action": "go"}),
            TraceEvent(tick=110, type="action_taken", payload={"agent": "a", "action": "go"}),
        ]
        out = render_trace_timeline(events, skip_repeats=True)
        assert "분기점" in out
        assert out.count("go") == 1  # repeat collapsed

    def test_skip_repeats_per_agent(self):
        """agent A의 pray 반복은 B의 action이 중간에 와도 묶여야 한다."""
        events = [
            TraceEvent(tick=1, type="action_taken", payload={"agent": "a", "action": "pray"}),
            TraceEvent(tick=1, type="action_taken", payload={"agent": "b", "action": "walk"}),
            TraceEvent(tick=2, type="action_taken", payload={"agent": "a", "action": "pray"}),
            TraceEvent(tick=2, type="action_taken", payload={"agent": "b", "action": "walk"}),
            TraceEvent(tick=3, type="action_taken", payload={"agent": "a", "action": "flee"}),
        ]
        out = render_trace_timeline(events, skip_repeats=True)
        # a: pray once (tick 1, 2 collapsed), flee once → 2 lines
        # b: walk once (tick 1, 2 collapsed) → 1 line
        assert out.count("pray") == 1
        assert out.count("walk") == 1
        assert out.count("flee") == 1


class TestNarrateResult:
    def _mock_result(self):
        """Minimal SimulationResult-compatible object."""
        return SimpleNamespace(
            action_histories={
                "peter": [
                    ActionRecord(tick=1, event_id="v", chosen_action="follow",
                                 observable_from=[], visible_signal=None),
                    ActionRecord(tick=2, event_id="v", chosen_action="pray",
                                 observable_from=[], visible_signal=None),
                ],
                "judas": [
                    ActionRecord(tick=1, event_id="v", chosen_action="withdraw",
                                 observable_from=["peter"], visible_signal="유다가 떠났다"),
                ],
            },
            fired_triggers=[],
            fired_events=[],
            checkpoint_results={},
        )

    def test_narrate_returns_string(self):
        result = self._mock_result()
        out = narrate_result(result, player_id="peter")
        assert isinstance(out, str)
        assert len(out) > 0

    def test_narrate_includes_own_actions(self):
        result = self._mock_result()
        out = narrate_result(result, player_id="peter")
        # Peter의 자기 행동 follow, pray 둘 다
        assert "follow" in out
        assert "pray" in out

    def test_narrate_includes_observable_other_action(self):
        result = self._mock_result()
        out = narrate_result(result, player_id="peter")
        # Judas withdraw는 observable_from=['peter']이므로 Peter 시점에서 보임
        assert "유다가 떠났다" in out

    def test_narrate_from_non_observer_excludes_private(self):
        """observable_from=[peter]인 judas action은 caiaphas 시점에서 안 보임."""
        result = self._mock_result()
        out = narrate_result(result, player_id="caiaphas")
        assert "유다가 떠났다" not in out
