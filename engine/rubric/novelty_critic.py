"""Novelty Critic -- Axis 4 of 4-axis rubric.

Spec §6.2 verbatim:
    축 4: Novelty under Constraint
    - 정경 복사본이 아닌가
    측정: 정경 trajectory와의 거리 (너무 가까우면 복사) /
          무작위 일탈 여부 (너무 멀면 noise) /
          "의미 있는 다름" 지표
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NoveltyReport:
    canon_distance: float      # soft_drift from canon
    is_copy: bool              # drift < copy_threshold
    is_noise: bool             # drift > noise_threshold (random deviation)
    novelty_band: str          # "copy" | "meaningful" | "noise"
    notes: list[str]


class NoveltyCritic:
    """Classify trajectory novelty using canon drift from SoftConstraintScorer.

    Two thresholds:
        copy_threshold  : drift below this = canon copy (not novel)
        noise_threshold : drift above this = likely random deviation

    Meaningful novelty band: copy_threshold <= drift <= noise_threshold.
    """

    def __init__(
        self,
        *,
        copy_threshold: float = 1.5,
        noise_threshold: float = 15.0,
    ) -> None:
        self._copy_t = copy_threshold
        self._noise_t = noise_threshold

    def evaluate(self, canon_soft_drift: float) -> NoveltyReport:
        is_copy = canon_soft_drift < self._copy_t
        is_noise = canon_soft_drift > self._noise_t
        if is_copy:
            band = "copy"
        elif is_noise:
            band = "noise"
        else:
            band = "meaningful"
        return NoveltyReport(
            canon_distance=canon_soft_drift,
            is_copy=is_copy,
            is_noise=is_noise,
            novelty_band=band,
            notes=[
                f"copy_t={self._copy_t}",
                f"noise_t={self._noise_t}",
            ],
        )
