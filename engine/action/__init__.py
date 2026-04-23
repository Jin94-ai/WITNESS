"""Witness v3.0 Action module -- action → event mapping (v2 §5).

Rule #12 완화 (v2 §10.2): 월드는 행동 결정 금지. 하지만 **행동의 결과로
월드가 갱신되는 것은 허용**. 이 모듈이 그 폐루프를 담당.

Flow:
    Person action → [action_event_mapper] → Layer B Event → Layer A update
"""

from engine.action.action_event_mapper import (
    ACTION_EVENT_TABLE,
    ActionEventMapper,
)

__all__ = ["ActionEventMapper", "ACTION_EVENT_TABLE"]
