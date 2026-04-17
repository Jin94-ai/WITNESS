"""월드 상태와 시뮬레이션 설정.

시뮬레이션의 전역 컨테이너와 실행 설정을 정의한다.
Hazard-driven 모드와 기존 tick 고정 모드를 모두 지원 (하위 호환).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from engine.core.environment import EnvironmentState
from engine.core.event import CanonicalIntervention, ExternalEvent
from engine.core.hazard import HazardEvent
from engine.core.state import AgentState


class SimulationConfig(BaseModel):
    """시뮬레이션 실행 설정.

    hazard_events가 있으면 hazard-driven 모드로 동작.
    events만 있으면 기존 tick 고정 모드 (하위 호환).
    """

    seed: int | None = Field(default=None, description="난수 시드")
    max_tick: int = Field(default=500, gt=0, description="최대 tick 수")
    initial_state: AgentState = Field(description="에이전트 초기 상태")

    # 기존 tick 고정 이벤트 (하위 호환)
    events: list[ExternalEvent] = Field(default_factory=list)
    interventions: list[CanonicalIntervention] = Field(default_factory=list)

    # Hazard 기반 이벤트 (신규)
    hazard_events: list[HazardEvent] = Field(
        default_factory=list, description="Hazard 기반 이벤트 목록"
    )

    # 환경 상태
    environment: EnvironmentState = Field(
        default_factory=EnvironmentState,
        description="에이전트 외부 ���경 압력",
    )

    # 에이전트 상태에 추가할 노이즈 크기 (Langevin)
    state_noise_scale: float = Field(
        default=0.0, ge=0.0,
        description="매 tick 감정 상태에 추가할 가우시안 노이즈 표준편차",
    )

    parameter_overrides: dict[str, float] = Field(
        default_factory=dict,
        description="초기 상태에 적용할 파라미터 오버라이드",
    )

    @property
    def is_hazard_driven(self) -> bool:
        """Hazard 기반 모드인지 여부."""
        return len(self.hazard_events) > 0
