"""AgentPosition / SpatialState — per-substep position tracking.

Tracks where each agent is at the current substep and how many
substeps remain until they arrive at their destination (if in
``transit``). No agent state mutation — this is world-layer
bookkeeping that lives alongside the per-person substep loop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class AgentPosition:
    """Snapshot of one agent's spatial state at one substep."""

    agent_id: str
    current_location: str
    destination: str | None = None
    substeps_remaining: int = 0

    @property
    def is_in_transit(self) -> bool:
        return self.current_location == "transit"


@dataclass
class SpatialState:
    """Mutable per-substep spatial state for all agents.

    The world-side runner advances this each substep. Queries are
    read-only and tolerate missing agents (return None, don't raise).
    """

    positions: dict[str, AgentPosition] = field(default_factory=dict)

    # --- Queries --------------------------------------------------------
    def where(self, agent_id: str) -> str | None:
        p = self.positions.get(agent_id)
        return p.current_location if p is not None else None

    def agents_at(self, location_id: str) -> list[str]:
        return [
            aid for aid, p in self.positions.items()
            if p.current_location == location_id
        ]

    def agents_in_transit(self) -> list[str]:
        return [aid for aid, p in self.positions.items() if p.is_in_transit]

    def same_location(self, a: str, b: str) -> bool:
        loc_a = self.where(a)
        loc_b = self.where(b)
        if loc_a is None or loc_b is None:
            return False
        if loc_a == "transit" or loc_b == "transit":
            return False
        return loc_a == loc_b

    # --- Mutations ------------------------------------------------------
    def place(self, agent_id: str, location_id: str) -> None:
        """Teleport an agent to a location (used for initial placement)."""
        self.positions[agent_id] = AgentPosition(
            agent_id=agent_id, current_location=location_id,
        )

    def begin_move(self, agent_id: str, destination: str, cost_substeps: int) -> None:
        """Mark an agent as in transit toward destination."""
        if cost_substeps <= 0:
            self.place(agent_id, destination)
            return
        self.positions[agent_id] = AgentPosition(
            agent_id=agent_id,
            current_location="transit",
            destination=destination,
            substeps_remaining=cost_substeps,
        )

    def advance_one_substep(self) -> None:
        """Decrement substeps_remaining for all in-transit agents and
        arrive those that reach 0."""
        updated: dict[str, AgentPosition] = {}
        for aid, p in self.positions.items():
            if p.is_in_transit:
                remaining = p.substeps_remaining - 1
                if remaining <= 0 and p.destination is not None:
                    updated[aid] = AgentPosition(
                        agent_id=aid, current_location=p.destination,
                    )
                else:
                    updated[aid] = AgentPosition(
                        agent_id=aid, current_location="transit",
                        destination=p.destination,
                        substeps_remaining=remaining,
                    )
            else:
                updated[aid] = p
        self.positions = updated

    def initial(self, initial_positions: Iterable[tuple[str, str]]) -> "SpatialState":
        """Populate starting positions (agent_id, location_id pairs)."""
        for aid, loc in initial_positions:
            self.place(aid, loc)
        return self
