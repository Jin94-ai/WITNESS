"""JSON 데이터 로더.

content/ 폴더의 JSON 파일을 Pydantic 모델로 로드한다.
DomainState의 다형성을 위한 타입 레지스트리를 포함한다.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.core.action import AgentBehaviorProfile
from engine.core.event import CanonicalIntervention, ExternalEvent
from engine.core.hazard import HazardEvent
from engine.core.phase import (
    FieldMapping,
    Phase,
    PhaseExitCondition,
    PhaseHandoffSpec,
)
from engine.core.state import AgentState, DomainState
from engine.core.trigger import Trigger

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


def load_behavior_profile(path: Path) -> AgentBehaviorProfile:
    """JSON 파일에서 AgentBehaviorProfile을 로드한다."""
    data = load_json(path)
    return AgentBehaviorProfile.model_validate(data)


def load_triggers(path: Path) -> list[Trigger]:
    """JSON 파일에서 Trigger 목록을 로드한다.

    JSON 구조: {"triggers": [...]} 또는 직접 리스트.
    """
    data = load_json(path)
    items = data.get("triggers", data) if isinstance(data, dict) else data
    return [Trigger.model_validate(t) for t in items]


def load_phase(
    path: Path,
    agents_active: list[str] | None = None,
    handoff_to_next: PhaseHandoffSpec | None = None,
) -> Phase:
    """`phase_config.json`을 `Phase` 객체로 로드 (v1.2 Iter 44).

    JSON 스키마 (content/*/phases/*/phase_config.json):
    ```
    {
      "phase_id": "...",
      "description": "..." (optional),
      "tick_scale_hours": 2.0,
      "max_tick": 84,
      "exit_condition": {
        "triggered_by": "..." (optional),
        "max_tick_fallback": 84 (optional)
      },
      "canonical_events_path": "..." (optional, file path)
    }
    ```

    `agents_active`와 `handoff_to_next`는 orchestration 결정이라 JSON에 없음;
    caller가 인자로 제공. `agents_active=None`이면 `SimulationConfig.initial_states`
    fallback (`PhasedSimulationWorld` 동작).

    Args:
        path: phase_config.json 경로.
        agents_active: 이 phase에서 활성화할 agent IDs.
        handoff_to_next: 별도로 로드한 (예: `load_handoff_spec`) handoff spec.

    Returns:
        `Phase` dataclass.
    """
    data = load_json(path)
    exit_cond_raw = data.get("exit_condition", {}) or {}
    exit_condition = PhaseExitCondition(
        max_tick=(
            exit_cond_raw.get("max_tick_fallback")
            if exit_cond_raw.get("max_tick_fallback") is not None
            else data.get("max_tick")
        ),
        triggered_by=exit_cond_raw.get("triggered_by"),
    )
    return Phase(
        phase_id=data["phase_id"],
        description=data.get("description", ""),
        tick_scale_hours=float(data["tick_scale_hours"]),
        exit_condition=exit_condition,
        agents_active=agents_active,
        handoff_to_next=handoff_to_next,
        canonical_events_path=data.get("canonical_events_path"),
        tick_offset=int(data.get("tick_offset_from_life_start", 0)),
    )


def load_handoff_spec(path: Path) -> PhaseHandoffSpec:
    """JSON 파일에서 `PhaseHandoffSpec`을 로드 (v1.2 Iter 43).

    JSON 구조 (content/*/phases/*/handoff_to_next.json):
    ```
    {
      "phase_from": "...",
      "phase_to": "...",
      "carry_all_slow_state": bool (optional, default True),
      "mappings": [
        {
          "source_agent_id": "...",
          "source_field_path": "...",
          "target_agent_id": "...",
          "target_field_path": "...",
          "default_if_missing": float | null (optional),
          "note": "..." (optional, ignored)
        }, ...
      ]
    }
    ```

    phase_from / phase_to / note 등 메타 필드는 검증 목적. `PhaseHandoffSpec`
    구성에는 carry_all_slow_state + mappings만 사용.
    """
    data = load_json(path)
    raw_mappings = data.get("mappings", [])
    mappings: list[FieldMapping] = []
    for m in raw_mappings:
        mappings.append(FieldMapping(
            source_agent_id=m["source_agent_id"],
            source_field_path=m["source_field_path"],
            target_agent_id=m["target_agent_id"],
            target_field_path=m["target_field_path"],
            default_if_missing=m.get("default_if_missing"),
        ))
    return PhaseHandoffSpec(
        carry_all_slow_state=data.get("carry_all_slow_state", True),
        mappings=mappings,
    )
