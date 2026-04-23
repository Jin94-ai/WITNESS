"""BaseWorldAgent — world-layer agent adapter protocol (Phase 5A).

The world engine doesn't replace the Person Engine's ``AgentState`` +
``AgentBehaviorProfile``; it *wraps* them with world-layer context
(location, other agents, rumours). All world-side agents — including
Jesus — satisfy the same lightweight protocol so the simulation loop
can iterate over them uniformly.

ABSOLUTE RULE #3 v1.1 (jesus as agent): the interface is identical
for Peter, Judas, Caiaphas, Crowd, and Jesus. Jesus has larger
influence bias in content but no mechanism-level special treatment.

Spike 5 Part 1 scope: protocol + default adapter + Jesus class. Spike 5
Part 2 (scheduled separately) plugs these into IntegratedWorldRunner.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class WorldAgentContext:
    """Read-only per-substep context handed to a world agent's ``decide``.

    Intentionally narrow: spatial + co-located agents + rumour digest +
    day index. Expansion happens in Part 2 as new percepts arrive.
    """

    agent_id: str
    substep_index: int
    day_index: int
    current_location: str
    co_located_agents: list[str] = field(default_factory=list)
    recent_rumours: list[str] = field(default_factory=list)
    crowd_density_here: float = 0.0
    surveillance_level_here: float = 0.0
    active_feast: str = "none"
    # Domain-specific hints (optional) — e.g. "peter_fear", "judas_disill".
    agent_state_digest: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class WorldActionDecision:
    """One selected action with its world-effect fan-out.

    Multi-path influence emitters (Phase 5A §4.2.2) are encoded as
    multiple effects per decision. The adapter returns this structure
    instead of a scalar action_id to keep the fan-out explicit.
    """

    action_id: str
    # Channel → scalar magnitude. The caller aggregates these into
    # ``aggregated_effects`` just like Spike 2's Sync Layer.
    world_effects: dict[str, float] = field(default_factory=dict)
    # Free-form metadata (e.g. canonical_flag, target_agent).
    meta: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class BaseWorldAgent(Protocol):
    """World-side agent interface.

    A concrete implementation picks an action based on the
    world-layer context. The Person-Engine action (with its state
    effects) is resolved separately via the existing content pack.
    """

    agent_id: str

    def decide(self, ctx: WorldAgentContext) -> WorldActionDecision:
        ...


class ContentBackedWorldAgent:
    """Default world-agent adapter: delegates to a content behavior profile.

    This class is the 'existing Peter/Judas/etc. but wearing a world-side
    jacket' — it implements ``BaseWorldAgent`` by consulting a content
    pack's action list. For agents that need only content-driven
    behavior, no subclass is required.

    Spike 5 Part 1 scope: provides the interface + a stub implementation
    that returns a no-op decision. Part 2 will wire real
    content-backed decision-making.
    """

    def __init__(self, agent_id: str, content_actions: list[str] | None = None) -> None:
        self.agent_id = agent_id
        self.content_actions = content_actions or []

    def decide(self, ctx: WorldAgentContext) -> WorldActionDecision:
        # Part 1: no-op fallback. Subclasses (Jesus) override.
        return WorldActionDecision(
            action_id=self.content_actions[0] if self.content_actions else "idle",
            world_effects={},
            meta={"ctx_substep": ctx.substep_index},
        )
