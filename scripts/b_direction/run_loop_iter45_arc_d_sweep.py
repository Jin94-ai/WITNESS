"""WORLD_FLOW_LOOP Iter 45 -- Arc D guilt threshold sweep.

Iter 40-41 showed Arc D (private-grief-dispersed) emerges from the
private_crisis scenario's starting conditions (high guilt, dispersed,
low alignment). This iter tests whether Arc D is robust across
different initial guilt levels:
  G=0.0  no starting guilt (pure calling-like)
  G=2.0  mild guilt
  G=4.0  baseline (Iter 40 private_crisis)
  G=6.0  high guilt
  G=8.0  saturated guilt

If Arc D emerges only at G=4+ but calling-like at G=0-2, the
topology is guilt-threshold-triggered and robust to finer changes.
"""

from __future__ import annotations

import copy
import json
import math
import sys
from collections import Counter
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.persona.profile import DEFAULT_PROFILE, PersonaProfile  # noqa: E402
from engine.population import ROLE_CLUSTERS  # noqa: E402
from engine.world.crowd_dynamics import CrowdState  # noqa: E402
from engine.world.micro_world import (  # noqa: E402
    AgentHandle, MicroWorld, MicroWorldConfig,
)
from engine.world.spatial import Location  # noqa: E402

N_SEEDS = 10  # compromise between rigor and speed (5 levels)
N_TICKS = 60
GUILT_LEVELS = [0.0, 2.0, 4.0, 6.0, 8.0]


def _profile_from_role(role_id: str) -> PersonaProfile:
    role = ROLE_CLUSTERS[role_id]
    p = copy.deepcopy(DEFAULT_PROFILE)
    p.name = role_id
    for section_name, params in role.profile_prior.items():
        section = getattr(p, section_name, None)
        if section is None:
            continue
        for k, v in params.items():
            if hasattr(section, k):
                setattr(section, k, v)
    p.motif_action_priors = copy.deepcopy(DEFAULT_PROFILE.motif_action_priors)
    return p


def _state_with_guilt(guilt_level: float) -> dict:
    return {
        "fear": 3.0, "hope": 3.0, "grief": 3.0, "confusion": 3.0,
        "awe": 1.0, "anger": 2.0, "fatigue": 5.0, "vitality": 4.0,
        "doubt": 5.0, "resolve": 3.0, "trauma": 2.0, "joy": 2.0,
        "hunger": 3.0,
        "guilt": {"self": guilt_level, "primary_focus": guilt_level * 0.75},
        "love": {"primary_focus": 3.0},
        "loyalty": {"primary_focus": 3.0},
        "trust": {"primary_focus": 3.0},
        "shame": {"public_group": 2.0, "self": 4.0, "peer_group": 3.0},
        "belonging": {"peer_group": 2.0, "public_group": 1.0},
    }


def build_world_with_guilt(seed: int, guilt_level: float) -> MicroWorld:
    roster = [
        ("agent_01", "outsider", {}),
        ("agent_02", "outsider", {}),
        ("agent_03", "disciple_follower", {}),
        ("agent_04", "family_anchor", {}),
        ("agent_05", "merchant", {}),
        ("agent_06", "crowd_participant", {}),
        ("agent_07", "fisher_laborer", {}),
        ("agent_08", "spiritual_wanderer", {}),
    ]
    agents = []
    for aid, role_id, _ in roster:
        state = _state_with_guilt(guilt_level)
        role = ROLE_CLUSTERS[role_id]
        agents.append(AgentHandle(
            agent_id=aid, role_id=role_id,
            profile=_profile_from_role(role_id),
            state=state, relations={"peer_group": "dispersed"},
            affordance_pack=list(role.affordance_pack),
            info_access_level=role.info_access_level,
        ))

    locations = [
        Location(location_id="alley_north", visibility=0.3,
                 concealment=0.6, crowdability=0.2, authority_reach=0.2,
                 escape_routes=["market_edge"], tags=["private"]),
        Location(location_id="market_edge", visibility=0.5,
                 concealment=0.3, crowdability=0.3, authority_reach=0.3,
                 escape_routes=["alley_north", "alley_south"],
                 tags=["semi_public"]),
        Location(location_id="alley_south", visibility=0.3,
                 concealment=0.6, crowdability=0.2, authority_reach=0.2,
                 escape_routes=["market_edge"], tags=["private"]),
        Location(location_id="dwelling", visibility=0.1,
                 concealment=0.9, crowdability=0.1, authority_reach=0.0,
                 escape_routes=["alley_north"], tags=["refuge"]),
    ]
    placements = {
        "agent_01": "alley_north", "agent_02": "alley_north",
        "agent_03": "market_edge", "agent_04": "market_edge",
        "agent_05": "alley_south", "agent_06": "alley_south",
        "agent_07": "dwelling", "agent_08": "dwelling",
    }
    crowds = {
        "market_edge": CrowdState(crowd_id="market_edge", density=0.15),
    }
    net: dict[str, set[str]] = {a.agent_id: set() for a in agents}
    net["agent_01"].update({"agent_02"})
    net["agent_02"].update({"agent_01", "agent_05"})
    net["agent_03"].update({"agent_08"})
    net["agent_04"].update({"agent_07"})
    net["agent_05"].update({"agent_02"})
    net["agent_06"].update({"agent_07"})
    net["agent_07"].update({"agent_04", "agent_06"})
    net["agent_08"].update({"agent_03"})

    seed_events = [
        {"tick": 10, "event_id": "guard_approaches",
         "location": "market_edge"},
    ]
    return MicroWorld(MicroWorldConfig(
        agents=agents, locations=locations, initial_placements=placements,
        crowd_instances=crowds, social_network=net,
        seed_events=seed_events, seed_rumors=[], seed=seed,
    ))


