"""Soft constraints -- penalty-based distance from canonical attractors.

Unlike hard constraints (binary pass/fail), soft scoring produces a
scalar "drift" value used in Phase 4 rubric (novelty vs canon-copy).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SoftConstraintScorer:
    """Score a trajectory by distance from a canonical reference.

    Attributes:
        canonical_sequence: reference list of (tick, action_id) from canon.
        edit_distance_weight: weight for action-level edits (default 1.0).
        order_penalty_weight: weight for out-of-order matches (default 0.5).
    """

    canonical_sequence: list[tuple[int, str]]
    edit_distance_weight: float = 1.0
    order_penalty_weight: float = 0.5

    def _action_edit_distance(
        self, observed: list[tuple[int, str]],
    ) -> int:
        """Count (insert+delete+substitute) between observed and canonical
        action sequences. Simple Levenshtein on action_id lists.
        """
        a = [aid for _, aid in self.canonical_sequence]
        b = [aid for _, aid in observed]
        if not a:
            return len(b)
        if not b:
            return len(a)
        prev = list(range(len(b) + 1))
        curr = [0] * (len(b) + 1)
        for i in range(1, len(a) + 1):
            curr[0] = i
            for j in range(1, len(b) + 1):
                cost = 0 if a[i - 1] == b[j - 1] else 1
                curr[j] = min(
                    prev[j] + 1,        # delete
                    curr[j - 1] + 1,    # insert
                    prev[j - 1] + cost,  # substitute
                )
            prev, curr = curr[:], prev[:]
        return prev[-1]

    def score(self, observed: list[dict[str, Any]]) -> float:
        """Return a non-negative drift score (0 = exact match)."""
        obs_pairs = [(int(r.get("tick", 0)), str(r.get("action_id", "")))
                     for r in observed]
        edit = self._action_edit_distance(obs_pairs)

        # Order penalty: count inversions among matched action_ids
        canon_order = {aid: i for i, (_, aid) in enumerate(self.canonical_sequence)}
        positions = [canon_order[aid] for _, aid in obs_pairs if aid in canon_order]
        inversions = 0
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                if positions[i] > positions[j]:
                    inversions += 1

        return float(
            self.edit_distance_weight * edit
            + self.order_penalty_weight * inversions,
        )
