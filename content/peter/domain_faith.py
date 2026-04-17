"""베드로 도메인 상태: 신앙 여정.

engine/이 아니라 content/peter/에 위치한다.
엔진은 DomainState 추상만 알며, 이 모듈은 베드로 전용 스키마이다.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from engine.core.state import DomainState


class FearProfile(DomainState):
    """두려움의 층위. 자연적/사회적/실존적 두려움을 구분한다."""

    type: str = Field(default="fear_profile", init=False)
    natural: float = Field(default=3.0, ge=0.0, le=10.0, description="자연적 두려움 (물리적 위험)")
    social: float = Field(default=4.0, ge=0.0, le=10.0, description="사회적 두려움 (배척, 비난)")
    existential: float = Field(default=2.0, ge=0.0, le=10.0, description="실존적 두려움 (의미 상실)")


class RepentanceCycle(DomainState):
    """회개 순환 기록. 비선형적 내면 변화를 추적한다."""

    type: str = Field(default="repentance_cycle", init=False)
    tick: int = Field(ge=0, description="회개가 발생한 tick")
    trigger: str = Field(description="회개를 촉발한 사건")
    depth: float = Field(default=5.0, ge=0.0, le=10.0, description="회개의 깊이")


JesusUnderstanding = Literal[
    "teacher",
    "prophet",
    "messiah_political",
    "messiah_suffering",
    "son_of_god",
    "risen_lord",
    "sending_lord",
]

CommunalRole = Literal[
    "disciple",
    "inner_circle",
    "failed",
    "restored",
    "shepherd",
    "foundation",
]


class FaithJourneyState(DomainState):
    """베드로의 신앙 여정 상태.

    jesus_understanding과 communal_role은 비선형 전환 가능.
    부인 사건에서 inner_circle -> failed로 되돌아갈 수 있다.
    """

    type: str = Field(default="faith_journey", init=False)
    jesus_understanding: JesusUnderstanding = Field(
        default="messiah_political",
        description="예수 이해의 단계",
    )
    obedience_maturity: float = Field(
        default=5.0, ge=0.0, le=10.0, description="순종 성숙도"
    )
    fear_layers: FearProfile = Field(
        default_factory=FearProfile, description="두려움의 층위"
    )
    communal_role: CommunalRole = Field(
        default="inner_circle", description="공동체 내 역할"
    )
    repentance_history: list[RepentanceCycle] = Field(
        default_factory=list, description="회개 순환 기록"
    )
