"""Derived variable calculator (v3 Phase 2 v2 §1.1).

Derived 등급:
    Active 변수들의 함수로 자동 계산. 독립 상태 아님. 저장 안 함.
    매 tick 필요 시 계산.
    예상 수: 10-20개 (v2 §1.1)

Per v2 §16 함정 11: "Pressure 별도 Active로 등록 금지. Derived로만."
Pressure는 engine/world/pressure.py에서 계산 (외부 변수 Layer C).
Person-side Derived는 여기서 Active 조합으로 계산.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from engine.person.state_v3 import ActiveState


@dataclass
class DerivedVariable:
    """A computed-from-Active variable. Not stored in state."""

    name: str
    description: str
    compute: Callable[[ActiveState], float]


# =============================================================================
# Derived formula registry
# =============================================================================

def _sum_target_aware(values: dict[str, float]) -> float:
    """Sum values across all targets."""
    if not values:
        return 0.0
    return sum(values.values())


def _max_target_aware(values: dict[str, float], default: float = 0.0) -> float:
    if not values:
        return default
    return max(values.values())


def _stress(state: ActiveState) -> float:
    """스트레스 = 두려움 + 혼란 + 피로 (가중 평균)."""
    return float(0.4 * state.fear + 0.3 * state.confusion + 0.3 * state.fatigue)


def _distress(state: ActiveState) -> float:
    """비통 = 슬픔 + 최대 죄책감 + 외상."""
    guilt_max = _max_target_aware(state.guilt)
    return float(0.4 * state.grief + 0.3 * guilt_max + 0.3 * state.trauma)


def _peace(state: ActiveState) -> float:
    """평안 = 소망 + 활력 - 스트레스."""
    st = _stress(state)
    return max(0.0, min(10.0, 0.5 * state.hope + 0.5 * state.vitality - 0.3 * st))


def _inner_turmoil(state: ActiveState) -> float:
    """내적 혼란 = 의심 + 혼란 + (총 수치 평균)."""
    shame_sum = _sum_target_aware(state.shame)
    n_shame = max(1, len(state.shame))
    avg_shame = shame_sum / n_shame
    return float(0.4 * state.doubt + 0.3 * state.confusion + 0.3 * avg_shame)


def _loyalty_composite(state: ActiveState) -> float:
    """전체 loyalty 강도 (모든 target 평균)."""
    if not state.loyalty:
        return 0.0
    return sum(state.loyalty.values()) / len(state.loyalty)


def _isolation_index(state: ActiveState) -> float:
    """고립 지수 = 1 - 평균 belonging."""
    if not state.belonging:
        return 10.0
    avg_belonging = sum(state.belonging.values()) / len(state.belonging)
    return max(0.0, 10.0 - avg_belonging)


def _repentance_depth(state: ActiveState) -> float:
    """회개 깊이 = guilt + grief + trauma (높을수록 깊은 회개)."""
    guilt_max = _max_target_aware(state.guilt)
    return float((guilt_max + state.grief + state.trauma) / 3)


def _faith_stage_tag(state: ActiveState) -> str:
    """Derived faith_stage_tag (Dynamics Step 1).

    faith_stage는 서사 압축 레이블이며 Active 아님. love/guilt/trust/shame/hope/resolve
    등 Active 조합으로 매 tick 태그. 관찰자 사후 분류용.

    반환값은 FaithStage Literal 중 하나의 문자열.
    """
    love_pf = state.love.get("primary_figure", 0.0)
    guilt_pf = state.guilt.get("primary_figure", 0.0)
    trust_pf = state.trust.get("primary_figure", 0.0)
    shame_max = _max_target_aware(state.shame)
    hope = state.hope
    resolve = state.resolve

    # foundation: 사역/권위 단계 (resolve 매우 높음, guilt 낮음, trust 최대)
    if resolve >= 9.0 and trust_pf >= 9.0 and guilt_pf <= 0.5 and hope >= 8.5:
        return "foundation"
    # shepherd: 돌봄 단계 — restored 위 상위 단계 (더 엄격)
    if (love_pf >= 9.5 and resolve >= 8.5
            and guilt_pf <= 1.0 and hope >= 8.0):
        return "shepherd"
    # restored: guilt 일부 해소 + hope 회복 + love 유지 + resolve 회복
    if (guilt_pf <= 3.0 and hope >= 6.0 and love_pf >= 8.0
            and shame_max <= 4.0 and resolve >= 7.0):
        return "restored"
    # failed: guilt_pf 매우 높음 + love_pf 유지 (떠나지 않음) + shame 상승
    if guilt_pf >= 6.0 and love_pf >= 5.0:
        return "failed"
    # tested: shame 또는 doubt 상승, 아직 failed 도달 전
    if (shame_max >= 3.0 or state.doubt >= 4.0) and guilt_pf < 6.0:
        return "tested"
    # follower: love/loyalty 있고 아직 시련 이전
    if love_pf >= 5.0 or trust_pf >= 5.0:
        return "follower"
    return "none"


def _restoration_readiness(state: ActiveState) -> float:
    """회복 준비도 = hope + derived_faith_stage_numeric - guilt_max.

    faith_stage_numeric: none=0, follower=1, tested=2, failed=3, restored=4, shepherd=5, foundation=6
    """
    stage_numeric = {
        "none": 0, "follower": 1, "tested": 2, "failed": 3,
        "restored": 4, "shepherd": 5, "foundation": 6,
    }.get(_faith_stage_tag(state), 0)
    guilt_max = _max_target_aware(state.guilt)
    raw = state.hope + stage_numeric * 1.5 - guilt_max * 0.8
    return max(0.0, min(10.0, raw))


DERIVED_VARIABLES: list[DerivedVariable] = [
    DerivedVariable("stress", "두려움+혼란+피로 조합", _stress),
    DerivedVariable("distress", "슬픔+죄책+외상 조합", _distress),
    DerivedVariable("peace", "평안 = 소망+활력-스트레스", _peace),
    DerivedVariable("inner_turmoil", "의심+혼란+평균수치", _inner_turmoil),
    DerivedVariable("loyalty_composite", "전체 loyalty target 평균", _loyalty_composite),
    DerivedVariable("isolation_index", "고립 지수 (1-belonging 평균)", _isolation_index),
    DerivedVariable("repentance_depth", "회개 깊이 (guilt+grief+trauma)", _repentance_depth),
    DerivedVariable("restoration_readiness", "회복 준비도", _restoration_readiness),
]


# faith_stage_tag is a string-valued Derived -- separate from the
# numeric DERIVED_VARIABLES registry but still Derived per Dynamics Step 1.

def faith_stage_tag(state: ActiveState) -> str:
    """Public API: compute faith_stage tag from ActiveState."""
    return _faith_stage_tag(state)


# =============================================================================
# Calculator API
# =============================================================================

class DerivedCalculator:
    """Compute all Derived variables from an ActiveState snapshot."""

    def __init__(
        self,
        derived: list[DerivedVariable] | None = None,
    ) -> None:
        self._derived = list(derived) if derived is not None else list(DERIVED_VARIABLES)

    def compute_all(self, state: ActiveState) -> dict[str, float]:
        return {d.name: d.compute(state) for d in self._derived}

    def compute_one(self, state: ActiveState, name: str) -> float:
        for d in self._derived:
            if d.name == name:
                return d.compute(state)
        raise KeyError(f"No derived variable named {name}")

    def names(self) -> list[str]:
        return [d.name for d in self._derived]

    def n_derived(self) -> int:
        return len(self._derived)
