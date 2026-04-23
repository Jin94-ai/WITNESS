"""Phase 3 — re-train on pipeline v1 dataset + rich evaluation.

Metrics (spec §4.2):
- Val accuracy (overall + per-class)
- Per-class precision / recall / F1
- Behavior fidelity: symmetric KL divergence between neural and rule-based
  action distributions on held-out states (ChatGPT core suggestion)
- Log-likelihood (NLL)
- Confusion matrix
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402

from engine.core.state import AgentState, EmotionalState, PhysicalState, SlowState  # noqa: E402
from engine.io.loader import load_behavior_profile  # noqa: E402
from engine.policies.neural.dataset import BehaviorCloningDataset  # noqa: E402
from engine.policies.neural.model import BehaviorCloningMLP  # noqa: E402
from engine.policies.neural.trainer import (  # noqa: E402
    save_checkpoint,
    train_behavior_cloning,
)
from scripts.data_pipeline._common import CONTENT, register_domain_types  # noqa: E402

PIPELINE_FINAL = ROOT / "data" / "person" / "pipeline_v1" / "final"
TRAINED_DIR = CONTENT / "peter" / "trained"


def load_final_dataset() -> BehaviorCloningDataset:
    payload = np.load(PIPELINE_FINAL / "dataset.npz")
    X, y = payload["X"], payload["y"]
    meta = json.loads((PIPELINE_FINAL / "meta.json").read_text(encoding="utf-8"))
    return BehaviorCloningDataset(
        X=X.astype(np.float32), y=y.astype(np.int64),
        action_vocab=meta["action_vocab"],
        feature_dim=X.shape[1],
        agent_id="peter",
    )


def state_from_feature(vec: np.ndarray) -> AgentState:
    """Rebuild a minimal AgentState from a 12-dim feature vector."""
    state = AgentState(agent_id="peter")
    state.emotions = EmotionalState(
        fear=float(vec[0]), hope=float(vec[1]), grief=float(vec[2]),
        confusion=float(vec[3]), love=float(vec[4]),
    )
    state.physical = PhysicalState(
        fatigue=float(vec[5]), hunger=float(vec[6]), health=float(vec[7]),
    )
    state.slow_state = SlowState(
        moral_injury=float(vec[8]), identity_shift=float(vec[9]),
        event_trauma=float(vec[10]), trust_scar=float(vec[11]),
    )
    return state


def rule_based_weights(state: AgentState, action_vocab: list[str]) -> np.ndarray:
    """Rule-based weight for each action in vocab. Unavailable → 0."""
    profile = load_behavior_profile(CONTENT / "peter" / "behavior_profile.json")
    action_by_id = {a.action_id: a for a in profile.actions}
    weights = np.zeros(len(action_vocab), dtype=np.float64)
    for i, aid in enumerate(action_vocab):
        action = action_by_id.get(aid)
        if action is None:
            continue
        # Preconditions check — if not satisfied, weight=0.
        # AgentAction's `is_available` takes (tick, state), but we don't have
        # tick here; preconditions tied to cooldowns will be skipped.
        # For pure state-based weight formulae this is fine.
        try:
            w = action.weight_formula.compute_weight(state, None)
            weights[i] = float(max(0.0, w))
        except Exception:
            weights[i] = 0.0
    return weights


def symmetric_kl(p: np.ndarray, q: np.ndarray, eps: float = 1e-8) -> float:
    p = np.clip(p, eps, 1.0)
    q = np.clip(q, eps, 1.0)
    p /= p.sum()
    q /= q.sum()
    return float(0.5 * (np.sum(p * np.log(p / q)) + np.sum(q * np.log(q / p))))


def compute_per_class_metrics(y_true: np.ndarray, y_pred: np.ndarray, vocab: list[str]) -> dict:
    per_class: dict[str, dict[str, float]] = {}
    for idx, name in enumerate(vocab):
        true_mask = y_true == idx
        pred_mask = y_pred == idx
        tp = int((true_mask & pred_mask).sum())
        fp = int((~true_mask & pred_mask).sum())
        fn = int((true_mask & ~pred_mask).sum())
        support = int(true_mask.sum())
        precision = tp / (tp + fp) if tp + fp > 0 else 0.0
        recall = tp / (tp + fn) if tp + fn > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0
        per_class[name] = {
            "support": support, "precision": precision,
            "recall": recall, "f1": f1,
        }
    return per_class


def behavior_fidelity(
    model: BehaviorCloningMLP, X_val: np.ndarray, vocab: list[str],
    *, max_samples: int = 500,
) -> dict:
    """Per-state KL divergence between neural and rule-based distributions."""
    n = min(len(X_val), max_samples)
    idxs = np.random.default_rng(0).choice(len(X_val), size=n, replace=False)

    kl_values: list[float] = []
    rb_zero_count = 0
    for i in idxs:
        vec = X_val[i]
        state = state_from_feature(vec)
        rb_w = rule_based_weights(state, vocab)
        if rb_w.sum() <= 0:
            rb_zero_count += 1
            continue
        rb_prob = rb_w / rb_w.sum()

        with torch.no_grad():
            x = torch.tensor([vec], dtype=torch.float32)
            neural_prob = F.softmax(model(x), dim=-1)[0].cpu().numpy()

        kl_values.append(symmetric_kl(neural_prob, rb_prob))

    return {
        "n_evaluated": len(kl_values),
        "n_rule_zero": rb_zero_count,
        "kl_mean": float(np.mean(kl_values)) if kl_values else float("nan"),
        "kl_median": float(np.median(kl_values)) if kl_values else float("nan"),
        "kl_std": float(np.std(kl_values)) if kl_values else float("nan"),
        "kl_min": float(np.min(kl_values)) if kl_values else float("nan"),
        "kl_max": float(np.max(kl_values)) if kl_values else float("nan"),
    }


def main() -> int:
    register_domain_types()
    print("[Phase 3] Loading pipeline_v1 final dataset...")
    ds = load_final_dataset()
    print(f"  {ds.n_samples} samples, {ds.n_actions} actions: {ds.action_vocab}")

    # Stratified split
    rng = np.random.default_rng(0)
    indices_per_class: dict[int, list[int]] = {}
    for i, y in enumerate(ds.y.tolist()):
        indices_per_class.setdefault(y, []).append(i)
    val_idx, train_idx = [], []
    for cls, idxs in indices_per_class.items():
        rng.shuffle(idxs)
        n_val = max(1, int(len(idxs) * 0.2))
        val_idx.extend(idxs[:n_val])
        train_idx.extend(idxs[n_val:])
    val_idx.sort()
    train_idx.sort()

    train = BehaviorCloningDataset(
        X=ds.X[train_idx], y=ds.y[train_idx],
        action_vocab=ds.action_vocab, feature_dim=ds.feature_dim, agent_id="peter",
    )
    val = BehaviorCloningDataset(
        X=ds.X[val_idx], y=ds.y[val_idx],
        action_vocab=ds.action_vocab, feature_dim=ds.feature_dim, agent_id="peter",
    )
    print(f"  train={train.n_samples}  val={val.n_samples} (stratified)")

    print("\n[Phase 3] Training MLP (30 epochs, lr=1e-2)...")
    model, history = train_behavior_cloning(
        train, val, epochs=50, batch_size=64, lr=1e-2, seed=0,
        early_stop_patience=10,
    )
    final = history.final
    assert final is not None
    print(
        f"  epoch {final.epoch}  train_acc={final.train_acc:.3f}  "
        f"val_acc={final.val_acc:.3f}  best_val_acc={history.best_val_acc:.3f}",
    )

    # --- Evaluation ---
    print("\n[Phase 3] Computing evaluation metrics...")
    model.eval()
    with torch.no_grad():
        X_val_t = torch.from_numpy(val.X)
        logits = model(X_val_t)
        y_pred = logits.argmax(dim=-1).cpu().numpy()
        nll = float(F.cross_entropy(logits, torch.from_numpy(val.y)).item())

    acc = float((y_pred == val.y).mean())
    from collections import Counter
    majority = max(Counter(val.y.tolist()).values()) / val.n_samples

    per_class = compute_per_class_metrics(val.y, y_pred, ds.action_vocab)
    fidelity = behavior_fidelity(model, val.X, ds.action_vocab)

    print(f"\n  overall accuracy: {acc:.3f} (majority baseline: {majority:.3f})")
    print(f"  NLL:              {nll:.3f}")
    print("\n  per-class F1 (support):")
    for a, m in sorted(per_class.items(), key=lambda kv: -kv[1]["support"]):
        print(
            f"    {a:<26} F1={m['f1']:.3f}  P={m['precision']:.3f}  "
            f"R={m['recall']:.3f}  (n={m['support']})",
        )

    print("\n  behavior fidelity (symmetric KL to rule-based):")
    print(f"    n_evaluated: {fidelity['n_evaluated']}")
    print(f"    KL mean:   {fidelity['kl_mean']:.4f}")
    print(f"    KL median: {fidelity['kl_median']:.4f}")
    print(f"    KL std:    {fidelity['kl_std']:.4f}")

    # Persist
    TRAINED_DIR.mkdir(parents=True, exist_ok=True)
    weights_path = TRAINED_DIR / "peter_bc_v2.pt"
    save_checkpoint(model, weights_path, ds.action_vocab)
    feature_cfg = TRAINED_DIR / "peter_bc_v2.feature_config.json"
    ds.save_feature_config(feature_cfg)

    report = {
        "dataset_samples": ds.n_samples,
        "train_samples": train.n_samples,
        "val_samples": val.n_samples,
        "action_vocab": ds.action_vocab,
        "final_epoch": final.epoch,
        "train_acc": final.train_acc,
        "val_acc": final.val_acc,
        "best_val_acc": history.best_val_acc,
        "nll": nll,
        "majority_baseline": majority,
        "per_class_metrics": per_class,
        "behavior_fidelity": fidelity,
    }
    report_path = ROOT / "docs" / "person" / "stage2_v2_evaluation.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n  checkpoint:   {weights_path}")
    print(f"  feature cfg:  {feature_cfg}")
    print(f"  report JSON:  {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
