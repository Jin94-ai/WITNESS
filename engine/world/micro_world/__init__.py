"""Micro-world engine (Phase 5).

Multi-agent simulation with crowd + rumor + spatial layers.
Wires persona engine (agents) + world process engine (crowd/rumor/space).
"""

from engine.world.micro_world.world import (
    AgentHandle,
    MicroWorld,
    MicroWorldConfig,
    WorldStep,
)

__all__ = ["AgentHandle", "MicroWorld", "MicroWorldConfig", "WorldStep"]
