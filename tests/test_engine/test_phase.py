"""v1.2 Phase dataclass unit tests.

phase-linked continuous life architecture의 핵심 자료구조 검증.
"""

import pytest

from engine.core.phase import (
    FieldMapping,
    Phase,
    PhaseExitCondition,
    PhaseHandoffSpec,
)


class TestPhaseExitCondition:
    def test_max_tick_triggers(self):
        cond = PhaseExitCondition(max_tick=100)
        assert cond.is_met(tick=100, fired_trigger_ids=[], states={}) is True
        assert cond.is_met(tick=99, fired_trigger_ids=[], states={}) is False

    def test_trigger_id_triggers(self):
        cond = PhaseExitCondition(triggered_by="calling_accepted")
        assert cond.is_met(0, ["calling_accepted"], {}) is True
        assert cond.is_met(0, ["other_trigger"], {}) is False

    def test_state_predicate(self):
        cond = PhaseExitCondition(
            state_predicate=lambda s: s.get("peter", {}).get("faith", 0) > 5.0,
        )
        assert cond.is_met(0, [], {"peter": {"faith": 6.0}}) is True
        assert cond.is_met(0, [], {"peter": {"faith": 4.0}}) is False

    def test_multiple_conditions_any_triggers(self):
        cond = PhaseExitCondition(
            max_tick=1000,
            triggered_by="arrest",
            state_predicate=lambda s: False,
        )
        # tick 500, arrest fired → trigger wins
        assert cond.is_met(500, ["arrest"], {}) is True
        # tick 500, no trigger, predicate false → no exit
        assert cond.is_met(500, [], {}) is False
        # tick 1000 reached → max_tick wins
        assert cond.is_met(1000, [], {}) is True

    def test_predicate_exception_safe(self):
        """predicate가 예외 발생시 False 반환 (phase 계속)."""
        cond = PhaseExitCondition(
            state_predicate=lambda s: 1 / 0,  # ZeroDivisionError
        )
        assert cond.is_met(0, [], {}) is False

    def test_no_conditions_never_triggers(self):
        cond = PhaseExitCondition()
        assert cond.is_met(999999, ["anything"], {"any": "state"}) is False


class TestFieldMapping:
    def test_default_none(self):
        m = FieldMapping("peter", "emotions.fear", "peter", "emotions.fear")
        assert m.default_if_missing is None

    def test_with_default(self):
        m = FieldMapping(
            "peter", "emotions.fear", "peter", "emotions.fear",
            default_if_missing=3.0,
        )
        assert m.default_if_missing == 3.0


class TestPhaseHandoffSpec:
    def test_empty_default(self):
        spec = PhaseHandoffSpec()
        assert spec.mappings == []
        assert spec.carry_all_slow_state is True

    def test_with_mappings(self):
        spec = PhaseHandoffSpec(
            mappings=[
                FieldMapping("peter", "domain_state.obedience_maturity",
                             "peter", "domain_state.obedience_maturity"),
                FieldMapping("peter", "domain_state.jesus_understanding",
                             "peter", "domain_state.jesus_understanding"),
            ]
        )
        assert len(spec.mappings) == 2

    def test_slow_state_default_carry(self):
        """reviewer 피드백: slow state는 irreversible이므로 default carry."""
        spec = PhaseHandoffSpec()
        assert spec.carry_all_slow_state is True


class TestPhaseBasic:
    def test_minimal_phase(self):
        phase = Phase(phase_id="test_phase")
        assert phase.phase_id == "test_phase"
        assert phase.tick_scale_hours == 2.0  # default = v0.5 호환
        assert phase.agents_active is None
        assert phase.handoff_to_next is None
        assert phase.tick_offset == 0

    def test_empty_phase_id_raises(self):
        with pytest.raises(ValueError, match="phase_id must be non-empty"):
            Phase(phase_id="")

    def test_zero_tick_scale_raises(self):
        with pytest.raises(ValueError, match="tick_scale_hours must be > 0"):
            Phase(phase_id="bad", tick_scale_hours=0.0)

    def test_negative_tick_scale_raises(self):
        with pytest.raises(ValueError, match="tick_scale_hours must be > 0"):
            Phase(phase_id="bad", tick_scale_hours=-1.0)

    def test_hours_for_ticks_default(self):
        """기본 2h/tick에서 50 tick = 100시간."""
        phase = Phase(phase_id="x")
        assert phase.hours_for_ticks(50) == 100.0

    def test_hours_for_ticks_sparse(self):
        """24h/tick (일 단위)에서 30 tick = 720시간 = 30일."""
        phase = Phase(phase_id="galilean", tick_scale_hours=24.0)
        assert phase.hours_for_ticks(30) == 720.0
        assert phase.days_for_ticks(30) == 30.0

    def test_phase_with_exit_condition(self):
        phase = Phase(
            phase_id="calling",
            description="Luke 5:1-11 miraculous catch",
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=84),
        )
        assert phase.exit_condition.max_tick == 84
        assert phase.exit_condition.is_met(84, [], {}) is True

    def test_phase_with_handoff(self):
        phase = Phase(
            phase_id="calling",
            handoff_to_next=PhaseHandoffSpec(
                mappings=[
                    FieldMapping("peter", "domain_state.obedience_maturity",
                                 "peter", "domain_state.obedience_maturity"),
                ]
            ),
        )
        assert phase.handoff_to_next is not None
        assert len(phase.handoff_to_next.mappings) == 1


class TestPhaseScalingConsistency:
    """reviewer 지적: tick이 바뀌어도 시간당 비율은 불변이어야 함."""

    def test_same_hours_different_ticks(self):
        """dense phase 84 tick (168h) == sparse phase 7 tick (168h)."""
        dense = Phase(phase_id="dense", tick_scale_hours=2.0)
        sparse = Phase(phase_id="sparse", tick_scale_hours=24.0)
        assert dense.hours_for_ticks(84) == sparse.hours_for_ticks(7)

    def test_days_conversion(self):
        passion_phase = Phase(phase_id="passion", tick_scale_hours=2.0)
        # 500 tick * 2h = 1000h = ~41.67일
        assert 41.0 < passion_phase.days_for_ticks(500) < 42.0
