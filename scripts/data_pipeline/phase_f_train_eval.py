"""Phase F -- 재학습 + 평가 (spec §7).

Uses 15-dim extended features (Phase B) on balanced_for_training (Phase C)
built with data-driven zones (Phase A re-design).

Evaluation per spec §7.2:
- Val accuracy + per-class F1 + macro F1
- Behavior fidelity: per-state KL (1회차 KL 1.44 대비)
- Rare action 구제 확인 (weep/fall_asleep/follow_at_distance/run_to_tomb)
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402

from engine.policies.neural.dataset import BehaviorCloningDataset  # noqa: E402
from engine.policies.neural.model import BehaviorCloningMLP  # noqa: E402
from engine.policies.neural.trainer import (  # noqa: E402
    save_checkpoint,
    train_behavior_cloning,
)
from scripts.data_pipeline._common import (  # noqa: E402
    CONTENT,
    register_domain_types,
    run_peter,
)
from scripts.data_pipeline.extended_features import (  # noqa: E402
    extract_event_context_per_tick,
    state_to_extended_feature_vector,
)

PIPELINE = ROOT / "data" / "person" / "pipeline_v2"


def stratified_split(X, y, val_fraction=0.2, seed=0):
    rng = np.random.default_rng(seed)
    per_cls: dict[int, list[int]] = defaultdict(list)
    for i, lbl in enumerate(y.tolist()):
        per_cls[lbl].append(i)
    val_idx, train_idx = [], []
    for cls, idxs in per_cls.items():
        rng.shuffle(idxs)
        n_val = max(1, int(len(idxs) * val_fraction))
        val_idx.extend(idxs[:n_val])
        train_idx.extend(idxs[n_val:])
    val_idx.sort(); train_idx.sort()
    return np.asarray(train_idx), np.asarray(val_idx)


def rule_based_voluntary_weights(state, vocab):
    from engine.io.loader import load_behavior_profile
    profile = load_behavior_profile(CONTENT / "peter" / "behavior_profile.json")
    by_id = {a.action_id: a for a in profile.actions}
    w = np.zeros(len(vocab), dtype=np.float64)
    for i, aid in enumerate(vocab):
        a = by_id.get(aid)
        if a is None:
            continue
        try:
            w[i] = max(0.0, float(a.weight_formula.compute_weight(state, None)))
        except Exception:
            w[i] = 0.0
    return w


def symmetric_kl(p, q, eps=1e-8):
    p = np.clip(p, eps, 1.0); p = p / p.sum()
    q = np.clip(q, eps, 1.0); q = q / q.sum()
    return float(0.5 * (np.sum(p * np.log(p / q)) + np.sum(q * np.log(q / p))))


def rebuild_state_from_12feat(vec):
    from engine.core.state import AgentState, EmotionalState, PhysicalState, SlowState
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


def fidelity_on_natural(model, vocab, n_seeds=10, max_tick=200):
    register_domain_types()
    X_rows, actions, event_ids = [], [], []
    for seed in range(n_seeds):
        result = run_peter(seed=seed, max_tick=max_tick)
        ctx_by_tick = extract_event_context_per_tick(result)
        action_recs = result.action_histories.get("peter", [])
        event_by_tick = {r.tick: r.event_id for r in action_recs}
        from engine.simulation.training_samples import extract_samples
        samples = extract_samples(result)
        for s in samples:
            if s.agent_id != "peter" or s.action is None:
                continue
            ctx = ctx_by_tick.get(s.tick, {})
            ext = state_to_extended_feature_vector(
                s.state,
                recent_event_id=ctx.get("recent_event_id"),
                time_since_event=float(ctx.get("time_since_event", 0)),
                hazard_proximity=float(ctx.get("hazard_proximity", max_tick)),
                max_tick_norm=float(max_tick),
            )
            X_rows.append(ext)
            actions.append(s.action)
            event_ids.append(event_by_tick.get(s.tick, "unknown"))
    X = np.asarray(X_rows, dtype=np.float32)

    with torch.no_grad():
        logits = model(torch.from_numpy(X))
        probs = F.softmax(logits, dim=-1).cpu().numpy()
        pred_idx = logits.argmax(-1).cpu().numpy()
    pred_actions = [vocab[i] for i in pred_idx]

    voluntary_mask = np.array([eid == "voluntary" for eid in event_ids])

    all_match = np.array([a == p for a, p in zip(actions, pred_actions)])
    overall = float(all_match.mean())
    vol_rate = float(all_match[voluntary_mask].mean()) if voluntary_mask.any() else 0.0
    evt_rate = float(all_match[~voluntary_mask].mean()) if (~voluntary_mask).any() else 0.0

    # KL on voluntary (compare softmax vs rule-based voluntary weights)
    kls = []
    for i in np.where(voluntary_mask)[0]:
        vec12 = X[i, :12]
        state = rebuild_state_from_12feat(vec12)
        rb = rule_based_voluntary_weights(state, vocab)
        if rb.sum() <= 0:
            continue
        rb_p = rb / rb.sum()
        kls.append(symmetric_kl(probs[i], rb_p))

    return {
        "overall_match": overall,
        "voluntary_match": vol_rate,
        "event_match": evt_rate,
        "voluntary_kl_mean": float(np.mean(kls)) if kls else float("nan"),
        "voluntary_kl_median": float(np.median(kls)) if kls else float("nan"),
        "n_samples": int(X.shape[0]),
        "n_voluntary": int(voluntary_mask.sum()),
    }


def main() -> int:
    # Load balanced_for_training
    ds_path = PIPELINE / "balanced_for_training" / "dataset.npz"
    meta = json.loads((PIPELINE / "balanced_for_training" / "meta.json").read_text(encoding="utf-8"))
    data = np.load(ds_path)
    X, y = data["X"].astype(np.float32), data["y"].astype(np.int64)
    vocab = meta["action_vocab"]
    print(f"[Phase F] dataset X={X.shape}  {len(vocab)} classes  (feature_dim=15)")

    # Stratified split
    tr_idx, va_idx = stratified_split(X, y, val_fraction=0.2, seed=0)
    train = BehaviorCloningDataset(
        X=X[tr_idx], y=y[tr_idx],
        action_vocab=vocab, feature_dim=15, agent_id="peter",
    )
    val = BehaviorCloningDataset(
        X=X[va_idx], y=y[va_idx],
        action_vocab=vocab, feature_dim=15, agent_id="peter",
    )
    print(f"  train={train.n_samples}  val={val.n_samples}")

    # Train with in_dim=15 (Phase F §7.1)
    model = BehaviorCloningMLP(in_dim=15, n_actions=len(vocab), hidden=(32, 32))
    model, hist = train_behavior_cloning(
        train, val, model=model,
        epochs=60, batch_size=64, lr=1e-3, seed=0, early_stop_patience=12,
    )
    f = hist.final
    assert f is not None
    print(f"\n  epoch {f.epoch}  train_acc={f.train_acc:.3f}  val_acc={f.val_acc:.3f}  "
          f"best={hist.best_val_acc:.3f}")

    # Evaluation
    model.eval()
    with torch.no_grad():
        v_logits = model(torch.from_numpy(val.X))
        v_pred = v_logits.argmax(-1).numpy()
        nll = float(F.cross_entropy(v_logits, torch.from_numpy(val.y)).item())

    # Per-class F1
    per_cls_metrics = {}
    f1s = []
    for i, a in enumerate(vocab):
        mask_t = val.y == i
        mask_p = v_pred == i
        tp = int((mask_t & mask_p).sum())
        fp = int((~mask_t & mask_p).sum())
        fn = int((mask_t & ~mask_p).sum())
        support = int(mask_t.sum())
        P = tp / (tp + fp) if tp + fp else 0.0
        R = tp / (tp + fn) if tp + fn else 0.0
        F1 = 2 * P * R / (P + R) if P + R else 0.0
        per_cls_metrics[a] = {"support": support, "precision": P, "recall": R, "f1": F1}
        f1s.append(F1)

    print("\n  Per-class F1 (val):")
    for a, m in sorted(per_cls_metrics.items(), key=lambda kv: -kv[1]["support"]):
        print(f"    {a:<24} F1={m['f1']:.3f}  P={m['precision']:.3f}  R={m['recall']:.3f}  n={m['support']}")

    macro_f1 = float(np.mean(f1s))
    majority = max(Counter(val.y.tolist()).values()) / val.n_samples
    print(f"\n  macro F1:         {macro_f1:.3f}")
    print(f"  overall val_acc:  {f.val_acc:.3f} (majority={majority:.3f})")
    print(f"  NLL:              {nll:.3f}")
    print(f"  F1 >= 0.5: {sum(1 for x in f1s if x >= 0.5)}/{len(vocab)}")
    print(f"  F1 = 0:    {sum(1 for x in f1s if x == 0)}/{len(vocab)}")

    # Fidelity on natural trajectory
    print("\n  Fidelity check on natural trajectories (10 seeds x 200 tick)...")
    fid = fidelity_on_natural(model, vocab, n_seeds=10, max_tick=200)
    print(f"    overall match:    {fid['overall_match']:.3f}  (1회차 v2: 0.394)")
    print(f"    voluntary match:  {fid['voluntary_match']:.3f}  (1회차 v2: 0.300)")
    print(f"    event match:      {fid['event_match']:.3f}  (1회차 v2: 0.880)")
    print(f"    voluntary KL mean:   {fid['voluntary_kl_mean']:.3f}  (spec §7.2.2 target: < 1.44)")
    print(f"    voluntary KL median: {fid['voluntary_kl_median']:.3f}")

    # Persist
    save_checkpoint(model, CONTENT / "peter" / "trained" / "peter_bc_v4.pt", vocab)
    train.save_feature_config(CONTENT / "peter" / "trained" / "peter_bc_v4.feature_config.json")

    report = {
        "dataset_samples": train.n_samples + val.n_samples,
        "train_samples": train.n_samples,
        "val_samples": val.n_samples,
        "feature_dim": 15,
        "action_vocab": vocab,
        "final_epoch": f.epoch,
        "train_acc": f.train_acc,
        "val_acc": f.val_acc,
        "best_val_acc": hist.best_val_acc,
        "macro_f1": macro_f1,
        "nll": nll,
        "majority_baseline": majority,
        "per_class_metrics": per_cls_metrics,
        "fidelity": fid,
        "f1_ge_0.5_count": sum(1 for x in f1s if x >= 0.5),
        "f1_eq_0_count": sum(1 for x in f1s if x == 0),
    }
    out = ROOT / "docs" / "person" / "stage2_v4_evaluation.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n  saved checkpoint: content/peter/trained/peter_bc_v4.pt")
    print(f"  saved report:     {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
