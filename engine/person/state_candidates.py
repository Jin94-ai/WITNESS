"""Candidate variable registry (v3 Phase 2 v2 §1.1).

Candidate 변수:
    정경에서 추출되었으나 아직 시뮬레이션에 활성화 안 된 변수들.
    Reserve / dormant 상태로 보관. 필요 시 Active로 승격 가능.
    예상 수: 50-60개 (v2 §1.1)

승격 4 조건 (v2 §1.2):
    1. 정경 Level A 또는 B
    2. 다른 Active의 단순 합/차 아님
    3. 행동 결정에 영향
    4. Sensitivity: 변수 변경 시 policy output 변화

4조건 모두 만족해야 Active 승격. 셋만 만족하면 Candidate 보류.

v2 §11: 승격 최종 승인은 Lee 판단 필수. Claude는 초안만 제공.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from engine.person.state_v3 import (
    VariableMeta,
)

PromotionBlocker = Literal[
    "derivable_from_active",   # condition (2) fails: can be computed from Active
    "low_sensitivity",         # condition (4) fails: untested or negligible
    "level_C",                 # condition (1) fails: Level C, needs Lee approval
    "low_behavior_impact",     # condition (3) fails: doesn't influence action choice
]


@dataclass
class CandidateVariable:
    """A variable extracted from scripture but not yet Active."""

    meta: VariableMeta
    extraction_note: str = ""
    promotion_blockers: list[PromotionBlocker] = field(default_factory=list)


# =============================================================================
# Candidate registry -- Claude's provisional draft (Lee reviews to promote)
# =============================================================================

CANDIDATE_VARIABLES: list[CandidateVariable] = [
    # --- Derivable from Active (blocker: derivable_from_active) ---
    CandidateVariable(
        meta=VariableMeta(
            name="stress",
            grade="candidate",
            evidence_level="A",
            structure="scalar",
        ),
        extraction_note="정경에서 '압박/근심' 표현. 그러나 fear+fatigue+uncertainty 합성으로 대체 가능.",
        promotion_blockers=["derivable_from_active"],
    ),
    CandidateVariable(
        meta=VariableMeta(
            name="peace",
            grade="candidate",
            evidence_level="A",
            structure="scalar",
            scripture_references=["요한복음 14:27 '평안을 너희에게 끼치노니'"],
        ),
        extraction_note="고요함. hope + vitality 함수로 표현 가능 → Derived 후보.",
        promotion_blockers=["derivable_from_active"],
    ),
    # --- Level C (blocker: level_C) ---
    CandidateVariable(
        meta=VariableMeta(
            name="forgiveness_perception",
            grade="candidate",
            evidence_level="C",
            structure="target_aware",
            default_targets=["primary_figure"],
            scripture_references=["요한복음 21:15-17 (해석적)"],
        ),
        extraction_note="디베랴 호숫가 3회 질문 후 '회복' 감각. 심리 해석 필요.",
        promotion_blockers=["level_C"],
    ),
    CandidateVariable(
        meta=VariableMeta(
            name="identity_restoration",
            grade="candidate",
            evidence_level="C",
            structure="scalar",
            scripture_references=["요한복음 21:15-17 (해석적)"],
        ),
        extraction_note="'반석' 호칭 회복의 내면 경험. 해석 필요.",
        promotion_blockers=["level_C"],
    ),
    CandidateVariable(
        meta=VariableMeta(
            name="spiritual_courage",
            grade="candidate",
            evidence_level="C",
            structure="scalar",
            scripture_references=["사도행전 4:13 (해석적)"],
        ),
        extraction_note="오순절 후 담대함. 정경 명시 있지만 내면 변수 해석.",
        promotion_blockers=["level_C"],
    ),
    # --- Low sensitivity (blocker: low_sensitivity, not yet measured) ---
    CandidateVariable(
        meta=VariableMeta(
            name="attention",
            grade="candidate",
            evidence_level="B",
            structure="scalar",
        ),
        extraction_note="주의 집중도. 행동 영향은 있지만 Phase B sensitivity 측정 전.",
        promotion_blockers=["low_sensitivity"],
    ),
    CandidateVariable(
        meta=VariableMeta(
            name="curiosity",
            grade="candidate",
            evidence_level="B",
            structure="scalar",
        ),
        extraction_note="호기심. 정경 직접 명시 약함.",
        promotion_blockers=["low_sensitivity", "level_C"],
    ),
    # --- Low behavior impact ---
    CandidateVariable(
        meta=VariableMeta(
            name="hunger_specificity",
            grade="candidate",
            evidence_level="C",
            structure="scalar",
        ),
        extraction_note="특정 음식에 대한 욕구. hunger로 충분히 포함.",
        promotion_blockers=["low_behavior_impact", "derivable_from_active", "level_C"],
    ),
    # --- Target-aware candidates awaiting target list definition ---
    CandidateVariable(
        meta=VariableMeta(
            name="envy",
            grade="candidate",
            evidence_level="B",
            structure="target_aware",
            default_targets=["peers"],
        ),
        extraction_note="요한복음 21:21 '이 사람은 어떻게 되겠삽나이까' 해석.",
        promotion_blockers=["low_sensitivity"],
    ),
    CandidateVariable(
        meta=VariableMeta(
            name="admiration",
            grade="candidate",
            evidence_level="A",
            structure="target_aware",
            default_targets=["primary_figure"],
            scripture_references=["마태복음 14:33 '하나님의 아들이로소이다'"],
        ),
        extraction_note="경외(awe)와 구별되는 찬탄. awe와 overlap 검토 필요.",
        promotion_blockers=["derivable_from_active"],
    ),
]


# =============================================================================
# Registry API
# =============================================================================

class CandidateRegistry:
    """Read-only registry with promotion-check utilities."""

    def __init__(self, candidates: list[CandidateVariable] | None = None) -> None:
        self._items = list(candidates) if candidates is not None else list(CANDIDATE_VARIABLES)

    def all(self) -> list[CandidateVariable]:
        return list(self._items)

    def get(self, name: str) -> CandidateVariable | None:
        for c in self._items:
            if c.meta.name == name:
                return c
        return None

    def n_total(self) -> int:
        return len(self._items)

    def by_blocker(self, blocker: PromotionBlocker) -> list[CandidateVariable]:
        return [c for c in self._items if blocker in c.promotion_blockers]

    def promotable_if(self, *, allow_level_c: bool = False) -> list[CandidateVariable]:
        """Return candidates that could plausibly be promoted.

        Default: excludes Level C (needs Lee approval per Rule #17) and
        anything with derivable_from_active / low_sensitivity blocker.
        """
        result = []
        for c in self._items:
            blockers = set(c.promotion_blockers)
            if "derivable_from_active" in blockers:
                continue
            if "low_behavior_impact" in blockers:
                continue
            if "low_sensitivity" in blockers:
                continue
            if "level_C" in blockers and not allow_level_c:
                continue
            result.append(c)
        return result
