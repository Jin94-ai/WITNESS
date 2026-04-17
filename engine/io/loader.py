"""JSON 데이터 로더.

content/ 폴더의 JSON 파일을 Pydantic 모델로 로드한다.
DomainState의 다형성을 위한 타입 레지스트리를 포함한다.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.core.event import CanonicalIntervention, ExternalEvent
from engine.core.hazard import HazardEvent
from engine.core.state import AgentState, DomainState


# DomainState 타입 레지스트리
_domain_registry: dict[str, type[DomainState]] = {}


def register_domain_type(type_name: str, cls: type[DomainState]) -> None:
    """도메인 상태 타입을 레지스트리에 등록한다.

    Args:
        type_name: JSON의 "type" 필드 값
        cls: 해당 타입의 Pydantic 모델 클래스
    """
    _domain_registry[type_name] = cls


def resolve_domain_state(data: dict[str, Any] | None) -> DomainState | None:
    """딕셔너리에서 적절한 DomainState 서브클래스 인스턴스를 생성한다.

    Args:
        data: JSON에서 파싱된 딕셔너리. "type" 키로 타입을 식별.

    Returns:
        적절한 DomainState 인스턴스. data가 None이면 None.
    """
    if data is None:
        return None

    type_name = data.get("type", "base")
    cls = _domain_registry.get(type_name, DomainState)
    return cls.model_validate(data)


def load_json(path: Path) -> Any:
    """JSON 파일을 파싱하여 반환한다."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_agent_state(path: Path) -> AgentState:
    """JSON 파일에서 AgentState를 로드한다.

    domain_state는 타입 레지스트리를 통해 적절한 서브클래스로 복원된다.
    """
    data = load_json(path)
    domain_data = data.pop("domain_state", None)
    state = AgentState.model_validate(data)
    domain = resolve_domain_state(domain_data)
    if domain is not None:
        state = state.model_copy(update={"domain_state": domain})
    return state


def load_events(path: Path) -> list[ExternalEvent]:
    """JSON 파일에서 이벤트 목록을 로드한다.

    JSON 구조: {"events": [...]} 또는 직접 리스트.
    """
    data = load_json(path)
    events_data = data.get("events", data) if isinstance(data, dict) else data
    return [ExternalEvent.model_validate(e) for e in events_data]


def load_interventions(path: Path) -> list[CanonicalIntervention]:
    """JSON 파일에서 CanonicalIntervention 목록을 로드한다.

    JSON 구조: {"interventions": [...]} 또는 직접 리스트.
    """
    data = load_json(path)
    items = data.get("interventions", data) if isinstance(data, dict) else data
    return [CanonicalIntervention.model_validate(i) for i in items]


def load_hazard_events(path: Path) -> list[HazardEvent]:
    """JSON 파일에서 HazardEvent 목록을 로드한다.

    JSON 구조: {"hazard_events": [...]} 또는 직접 리스트.
    """
    data = load_json(path)
    items = data.get("hazard_events", data) if isinstance(data, dict) else data
    return [HazardEvent.model_validate(e) for e in items]
