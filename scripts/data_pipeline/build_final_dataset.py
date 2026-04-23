"""Phase 2F + orchestrator — merge all harvests, balance, add noise, save.

Reads the four harvest directories under ``data/person/pipeline_v1/``:
- baseline/
- rare_sweep/
- mild/
- stress/

Merges, builds a stable action_vocab, balances per-class down to a target
count (oversample if short), adds small gaussian noise (σ=0.3 per feature,
clipped to [0, 10]), and writes the final NPZ + metadata ready for
``train_behavior_cloning``.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PIPELINE_ROOT = ROOT / "data" / "person" / "pipeline_v1"
SOURCE_DIRS = ["baseline", "rare_sweep", "mild", "stress"]


def _load_source(name: str) -> dict[str, Any] | None:
    path = PIPELINE_ROOT / name
    if not (path / "X.npy").exists():
        return None
    X = np.load(path / "X.npy")
    meta = json.loads((path / "meta.json").read_text(encoding="utf-8"))
    return {"name": name, "X": X, "actions": meta["actions"]}


def merge_all() -> tuple[np.ndarray, list[str], list[str]]:
    Xs: list[np.ndarray] = []
    actions: list[str] = []
    sources: list[str] = []
    for name in SOURCE_DIRS:
        src = _load_source(name)
        if src is None:
            print(f"  [merge] {name}: missing, skipped")
            continue
        print(f"  [merge] {name}: {src['X'].shape[0]} samples")
        Xs.append(src["X"])
        actions.extend(src["actions"])
        sources.extend([name] * len(src["actions"]))
    X = np.concatenate(Xs, axis=0) if Xs else np.zeros((0, 12), dtype=np.float32)
    return X, actions, sources


def balance_per_class(
    X: np.ndarray, actions: list[str], sources: list[str],
    *, target_per_class: int = 800, max_per_class: int = 1500, seed: int = 0,
) -> tuple[np.ndarray, list[str], list[str]]:
    """Down-sample majority / copy-upsample minorities to roughly equalize.

    - If a class has ≥ target_per_class, take a random target_per_class subset.
    - If < target_per_class, **keep all** (oversampling only done in training
      via class weights, not here — avoids duplicate-row artefacts).
    - Never exceed max_per_class per class.
    """
    rng = np.random.default_rng(seed)
    per_class_idx: dict[str, list[int]] = {}
    for i, a in enumerate(actions):
        per_class_idx.setdefault(a, []).append(i)

    selected: list[int] = []
    for a, idxs in per_class_idx.items():
        pool_size = min(len(idxs), max_per_class)
        take = min(pool_size, target_per_class) if len(idxs) >= target_per_class else len(idxs)
        chosen = rng.choice(idxs, size=take, replace=False).tolist()
        selected.extend(chosen)

    selected.sort()
    X_sel = X[selected]
    actions_sel = [actions[i] for i in selected]
    sources_sel = [sources[i] for i in selected]
    return X_sel, actions_sel, sources_sel


def add_gaussian_noise(
    X: np.ndarray, std: float = 0.3, seed: int = 1,
) -> np.ndarray:
    """Per-element gaussian noise, clipped. Spec §3.7.2."""
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, std, size=X.shape).astype(np.float32)
    out = X + noise
    # Clip per-column: fear/hope/grief/confusion/love/fatigue/hunger/health in [0,10],
    # moral_injury/event_trauma/trust_scar in [0,10], identity_shift in [-10,10].
    lo = np.array([0.0]*9 + [-10.0] + [0.0, 0.0], dtype=np.float32)
    hi = np.array([10.0]*12, dtype=np.float32)
    return np.clip(out, lo, hi)


def build_final(
    *, target_per_class: int = 800,
    noise_std: float = 0.3,
) -> dict[str, Any]:
    X, actions, sources = merge_all()
    print(f"\n  merged total: {X.shape[0]}")
    print(f"  merged distribution: {dict(Counter(actions))}")
    print(f"  source split: {dict(Counter(sources))}")

    vocab = sorted(set(actions))
    action_to_idx = {a: i for i, a in enumerate(vocab)}

    X_bal, actions_bal, sources_bal = balance_per_class(
        X, actions, sources, target_per_class=target_per_class,
    )
    print(f"\n  after balance: {X_bal.shape[0]}")
    print(f"  balanced dist: {dict(Counter(actions_bal))}")

    y_bal = np.asarray([action_to_idx[a] for a in actions_bal], dtype=np.int64)

    X_noisy = add_gaussian_noise(X_bal, std=noise_std)

    return {
        "X": X_noisy, "y": y_bal,
        "action_vocab": vocab,
        "sources": sources_bal,
        "n_samples": int(X_noisy.shape[0]),
        "meta": {
            "target_per_class": target_per_class,
            "noise_std": noise_std,
        },
    }


def main() -> int:
    out = PIPELINE_ROOT / "final"
    out.mkdir(parents=True, exist_ok=True)
    final = build_final()
    np.savez(
        out / "dataset.npz",
        X=final["X"], y=final["y"],
    )
    (out / "meta.json").write_text(
        json.dumps({
            "action_vocab": final["action_vocab"],
            "sources": final["sources"],
            "n_samples": final["n_samples"],
            "meta": final["meta"],
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n[FINAL] {final['n_samples']} samples, {len(final['action_vocab'])} actions")
    print(f"  saved: {out}/dataset.npz")
    print(f"  vocab: {final['action_vocab']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
