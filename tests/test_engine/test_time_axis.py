"""Absolute time axis utilities 검증 (v1.2 Iter 22).

reviewer (ChatGPT) 지적 대응:
    phase-variable tick scale 환경에서는 tick이 phase마다 단위가 다름.
    장기 분석은 absolute hours 기준으로만 유효해야 함.

이 테스트는 engine/simulation/time_axis.py의 함수들을
다양한 phase 구성에서 검증한다.
"""

import pytest

from engine.core.state import (
    AgentState,
    DomainState,
    EmotionalState,
    PhysicalState,
    SlowState,
)
from engine.simulation.time_axis import (
    TimePoint,
    convert_phase_boundaries_to_hours,
    extract_field_trajectory_absolute,
    hours_to_days,
    hours_to_years,
    ticks_to_absolute_hours,
)


def _state(agent_id: str, fear: float, tick: int = 0) -> AgentState:
    return AgentState(
        agent_id=agent_id,
        tick=tick,
        physical=PhysicalState(),
        emotions=EmotionalState(fear=fear),
        slow_state=SlowState(),
        domain_state=DomainState(),
    )


@pytest.fixture
def three_phase_boundaries() -> list[dict]:
    """세 phase: 2h/tick (10 tick) + 24h/tick (5 tick) + 2h/tick (8 tick)."""
    return [
        {"phase_id": "p1", "start_tick": 0, "end_tick": 10, "tick_scale_hours": 2.0},
        {"phase_id": "p2", "start_tick": 10, "end_tick": 15, "tick_scale_hours": 24.0},
        {"phase_id": "p3", "start_tick": 15, "end_tick": 23, "tick_scale_hours": 2.0},
    ]


class TestTicksToAbsoluteHours:
    def test_first_phase_tick_zero(self, three_phase_boundaries):
        assert ticks_to_absolute_hours(0, "p1", three_phase_boundaries) == 0.0

    def test_first_phase_local_tick(self, three_phase_boundaries):
        # 5 * 2.0 = 10 hours
        assert ticks_to_absolute_hours(5, "p1", three_phase_boundaries) == 10.0

    def test_second_phase_start(self, three_phase_boundaries):
        # p1 전부 (10 * 2 = 20 hours) + 0 = 20
        assert ticks_to_absolute_hours(0, "p2", three_phase_boundaries) == 20.0

    def test_second_phase_middle(self, three_phase_boundaries):
        # 20 (p1 total) + 3 * 24 = 92 hours
        assert ticks_to_absolute_hours(3, "p2", three_phase_boundaries) == 92.0

    def test_third_phase_local_tick(self, three_phase_boundaries):
        # 20 (p1) + 5*24 (p2 total=120) + 2*2 = 144
        assert ticks_to_absolute_hours(2, "p3", three_phase_boundaries) == 144.0

    def test_unknown_phase_raises(self, three_phase_boundaries):
        with pytest.raises(ValueError, match="not in boundaries"):
            ticks_to_absolute_hours(0, "does_not_exist", three_phase_boundaries)


class TestExtractFieldTrajectory:
    def test_single_phase_extraction(self, three_phase_boundaries):
        snaps = {
            "p1": {"alpha": {0: _state("alpha", 1.0), 3: _state("alpha", 2.5)}},
        }
        points = extract_field_trajectory_absolute(
            snaps, three_phase_boundaries, "alpha", "emotions.fear",
        )
        assert len(points) == 2
        assert points[0].hours == 0.0
        assert points[0].value == 1.0
        assert points[1].hours == 6.0  # 3 * 2h
        assert points[1].value == 2.5

    def test_multi_phase_sorted_by_hours(self, three_phase_boundaries):
        snaps = {
            "p3": {"alpha": {0: _state("alpha", 9.0)}},
            "p1": {"alpha": {0: _state("alpha", 1.0)}},
            "p2": {"alpha": {2: _state("alpha", 5.0)}},
        }
        points = extract_field_trajectory_absolute(
            snaps, three_phase_boundaries, "alpha", "emotions.fear",
        )
        assert [p.hours for p in points] == sorted(p.hours for p in points)
        assert points[0].value == 1.0
        assert points[-1].phase_id == "p3"

    def test_missing_agent_returns_empty(self, three_phase_boundaries):
        snaps = {"p1": {"other": {0: _state("other", 1.0)}}}
        points = extract_field_trajectory_absolute(
            snaps, three_phase_boundaries, "alpha", "emotions.fear",
        )
        assert points == []

    def test_non_numeric_field_skipped(self, three_phase_boundaries):
        snaps = {"p1": {"alpha": {0: _state("alpha", 1.0)}}}
        # agent_id 는 string이라 skip됨
        points = extract_field_trajectory_absolute(
            snaps, three_phase_boundaries, "alpha", "agent_id",
        )
        assert points == []


class TestConvertPhaseBoundariesToHours:
    def test_cumulative_hours(self, three_phase_boundaries):
        result = convert_phase_boundaries_to_hours(three_phase_boundaries)
        assert result[0]["start_hours"] == 0.0
        assert result[0]["end_hours"] == 20.0
        assert result[0]["duration_hours"] == 20.0

        assert result[1]["start_hours"] == 20.0
        assert result[1]["end_hours"] == 140.0  # 20 + 120
        assert result[1]["duration_hours"] == 120.0

        assert result[2]["start_hours"] == 140.0
        assert result[2]["end_hours"] == 156.0  # 140 + 16
        assert result[2]["duration_hours"] == 16.0

    def test_preserves_original_fields(self, three_phase_boundaries):
        result = convert_phase_boundaries_to_hours(three_phase_boundaries)
        for orig, new in zip(three_phase_boundaries, result):
            for key in orig:
                assert new[key] == orig[key]


class TestHoursConversion:
    def test_hours_to_days(self):
        assert hours_to_days(24.0) == 1.0
        assert hours_to_days(48.0) == 2.0
        assert hours_to_days(0.0) == 0.0

    def test_hours_to_years(self):
        # 1 year = 24 * 365.25 hours
        assert abs(hours_to_years(24.0 * 365.25) - 1.0) < 1e-9
        assert hours_to_years(0.0) == 0.0


class TestTimePointDataclass:
    def test_construction(self):
        p = TimePoint(hours=10.0, value=5.0, phase_id="p1", local_tick=3)
        assert p.hours == 10.0
        assert p.value == 5.0
        assert p.phase_id == "p1"
        assert p.local_tick == 3
