"""Aux recovery magnitude sweep (Iter 93, follow-up to Iter 92).

Iter 92 found awe_recovery_shame_decay=0.05/tick is below effect floor.
Sweep [0.05, 0.1, 0.2, 0.3, 0.5] to find effective range.

Test design:
  Per magnitude, run 2 conditions:
    P2a-on: aux + Phase 2a both active (does aux contribute when both run?)
    P2a-off: aux only (does aux alone produce cycles or recovery?)

  awe-injected on agent_04, agent_06, agent_09 (cycling cohort)

Looking for:
  - magnitude where P2a-off produces rev > 0 (true auxiliary channel)
  - or magnitude where P2a-off final shame < 8 (partial recovery without saturation)
  - confirm P2a-on results don't change much (aux shouldn't dominate when P2a present)
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction._pyhash_guard import enforce_pyhash
enforce_pyhash()

N_SEEDS = 5
N_TICKS = 200
AWE_INJECT_AGENTS = {"agent_04", "agent_06", "agent_09"}
AWE_VALUE = 8.0
DECAYS = [0.05, 0.1, 0.2, 0.3, 0.5]


def build_world(seed, *, p2a_on=True, decay=0.05):
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast, build_locations, build_social_network,
    )
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorldConfig, MicroWorld

    agents = build_accusation_cast()
    for a in agents:
        if a.agent_id in AWE_INJECT_AGENTS:
            a.state["awe"] = AWE_VALUE

    aids = [a.agent_id for a in agents]
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=build_locations(),
        initial_placements={
            "agent_01": "upper_room", "agent_02": "upper_room",
            "agent_03": "upper_room", "agent_04": "priest_courtyard",
            "agent_05": "priest_courtyard", "agent_06": "city_street",
            "agent_07": "city_street", "agent_08": "city_street",
            "agent_09": "upper_room", "agent_10": "city_street",
        },
        crowd_instances={
            "priest_courtyard": CrowdState(crowd_id="priest_courtyard", density=0.4),
            "city_street": CrowdState(crowd_id="city_street", density=0.6),
        },
        social_network=build_social_network(aids),
        seed_events=[
            {"tick": 3, "event_id": "public_accusation",
             "target_role": "disciple_follower", "location": "priest_courtyard"},
            {"tick": 7, "event_id": "public_accusation",
             "target_role": "outsider", "location": "city_street"},
            {"tick": 12, "event_id": "guard_approaches", "location": "priest_courtyard"},
        ],
        seed_rumors=[{
            "content_tag": "threat_to_authority",
            "target_role": "disciple_follower",
            "origin_source": "agent_04",
            "initial_reach": ["agent_04", "agent_05"],
            "intensity": 0.6, "credibility": 0.5,
        }],
        seed=seed,
        forgiveness_phase_enabled=p2a_on,
        awe_recovery_enabled=True,
        awe_recovery_shame_decay=decay,
    ))


def count_reversals(ts, window=20):
    if len(ts) < 2 * window:
        return 0
    smoothed = [sum(ts[i:i + window]) / window
                for i in range(len(ts) - window + 1)]
    revs, prev = 0, None
    for i in range(1, len(smoothed)):
        d = smoothed[i] - smoothed[i - 1]
        if abs(d) < 0.05:
            continue
        direction = 1 if d > 0 else -1
        if prev is not None and direction != prev:
            revs += 1
        prev = direction
    return revs


def run_cell(decay, p2a_on):
    revs_inj, revs_oth, finals_inj, finals_oth = [], [], [], []
    for seed in range(N_SEEDS):
        w = build_world(seed, p2a_on=p2a_on, decay=decay)
        per_shame = defaultdict(list)
        for _ in range(N_TICKS):
            w.step()
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
        for aid, ts in per_shame.items():
            if max(ts) >= 1.5:
                rev = count_reversals(ts)
                if aid in AWE_INJECT_AGENTS:
                    revs_inj.append(rev)
                    finals_inj.append(ts[-1])
                else:
                    revs_oth.append(rev)
                    finals_oth.append(ts[-1])
    return {
        "rev_inj": round(mean(revs_inj) if revs_inj else 0, 2),
        "rev_oth": round(mean(revs_oth) if revs_oth else 0, 2),
        "final_inj": round(mean(finals_inj) if finals_inj else 0, 2),
        "final_oth": round(mean(finals_oth) if finals_oth else 0, 2),
        "n_inj": len(revs_inj),
        "n_oth": len(revs_oth),
    }


def main() -> int:
    print(f"[Iter 93] Aux recovery magnitude sweep")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} "
          f"N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print(f"  awe injected on {AWE_INJECT_AGENTS} = {AWE_VALUE}")
    print()

    results = {}
    for decay in DECAYS:
        for p2a_on in (True, False):
            label = f"decay={decay}_p2a={'on' if p2a_on else 'off'}"
            r = run_cell(decay, p2a_on)
            results[label] = r
            print(f"  {label:<28} "
                  f"rev_inj={r['rev_inj']:<5} rev_oth={r['rev_oth']:<5} "
                  f"final_inj={r['final_inj']:<5} final_oth={r['final_oth']}")

    # Analysis
    print()
    print("=== P2a-OFF column (aux alone test) ===")
    print(f"  {'decay':<8} {'rev_inj':<10} {'final_inj':<10} {'rev_oth':<10} {'final_oth':<10}")
    for decay in DECAYS:
        r = results[f"decay={decay}_p2a=off"]
        print(f"  {decay:<8} {r['rev_inj']:<10} {r['final_inj']:<10} "
              f"{r['rev_oth']:<10} {r['final_oth']}")

    print()
    print("=== P2a-ON column (aux + p2a together) ===")
    print(f"  {'decay':<8} {'rev_inj':<10} {'final_inj':<10} {'rev_oth':<10} {'final_oth':<10}")
    for decay in DECAYS:
        r = results[f"decay={decay}_p2a=on"]
        print(f"  {decay:<8} {r['rev_inj']:<10} {r['final_inj']:<10} "
              f"{r['rev_oth']:<10} {r['final_oth']}")

    # Effective range identification
    print()
    print("=== Effective range search ===")

    # Threshold 1: aux alone produces injected rev > 0.5
    threshold_cycling = None
    for decay in DECAYS:
        r = results[f"decay={decay}_p2a=off"]
        if r["rev_inj"] > 0.5:
            threshold_cycling = decay
            break
    print(f"  Aux-alone CYCLING threshold (rev_inj > 0.5): {threshold_cycling}")

    # Threshold 2: aux alone reduces injected final shame below 8
    threshold_partial = None
    for decay in DECAYS:
        r = results[f"decay={decay}_p2a=off"]
        if r["final_inj"] < 8.0:
            threshold_partial = decay
            break
    print(f"  Aux-alone PARTIAL recovery threshold (final_inj < 8): "
          f"{threshold_partial}")

    # Iter 92 baseline (decay=0.05): aux+p2a final = 5.74, p2a-only (aux off) = 5.21
    # Compare aux+p2a final at higher decay to see aux contribution clearly
    print()
    print("=== Aux contribution under P2a (p2a-on column) ===")
    print(f"  {'decay':<8} {'final_inj':<12}")
    for decay in DECAYS:
        r = results[f"decay={decay}_p2a=on"]
        print(f"  {decay:<8} {r['final_inj']:<12}")

    # Verdict
    print()
    print("=== Scale-4 verdict ===")
    if threshold_cycling is not None:
        score4 = (
            f"Score 2 -- aux alone produces cycling at decay >= "
            f"{threshold_cycling}. True auxiliary channel."
        )
    elif threshold_partial is not None:
        score4 = (
            f"Score 1.5 -- aux alone reduces final shame at decay >= "
            f"{threshold_partial} but no cycling. Partial alternative."
        )
    else:
        score4 = (
            f"Score 1 -- even at decay=0.5 aux alone insufficient. "
            f"Decay rate inadequate vs accumulation."
        )
    print(f"  {score4}")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "aux_recovery_sweep.json"
    )
    out_path.write_text(
        json.dumps({
            "n_seeds": N_SEEDS, "n_ticks": N_TICKS,
            "decays": DECAYS,
            "results": results,
            "threshold_cycling": threshold_cycling,
            "threshold_partial": threshold_partial,
            "scale_4_score": score4,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
