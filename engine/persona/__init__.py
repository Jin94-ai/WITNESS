"""Persona Engine (v3.0 Persona transition).

Shared engine + persona profile 구조로 전환 (2026-04-23, Lee 지시).

- `profile`: PersonaProfile dataclass (pressure_sensitivity, motif_tendency,
  recovery_bias, relation_bias, motif_action_priors).
- `motif`: 8 response motifs with generic activation functions.
- `selector`: motif → action distribution + availability gate.

Rule #1 준수: 인물-특정 이름 없음. scenario content가 role binding 주입.
"""

from engine.persona.motif import (
    MOTIF_NAMES,
    MotifActivation,
    activate_motifs,
)
from engine.persona.profile import (
    DEFAULT_PROFILE,
    MotifTendency,
    PersonaProfile,
    PressureSensitivity,
    RecoveryBias,
    RelationBias,
    load_profile,
)
from engine.persona.selector import ActionSelection, select_action

__all__ = [
    "PersonaProfile",
    "PressureSensitivity",
    "MotifTendency",
    "RecoveryBias",
    "RelationBias",
    "DEFAULT_PROFILE",
    "load_profile",
    "MOTIF_NAMES",
    "MotifActivation",
    "activate_motifs",
    "select_action",
    "ActionSelection",
]
