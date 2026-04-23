"""유다의 도메인 상태: 배반의 심리.

유다의 핵심 파라미터:
- disillusionment: 예수에 대한 환멸 (정치적 메시아 기대 불일치)
- greed: 물질적 욕심 (은전 30에 대한 유혹)
- messiah_expectation: 메시아 기대치 (정치적 vs 영적)
- guilt: 죄책감 (배반 후 누적)
"""

from __future__ import annotations

from pydantic import Field

from engine.core.state import DomainState


class BetrayalPsychologyState(DomainState):
    """유다의 배반 심리 도메인 상태."""

    type: str = Field(default="betrayal_psychology")
    disillusionment: float = Field(
        default=3.0, ge=0.0, le=10.0,
        description="예수에 대한 환멸. 기대한 정치적 메시아가 아님을 깨달아감.",
    )
    greed: float = Field(
        default=4.0, ge=0.0, le=10.0,
        description="물질적 욕심. 은전 30에 대한 유혹.",
    )
    messiah_expectation: float = Field(
        default=7.0, ge=0.0, le=10.0,
        description="메시아 기대치. 높을수록 정치적 해방을 기대.",
    )
    guilt: float = Field(
        default=0.0, ge=0.0, le=10.0,
        description="죄책감. 배반 후 누적.",
    )
    loyalty_to_cause: float = Field(
        default=6.0, ge=0.0, le=10.0,
        description="대의에 대한 충성. 예수 개인이 아닌 운동에 대한 헌신.",
    )
