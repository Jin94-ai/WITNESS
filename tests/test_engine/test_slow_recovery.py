"""SlowStateFieldRecoveryRule 검증 (v1.2 Iter 23).

reviewer 피드백: field-specific slow state 회복 — moral_injury, trust_scar,
identity_shift은 조건부 회복; event_trauma는 자연 회복 없음 (PTSD).
기본값 모두 0 = zero-effect (기존 v0.7 행동 보존).
"""

from __future__ import annotations

import random

import pytest

from engine.core.state import (
    AgentState,
    DomainState,
    EmotionalState,
    PhysicalState,
    Relationship,
    SlowState,
)
from engine.rules.base import RuleContext
from engine.rules.slow_recovery import SlowStateFieldRecoveryRule


def _make_state(
    *,
    hope: float = 5.0,
    love: float = 5.0,
    fear: float = 2.0,
    moral_injury: float = 0.0,
    trust_scar: float = 0.0,
    identity_shift: float = 0.0,
    event_trauma: float = 0.0,
    trust_with: dict[str, float] | None = None,
) -> AgentState:
    rels = {}
    if trust_with:
        for tid, t in trust_with.items():
            rels[tid] = Relationship(target_id=tid, trust=t)
    return AgentState(
        agent_id="test",
        tick=0,
        physical=PhysicalState(),
        emotions=EmotionalState(hope=hope, love=love, fear=fear),
        slow_state=SlowState(
            moral_injury=moral_injury,
            trust_scar=trust_scar,
            identity_shift=identity_shift,
            event_trauma=event_trauma,
        ),
        relationships=rels,
        domain_state=DomainState(),
    )


def _ctx(dt_hours: float = 2.0) -> RuleContext:
    return RuleContext(tick=0, delta_tick=1, dt_hours=dt_hours, rng=random.Random(0))


class TestDefaultZeroEffect:
    """기본 rate=0이면 기존 시나리오 무영향."""

    def test_default_rule_no_change_with_high_injury(self):
        rule = SlowStateFieldRecoveryRule()
        state = _make_state(moral_injury=5.0, hope=10.0)
        result = rule.apply(state, _ctx())
        assert result.slow_state.moral_injury == 5.0

    def test_default_rule_no_change_with_trust_scar(self):
        rule = SlowStateFieldRecoveryRule()
        state = _make_state(trust_scar=3.0, trust_with={"a": 9.0})
        result = rule.apply(state, _ctx())
        assert result.slow_state.trust_scar == 3.0

    def test_default_rule_no_change_with_identity_shift(self):
        rule = SlowStateFieldRecoveryRule()
        state = _make_state(identity_shift=-5.0, hope=10.0, love=10.0)
        result = rule.apply(state, _ctx())
        assert result.slow_state.identity_shift == -5.0


class TestMoralInjuryRecovery:
    def test_recovers_when_hope_high(self):
        rule = SlowStateFieldRecoveryRule(moral_injury_rate_per_hour=0.1)
        state = _make_state(moral_injury=5.0, hope=8.0)
        # dt=2.0, rate=0.1 → step=0.2, new=4.8
        result = rule.apply(state, _ctx(dt_hours=2.0))
        assert abs(result.slow_state.moral_injury - 4.8) < 1e-9

    def test_no_recovery_when_hope_low(self):
        rule = SlowStateFieldRecoveryRule(
            moral_injury_rate_per_hour=0.1, hope_threshold=7.0,
        )
        state = _make_state(moral_injury=5.0, hope=5.0)
        result = rule.apply(state, _ctx(dt_hours=2.0))
        assert result.slow_state.moral_injury == 5.0

    def test_floors_at_zero(self):
        rule = SlowStateFieldRecoveryRule(moral_injury_rate_per_hour=100.0)
        state = _make_state(moral_injury=0.5, hope=10.0)
        result = rule.apply(state, _ctx(dt_hours=2.0))
        assert result.slow_state.moral_injury == 0.0

    def test_no_change_when_already_zero(self):
        rule = SlowStateFieldRecoveryRule(moral_injury_rate_per_hour=0.1)
        state = _make_state(moral_injury=0.0, hope=10.0)
        result = rule.apply(state, _ctx())
        assert result.slow_state.moral_injury == 0.0

    def test_dt_scales_recovery(self):
        rule = SlowStateFieldRecoveryRule(moral_injury_rate_per_hour=0.1)
        # dt=24 → step=2.4, new=5-2.4=2.6
        state = _make_state(moral_injury=5.0, hope=10.0)
        result = rule.apply(state, _ctx(dt_hours=24.0))
        assert abs(result.slow_state.moral_injury - 2.6) < 1e-9


class TestTrustScarRecovery:
    def test_recovers_when_trust_avg_high(self):
        rule = SlowStateFieldRecoveryRule(
            trust_scar_rate_per_hour=0.05, required_trust_avg=6.0,
        )
        state = _make_state(
            trust_scar=4.0, trust_with={"a": 8.0, "b": 7.0},
        )
        # dt=2.0 → step=0.1 → new=3.9
        result = rule.apply(state, _ctx(dt_hours=2.0))
        assert abs(result.slow_state.trust_scar - 3.9) < 1e-9

    def test_no_recovery_when_avg_below_threshold(self):
        rule = SlowStateFieldRecoveryRule(
            trust_scar_rate_per_hour=0.05, required_trust_avg=6.0,
        )
        state = _make_state(trust_scar=4.0, trust_with={"a": 3.0})
        result = rule.apply(state, _ctx())
        assert result.slow_state.trust_scar == 4.0

    def test_no_recovery_when_no_relationships(self):
        rule = SlowStateFieldRecoveryRule(trust_scar_rate_per_hour=0.05)
        state = _make_state(trust_scar=4.0)
        result = rule.apply(state, _ctx())
        assert result.slow_state.trust_scar == 4.0


