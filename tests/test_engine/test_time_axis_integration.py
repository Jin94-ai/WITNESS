"""time_axis integration with PhasedSimulationWorld (v1.2 Iter 25).

unit test (test_time_axis.py)는 합성 dict를 사용.
여기서는 실제 PhasedSimulationWorld 실행 결과를 받아 absolute-hours
trajectory로 변환하고 시나리오 의미와 일관되는지 검증한다.

reviewer 지적: "phase-variable tick에서는 tick이 단위가 다르므로 장기
분석은 반드시 hours since call 기준이어야 한다." — 이 통합 테스트는
그 원칙이 end-to-end로 작동함을 증명.
"""

from pathlib import Path

import pytest

from content.peter.domain_faith import FaithJourneyState
from engine.core.phase import Phase, PhaseExitCondition, PhaseHandoffSpec
from engine.core.world import SimulationConfig
from engine.io.loader import load_agent_state, register_domain_type
from engine.rules.base import RuleEngine
from engine.rules.emotional import (
    ConfusionRule,
    FearResponseRule,
    GriefRule,
    HopeRule,
    LoveRule,
)
from engine.rules.temporal import HomeostasisRule
from engine.simulation.phased_world import (
    PhasedMultiAgentResult,
    PhasedSimulationWorld,
)
from engine.simulation.time_axis import (
    convert_phase_boundaries_to_hours,
    hours_to_days,
)

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ])


@pytest.fixture(scope="module")
def _setup_domain():
    register_domain_type("faith_journey", FaithJourneyState)
    return None


def _two_phase_config(peter_state):
    return SimulationConfig(
        initial_state=peter_state,
        initial_states=[peter_state],
        max_tick=500,
        state_noise_scale=0.0,
        phases=[
            Phase(
                phase_id="01_calling",
                agents_active=["peter"],
                tick_scale_hours=2.0,
                exit_condition=PhaseExitCondition(max_tick=84),
                handoff_to_next=PhaseHandoffSpec(),
                canonical_events_path=str(
                    CONTENT / "peter" / "phases" / "01_calling" / "canonical_events.json",
                ),
            ),
            Phase(
                phase_id="02_galilean",
                agents_active=["peter"],
                tick_scale_hours=24.0,
                exit_condition=PhaseExitCondition(max_tick=30),
            ),
        ],
    )


class TestAbsoluteTrajectoryE2E:
    def test_extract_trajectory_from_live_run(self, _setup_domain):
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        config = _two_phase_config(peter)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)
        assert isinstance(result, PhasedMultiAgentResult)

        traj = result.extract_absolute_trajectory("peter", "emotions.awe")
        # phase 1 84 tick + phase 2 30 tick = 114 tick 가량
        assert len(traj) > 0

        # hours는 단조증가
        hours = [p.hours for p in traj]
        assert hours == sorted(hours)

        # phase 1 경계가 168h (=84 tick × 2h), phase 2 시작 >= 168h
        p2_points = [p for p in traj if p.phase_id == "02_galilean"]
        if p2_points:
            assert p2_points[0].hours >= 168.0

    def test_tick_scale_diff_visible_in_hours(self, _setup_domain):
        """phase 1 dense (2h/tick) vs phase 2 sparse (24h/tick) — hours 간격 분포 차이."""
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        config = _two_phase_config(peter)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        traj = result.extract_absolute_trajectory("peter", "emotions.awe")
        p1 = [p for p in traj if p.phase_id == "01_calling"]
        p2 = [p for p in traj if p.phase_id == "02_galilean"]
        if len(p1) >= 2 and len(p2) >= 2:
            p1_gap = p1[1].hours - p1[0].hours
            p2_gap = p2[1].hours - p2[0].hours
            # phase 2 간격이 더 넓어야 (24 > 2)
            assert p2_gap > p1_gap

    def test_phase_boundaries_hours_consistency(self, _setup_domain):
        """convert_phase_boundaries_to_hours가 실제 실행 결과와 일치."""
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        config = _two_phase_config(peter)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        enriched = convert_phase_boundaries_to_hours(result.phase_boundaries)
        assert enriched[0]["start_hours"] == 0.0
        assert enriched[0]["end_hours"] == 168.0  # 84 × 2
        assert enriched[1]["start_hours"] == 168.0
        assert enriched[1]["end_hours"] == 168.0 + 30 * 24.0
        # 총 기간 = 888h ≈ 37 days
        total_hours = enriched[-1]["end_hours"]
        assert abs(hours_to_days(total_hours) - 37.0) < 0.1

    def test_phase_hours_table_convenience_method(self, _setup_domain):
        """Iter 47: result.phase_hours_table()이 convert_phase_boundaries_to_hours와 동일 결과."""
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        config = _two_phase_config(peter)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        direct = convert_phase_boundaries_to_hours(result.phase_boundaries)
        via_method = result.phase_hours_table()
        assert direct == via_method

    def test_missing_agent_returns_empty(self, _setup_domain):
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        config = _two_phase_config(peter)
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)
        traj = result.extract_absolute_trajectory("nonexistent", "emotions.awe")
        assert traj == []

    def test_single_phase_legacy_mode_no_absolute_method(self, _setup_domain):
        """phases=None legacy 모드는 PhasedMultiAgentResult 아님 (기존 MultiAgentResult)."""
        peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
        config = SimulationConfig(
            initial_state=peter,
            initial_states=[peter],
            max_tick=20,
            state_noise_scale=0.0,
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)
        # legacy는 plain MultiAgentResult, 새 method 없음
        assert not isinstance(result, PhasedMultiAgentResult)
        assert not hasattr(result, "extract_absolute_trajectory")
