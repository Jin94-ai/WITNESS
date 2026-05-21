"""Iter 162: Re-audit INERT field claim under proper PYHASH + N=15.

Original audit (Iter 89 era) at N=3 × 100t with broken PYHASH found
6 fields INERT in MicroWorld: awe, moral_injury, identity_shift,
trust_scar, event_trauma, breach_count.

Iter 123 later found awe is CONDITIONALLY load-bearing in sacred
contexts. So the audit was scenario-dependent.

Per directive §6 improvement point 1 (decorative cleanup), re-verify
INERT claim with:
- Proper PYHASH guard (Iter 105 fix)
- N=15 seeds (vs original N=3)
- 500 ticks (vs original 100)
- Per-agent peak/final classification (vs aggregate)

If still INERT → field can be safely marked for reserve/remove.
If NOT inert → audit needs update.
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


def build_world(seed, *, inject_field=None, inject_value=0.0):
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast,
        build_locations,
        build_social_network,
    )

    agents = build_accusation_cast()
    aids = [a.agent_id for a in agents]

    # Inject value into target field for agent_04, agent_06, agent_09
    if inject_field:
        target_agents = ["agent_04", "agent_06", "agent_09"]
        for agent in agents:
            if agent.agent_id in target_agents:
                if "." in inject_field:
                    parent, child = inject_field.split(".")
                    parent_dict = agent.state.setdefault(parent, {})
                    parent_dict[child] = inject_value
                else:
                    agent.state[inject_field] = inject_value

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


def run_baseline_or_injected(label, *, inject_field=None, inject_value=0.0):
    """Run scenario, return per-seed mean shame trajectories."""
    final_means = []
    for seed in range(N_SEEDS):
        w = build_world(seed, inject_field=inject_field, inject_value=inject_value)
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
        if ag_finals:
            final_means.append(mean(ag_finals))
        else:
            final_means.append(0.0)
    return {
        "label": label,
        "per_seed_finals": [round(f, 2) for f in final_means],
        "overall_mean": round(mean(final_means), 3),
        "overall_stdev": round(stdev(final_means) if len(final_means) > 1 else 0, 3),
    }


def main() -> int:
    print("[Iter 162] INERT field re-audit (post Iter 105 PYHASH + N=15)")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    baseline = run_baseline_or_injected("baseline")
    print(f"  baseline: mean={baseline['overall_mean']} stdev={baseline['overall_stdev']}")
    print()

    inject_tests = [
        ("awe=8.0", "awe", 8.0),
        ("moral_injury=8.0", "moral_injury", 8.0),
        ("identity_shift=-6.0", "identity_shift", -6.0),
        ("trust_scar=7.0", "trust_scar", 7.0),
        ("event_trauma=7.0", "event_trauma", 7.0),
        ("breach_count=5", "breach_count", 5),
    ]
    results = {"baseline": baseline}
    for name, field, value in inject_tests:
        r = run_baseline_or_injected(name, inject_field=field, inject_value=value)
        results[name] = r
        delta = r["overall_mean"] - baseline["overall_mean"]
        if abs(delta) < 0.5:
            tag = "[INERT]"
        elif abs(delta) < 1.5:
            tag = "[weak effect]"
        else:
            tag = "[LOAD-BEARING]"
        print(f"  {name}: mean={r['overall_mean']} (Δ {delta:+.2f}) {tag}")

    print()
    print("=== INERT field re-audit verdict ===")
    print(f"  Baseline: {baseline['overall_mean']:.2f} ± {baseline['overall_stdev']:.2f}")
    print("  Pre-PYHASH-fix audit (Iter 89): all 6 fields INERT")
    print()
    inert_count = 0
    for name, _, _ in inject_tests:
        delta = results[name]["overall_mean"] - baseline["overall_mean"]
        status = "INERT" if abs(delta) < 0.5 else "non-inert"
        if status == "INERT":
            inert_count += 1
        print(f"  {name}: Δ {delta:+.2f} -> {status}")
    print()
    print(f"  Inert: {inert_count}/6 (Iter 162 N=15 PYHASH-corrected)")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "inert_reaudit_iter162.json"
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
