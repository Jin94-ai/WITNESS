"""가야바의 도메인 상태: 정치적 계산.

가야바의 핵심 파라미터:
- threat_assessment: 예수 운동에 대한 위협 평가
- political_calculation: 로마에 대한 정치적 계산
- religious_authority: 종교적 권위 보전 욕구
- pragmatism: 실용주의 (한 사람의 죽음으로 민족을 구한다)
"""

from __future__ import annotations

from pydantic import Field

from engine.core.state import DomainState


class PoliticalCalculationState(DomainState):
    """가야바의 정치적 계산 도메인 상태."""

    type: str = Field(default="political_calculation")
    threat_assessment: float = Field(
        default=4.0, ge=0.0, le=10.0,
        description="예수 운동의 위협 수준 평가. 높을수록 위험하다고 판단.",
    )
    political_calculation: float = Field(
        default=6.0, ge=0.0, le=10.0,
        description="로마와의 정치적 관계 계산. 높을수록 로마를 의식.",
    )
    religious_authority: float = Field(
        default=7.0, ge=0.0, le=10.0,
        description="종교적 권위 보전 욕구.",
    )
    pragmatism: float = Field(
        default=7.0, ge=0.0, le=10.0,
        description="실용주의. '한 사람의 죽음으로 민족을 구한다'는 논리.",
    )
    intelligence_quality: float = Field(
        default=3.0, ge=0.0, le=10.0,
        description="내부자 정보의 질. inform_authorities로 상승.",
    )
