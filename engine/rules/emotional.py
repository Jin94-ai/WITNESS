"""감정 상태 전이 규칙.

핵심: 교차 효과 (cross-effects).
fatigue>7 AND fear>6 -> confusion 증폭 (겟세마네 졸음 + 체포 공포 -> 부인 조건).
grief>8 AND hope<3 -> confusion 급등 (십자가 후 상태).
"""

from __future__ import annotations

from engine.core.state import AgentState, clamp
from engine.rules.base import RuleContext


class FearResponseRule:
    """두려움 반응 규칙.

    - 위협 이벤트에 fear 증가
    - 안전 환경에서 서서히 감소 (항상성)
    - 피로가 높으면 fear 증폭 (피로-공포 교차 효과)
    - 고립 시 fear 추가 증가
    """

    def __init__(
        self,
        decay_rate: float = 0.02,
        fatigue_amplifier: float = 0.3,
        fatigue_threshold: float = 7.0,
        isolation_bonus: float = 0.1,
    ) -> None:
        self.decay_rate = decay_rate
        self.fatigue_amplifier = fatigue_amplifier
        self.fatigue_threshold = fatigue_threshold
        self.isolation_bonus = isolation_bonus

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        fear = state.emotions.fear

        # 이벤트가 없으면 자연 감쇠
        if not context.active_events:
            fear = clamp(fear - self.decay_rate * context.delta_tick)
        else:
            # 피로-공포 교차 효과: 피로가 높으면 공포 증폭
            if state.physical.fatigue > self.fatigue_threshold:
                excess = state.physical.fatigue - self.fatigue_threshold
                fear = clamp(fear + excess * self.fatigue_amplifier * 0.1)

        # 고립 효과: 동료 관계가 약하면 추가 공포
        has_companions = any(
            r.trust > 5.0 for r in state.relationships.values()
        )
        if not has_companions and fear > 3.0:
            fear = clamp(fear + self.isolation_bonus * context.delta_tick)

        new_emotions = state.emotions.model_copy(update={"fear": fear})
        return state.model_copy(update={"emotions": new_emotions})


class HopeRule:
    """희망 규칙. 긍정 이벤트에 증가, 연속 부정에 감소, 자연 항상성."""

    def __init__(self, decay_rate: float = 0.01, baseline: float = 4.0) -> None:
        self.decay_rate = decay_rate
        self.baseline = baseline

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        hope = state.emotions.hope

        # 높은 grief가 hope를 억제
        if state.emotions.grief > 7.0:
            hope = clamp(hope - 0.05 * context.delta_tick)

        # 항상성: baseline으로 복귀 (극단에서 중앙으로)
        diff = self.baseline - hope
        hope = clamp(hope + diff * self.decay_rate * context.delta_tick)

        new_emotions = state.emotions.model_copy(update={"hope": hope})
        return state.model_copy(update={"emotions": new_emotions})


class GriefRule:
    """슬픔 규칙. 상실 이벤트에 급등, 시간에 따라 완만히 감소."""

    def __init__(self, decay_rate: float = 0.01) -> None:
        self.decay_rate = decay_rate

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        grief = state.emotions.grief

        # 자연 감쇠 (아주 느림)
        if grief > 0:
            grief = clamp(grief - self.decay_rate * context.delta_tick)

        new_emotions = state.emotions.model_copy(update={"grief": grief})
        return state.model_copy(update={"emotions": new_emotions})


class ConfusionRule:
    """혼란 규칙. 핵심 교차 효과를 구현한다.

    - 피로>7 AND 공포>6 → 혼란 증폭 (부인의 조건)
    - 슬픔>8 AND 희망<3 → 혼란 급등 (십자가 후)
    - 기본 항상성으로 서서히 감소
    """

    def __init__(
        self,
        fatigue_fear_threshold: tuple[float, float] = (7.0, 6.0),
        cross_effect_rate: float = 0.15,
        grief_hope_rate: float = 0.1,
        decay_rate: float = 0.02,
    ) -> None:
        self.fatigue_threshold = fatigue_fear_threshold[0]
        self.fear_threshold = fatigue_fear_threshold[1]
        self.cross_effect_rate = cross_effect_rate
        self.grief_hope_rate = grief_hope_rate
        self.decay_rate = decay_rate

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        confusion = state.emotions.confusion

        # 교차 효과 1: 피로 + 공포 → 혼란
        if (
            state.physical.fatigue > self.fatigue_threshold
            and state.emotions.fear > self.fear_threshold
        ):
            excess_fatigue = state.physical.fatigue - self.fatigue_threshold
            excess_fear = state.emotions.fear - self.fear_threshold
            confusion = clamp(
                confusion + excess_fatigue * excess_fear * self.cross_effect_rate * 0.1
            )

        # 교차 효과 2: 슬픔 + 절망 → 혼란
        if state.emotions.grief > 8.0 and state.emotions.hope < 3.0:
            confusion = clamp(confusion + self.grief_hope_rate * context.delta_tick)

        # 항상성: 서서히 감소
        if confusion > 0 and not context.active_events:
            confusion = clamp(confusion - self.decay_rate * context.delta_tick)

        new_emotions = state.emotions.model_copy(update={"confusion": confusion})
        return state.model_copy(update={"emotions": new_emotions})


class LoveRule:
    """사랑 규칙. 관계 상호작용에 따라 변동. 기본 항상성."""

    def __init__(self, baseline: float = 5.0, drift_rate: float = 0.005) -> None:
        self.baseline = baseline
        self.drift_rate = drift_rate

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        love = state.emotions.love

        # 항상성
        diff = self.baseline - love
        love = clamp(love + diff * self.drift_rate * context.delta_tick)

        new_emotions = state.emotions.model_copy(update={"love": love})
        return state.model_copy(update={"emotions": new_emotions})
