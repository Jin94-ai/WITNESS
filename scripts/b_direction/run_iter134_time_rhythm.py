"""Iter 134: Time-as-rhythm probe (Element I).

Project file Element I: 'same event at different timing has different
meaning'. Tests this by varying accusation event tick:
  V0: accusation at t=3 (immediate, baseline 53%)
  V1: accusation at t=50 (delayed slightly)
  V2: accusation at t=100 (mid-horizon)
  V3: accusation at t=200 (late)
  V4: accusation at t=300 (very late)

Hypothesis: later accusations leave less recovery time -> lower
recovery rate. If true, time IS rhythm: same event at different
times has different consequences.
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction._pyhash_guard import enforce_pyhash

enforce_pyhash()

N_SEEDS = 15
N_TICKS = 500


def build_world(seed, accusation_tick):
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
            {"tick": accusation_tick, "event_id": "public_accusation",
             "target_role": "disciple_follower", "location": "priest_courtyard"},
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


def run_variant(label, accusation_tick):
    finals = []
    for seed in range(N_SEEDS):
        w = build_world(seed, accusation_tick)
        per_shame = defaultdict(list)
        for _ in range(N_TICKS):
            w.step()
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
        ag_finals = []
        for aid, ts in per_shame.items():
            if max(ts) >= 1.5:
                ag_finals.append(ts[-1])
        finals.append(mean(ag_finals) if ag_finals else 0.0)
    rec_count = sum(1 for f in finals if f < 4.0)
    return {
        "label": label,
        "accusation_tick": accusation_tick,
        "recovery_window": N_TICKS - accusation_tick,
        "finals": [round(f, 2) for f in finals],
        "mean": round(mean(finals), 3),
        "stdev": round(stdev(finals) if len(finals) > 1 else 0, 3),
        "recovery_rate": f"{rec_count}/{N_SEEDS}",
        "recovery_pct": round(100 * rec_count / N_SEEDS, 1),
    }


def main() -> int:
    print("[Iter 134] Time-as-rhythm probe")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    accusation_ticks = [3, 50, 100, 200, 300, 400]
    results = {}
    for t in accusation_ticks:
        name = f"acc_t={t}"
        print(f"  Running {name} (recovery window = {N_TICKS - t}t)...")
        r = run_variant(name, t)
        results[name] = r
        print(f"    final mean={r['mean']} stdev={r['stdev']}  "
              f"recovery={r['recovery_rate']} ({r['recovery_pct']}%)")

    print()
    print("=== Time-as-rhythm curve ===")
    print(f"  {'tick':<8} {'window':<10} {'recovery':<14} {'mean':<8} {'bar'}")
    for t in accusation_ticks:
        name = f"acc_t={t}"
        r = results[name]
        bar = "#" * int(r["recovery_pct"] / 5)
        print(f"  {t:<8} {N_TICKS - t:<10} {r['recovery_rate']:<14} {r['mean']:<8} {bar}")

    print()
    print("=== Verdict ===")
    rates = [(t, results[f"acc_t={t}"]["recovery_pct"]) for t in accusation_ticks]
    early = rates[0][1]
    late = rates[-1][1]
    if late < early - 13:
        print(f"  TIME IS RHYTHM: late accusation reduces recovery from {early}% to {late}% (Δ {late - early:+.0f}%)")
        print("  Same event at different times produces different outcomes")
    elif late > early + 13:
        print(f"  TIME UNUSUAL: late accusation INCREASES recovery {early}% -> {late}%")
    else:
        print(f"  TIME WEAK: recovery rate similar across timing ({early}% -> {late}%)")
        print("  Element I (time as rhythm) may be weakly active in current scenario")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "time_rhythm_iter134.json"
    )
    out_path.write_text(
        json.dumps({"n_seeds": N_SEEDS, "n_ticks": N_TICKS, "results": results},
                   indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
