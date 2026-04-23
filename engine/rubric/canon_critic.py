"""Canon Critic -- Axis 2 of 4-axis rubric.

Spec §6.2 verbatim:
    축 2: Canon Compatibility
    측정: Hard constraint 침범 / Soft constraint (canonical attractor 편차)

v3 discovery definitions §2.2 measurement methods:
    (1) Anachronism check
    (2) Canonical contradiction check
    (3) Sacred-text violation check (Rule #2 scripture-verbatim guard)

Uses existing HardConstraintChecker + SoftConstraintScorer as the
measurement backbone. This critic wraps them and classifies trajectories
as 'canon-reproducing' / 'canon-compatible' / 'canon-violating'.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.constraint.hard_constraints import (
    ConstraintViolation,
    HardConstraintChecker,
)
from engine.constraint.soft_constraints import SoftConstraintScorer


@dataclass
class CanonReport:
    hard_violations: list[ConstraintViolation]
    soft_drift: float           # 0 = canon-exact, larger = more drift
    is_canon_valid: bool        # True = no hard violations
    is_canon_reproducing: bool  # True = soft drift near 0


class CanonCritic:
    """Combine hard + soft constraint checks into a canon-axis score."""

    def __init__(
        self,
        *,
        hard: HardConstraintChecker | None = None,
        soft: SoftConstraintScorer | None = None,
        reproduction_threshold: float = 2.0,
    ) -> None:
        self._hard = hard
        self._soft = soft
        self._repro_t = reproduction_threshold

    def evaluate(self, records: list[dict[str, Any]]) -> CanonReport:
        hard_vs = self._hard.check_all(records) if self._hard else []
        drift = self._soft.score(records) if self._soft else 0.0
        return CanonReport(
            hard_violations=hard_vs,
            soft_drift=drift,
            is_canon_valid=len(hard_vs) == 0,
            is_canon_reproducing=(
                len(hard_vs) == 0 and drift <= self._repro_t
            ),
        )
