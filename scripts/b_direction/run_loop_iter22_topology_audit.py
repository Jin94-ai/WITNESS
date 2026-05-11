"""WORLD_FLOW_LOOP Iter 22 -- Step 3: Scenario Diversity Structural Audit.

Tests whether the 3 scenarios (calling, accusation, scarcity) differ at
the pressure-topology level or only at surface content level.

Per NEXT_STEPS Step 3, computes 5 fingerprints per scenario and
compares pairwise. If scenarios show high similarity on fingerprints,
they are content-different but structurally same (problem). Iter 21
decomposition says Layer 2 (outcomes) should be scenario-dependent;
Iter 22 confirms whether this is actual or nominal.

Fingerprints per scenario (aggregated over 5 seeds):
  F1: motif activation distribution (top-8 motifs, normalized)
  F2: action family distribution (over 16 actions, normalized)
  F3: pressure profile over time (mean alignment / density / blame
      concentration / shame_climate / authority_vigilance per tick)
  F4: event family composition (emergent event type counts)
  F5: layer contribution ratio (rumor-tick-count : crowd-change-count :
      event-count)

Pairwise similarity:
  JS divergence on F1, F2, F4 (they are distributions)
  L1 distance on F3 time series summary
  Cosine-ish on F5 ratios

Verdict:
  If mean pairwise JS on F1+F2 is HIGH (>=0.2) AND F4 shows distinct
  dominant event types: topology differs.
  If mean pairwise JS is LOW (<=0.05): scenarios are structurally
  same, finding fails.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

N_SEEDS = 5
N_TICKS = 30


def _js(p: Counter, q: Counter) -> float:
    keys = set(p) | set(q)
    if not keys:
        return 0.0
    tp = sum(p.values()) or 1
    tq = sum(q.values()) or 1
    pp = {k: p.get(k, 0) / tp for k in keys}
    qp = {k: q.get(k, 0) / tq for k in keys}
    mp = {k: 0.5 * (pp[k] + qp[k]) for k in keys}
    def kl(a, b):
        return sum(a[k] * math.log(a[k] / b[k])
                   for k in keys if a[k] > 0 and b[k] > 0)
    return (0.5 * kl(pp, mp) + 0.5 * kl(qp, mp)) / math.log(2)


def run_scenario(scenario: str, seed: int):
    if scenario == "accusation":
        from scripts.b_direction.run_accusation_scene import build_micro_world
        w = build_micro_world(seed=seed)
    elif scenario == "scarcity":
        from scripts.b_direction.run_scarcity_scene import build_micro_world
        w = build_micro_world(seed=seed)
    elif scenario == "calling":
        from scripts.b_direction.run_loop_iter1_transition import (
            build_micro_world,
        )
        w = build_micro_world(seed=seed, enable_transition=True)
    else:
        raise ValueError(scenario)
    w.run(N_TICKS)
    return w


def compute_fingerprints(scenario: str) -> dict:
    motifs: Counter = Counter()
    actions: Counter = Counter()
    event_types: Counter = Counter()

    # time-series pressure profile (per-tick mean across seeds)
    alignment_over_time: list[list[float]] = [[] for _ in range(N_TICKS)]
    density_over_time: list[list[float]] = [[] for _ in range(N_TICKS)]
    blame_concen_over_time: list[list[float]] = [[] for _ in range(N_TICKS)]
    shame_climate_over_time: list[list[float]] = [[] for _ in range(N_TICKS)]
    authority_vigilance_over_time: list[list[float]] = [[] for _ in range(N_TICKS)]

    rumor_tick_total = 0
    crowd_change_total = 0
    event_total = 0

    for s in range(N_SEEDS):
        w = run_scenario(scenario, seed=s)
        prior_phases: dict[str, str] = {}
        for step in w.history:
            motifs.update(step.agent_motifs.values())
            actions.update(step.agent_actions.values())

            for ev in step.spawned_events:
                et = ev.get("event_id", "?")
                event_types[et] += 1
                event_total += 1

            # Per-tick aggregates (mean across crowds)
            aligns, densities, blames, shames, auths = [], [], [], [], []
            for cid, cs in step.crowd_state_snapshot.items():
                aligns.append(cs["alignment"])
                densities.append(cs["density"])
                blames.append(
                    max(cs.get("blame", {}).values(), default=0.0)
                )
                shames.append(cs.get("shame_climate", 0.0))
                auths.append(cs.get("authority_vigilance", 0.0))
                # Count phase change
                phase = cs["phase"]
                key = f"{cid}"
                if key in prior_phases and prior_phases[key] != phase:
                    crowd_change_total += 1
                prior_phases[key] = phase

            idx = min(step.tick - 1, N_TICKS - 1)
            if aligns:
                alignment_over_time[idx].append(mean(aligns))
                density_over_time[idx].append(mean(densities))
                blame_concen_over_time[idx].append(mean(blames))
                shame_climate_over_time[idx].append(mean(shames))
                authority_vigilance_over_time[idx].append(mean(auths))

            rumor_tick_total += len(step.rumor_snapshot)

    # Aggregate time-series
    align_profile = [mean(b) if b else 0.0 for b in alignment_over_time]
    density_profile = [mean(b) if b else 0.0 for b in density_over_time]
    blame_profile = [mean(b) if b else 0.0 for b in blame_concen_over_time]
    shame_profile = [mean(b) if b else 0.0 for b in shame_climate_over_time]
    auth_profile = [mean(b) if b else 0.0 for b in authority_vigilance_over_time]

    # Summary statistics for time-series
    def summarize(ts):
        return {
            "mean": round(mean(ts), 3),
            "peak": round(max(ts), 3),
            "final": round(ts[-1] if ts else 0.0, 3),
            "auc": round(sum(ts) / max(1, len(ts)), 3),  # area / length
        }

    return {
        "scenario": scenario,
        "F1_motifs": dict(motifs),
        "F2_actions": dict(actions),
        "F4_event_types": dict(event_types),
        "F3_alignment": summarize(align_profile),
        "F3_density": summarize(density_profile),
        "F3_blame": summarize(blame_profile),
        "F3_shame_climate": summarize(shame_profile),
        "F3_authority_vigilance": summarize(auth_profile),
        "F5_layer_contribution": {
            "rumor_tick_total": rumor_tick_total,
            "crowd_change_total": crowd_change_total,
            "event_total": event_total,
        },
    }


def l1_distance_profile(ap: dict, bp: dict) -> float:
    keys = set(ap) | set(bp)
    return sum(abs(ap.get(k, 0.0) - bp.get(k, 0.0)) for k in keys)


def normalized_cosine(a: dict, b: dict) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    na = math.sqrt(sum(v * v for v in a.values())) or 1
    nb = math.sqrt(sum(v * v for v in b.values())) or 1
    return dot / (na * nb)


def main() -> int:
    print(f"[LOOP Iter 22] Step 3 -- Scenario Diversity Structural Audit")
    print(f"  Scenarios: calling, accusation, scarcity")
    print(f"  Seeds/scenario: {N_SEEDS}  Ticks: {N_TICKS}")
    print()

    fingerprints = {}
    for scn in ("calling", "accusation", "scarcity"):
        print(f"  Computing fingerprint: {scn}...")
        fingerprints[scn] = compute_fingerprints(scn)

    print()
    print("=== F1 motif distribution (top5) ===")
    for scn, fp in fingerprints.items():
        top = Counter(fp["F1_motifs"]).most_common(5)
        print(f"  {scn:<12}: {top}")

    print()
    print("=== F2 action distribution (top5) ===")
    for scn, fp in fingerprints.items():
        top = Counter(fp["F2_actions"]).most_common(5)
        print(f"  {scn:<12}: {top}")

    print()
    print("=== F3 pressure time-series summary ===")
    for scn, fp in fingerprints.items():
        print(f"  {scn:<12} "
              f"align peak={fp['F3_alignment']['peak']:.2f}  "
              f"blame peak={fp['F3_blame']['peak']:.2f}  "
              f"shame_climate peak={fp['F3_shame_climate']['peak']:.2f}  "
              f"auth_vig peak={fp['F3_authority_vigilance']['peak']:.2f}")

    print()
    print("=== F4 event types ===")
    for scn, fp in fingerprints.items():
        top = Counter(fp["F4_event_types"]).most_common(5)
        print(f"  {scn:<12}: {top}")

    print()
    print("=== F5 layer contribution ===")
    for scn, fp in fingerprints.items():
        l = fp["F5_layer_contribution"]
        total = l["rumor_tick_total"] + l["crowd_change_total"] + l["event_total"]
        ratios = [round(v / total, 3) if total else 0 for v in
                  (l["rumor_tick_total"], l["crowd_change_total"], l["event_total"])]
        print(f"  {scn:<12} rumor:{l['rumor_tick_total']:>4} "
              f"crowd_changes:{l['crowd_change_total']:>4} "
              f"events:{l['event_total']:>4}  "
              f"ratios(R:C:E)={ratios}")

    print()
    print("=== Pairwise similarity matrices ===")

    def js_matrix(key: str, label: str):
        print(f"\n  {label} (JS divergence):")
        scns = list(fingerprints.keys())
        for i, a in enumerate(scns):
            row = []
            for b in scns:
                js = _js(Counter(fingerprints[a][key]),
                         Counter(fingerprints[b][key]))
                row.append(f"{js:.3f}")
            print(f"    {a:<12}: " + " ".join(f"{v:>6}" for v in row))
        print(f"              " + " ".join(f"{s:>6}" for s in scns))

    js_matrix("F1_motifs", "F1 motif distributions")
    js_matrix("F2_actions", "F2 action distributions")
    js_matrix("F4_event_types", "F4 event types")

    # Mean pairwise JS
    def mean_pairwise(key: str):
        scns = list(fingerprints.keys())
        vals = []
        for i, a in enumerate(scns):
            for j, b in enumerate(scns):
                if i < j:
                    vals.append(_js(Counter(fingerprints[a][key]),
                                    Counter(fingerprints[b][key])))
        return mean(vals) if vals else 0.0

    mean_F1 = mean_pairwise("F1_motifs")
    mean_F2 = mean_pairwise("F2_actions")
    mean_F4 = mean_pairwise("F4_event_types")

    print()
    print("=== Aggregate verdict ===")
    print(f"  mean pairwise JS:  F1={mean_F1:.3f}  F2={mean_F2:.3f}  F4={mean_F4:.3f}")

    # Verdict rules (Step 3):
    # - If all fingerprints very similar (mean JS <= 0.05), topology same -> fail
    # - If at least one distribution clearly differs (JS >= 0.2), topology differs
    # - Intermediate: scenarios differ at some level but not others

    max_mean = max(mean_F1, mean_F2, mean_F4)
    min_mean = min(mean_F1, mean_F2, mean_F4)

    if min_mean <= 0.05 and max_mean <= 0.10:
        verdict = "STRUCTURAL SAMENESS -- scenarios are topologically similar"
    elif max_mean >= 0.20:
        verdict = (
            "STRUCTURAL DIVERGENCE -- at least one fingerprint dimension "
            "clearly distinguishes scenarios"
        )
    else:
        verdict = (
            "PARTIAL -- scenarios differ weakly on some dimensions, "
            "similar on others"
        )
    print(f"  verdict: {verdict}")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "loop_iter22_topology_audit.json"
    )
    out_path.write_text(
        json.dumps({
            "iter": 22,
            "step_ref": "NEXT_STEPS.md Step 3",
            "n_seeds": N_SEEDS, "n_ticks": N_TICKS,
            "fingerprints": fingerprints,
            "mean_pairwise_JS": {
                "F1_motifs": mean_F1,
                "F2_actions": mean_F2,
                "F4_event_types": mean_F4,
            },
            "verdict": verdict,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
