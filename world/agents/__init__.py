"""World-side agent adapters (Spike 5 Phase 5A).

The engine's ``AgentState`` + ``AgentBehaviorProfile`` remain the
primitive. World-side agents are thin adapters that combine:
- world-layer context (location, other agents, rumours, factions)
- canonical constraints (fixed-date events)
- multi-path influence emitters (visible actions → WorldEffect channels)

Jesus is the first canonical world-side agent. Peter / Judas /
Caiaphas / Crowd all satisfy the same ``BaseWorldAgent`` protocol
through the default ``ContentBackedWorldAgent`` adapter — so Spike 5
does not require any content rewrite; it just exposes the adapter.

Nothing in this module modifies ``engine/`` (ABSOLUTE RULE #6).
"""

from world.agents.base import (
    BaseWorldAgent,
    ContentBackedWorldAgent,
    WorldActionDecision,
    WorldAgentContext,
)
from world.agents.caiaphas import CaiaphasAgent, CaiaphasAgentOutcome, CaiaphasState
from world.agents.jesus import JesusAgent, JesusAgentOutcome
from world.agents.light import BarabbasAgent, JamesAgent, JohnAgent, ThomasAgent
from world.agents.pilate import PilateAgent, PilateAgentOutcome, PilateState

__all__ = [
    "BaseWorldAgent",
    "ContentBackedWorldAgent",
    "WorldActionDecision",
    "WorldAgentContext",
    "JesusAgent",
    "JesusAgentOutcome",
    "PilateAgent",
    "PilateAgentOutcome",
    "PilateState",
    "CaiaphasAgent",
    "CaiaphasAgentOutcome",
    "CaiaphasState",
    "BarabbasAgent",
    "JohnAgent",
    "JamesAgent",
    "ThomasAgent",
]
