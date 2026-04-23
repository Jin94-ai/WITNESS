"""Causal Critic -- Axis 3 of 4-axis rubric.

Spec §6.2 verbatim:
    축 3: Causal Coherence
    - 상태 변화와 행동의 인과 설명 가능 여부
    측정: 상태 전이가 이유를 가지는가 / 뜬금없는 점프 / 시간 경과 자연스러움
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CausalReport:
    unexplained_jumps: int       # count of unexplained state discontinuities
    mean_jump_size: float        # avg |Δstate| per tick (proxy)
    smoothness_score: float      # 0-1, 1 = no jumps
    notes: list[str]


class CausalCritic:
    """Measure causal coherence of state transitions.

    Heuristic: for each consecutive tick, compute the L1 norm of state
    changes. If a tick has a change > jump_threshold without a triggering
    event, flag as unexplained jump.
    """

    def __init__(
        self,
        *,
        jump_threshold: float = 5.0,
        state_fields: list[str] | None = None,
    ) -> None:
        self._jump_t = jump_threshold
        self._fields = state_fields or [
            "fear", "hope", "grief", "confusion", "love",
            "fatigue", "exhaustion_emotional",
        ]

    def evaluate(self, records: list[dict[str, Any]]) -> CausalReport:
        if len(records) < 2:
            return CausalReport(
                unexplained_jumps=0, mean_jump_size=0.0, smoothness_score=1.0,
                notes=["trajectory too short"],
            )

        jumps: list[float] = []
        unexplained = 0
        for i in range(len(records) - 1):
            prev = records[i].get("state", {})
            curr = records[i + 1].get("state", {})
            event = records[i + 1].get("event_triggered", False)
            size = 0.0
            for f in self._fields:
                size += abs(float(curr.get(f, 0.0)) - float(prev.get(f, 0.0)))
            jumps.append(size)
            if size > self._jump_t and not event:
                unexplained += 1

        mean_size = sum(jumps) / max(1, len(jumps))
        # Smoothness: 1 at mean_size=0, 0 at mean_size>=2*threshold
        smoothness = max(0.0, min(1.0, 1.0 - mean_size / (2.0 * self._jump_t)))
        return CausalReport(
            unexplained_jumps=unexplained,
            mean_jump_size=mean_size,
            smoothness_score=smoothness,
            notes=[
                f"total_ticks={len(records)}",
                f"unexplained_jumps={unexplained}",
            ],
        )
