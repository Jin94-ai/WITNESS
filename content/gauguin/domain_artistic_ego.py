"""고갱의 도메인 상태: 예술적 자아.

고갱의 핵심 파라미터:
- artistic_superiority: 자신의 예술적 우월감
- frustration_with_vincent: 반 고흐에 대한 좌절/짜증
- wanderlust: 떠나고 싶은 욕구 (타히티에 대한 동경)
- collaboration_willingness: 협업 의지
"""

from __future__ import annotations

from pydantic import Field

from engine.core.state import DomainState


class ArtisticEgoState(DomainState):
    """고갱의 예술적 자아 도메인 상태."""

    type: str = Field(default="artistic_ego")
    artistic_superiority: float = Field(
        default=7.0, ge=0.0, le=10.0,
        description="자신의 예술적 우월감.",
    )
    frustration_with_partner: float = Field(
        default=3.0, ge=0.0, le=10.0,
        description="협업 파트너에 대한 좌절. 높을수록 갈등.",
    )
    wanderlust: float = Field(
        default=5.0, ge=0.0, le=10.0,
        description="떠나고 싶은 욕구.",
    )
    collaboration_willingness: float = Field(
        default=5.0, ge=0.0, le=10.0,
        description="협업 의지. 낮을수록 떠날 준비.",
    )
