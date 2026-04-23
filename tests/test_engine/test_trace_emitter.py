"""Trace event emitter 단위 테스트.

SimulationResult → JSONL trace stream 변환 검증.
"""

import json
import tempfile
from types import SimpleNamespace

from engine.rendering.trace_emitter import (
    TraceEvent,
    collect_trace_events,
    emit_action_events,
    emit_canonical_matches,
    emit_trigger_events,
    write_trace_jsonl,
)
from engine.simulation.checkpoint import ActionRecord, CheckpointResult


class TestTraceEventBasics:
    def test_trace_event_to_json(self):
        ev = TraceEvent(tick=10, type="action_taken", payload={"agent": "p", "action": "x"})
        d = json.loads(ev.to_json())
        assert d["tick"] == 10
        assert d["type"] == "action_taken"
        assert d["payload"]["agent"] == "p"


class TestActionEmitter:
    def test_emit_action_events(self):
        hist = {
            "peter": [
                ActionRecord(
                    tick=5,
                    event_id="voluntary",
                    chosen_action="follow",
                    observable_from=["judas"],
                    visible_signal="Peter는 주변을 살핀다",
                ),
            ],
            "judas": [
                ActionRecord(tick=7, event_id="voluntary", chosen_action="withdraw"),
            ],
        }
        events = list(emit_action_events(hist))
        assert len(events) == 2
        action_types = [e.type for e in events]
        assert all(t == "action_taken" for t in action_types)
        peter_ev = [e for e in events if e.payload["agent"] == "peter"][0]
        assert peter_ev.payload["observable_from"] == ["judas"]
        assert peter_ev.payload["visible_signal"] == "Peter는 주변을 살핀다"
        judas_ev = [e for e in events if e.payload["agent"] == "judas"][0]
        assert judas_ev.payload["observable_from"] == []


class TestTriggerEmitter:
    def test_emit_trigger_events(self):
        triggers = [
            {"trigger_id": "arrest_trigger", "tick": 150, "event_id": "arrest"},
            {"trigger_id": "crowd_spike", "tick": 80, "event_id": "crowd_event"},
        ]
        events = list(emit_trigger_events(triggers))
        assert len(events) == 2
        assert events[0].payload["trigger_id"] == "arrest_trigger"


class TestCanonicalMatchEmitter:
    def test_emit_canonical_matches(self):
        cps = {
            "peter": [
                CheckpointResult(checkpoint_id="deny_3", passed=True, details="ok"),
                CheckpointResult(checkpoint_id="sword", passed=False),
            ],
        }
        events = list(emit_canonical_matches(cps))
        assert len(events) == 2
        deny_ev = [e for e in events if e.payload["checkpoint_id"] == "deny_3"][0]
        assert deny_ev.payload["passed"] is True


class TestCollectAndSort:
    def test_collect_sorted_by_tick(self):
        result = SimpleNamespace(
            action_histories={
                "peter": [
                    ActionRecord(tick=5, event_id="v", chosen_action="a"),
                    ActionRecord(tick=50, event_id="v", chosen_action="b"),
                ]
            },
            fired_triggers=[{"trigger_id": "t1", "tick": 30, "event_id": "e1"}],
            checkpoint_results={},
        )
        events = collect_trace_events(result)
        ticks = [e.tick for e in events]
        assert ticks == sorted(ticks)
        # tick 5 (action), 30 (trigger), 50 (action) 순
        assert ticks == [5, 30, 50]

    def test_write_jsonl(self):
        events = [
            TraceEvent(tick=1, type="action_taken", payload={}),
            TraceEvent(tick=2, type="trigger_fired", payload={}),
        ]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8",
        ) as f:
            path = f.name
        try:
            n = write_trace_jsonl(events, path)
            assert n == 2
            with open(path, encoding="utf-8") as rf:
                lines = rf.readlines()
            assert len(lines) == 2
            assert json.loads(lines[0])["type"] == "action_taken"
        finally:
            import os
            os.unlink(path)


class TestIntegrationWithEmptyResult:
    def test_empty_result_no_events(self):
        result = SimpleNamespace(
            action_histories={},
            fired_triggers=[],
            checkpoint_results={},
        )
        events = collect_trace_events(result)
        assert events == []


class TestSingleAgentResultFormat:
    """Legacy single-agent SimulationResult (action_histories는 list)."""

    def test_single_agent_list_action_history(self):
        """action_histories가 list면 agent_id를 붙여 emit."""
        result = SimpleNamespace(
            action_histories=[
                ActionRecord(tick=1, event_id="v", chosen_action="x"),
                ActionRecord(tick=2, event_id="v", chosen_action="y"),
            ],
            agent_id="solo",
            fired_triggers=[],
            checkpoint_results={},
        )
        events = collect_trace_events(result)
        actions = [e for e in events if e.type == "action_taken"]
        assert len(actions) == 2
        assert all(e.payload["agent"] == "solo" for e in actions)

    def test_single_agent_list_no_agent_id_fallback(self):
        """agent_id 미상 → '_' fallback."""
        result = SimpleNamespace(
            action_histories=[
                ActionRecord(tick=1, event_id="v", chosen_action="x"),
            ],
            fired_triggers=[],
            checkpoint_results={},
        )
        events = collect_trace_events(result)
        actions = [e for e in events if e.type == "action_taken"]
        assert actions[0].payload["agent"] == "_"


class TestBifurcationAttachment:
    def test_bifurcation_reports_emitted(self):
        """collect_trace_events에 bifurcation_reports 전달 → entry 생성."""
        from dataclasses import dataclass

        @dataclass
        class _MockReport:
            decision_window: tuple[int, int] = (30, 50)
            plateau_start: int | None = 60
            max_growth_std_tick: int = 40
            max_growth_std_value: float = 0.9

        result = SimpleNamespace(
            action_histories={}, fired_triggers=[], checkpoint_results={},
        )
        events = collect_trace_events(result, bifurcation_reports=[_MockReport()])
        bif = [e for e in events if e.type == "bifurcation_point"]
        assert len(bif) == 1
        assert bif[0].payload["decision_window"] == [30, 50]
