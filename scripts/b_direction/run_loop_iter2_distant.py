"""WORLD_FLOW_LOOP Iter 2 — distant-role transition + multi-seed.

Hypothesis from Iter 1:
  fisher_laborer -> disciple_follower showed 0.0 counterfactual action
  divergence at top-5 level because the two clusters are structurally
  too close. If we transition fisher -> elite_strategist (far cluster),
  does divergence rise to C_propagating threshold (≥ 0.3)?

Multi-seed robustness: 5 seeds (0,1,2,3,4). Report mean divergence +
fraction-of-seeds-with-divergence ≥ 0.3.

One change vs Iter 1:
  - new_role_id: disciple_follower -> elite_strategist
  - multi-seed loop (5 seeds)
  - NOTHING ELSE changes from Iter 1 scenario.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction.run_loop_iter1_transition import (  # noqa: E402
    build_micro_world as build_iter1_world,
    summarize_run,
    flow_type_verdict,
    score_6_axes,
    divergence_score,
)
from engine.world.micro_world import MicroWorld  # noqa: E402


def build_distant_transition_world(seed: int = 0, enable_transition: bool = True) -> MicroWorld:
    """Clone of Iter 1 scenario, but with fisher -> elite_strategist."""
    # We can't monkey-patch build_iter1_world cleanly, so replicate the
    # scenario setup with the role swap.
    from scripts.b_direction.run_loop_iter1_transition import (
        build_cast, build_locations, build_network,
    )
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorldConfig

    agents = build_cast()
    locations = build_locations()
    placements = {
        "agent_01": "shore", "agent_02": "shore", "agent_03": "shore",
        "agent_04": "village_street", "agent_05": "village_street",
        "agent_06": "village_street", "agent_07": "village_street",
        "agent_08": "village_street",
    }
    crowds = {
        "shore": CrowdState(
            crowd_id="shore", density=0.4, dominant_emotion="indifferent",
        ),
        "village_street": CrowdState(
            crowd_id="village_street", density=0.5,
        ),
    }
    seed_events: list[dict] = [
        {"tick": 3, "event_id": "prayer_invitation", "location": "shore"},
        {"tick": 6, "event_id": "miracle_witnessed", "location": "shore"},
    ]
    if enable_transition:
        seed_events.extend([
            # DISTANT ROLE — the one change in this Iter
            {"tick": 7, "event_id": "role_transition",
             "agent_id": "agent_01", "new_role_id": "elite_strategist",
             "reason": "covert_bargain", "blend_factor": 0.7},
            {"tick": 7, "event_id": "role_transition",
             "agent_id": "agent_02", "new_role_id": "elite_strategist",
             "reason": "covert_bargain", "blend_factor": 0.7},
        ])
    seed_events.append({
        "tick": 18, "event_id": "public_accusation",
        "target_role": "spiritual_wanderer", "location": "village_street",
    })
    config = MicroWorldConfig(
        agents=agents, locations=locations,
        initial_placements=placements,
        crowd_instances=crowds,
        social_network=build_network([a.agent_id for a in agents]),
        seed_events=seed_events, seed_rumors=[], seed=seed,
    )
    return MicroWorld(config)


def run_single_seed(seed: int, n_ticks: int = 30) -> dict:
    world_tr = build_distant_transition_world(seed=seed, enable_transition=True)
    world_tr.run(n_ticks)
    world_ctrl = build_distant_transition_world(seed=seed, enable_transition=False)
    world_ctrl.run(n_ticks)

    sum_tr = summarize_run(world_tr)
    sum_ctrl = summarize_run(world_ctrl)

    # Counterfactual top-5 divergence
    with_top = set(list(sum_tr["actions"])[:5])
    without_top = set(list(sum_ctrl["actions"])[:5])
    if with_top or without_top:
        counter_div = len(with_top.symmetric_difference(without_top)) / len(
            with_top.union(without_top)
        )
    else:
        counter_div = 0.0

    verdict = flow_type_verdict(sum_tr, sum_ctrl)
    scores = score_6_axes(sum_tr, sum_ctrl)

    return {
        "seed": seed,
        "verdict": verdict,
        "emergent_events_tr": sum_tr["emergent_events"],
        "emergent_events_ctrl": sum_ctrl["emergent_events"],
        "cross_layer_ticks_tr": sum_tr["cross_layer_ticks"],
        "cross_layer_ticks_ctrl": sum_ctrl["cross_layer_ticks"],
        "post_miracle_div": sum_tr["post_miracle_divergence"],
        "post_accusation_div": sum_tr["post_accusation_divergence"],
        "counterfactual_action_div": round(counter_div, 3),
        "with_tr_top5": list(sum_tr["actions"])[:5],
        "without_tr_top5": list(sum_ctrl["actions"])[:5],
        "scores": scores,
    }


def main() -> int:
    n_ticks = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    n_seeds = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    print(f"[LOOP Iter 2] distant-role transition | seeds=0..{n_seeds - 1} "
          f"| ticks={n_ticks}")
    print("  Structural change: transition target = elite_strategist (distant)")
    print("  Baseline: Iter 1 scenario otherwise identical")
    print()

    results = []
    for s in range(n_seeds):
        r = run_single_seed(seed=s, n_ticks=n_ticks)
        results.append(r)
        print(f"  seed={s} verdict={r['verdict']:<14} "
              f"counter_div={r['counterfactual_action_div']:.3f} "
              f"post_acc_div={r['post_accusation_div']:.3f} "
              f"emergent_tr={r['emergent_events_tr']}")

    print()
    print("=== Aggregate (n = {}) ===".format(n_seeds))
    cdivs = [r["counterfactual_action_div"] for r in results]
    pdivs = [r["post_accusation_div"] for r in results]
    verdicts = Counter(r["verdict"] for r in results)
    print(f"  counter_div mean={mean(cdivs):.3f} "
          f"stdev={stdev(cdivs) if len(cdivs) > 1 else 0:.3f} "
          f"max={max(cdivs):.3f}")
    print(f"  post_acc_div mean={mean(pdivs):.3f} "
          f"stdev={stdev(pdivs) if len(pdivs) > 1 else 0:.3f}")
    print(f"  seeds with counter_div >= 0.3: "
          f"{sum(1 for d in cdivs if d >= 0.3)}/{n_seeds}")
    print(f"  verdict distribution: {dict(verdicts)}")

    success = sum(1 for d in cdivs if d >= 0.3) >= 3
    print()
    print(f"  Iter 2 success criterion (>= 3/5 seeds with counter_div >= 0.3): "
          f"{'PASS' if success else 'FAIL'}")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / f"loop_iter2_distant_n{n_seeds}.json"
    )
    out_path.write_text(
        json.dumps({
            "iter": 2,
            "structural_change": "distant-role transition (fisher -> elite_strategist)",
            "n_seeds": n_seeds, "n_ticks": n_ticks,
            "success": success,
            "aggregate": {
                "counter_div_mean": mean(cdivs),
                "counter_div_max": max(cdivs),
                "post_acc_div_mean": mean(pdivs),
                "verdict_distribution": dict(verdicts),
                "seeds_pass_threshold": sum(1 for d in cdivs if d >= 0.3),
            },
            "per_seed": results,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
