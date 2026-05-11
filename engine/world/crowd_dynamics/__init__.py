"""Crowd Dynamics meso-layer (Phase 3 B direction).

Independent crowd state — density / alignment / volatility / blame /
accusation_amplification / phase transition.

Rule #1 준수: 모든 이름 generic. 시나리오 content 가 crowd instance 이름 주입.
"""

from engine.world.crowd_dynamics.state import (
    CROWD_PHASES,
    CrowdPhase,
    CrowdState,
    compute_phase,
    step_crowd,
)

__all__ = [
    "CrowdState",
    "CrowdPhase",
    "CROWD_PHASES",
    "compute_phase",
    "step_crowd",
]
