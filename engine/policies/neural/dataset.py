"""Behavior-cloning dataset construction — person-agnostic.

Takes a ``run_fn(seed) -> MultiAgentResult`` (provided by the caller,
which owns the agent setup) and produces the (X, y) tensors a neural
policy needs to mimic rule-based action choices.

Spike 6 Phase B scope:

- Pure data pipeline. No model, no training, no torch dependency beyond
  returning numpy arrays (torch tensors are built later in ``trainer.py``).
- Stable action-id vocabulary so `y` is an int class index.
- Single agent filter — one model per agent id. Multi-agent joint models
  are out of scope for this spike.
- Reuses the existing ``TrainingSample`` + ``state_to_feature_vector``
  from ``engine.simulation.training_samples`` so this module stays small.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np

from engine.simulation.training_samples import (
    SampleStatistics,
    extract_samples,
    state_to_feature_vector,
    summarize_samples,
)


@dataclass
class BehaviorCloningDataset:
    """Training tensors + metadata for a single agent's behavior cloning.

    Attributes:
        X: shape (N, feature_dim), float32. State feature vectors.
        y: shape (N,), int64. Action class indices into ``action_vocab``.
        action_vocab: action_id strings, index-aligned with ``y``.
        feature_dim: X.shape[1].
        agent_id: the agent this dataset targets.
        stats: class-imbalance + event-rate diagnostics.
    """

    X: np.ndarray
    y: np.ndarray
    action_vocab: list[str]
    feature_dim: int
    agent_id: str
    stats: SampleStatistics = field(default_factory=lambda: SampleStatistics(
        n_samples=0, n_agents=0, agent_counts={}, action_counts={},
        event_rate=0.0, avg_tick_delta=0.0, feature_dim=12,
    ))

    @property
    def n_samples(self) -> int:
        return int(self.X.shape[0])

    @property
    def n_actions(self) -> int:
        return len(self.action_vocab)

    def save_feature_config(self, path: Path | str) -> None:
        """Persist vocab + shape for reproducibility.

        The weights file (trainer output) references this by path. Loading
        both together guarantees class-index → action-id correspondence.
        """
        payload = {
            "agent_id": self.agent_id,
            "feature_dim": self.feature_dim,
            "feature_schema": _DEFAULT_FEATURE_SCHEMA,
            "action_vocab": self.action_vocab,
            "n_samples": self.n_samples,
        }
        Path(path).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @classmethod
    def load_feature_config(cls, path: Path | str) -> dict[str, Any]:
        payload: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
        return payload


_DEFAULT_FEATURE_SCHEMA = [
    "emotions.fear", "emotions.hope", "emotions.grief",
    "emotions.confusion", "emotions.love",
    "physical.fatigue", "physical.hunger", "physical.health",
    "slow_state.moral_injury", "slow_state.identity_shift",
    "slow_state.event_trauma", "slow_state.trust_scar",
]


def build_behavior_cloning_dataset(
    run_fn: Callable[[int], Any],
    *,
    agent_id: str,
    seeds: list[int] | int,
    action_vocab: list[str] | None = None,
    drop_none_actions: bool = True,
) -> BehaviorCloningDataset:
    """Run a simulation factory N times, extract (state, action) pairs.

    Args:
        run_fn: callable that takes a seed and returns a MultiAgentResult
                (or any object with state_snapshots / action_histories /
                fired_events / fired_triggers attributes).
        agent_id: filter samples to this agent. One model per agent.
        seeds: list of seeds (or an int n_seeds → [0..n-1]).
        action_vocab: optional fixed vocab. If None, derived from observed
                      actions sorted alphabetically. Passing a vocab pins
                      class indices across datasets (e.g. train vs val).
        drop_none_actions: exclude samples with `action is None` (no
                           voluntary action fired this tick). Default True
                           so the classifier only learns active choices.

    Returns:
        BehaviorCloningDataset ready for trainer consumption.
    """
    seed_list = list(range(seeds)) if isinstance(seeds, int) else list(seeds)

    all_samples = []
    for seed in seed_list:
        result = run_fn(seed)
        all_samples.extend(extract_samples(result))

    agent_samples = [s for s in all_samples if s.agent_id == agent_id]
    if drop_none_actions:
        agent_samples = [s for s in agent_samples if s.action is not None]

    stats = summarize_samples(agent_samples)

    if action_vocab is None:
        observed = sorted({s.action for s in agent_samples if s.action is not None})
        action_vocab = list(observed)
    action_to_idx = {a: i for i, a in enumerate(action_vocab)}

    X_rows: list[list[float]] = []
    y_rows: list[int] = []
    for s in agent_samples:
        if s.action not in action_to_idx:
            continue  # action outside fixed vocab → skip
        X_rows.append(state_to_feature_vector(s.state))
        y_rows.append(action_to_idx[s.action])

    X = np.asarray(X_rows, dtype=np.float32) if X_rows else np.zeros((0, 12), dtype=np.float32)
    y = np.asarray(y_rows, dtype=np.int64)

    return BehaviorCloningDataset(
        X=X, y=y,
        action_vocab=action_vocab,
        feature_dim=X.shape[1] if X.size else 12,
        agent_id=agent_id,
        stats=stats,
    )


def train_val_split(
    dataset: BehaviorCloningDataset,
    val_fraction: float = 0.2,
    seed: int = 0,
) -> tuple[BehaviorCloningDataset, BehaviorCloningDataset]:
    """Deterministic shuffle + slice. Vocab shared across both splits."""
    n = dataset.n_samples
    if n == 0:
        return dataset, dataset
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    n_val = max(1, int(round(n * val_fraction)))
    val_idx, train_idx = perm[:n_val], perm[n_val:]

    def _sub(idx: np.ndarray) -> BehaviorCloningDataset:
        return BehaviorCloningDataset(
            X=dataset.X[idx], y=dataset.y[idx],
            action_vocab=dataset.action_vocab,
            feature_dim=dataset.feature_dim,
            agent_id=dataset.agent_id,
            stats=dataset.stats,
        )

    return _sub(train_idx), _sub(val_idx)
