"""Constraint Layer D -- "Constitution" of allowed trajectories.

Spec §5.2 "Layer D: Constraint (헌법)":
  - 역사적 모순 금지
  - 정경 충돌 금지
  - 시대착오 금지
  - 신성모독 금지
  - 특정 인물 지식 범위 제한

Hard constraints are binary (violation → invalid). Soft constraints
produce penalty scores (distance from canonical attractor).

Rule #1: constraint definitions are generic. Scenario-specific lists
(canonical_events, anachronism allowlist) come from content/.
"""

from engine.constraint.hard_constraints import (
    ConstraintViolation,
    HardConstraintChecker,
)
from engine.constraint.soft_constraints import SoftConstraintScorer

__all__ = [
    "HardConstraintChecker", "ConstraintViolation",
    "SoftConstraintScorer",
]
