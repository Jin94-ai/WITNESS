"""Variable-specific recovery profile (Phase G Step G5).

ChatGPT 지적 (Phase G spec §5.1):
    fear 9.9 → 0, confusion 9.92 → 0, grief 10.0 → 0 은 너무 완전하다.
    Recovery edge가 합성되어 과보정됐을 가능성.

전 tick 일괄 half-life 8 → **변수별 분리**:
    fear:      fast spike / fast decay    half-life  4.5   (floor 0.0)
    confusion: medium decay               half-life  7.0   (floor 0.0)
    grief:     slow decay + long tail     half-life 13.0   (floor 0.15)
    guilt:     slow decay + rebound ready half-life 11.0   (floor 0.10)
    shame:     context-dependent decay    half-life  6.0   (floor 0.05)
    anger:     medium decay               half-life  6.0   (floor 0.0)
    awe:       slow decay                 half-life 10.0   (floor 0.0)

Floor > 0 ensures long-tail echo (ChatGPT's "memory echo").
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class DecayProfile:
    """Per-tick decay parameterized by half-life + floor."""
    half_life_ticks: float
    floor: float = 0.0

    @property
    def factor(self) -> float:
        return math.pow(0.5, 1.0 / max(0.01, self.half_life_ticks))

    def apply(self, current: float) -> float:
        """Decay one tick toward floor.

        new = floor + (current - floor) * factor
        """
        if current <= self.floor:
            return current  # already at or below floor, no further decay
        return self.floor + (current - self.floor) * self.factor


# =============================================================================
# Registry (Phase G Step G5 defaults)
# =============================================================================

RECOVERY_PROFILES: dict[str, DecayProfile] = {
    "fear":      DecayProfile(half_life_ticks=4.5,  floor=0.0),
    "confusion": DecayProfile(half_life_ticks=7.0,  floor=0.0),
    "grief":     DecayProfile(half_life_ticks=13.0, floor=0.15),
    "anger":     DecayProfile(half_life_ticks=6.0,  floor=0.0),
    "awe":       DecayProfile(half_life_ticks=10.0, floor=0.0),
    # target-aware: guilt / shame handled separately (per-target)
    "guilt":     DecayProfile(half_life_ticks=11.0, floor=0.10),
    "shame":     DecayProfile(half_life_ticks=6.0,  floor=0.05),
}


def get_profile(field_name: str) -> DecayProfile | None:
    return RECOVERY_PROFILES.get(field_name)
