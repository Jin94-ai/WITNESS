"""Iter 143: Audit Iter 142 V1 -- did agents recover or never get shame?

Iter 142 V1 had ALL 12 scarcity agents at poor_quarter, mean
final shame=0.0, "100% recovery". Caveat: low-pressure location
might prevent shame from accumulating in the first place, in which
case there's no recovery to claim.

This iter checks per-agent peak shame:
  - If peak > threshold (e.g., 1.5): agent did experience shame -> recovery real
  - If peak ~= 0: agent never experienced shame -> no recovery to measure

Run V1 (all at poor_quarter) and report per-agent (peak, final).
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

N_SEEDS = 3  # small N for detailed audit
N_TICKS = 500


def build_world(seed):
    from scripts.b_direction.run_scarcity_scene import (
        build_scarcity_cast, build_locations, build_network,
    )
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorldConfig, MicroWorld

    agents = build_scarcity_cast()
    aid_to_role = {a.agent_id: a.role_id for a in agents}
    placements = {a.agent_id: "poor_quarter" for a in agents}
    config = MicroWorldConfig(
        agents=agents,
        locations=build_locations(),
        initial_placements=placements,
        crowd_instances={
            "marketplace": CrowdState(crowd_id="marketplace", density=0.7),
            "poor_quarter": CrowdState(crowd_id="poor_quarter", density=0.5),
        },
        social_network=build_network([a.agent_id for a in agents]),
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
        seed=seed,
    )
    return MicroWorld(config), aid_to_role


def main() -> int:
    print(f"[Iter 143] Audit Iter 142 V1 -- recovery vs no-shame")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    per_agent_peak_seed = defaultdict(list)
    per_agent_final_seed = defaultdict(list)
    role_map_global = {}
    for seed in range(N_SEEDS):
        w, aid_to_role = build_world(seed)
        role_map_global.update(aid_to_role)
        per_shame = defaultdict(list)
        for _ in range(N_TICKS):
            w.step()
            for aid, a in w._agents.items():
                per_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
        for aid, ts in per_shame.items():
            per_agent_peak_seed[aid].append(max(ts))
            per_agent_final_seed[aid].append(ts[-1])

    print(f"  {'agent':<10} {'role':<22} {'peak shames':<28} {'final shames'}")
    no_shame_count = 0
    real_recovery_count = 0
    for aid in sorted(per_agent_peak_seed.keys()):
        role = role_map_global[aid]
        peaks = [round(p, 2) for p in per_agent_peak_seed[aid]]
        finals = [round(f, 2) for f in per_agent_final_seed[aid]]
        peak_str = str(peaks)
        final_str = str(finals)
        # Classify: if peak < 1.5 in all seeds, no shame; else, recovery (if final < 4)
        max_peak = max(peaks)
        if max_peak < 1.5:
            no_shame_count += 1
        elif max(finals) < 4.0:
            real_recovery_count += 1
        print(f"  {aid:<10} {role:<22} {peak_str:<28} {final_str}")

    print()
    print("=== Verdict on Iter 142 V1 finding ===")
    total = len(per_agent_peak_seed)
    print(f"  Total agents: {total}")
    print(f"  No shame ever (peak < 1.5): {no_shame_count}")
    print(f"  Real recovery (peak >= 1.5 AND final < 4): {real_recovery_count}")
    print(f"  Saturated/other: {total - no_shame_count - real_recovery_count}")
    print()
    if no_shame_count == total:
        print(f"  CAVEAT CONFIRMED: ALL agents at poor_quarter never experienced shame")
        print(f"  Iter 142 'rescue' was no-shame, not recovery")
        print(f"  Location placement prevents shame accumulation; doesn't enable recovery from it")
    elif real_recovery_count > total / 2:
        print(f"  RECOVERY GENUINE: most agents had peak shame > 1.5 then recovered")
        print(f"  Iter 142 finding stands as recovery, not no-shame")
    else:
        print(f"  MIXED: some no-shame, some genuine recovery")
        print(f"  Iter 142 finding is partially real")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "recovery_audit_iter143.json"
    )
    out_path.write_text(
        json.dumps({
            "n_seeds": N_SEEDS,
            "per_agent_peaks": {aid: per_agent_peak_seed[aid] for aid in per_agent_peak_seed},
            "per_agent_finals": {aid: per_agent_final_seed[aid] for aid in per_agent_final_seed},
            "no_shame_count": no_shame_count,
            "real_recovery_count": real_recovery_count,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
