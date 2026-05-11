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
    # Phase 3.05 rubric review §2.6 P2 — hard/soft 명시 분리 보강
    soft_deviations: tuple[str, ...] = ()    # soft 편차 명시 (default empty for backwards compat)
    soft_compatibility_score: float = 1.0    # 0-1, 1 = canon-exact (drift 0)
    calibration_status: str = "uncalibrated_phase3_placeholder"

    # Phase 3.05 review §2.6 — alias property
    @property
    def hard_pass(self) -> bool:
        """rubric review §2.6 권장 명칭 — is_canon_valid의 의미적 alias."""
        return self.is_canon_valid


class CanonCritic:
    """Combine hard + soft constraint checks into a canon-axis score.

    Phase 3.05 rubric review §2.6 P2:
        - hard/soft 명시 분리 유지 (hard_violations / soft_drift)
        - soft_compatibility_score (0-1) 추가 — drift의 normalized form
        - calibration_status 명시
        - hard_pass alias (review 권장 명칭)
    """

    def __init__(
        self,
        *,
        hard: HardConstraintChecker | None = None,
        soft: SoftConstraintScorer | None = None,
        reproduction_threshold: float = 2.0,
        # Phase 3.05 review §2.6 — soft compatibility normalization scale (uncalibrated)
        soft_drift_max: float = 10.0,
    ) -> None:
        self._hard = hard
        self._soft = soft
        self._repro_t = reproduction_threshold
        self._soft_max = soft_drift_max

    def evaluate(self, records: list[dict[str, Any]]) -> CanonReport:
        hard_vs = self._hard.check_all(records) if self._hard else []
        drift = self._soft.score(records) if self._soft else 0.0
        # Phase 3.05 review §2.6: soft_compatibility_score 0-1 (1 = canon-exact)
        soft_compat = max(0.0, min(1.0, 1.0 - drift / self._soft_max))
        return CanonReport(
            hard_violations=hard_vs,
            soft_drift=drift,
            is_canon_valid=len(hard_vs) == 0,
            is_canon_reproducing=(
                len(hard_vs) == 0 and drift <= self._repro_t
            ),
            soft_compatibility_score=soft_compat,
            # soft_deviations는 현재 단일 scalar drift만 측정 — 미래 SoftConstraintScorer 보강 시
            # detail list 채워질 수 있음. P2에서는 default empty 유지.
            soft_deviations=(),
        )