class TestIdentityShiftRecovery:
    def test_negative_identity_recovers_toward_zero(self):
        rule = SlowStateFieldRecoveryRule(
            identity_shift_recovery_rate_per_hour=0.05,
        )
        # hope=8 >= 7, love=7 >= 6 → recovery
        state = _make_state(identity_shift=-4.0, hope=8.0, love=7.0)
        # dt=2.0 → step=0.1 → new=-3.9
        result = rule.apply(state, _ctx(dt_hours=2.0))
        assert abs(result.slow_state.identity_shift - (-3.9)) < 1e-9

    def test_does_not_overshoot_zero(self):
        rule = SlowStateFieldRecoveryRule(
            identity_shift_recovery_rate_per_hour=100.0,
        )
        state = _make_state(identity_shift=-0.5, hope=10.0, love=10.0)
        result = rule.apply(state, _ctx(dt_hours=2.0))
        # step huge, but capped at 0
        assert result.slow_state.identity_shift == 0.0

    def test_positive_identity_untouched(self):
        rule = SlowStateFieldRecoveryRule(
            identity_shift_recovery_rate_per_hour=0.05,
        )
        # positive identity → rule only recovers negatives
        state = _make_state(identity_shift=5.0, hope=10.0, love=10.0)
        result = rule.apply(state, _ctx())
        assert result.slow_state.identity_shift == 5.0

    def test_no_recovery_without_hope_and_love(self):
        rule = SlowStateFieldRecoveryRule(
            identity_shift_recovery_rate_per_hour=0.05,
            hope_threshold=7.0, love_threshold=6.0,
        )
        # hope ok, love low → no recovery
        state = _make_state(identity_shift=-4.0, hope=8.0, love=4.0)
        result = rule.apply(state, _ctx())
        assert result.slow_state.identity_shift == -4.0


class TestEventTraumaDefaultNoRecovery:
    """기본값(event_trauma_rate_per_hour=0)에서 PTSD 원칙 유지."""

    def test_event_trauma_unchanged_under_ideal_conditions(self):
        """event_trauma rate 지정 안 하면 다른 field가 회복돼도 event_trauma 그대로."""
        rule = SlowStateFieldRecoveryRule(
            moral_injury_rate_per_hour=0.1,
            trust_scar_rate_per_hour=0.1,
            identity_shift_recovery_rate_per_hour=0.1,
        )
        state = _make_state(
            event_trauma=7.0, hope=10.0, love=10.0,
            trust_with={"a": 10.0},
        )
        result = rule.apply(state, _ctx(dt_hours=24.0))
        assert result.slow_state.event_trauma == 7.0


class TestEventTraumaOptInRecovery:
    """양수 rate 주면 hope+관계 동시 충족 시만 decay (ChatGPT: 완전 0 decay 아님)."""

    def test_decay_when_both_hope_and_trust_high(self):
        rule = SlowStateFieldRecoveryRule(
            event_trauma_rate_per_hour=0.01,
        )
        state = _make_state(
            event_trauma=5.0, hope=8.0,
            trust_with={"a": 8.0},
        )
        # dt=2h, rate=0.01/h → step=0.02 → 4.98
        result = rule.apply(state, _ctx(dt_hours=2.0))
        assert abs(result.slow_state.event_trauma - 4.98) < 1e-9

    def test_no_decay_when_hope_low(self):
        rule = SlowStateFieldRecoveryRule(event_trauma_rate_per_hour=0.01)
        state = _make_state(
            event_trauma=5.0, hope=3.0,  # below threshold
            trust_with={"a": 8.0},
        )
        result = rule.apply(state, _ctx())
        assert result.slow_state.event_trauma == 5.0

    def test_no_decay_when_trust_low(self):
        rule = SlowStateFieldRecoveryRule(event_trauma_rate_per_hour=0.01)
        state = _make_state(
            event_trauma=5.0, hope=9.0,
            trust_with={"a": 3.0},  # below required_trust_avg
        )
        result = rule.apply(state, _ctx())
        assert result.slow_state.event_trauma == 5.0

    def test_no_decay_when_no_relationships(self):
        """관계 자체가 없으면 event_trauma 절대 낮아지지 않음."""
        rule = SlowStateFieldRecoveryRule(event_trauma_rate_per_hour=0.01)
        state = _make_state(event_trauma=5.0, hope=10.0)  # no trust_with
        result = rule.apply(state, _ctx())
        assert result.slow_state.event_trauma == 5.0

    def test_floors_at_zero(self):
        rule = SlowStateFieldRecoveryRule(event_trauma_rate_per_hour=100.0)
        state = _make_state(
            event_trauma=0.5, hope=10.0,
            trust_with={"a": 10.0},
        )
        result = rule.apply(state, _ctx(dt_hours=2.0))
        assert result.slow_state.event_trauma == 0.0

    def test_negative_rate_raises(self):
        import pytest
        with pytest.raises(ValueError, match="event_trauma"):
            SlowStateFieldRecoveryRule(event_trauma_rate_per_hour=-0.01)


class TestValidation:
    def test_negative_moral_rate_raises(self):
        with pytest.raises(ValueError, match="moral_injury"):
            SlowStateFieldRecoveryRule(moral_injury_rate_per_hour=-0.1)

    def test_negative_trust_rate_raises(self):
        with pytest.raises(ValueError, match="trust_scar"):
            SlowStateFieldRecoveryRule(trust_scar_rate_per_hour=-0.01)

    def test_negative_identity_rate_raises(self):
        with pytest.raises(ValueError, match="identity_shift"):
            SlowStateFieldRecoveryRule(identity_shift_recovery_rate_per_hour=-0.5)
