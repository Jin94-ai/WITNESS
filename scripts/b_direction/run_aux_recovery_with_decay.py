"""Aux recovery + awe decay probe (Iter 94).

Iter 92-93 had awe persisting at 8 forever — artificial.
Iter 94 added awe decay (0.05/tick toward baseline 3.0).

Test:
- A baseline (no inject)
- B awe-inject + aux on + awe decay on (production)
- C awe-inject + aux on + awe decay OFF (Iter 92-93 regime)
- D awe-inject + aux off + awe decay on

Watch:
- awe trajectory over time (should fade in B but not C)
- final shame (B should be less recovered than C if decay matters)
- rev/agent for both cohorts

Goal: realistic dynamics where awe spike has time-limited recovery
effect, not permanent.
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


def build_world(seed, *, inject=True, aux_on=True, decay_on=True):
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast, build_locations, build_social_network,
    )
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorldConfig, MicroWorld

    agents = build_accusation_cast()
    if inject:
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
        awe_recovery_enabled=aux_on,
        awe_decay_enabled=decay_on,
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


def run_cell(label, inject, aux_on, decay_on):
    revs_inj, finals_inj, awe_traces = [], [], []
    revs_oth, finals_oth = [], []
    for seed in range(N_SEEDS):
        w = build_world(seed, inject=inject, aux_on=aux_on, decay_on=decay_on)
        per_shame = defaultdict(list)
        # awe trace for first injected agent at seed 0
        awe_trace_seed0 = []
        for tick_idx in range(N_TICKS):
            w.step()
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
            if seed == 0:
                a4 = w._agents.get("agent_04")
                if a4:
                    awe_trace_seed0.append(round(a4.state.get("awe", 0.0), 2))
        if seed == 0:
            awe_traces = awe_trace_seed0
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
        "label": label,
        "rev_inj": round(mean(revs_inj) if revs_inj else 0, 2),
        "rev_oth": round(mean(revs_oth) if revs_oth else 0, 2),
        "final_inj": round(mean(finals_inj) if finals_inj else 0, 2),
        "final_oth": round(mean(finals_oth) if finals_oth else 0, 2),
        "awe_trace_agent04_seed0": awe_traces[::20] if awe_traces else [],
    }


def main() -> int:
    print(f"[Iter 94] Aux recovery + awe decay probe")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} "
          f"N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    conditions = [
        ("A_no_inject",                 False, True,  True),
        ("B_inject_aux_on_decay_on",    True,  True,  True),
        ("C_inject_aux_on_decay_OFF",   True,  True,  False),
        ("D_inject_aux_off_decay_on",   True,  False, True),
    ]
    results = {}
    for name, inj, aux, dec in conditions:
        r = run_cell(name, inj, aux, dec)
        results[name] = r
        print(f"  {name}")
        print(f"    rev_inj={r['rev_inj']} final_inj={r['final_inj']}  "
              f"rev_oth={r['rev_oth']} final_oth={r['final_oth']}")
        print(f"    agent_04 awe trace (every 20t): {r['awe_trace_agent04_seed0']}")

    print()
    print("=== Iter 94 awe-decay verification ===")

    a = results["A_no_inject"]
    b = results["B_inject_aux_on_decay_on"]
    c = results["C_inject_aux_on_decay_OFF"]
    d = results["D_inject_aux_off_decay_on"]

    # Trace check: B should show awe declining; C should show awe stable at 8
    b_awe = b["awe_trace_agent04_seed0"]
    c_awe = c["awe_trace_agent04_seed0"]
    print(f"  B awe trace: {b_awe}  (decay ON -- should fall toward 3.0)")
    print(f"  C awe trace: {c_awe}  (decay OFF -- should stay at 8)")

    print()
    print("  Final shame comparison (injected cohort):")
    print(f"    A baseline:                final={a['final_inj']}")
    print(f"    B inject + aux + decay:    final={b['final_inj']}")
    print(f"    C inject + aux + NO decay: final={c['final_inj']}")
    print(f"    D inject + aux off:        final={d['final_inj']}")
    print()
    print(f"  B vs C delta (decay vs no decay): "
          f"{b['final_inj'] - c['final_inj']:+.2f} "
          f"(positive = decay reduces aux contribution)")

    if b_awe and c_awe and b_awe[-1] < 4.0 and c_awe[-1] >= 7.5:
        decay_works = True
    else:
        decay_works = False
    print(f"\n  Decay mechanism wired correctly: {decay_works}")

    if b["final_inj"] > c["final_inj"] + 0.5:
        recovery_limited = True
        print(f"  Recovery time-limited (B has higher final than C): YES")
    else:
        recovery_limited = False
        print(f"  Recovery NOT measurably time-limited (B ~ C): {b['final_inj'] - c['final_inj']:+.2f}")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "aux_recovery_with_decay.json"
    )
    out_path.write_text(
        json.dumps({
            "n_seeds": N_SEEDS, "n_ticks": N_TICKS,
            "results": results,
            "decay_works": decay_works,
            "recovery_limited": recovery_limited,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
