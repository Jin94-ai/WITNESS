"""테오의 도메인 상태: 후원자/형제.

테오의 핵심 파라미터:
- concern_for_brother: 형에 대한 걱정
- financial_strain: 재정적 부담
- belief_in_art: 형의 예술에 대한 신념
"""

from __future__ import annotations

from pydantic import Field

from engine.core.state import DomainState


class PatronState(DomainState):
    """테오의 후원자 도메인 상태."""

    type: str = Field(default="patron")
    concern_for_brother: float = Field(
        default=6.0, ge=0.0, le=10.0,
        description="형에 대한 걱정.",
    )
    financial_strain: float = Field(
        default=4.0, ge=0.0, le=10.0,
        description="재정적 부담.",
    )
    belief_in_art: float = Field(
        default=7.0, ge=0.0, le=10.0,
        description="형의 예술에 대한 신념.",
    )
