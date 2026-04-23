"""Small MLP for behavior-cloning — person-agnostic.

Minimal architecture by design (spec §3 "작은 모델부터"):

    input: state feature vector (default 12-dim)
    hidden: 2 × Linear(32) + ReLU
    output: logits over action classes

The caller supplies ``in_dim`` (feature length) and ``n_actions`` (class
count). The model itself knows nothing about which agent it represents.
"""

from __future__ import annotations

import torch
from torch import nn


class BehaviorCloningMLP(nn.Module):
    """Feed-forward classifier mapping state features to action logits."""

    def __init__(
        self,
        in_dim: int,
        n_actions: int,
        hidden: tuple[int, ...] = (32, 32),
    ) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = in_dim
        for h in hidden:
            layers.append(nn.Linear(prev, h))
            layers.append(nn.ReLU())
            prev = h
        layers.append(nn.Linear(prev, n_actions))
        self.net = nn.Sequential(*layers)
        self.in_dim = in_dim
        self.n_actions = n_actions
        self.hidden = hidden

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out: torch.Tensor = self.net(x)
        return out

    @torch.no_grad()
    def action_weights(self, x: torch.Tensor) -> torch.Tensor:
        """Softmax probabilities (for sampling). Batched."""
        logits = self.forward(x)
        return torch.softmax(logits, dim=-1)
