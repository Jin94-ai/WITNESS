"""Meso-scale probe (Priority 5 of WORLD_BUILDING).

Verifies public_suspicion (new field added in Iter 90):
  1. Generates from accusation + authority_suppression events
  2. Decays autonomously (0.02/tick)
  3. Couples to social_threat pressure
  4. Reduced by Phase 2a forgiveness + shame_repair

Method: 3 conditions × 3 seeds × 100 ticks
  A: baseline (with public_suspicion active per new wiring)
  B: zero-clamp (manually zero public_suspicion every tick — INERT control)
  C: extreme-inject (manually set public_suspicion = 1.0 every tick — saturated control)

Compare cycle metrics + final shame across A/B/C.
If A/B differ measurably → public_suspicion has real coupling.
If A/B identical → field is wired but downstream pressure already
    saturated; new variable is decorative.
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


def build_world(seed):
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
            {"tick": 3, "event_id": "public_accusation",
             "target_role": "disciple_follower", "location": "priest_courtyard"},
            {"tick": 7, "event_id": "public_accusation",
             "target_role": "outsider", "location": "city_street"},
            {"tick": 12, "event_id": "guard_approaches", "location": "priest_courtyard"},
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


def run_condition(label, ps_override=None):
    """ps_override: None=normal, 0.0=zero-clamp every tick, 1.0=saturated."""
    revs = []
    finals = []
    confess_counts = []
    ps_trace = []  # public_suspicion over time (1 seed for visualization)

    for seed in range(N_SEEDS):
        w = build_world(seed)
        per_agent_shame = defaultdict(list)
        per_tick_ps = []
        cc = 0
        for tick_idx in range(N_TICKS):
            w.step()
            # Override after step
            if ps_override is not None:
                for crowd in w._crowds.values():
                    crowd.public_suspicion = ps_override
            # Snapshot
            for aid, a in w._agents.items():
                per_agent_shame[aid].append(
                    a.state.get("shame", {}).get("public_group", 0.0))
            for ev in w.history[-1].spawned_events:
                if ev.get("event_id") == "public_confession":
                    cc += 1
            if seed == 0:
                pcs = list(w._crowds.values())
                per_tick_ps.append(round(
                    max(c.public_suspicion for c in pcs), 3,
                ))

        confess_counts.append(cc)
        for aid, ts in per_agent_shame.items():
            if max(ts) >= 1.5:
                revs.append(count_reversals(ts))
                finals.append(ts[-1])
        if seed == 0:
            ps_trace = per_tick_ps

    return {
        "label": label,
        "rev_mean": round(mean(revs) if revs else 0, 3),
        "n_active": len(revs),
        "final_mean": round(mean(finals) if finals else 0, 3),
        "confess_per_seed": round(mean(confess_counts), 1),
        "ps_trace_seed0": ps_trace,
    }


def main() -> int:
    print("[Priority 5] Meso-scale probe -- public_suspicion coupling")
    print(f"  PYHASH={os.environ.get('PYTHONHASHSEED')} "
          f"N_SEEDS={N_SEEDS} N_TICKS={N_TICKS}")
    print()

    print("Condition A: baseline (public_suspicion active per design)...")
    a = run_condition("A_baseline", ps_override=None)
    print(f"  rev={a['rev_mean']}  final={a['final_mean']}  "
          f"active={a['n_active']}  confess/seed={a['confess_per_seed']}")
    print(f"  ps_trace[seed0] (every 20 ticks): "
          f"{a['ps_trace_seed0'][::20]}")

    print()
    print("Condition B: zero-clamp (public_suspicion = 0 every tick)...")
    b = run_condition("B_zero_clamp", ps_override=0.0)
    print(f"  rev={b['rev_mean']}  final={b['final_mean']}  "
          f"active={b['n_active']}  confess/seed={b['confess_per_seed']}")

    print()
    print("Condition C: saturated (public_suspicion = 1.0 every tick)...")
    c = run_condition("C_saturated", ps_override=1.0)
    print(f"  rev={c['rev_mean']}  final={c['final_mean']}  "
          f"active={c['n_active']}  confess/seed={c['confess_per_seed']}")

    print()
    print("=== Verdict ===")
    d_ab_rev = a["rev_mean"] - b["rev_mean"]
    d_ab_final = a["final_mean"] - b["final_mean"]
    d_ac_rev = c["rev_mean"] - a["rev_mean"]
    d_ac_final = c["final_mean"] - a["final_mean"]
    print(f"  A vs B (zero-clamp): Δrev={d_ab_rev:+.3f}  "
          f"Δfinal={d_ab_final:+.3f}")
    print(f"  C vs A (saturated):  Δrev={d_ac_rev:+.3f}  "
          f"Δfinal={d_ac_final:+.3f}")

    # Verdict: does public_suspicion produce measurable effect?
    if (abs(d_ab_rev) >= 0.3 or abs(d_ab_final) >= 0.5
            or abs(d_ac_rev) >= 0.3 or abs(d_ac_final) >= 0.5):
        verdict = (
            "CONFIRMED: public_suspicion produces measurable cycle/recovery "
            "effects. New meso-scale field is WIRED."
        )
    else:
        verdict = (
            "NULL: public_suspicion has wiring but no measurable downstream "
            "delta. May be saturated by other social_threat sources or "
            "below noise floor."
        )
    print(f"  Verdict: {verdict}")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "meso_scale_probe.json"
    )
    out_path.write_text(
        json.dumps({
            "n_seeds": N_SEEDS, "n_ticks": N_TICKS,
            "A_baseline": a,
            "B_zero_clamp": b,
            "C_saturated": c,
            "verdict": verdict,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
