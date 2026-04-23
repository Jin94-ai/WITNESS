"""Runtime wrapper: trained MLP → DecisionPolicy.

Given a ``BehaviorCloningMLP`` and the ``action_vocab`` it was trained on,
``NeuralDecisionPolicy`` implements the ``DecisionPolicy`` Protocol so a
``decide_action`` call-site can consult it in place of rule-based weights.

**Rule #11 fallback** is built into the return contract: for any option
whose ``action_id`` is absent from the vocab, the weight is zero. When every
option is unknown, the returned list is all zeros; the sampler (see
``engine.simulation.decision.decide_action``) interprets all-zero as
"policy abstains" and falls through to rule-based weights.
"""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
import torch

from engine.core.event import ActionOption
from engine.core.state import AgentState
from engine.policies.neural.model import BehaviorCloningMLP
from engine.simulation.training_samples import state_to_feature_vector

FeatureFn = Callable[[AgentState], list[float]]


class NeuralDecisionPolicy:
    """Adapts a trained classifier to the DecisionPolicy protocol."""

    def __init__(
        self,
        model: BehaviorCloningMLP,
        action_vocab: list[str],
        feature_fn: FeatureFn | None = None,
        device: str | torch.device | None = None,
    ) -> None:
        self.model = model
        self.action_vocab = list(action_vocab)
        self._vocab_index = {a: i for i, a in enumerate(self.action_vocab)}
        self.feature_fn = feature_fn or state_to_feature_vector
        dev = device if device is not None else (
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self._device = torch.device(dev)
        self.model = self.model.to(self._device)
        self.model.eval()

    def weights(
        self,
        state: AgentState,
        options: list[ActionOption],
        environment: Any = None,  # noqa: ARG002  (part of protocol)
    ) -> list[float]:
        if not options:
            return []
        feats = self.feature_fn(state)
        x = torch.tensor([feats], dtype=torch.float32, device=self._device)
        with torch.no_grad():
            probs = self.model.action_weights(x)[0].cpu().numpy()
        out: list[float] = []
        for opt in options:
            idx = self._vocab_index.get(opt.action_id)
            out.append(float(probs[idx]) if idx is not None else 0.0)
        return out

    @classmethod
    def from_checkpoint(
        cls,
        checkpoint_path: str,
        feature_fn: FeatureFn | None = None,
        device: str | torch.device | None = None,
    ) -> "NeuralDecisionPolicy":
        """Convenience: rebuild model + vocab from a saved checkpoint."""
        from engine.policies.neural.trainer import load_checkpoint
        model, vocab = load_checkpoint(checkpoint_path)
        return cls(model=model, action_vocab=vocab, feature_fn=feature_fn, device=device)

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "neural_mlp",
            "n_actions": len(self.action_vocab),
            "action_vocab": self.action_vocab,
            "device": str(self._device),
            "in_dim": self.model.in_dim,
            "hidden": list(self.model.hidden),
        }


def uniform_random_weights(
    state: AgentState,  # noqa: ARG001
    options: list[ActionOption],
    environment: Any = None,  # noqa: ARG001
) -> list[float]:
    """Diagnostic policy: returns uniform weights (for dual-path tests)."""
    return [1.0 / max(1, len(options))] * len(options)


def always_abstain_weights(
    state: AgentState,  # noqa: ARG001
    options: list[ActionOption],
    environment: Any = None,  # noqa: ARG001
) -> list[float]:
    """Diagnostic policy: returns all zeros, triggering rule-based fallback."""
    _ = np  # keep numpy imported for downstream helpers
    return [0.0] * len(options)
