"""Field-specific slow state recovery (v1.2 Iter 23).

reviewer 피드백 대응:
    "moral_injury / event_trauma는 단조 증가만 — 50일 scenario에 맞춤.
    3년 '소명-회복-재실패' 반복을 표현하려면 field-specific 회복 필요.
    canonical intervention = reparameterization shock (완전 회복 ≠)."

설계 원칙:
1. **기본값 전부 0 (opt-in)**: 기존 v0.7 시나리오는 이 rule을 추가해도 동작 불변.
   content config에서 명시적으로 rate를 줘야 활성화.
2. **dt_hours 기반**: rate는 per-hour 기준. 매 tick 적용 시 × context.dt_hours.
3. **Field별 서로 다른 의미**:
   - moral_injury: hope ≥ threshold 일 때만 회복 (자기 용서는 희망이 있어야).
   - trust_scar: 평균 관계 trust ≥ threshold 일 때 회복 (신뢰 회복은 관계 재건).
   - identity_shift (음수): hope+love 동시 threshold일 때 0 방향으로 회복.
   - event_trauma: **자연 회복 없음** (PTSD 모델, intervention-only).
4. **Canonical intervention과 독립**: 이 rule은 "slow mending". intervention은
   state에 shock을 가할 뿐 이 rule의 rate에 영향 없음.
5. **인물 비종속**: engine/rules/ 에 위치 — 모든 agent 적용 가능.

적용 예시 (content/peter에서):
    RuleEngine([
        ...,
        SlowStateFieldRecoveryRule(
            moral_injury_rate_per_hour=0.002,   # 500시간에 1.0 복원
            trust_scar_rate_per_hour=0.001,
            identity_shift_recovery_rate_per_hour=0.0005,
        ),
    ])

기본 생성자 (모든 rate=0)는 zero-effect sentinel.
"""

from __future__ import annotations

from engine.core.state import AgentState, clamp
from engine.rules.base import RuleContext


class SlowStateFieldRecoveryRule:
    """Field-specific slow state 회복 rule (opt-in, dt-aware).

    기본 생성자로 만든 인스턴스는 zero-effect. 각 rate를 양수로 설정해야
    해당 field에 회복이 적용된다.

    event_trauma 정책 (외부 리뷰 수용):
    - 기본값 0.0 = PTSD 원칙(Gemini) — canonical intervention만으로 낮춤
    - 양수 rate = "거의 0이지만 완전 0은 아닌 baseline decay"(ChatGPT)
      단, hope ≥ threshold 이고 관계 안정(평균 trust ≥ required_trust_avg)인 경우만 작동
      → 단독 시간 경과로는 절대 낮아지지 않음 (신학적 사건 버튼화 방지)
    """

    def __init__(
        self,
        moral_injury_rate_per_hour: float = 0.0,
        trust_scar_rate_per_hour: float = 0.0,
        identity_shift_recovery_rate_per_hour: float = 0.0,
        event_trauma_rate_per_hour: float = 0.0,
        hope_threshold: float = 7.0,
        love_threshold: float = 6.0,
        required_trust_avg: float = 6.0,
    ) -> None:
        if moral_injury_rate_per_hour < 0.0:
            raise ValueError("moral_injury_rate_per_hour must be >= 0")
        if trust_scar_rate_per_hour < 0.0:
            raise ValueError("trust_scar_rate_per_hour must be >= 0")
        if identity_shift_recovery_rate_per_hour < 0.0:
            raise ValueError("identity_shift_recovery_rate_per_hour must be >= 0")
        if event_trauma_rate_per_hour < 0.0:
            raise ValueError("event_trauma_rate_per_hour must be >= 0")

        self.moral_injury_rate_per_hour = moral_injury_rate_per_hour
        self.trust_scar_rate_per_hour = trust_scar_rate_per_hour
        self.identity_shift_recovery_rate_per_hour = (
            identity_shift_recovery_rate_per_hour
        )
        self.event_trauma_rate_per_hour = event_trauma_rate_per_hour
        self.hope_threshold = hope_threshold
        self.love_threshold = love_threshold
        self.required_trust_avg = required_trust_avg

    def _avg_trust(self, state: AgentState) -> float:
        if not state.relationships:
            return 0.0
        trusts = [r.trust for r in state.relationships.values()]
        return sum(trusts) / len(trusts)

    def apply(self, state: AgentState, context: RuleContext) -> AgentState:
        # 모두 rate=0이면 early exit (기본 zero-effect 보장)
        if (
            self.moral_injury_rate_per_hour == 0.0
            and self.trust_scar_rate_per_hour == 0.0
            and self.identity_shift_recovery_rate_per_hour == 0.0
            and self.event_trauma_rate_per_hour == 0.0
        ):
            return state

        slow = state.slow_state
        updates: dict[str, float] = {}
        dt = context.dt_hours

        # moral_injury: hope 충분할 때만 회복
        if (
            self.moral_injury_rate_per_hour > 0.0
            and state.emotions.hope >= self.hope_threshold
            and slow.moral_injury > 0.0
        ):
            new_val = slow.moral_injury - self.moral_injury_rate_per_hour * dt
            updates["moral_injury"] = clamp(new_val, 0.0, 10.0)

        # trust_scar: 평균 관계 trust 충분할 때만 회복
        if (
            self.trust_scar_rate_per_hour > 0.0
            and self._avg_trust(state) >= self.required_trust_avg
            and slow.trust_scar > 0.0
        ):
            new_val = slow.trust_scar - self.trust_scar_rate_per_hour * dt
            updates["trust_scar"] = clamp(new_val, 0.0, 10.0)

        # identity_shift: 음수일 때 0 방향으로만 회복 (hope+love 동시)
        if (
            self.identity_shift_recovery_rate_per_hour > 0.0
            and slow.identity_shift < 0.0
            and state.emotions.hope >= self.hope_threshold
            and state.emotions.love >= self.love_threshold
        ):
            step = self.identity_shift_recovery_rate_per_hour * dt
            new_val = min(slow.identity_shift + step, 0.0)
            updates["identity_shift"] = clamp(new_val, -10.0, 10.0)

        # event_trauma: 기본 0 (PTSD 원칙), 양수 rate일 때만 제한적 decay.
        # 조건: hope 높고 + 관계 안정 동시 충족 시만 baseline decay.
        # 단독 시간 경과로는 절대 낮아지지 않는다 — "사건에 의해서만 재구성되지만,
        # 지속적 안정/희망 환경에서는 매우 느리게 완화 가능" 모델.
        if (
            self.event_trauma_rate_per_hour > 0.0
            and state.emotions.hope >= self.hope_threshold
            and self._avg_trust(state) >= self.required_trust_avg
            and slow.event_trauma > 0.0
        ):
            new_val = slow.event_trauma - self.event_trauma_rate_per_hour * dt
            updates["event_trauma"] = clamp(new_val, 0.0, 10.0)

        if updates:
            new_slow = slow.model_copy(update=updates)
            return state.model_copy(update={"slow_state": new_slow})
        return state
