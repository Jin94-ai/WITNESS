"""Rumor registry + epidemic propagation.

Each Rumor = item with intensity / credibility / distortion / reach.
매 tick: propagate within network + decay + distortion accumulate.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

# Simple default network: all agents ↔ all agents (complete graph).
# Content layers can override.
SOCIAL_NETWORK_DEFAULT: dict[str, set[str]] = {}


@dataclass
class Rumor:
    rumor_id: str
    origin_tick: int
    origin_source: str                      # agent_id or event_id
    content_tag: str                        # "accusation" | "prophecy" | "secret" | "misdeed" | ...
    target_role: str | None                 # role or agent_id being talked about
    payload: dict[str, Any] = field(default_factory=dict)

    intensity: float = 0.8                  # 0-1
    credibility: float = 0.5                # 0-1
    distortion: float = 0.0                 # 0-1
    reach: set[str] = field(default_factory=set)

    # Dynamics
    propagation_rate: float = 0.3
    decay_rate: float = 0.08
    distortion_gain: float = 0.05


class RumorRegistry:
    """Holds active rumors + handles propagation + decay.

    Usage:
        registry = RumorRegistry(network)
        registry.spawn("accusation", target_role="outsider", ...)
        registry.step(tick=5)
    """

    def __init__(
        self,
        network: dict[str, set[str]] | None = None,
        *,
        cleanup_threshold: float = 0.03,
        authority_suppression: float = 0.0,  # 0-1
    ) -> None:
        self._rumors: dict[str, Rumor] = {}
        self._network = dict(network) if network else {}
        self._cleanup_t = cleanup_threshold
        self._authority_suppression = authority_suppression
        self._next_id = 0

    # -----------------------------------------------------------------
    # Spawn
    # -----------------------------------------------------------------

    def spawn(
        self,
        content_tag: str,
        *,
        target_role: str | None = None,
        origin_source: str,
        origin_tick: int,
        initial_reach: set[str] | None = None,
        intensity: float = 0.8,
        credibility: float = 0.5,
        payload: dict | None = None,
    ) -> Rumor:
        self._next_id += 1
        rumor = Rumor(
            rumor_id=f"r_{self._next_id:05d}",
            origin_tick=origin_tick,
            origin_source=origin_source,
            content_tag=content_tag,
            target_role=target_role,
            payload=payload or {},
            intensity=intensity,
            credibility=credibility,
            reach=set(initial_reach or [origin_source]),
        )
        self._rumors[rumor.rumor_id] = rumor
        return rumor

    # -----------------------------------------------------------------
    # Per-tick step
    # -----------------------------------------------------------------

    def step(
        self,
        tick: int,
        *,
        rng: random.Random | None = None,
    ) -> None:
        """Propagate + decay + cleanup. Mutates in place."""
        rng = rng or random.Random(tick)

        # 1. Propagation
        for rumor in list(self._rumors.values()):
            self._propagate_one(rumor, rng)

        # 2. Decay
        for rumor in list(self._rumors.values()):
            rumor.intensity = max(0.0, rumor.intensity - rumor.decay_rate)
            # credibility soft drift toward 0.5 (no new info → uncertainty)
            rumor.credibility += (0.5 - rumor.credibility) * 0.02

        # 3. Cleanup
        for rid in list(self._rumors.keys()):
            if self._rumors[rid].intensity < self._cleanup_t:
                del self._rumors[rid]

    def _propagate_one(self, rumor: Rumor, rng: random.Random) -> None:
        """Epidemic spread within social network."""
        new_reach = set()
        for agent in rumor.reach:
            neighbors = self._network.get(agent, set())
            for n in neighbors:
                if n in rumor.reach:
                    continue
                p_spread = (
                    rumor.intensity
                    * rumor.credibility
                    * rumor.propagation_rate
                    * (1 - self._authority_suppression)
                )
                if rng.random() < p_spread:
                    new_reach.add(n)
                    rumor.distortion = min(
                        1.0, rumor.distortion + rumor.distortion_gain,
                    )
                    rumor.intensity = max(0.0, rumor.intensity - 0.01)
        rumor.reach.update(new_reach)

    # -----------------------------------------------------------------
    # Queries
    # -----------------------------------------------------------------

    def get_active(self) -> list[Rumor]:
        return list(self._rumors.values())

    def get_about(self, target: str) -> list[Rumor]:
        return [r for r in self._rumors.values() if r.target_role == target]

    def reach_fraction(self, rumor_id: str, population_size: int) -> float:
        if rumor_id not in self._rumors:
            return 0.0
        return len(self._rumors[rumor_id].reach) / max(1, population_size)

    def __len__(self) -> int:
        return len(self._rumors)

    # -----------------------------------------------------------------
    # Network management
    # -----------------------------------------------------------------

    def set_network(self, network: dict[str, set[str]]) -> None:
        self._network = dict(network)

    def add_edge(self, a: str, b: str) -> None:
        self._network.setdefault(a, set()).add(b)
        self._network.setdefault(b, set()).add(a)

    # -----------------------------------------------------------------
    # Authority suppression
    # -----------------------------------------------------------------

    def set_authority_suppression(self, level: float) -> None:
        self._authority_suppression = max(0.0, min(1.0, level))
