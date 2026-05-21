"""WORLD_FLOW_LOOP Iter 23 -- Audit sacred_gathering topology.

Per Iter 22 finding: 3 scenarios -> 2 topologies (calling + crisis).
This iter adds sacred_gathering (Batch 5 iter 5) to see if it's a 3rd.
Reuses Iter 22's fingerprint machinery.

Verdict rules:
  - If sacred pairwise JS to all 3 others is >= 0.15, it's a 3rd topology.
  - If sacred JS to calling < 0.10, sacred merges with calling.
  - If sacred JS to acc/scr < 0.10, sacred merges with crisis.
  - Between: sacred is partial/hybrid.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction.run_loop_iter22_topology_audit import (  # noqa
    compute_fingerprints, _js,
)

N_SEEDS = 5
N_TICKS = 30


def run_scenario_sacred(seed: int):
    from scripts.b_direction.run_sacred_gathering import build_micro_world
    w = build_micro_world(seed=seed)
    w.run(N_TICKS)
    return w


def compute_sacred_fingerprint():
    """Adapted copy of compute_fingerprints for sacred scenario."""
    # Reuse the same structure; we need the N_TICKS/N_SEEDS to match
    from scripts.b_direction.run_sacred_gathering import build_micro_world

    motifs: Counter = Counter()
    actions: Counter = Counter()
    event_types: Counter = Counter()

    alignment_over_time: list[list[float]] = [[] for _ in range(N_TICKS)]
    density_over_time: list[list[float]] = [[] for _ in range(N_TICKS)]
    blame_concen_over_time: list[list[float]] = [[] for _ in range(N_TICKS)]
    shame_climate_over_time: list[list[float]] = [[] for _ in range(N_TICKS)]
    auth_vig_over_time: list[list[float]] = [[] for _ in range(N_TICKS)]

    rumor_tick_total = 0
    crowd_change_total = 0
    event_total = 0

    for s in range(N_SEEDS):
        w = build_micro_world(seed=s)
        w.run(N_TICKS)
        prior_phases: dict[str, str] = {}
        for step in w.history:
            motifs.update(step.agent_motifs.values())
            actions.update(step.agent_actions.values())
            for ev in step.spawned_events:
                et = ev.get("event_id", "?")
                event_types[et] += 1
                event_total += 1

            aligns, densities, blames, shames, auths = [], [], [], [], []
            for cid, cs in step.crowd_state_snapshot.items():
                aligns.append(cs["alignment"])
                densities.append(cs["density"])
                blames.append(
                    max(cs.get("blame", {}).values(), default=0.0)
                )
                shames.append(cs.get("shame_climate", 0.0))
                auths.append(cs.get("authority_vigilance", 0.0))
                phase = cs["phase"]
                if cid in prior_phases and prior_phases[cid] != phase:
                    crowd_change_total += 1
                prior_phases[cid] = phase

            idx = min(step.tick - 1, N_TICKS - 1)
            if aligns:
                alignment_over_time[idx].append(mean(aligns))
                density_over_time[idx].append(mean(densities))
                blame_concen_over_time[idx].append(mean(blames))
                shame_climate_over_time[idx].append(mean(shames))
                auth_vig_over_time[idx].append(mean(auths))

            rumor_tick_total += len(step.rumor_snapshot)

    def summarize(ts):
        return {
            "mean": round(mean([mean(b) if b else 0.0 for b in ts]), 3),
            "peak": round(max([mean(b) if b else 0.0 for b in ts]), 3),
            "final": round(mean(ts[-1]) if ts[-1] else 0.0, 3),
        }

    return {
        "scenario": "sacred",
        "F1_motifs": dict(motifs),
        "F2_actions": dict(actions),
        "F4_event_types": dict(event_types),
        "F3_alignment": summarize(alignment_over_time),
        "F3_blame": summarize(blame_concen_over_time),
        "F3_shame_climate": summarize(shame_climate_over_time),
        "F3_authority_vigilance": summarize(auth_vig_over_time),
        "F5_layer_contribution": {
            "rumor_tick_total": rumor_tick_total,
            "crowd_change_total": crowd_change_total,
            "event_total": event_total,
        },
    }


def main() -> int:
    print("[LOOP Iter 23] Sacred-gathering topology audit")
    print(f"  Seeds/scenario: {N_SEEDS}  Ticks: {N_TICKS}")
    print()

    fingerprints = {}
    print("  Computing fingerprints (calling, accusation, scarcity, sacred)...")
    for scn in ("calling", "accusation", "scarcity"):
        fingerprints[scn] = compute_fingerprints(scn)
    fingerprints["sacred"] = compute_sacred_fingerprint()

    print()
    print("=== Fingerprint highlights ===")
    for scn, fp in fingerprints.items():
        top_motifs = Counter(fp["F1_motifs"]).most_common(3)
        top_events = Counter(fp["F4_event_types"]).most_common(3)
        print(f"  {scn:<12}")
        print(f"    motifs top3: {top_motifs}")
        print(f"    events top3: {top_events}")
        print(f"    blame peak: {fp['F3_blame']['peak']}  "
              f"shame_climate peak: {fp['F3_shame_climate']['peak']}")

    print()
    print("=== Pairwise JS matrices ===")

    def print_matrix(key: str, label: str):
        print(f"\n  {label} (JS):")
        scns = list(fingerprints.keys())
        header = " ".join(f"{s:>10}" for s in scns)
        print(f"    {'':<12}  {header}")
        for a in scns:
            row = []
            for b in scns:
                js = _js(Counter(fingerprints[a][key]),
                         Counter(fingerprints[b][key]))
                row.append(f"{js:.3f}")
            print(f"    {a:<12}: " + " ".join(f"{v:>10}" for v in row))

    print_matrix("F1_motifs", "F1 motif distributions")
    print_matrix("F2_actions", "F2 action distributions")
    print_matrix("F4_event_types", "F4 event types")

    # Classify sacred
    def mean_js(key: str, scn_a: str, scn_b: str) -> float:
        return _js(Counter(fingerprints[scn_a][key]),
                   Counter(fingerprints[scn_b][key]))

    sac_vs_calling_F1 = mean_js("F1_motifs", "sacred", "calling")
    sac_vs_crisis_F1 = mean([mean_js("F1_motifs", "sacred", "accusation"),
                             mean_js("F1_motifs", "sacred", "scarcity")])
    sac_vs_calling_F4 = mean_js("F4_event_types", "sacred", "calling")
    sac_vs_crisis_F4 = mean([mean_js("F4_event_types", "sacred", "accusation"),
                             mean_js("F4_event_types", "sacred", "scarcity")])

    print()
    print("=== Sacred classification ===")
    print(f"  sacred vs calling : F1={sac_vs_calling_F1:.3f}  "
          f"F4={sac_vs_calling_F4:.3f}")
    print(f"  sacred vs crisis  : F1={sac_vs_crisis_F1:.3f}  "
          f"F4={sac_vs_crisis_F4:.3f}")

    if min(sac_vs_calling_F1, sac_vs_crisis_F1) >= 0.15:
        verdict = "THIRD TOPOLOGY -- sacred is distinct from both"
    elif sac_vs_calling_F1 < 0.10:
        verdict = "MERGES WITH CALLING (devotion topology)"
    elif sac_vs_crisis_F1 < 0.10:
        verdict = "MERGES WITH CRISIS"
    else:
        verdict = "HYBRID -- sacred is partial/intermediate"

    print(f"  verdict: {verdict}")

    # §15 condition 4 status
    n_topologies = None
    if "THIRD" in verdict:
        n_topologies = 3
        cond_4_status = "RESTORED -- §15 cond 4 satisfied with 3 genuine topologies"
    elif "HYBRID" in verdict:
        n_topologies = 2.5
        cond_4_status = "PARTIAL -- sacred is intermediate between 2 existing"
    else:
        n_topologies = 2
        cond_4_status = "UNCHANGED -- still 2 topologies; need new 3rd"

    print(f"  §15 cond 4 status: {cond_4_status}")
    print(f"  distinct topologies identified: {n_topologies}")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "loop_iter23_sacred_audit.json"
    )
    out_path.write_text(
        json.dumps({
            "iter": 23,
            "n_seeds": N_SEEDS, "n_ticks": N_TICKS,
            "fingerprints": fingerprints,
            "sacred_vs_calling_F1": sac_vs_calling_F1,
            "sacred_vs_crisis_F1": sac_vs_crisis_F1,
            "sacred_vs_calling_F4": sac_vs_calling_F4,
            "sacred_vs_crisis_F4": sac_vs_crisis_F4,
            "verdict": verdict,
            "cond_4_status": cond_4_status,
            "distinct_topologies": n_topologies,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
