"""DecisionPolicy Protocol — the single injection point for neural policies.

Spike 6 Rule #11 ("신경망 전환 시 규칙 기반 fallback을 제거하지 않는다"):
Rule-based and neural behavior selection must share an interface so the
call-site can swap without knowing which is active.

The protocol is **minimal** by design. A policy sees:

- the full AgentState (same as rule-based weight_formula input)
- the pre-filtered list of available actions (preconditions already passed)
- an environment object (forwarded untouched, may be None)

and returns a parallel list of non-negative weights. The sampler
(``engine.simulation.decision.decide_action``) owns the rng and the final
``rng.choices`` call.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from engine.core.event import ActionOption
from engine.core.state import AgentState


@runtime_checkable
class DecisionPolicy(Protocol):
    """Replace a rule-based weight computation with a learned one."""

    def weights(
        self,
        state: AgentState,
        options: list[ActionOption],
        environment: Any = None,
    ) -> list[float]:
        """Return non-negative weights aligned with ``options``.

        The caller already filtered by preconditions, so every ``options[i]``
        is legal. Returning all zeros is allowed (caller falls back).
        """
        ...
