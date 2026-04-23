"""Behavior-cloning trainer — person-agnostic.

Given a ``BehaviorCloningDataset`` and a ``BehaviorCloningMLP``, minimize
cross-entropy on (state_features, action_idx) pairs. Returns a history of
per-epoch metrics so the caller (and Lee) can eyeball convergence.

Deterministic where possible:
- ``torch.manual_seed(seed)`` at entry
- ``numpy.random.default_rng(seed)`` for mini-batch shuffling

Device: CPU by default. CUDA is auto-detected and used if available.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
from torch import nn

from engine.policies.neural.dataset import BehaviorCloningDataset
from engine.policies.neural.model import BehaviorCloningMLP


@dataclass
class EpochMetrics:
    epoch: int
    train_loss: float
    train_acc: float
    val_loss: float
    val_acc: float


@dataclass
class TrainingHistory:
    per_epoch: list[EpochMetrics] = field(default_factory=list)

    @property
    def final(self) -> EpochMetrics | None:
        return self.per_epoch[-1] if self.per_epoch else None

    @property
    def best_val_acc(self) -> float:
        if not self.per_epoch:
            return 0.0
        return max(m.val_acc for m in self.per_epoch)

    def converged(self, min_improvement: float = 1e-4, patience: int = 5) -> bool:
        """Heuristic: val_loss stopped improving for ``patience`` epochs."""
        if len(self.per_epoch) <= patience:
            return False
        tail = self.per_epoch[-(patience + 1):]
        baseline = tail[0].val_loss
        return all(m.val_loss > baseline - min_improvement for m in tail[1:])


def _to_tensors(
    ds: BehaviorCloningDataset, device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor]:
    X = torch.from_numpy(ds.X).to(device)
    y = torch.from_numpy(ds.y).to(device)
    return X, y


def train_behavior_cloning(
    train_ds: BehaviorCloningDataset,
    val_ds: BehaviorCloningDataset,
    *,
    model: BehaviorCloningMLP | None = None,
    epochs: int = 50,
    batch_size: int = 64,
    lr: float = 1e-3,
    weight_decay: float = 0.0,
    seed: int = 0,
    device: str | None = None,
    early_stop_patience: int | None = 8,
) -> tuple[BehaviorCloningMLP, TrainingHistory]:
    """Train an MLP classifier on (state → action) pairs.

    Args:
        train_ds / val_ds: share the same ``action_vocab`` and ``feature_dim``.
        model: reuse an existing instance, or construct a fresh one when None.
        epochs: maximum epochs. Early stop may cut earlier.
        batch_size: mini-batch size.
        lr / weight_decay: Adam hyperparameters.
        seed: rng seed for reproducibility.
        device: "cpu" / "cuda" / None (auto).
        early_stop_patience: stop if val_loss hasn't improved for N epochs.
                             None disables.

    Returns:
        (trained model, training history)
    """
    assert train_ds.feature_dim == val_ds.feature_dim
    assert train_ds.n_actions == val_ds.n_actions
    assert train_ds.action_vocab == val_ds.action_vocab

    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)

    dev = torch.device(
        device if device is not None
        else ("cuda" if torch.cuda.is_available() else "cpu"),
    )

    if model is None:
        model = BehaviorCloningMLP(
            in_dim=train_ds.feature_dim, n_actions=train_ds.n_actions,
        )
    model = model.to(dev)

    X_tr, y_tr = _to_tensors(train_ds, dev)
    X_va, y_va = _to_tensors(val_ds, dev)

    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    loss_fn = nn.CrossEntropyLoss()

    history = TrainingHistory()
    n = train_ds.n_samples
    best_val = float("inf")
    no_improve = 0

    for epoch in range(1, epochs + 1):
        # --- train
        model.train()
        perm = rng.permutation(n)
        epoch_loss = 0.0
        epoch_correct = 0
        for start in range(0, n, batch_size):
            idx = perm[start:start + batch_size]
            xb = X_tr[idx]
            yb = y_tr[idx]
            opt.zero_grad()
            logits = model(xb)
            loss = loss_fn(logits, yb)
            loss.backward()
            opt.step()
            epoch_loss += float(loss.item()) * xb.size(0)
            epoch_correct += int((logits.argmax(dim=-1) == yb).sum().item())
        train_loss = epoch_loss / max(1, n)
        train_acc = epoch_correct / max(1, n)

        # --- validate
        model.eval()
        with torch.no_grad():
            v_logits = model(X_va)
            v_loss = float(loss_fn(v_logits, y_va).item())
            v_acc = float((v_logits.argmax(dim=-1) == y_va).float().mean().item())

        history.per_epoch.append(EpochMetrics(
            epoch=epoch, train_loss=train_loss, train_acc=train_acc,
            val_loss=v_loss, val_acc=v_acc,
        ))

        # --- early stop
        if early_stop_patience is not None:
            if v_loss + 1e-6 < best_val:
                best_val = v_loss
                no_improve = 0
            else:
                no_improve += 1
                if no_improve >= early_stop_patience:
                    break

    return model, history


def save_checkpoint(
    model: BehaviorCloningMLP, path: Path | str, action_vocab: list[str],
) -> None:
    """Persist weights + minimal metadata. Paired with feature_config.json."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "state_dict": model.state_dict(),
            "in_dim": model.in_dim,
            "n_actions": model.n_actions,
            "hidden": list(model.hidden),
            "action_vocab": action_vocab,
        },
        path,
    )


def load_checkpoint(path: Path | str) -> tuple[BehaviorCloningMLP, list[str]]:
    """Restore a previously-saved model."""
    payload = torch.load(Path(path), map_location="cpu", weights_only=False)
    model = BehaviorCloningMLP(
        in_dim=payload["in_dim"],
        n_actions=payload["n_actions"],
        hidden=tuple(payload["hidden"]),
    )
    model.load_state_dict(payload["state_dict"])
    return model, payload["action_vocab"]
