"""시간 진행 규칙.

v0.3: HomeostasisRule을 조건부 회복으로 재설계.
- fast state(emotions)만 항상성 적용. slow state는 건드리지 않음.
- 감정별 회복 속도 차등 (fear 빠름, grief 느림)
- slow state가 높으면 회복이 느려짐 (상처가 회복을 방해)
"""

from __future__ import annotations

import math

from engine.core.state import AgentState, clamp
from engine.rules.base import RuleContext


# 감정별 회복 속도. grief는 느리고, fear는 빠르다.
_RECOVERY_RATES: dict[str, float] = {
    "fear": 0.006,       # 공포는 비교적 빨리 감소
    "hope": 0.003,       # 희망은 보통
    "grief": 0.001,      # 슬픔은 아주 느리게 감소
    "confusion": 0.004,  # 혼란은 보통~빠름
    "love": 0.002,       # 사랑은 느리게 변화
}

_BASELINES: dict[str, float] = {
    "fear": 3.0,
    "hope": 5.0,
    "grief": 1.0,
    "confusion": 2.0,
    "love": 6.0,
}


class HomeostasisRule:
    """조건부 항상성 규칙.

    fast state(emotions)만 중앙 수렴. slow state는 건드리지 않음.
    slow_state.moral_injury가 높으면 grief/fear 회복이 느려짐.
    고립 상태(관계 trust 낮음)면 hope 회복 안 됨.
    """

    def __init__(
        self,
        rate_scale: float = 1.0,
        slow_state_penalty: float = 0.3,
    ) -> None:
        self.rate_scale = rate_scale
        self.slow_state_penalty = slow_state_penalty

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        emotions = state.emotions
        slow = state.slow_state
        updates: dict[str, float] = {}

        # slow state에 의한 회복 페널티
        injury_factor = 1.0 - min(slow.moral_injury / 10.0 * self.slow_state_penalty, 0.8)
        trauma_factor = 1.0 - min(slow.event_trauma / 10.0 * self.slow_state_penalty, 0.8)

        # 고립 판정: 동료 관계 trust 평균
        trust_values = [r.trust for r in state.relationships.values()]
        avg_trust = sum(trust_values) / len(trust_values) if trust_values else 5.0
        isolation_factor = min(avg_trust / 7.0, 1.0)  # trust 낮으면 회복 느림

        for field in ("fear", "hope", "grief", "confusion", "love"):
            current = getattr(emotions, field)
            baseline = _BASELINES.get(field, 4.0)
            base_rate = _RECOVERY_RATES.get(field, 0.003) * self.rate_scale

            # 조건부 회복 속도
            effective_rate = base_rate
            if field in ("grief", "fear"):
                effective_rate *= injury_factor * trauma_factor
            if field == "hope":
                effective_rate *= isolation_factor

            diff = baseline - current
            new_val = clamp(current + diff * effective_rate * context.delta_tick)
            updates[field] = new_val

        new_emotions = emotions.model_copy(update=updates)
        return state.model_copy(update={"emotions": new_emotions})


class SlowStateRule:
    """Slow state 누적 규칙.

    특정 행동/사건 후 slow_state를 비가역적으로 증가시킨다.
    이 규칙은 이벤트 발동 후에만 의미 있지만, 매 tick 적용해도
    이벤트가 없으면 변화 없도록 설계.
    """

    def __init__(
        self,
        stress_injury: float = 1.5,
        extreme_event_trauma: float = 0.5,
        fear_threshold: float = 8.0,
        grief_threshold: float = 8.0,
    ) -> None:
        self.stress_injury = stress_injury
        self.extreme_event_trauma = extreme_event_trauma
        self.fear_threshold = fear_threshold
        self.grief_threshold = grief_threshold

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        slow = state.slow_state
        updates: dict[str, float | int] = {}

        # 극한 공포 경험 -> event_trauma 누적
        if state.emotions.fear >= self.fear_threshold:
            updates["event_trauma"] = clamp(
                slow.event_trauma + self.extreme_event_trauma * 0.1
            )

        # 극한 슬픔 경험 -> event_trauma 누적
        if state.emotions.grief >= self.grief_threshold:
            updates["event_trauma"] = clamp(
                updates.get("event_trauma", slow.event_trauma)
                + self.extreme_event_trauma * 0.1
            )

        # identity_shift: hope와 fear의 차이에 따라 미세하게 이동
        if state.emotions.hope > 7.0:
            updates["identity_shift"] = clamp(
                slow.identity_shift + 0.01, -10.0, 10.0
            )
        elif state.emotions.fear > 7.0 and state.emotions.hope < 3.0:
            updates["identity_shift"] = clamp(
                slow.identity_shift - 0.01, -10.0, 10.0
            )

        if updates:
            new_slow = slow.model_copy(update=updates)
            return state.model_copy(update={"slow_state": new_slow})
        return state


class HighStressConsequenceRule:
    """극한 스트레스의 slow state 결과. 인물 비종속.

    grief와 fear가 동시에 높을 때 moral_injury가 누적.
    특정 행동 ID에 의존하지 않음 -- 상태 기반으로만 판단.
    """

    def __init__(
        self,
        grief_threshold: float = 5.0,
        fear_threshold: float = 5.0,
        injury_rate: float = 0.3,
    ) -> None:
        self.grief_threshold = grief_threshold
        self.fear_threshold = fear_threshold
        self.injury_rate = injury_rate

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        if not context.active_events:
            return state

        if (
            state.emotions.grief > self.grief_threshold
            and state.emotions.fear > self.fear_threshold
        ):
            slow = state.slow_state
            new_slow = slow.model_copy(update={
                "moral_injury": clamp(slow.moral_injury + self.injury_rate),
            })
            return state.model_copy(update={"slow_state": new_slow})

        return state


class CircadianRule:
    """일주기 규칙. 밤에 피로 증가, 낮에 자연 감소."""

    def __init__(self, night_fatigue_rate: float = 0.08, day_recovery_rate: float = 0.02) -> None:
        self.night_fatigue_rate = night_fatigue_rate
        self.day_recovery_rate = day_recovery_rate

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        hour_phase = (context.tick % 12) / 12.0
        circadian = math.sin(hour_phase * 2 * math.pi)

        fatigue = state.physical.fatigue
        if circadian > 0:
            fatigue = clamp(fatigue + circadian * self.night_fatigue_rate * context.delta_tick)
        else:
            fatigue = clamp(fatigue + circadian * self.day_recovery_rate * context.delta_tick)

        new_physical = state.physical.model_copy(update={"fatigue": fatigue})
        return state.model_copy(update={"physical": new_physical})
