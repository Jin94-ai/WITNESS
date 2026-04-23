"""Layer 5 — population-level social signals. Spike 1A: crowd density; Spike 3: +rumours."""

from world.social.crowd import CrowdLayer
from world.social.rumors import RumorLayer

__all__ = ["CrowdLayer", "RumorLayer"]
