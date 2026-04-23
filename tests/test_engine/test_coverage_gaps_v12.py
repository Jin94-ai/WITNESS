"""v1.2 모듈 coverage gap 커버 (Iter 36).

이전 Iter에서 누락된 edge case:
- engine/simulation/time_axis.py::extract_final_states_at_phase_boundaries (untested)
- engine/rules/inhibitor.py::FieldAmplificationRule non-numeric / missing-agent 경로
- engine/rules/inhibitor.py::FieldAttenuationRule non-numeric 경로
"""

from __future__ import annotations

import random
from types import SimpleNamespace

from engine.core.state import AgentState, EmotionalState
from engine.rules.base import RuleContext
from engine.rules.inhibitor import FieldAmplificationRule, FieldAttenuationRule
from engine.simulation.time_axis import (
    TimePoint,
    extract_final_states_at_phase_boundaries,
)


def _agent(aid: str, awe: float = 0.0, fear: float = 0.0) -> AgentState:
    return AgentState(
        agent_id=aid,
        emotions=EmotionalState(awe=awe, fear=fear),
    )


def _ctx(all_agents: dict | None = None) -> RuleContext:
    return RuleContext(
        tick=0, delta_tick=1, dt_hours=2.0,
        rng=random.Random(0), all_agents=all_agents or {},
    )


class TestAttenuationEdgeCases:
    def test_trigger_field_not_numeric_skips(self):
        """trigger_field가 string (예: agent_id)이면 no-op."""
        rule = FieldAttenuationRule(
            subject_agent_id="sub", target_field_path="emotions.fear",
            trigger_agent_id="src", trigger_field_path="agent_id",
            trigger_threshold=0.0, attenuation_per_hour=0.1,
        )
        sub = _agent("sub", fear=5.0)
        src = _agent("src", awe=10.0)
        result = rule.apply(sub, _ctx({"src": src}))
        assert result.emotions.fear == 5.0

    def test_target_field_not_numeric_skips(self):
        """target field가 numeric이 아니면 no-op (e.g., agent_id)."""
        rule = FieldAttenuationRule(
            subject_agent_id="sub", target_field_path="agent_id",
            trigger_agent_id="src", trigger_field_path="emotions.awe",
            trigger_threshold=0.0, attenuation_per_hour=0.1,
        )
        sub = _agent("sub")
        src = _agent("src", awe=10.0)
        result = rule.apply(sub, _ctx({"src": src}))
        # agent_id 여전히 string "sub"
        assert result.agent_id == "sub"


class TestAmplificationEdgeCases:
    def test_trigger_agent_missing(self):
        rule = FieldAmplificationRule(
            subject_agent_id="sub", target_field_path="emotions.hope",
            trigger_agent_id="ghost", trigger_field_path="emotions.awe",
            trigger_threshold=5.0, amplification_per_hour=0.1,
        )
        sub = _agent("sub")
        result = rule.apply(sub, _ctx({}))  # ghost 없음
        assert result.emotions.hope == sub.emotions.hope

    def test_trigger_field_not_numeric(self):
        rule = FieldAmplificationRule(
            subject_agent_id="sub", target_field_path="emotions.hope",
            trigger_agent_id="src", trigger_field_path="agent_id",
            trigger_threshold=0.0, amplification_per_hour=0.1,
        )
        sub = _agent("sub")
        src = _agent("src")
        result = rule.apply(sub, _ctx({"src": src}))
        assert result.emotions.hope == sub.emotions.hope

    def test_trigger_below_threshold(self):
        rule = FieldAmplificationRule(
            subject_agent_id="sub", target_field_path="emotions.hope",
            trigger_agent_id="src", trigger_field_path="emotions.awe",
            trigger_threshold=5.0, amplification_per_hour=0.1,
        )
        sub = _agent("sub")
        src = _agent("src", awe=2.0)  # below 5.0
        result = rule.apply(sub, _ctx({"src": src}))
        assert result.emotions.hope == sub.emotions.hope

    def test_target_field_not_numeric(self):
        rule = FieldAmplificationRule(
            subject_agent_id="sub", target_field_path="agent_id",
            trigger_agent_id="src", trigger_field_path="emotions.awe",
            trigger_threshold=0.0, amplification_per_hour=0.1,
        )
        sub = _agent("sub")
        src = _agent("src", awe=10.0)
        result = rule.apply(sub, _ctx({"src": src}))
        assert result.agent_id == "sub"


