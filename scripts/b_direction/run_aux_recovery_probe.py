"""Auxiliary recovery channel probe (Iter 92, Branch B core).

Tests awe-driven calm: when agent.awe > 5.0, shame decays 0.05/tick
independent of Phase 2a forgiveness loop.

Goal: demonstrate Scale-4 (Recovery Diversity) increase from 1 to 2.

Method: 4 conditions × 5 seeds × 200 ticks (PYHASH=0)
  A: baseline (no awe injection, aux recovery on by default)
  B: awe-inject 3 disciples (agent_01,02,03 awe=8) + aux recovery on
  C: awe-inject + aux recovery OFF (compare to B; verifies channel does work)
  D: awe-inject + Phase 2a OFF (does aux recovery alone produce cycles?)

If D rev > 0: aux recovery alone can drive cycles → real auxiliary channel.
If D rev = 0: aux recovery enhances Phase 2a but isn't sufficient alone.
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
AWE_INJECT_AGENTS = {"agent_04", "agent_06", "agent_09"}  # cycling cohort
AWE_VALUE = 8.0


def build_world(seed, *, awe_inject=False, aux_on=True, p2a_on=True):
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast, build_locations, build_social_network,
    )
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorldConfig, MicroWorld

    agents = build_accusation_cast()
    if awe_inject:
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
        forgiveness_phase_enabled=p2a_on,
        awe_recovery_enabled=aux_on,
    ))


def count_reversals(ts, window=20):
    if len(ts) < 2 * window:
        return 0
    smoothed = [sum(ts[i:i + window]) / window
                for i in range(len(ts) - window + 1)]
    revs = 0
    prev = None
    for i in range(1, len(smoothed)):
        d = smoothed[i] - smoothed[i - 1]
        if abs(d) < 0.05:
            continue
        direction = 1 if d > 0 else -1
        if prev is not None and direction != prev:
            revs += 1
        prev = direction
    return revs


def run_condition(label, awe_inject, aux_on, p2a_on):
    revs_inj = []
    revs_oth = []
    revs_all = []
    finals_inj = []
    finals_oth = []
    awe_finals = []
    for seed in range(N_SEEDS):
        w = build_world(seed,
                        awe_inject=awe_inject, aux_on=aux_on, p2a_on=p2a_on)
        per_shame = defaultdict(list)
        for _ in range(N_TICKS):
            w.step()
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
        # Final awe levels for injected
        for aid in AWE_INJECT_AGENTS:
            if aid in w._agents:
                awe_finals.append(w._agents[aid].state.get("awe", 0.0))
        for aid, ts in per_shame.items():
            if max(ts) >= 1.5:
                rev = count_reversals(ts)
                final = ts[-1]
                revs_all.append(rev)
                if aid in AWE_INJECT_AGENTS:
                    revs_inj.append(rev)
                    finals_inj.append(final)
                else:
                    revs_oth.append(rev)
                    finals_oth.append(final)
    return {
        "label": label,
        "rev_all": round(mean(revs_all) if revs_all else 0, 3),
        "rev_inj": round(mean(revs_inj) if revs_inj else 0, 3),
        "rev_oth": round(mean(revs_oth) if revs_oth else 0, 3),
        "final_inj": round(mean(finals_inj) if finals_inj else 0, 3),
        "final_oth": round(mean(finals_oth) if finals_oth else 0, 3),
        "awe_final_inj": round(mean(awe_finals) if awe_finals else 0, 3),
        "n_inj_active": len(revs_inj),
        "n_oth_active": len(revs_oth),
    }


def main() -> int:
    print("[Iter 92] Auxiliary recovery channel probe -- awe-driven calm")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} "
          f"N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print(f"  Awe injection: {AWE_INJECT_AGENTS} → awe={AWE_VALUE}")
    print()

    conditions = [
        ("A_baseline_no_inject",       False, True,  True),
        ("B_awe_inject_aux_on_p2a_on", True,  True,  True),
        ("C_awe_inject_aux_OFF_p2a_on", True, False, True),
        ("D_awe_inject_aux_on_p2a_OFF", True, True,  False),
    ]
    results = {}
    for name, awi, aux, p2a in conditions:
        print(f"  Running {name}...")
        r = run_condition(name, awi, aux, p2a)
        results[name] = r
        print(f"    rev_all={r['rev_all']} rev_inj={r['rev_inj']} "
              f"rev_oth={r['rev_oth']} final_inj={r['final_inj']} "
              f"awe_inj_final={r['awe_final_inj']}")

    print()
    print("=== Aux recovery channel test ===")
    a = results["A_baseline_no_inject"]
    b = results["B_awe_inject_aux_on_p2a_on"]
    c = results["C_awe_inject_aux_OFF_p2a_on"]
    d = results["D_awe_inject_aux_on_p2a_OFF"]

    print(f"\n  Test 1: aux recovery active vs disabled (B vs C)")
    print(f"    Injected agents:")
    print(f"      B (aux on):  rev={b['rev_inj']} final={b['final_inj']}")
    print(f"      C (aux off): rev={c['rev_inj']} final={c['final_inj']}")
    bc_delta_final = c["final_inj"] - b["final_inj"]
    print(f"    Δ final shame (C - B) = {bc_delta_final:+.3f}  "
          f"(positive = aux recovery actually reduces shame)")

    print(f"\n  Test 2: aux recovery alone (no Phase 2a) - D")
    print(f"    Injected: rev={d['rev_inj']} final={d['final_inj']}")
    print(f"    Others:   rev={d['rev_oth']} final={d['final_oth']}")
    if d["rev_inj"] > 0.5:
        d_verdict = (
            f"YES - aux recovery alone produces cycling in injected cohort. "
            f"True auxiliary channel. Scale-4 = 2."
        )
    elif d["final_inj"] < 8.0:
        d_verdict = (
            f"PARTIAL - aux alone reduces final shame but doesn't produce "
            f"cycles. Scale-4 = 1.5."
        )
    else:
        d_verdict = (
            f"NO - aux recovery alone insufficient to produce cycles. "
            f"Scale-4 stays at 1. Magnitude needs tuning OR Phase 2a "
            f"dominance still complete."
        )
    print(f"    Verdict: {d_verdict}")

    print()
    print("=== Scale-4 Recovery Diversity score ===")
    if d["rev_inj"] > 0.5:
        score4 = "Score 2 -- aux recovery is independent channel"
    elif bc_delta_final > 1.0:
        score4 = "Score 1.5 -- aux recovery contributes but doesn't stand alone"
    else:
        score4 = "Score 1 -- still single-loop"
    print(f"  {score4}")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "aux_recovery_probe.json"
    )
    out_path.write_text(
        json.dumps({
            "n_seeds": N_SEEDS, "n_ticks": N_TICKS,
            "awe_threshold": 5.0, "awe_decay": 0.05,
            "results": results,
            "verdict_d": d_verdict,
            "scale_4_score": score4,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
