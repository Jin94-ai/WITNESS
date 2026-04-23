"""이벤트 스케줄러.

tick 기반으로 이벤트를 관리하고 반환하는 큐.
"""

from __future__ import annotations

from engine.core.event import CanonicalIntervention, ExternalEvent


class EventScheduler:
    """tick 기반 이벤트 스케줄러.

    이벤트와 정경 개입을 tick 순서로 관리한다.
    """

    def __init__(
        self,
        events: list[ExternalEvent],
        interventions: list[CanonicalIntervention] | None = None,
    ) -> None:
        self._events = sorted(events, key=lambda e: e.tick)
        self._interventions = sorted(
            interventions or [], key=lambda i: i.tick
        )
        self._event_idx = 0
        self._intervention_idx = 0

    def get_events_for_tick(self, tick: int) -> list[ExternalEvent]:
        """해당 tick에 발생하는 이벤트 목록을 반환한다."""
        result: list[ExternalEvent] = []
        while (
            self._event_idx < len(self._events)
            and self._events[self._event_idx].tick == tick
        ):
            result.append(self._events[self._event_idx])
            self._event_idx += 1
        return result

    def get_interventions_for_tick(self, tick: int) -> list[CanonicalIntervention]:
        """해당 tick에 발생하는 정경 개입 목록을 반환한다."""
        result: list[CanonicalIntervention] = []
        while (
            self._intervention_idx < len(self._interventions)
            and self._interventions[self._intervention_idx].tick == tick
        ):
            result.append(self._interventions[self._intervention_idx])
            self._intervention_idx += 1
        return result

    def inject_event(self, event: ExternalEvent) -> None:
        """동적으로 이벤트를 주입한다. 트리거 시스템에서 사용."""
        # 정렬 유지를 위해 적절한 위치에 삽입
        idx = len(self._events)
        for i in range(self._event_idx, len(self._events)):
            if self._events[i].tick > event.tick:
                idx = i
                break
        self._events.insert(idx, event)

    def has_remaining(self) -> bool:
        """처리되지 않은 이벤트가 남아있는지 확인한다."""
        return (
            self._event_idx < len(self._events)
            or self._intervention_idx < len(self._interventions)
        )

    def reset(self) -> None:
        """스케줄러를 초기 상태로 리셋한다."""
        self._event_idx = 0
        self._intervention_idx = 0
