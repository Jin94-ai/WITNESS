"""Phase-orthogonal utility: behavior-fidelity check.

Measures how closely a trained DecisionPolicy (typically a neural MLP)
reproduces the engine's action choices on naturally-sampled states.

Two metrics (spec §7.2):
- **match_rate**: hard-decision agreement (1 if MLP argmax == engine chose,
  else 0). Easy to interpret; loses softness.
- **symmetric_kl**: softmax(neural) vs softmax(rule_based_weights) KL div,
  averaged over sampled states. Captures "how different is the whole
  distribution", not just the mode. Needed to distinguish "noise" from
  "genuine alternative policy".

This module is **direction-agnostic** (HARNESS H6): it runs regardless of
whether Phase B / D / F is chosen next. Output JSON feeds the next
iteration's decision.

Split measurement:
- **voluntary only** -- states where engine chose a voluntary action
  (event_id == 'voluntary'). Rule-based policy is well-defined here.
- **event-triggered** -- engine chose an event-option action. Rule-based
  at arbitrary state is undefined (no event fired), so KL not meaningful;
  only match_rate reported.

This split matters because mixed fidelity conflates two failure modes:
(a) MLP learns wrong voluntary policy
(b) MLP cannot distinguish "normal state" from "event moment" without
    temporal context (Phase B concern)
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

from engine.io.loader import load_behavior_profile  # noqa: E402
from engine.policies.neural.trainer import load_checkpoint  # noqa: E402
from engine.simulation.training_samples import (  # noqa: E402
    extract_samples,
    state_to_feature_vector,
)
from scripts.data_pipeline._common import (  # noqa: E402
    CONTENT,
    register_domain_types,
    run_peter,
)


def _rule_based_voluntary_weights(state, vocab):
    """Rule-based weight for each action in vocab; 0 for non-voluntary
    actions (not in behavior_profile)."""
    profile = load_behavior_profile(CONTENT / "peter" / "behavior_profile.json")
    by_id = {a.action_id: a for a in profile.actions}
    w = np.zeros(len(vocab), dtype=np.float64)
    for i, aid in enumerate(vocab):
        action = by_id.get(aid)
        if action is None:
            continue
        try:
            w[i] = max(0.0, float(action.weight_formula.compute_weight(state, None)))
        except Exception:
            w[i] = 0.0
    return w


def _symmetric_kl(p, q, eps=1e-8):
    p = np.clip(p, eps, 1.0); p = p / p.sum()
    q = np.clip(q, eps, 1.0); q = q / q.sum()
    return float(0.5 * (np.sum(p * np.log(p / q)) + np.sum(q * np.log(q / p))))


def collect_natural_trajectories(n_seeds: int, max_tick: int) -> dict:
    """Run N seeds × M tick canonical Peter, return paired (state, action,
    event_id) records via extract_samples (so state_t ↔ action_t page)."""
    states_feat = []
    actions = []
    event_ids = []

    for seed in range(n_seeds):
        result = run_peter(seed=seed, max_tick=max_tick)
        samples = extract_samples(result)
        # per_agent_action map: tick -> (action, event_id)
        action_recs = result.action_histories.get("peter", [])
        event_by_tick = {r.tick: r.event_id for r in action_recs}
        for s in samples:
            if s.agent_id != "peter" or s.action is None:
                continue
            states_feat.append(state_to_feature_vector(s.state))
            actions.append(s.action)
            event_ids.append(event_by_tick.get(s.tick, "unknown"))

    X = np.asarray(states_feat, dtype=np.float32)
    return {
        "X": X,
        "actions": actions,
        "event_ids": event_ids,
    }


def fidelity_report(
    *, checkpoint: str | Path, n_seeds: int = 10, max_tick: int = 200,
    out_json: str | Path | None = None,
) -> dict:
    register_domain_types()
    model, vocab = load_checkpoint(checkpoint)
    model.eval()

    print(f"[fidelity] harvesting {n_seeds}x{max_tick} natural trajectories...")
    nat = collect_natural_trajectories(n_seeds, max_tick)
    print(f"  {nat['X'].shape[0]} natural (state, action) pairs")

    with torch.no_grad():
        logits = model(torch.from_numpy(nat["X"]))
        neural_probs = F.softmax(logits, dim=-1).cpu().numpy()
        pred_idx = logits.argmax(dim=-1).cpu().numpy()
    pred_actions = [vocab[i] for i in pred_idx]

    # Split by voluntary / event
    voluntary_mask = np.array([eid == "voluntary" for eid in nat["event_ids"]])
    event_mask = ~voluntary_mask

    # Match rate overall
    all_match = np.array([a == p for a, p in zip(nat["actions"], pred_actions)])
    overall_rate = float(all_match.mean())
    vol_rate = float(all_match[voluntary_mask].mean()) if voluntary_mask.any() else 0.0
    evt_rate = float(all_match[event_mask].mean()) if event_mask.any() else 0.0

    # KL (voluntary only, where rule-based policy is well-defined)
    kls = []
    kl_per_action: dict[str, list[float]] = {}
    for i in np.where(voluntary_mask)[0]:
        state_vec = nat["X"][i]
        from engine.core.state import AgentState, EmotionalState, PhysicalState, SlowState
        state = AgentState(agent_id="peter")
        state.emotions = EmotionalState(
            fear=float(state_vec[0]), hope=float(state_vec[1]),
            grief=float(state_vec[2]), confusion=float(state_vec[3]),
            love=float(state_vec[4]),
        )
        state.physical = PhysicalState(
            fatigue=float(state_vec[5]), hunger=float(state_vec[6]),
            health=float(state_vec[7]),
        )
        state.slow_state = SlowState(
            moral_injury=float(state_vec[8]), identity_shift=float(state_vec[9]),
            event_trauma=float(state_vec[10]), trust_scar=float(state_vec[11]),
        )
        rb_w = _rule_based_voluntary_weights(state, vocab)
        if rb_w.sum() <= 0:
            continue
        rb_p = rb_w / rb_w.sum()
        kl = _symmetric_kl(neural_probs[i], rb_p)
        kls.append(kl)
        act = nat["actions"][i]
        kl_per_action.setdefault(act, []).append(kl)

    # Per-class match breakdown
    from collections import defaultdict
    per_cls = defaultdict(lambda: [0, 0])
    for a, p, is_vol in zip(nat["actions"], pred_actions, voluntary_mask):
        per_cls[a][1] += 1
        if a == p:
            per_cls[a][0] += 1

    report = {
        "checkpoint": str(checkpoint),
        "n_seeds": n_seeds, "max_tick": max_tick,
        "total_samples": int(nat["X"].shape[0]),
        "voluntary_samples": int(voluntary_mask.sum()),
        "event_samples": int(event_mask.sum()),
        "overall_match_rate": overall_rate,
        "voluntary_match_rate": vol_rate,
        "event_match_rate": evt_rate,
        "voluntary_kl_n": len(kls),
        "voluntary_kl_mean": float(np.mean(kls)) if kls else float("nan"),
        "voluntary_kl_median": float(np.median(kls)) if kls else float("nan"),
        "voluntary_kl_max": float(np.max(kls)) if kls else float("nan"),
        "per_class_match": {a: {"correct": c, "total": t, "rate": c/t if t else 0.0}
                            for a, (c, t) in per_cls.items()},
        "per_action_kl_mean": {a: float(np.mean(v)) for a, v in kl_per_action.items()},
    }

    print(f"\n  overall match:   {overall_rate:.3f}")
    print(f"  voluntary match: {vol_rate:.3f}  (n={int(voluntary_mask.sum())})")
    print(f"  event match:     {evt_rate:.3f}  (n={int(event_mask.sum())})")
    print(f"  voluntary KL mean:   {report['voluntary_kl_mean']:.3f}")
    print(f"  voluntary KL median: {report['voluntary_kl_median']:.3f}")
    print("\n  per-class match (sorted by total):")
    for a in sorted(per_cls.keys(), key=lambda k: -per_cls[k][1]):
        c, t = per_cls[a]
        print(f"    {a:<22} {c}/{t} = {c/t if t else 0:.3f}")

    if out_json is not None:
        Path(out_json).parent.mkdir(parents=True, exist_ok=True)
        Path(out_json).write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8",
        )
        print(f"\n  report: {out_json}")

    return report


def main() -> int:
    checkpoint = sys.argv[1] if len(sys.argv) > 1 else "content/peter/trained/peter_bc_v3.pt"
    out = sys.argv[2] if len(sys.argv) > 2 else "docs/person/fidelity_v3.json"
    fidelity_report(
        checkpoint=checkpoint, n_seeds=10, max_tick=200, out_json=out,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
