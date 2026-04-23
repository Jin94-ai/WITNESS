"""Hard constraints -- binary violation checker.

Spec §5.2 Layer D:
    - 역사적 모순 금지      (historical contradiction)
    - 정경 충돌 금지         (canonical contradiction)
    - 시대착오 금지          (anachronism)
    - 신성모독 금지          (sacred-text violation, Rule #2)
    - 특정 인물 지식 범위 제한 (knowledge scope limit)

Rule #1: this module takes content-provided allowlists and fixed-action
maps. It does not hardcode scenario names.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConstraintViolation:
    """A single rule violation record."""

    rule: str           # e.g., "canonical_contradiction", "anachronism"
    details: str        # human-readable explanation
    tick: int | None = None
    action_id: str | None = None


class HardConstraintChecker:
    """Check a trajectory against hard constraints.

    Args:
        action_vocabulary: set of valid action_ids for this scenario
                           (anachronism check)
        fixed_actions: {tick: action_id} for canonical-fixed moments
                       (canonical contradiction check)
        sacred_text_guards: list of substrings that must NOT appear in
                            any visible_signal if its source is a primary
                            sacred figure (Rule #2 guard)
    """

    def __init__(
        self,
        *,
        action_vocabulary: set[str] | None = None,
        fixed_actions: dict[int, str] | None = None,
        sacred_text_guards: list[str] | None = None,
    ) -> None:
        self._vocab = set(action_vocabulary) if action_vocabulary is not None else None
        self._fixed = dict(fixed_actions) if fixed_actions is not None else {}
        self._sacred_guards = list(sacred_text_guards or [])

    def check_action_vocabulary(
        self, tick: int, action_id: str,
    ) -> ConstraintViolation | None:
        """Anachronism: action must belong to scenario's allowed vocabulary."""
        if self._vocab is None:
            return None
        if action_id not in self._vocab:
            return ConstraintViolation(
                rule="anachronism",
                details=f"action_id '{action_id}' not in scenario vocabulary",
                tick=tick, action_id=action_id,
            )
        return None

    def check_canonical_fixed(
        self, tick: int, action_id: str,
    ) -> ConstraintViolation | None:
        """Canonical contradiction: if tick has a fixed action, actual must match."""
        expected = self._fixed.get(tick)
        if expected is None:
            return None
        if action_id != expected:
            return ConstraintViolation(
                rule="canonical_contradiction",
                details=f"tick {tick} fixed='{expected}' but got '{action_id}'",
                tick=tick, action_id=action_id,
            )
        return None

    def check_sacred_text_signal(
        self, tick: int, visible_signal: str,
    ) -> ConstraintViolation | None:
        """Rule #2: sacred figure's visible_signal must not deviate from canon.

        Content provides guard substrings (e.g., "개역개정") that mark a
        signal as scripture-verbatim. Any deviation is a violation.
        """
        if not self._sacred_guards:
            return None
        # If any guard is missing → violation
        for guard in self._sacred_guards:
            if guard not in visible_signal:
                return ConstraintViolation(
                    rule="sacred_text_violation",
                    details=(
                        f"signal lacks guard '{guard}': {visible_signal!r}"
                    ),
                    tick=tick,
                )
        return None

    def check_all(
        self,
        records: list[dict[str, Any]],
    ) -> list[ConstraintViolation]:
        """Run all checks on a trajectory.

        Args:
            records: list of {tick, action_id, visible_signal?, is_sacred?}

        Returns:
            list of violations (empty = passes).
        """
        violations: list[ConstraintViolation] = []
        for rec in records:
            tick = int(rec.get("tick", -1))
            action_id = str(rec.get("action_id", ""))
            # Vocabulary
            v = self.check_action_vocabulary(tick, action_id)
            if v:
                violations.append(v)
            # Canonical fixed
            v = self.check_canonical_fixed(tick, action_id)
            if v:
                violations.append(v)
            # Sacred-text (only if record marked sacred)
            if rec.get("is_sacred"):
                signal = str(rec.get("visible_signal", ""))
                v = self.check_sacred_text_signal(tick, signal)
                if v:
                    violations.append(v)
        return violations
