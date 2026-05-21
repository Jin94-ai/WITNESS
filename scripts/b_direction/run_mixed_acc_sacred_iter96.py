"""Cross-scenario sacred injection in accusation (Iter 96).

Iter 90 found accusation+sacred mixing collapsed to single loop
(sacred decoupled). Iter 95 wired sacred events. This iter re-tests:
does coupling produce real mixed-arc dynamics now?

Method: accusation scenario + injection at mid-run:
  - prayer_invitation at upper_room t=40
  - miracle_witnessed at upper_room t=55

Expected: agents at upper_room (agent_01, _02, _03, _09) get awe boost
            -> aux recovery activates for them
            -> they cycle differently than crisis cohort (agent_04, _06,
               _07, _08, _10)
            -> Two-cohort divergence within accusation = mixed-arc

Conditions (5 seeds × 200 ticks):
  A: pure accusation (baseline)
  B: accusation + sacred injection (mixed)
  C: B but aux recovery OFF (sacred events fire but no recovery effect)
  D: B but awe decay OFF (Iter 93 regime — perpetual awe)
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
# Updated for retargeting: sacred events now at priest_courtyard.
# "Sacred-affected" cohort = priest_courtyard agents.
UPPER_ROOM_AGENTS = {"agent_04", "agent_05"}  # actually now priest_courtyard
OTHER_AGENTS = {"agent_06", "agent_07", "agent_08", "agent_10"}


def build_world(seed, *, sacred_inject=True, aux_on=True, decay_on=True):
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast,
        build_locations,
        build_social_network,
    )

    agents = build_accusation_cast()
    aids = [a.agent_id for a in agents]
    seed_events = [
        {"tick": 3, "event_id": "public_accusation",
         "target_role": "disciple_follower", "location": "priest_courtyard"},
        {"tick": 7, "event_id": "public_accusation",
         "target_role": "outsider", "location": "city_street"},
        {"tick": 12, "event_id": "guard_approaches",
         "location": "priest_courtyard"},
    ]
    if sacred_inject:
        # Sacred events at priest_courtyard where cycling agents live
        # (agent_04 priest, agent_05 priest -- both cycling cohort).
        seed_events.append(
            {"tick": 40, "event_id": "prayer_invitation",
             "location": "priest_courtyard"},
        )
        seed_events.append(
            {"tick": 55, "event_id": "miracle_witnessed",
             "location": "priest_courtyard"},
        )

    crowd_instances = {
        "priest_courtyard": CrowdState(crowd_id="priest_courtyard", density=0.4),
        "city_street": CrowdState(crowd_id="city_street", density=0.6),
    }

    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=build_locations(),
        initial_placements={
            "agent_01": "upper_room", "agent_02": "upper_room",
            "agent_03": "upper_room", "agent_04": "priest_courtyard",
            "agent_05": "priest_courtyard", "agent_06": "city_street",
            "agent_07": "city_street", "agent_08": "city_street",
            "agent_09": "upper_room", "agent_10": "city_street",
        },
        crowd_instances=crowd_instances,
        social_network=build_social_network(aids),
        seed_events=seed_events,
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


def run_cell(label, sacred_inject, aux_on, decay_on):
    revs_upper, finals_upper = [], []
    revs_other, finals_other = [], []
    awe_traces_upper = []
    awe_traces_other = []
    for seed in range(N_SEEDS):
        w = build_world(seed, sacred_inject=sacred_inject,
                        aux_on=aux_on, decay_on=decay_on)
        per_shame = defaultdict(list)
        for tick_idx in range(N_TICKS):
            w.step()
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
            if seed == 0 and tick_idx % 25 == 0:
                a1 = w._agents.get("agent_01")
                a4 = w._agents.get("agent_04")
                if a1: awe_traces_upper.append(round(a1.state.get("awe", 0), 2))
                if a4: awe_traces_other.append(round(a4.state.get("awe", 0), 2))
        for aid, ts in per_shame.items():
            if max(ts) >= 1.5:
                rev = count_reversals(ts)
                if aid in UPPER_ROOM_AGENTS:
                    revs_upper.append(rev)
                    finals_upper.append(ts[-1])
                else:
                    revs_other.append(rev)
                    finals_other.append(ts[-1])
    return {
        "rev_upper": round(mean(revs_upper) if revs_upper else 0, 2),
        "rev_other": round(mean(revs_other) if revs_other else 0, 2),
        "final_upper": round(mean(finals_upper) if finals_upper else 0, 2),
        "final_other": round(mean(finals_other) if finals_other else 0, 2),
        "n_upper": len(revs_upper),
        "n_other": len(revs_other),
        "awe_upper_seed0_25t": awe_traces_upper,
        "awe_other_seed0_25t": awe_traces_other,
    }


def main() -> int:
    print("[Iter 96] Cross-scenario sacred injection in accusation")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} "
          f"N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    print("A: pure accusation (no sacred events)")
    a = run_cell("A", sacred_inject=False, aux_on=True, decay_on=True)
    print(f"  upper: rev={a['rev_upper']} final={a['final_upper']} n={a['n_upper']}")
    print(f"  other: rev={a['rev_other']} final={a['final_other']} n={a['n_other']}")
    print(f"  awe upper seed0: {a['awe_upper_seed0_25t']}")

    print()
    print("B: accusation + sacred injection (prayer t=40, miracle t=55)")
    b = run_cell("B", sacred_inject=True, aux_on=True, decay_on=True)
    print(f"  upper: rev={b['rev_upper']} final={b['final_upper']} n={b['n_upper']}")
    print(f"  other: rev={b['rev_other']} final={b['final_other']} n={b['n_other']}")
    print(f"  awe upper seed0: {b['awe_upper_seed0_25t']}")
    print(f"  awe other seed0: {b['awe_other_seed0_25t']}")

    print()
    print("C: B but aux recovery OFF (sacred events fire, no recovery)")
    c = run_cell("C", sacred_inject=True, aux_on=False, decay_on=True)
    print(f"  upper: rev={c['rev_upper']} final={c['final_upper']} n={c['n_upper']}")
    print(f"  other: rev={c['rev_other']} final={c['final_other']} n={c['n_other']}")

    print()
    print("D: B but awe decay OFF (perpetual awe regime)")
    d = run_cell("D", sacred_inject=True, aux_on=True, decay_on=False)
    print(f"  upper: rev={d['rev_upper']} final={d['final_upper']} n={d['n_upper']}")
    print(f"  other: rev={d['rev_other']} final={d['final_other']} n={d['n_other']}")

    # Cohort divergence analysis
    print()
    print("=== Two-cohort divergence ===")
    for name, r in [("A pure", a), ("B mixed", b), ("C aux off", c), ("D no decay", d)]:
        upper_oth_rev_delta = r["rev_upper"] - r["rev_other"]
        upper_oth_final_delta = r["final_upper"] - r["final_other"]
        print(f"  {name}: upper rev={r['rev_upper']} other rev={r['rev_other']}  "
              f"Δrev={upper_oth_rev_delta:+.2f}  Δfinal={upper_oth_final_delta:+.2f}")

    # Mixed-arc detection: B vs A divergence
    print()
    print("=== B vs A: does mixing produce new dynamics? ===")
    upper_delta_rev = b["rev_upper"] - a["rev_upper"]
    upper_delta_final = b["final_upper"] - a["final_upper"]
    other_delta_rev = b["rev_other"] - a["rev_other"]
    other_delta_final = b["final_other"] - a["final_other"]

    print(f"  Upper room cohort:  Δrev={upper_delta_rev:+.2f} Δfinal={upper_delta_final:+.2f}")
    print(f"  Other cohort:       Δrev={other_delta_rev:+.2f} Δfinal={other_delta_final:+.2f}")

    # Verdict
    print()
    print("=== Verdict -- Scale-8 Mixed-Arc Richness ===")
    upper_changes = abs(upper_delta_rev) > 0.5 or abs(upper_delta_final) > 0.5
    other_unchanged = abs(other_delta_rev) < 0.5 and abs(other_delta_final) < 0.5

    if upper_changes and other_unchanged:
        verdict = (
            "Score 2 — sacred injection produces cohort-specific mixed "
            "dynamics. Upper-room agents cycle/recover differently while "
            "crisis cohort unchanged. Two-cohort divergence WITHIN one scenario."
        )
    elif upper_changes and not other_unchanged:
        verdict = (
            "Score 1.5 — mixing changes both cohorts (propagation through "
            "social_network or shared crowd state)."
        )
    else:
        verdict = (
            "Score 1 — mixing has no measurable cohort-specific effect. "
            "Single-loop collapse persists."
        )
    print(f"  {verdict}")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "mixed_acc_sacred_iter96.json"
    )
    out_path.write_text(
        json.dumps({
            "n_seeds": N_SEEDS, "n_ticks": N_TICKS,
            "A_pure": a, "B_mixed": b,
            "C_aux_off": c, "D_no_decay": d,
            "scale_8_verdict": verdict,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
