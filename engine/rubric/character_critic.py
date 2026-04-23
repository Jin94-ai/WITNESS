"""Character Critic -- Axis 1 of 4-axis rubric.

Spec §6.2 verbatim:
    축 1: Character Consistency
    - 측정: 충동성 패턴, 관계 반응, 두려움-용기 전환

v3 discovery definitions §3.2 measurement methods:
    (1) impulsivity_pattern_match
    (2) relationship_specific_response_check
    (3) fear_courage_oscillation

Rule #1: this critic is person-agnostic. Content provides the baseline
patterns (scenario-specific impulsivity-score baseline etc.).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CharacterReport:
    impulsivity_score: float       # 0-1 (higher = more impulsivity patterns)
    relationship_coherence: float  # 0-1 (higher = matches expected pattern)
    oscillation_score: float       # 0-1 (higher = more fear-courage oscillation)
    composite: float               # weighted mean of above
    notes: list[str]


class CharacterCritic:
    """Measure trajectory's character consistency against a baseline profile.

    The baseline profile (content-provided) specifies:
        impulsivity_threshold: min rapid-switch frequency
        relationship_patterns: {event_cat: expected_action_cat}
        oscillation_target: expected sign-change frequency for a fear-like variable
    """

    def __init__(
        self,
        *,
        impulsivity_threshold: float = 0.1,
        relationship_patterns: dict[str, set[str]] | None = None,
        oscillation_target: float = 0.15,
    ) -> None:
        self._imp_t = impulsivity_threshold
        self._rel_patterns = relationship_patterns or {}
        self._osc_target = oscillation_target

    def _impulsivity(self, records: list[dict[str, Any]]) -> tuple[float, str]:
        """Count consecutive direction-flip patterns.

        Heuristic: detect 'A → (large state change) → B' where A and B are
        opposite-category actions in close succession. Uses consecutive
        different-kind action runs as a proxy.
        """
        if len(records) < 2:
            return 0.0, "trajectory too short for impulsivity"
        flips = 0
        for i in range(len(records) - 1):
            a = records[i].get("action_kind", "")
            b = records[i + 1].get("action_kind", "")
            if a and b and a != b:
                flips += 1
        rate = flips / max(1, len(records) - 1)
        score = min(1.0, rate / max(0.01, self._imp_t))
        return score, f"flip_rate={rate:.3f} vs threshold={self._imp_t:.3f}"

    def _relationship(self, records: list[dict[str, Any]]) -> tuple[float, str]:
        """For each (event_category, action_category) pair, check that the
        action belongs to the expected set for that event."""
        if not self._rel_patterns:
            return 1.0, "no relationship patterns provided"
        matches = 0
        total = 0
        for r in records:
            ec = r.get("event_category")
            ak = r.get("action_kind")
            if ec is None or ak is None:
                continue
            total += 1
            expected = self._rel_patterns.get(ec)
            if expected is None or ak in expected:
                matches += 1
        if total == 0:
            return 1.0, "no typed records"
        score = matches / total
        return score, f"{matches}/{total} relationship-consistent"

    def _oscillation(self, records: list[dict[str, Any]]) -> tuple[float, str]:
        """Count sign changes in a fear-like variable across ticks."""
        fear_series = [r.get("fear_like") for r in records if r.get("fear_like") is not None]
        if len(fear_series) < 3:
            return 0.0, "fear series too short"
        # Sign changes in first-difference
        diffs = [fear_series[i + 1] - fear_series[i] for i in range(len(fear_series) - 1)]
        sign_changes = sum(
            1 for i in range(len(diffs) - 1) if diffs[i] * diffs[i + 1] < 0
        )
        rate = sign_changes / max(1, len(diffs) - 1)
        # Score = 1 if rate == target, drop off with |rate - target|
        deviation = abs(rate - self._osc_target)
        score = max(0.0, 1.0 - deviation * 3.0)
        return score, f"osc_rate={rate:.3f} target={self._osc_target:.3f}"

    def evaluate(self, records: list[dict[str, Any]]) -> CharacterReport:
        imp, imp_note = self._impulsivity(records)
        rel, rel_note = self._relationship(records)
        osc, osc_note = self._oscillation(records)
        composite = (imp + rel + osc) / 3.0
        return CharacterReport(
            impulsivity_score=imp,
            relationship_coherence=rel,
            oscillation_score=osc,
            composite=composite,
            notes=[imp_note, rel_note, osc_note],
        )