class TestExtractFinalStatesAtBoundaries:
    def test_simple_two_phase_extraction(self):
        """두 phase, 각 종료 시점 awe 추출."""
        phase_boundaries = [
            {"phase_id": "p1", "start_tick": 0, "end_tick": 10, "tick_scale_hours": 2.0},
            {"phase_id": "p2", "start_tick": 10, "end_tick": 15, "tick_scale_hours": 24.0},
        ]
        p1_result = SimpleNamespace(
            final_states={"alpha": _agent("alpha", awe=4.0)},
        )
        p2_result = SimpleNamespace(
            final_states={"alpha": _agent("alpha", awe=8.0)},
        )
        per_phase = {"p1": p1_result, "p2": p2_result}
        points = extract_final_states_at_phase_boundaries(
            per_phase, phase_boundaries, "alpha", "emotions.awe",
        )
        assert len(points) == 2
        # p1 끝 = 20h
        assert points[0].hours == 20.0
        assert points[0].value == 4.0
        assert points[0].phase_id == "p1"
        # p2 끝 = 20 + 5*24 = 140h
        assert points[1].hours == 140.0
        assert points[1].value == 8.0

    def test_missing_phase_result_skipped(self):
        """per_phase_results에 없는 phase는 조용히 skip."""
        phase_boundaries = [
            {"phase_id": "p1", "start_tick": 0, "end_tick": 10, "tick_scale_hours": 2.0},
            {"phase_id": "p2", "start_tick": 10, "end_tick": 15, "tick_scale_hours": 24.0},
        ]
        per_phase = {
            "p1": SimpleNamespace(final_states={"alpha": _agent("alpha", awe=3.0)}),
            # p2 missing
        }
        points = extract_final_states_at_phase_boundaries(
            per_phase, phase_boundaries, "alpha", "emotions.awe",
        )
        assert len(points) == 1
        assert points[0].phase_id == "p1"

    def test_missing_agent_skipped(self):
        """해당 phase final_states에 agent 없으면 skip."""
        phase_boundaries = [
            {"phase_id": "p1", "start_tick": 0, "end_tick": 10, "tick_scale_hours": 2.0},
        ]
        per_phase = {
            "p1": SimpleNamespace(final_states={"other": _agent("other")}),
        }
        points = extract_final_states_at_phase_boundaries(
            per_phase, phase_boundaries, "alpha", "emotions.awe",
        )
        assert points == []

    def test_non_numeric_field_skipped(self):
        phase_boundaries = [
            {"phase_id": "p1", "start_tick": 0, "end_tick": 10, "tick_scale_hours": 2.0},
        ]
        per_phase = {
            "p1": SimpleNamespace(final_states={"alpha": _agent("alpha")}),
        }
        # agent_id는 string
        points = extract_final_states_at_phase_boundaries(
            per_phase, phase_boundaries, "alpha", "agent_id",
        )
        assert points == []

    def test_returns_timepoint_objects(self):
        phase_boundaries = [
            {"phase_id": "p1", "start_tick": 0, "end_tick": 5, "tick_scale_hours": 2.0},
        ]
        per_phase = {
            "p1": SimpleNamespace(final_states={"alpha": _agent("alpha", awe=7.5)}),
        }
        points = extract_final_states_at_phase_boundaries(
            per_phase, phase_boundaries, "alpha", "emotions.awe",
        )
        assert len(points) == 1
        assert isinstance(points[0], TimePoint)
        assert points[0].local_tick == 5  # phase 길이
