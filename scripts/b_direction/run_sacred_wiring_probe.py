"""Sacred wiring probe (Iter 95).

Tests the chain: prayer/miracle event -> awe boost -> aux recovery
fires -> sacred-flavored agents recover differently from accusation.

Compares:
  A: sacred scenario, baseline (post Iter 95 wiring)
  B: sacred scenario, but events MANUALLY removed (regression to Iter 77 null)
  C: sacred scenario, aux recovery OFF (events fire but no recovery effect)
  D: accusation scenario for direct comparison

If A vs B differs measurably, sacred events are now coupled.
If A vs C differs, aux recovery is the active link.
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


def build_sacred(seed, *, include_sacred_events=True, aux_on=True):
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
    from scripts.b_direction.run_sacred_gathering import (
        build_cast,
        build_locations,
        build_network,
    )

    agents = build_cast()
    aids = [a.agent_id for a in agents]

    seed_events = [
        {"tick": 18, "event_id": "public_accusation",
         "target_role": "spiritual_wanderer",
         "location": "temple_outer_court"},
    ]
    if include_sacred_events:
        # Insert prayer + miracle as in default sacred scenario
        seed_events.insert(0, {
            "tick": 5, "event_id": "prayer_invitation",
            "location": "temple_outer_court",
        })
        seed_events.insert(1, {
            "tick": 10, "event_id": "miracle_witnessed",
            "location": "temple_outer_court",
        })

    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=build_locations(),
        initial_placements={
            "agent_01": "temple_outer_court", "agent_02": "temple_inner",
            "agent_03": "temple_outer_court", "agent_04": "temple_outer_court",
            "agent_05": "temple_outer_court", "agent_06": "temple_outer_court",
            "agent_07": "city_street", "agent_08": "city_street",
        },
        crowd_instances={
            "temple_outer_court": CrowdState(
                crowd_id="temple_outer_court", density=0.6,
                dominant_emotion="awe",
            ),
            "city_street": CrowdState(crowd_id="city_street", density=0.3),
        },
        social_network=build_network(aids),
        seed_events=seed_events,
        seed_rumors=[],
        seed=seed,
        awe_recovery_enabled=aux_on,
    ))


def build_accusation(seed):
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast,
        build_locations,
        build_social_network,
    )

    agents = build_accusation_cast()
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
            {"tick": 12, "event_id": "guard_approaches",
             "location": "priest_courtyard"},
        ],
        seed_rumors=[{
            "content_tag": "threat_to_authority",
            "target_role": "disciple_follower",
            "origin_source": "agent_04",
            "initial_reach": ["agent_04", "agent_05"],
            "intensity": 0.6, "credibility": 0.5,
        }],
        seed=seed,
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


def run_cell(builder, **kwargs):
    revs, finals, awe_finals = [], [], []
    awe_trace_seed0 = []
    for seed in range(N_SEEDS):
        w = builder(seed, **kwargs)
        per_shame = defaultdict(list)
        for tick_idx in range(N_TICKS):
            w.step()
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
            if seed == 0 and tick_idx % 20 == 0:
                # awe of an agent at temple_outer_court (if sacred)
                a3 = w._agents.get("agent_03")
                if a3:
                    awe_trace_seed0.append(round(a3.state.get("awe", 0.0), 2))
        for aid, ts in per_shame.items():
            if max(ts) >= 1.5:
                revs.append(count_reversals(ts))
                finals.append(ts[-1])
            awe_finals.append(w._agents[aid].state.get("awe", 0.0))
    return {
        "rev_mean": round(mean(revs) if revs else 0, 2),
        "n_active": len(revs),
        "final_mean": round(mean(finals) if finals else 0, 2),
        "awe_final_mean": round(mean(awe_finals) if awe_finals else 0, 2),
        "awe_trace_seed0": awe_trace_seed0,
    }


def main() -> int:
    print("[Iter 95] Sacred wiring probe")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} "
          f"N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    print("A: sacred WITH events wired (prayer + miracle)")
    a = run_cell(build_sacred, include_sacred_events=True, aux_on=True)
    print(f"  rev={a['rev_mean']} final={a['final_mean']} active={a['n_active']} "
          f"awe_final={a['awe_final_mean']}")
    print(f"  awe trace agent_03 seed0: {a['awe_trace_seed0']}")

    print()
    print("B: sacred WITHOUT events (Iter 77 regression)")
    b = run_cell(build_sacred, include_sacred_events=False, aux_on=True)
    print(f"  rev={b['rev_mean']} final={b['final_mean']} active={b['n_active']} "
          f"awe_final={b['awe_final_mean']}")
    print(f"  awe trace agent_03 seed0: {b['awe_trace_seed0']}")

    print()
    print("C: sacred WITH events but aux OFF")
    c = run_cell(build_sacred, include_sacred_events=True, aux_on=False)
    print(f"  rev={c['rev_mean']} final={c['final_mean']} active={c['n_active']} "
          f"awe_final={c['awe_final_mean']}")
    print(f"  awe trace agent_03 seed0: {c['awe_trace_seed0']}")

    print()
    print("D: accusation comparison")
    d = run_cell(build_accusation)
    print(f"  rev={d['rev_mean']} final={d['final_mean']} active={d['n_active']}")

    print()
    print("=== Iter 95 wiring verification ===")

    # Test 1: A vs B -- does adding events change dynamics?
    delta_rev_ab = a["rev_mean"] - b["rev_mean"]
    delta_final_ab = a["final_mean"] - b["final_mean"]
    print("\n  Test 1 (A vs B): events present?")
    print(f"    A rev={a['rev_mean']}  B rev={b['rev_mean']}  Δrev={delta_rev_ab:+.2f}")
    print(f"    A final={a['final_mean']}  B final={b['final_mean']}  "
          f"Δfinal={delta_final_ab:+.2f}")
    a_b_differ = abs(delta_rev_ab) > 0.5 or abs(delta_final_ab) > 0.5

    # Test 2: A vs C -- does aux recovery activate?
    delta_rev_ac = a["rev_mean"] - c["rev_mean"]
    delta_final_ac = a["final_mean"] - c["final_mean"]
    print("\n  Test 2 (A vs C): aux recovery contributes?")
    print(f"    A rev={a['rev_mean']}  C rev={c['rev_mean']}  Δrev={delta_rev_ac:+.2f}")
    print(f"    A final={a['final_mean']}  C final={c['final_mean']}  "
          f"Δfinal={delta_final_ac:+.2f}")
    a_c_differ = abs(delta_rev_ac) > 0.5 or abs(delta_final_ac) > 0.5

    # Test 3: A vs D -- does sacred differ from accusation now?
    delta_rev_ad = a["rev_mean"] - d["rev_mean"]
    delta_final_ad = a["final_mean"] - d["final_mean"]
    print("\n  Test 3 (A vs D): sacred vs accusation differentiation?")
    print(f"    A sacred rev={a['rev_mean']} final={a['final_mean']}")
    print(f"    D acc rev={d['rev_mean']} final={d['final_mean']}")
    print(f"    Δrev={delta_rev_ad:+.2f}  Δfinal={delta_final_ad:+.2f}")

    print()
    print("=== Verdict ===")
    if a_b_differ:
        print("  Iter 77 regression: events PRODUCE measurable effect now (was null)")
    else:
        print("  Iter 77 regression: events still produce no measurable effect")

    if a_c_differ:
        print("  Aux recovery is ACTIVE in sacred scenario")
    else:
        print("  Aux recovery effect not measurable")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "sacred_wiring_probe.json"
    )
    out_path.write_text(
        json.dumps({
            "n_seeds": N_SEEDS, "n_ticks": N_TICKS,
            "A_events_aux_on": a, "B_no_events": b,
            "C_events_aux_off": c, "D_accusation": d,
            "events_produce_effect": a_b_differ,
            "aux_recovery_active": a_c_differ,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
