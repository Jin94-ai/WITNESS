"""군중/하인/경비 준-에이전트 도메인 상태.

중간 압력층: 베드로의 부인이 하인/군중의 미시적 압력에 의해 매개된다.
완전한 에이전트보�� 가볍다 -- 핵심은 사회적 압력 생성.
"""

from __future__ import annotations

from pydantic import Field

from engine.core.state import DomainState


class CrowdDynamicsState(DomainState):
    """군중 역학 도메인 상태. 집단적 행동 경향."""

    type: str = Field(default="crowd_dynamics")
    suspicion_level: float = Field(
        default=3.0, ge=0.0, le=10.0,
        description="의심 수준. 높을수록 외부인을 의심.",
    )
    mob_energy: float = Field(
        default=2.0, ge=0.0, le=10.0,
        description="군중 에너지. 높을수록 행동적.",
    )
    hostility: float = Field(
        default=2.0, ge=0.0, le=10.0,
        description="적대성. 체포/재판 시 높아짐.",
    )
    recognition_risk: float = Field(
        default=3.0, ge=0.0, le=10.0,
        description="베드로를 알아볼 위험. 높을수록 노출 위험.",
    )