def _js(p, q):
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


def compute_fingerprint(guilt_level: float):
    motifs: Counter = Counter()
    actions: Counter = Counter()
    events: Counter = Counter()
    grieve_count = 0
    weep_count = 0
    deny_count = 0
    total_motif = 0

    for s in range(N_SEEDS):
        w = build_world_with_guilt(s, guilt_level)
        w.run(N_TICKS)
        for step in w.history:
            motifs.update(step.agent_motifs.values())
            actions.update(step.agent_actions.values())
            for ev in step.spawned_events:
                et = ev.get("event_id", "?")
                events[et] += 1
            for m in step.agent_motifs.values():
                total_motif += 1
                if m == "grieve":
                    grieve_count += 1
            for a in step.agent_actions.values():
                if a == "weep":
                    weep_count += 1
                elif a == "deny":
                    deny_count += 1

    grieve_frac = grieve_count / total_motif if total_motif else 0.0
    return {
        "guilt_level": guilt_level,
        "motifs": dict(motifs),
        "actions": dict(actions),
        "events": dict(events),
        "grieve_fraction": round(grieve_frac, 3),
        "weep_count": weep_count,
        "deny_count": deny_count,
    }


def main() -> int:
    print(f"[LOOP Iter 45] Arc D guilt threshold sweep | "
          f"guilt_levels={GUILT_LEVELS} seeds={N_SEEDS} ticks={N_TICKS}")
    print()

    from scripts.b_direction.run_loop_iter22_topology_audit import (
        compute_fingerprints,
    )
    print("  Loading reference fingerprints (calling/accusation)...")
    calling_fp = compute_fingerprints("calling")
    acc_fp = compute_fingerprints("accusation")

    results = {}
    for g in GUILT_LEVELS:
        fp = compute_fingerprint(g)
        f1_vs_calling = _js(Counter(fp["motifs"]),
                             Counter(calling_fp["F1_motifs"]))
        f1_vs_acc = _js(Counter(fp["motifs"]),
                         Counter(acc_fp["F1_motifs"]))
        f4_vs_calling = _js(Counter(fp["events"]),
                             Counter(calling_fp["F4_event_types"]))
        f4_vs_acc = _js(Counter(fp["events"]),
                         Counter(acc_fp["F4_event_types"]))

        results[g] = {
            "grieve_fraction": fp["grieve_fraction"],
            "weep_count": fp["weep_count"],
            "deny_count": fp["deny_count"],
            "F1_vs_calling": round(f1_vs_calling, 3),
            "F1_vs_accusation": round(f1_vs_acc, 3),
            "F4_vs_calling": round(f4_vs_calling, 3),
            "F4_vs_accusation": round(f4_vs_acc, 3),
            "top5_motifs": Counter(fp["motifs"]).most_common(5),
        }

        print(f"  guilt={g:3.1f}  grieve_frac={fp['grieve_fraction']:.3f}  "
              f"weep={fp['weep_count']:>4}  deny={fp['deny_count']:>4}  "
              f"F1(call)={f1_vs_calling:.3f}  "
              f"F1(acc)={f1_vs_acc:.3f}  "
              f"F4(call)={f4_vs_calling:.3f}")

    # Classify each guilt level
    print()
    print("=== Topology classification per guilt level ===")
    for g in GUILT_LEVELS:
        r = results[g]
        if r["grieve_fraction"] >= 0.10 and r["deny_count"] <= 30:
            topology = "Arc D (private-grief)"
        elif r["deny_count"] >= 100:
            topology = "Arc B (crisis-deny-dominant)"
        elif r["grieve_fraction"] < 0.05:
            topology = "Arc A (calling-like)"
        else:
            topology = "intermediate"
        print(f"  guilt={g:3.1f} -> {topology}")

    # Find threshold
    print()
    print("=== Arc D emergence threshold ===")
    emergent = []
    for g in GUILT_LEVELS:
        if results[g]["grieve_fraction"] >= 0.10:
            emergent.append(g)
    if emergent:
        threshold = min(emergent)
        print(f"  Arc D emerges at guilt >= {threshold}")
    else:
        print(f"  Arc D did not emerge at tested levels")

    out_path = (
        ROOT / "docs" / "b_direction" / "probe_runs"
        / "loop_iter45_arc_d_sweep.json"
    )
    out_path.write_text(
        json.dumps({
            "iter": 45,
            "n_seeds": N_SEEDS, "n_ticks": N_TICKS,
            "guilt_levels": GUILT_LEVELS,
            "per_level": results,
            "emergence_threshold": min(emergent) if emergent else None,
        }, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
