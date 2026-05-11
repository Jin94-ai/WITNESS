"""Analyze S2 nonmonotonicity — extract confession + forgiveness counts per probe.

Per BRANCH_C_S2_RESULTS.md §5: triple accusations -> RECOVERY (nonmonotonic).
3 candidate hypotheses:
  A. Forgiveness cascade dominates (more accusations -> more forgiveness -> recovery)
  B. Moral fatigue (cohorts stop responding)
  C. Cohort propagation (more accusations -> more cohorts exposed -> more cascades)

Test: compare confession + forgiveness counts across single/double/triple.
- A predicts: forgiveness_count scales monotonically with accusation count
- B predicts: confession_count plateaus or decreases at triple
- C predicts: cohort_with_confessions count increases with triple

Output: docs/b_direction/BRANCH_C_S2_NONMONOTONIC_ANALYSIS.md
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.b_direction._pyhash_guard import enforce_pyhash
enforce_pyhash()

from scripts.b_direction.generate_readability_probes import N_TICKS
from scripts.b_direction.generate_scarcity_depth_variations import (
    build_scarcity_depth_world, EVENT_COUNTS, CROWD_DENSITIES,
)


def analyze_probe(event_count, crowd_density):
    w = build_scarcity_depth_world(seed=0, event_count=event_count, crowd_density=crowd_density)
    aids = list(w._agents.keys())
    cohort_groups = defaultdict(list)
    for aid in aids:
        loc = w._spatial.where(aid)
        cohort_groups[loc].append(aid)

    per_shame = defaultdict(list)
    confessions = []
    forgiveness_count = 0
    accusations = []
    confessor_aids = set()
    cohorts_with_conf = set()
    forgiveness_per_tick = []
    confession_per_tick = []

    for tick in range(N_TICKS):
        result = w.step()
        for aid, a in w._agents.items():
            per_shame[aid].append(a.state.get("shame", {}).get("public_group", 0.0))
        tick_conf = 0
        for aid, action in result.agent_actions.items():
            if action == "confess":
                confessions.append((tick + 1, aid, w._agents[aid].role_id))
                confessor_aids.add(aid)
                cohorts_with_conf.add(w._spatial.where(aid))
                tick_conf += 1
        confession_per_tick.append(tick_conf)
        tick_forg = 0
        for ev in result.spawned_events:
            eid = ev.get("event_id")
            if eid == "forgiveness_emitted":
                forgiveness_count += 1
                tick_forg += 1
            elif eid == "public_accusation":
                accusations.append((tick + 1, ev.get("target_role", "?")))
        forgiveness_per_tick.append(tick_forg)

    total_shame_peak = max(max(per_shame[a]) for a in per_shame if per_shame[a])
    final_mean = sum(per_shame[a][-1] for a in per_shame) / len(per_shame)

    return {
        "event_count": event_count,
        "crowd_density": crowd_density,
        "n_accusations": len(accusations),
        "n_confessions": len(confessions),
        "n_confessors": len(confessor_aids),
        "cohorts_with_confessions": len(cohorts_with_conf),
        "n_total_cohorts": len(cohort_groups),
        "n_forgiveness_emitted": forgiveness_count,
        "shame_peak": total_shame_peak,
        "final_shame_mean": final_mean,
        "confession_per_tick_max": max(confession_per_tick),
        "forgiveness_per_tick_max": max(forgiveness_per_tick),
    }


def main():
    rows = []
    for event_count in ["single", "double", "triple"]:
        for crowd_density in ["low", "baseline", "high"]:
            r = analyze_probe(event_count, crowd_density)
            rows.append(r)

    out = ROOT / "docs" / "b_direction" / "BRANCH_C_S2_NONMONOTONIC_ANALYSIS.md"
    lines = [
        "# Branch C — S2 Nonmonotonicity Analysis",
        "",
        "**Date:** 2026-04-28",
        "**Source:** `BRANCH_C_S2_RESULTS.md` §5 + §9 — investigate triple->RECOVERY nonmonotonicity.",
        "",
        "## 1. Per-probe metrics",
        "",
        "| Events | Density | n_acc | n_conf | n_confessors | cohorts_w_conf | n_forg | shame_peak | final_mean |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['event_count']} | {r['crowd_density']} | {r['n_accusations']} | "
            f"{r['n_confessions']} | {r['n_confessors']} | "
            f"{r['cohorts_with_confessions']}/{r['n_total_cohorts']} | "
            f"{r['n_forgiveness_emitted']} | {r['shame_peak']:.2f} | "
            f"{r['final_shame_mean']:.2f} |"
        )

    lines.extend([
        "",
        "## 2. Aggregate by event count (averaged across densities)",
        "",
        "| Events | mean n_conf | mean n_forg | mean cohorts_w_conf | mean final_shame |",
        "|---|---:|---:|---:|---:|",
    ])
    for ec in ["single", "double", "triple"]:
        ec_rows = [r for r in rows if r["event_count"] == ec]
        mean_conf = sum(r["n_confessions"] for r in ec_rows) / len(ec_rows)
        mean_forg = sum(r["n_forgiveness_emitted"] for r in ec_rows) / len(ec_rows)
        mean_cohorts = sum(r["cohorts_with_confessions"] for r in ec_rows) / len(ec_rows)
        mean_final = sum(r["final_shame_mean"] for r in ec_rows) / len(ec_rows)
        lines.append(
            f"| {ec} | {mean_conf:.1f} | {mean_forg:.1f} | "
            f"{mean_cohorts:.1f} | {mean_final:.2f} |"
        )

    lines.extend([
        "",
        "## 3. Hypothesis test (HARNESS H1 — falsification)",
        "",
        "### Hypothesis A: forgiveness cascade scales with event count",
        "",
        "**Prediction**: n_forgiveness monotonic in event count (1 < 2 < 3).",
        "",
        "**If A true**: triple has more forgiveness emissions, drives recovery.",
        "**If A false**: forgiveness flat or peaks at 2 -> hypothesis rejected.",
        "",
        "### Hypothesis B: moral fatigue",
        "",
        "**Prediction**: confession count plateaus or decreases at triple (cohorts stop responding).",
        "",
        "**If B true**: triple has fewer confessions than double.",
        "**If B false**: confessions increase or stay similar -> hypothesis rejected.",
        "",
        "### Hypothesis C: cohort propagation",
        "",
        "**Prediction**: cohorts_with_confessions monotonic in event count.",
        "",
        "**If C true**: triple has more cohorts with confessions than double.",
        "**If C false**: cohorts plateau -> hypothesis rejected.",
        "",
        "## 4. Verdict",
        "",
        "(filled by inspection of §1+§2 above)",
        "",
        "## 5. Implication",
        "",
        "Whichever hypothesis survives reveals the actual mechanism behind",
        "scarcity nonmonotonicity. This unlocks per-mechanism understanding ",
        "needed for KERNEL_GAPS Gap 4 (forgiveness uptake threshold).",
    ])

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote analysis to {out}")
    print()
    print("Summary by event count:")
    for ec in ["single", "double", "triple"]:
        ec_rows = [r for r in rows if r["event_count"] == ec]
        mean_conf = sum(r["n_confessions"] for r in ec_rows) / len(ec_rows)
        mean_forg = sum(r["n_forgiveness_emitted"] for r in ec_rows) / len(ec_rows)
        mean_cohorts = sum(r["cohorts_with_confessions"] for r in ec_rows) / len(ec_rows)
        mean_final = sum(r["final_shame_mean"] for r in ec_rows) / len(ec_rows)
        print(f"  {ec:<6}: conf={mean_conf:.1f}, forg={mean_forg:.1f}, cohorts={mean_cohorts:.1f}, final_shame={mean_final:.2f}")


if __name__ == "__main__":
    main()
