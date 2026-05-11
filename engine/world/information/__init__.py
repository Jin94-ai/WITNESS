"""Information layer — Rumor registry + propagation (Phase 3 B direction).

Rumor 단위 epidemic-style propagation + distortion + credibility decay.

Rule #1: rumor content_tag + target_role 모두 generic. 특정 고유명은 payload dict에서만.
"""

from engine.world.information.rumor_registry import (
    SOCIAL_NETWORK_DEFAULT,
    Rumor,
    RumorRegistry,
)

__all__ = [
    "Rumor",
    "RumorRegistry",
    "SOCIAL_NETWORK_DEFAULT",
]
