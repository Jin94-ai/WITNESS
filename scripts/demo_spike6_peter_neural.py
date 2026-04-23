"""Spike 6 Phase E — dual-path Peter comparison demo.

Trains a small MLP on rule-based Peter trajectories, then replays a fixed
seed twice — once with ``policy=None`` (legacy), once with the trained
neural policy — and prints both action trajectories side-by-side for Lee.

This is a **diagnostic**, not a test. Per spec §2.2 there is no numeric
completion bar; Lee eyeballs whether the neural Peter is "살아 움직이는가".

Usage (from repo root)::

    python scripts/demo_spike6_peter_neural.py

Optional flags::

    --seeds-train 10        # how many seeds to train on
    --seed-compare 99       # the single seed replayed in both modes
    --max-tick 100          # length of each compared run
    --save-weights PATH     # path to save the trained MLP checkpoint
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from content.caiaphas.domain_politics import PoliticalCalculationState  # noqa: E402
from content.crowd.domain_crowd import CrowdDynamicsState  # noqa: E402
from content.judas.domain_betrayal import BetrayalPsychologyState  # noqa: E402
from content.peter.domain_faith import FaithJourneyState  # noqa: E402
from engine.core.world import SimulationConfig  # noqa: E402
from engine.io.loader import (  # noqa: E402
    load_agent_state,
    load_behavior_profile,
    load_events,
    load_hazard_events,
    load_triggers,
    register_domain_type,
)
from engine.policies.neural.dataset import (  # noqa: E402
    build_behavior_cloning_dataset,
    train_val_split,
)
from engine.policies.neural.inference import NeuralDecisionPolicy  # noqa: E402
from engine.policies.neural.trainer import (  # noqa: E402
    save_checkpoint,
    train_behavior_cloning,
)
from engine.rules.base import RuleEngine  # noqa: E402
from engine.rules.emotional import (  # noqa: E402
    ConfusionRule,
    FearResponseRule,
    GriefRule,
    HopeRule,
    LoveRule,
)
from engine.rules.temporal import HomeostasisRule  # noqa: E402
from engine.simulation.world import SimulationWorld  # noqa: E402

CONTENT = ROOT / "content"


def _register_domains() -> None:
    for t, c in [
        ("faith_journey", FaithJourneyState),
        ("betrayal_psychology", BetrayalPsychologyState),
        ("political_calculation", PoliticalCalculationState),
        ("crowd_dynamics", CrowdDynamicsState),
    ]:
        register_domain_type(t, c)


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(), HomeostasisRule(),
    ])


def _build_config(max_tick: int) -> SimulationConfig:
    peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    cai = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
    events = load_events(CONTENT / "peter" / "canonical_events.json")
    triggers = load_triggers(CONTENT / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT / "peter" / "hazard_events.json")
    return SimulationConfig(
        initial_state=peter,
        initial_states=[peter, judas, cai, crowd],
        max_tick=max_tick, state_noise_scale=0.02,
        events=events, triggers=triggers, hazard_events=hazards,
    )


def _load_profiles() -> dict:
    return {
        "peter": load_behavior_profile(CONTENT / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT / "caiaphas" / "behavior_profile.json"),
        "crowd": load_behavior_profile(CONTENT / "crowd" / "behavior_profile.json"),
    }


def _run(
    *, seed: int, max_tick: int, policies: dict | None = None,
) -> list[tuple[int, str]]:
    """Return [(tick, chosen_action)] for Peter."""
    config = _build_config(max_tick=max_tick)
    profiles = _load_profiles()
    world = SimulationWorld(config, _rules(), behavior_profiles=profiles, policies=policies)
    result = world.run(seed=seed)
    records = result.action_histories.get("peter", [])
    return [(r.tick, r.chosen_action) for r in records]


def _print_side_by_side(
    legacy: list[tuple[int, str]], neural: list[tuple[int, str]],
) -> None:
    print(f"\n{'tick':>6} | {'legacy (policy=None)':<28} | neural (policy=NeuralDecisionPolicy)")
    print("-" * 78)
    max_len = max(len(legacy), len(neural))
    for i in range(max_len):
        l_tick, l_action = legacy[i] if i < len(legacy) else ("", "")
        n_tick, n_action = neural[i] if i < len(neural) else ("", "")
        marker = "  " if l_action == n_action else "**"
        tick_str = str(l_tick if l_tick != "" else n_tick)
        print(f"{tick_str:>6} | {str(l_action):<28} | {n_action} {marker}")

    # Divergence summary.
    shared = min(len(legacy), len(neural))
    diff = sum(1 for i in range(shared) if legacy[i][1] != neural[i][1])
    print(f"\n  shared actions:  {shared}")
    print(f"  divergent:       {diff}  ({100 * diff / max(1, shared):.1f}%)")
    print("  ** = diverged tick")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds-train", type=int, default=10)
    parser.add_argument("--seed-compare", type=int, default=99)
    parser.add_argument("--max-tick", type=int, default=100)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument(
        "--save-weights",
        type=str,
        default=str(CONTENT / "peter" / "trained" / "peter_bc_v1.pt"),
    )
    args = parser.parse_args()

    _register_domains()

    # === 1. Train on rule-based Peter trajectories.
    def _run_fn(seed: int):
        config = _build_config(max_tick=args.max_tick)
        profiles = _load_profiles()
        return SimulationWorld(
            config, _rules(), behavior_profiles=profiles,
        ).run(seed=seed)

    print(f"[1/4] Collecting training data from {args.seeds_train} seeds × {args.max_tick} tick...")
    ds = build_behavior_cloning_dataset(
        _run_fn, agent_id="peter", seeds=args.seeds_train,
    )
    print(f"      {ds.n_samples} samples | vocab={ds.action_vocab}")
    if ds.n_samples < 20:
        print("      WARNING: too few samples for meaningful training.")

    train, val = train_val_split(ds, val_fraction=0.2, seed=0)
    print(f"      train={train.n_samples}  val={val.n_samples}")

    # === 2. Train MLP.
    print(f"[2/4] Training MLP for up to {args.epochs} epochs (CPU)...")
    model, history = train_behavior_cloning(
        train, val, epochs=args.epochs, batch_size=32, lr=1e-2, seed=0,
        early_stop_patience=8,
    )
    final = history.final
    if final is not None:
        print(
            f"      epoch {final.epoch}  train_loss={final.train_loss:.3f}  "
            f"train_acc={final.train_acc:.3f}  val_loss={final.val_loss:.3f}  "
            f"val_acc={final.val_acc:.3f}",
        )
        print(f"      best val_acc: {history.best_val_acc:.3f}")

    # === 3. Save + reload checkpoint.
    weights_path = Path(args.save_weights)
    save_checkpoint(model, weights_path, ds.action_vocab)
    feature_cfg_path = weights_path.with_suffix(".feature_config.json")
    ds.save_feature_config(feature_cfg_path)
    print(f"[3/4] Saved checkpoint: {weights_path}")
    print(f"      Feature config:  {feature_cfg_path}")

    # === 4. Replay the same seed twice — legacy vs neural.
    print(f"\n[4/4] Replaying seed={args.seed_compare} for {args.max_tick} tick...")
    policy = NeuralDecisionPolicy(model=model, action_vocab=ds.action_vocab, device="cpu")

    legacy = _run(seed=args.seed_compare, max_tick=args.max_tick)
    neural = _run(
        seed=args.seed_compare, max_tick=args.max_tick,
        policies={"peter": policy},
    )

    _print_side_by_side(legacy, neural)

    # Persist the comparison for later inspection.
    report_path = ROOT / "docs" / "person" / "peter_neural_comparison.json"
    report_path.write_text(json.dumps({
        "seed_compare": args.seed_compare,
        "max_tick": args.max_tick,
        "legacy_trajectory": legacy,
        "neural_trajectory": neural,
        "action_vocab": ds.action_vocab,
        "train_samples": train.n_samples,
        "val_samples": val.n_samples,
        "val_acc_best": history.best_val_acc if final is not None else None,
        "action_distribution_train": {
            ds.action_vocab[k]: int(v)
            for k, v in zip(*np.unique(train.y, return_counts=True))
        },
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n      Comparison JSON: {report_path}")
    print("      (Lee: eyeball the diverged '**' rows above, or the JSON.)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
