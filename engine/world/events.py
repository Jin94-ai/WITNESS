"""Layer B -- Events (v3 Phase 2 v2 §2.2).

짧은 수명 사건 (short-lived). 특정 tick에 발생하며 다음 tick으로 지속하지
않는다. Primitive(Layer A)를 갱신할 수 있다 (v2 §5 폐루프).

v2 §2.2 예시:
    accusation, eye_contact, betrayal_witnessed, prayer_invitation,
    miracle_witnessed, ally_arrival, ally_departure, ...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Event:
    """Single event declaration + primitive updates.

    primitive_updates: {primitive_name: delta} -- Applied on event fire.
    """

    event_id: str
    description: str
    duration_ticks: int = 1
    primitive_updates: dict[str, float] = field(default_factory=dict)
    source: str = "content"  # "content" = canonical event, "action" = caused by person action (v2 §5)


# =============================================================================
# EVENT_REGISTRY -- initial draft (content will extend)
# =============================================================================

EVENT_REGISTRY_DRAFT: list[Event] = [
    # --- Social / public exposure ---
    Event(
        event_id="public_accusation",
        description="공개 고발 (여종의 질문 등)",
        primitive_updates={"accusation_visibility": 0.8, "public_visibility": 0.3},
    ),
    Event(
        event_id="crowd_mockery",
        description="군중의 조롱",
        primitive_updates={"crowd_density": 0.2, "public_visibility": 0.4},
    ),
    Event(
        event_id="eye_contact",
        description="주된 결속 대상과 눈 마주침 (누가 22:61)",
        primitive_updates={"primary_figure_visible": 1.0},
    ),
    # --- Interpersonal ---
    Event(
        event_id="ally_arrival",
        description="동료 도착",
        primitive_updates={"ally_proximity": 0.4, "group_cohesion": 0.2},
    ),
    Event(
        event_id="ally_departure",
        description="동료 이탈",
        primitive_updates={"ally_proximity": -0.4, "group_cohesion": -0.3},
    ),
    Event(
        event_id="betrayal_witnessed",
        description="배반을 목격",
        primitive_updates={"group_cohesion": -0.5, "volatility": 0.3},
    ),
    # --- Physical threat ---
    Event(
        event_id="guard_approaches",
        description="경비병 접근",
        primitive_updates={"roman_presence": 0.3, "time_pressure": 0.3, "volatility": 0.2},
    ),
    Event(
        event_id="weapon_drawn_nearby",
        description="근처 무기 뽑힘",
        primitive_updates={"volatility": 0.5, "decision_criticality": 0.5},
    ),
    # --- Sacred ---
    Event(
        event_id="sacred_meal",
        description="거룩한 식사 (최후의 만찬)",
        primitive_updates={"religious_context": 0.5, "primary_figure_presence": 0.5},
    ),
    Event(
        event_id="miracle_witnessed",
        description="기적 목격",
        primitive_updates={"religious_context": 0.5, "decision_stakes": 0.1},
    ),
    Event(
        event_id="prayer_invitation",
        description="기도 초대",
        primitive_updates={"religious_context": 0.3},
    ),
    # --- Recovery ---
    Event(
        event_id="forgiveness_offered",
        description="용서 제공",
        primitive_updates={"primary_figure_presence": 0.3},
    ),
    Event(
        event_id="restoration_moment",
        description="회복 순간 (디베랴)",
        primitive_updates={"primary_figure_presence": 0.5, "religious_context": 0.3},
    ),
    # --- Decision-critical ---
    Event(
        event_id="time_running_out",
        description="시간 임박",
        primitive_updates={"time_pressure": 0.5, "decision_criticality": 0.4},
    ),
    Event(
        event_id="hidden_information_revealed",
        description="숨겨진 정보 공개",
        primitive_updates={"information_gap": -0.5},
    ),
    # --- Covert / decision-transition (generic; scenario-specific meaning in content) ---
    Event(
        event_id="covert_bargain",
        description="비공개 거래 또는 약속 (비밀 맹약)",
        primitive_updates={"information_gap": -0.2, "decision_stakes": 0.3},
    ),
    Event(
        event_id="identification_signal",
        description="식별 신호를 보냄 (대중 앞에서 특정인 지목)",
        primitive_updates={"public_visibility": 0.4, "authority_presence": 0.3,
                           "decision_criticality": 0.4},
    ),
    Event(
        event_id="remorse_trigger",
        description="자신의 행동 결과를 목격 (되돌릴 수 없음 인식)",
        primitive_updates={"proximity_of_suffering": 0.5,
                           "prior_failure_salience": 0.4,
                           "decision_stakes": 0.4},
    ),
    Event(
        event_id="return_token",
        description="받은 대가나 표시를 되돌림 (상징적 거부)",
        primitive_updates={"public_visibility": 0.3,
                           "prior_failure_salience": 0.3},
    ),

    # --- Creative / isolated-context scenarios (generic) ---
    Event(
        event_id="creative_surge",
        description="집중 창작 연속 (예술가/작업자 맥락)",
        primitive_updates={"religious_context": 0.3,
                           "decision_stakes": 0.2},
    ),
    Event(
        event_id="creative_conflict",
        description="작업/관점 갈등 (동료와)",
        primitive_updates={"volatility": 0.3, "ally_proximity": -0.2,
                           "decision_criticality": 0.3},
    ),
    Event(
        event_id="self_harm_impulse",
        description="극도 절망 / 자기 파괴 충동",
        primitive_updates={"decision_criticality": 0.5,
                           "volatility": 0.5,
                           "proximity_of_suffering": 0.5},
    ),

    # --- Action-caused events (v2 §5 폐루프) ---
    Event(
        event_id="public_denial",
        description="공개 부인 (agent 행동 결과)",
        primitive_updates={"accusation_visibility": 0.3, "public_visibility": 0.3},
        source="action",
    ),
    Event(
        event_id="visible_distress",
        description="눈물/흔들림 가시적 드러남",
        primitive_updates={"public_visibility": -0.2},  # 숨어서 울면 노출 감소
        source="action",
    ),
    Event(
        event_id="public_declaration",
        description="공개 고백/선언",
        primitive_updates={"authority_presence": 0.2, "public_visibility": 0.4},
        source="action",
    ),
    Event(
        event_id="withdrawal",
        description="물러남",
        primitive_updates={"ally_proximity": -0.3, "public_visibility": -0.3},
        source="action",
    ),
    Event(
        event_id="weapon_raised",
        description="무기 들어올림 (칼을 빼는 행동)",
        primitive_updates={"volatility": 0.4, "decision_criticality": 0.3},
        source="action",
    ),
]


class EventRegistry:
    """Registry + primitive updater."""

    def __init__(self, events: list[Event] | None = None) -> None:
        self._events = {e.event_id: e for e in (events if events is not None else EVENT_REGISTRY_DRAFT)}

    def get(self, event_id: str) -> Event | None:
        return self._events.get(event_id)

    def all(self) -> list[Event]:
        return list(self._events.values())

    def n_events(self) -> int:
        return len(self._events)

    def action_caused(self) -> list[Event]:
        return [e for e in self._events.values() if e.source == "action"]

    def content_caused(self) -> list[Event]:
        return [e for e in self._events.values() if e.source == "content"]

    def apply_to_primitives(
        self, event_id: str, primitives: Any,
    ) -> list[str]:
        """Apply event's primitive_updates to a PrimitiveState dataclass.

        Returns list of updated field names. If event unknown, returns [].
        """
        event = self.get(event_id)
        if event is None:
            return []
        updated: list[str] = []
        for field_name, delta in event.primitive_updates.items():
            if hasattr(primitives, field_name):
                current = getattr(primitives, field_name)
                if isinstance(current, bool):
                    # Bool update: delta > 0 sets True, < 0 sets False, 0 no change
                    if delta > 0:
                        setattr(primitives, field_name, True)
                        updated.append(field_name)
                    elif delta < 0:
                        setattr(primitives, field_name, False)
                        updated.append(field_name)
                elif isinstance(current, (int, float)):
                    new_val = max(0.0, min(1.0, current + delta))
                    setattr(primitives, field_name, new_val)
                    updated.append(field_name)
        return updated
