"""Step E — Mixed-arc minimal probe (freeze audit).

Two mixed scenarios:
  1. accusation + sacred overlap
  2. scarcity + private grief overlap

Uses only KNOWN-COUPLED mixing mechanisms (Iter 77-80 established
sacred events are dormant, awe is decoupled, layered blame hits
motif-filter). Working approaches:
  - Direct guilt + grief injection into cohort (Iter 57/80 method)
  - Crowd-level state initialization (dominant_emotion on crowd)
  - Inter-scenario agent mixing (cast composition)

## Mixing design

### Probe 1 — accusation + sacred overlap
Base: accusation cast.
Sacred overlay:
  - Crowd dominant_emotion = "awe" in a subset of crowds
  - Direct awe injection into 2 agents at t=0 (documenting awe-decouple
    via Iter 78)
  - (Acknowledge sacred state fields are decoupled; mixing is mostly
    crowd-emotion baseline shift)

### Probe 2 — scarcity + private grief overlap
Base: scarcity cast.
Private grief overlay:
  - Guilt (4.2) + grief (3.0) injection into 3 fisher/family agents
    (Iter 57 coupling-verified mixing)

## Measured

- rev/agent per cohort (injected vs non-injected)
- grieve_frac
- Phase 2a ablation under mixed condition
- Readability-relevant patterns: does mixed probe look like
  coherent arc or collapse to single loop?

## Per probe conditions
  A: baseline (no mixing)
  B: mixing (full overlay)
  C: B + Phase 2a off (mixed + ablation)

5 seeds × 200 ticks each, PYHASH=0.
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

N_SEEDS = 5
N_TICKS = 200


def build_accusation_sacred_mix(seed, *, mix=False, phase2a=True):
    """Probe 1: accusation + sacred overlay.

    Sacred overlay:
      - awe=6.0 injected on agent_01 + agent_02 (upper_room disciples)
      - crowd.dominant_emotion = "awe" on priest_courtyard (Phase 1
        handler doesn't read dominant_emotion directly, but shame_climate
        starts lower via _update_agent_state_from_world pressure mapping)
      - NOTE: sacred state/events are largely decoupled (Iter 78);
        this mixing mostly tests whether ANY sacred overlay changes
        cycling under accusation's kernel machinery.
    """
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast, build_locations, build_social_network,
    )
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorldConfig, MicroWorld

    agents = build_accusation_cast()
    if mix:
        for a in agents:
            if a.agent_id in ("agent_01", "agent_02"):
                a.state["awe"] = 6.0

    aids = [a.agent_id for a in agents]
    priest_crowd = CrowdState(crowd_id="priest_courtyard", density=0.4)
    if mix:
        priest_crowd.dominant_emotion = "awe"

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
            "priest_courtyard": priest_crowd,
            "city_street": CrowdState(crowd_id="city_street", density=0.6),
        },
        social_network=build_social_network(aids),
        seed_events=[
            {"tick": 3, "event_id": "public_accusation",
             "target_role": "disciple_follower", "location": "priest_courtyard"},
            {"tick": 7, "event_id": "public_accusation",
             "target_role": "outsider", "location": "city_street"},
            {"tick": 12, "event_id": "guard_approaches", "location": "upper_room"},
        ],
        seed_rumors=[{
            "content_tag": "threat_to_authority",
            "target_role": "disciple_follower",
            "origin_source": "agent_04",
            "initial_reach": ["agent_04", "agent_05"],
            "intensity": 0.6, "credibility": 0.5,
        }],
        seed=seed, forgiveness_phase_enabled=phase2a,
    ))


def build_scarcity_grief_mix(seed, *, mix=False, phase2a=True):
    """Probe 2: scarcity + private grief overlay.

    Grief overlay (coupling-verified via Iter 57):
      - Inject guilt.self=6.0, guilt.primary_focus=4.2, grief=3.0
        on agent_03 + agent_04 + agent_05 (fisher_laborer cohort)
    """
    from scripts.b_direction.run_scarcity_scene import (
        build_scarcity_cast, build_locations, build_network,
    )
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorldConfig, MicroWorld

    agents = build_scarcity_cast()
    if mix:
        for a in agents:
            if a.agent_id in ("agent_03", "agent_04", "agent_05"):
                a.state.setdefault("guilt", {})
                a.state["guilt"]["self"] = 6.0
                a.state["guilt"]["primary_focus"] = 4.2
                a.state["grief"] = 3.0

    aids = [a.agent_id for a in agents]
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=build_locations(),
        initial_placements={
            "agent_01": "granary", "agent_02": "poor_quarter",
            "agent_03": "marketplace", "agent_04": "poor_quarter",
            "agent_05": "marketplace", "agent_06": "granary",
            "agent_07": "granary", "agent_08": "marketplace",
            "agent_09": "marketplace", "agent_10": "poor_quarter",
            "agent_11": "poor_quarter", "agent_12": "granary",
        },
        crowd_instances={
            "marketplace": CrowdState(crowd_id="marketplace", density=0.7),
            "poor_quarter": CrowdState(crowd_id="poor_quarter", density=0.5),
        },
        social_network=build_network(aids),
        seed_events=[
            {"tick": 5, "event_id": "public_accusation",
             "target_role": "merchant", "location": "marketplace"},
            {"tick": 15, "event_id": "guard_approaches", "location": "marketplace"},
        ],
        seed_rumors=[{
            "content_tag": "misdeed", "target_role": "merchant",
            "origin_source": "agent_09",
            "initial_reach": ["agent_09", "agent_10"],
            "intensity": 0.7, "credibility": 0.6,
        }],
        seed=seed, forgiveness_phase_enabled=phase2a,
    ))


def count_reversals(ts, window=20):
    if len(ts) < 2 * window:
        return 0
    smoothed = [sum(ts[i:i + window]) / window
                for i in range(len(ts) - window + 1)]
    reversals = 0
    prev = None
    for i in range(1, len(smoothed)):
        d = smoothed[i] - smoothed[i - 1]
        if abs(d) < 0.05:
            continue
        direction = 1 if d > 0 else -1
        if prev is not None and direction != prev:
            reversals += 1
        prev = direction
    return reversals


def run_probe(builder, probe_label, inject_targets):
    """Run A/B/C conditions for a probe. Return results dict."""
    conditions = [
        ("A_baseline",      False, True),
        ("B_mixed",         True,  True),
        ("C_mixed_p2a_off", True,  False),
    ]
    out = {}
    for name, mix, p2a in conditions:
        per_agent_rev = []
        per_agent_rev_inj = []
        per_agent_rev_oth = []
        peaks = []
        finals = []
        confess_counts = []
        grieve_counts = []

        for s in range(N_SEEDS):
            w = builder(s, mix=mix, phase2a=p2a)
            per_agent_shame = defaultdict(list)
            cc = 0
            gc = 0
            for _ in range(N_TICKS):
                step = w.step()
                for aid, a in w._agents.items():
                    per_agent_shame[aid].append(
                        a.state.get("shame", {}).get("public_group", 0.0))
                for ev in w.history[-1].spawned_events:
                    if ev.get("event_id") == "public_confession":
                        cc += 1
                for aid, motif in step.agent_motifs.items():
                    if motif == "grieve":
                        gc += 1
            confess_counts.append(cc)
            grieve_counts.append(gc)
            for aid, ts in per_agent_shame.items():
                if max(ts) >= 1.5:
                    rev = count_reversals(ts)
                    per_agent_rev.append(rev)
                    if aid in inject_targets:
                        per_agent_rev_inj.append(rev)
                    else:
                        per_agent_rev_oth.append(rev)
                    peaks.append(max(ts))
                    finals.append(ts[-1])

        out[name] = {
            "probe": probe_label,
            "rev_all": round(mean(per_agent_rev) if per_agent_rev else 0, 2),
            "rev_inj": round(mean(per_agent_rev_inj) if per_agent_rev_inj else 0, 2),
            "rev_oth": round(mean(per_agent_rev_oth) if per_agent_rev_oth else 0, 2),
            "peak_shame": round(mean(peaks) if peaks else 0, 2),
            "final_shame": round(mean(finals) if finals else 0, 2),
            "confess_per_seed": round(mean(confess_counts), 1),
            "grieve_per_seed": round(mean(grieve_counts), 1),
            "n_active_all": len(per_agent_rev),
            "n_active_inj": len(per_agent_rev_inj),
            "n_active_oth": len(per_agent_rev_oth),
        }
    return out


def analyze_probe(label, results, inject_desc):
    print(f"\n=== {label} ===")
    print(f"  Mixing: {inject_desc}")
    print(f"  {'condition':<20} {'rev_all':<8} {'rev_inj':<8} {'rev_oth':<8} "
          f"{'final':<7} {'confess/s':<10} {'grieve/s'}")
    for cond in ("A_baseline", "B_mixed", "C_mixed_p2a_off"):
        r = results[cond]
        print(f"  {cond:<20} {r['rev_all']:<8} {r['rev_inj']:<8} "
              f"{r['rev_oth']:<8} {r['final_shame']:<7} "
              f"{r['confess_per_seed']:<10} {r['grieve_per_seed']}")

    # Analysis
    a = results["A_baseline"]
    b = results["B_mixed"]
    c = results["C_mixed_p2a_off"]

    print(f"\n  Mixing effect (B vs A):")
    print(f"    rev_all:  {a['rev_all']:<6} -> {b['rev_all']:<6} "
          f"(Δ{b['rev_all'] - a['rev_all']:+.2f})")
    print(f"    final:    {a['final_shame']:<6} -> {b['final_shame']:<6} "
          f"(Δ{b['final_shame'] - a['final_shame']:+.2f})")
    print(f"    grieve:   {a['grieve_per_seed']:<6} -> {b['grieve_per_seed']:<6} "
          f"(Δ{b['grieve_per_seed'] - a['grieve_per_seed']:+.1f})")

    print(f"\n  Ablation under mixing (B vs C):")
    print(f"    rev_all:  {b['rev_all']:<6} -> {c['rev_all']:<6} "
          f"(cycles collapse if →0: {c['rev_all'] < 0.5})")
    print(f"    final:    {b['final_shame']:<6} -> {c['final_shame']:<6} "
          f"(ceiling if ~10: {c['final_shame'] >= 9.5})")

    # Collapse check
    collapse = (
        abs(b['rev_all'] - a['rev_all']) < 0.5 and
        abs(b['grieve_per_seed'] - a['grieve_per_seed']) < 10
    )
    cohort_separation = (
        b.get('rev_inj', 0) > 0 and abs(b['rev_inj'] - b['rev_oth']) > 0.5
    )
    p1_holds = c['rev_all'] < 0.5

    print(f"\n  Diagnostics:")
    print(f"    Mixing visible (vs A): {not collapse}")
    print(f"    Cohort separation (inj vs oth): {cohort_separation}")
    print(f"    P1 holds under mixing: {p1_holds}")


def main() -> int:
    print(f"[Step E] Mixed-arc minimal probe")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} "
          f"N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")

    # Probe 1: accusation + sacred
    print("\n### PROBE 1: accusation + sacred overlay ###")
    probe1_inject = {"agent_01", "agent_02"}
    r1 = run_probe(
        build_accusation_sacred_mix,
        "accusation+sacred",
        probe1_inject,
    )
    analyze_probe(
        "Probe 1: accusation + sacred",
        r1,
        "awe=6 on agent_01,02 + priest_courtyard dominant=awe",
    )

    # Probe 2: scarcity + grief
    print("\n### PROBE 2: scarcity + private grief overlay ###")
    probe2_inject = {"agent_03", "agent_04", "agent_05"}
    r2 = run_probe(
        build_scarcity_grief_mix,
        "scarcity+grief",
        probe2_inject,
    )
    analyze_probe(
        "Probe 2: scarcity + grief",
        r2,
        "guilt=6/grief=3 on agent_03,04,05 (fisher cohort)",
    )

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "mixed_arc_probe.json"
    )
    out_path.write_text(
        json.dumps({
            "pyhash": os.environ.get("PYTHONHASHSEED"),
            "n_seeds": N_SEEDS, "n_ticks": N_TICKS,
            "probe_1_accusation_sacred": r1,
            "probe_2_scarcity_grief": r2,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
