"""Layer protocol — common interface for every world-simulation layer.

Every layer (environment, economy, politics, factions, social) exposes:

- ``layer_id`` — stable short name used in telemetry and ordering.
- ``tick(state, ctx)`` — pure function that returns the next per-layer state
  slice. The caller (``world.simulation.world_tick``) is responsible for
  composing the full WorldState; layers see only what they need.
- ``initial_state(config)`` — build the layer's initial state slice from the
  serialised ``WorldConfig`` payload, so tests and demos start from an
  auditable, content-driven snapshot.

The protocol is intentionally narrow so that Spike 1A can ship with only the
calendar and crowd layers and still leave the shape that Spikes 1B–1D will
extend. Review notes that drove this design:

- **Review #1 (explicit dynamics)**: every layer documents its update equation
  + time constant + observation outputs in its module docstring.
- **Review #2 (cross-layer brakes)**: a layer that depends on another layer
  must do so via a snapshot it receives through ``LayerContext`` — never a
  mutable reference — so the ``world_tick`` module can decide when to insert
  delays / thresholds / saturation.
- **Review #4 (variable dt)**: every ``tick`` accepts ``dt_days``; Spike 1A
  fixes it at 1.0 but nothing in the protocol assumes that.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from world.core.world_state import WorldState


@dataclass(frozen=True)
class LayerContext:
    """Per-tick inputs handed to a ``Layer.tick`` call.

    The context is a snapshot, not a live reference, so a layer cannot reach
    into another layer's in-progress state during the same tick. ``world_tick``
    is responsible for composing a new ``LayerContext`` between layers when
    the sequenced updates require it (with or without explicit delay buffers).
    """

    tick_index: int
    """0-based tick counter, monotone increasing."""

    dt_days: float
    """Simulated days advanced by this tick. Spike 1A pins this at 1.0."""

    world_snapshot: WorldState
    """Frozen snapshot of ``WorldState`` as of the *start* of this tick."""

    rng_seed: int
    """Per-run seed; layers derive their own sub-streams from this deterministic source."""

    aggregated_effects: dict[str, float] = field(default_factory=dict)
    """Spike 2+ agent-to-world aggregated effects. Empty in Spike 1A."""


@runtime_checkable
class Layer(Protocol):
    """Interface every world layer implements.

    Layers are pure: ``tick`` returns a new state value; it does not mutate the
    snapshot. Each concrete layer also exposes a short ``describe_dynamics``
    method (see subclasses) that tests use to assert the documented update
    equation matches the implementation (review #1).
    """

    layer_id: str

    def initial_state(self, config: dict[str, Any]) -> Any:
        """Build the layer's initial state from ``content/worlds/...`` payload."""
        ...

    def tick(self, state: Any, ctx: LayerContext) -> Any:
        """Return the next state slice for this layer."""
        ...
