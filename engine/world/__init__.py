"""Witness v3.0 World 3-layer structure (v2 spec §2).

Rule #16 준수: 외부 변수는 Primitive / Event / Derived Pressure 3 layer로 분리.

Layer A: Primitives  (environment state, persistent)
Layer B: Events      (short-lived events, can update primitives)
Layer C: Pressures   (derived from A+B, computed per-tick, not stored)

Note: 이 `engine/world/` 는 v3.0 신규 모듈. 프로젝트 루트의 `world/` (v2.0
World Engine, Spike 1-5) 는 별개 -- Rule #6 보존.
"""

from engine.world.events import Event, EventRegistry
from engine.world.pressure import PressureLayer, PressureVector
from engine.world.primitives import PrimitiveState, WorldPrimitive

__all__ = [
    "WorldPrimitive", "PrimitiveState",
    "Event", "EventRegistry",
    "PressureVector", "PressureLayer",
]
