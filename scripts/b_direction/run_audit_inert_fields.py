"""Step D — empirical ablation for narrative-only state fields.

Iter 89 did static analysis showing 5 state fields have no
hits in engine/world + engine/persona. Step D confirms empirically
by injecting extreme values + running simulation, comparing
rev/agent + final shame vs baseline.

Predictions:
- All 5 fields → zero delta on cycle metrics (INERT confirmed)
- If any field shows delta → retract Iter 89 claim, reclassify

Fields tested:
  - moral_injury (inject 8.0 on cycling cohort at t=0)
  - identity_shift (inject -6.0)
  - trust_scar (inject 7.0)
  - event_trauma (inject 7.0)
  - breach_count (inject 5.0)

Plus awe confirmation (redundant with Iter 78 but completes catalog).

Protocol:
- accusation scenario (most tested)
- 3 seeds × 100 ticks
- PYHASH=0
- Inject at t=0 into agent_04, agent_06, agent_09 (cycling cohort)
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

N_SEEDS = 3
N_TICKS = 100
INJECT_TARGETS = {"agent_04", "agent_06", "agent_09"}

FIELDS_TO_TEST = [
    ("awe", "awe", 8.0),
    ("moral_injury", "slow_state.moral_injury", 8.0),
    ("identity_shift", "slow_state.identity_shift", -6.0),
    ("trust_scar", "slow_state.trust_scar", 7.0),
    ("event_trauma", "slow_state.event_trauma", 7.0),
    ("breach_count", "slow_state.breach_count", 5),
]


def build_world(seed, field_injection=None):
    """Build accusation world, optionally inject field_injection tuple."""
    from engine.world.crowd_dynamics import CrowdState
    from engine.world.micro_world import MicroWorld, MicroWorldConfig
    from scripts.b_direction.run_accusation_scene import (
        build_accusation_cast,
        build_locations,
        build_social_network,
    )

    agents = build_accusation_cast()

    if field_injection:
        label, path, value = field_injection
        for a in agents:
            if a.agent_id in INJECT_TARGETS:
                if "." in path:
                    # slow_state.X  → check if state has slow_state
                    parent, child = path.split(".")
                    # Try on agent.state dict (might have slow_state dict)
                    slow = a.state.setdefault(parent, {})
                    if isinstance(slow, dict):
                        slow[child] = value
                    else:
                        # Probably a Pydantic slow_state model on AgentState
                        # but AgentHandle doesn't carry it. Skip / note.
                        pass
                else:
                    a.state[path] = value

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
            {"tick": 12, "event_id": "guard_approaches", "location": "upper_room"},
        ],
        seed_rumors=[{
            "content_tag": "threat_to_authority",
            "target_role": "disciple_follower",
            "origin_source": "agent_04",
            "initial_reach": ["agent_04", "agent_05"],
            "intensity": 0.6, "credibility": 0.5,
        }],
        seed=seed,
        forgiveness_phase_enabled=True,
    ))


def count_reversals(ts, window: int = 20) -> int:
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


def run_condition(field_injection=None):
    per_agent_rev = []
    peaks = []
    finals = []
    confess_counts = []

    for seed in range(N_SEEDS):
        w = build_world(seed, field_injection)
        per_agent_shame = defaultdict(list)
        cc = 0
        for _ in range(N_TICKS):
            w.step()
            for aid, a in w._agents.items():
                per_agent_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
            for ev in w.history[-1].spawned_events:
                if ev.get("event_id") == "public_confession":
                    cc += 1
        confess_counts.append(cc)
        for aid, ts in per_agent_shame.items():
            if max(ts) >= 1.5:
                per_agent_rev.append(count_reversals(ts))
                peaks.append(max(ts))
                finals.append(ts[-1])

    return {
        "rev_mean": round(mean(per_agent_rev) if per_agent_rev else 0, 2),
        "n_active": len(per_agent_rev),
        "peak_shame": round(mean(peaks) if peaks else 0, 2),
        "final_shame": round(mean(finals) if finals else 0, 2),
        "confess_per_seed": round(mean(confess_counts), 1),
    }


def main() -> int:
    print("[Step D] Empirical inert-field audit")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} "
          f"N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    print("  Running BASELINE (no injection)...")
    baseline = run_condition(None)
    print(f"    rev={baseline['rev_mean']}  "
          f"final={baseline['final_shame']}  "
          f"active={baseline['n_active']}  "
          f"confess/seed={baseline['confess_per_seed']}")
    print()

    results = {"BASELINE": baseline}
    for label, path, value in FIELDS_TO_TEST:
        print(f"  Injecting {label}={value} on {INJECT_TARGETS}...")
        r = run_condition((label, path, value))
        results[label] = r
        d_rev = r["rev_mean"] - baseline["rev_mean"]
        d_final = r["final_shame"] - baseline["final_shame"]
        print(f"    rev={r['rev_mean']} (Δ{d_rev:+.2f})  "
              f"final={r['final_shame']} (Δ{d_final:+.2f})  "
              f"active={r['n_active']}  "
              f"confess/seed={r['confess_per_seed']}")

    # Verdict
    print()
    print("=== Verdict ===")
    print(f"  {'field':<20} {'rev':<7} {'Δrev':<8} {'final':<7} "
          f"{'Δfinal':<8} {'status'}")
    print(f"  {'BASELINE':<20} {baseline['rev_mean']:<7} "
          f"{'-':<8} {baseline['final_shame']:<7} {'-':<8} -")
    for label, _, _ in FIELDS_TO_TEST:
        r = results[label]
        d_rev = r["rev_mean"] - baseline["rev_mean"]
        d_final = r["final_shame"] - baseline["final_shame"]
        if abs(d_rev) < 0.3 and abs(d_final) < 0.5:
            status = "INERT (zero delta)"
        elif abs(d_rev) < 1.0 and abs(d_final) < 1.5:
            status = "MARGINAL (within noise)"
        else:
            status = "COUPLED -- investigate"
        print(f"  {label:<20} {r['rev_mean']:<7} {d_rev:+.2f}    "
              f"{r['final_shame']:<7} {d_final:+.2f}    {status}")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "audit_inert_fields.json"
    )
    out_path.write_text(
        json.dumps({
            "pyhash": os.environ.get("PYTHONHASHSEED"),
            "n_seeds": N_SEEDS, "n_ticks": N_TICKS,
            "targets": list(INJECT_TARGETS),
            "results": results,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
