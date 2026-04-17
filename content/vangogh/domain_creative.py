"""반 고흐 도메인 상태: 창작 드라이브.

engine/이 아니라 content/vangogh/에 위치.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from engine.core.state import DomainState

CreativePhase = Literal[
    "seeking",        # 방향 탐색
    "developing",     # 양식 발전 중
    "peak_output",    # 최고 생산기
    "crisis",         # 창작 위기
    "recovery",       # 회복기
]


class CreativeDriveState(DomainState):
    """반 고흐의 창작 상태."""

    type: str = Field(default="creative_drive", init=False)
    creative_energy: float = Field(
        default=7.0, ge=0.0, le=10.0, description="창작 에너지"
    )
    artistic_confidence: float = Field(
        default=4.0, ge=0.0, le=10.0, description="예술적 자신감"
    )
    phase: CreativePhase = Field(
        default="developing", description="창작 단계"
    )
    works_completed: int = Field(
        default=0, ge=0, description="완성한 작품 수"
    )
    palette_boldness: float = Field(
        default=5.0, ge=0.0, le=10.0, description="팔레트 대담함 (색채 강도)"
    )
