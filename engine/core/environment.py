"""환경 상태.

에��전트 외부의 환경 압력을 모델링한다.
���인 내부 심리만으로 분기가 설명되는 것을 ��지하기 위해,
환경이 행동에 영향을 주는 구조.

인물 비종속: 구체적인 환경 변수 값은 content/에서 정의.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class EnvironmentState(BaseModel):
    """시뮬레이션 전역 환경. 에이전트 외부의 압력."""

    crowd_pressure: float = Field(
        default=3.0, ge=0.0, le=10.0,
        description="군중/사회적 압력. 높을수록 동조 압력 증가.",
    )
    surveillance: float = Field(
        default=3.0, ge=0.0, le=10.0,
        description="감시/노출 수준. 높을수록 발각 위험 증가.",
    )
    threat_level: float = Field(
        default=3.0, ge=0.0, le=10.0,
        description="물리적 위협 수준. 체포, 폭력 위험.",
    )
    time_pressure: float = Field(
        default=0.0, ge=0.0, le=10.0,
        description="시간 압박. 즉각적 결정이 필요한 정도.",
    )
    isolation_degree: float = Field(
        default=0.0, ge=0.0, le=10.0,
        description="고립 정도. 동료와의 물리적 분리.",
    )
