"""Spike 6 Phase C — behavior cloning trainer smoke test.

Synthetic separable data verifies the MLP + trainer converge. No real
agent simulation here — that lands in a Peter-specific test later.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from engine.policies.neural.dataset import BehaviorCloningDataset  # noqa: E402
from engine.policies.neural.model import BehaviorCloningMLP  # noqa: E402
from engine.policies.neural.trainer import (  # noqa: E402
    load_checkpoint,
    save_checkpoint,
    train_behavior_cloning,
)


def _synthetic_separable(
    n_per_class: int = 80,
    n_actions: int = 3,
    feature_dim: int = 12,
    seed: int = 0,
) -> BehaviorCloningDataset:
    """Cluster-per-class with clean separation → should hit ~1.0 accuracy."""
    rng = np.random.default_rng(seed)
    X_list, y_list = [], []
    for cls in range(n_actions):
        # class centers on standard-basis axes, scaled.
        center = np.zeros(feature_dim, dtype=np.float32)
        center[cls % feature_dim] = 5.0
        noise = rng.normal(0.0, 0.3, size=(n_per_class, feature_dim)).astype(np.float32)
        X_list.append(center + noise)
        y_list.append(np.full(n_per_class, cls, dtype=np.int64))
    X = np.concatenate(X_list, axis=0)
    y = np.concatenate(y_list, axis=0)
    # Shuffle so ordering doesn't help the trainer.
    perm = rng.permutation(len(y))
    return BehaviorCloningDataset(
        X=X[perm], y=y[perm],
        action_vocab=[f"act_{i}" for i in range(n_actions)],
        feature_dim=feature_dim,
        agent_id="synthetic",
    )


def test_trainer_converges_on_separable_data() -> None:
    train = _synthetic_separable(n_per_class=80, n_actions=3, seed=0)
    val = _synthetic_separable(n_per_class=20, n_actions=3, seed=1)
    model, history = train_behavior_cloning(
        train, val, epochs=30, batch_size=32, lr=1e-2, seed=0,
    )
    assert history.final is not None
    # Easy problem — expect >90% val accuracy after 30 epochs.
    assert history.best_val_acc >= 0.9
    # Train loss decreases substantially.
    first_loss = history.per_epoch[0].train_loss
    final_loss = history.per_epoch[-1].train_loss
    assert final_loss < first_loss * 0.5


def test_trainer_early_stops_when_val_stops_improving() -> None:
    """Train and val drawn from independent random labelings — val_loss
    should plateau quickly and early stop should fire.
    """
    rng = np.random.default_rng(42)
    n, d, k = 60, 12, 3
    train_X = rng.normal(0.0, 1.0, size=(n, d)).astype(np.float32)
    train_y = rng.integers(0, k, size=n).astype(np.int64)
    val_X = rng.normal(0.0, 1.0, size=(n, d)).astype(np.float32)
    val_y = rng.integers(0, k, size=n).astype(np.int64)
    train_ds = BehaviorCloningDataset(
        X=train_X, y=train_y, action_vocab=["a", "b", "c"],
        feature_dim=d, agent_id="noise",
    )
    val_ds = BehaviorCloningDataset(
        X=val_X, y=val_y, action_vocab=["a", "b", "c"],
        feature_dim=d, agent_id="noise",
    )
    _, history = train_behavior_cloning(
        train_ds, val_ds, epochs=100, batch_size=16, lr=1e-2,
        early_stop_patience=3, seed=0,
    )
    # Independent random labels → val_loss plateaus or rises quickly.
    assert len(history.per_epoch) < 100


def test_save_and_load_checkpoint_round_trip(tmp_path: Path) -> None:
    train = _synthetic_separable(n_per_class=40, n_actions=3, seed=0)
    val = _synthetic_separable(n_per_class=10, n_actions=3, seed=1)
    model, _ = train_behavior_cloning(
        train, val, epochs=5, batch_size=32, lr=1e-2, seed=0,
    )
    path = tmp_path / "model.pt"
    save_checkpoint(model, path, train.action_vocab)

    restored, vocab = load_checkpoint(path)
    assert vocab == train.action_vocab
    assert restored.in_dim == model.in_dim
    assert restored.n_actions == model.n_actions
    # Predictions must match after restore (eval mode, same weights).
    model.eval()
    restored.eval()
    x_probe = torch.from_numpy(val.X[:5])
    with torch.no_grad():
        p_orig = model(x_probe)
        p_rest = restored(x_probe)
    assert torch.allclose(p_orig, p_rest, atol=1e-6)


def test_model_outputs_have_correct_shape() -> None:
    model = BehaviorCloningMLP(in_dim=12, n_actions=5, hidden=(16, 16))
    x = torch.zeros((7, 12))
    logits = model(x)
    assert logits.shape == (7, 5)
    probs = model.action_weights(x)
    assert probs.shape == (7, 5)
    # Softmax rows sum to 1.
    assert torch.allclose(probs.sum(dim=-1), torch.ones(7), atol=1e-5)
