"""Content-level Inhibitor + Amplifier 조합 (v1.2 Iter 31).

Gemini reviewer 지적: "3년 모델에서 환멸이 쌓이다가도 '기적 목격'이나
'가르침'을 통해 감쇄되는 Inhibitor Rule이 필수. 그렇지 않으면 모든
시뮬레이션이 1년 차에 조기 배반으로 종료됨."

이 테스트는 content-level composition을 증명:
1. `FieldAmplificationRule` — Judas.messiah_expectation 기반 disillusionment 드리프트
   (정치적 해방 기대가 충족되지 않으면 점진적 누적).
2. `FieldAttenuationRule` (inhibitor) — Peter.emotions.awe >= 5.0이면 감쇄
   (베드로가 목격한 기적이 유다 집단의 기대감을 잠시 유지시켜 환멸 둔화).
3. 두 rule 조합 vs 단독 amplifier 비교:
   inhibitor가 있으면 동일 시간에 disillusionment 누적이 감소해야 함.

engine/ 는 인물 비종속이므로 이 조합은 content 수준 (test + 나중에
behavior_profile에서 선언 가능)에서만 정의된다.
"""

from pathlib import Path

import pytest

from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.phase import Phase, PhaseExitCondition
from engine.core.state import AgentState, EmotionalState
from engine.core.world import SimulationConfig
from engine.io.loader import load_agent_state, register_domain_type
from engine.rules.base import RuleEngine
from engine.rules.inhibitor import FieldAmplificationRule, FieldAttenuationRule
from engine.simulation.phased_world import PhasedSimulationWorld

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


@pytest.fixture(scope="module")
def _setup_domain():
    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
    return None


def _peter_with_awe(awe: float) -> AgentState:
    peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
    return peter.model_copy(update={"emotions": EmotionalState(awe=awe)})


def _phase(tick_scale_hours: float, max_tick: int) -> Phase:
    return Phase(
        phase_id="galilean",
        agents_active=["peter", "judas"],
        tick_scale_hours=tick_scale_hours,
        exit_condition=PhaseExitCondition(max_tick=max_tick),
    )


def _amplifier_rule() -> FieldAmplificationRule:
    """Judas.messiah_expectation >= 6 이면 disillusionment 누적."""
    return FieldAmplificationRule(
        subject_agent_id="judas",
        target_field_path="domain_state.disillusionment",
        trigger_agent_id="judas",
        trigger_field_path="domain_state.messiah_expectation",
        trigger_threshold=6.0,
        amplification_per_hour=0.01,
        max_target_value=10.0,
    )


def _inhibitor_rule() -> FieldAttenuationRule:
    """Peter.emotions.awe >= 5.0 이면 Judas disillusionment 감쇄."""
    return FieldAttenuationRule(
        subject_agent_id="judas",
        target_field_path="domain_state.disillusionment",
        trigger_agent_id="peter",
        trigger_field_path="emotions.awe",
        trigger_threshold=5.0,
        attenuation_per_hour=0.008,
        min_target_value=0.0,
    )


def _run(peter_awe: float, rules: RuleEngine, tick_scale_hours: float, max_tick: int):
    peter = _peter_with_awe(peter_awe)
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    config = SimulationConfig(
        initial_state=peter,
        initial_states=[peter, judas],
        max_tick=1000,
        state_noise_scale=0.0,
        phases=[_phase(tick_scale_hours, max_tick)],
    )
    world = PhasedSimulationWorld(config, rules)
    return world.run(seed=0)


class TestAmplifierAloneAccumulates:
    def test_disillusionment_grows_without_inhibitor(self, _setup_domain):
        """Peter.awe=0 (기적 없음), amplifier만 → disillusionment 누적."""
        rules = RuleEngine([_amplifier_rule()])
        # 24h/tick × 30 tick = 720h
        result = _run(peter_awe=0.0, rules=rules, tick_scale_hours=24.0, max_tick=30)
        judas_final = result.final_states["judas"]
        # 초기 3.0, 720h × 0.01/h = +7.2 → 10.0 cap
        assert judas_final.domain_state.disillusionment == 10.0


class TestInhibitorReducesAccumulation:
    def test_peter_awe_high_limits_growth(self, _setup_domain):
        """Peter.awe=8 (기적 목격 중), amp+inhibitor → disillusionment 성장 감속."""
        rules = RuleEngine([_amplifier_rule(), _inhibitor_rule()])
        result = _run(peter_awe=8.0, rules=rules, tick_scale_hours=24.0, max_tick=30)
        judas_final = result.final_states["judas"]
        # 순증가: (0.01 - 0.008) × 720 = +1.44 → 3.0 + 1.44 = 4.44
        assert abs(judas_final.domain_state.disillusionment - 4.44) < 1e-6

    def test_inhibitor_noop_when_awe_below_threshold(self, _setup_domain):
        """Peter.awe=3 (< 5 threshold) → inhibitor 미작동, amplifier만 효과."""
        rules = RuleEngine([_amplifier_rule(), _inhibitor_rule()])
        result = _run(peter_awe=3.0, rules=rules, tick_scale_hours=24.0, max_tick=30)
        judas_final = result.final_states["judas"]
        # amplifier만: 3.0 + 7.2 = 10.0 cap
        assert judas_final.domain_state.disillusionment == 10.0


class TestInhibitorWithDenseTickScale:
    """2h/tick (dense) 에서도 동일 per-hour rate 해석 — Iter 22 time_axis 원칙."""

    def test_same_total_hours_same_effect_dense(self, _setup_domain):
        """2h/tick × 360 tick = 720h, inhibitor 효과 동일."""
        rules = RuleEngine([_amplifier_rule(), _inhibitor_rule()])
        result_dense = _run(
            peter_awe=8.0, rules=rules, tick_scale_hours=2.0, max_tick=360,
        )
        result_sparse = _run(
            peter_awe=8.0, rules=rules, tick_scale_hours=24.0, max_tick=30,
        )
        # 두 경로 모두 720h, 동일 per-hour rate → 동일 결과 (state_noise=0)
        d1 = result_dense.final_states["judas"].domain_state.disillusionment
        d2 = result_sparse.final_states["judas"].domain_state.disillusionment
        assert abs(d1 - d2) < 1e-6


class TestPreventsEarlyBetrayalMechanism:
    """Gemini 경고 시나리오: 억제 없이 1년 차 조기 한계 vs 억제 있으면 bounded."""

    def test_without_inhibitor_saturates_quickly(self, _setup_domain):
        """720h 동안 amplifier만 → disillusionment cap 10에 도달."""
        rules = RuleEngine([_amplifier_rule()])
        result = _run(peter_awe=8.0, rules=rules, tick_scale_hours=24.0, max_tick=30)
        # Peter awe 무관 (inhibitor 없음), amplifier만 ~10 cap
        assert result.final_states["judas"].domain_state.disillusionment >= 9.5

    def test_with_inhibitor_stays_below_saturation(self, _setup_domain):
        """동일 720h에서 inhibitor 있으면 disillusionment < 5."""
        rules = RuleEngine([_amplifier_rule(), _inhibitor_rule()])
        result = _run(peter_awe=8.0, rules=rules, tick_scale_hours=24.0, max_tick=30)
        # 순증가만 남아 5 미만
        assert result.final_states["judas"].domain_state.disillusionment < 5.0
