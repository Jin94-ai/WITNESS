"""State transition engine (Dynamics Step 4).

27 direct edges (v2 §6) 중 우선순위 **20개를 1차 구현**. 나머지 7개는 후순위.

5 카테고리 × 4 edges = 20:
    A. 외부 이벤트 → 내부 상태 (가장 중요)
    B. 가시적 고통/상실 → 정서
    C. 내부 상태 간 전이
    D. 관계/소속 → 감정
    E. 신성 이벤트 → 정서

Rule #1: 모든 edge는 event_id/primitive 이름 기반. 인물-특정 이름 없음.
Rule #12: StateTransitionEngine은 압력→상태 갱신만. 행동 결정 안 함.
Rule #15-18: 기존 ActiveState 구조 유지. 새 변수 추가 없음.

Grief 최소 3 경로 (ChatGPT 권고):
    1) event-induced: primary_figure_suffering_visible, peer_failure, ally_departure
    2) state-induced: guilt_max high + (helplessness = fear + confusion)
    3) action-induced expression: weep / withdraw_in_fear (이 쪽은 loop.py의
       action-consequences 섹션에서 처리)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from engine.person.state_v3 import ActiveState
from engine.world.primitives import PrimitiveState


# ---------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------

def _clip01_to_10(v: float) -> float:
    return max(0.0, min(10.0, v))


def _bump(current: float, delta: float) -> float:
    return _clip01_to_10(current + delta)


def _bump_target(
    d: dict[str, float], key: str, delta: float,
) -> None:
    d[key] = _clip01_to_10(d.get(key, 0.0) + delta)


def _max_target(d: dict[str, float]) -> float:
    return max(d.values()) if d else 0.0


# ---------------------------------------------------------------------
# StateTransitionEngine
# ---------------------------------------------------------------------

@dataclass
class TransitionContext:
    """Tick-level transition context."""

    events_this_tick: list[str] = field(default_factory=list)
    last_action: str | None = None


class StateTransitionEngine:
    """Apply 20 direct edges each tick.

    Call order:
        engine.apply(state, primitives, ctx)

    Events are identified by event_id string; primitives are read from
    PrimitiveState snapshot (post-event apply). Action-induced edges
    (grief path 3, shame path) are still in loop.py for now to keep
    action→state coupling explicit.
    """

    # Edge strengths (Dynamics §6.4):
    #   '+'   = +0.3~0.5  per event-tick
    #   '++'  = +0.5~1.0
    #   '-'   = -0.3~0.5
    #   '--'  = -0.5~1.0
    # Small passive decay each tick to prevent permanent saturation.

    # --------- passive per-tick decay ---------
    DECAY_FEAR = 0.10
    DECAY_CONFUSION = 0.08
    DECAY_SHAME_SELF = 0.05
    DECAY_ANGER = 0.10

    def apply(
        self,
        state: ActiveState,
        primitives: PrimitiveState,
        ctx: TransitionContext,
    ) -> None:
        events = set(ctx.events_this_tick)

        # ==============================================================
        # Category A — 외부 이벤트 → 내부 상태 (4 edges)
        # ==============================================================
        # A1. accusation_visible (primitive high) → fear+, shame[crowd]+, confusion+
        if primitives.accusation_visibility > 0.3:
            scale = primitives.accusation_visibility
            state.fear = _bump(state.fear, 0.5 * scale)
            _bump_target(state.shame, "crowd", 0.4 * scale)
            state.confusion = _bump(state.confusion, 0.3 * scale)

        # A2. public_exposure (public_visibility primitive high) → shame+, fear+
        if primitives.public_visibility > 0.3:
            scale = primitives.public_visibility
            _bump_target(state.shame, "crowd", 0.3 * scale)
            state.fear = _bump(state.fear, 0.3 * scale)

        # A3. guard_approaches event → fear++, anger+
        if "guard_approaches" in events:
            state.fear = _bump(state.fear, 0.8)
            state.anger = _bump(state.anger, 0.4)

        # A4. arrest_warrant-like (proxy: weapon_drawn_nearby) → fear++, confusion+
        if "weapon_drawn_nearby" in events:
            state.fear = _bump(state.fear, 0.7)
            state.confusion = _bump(state.confusion, 0.4)

        # ==============================================================
        # Category B — 가시적 고통/상실 → 정서 (4 edges)
        # ==============================================================
        # B1. primary_figure_suffering_visible → grief++, awe+, loyalty[primary_figure]+
        if primitives.proximity_of_suffering > 0.3 and primitives.primary_figure_visible:
            scale = primitives.proximity_of_suffering
            state.grief = _bump(state.grief, 0.8 * scale)
            state.awe = _bump(state.awe, 0.3 * scale)
            _bump_target(state.loyalty, "primary_figure", 0.3 * scale)

        # B2. peer_failure (betrayal_witnessed) → grief+, shame[self]+
        if "betrayal_witnessed" in events:
            state.grief = _bump(state.grief, 0.5)
            _bump_target(state.shame, "self", 0.3)

        # B3. ally_departure → belonging-, fear+
        if "ally_departure" in events:
            for k in list(state.belonging.keys()):
                state.belonging[k] = _clip01_to_10(state.belonging[k] - 0.5)
            state.fear = _bump(state.fear, 0.3)

        # B4. prolonged_suffering_context (proximity high + religious_context low)
        #     → grief+, doubt+
        if (primitives.proximity_of_suffering > 0.5
                and primitives.religious_context < 0.2):
            state.grief = _bump(state.grief, 0.4)
            state.doubt = _bump(state.doubt, 0.3)

        # ==============================================================
        # Category C — 내부 상태 간 전이 (4 edges)
        # ==============================================================
        # C1. guilt_max high → withdrawal tendency (confusion+, grief+, doubt+)
        guilt_max = _max_target(state.guilt)
        if guilt_max > 5.0:
            state.grief = _bump(state.grief, 0.3)
            state.doubt = _bump(state.doubt, 0.2)
            state.confusion = _bump(state.confusion, 0.2)

        # C2. shame_max high → resolve-, trauma+
        shame_max = _max_target(state.shame)
        if shame_max > 5.0:
            state.resolve = _clip01_to_10(state.resolve - 0.3)
            state.trauma = _bump(state.trauma, 0.15)

        # C3. fear high + guilt high (helplessness) → confusion+, grief+
        if state.fear > 5.0 and guilt_max > 4.0:
            state.confusion = _bump(state.confusion, 0.3)
            state.grief = _bump(state.grief, 0.4)  # grief path 2 (state-induced)

        # C4. hope drops when doubt rises sharply
        if state.doubt > 6.0:
            state.hope = _clip01_to_10(state.hope - 0.3)

        # ==============================================================
        # Category D — 관계/소속 → 감정 (4 edges)
        # ==============================================================
        # D1. ally_proximity high → belonging+, fear-
        if primitives.ally_proximity > 0.5:
            scale = primitives.ally_proximity
            for k in list(state.belonging.keys()):
                state.belonging[k] = _clip01_to_10(state.belonging[k] + 0.1 * scale)
            state.fear = _clip01_to_10(state.fear - 0.15 * scale)

        # D2. group_cohesion high → belonging+, isolation ↓ (derived, so skip)
        if primitives.group_cohesion > 0.5:
            scale = primitives.group_cohesion
            for k in list(state.belonging.keys()):
                state.belonging[k] = _clip01_to_10(state.belonging[k] + 0.08 * scale)

        # D3. primary_figure_presence → awe+, loyalty maintained
        if primitives.primary_figure_presence > 0.3:
            scale = primitives.primary_figure_presence
            state.awe = _bump(state.awe, 0.2 * scale)
            _bump_target(state.loyalty, "primary_figure", 0.1 * scale)

        # D4. isolation (no allies AND no group) → confusion+, hope-
        if primitives.ally_proximity < 0.2 and primitives.group_cohesion < 0.3:
            state.confusion = _bump(state.confusion, 0.2)
            state.hope = _clip01_to_10(state.hope - 0.15)

        # ==============================================================
        # Category E — 신성 이벤트 → 정서 (4 edges)
        # ==============================================================
        # E1. sacred_meal → awe+, peace-related (derived), trust+
        if "sacred_meal" in events:
            state.awe = _bump(state.awe, 0.5)
            _bump_target(state.trust, "primary_figure", 0.3)

        # E2. prayer_invitation → awe+, hope+
        if "prayer_invitation" in events:
            state.awe = _bump(state.awe, 0.4)
            state.hope = _bump(state.hope, 0.3)

        # E3. miracle_witnessed → awe++, trust[primary_figure]+, hope+
        if "miracle_witnessed" in events:
            state.awe = _bump(state.awe, 0.8)
            _bump_target(state.trust, "primary_figure", 0.5)
            state.hope = _bump(state.hope, 0.4)

        # E4. forgiveness_offered → hope+, guilt[primary_figure]-, resolve+
        if "forgiveness_offered" in events:
            state.hope = _bump(state.hope, 0.5)
            _bump_target(state.guilt, "primary_figure", -0.5)
            state.resolve = _bump(state.resolve, 0.3)

        # ==============================================================
        # Category F — Recovery edges (Dynamics Step 8 / D1 extension)
        # ==============================================================
        # v2 §6 원안의 27 edges 중 남은 7개는 recovery 경로로 정의
        # (ChatGPT "slow state 회복 메커니즘" 지적 반영).
        # 이 edges는 negative-side 동역학의 자연 상쇄 역할.

        # F1. hope high → fear 감쇄 (인지적 확신이 공포 완화)
        if state.hope > 6.0:
            state.fear = _clip01_to_10(state.fear - 0.1 * (state.hope - 6.0) / 4.0)

        # F2. awe high → grief 감쇄 (경외가 애도를 감싸 안음, 미미)
        if state.awe > 7.0:
            state.grief = _clip01_to_10(state.grief - 0.05 * (state.awe - 7.0) / 3.0)

        # F3. trust[primary_figure] high → confusion 감쇄
        trust_pf = state.trust.get("primary_figure", 0.0)
        if trust_pf > 6.0:
            state.confusion = _clip01_to_10(
                state.confusion - 0.15 * (trust_pf - 6.0) / 4.0,
            )

        # F4. belonging high → shame[crowd] 감쇄 (소속감이 공적 수치 완충)
        if state.belonging:
            avg_belong = sum(state.belonging.values()) / len(state.belonging)
            if avg_belong > 5.0:
                if "crowd" in state.shame:
                    state.shame["crowd"] = _clip01_to_10(
                        state.shame["crowd"] - 0.1 * (avg_belong - 5.0) / 5.0,
                    )

        # F5. loyalty maintained high → resolve 점진 회복
        loyalty_pf = state.loyalty.get("primary_figure", 0.0)
        if loyalty_pf > 7.0 and state.resolve < 8.0:
            state.resolve = _clip01_to_10(state.resolve + 0.05)

        # F6. guilt low + hope present → grief 자연 감쇄 (guilt 해소 이후만)
        if guilt_max < 2.0 and state.hope > 5.0 and state.grief > 1.0:
            state.grief = _clip01_to_10(state.grief - 0.08)

        # F7. vitality high → confusion 감쇄 (신체 건강이 인지 명료화)
        if state.vitality > 6.0 and state.confusion > 3.0:
            state.confusion = _clip01_to_10(
                state.confusion - 0.06 * (state.vitality - 6.0) / 4.0,
            )

        # ==============================================================
        # Passive decay (small, keeps acute spikes from persisting forever)
        # ==============================================================
        state.fear = _clip01_to_10(state.fear - self.DECAY_FEAR)
        state.confusion = _clip01_to_10(state.confusion - self.DECAY_CONFUSION)
        state.anger = _clip01_to_10(state.anger - self.DECAY_ANGER)
        if "self" in state.shame:
            state.shame["self"] = _clip01_to_10(
                state.shame["self"] - self.DECAY_SHAME_SELF,
            )
