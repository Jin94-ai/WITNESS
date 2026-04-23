"""Action → Event mapper (v3 Phase 2 v2 §5).

v2 §5.2 verbatim:
    금지: person_state → external_state 직접 연결
    허용: action → event → external update

이 모듈은 사람의 행동 (string action_id) 을 Event (engine/world/events.py)
로 변환. EventRegistry가 그 event를 PrimitiveState에 적용.

v2 §5.4: 각 행동이 어떤 이벤트를 유발하는지 + 이벤트가 어떤 primitive를
얼마나 갱신하는지 명시.

Rule #1: action_id strings are scenario-agnostic engine convention.
Content can extend the table.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ActionEventMap:
    """Single row: action → event_id."""
    action_id: str
    triggered_event_id: str
    description: str = ""


# =============================================================================
# Draft mapping -- actions observed from prior Spike 6 BC vocab + canonical
# =============================================================================

ACTION_EVENT_TABLE: list[ActionEventMap] = [
    # --- BC vocab (from peter_bc_v1/v2 action_vocab) ---
    ActionEventMap("deny", "public_denial",
                   "공개 부인 → 고발 가시성 + 공개 노출 증가"),
    ActionEventMap("confess", "public_declaration",
                   "공개 고백 → 권위 주의 + 공개 노출 증가"),
    ActionEventMap("weep", "visible_distress",
                   "통곡 → 공개 노출 감소 (숨어서)"),
    ActionEventMap("pray", "prayer_invitation",
                   "기도 → 종교 맥락 증가"),
    ActionEventMap("withdraw_in_fear", "withdrawal",
                   "두려움으로 물러남 → 동료 근접도 감소"),
    ActionEventMap("follow_closely", "ally_arrival",
                   "가까이 따라감 → 동료 근접 증가"),
    ActionEventMap("follow_at_distance", "withdrawal",
                   "거리두며 따라감 → 근접 감소, 노출 감소"),
    ActionEventMap("draw_sword", "weapon_raised",
                   "칼 뽑음 → 상황 변동성 급증"),
    ActionEventMap("flee", "withdrawal",
                   "도망 → 근접·노출 감소"),
    ActionEventMap("stay_awake", "ally_arrival",
                   "깨어있음 → 동료 근접 유지"),
    ActionEventMap("fall_asleep", "ally_departure",
                   "잠듦 → 동료 근접 이탈 (부재)"),
    ActionEventMap("stay_hiding", "withdrawal",
                   "숨어있음 → 공개 노출 감소"),
    ActionEventMap("run_to_tomb", "ally_arrival",
                   "무덤으로 달려감 → 동료(여인들)와 근접"),
    ActionEventMap("assert_loyalty", "public_declaration",
                   "충성 선언 → 공개 선언"),
    ActionEventMap("discuss_with_disciples", "ally_arrival",
                   "제자들과 토론 → 동료 근접"),
    # --- canonical event-triggered actions ---
    ActionEventMap("join_crowd", "public_declaration",
                   "군중 합류 → 공개 노출"),
    ActionEventMap("watch_quietly", "withdrawal",
                   "조용히 지켜봄 → 노출 감소"),
    ActionEventMap("resist_washing", "public_declaration",
                   "세족 거부 → 공개 선언"),
    ActionEventMap("accept_washing", "ally_arrival",
                   "세족 수용 → 결속 근접"),
    ActionEventMap("jump_into_sea", "public_declaration",
                   "바다로 뛰어듦 → 극적 공개 표현"),
    ActionEventMap("stay_on_boat", "withdrawal",
                   "배에 남음 → 관망"),
]


class ActionEventMapper:
    """Convert action_id → triggered Event, apply to world state."""

    def __init__(self, table: list[ActionEventMap] | None = None) -> None:
        source = table if table is not None else ACTION_EVENT_TABLE
        self._map: dict[str, ActionEventMap] = {a.action_id: a for a in source}

    def lookup(self, action_id: str) -> ActionEventMap | None:
        return self._map.get(action_id)

    def trigger_event_id(self, action_id: str) -> str | None:
        entry = self.lookup(action_id)
        return entry.triggered_event_id if entry is not None else None

    def all_actions(self) -> list[str]:
        return list(self._map.keys())

    def n_actions(self) -> int:
        return len(self._map)
