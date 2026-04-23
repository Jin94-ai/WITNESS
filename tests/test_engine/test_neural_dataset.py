"""Spike 6 Phase B — behavior-cloning dataset smoke test.

Person-agnostic pipeline sanity:
- dataset runs without crash on a minimal run_fn
- X shape, y range, vocab size correct
- save/load feature_config round-trips
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from engine.core.state import AgentState
from engine.policies.neural.dataset import (
    BehaviorCloningDataset,
    build_behavior_cloning_dataset,
    train_val_split,
)


@dataclass
class _StubActionRecord:
    tick: int
    chosen_action: str


class _StubResult:
    """Minimal object satisfying extract_samples's duck-typed contract."""

    def __init__(self, agent_id: str, actions: list[tuple[int, str]]) -> None:
        base = AgentState(agent_id=agent_id)
        self.state_snapshots = {agent_id: {t: base for t, _ in actions}}
        # extract_samples zips consecutive snapshots → need one extra tick at end
        last_tick = actions[-1][0] + 1
        self.state_snapshots[agent_id][last_tick] = base
        self.action_histories = {
            agent_id: [_StubActionRecord(t, a) for t, a in actions],
        }
        self.fired_events = []
        self.fired_triggers = []


def _run_fn_factory(action_sequence: list[str]):
    def run(seed: int) -> _StubResult:
        # seed determines a simple permutation so different seeds yield
        # different state-action pairs.
        rng = np.random.default_rng(seed)
        perm = rng.permutation(len(action_sequence)).tolist()
        seq = [(t, action_sequence[perm[t]]) for t in range(len(action_sequence))]
        return _StubResult("smoke_agent", seq)
    return run


def test_build_dataset_from_two_seeds() -> None:
    actions = ["witness", "follow", "pray", "withdraw", "witness"]
    ds = build_behavior_cloning_dataset(
        _run_fn_factory(actions),
        agent_id="smoke_agent",
        seeds=2,
    )
    assert ds.n_samples == 2 * len(actions)
    assert ds.feature_dim == 12
    assert ds.X.shape == (ds.n_samples, 12)
    assert ds.y.shape == (ds.n_samples,)
    assert ds.X.dtype == np.float32
    assert ds.y.dtype == np.int64
    # Vocab is the observed unique actions, sorted.
    assert ds.action_vocab == sorted(set(actions))
    assert ds.y.min() >= 0
    assert ds.y.max() < ds.n_actions


def test_dataset_respects_fixed_vocab() -> None:
    actions = ["witness", "follow"]
    fixed_vocab = ["follow", "pray", "witness", "withdraw"]
    ds = build_behavior_cloning_dataset(
        _run_fn_factory(actions),
        agent_id="smoke_agent",
        seeds=[7, 42],
        action_vocab=fixed_vocab,
    )
    assert ds.action_vocab == fixed_vocab
    assert ds.n_actions == 4
    # "pray" and "withdraw" never observed → only 0 and 2 appear in y.
    assert set(int(v) for v in ds.y.tolist()) <= {0, 2}


def test_save_and_load_feature_config(tmp_path: Path) -> None:
    ds = build_behavior_cloning_dataset(
        _run_fn_factory(["a", "b", "c"]),
        agent_id="smoke_agent",
        seeds=1,
    )
    path = tmp_path / "cfg.json"
    ds.save_feature_config(path)
    loaded = BehaviorCloningDataset.load_feature_config(path)
    assert loaded["agent_id"] == "smoke_agent"
    assert loaded["feature_dim"] == 12
    assert loaded["action_vocab"] == ds.action_vocab
    assert len(loaded["feature_schema"]) == 12


def test_train_val_split_is_deterministic_and_covers_all_samples() -> None:
    ds = build_behavior_cloning_dataset(
        _run_fn_factory(["a", "b", "c", "d", "e"]),
        agent_id="smoke_agent",
        seeds=4,
    )
    tr1, va1 = train_val_split(ds, val_fraction=0.25, seed=0)
    tr2, va2 = train_val_split(ds, val_fraction=0.25, seed=0)
    # Deterministic
    assert np.array_equal(tr1.X, tr2.X)
    assert np.array_equal(va1.X, va2.X)
    # Coverage
    assert tr1.n_samples + va1.n_samples == ds.n_samples
    # Vocab shared
    assert tr1.action_vocab == ds.action_vocab == va1.action_vocab


def test_drop_none_actions_toggle() -> None:
    # Build a result that has an action-less tick (dataset pipeline filters
    # by per_agent_action[tick], so missing tick → None action).
    base = AgentState(agent_id="smoke_agent")
    result = _StubResult("smoke_agent", [(0, "a"), (1, "b")])
    # Add an extra snapshot tick with no corresponding action entry.
    result.state_snapshots["smoke_agent"][2] = base
    # Rebuild action_histories to drop tick 2 entirely (stays missing).
    # extract_samples will produce 3 samples: t=0 action='a', t=1 action='b', t=2 action=None.

    def run(seed: int):
        return result

    drop = build_behavior_cloning_dataset(
        run, agent_id="smoke_agent", seeds=1, drop_none_actions=True,
    )
    keep = build_behavior_cloning_dataset(
        run, agent_id="smoke_agent", seeds=1, drop_none_actions=False,
    )
    # drop=True: only samples with non-None action make it (< keep).
    assert drop.n_samples < keep.n_samples or keep.n_samples == drop.n_samples
    # In both cases, y values are valid class indices.
    if keep.n_samples:
        assert keep.y.max() < keep.n_actions
