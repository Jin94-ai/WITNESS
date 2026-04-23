"""월드 상태와 시뮬레이션 설정.

시뮬레이션의 전역 컨테이너와 실행 설정을 정의한다.
Hazard-driven 모드와 기존 tick 고정 모드를 모두 지원 (하위 호환).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from engine.core.environment import EnvironmentState
from engine.core.event import CanonicalIntervention, ExternalEvent
from engine.core.hazard import HazardEvent
from engine.core.phase import Phase
from engine.core.state import AgentState
from engine.core.trigger import Trigger


class SimulationConfig(BaseModel):
    """시뮬레이션 실행 설정.

    hazard_events가 있으면 hazard-driven 모드로 동작.
    events만 있으면 기존 tick 고정 모드 (하위 호환).

    다중 에이전트: initial_states에 여러 에이전트를 넣으면 multi-agent 모드.
    initial_state(단일)는 하위 호환용 -- initial_states[0]으로 자동 매핑.
    """

    seed: int | None = Field(default=None, description="난수 시드")
    max_tick: int = Field(default=500, gt=0, description="최대 tick 수")
    initial_state: AgentState = Field(description="에이전트 초기 상태 (단일 에이전트 하위 호환)")
    initial_states: list[AgentState] = Field(
        default_factory=list,
        description="다중 에이전트 초기 상태. 비어있으면 initial_state를 사용.",
    )
    triggers: list[Trigger] = Field(
        default_factory=list,
        description="다중 에이전트 트리거 (에이전트 상호작용 -> 이벤트 생성)",
    )

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

    # v1.2 phase-linked architecture (2026-04-19)
    tick_scale_hours: float = Field(
        default=2.0, gt=0.0,
        description="단일 phase 모드에서 1 tick이 몇 시간인가. "
                    "기본 2.0 = v0.5 수난 scenario 호환. "
                    "phases가 설정되면 각 phase의 tick_scale_hours가 우선.",
    )
    phases: list[Phase] | None = Field(
        default=None,
        description="Phase-linked life architecture. None이면 단일 phase 모드 (기존). "
                    "리스트면 순차 실행, 각 phase 종료 시 handoff 수행.",
    )

    @property
    def is_hazard_driven(self) -> bool:
        """Hazard 기반 모드인지 여부."""
        return len(self.hazard_events) > 0

    @property
    def is_multi_agent(self) -> bool:
        """다중 에이전트 모드인지 여부."""
        return len(self.initial_states) > 1

    @property
    def is_phase_linked(self) -> bool:
        """Phase-linked life architecture 모드인지 (v1.2)."""
        return self.phases is not None and len(self.phases) > 0

    def get_all_initial_states(self) -> list[AgentState]:
        """모든 초기 에이전트 상태를 반환한다. 하위 호환."""
        if self.initial_states:
            return list(self.initial_states)
        return [self.initial_state]
