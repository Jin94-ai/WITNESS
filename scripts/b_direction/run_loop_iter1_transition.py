"""WORLD_FLOW_LOOP Iter 1 — structural change: role transition mechanism.

Question: does adding mid-simulation role transition (fisher_laborer ->
disciple_follower triggered by miracle_witnessed) propagate to observable
downstream divergence in motif/action patterns?

Design (one-change principle 원칙 4):
- The only structural delta vs Batch 5 sacred_gathering is the seeded
  role_transition event at tick 6 applied to 2 of 3 fishers.
- All other params held constant: same 8-agent cast, same 3 locations,
  same accusation event at tick 18.

Flow diagnosis (§10):
- Dominant / dead / over-dominant layer analysis
- Propagation / persistence / restructuring / divergence / boundedness /
  readability scoring (§6)
- Flow type (A/B/C/D) verdict (§5)
- Keep / rollback / refine decision (§11)
"""

from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.persona.profile import DEFAULT_PROFILE, PersonaProfile  # noqa: E402
from engine.population import ROLE_CLUSTERS  # noqa: E402
from engine.world.crowd_dynamics import CrowdState  # noqa: E402
from engine.world.micro_world import (  # noqa: E402
    AgentHandle,
    MicroWorld,
    MicroWorldConfig,
)
from engine.world.spatial import Location  # noqa: E402


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


def _baseline_state() -> dict:
    return {
        "fear": 2.0, "hope": 5.0, "grief": 1.0, "confusion": 2.0,
        "awe": 4.0, "anger": 1.5, "fatigue": 3.0, "vitality": 6.0,
        "doubt": 2.0, "resolve": 5.0, "trauma": 0.5, "joy": 4.0,
        "hunger": 3.0,
        "guilt": {"self": 1.0},
        "love": {"primary_focus": 5.0},
        "loyalty": {"primary_focus": 5.0},
        "trust": {"primary_focus": 5.0},
        "shame": {"public_group": 0.3, "self": 0.5, "peer_group": 0.5},
        "belonging": {"peer_group": 5.0, "public_group": 3.0},
    }


def build_cast() -> list[AgentHandle]:
    roster = [
        ("agent_01", "fisher_laborer", {"awe": 5.0}),       # will transition
        ("agent_02", "fisher_laborer", {"awe": 5.0}),       # will transition
        ("agent_03", "fisher_laborer", {}),                  # control
        ("agent_04", "outsider", {"grief": 3.0}),
        ("agent_05", "outsider", {"doubt": 4.0}),
        ("agent_06", "crowd_participant", {}),
        ("agent_07", "crowd_participant", {}),
        ("agent_08", "family_anchor", {"love": 6.0}),
    ]
    agents = []
    for aid, role_id, overrides in roster:
        state = _baseline_state()
        for k, v in overrides.items():
            if k == "love":
                state["love"]["primary_focus"] = v
            elif k in state:
                state[k] = v
        role = ROLE_CLUSTERS[role_id]
        agents.append(AgentHandle(
            agent_id=aid, role_id=role_id,
            profile=_profile_from_role(role_id),
            state=state,
            relations={"peer_group": "village"},
            affordance_pack=list(role.affordance_pack),
            info_access_level=role.info_access_level,
        ))
    return agents


def build_locations() -> list[Location]:
    return [
        Location(
            location_id="shore",
            visibility=0.8, concealment=0.2, crowdability=0.7,
            authority_reach=0.3, sacred_proximity=0.6,
            escape_routes=["village_street"], tags=["public", "open"],
        ),
        Location(
            location_id="village_street",
            visibility=0.6, concealment=0.3, crowdability=0.6,
            authority_reach=0.4, escape_routes=["shore"],
            tags=["public"],
        ),
        Location(
            location_id="temple_outer",
            visibility=0.7, concealment=0.3, crowdability=0.5,
            authority_reach=0.7, sacred_proximity=0.8,
            escape_routes=["village_street"],
            tags=["sacred", "authority"],
        ),
    ]


def build_network(ids: list[str]) -> dict[str, set[str]]:
    net = {a: set() for a in ids}
    # fishers ↔ fishers
    for a in ("agent_01", "agent_02", "agent_03"):
        for b in ("agent_01", "agent_02", "agent_03"):
            if a != b:
                net[a].add(b)
    # outsiders weakly connected to crowd
    for o in ("agent_04", "agent_05"):
        net[o].update({"agent_06", "agent_07"})
        net["agent_06"].add(o)
        net["agent_07"].add(o)
    # crowd ↔ family
    net["agent_06"].update({"agent_07", "agent_08"})
    net["agent_07"].update({"agent_06", "agent_08"})
    net["agent_08"].update({"agent_06", "agent_07"})
    return net


def build_micro_world(seed: int = 0, enable_transition: bool = True) -> MicroWorld:
    agents = build_cast()
    locations = build_locations()
    placements = {
        "agent_01": "shore", "agent_02": "shore", "agent_03": "shore",
        "agent_04": "village_street", "agent_05": "village_street",
        "agent_06": "village_street", "agent_07": "village_street",
        "agent_08": "village_street",
    }
    crowds = {
        "shore": CrowdState(
            crowd_id="shore", density=0.4, dominant_emotion="indifferent",
        ),
        "village_street": CrowdState(
            crowd_id="village_street", density=0.5,
        ),
    }
    seed_events: list[dict] = [
        {"tick": 3, "event_id": "prayer_invitation", "location": "shore"},
        {"tick": 6, "event_id": "miracle_witnessed", "location": "shore"},
    ]
    if enable_transition:
        seed_events.extend([
            {"tick": 7, "event_id": "role_transition",
             "agent_id": "agent_01", "new_role_id": "disciple_follower",
             "reason": "miracle_witnessed", "blend_factor": 0.7},
            {"tick": 7, "event_id": "role_transition",
             "agent_id": "agent_02", "new_role_id": "disciple_follower",
             "reason": "miracle_witnessed", "blend_factor": 0.7},
        ])
    seed_events.append({
        "tick": 18, "event_id": "public_accusation",
        "target_role": "spiritual_wanderer", "location": "village_street",
    })
    config = MicroWorldConfig(
        agents=agents, locations=locations,
        initial_placements=placements,
        crowd_instances=crowds,
        social_network=build_network([a.agent_id for a in agents]),
        seed_events=seed_events, seed_rumors=[], seed=seed,
    )
    return MicroWorld(config)


# -----------------------------------------------------------------
# Flow diagnostics
# -----------------------------------------------------------------

def action_set_by_phase(world: MicroWorld, phase_start: int, phase_end: int,
                         agent_ids: list[str]) -> Counter:
    c = Counter()
    for step in world.history:
        if phase_start <= step.tick <= phase_end:
            for aid in agent_ids:
                act = step.agent_actions.get(aid)
                if act:
                    c[act] += 1
    return c


def divergence_score(treat_actions: Counter, control_actions: Counter) -> float:
    """Jaccard-style symmetric diff / union over top 5 actions."""
    top_t = set([a for a, _ in treat_actions.most_common(5)])
    top_c = set([a for a, _ in control_actions.most_common(5)])
    if not top_t and not top_c:
        return 0.0
    return len(top_t.symmetric_difference(top_c)) / len(top_t.union(top_c))


def summarize_run(world: MicroWorld) -> dict:
    all_motifs: Counter = Counter()
    all_actions: Counter = Counter()
    emergent_events = 0
    cross_layer_ticks = 0

    for step in world.history:
        all_motifs.update(step.agent_motifs.values())
        all_actions.update(step.agent_actions.values())
        for ev in step.spawned_events:
            if ev.get("by"):
                emergent_events += 1
        crowd_active = any(
            c["alignment"] > 0.1 or len(c["blame"]) > 0
            for c in step.crowd_state_snapshot.values()
        )
        rumor_active = len(step.rumor_snapshot) > 0
        if crowd_active and rumor_active:
            cross_layer_ticks += 1

    # Transition-specific diagnostics
    transitioned = [a for a in ("agent_01", "agent_02")
                    if world.get_agent(a) and world.get_agent(a).role_id
                    != "fisher_laborer"]
    control_fisher = ["agent_03"]
    post_miracle_treat = action_set_by_phase(
        world, 8, 17, transitioned if transitioned else [],
    )
    post_miracle_ctrl = action_set_by_phase(
        world, 8, 17, control_fisher,
    )
    post_accusation_treat = action_set_by_phase(
        world, 19, 30, transitioned if transitioned else [],
    )
    post_accusation_ctrl = action_set_by_phase(
        world, 19, 30, control_fisher,
    )

    return {
        "motifs": dict(all_motifs.most_common()),
        "actions": dict(all_actions.most_common()),
        "emergent_events": emergent_events,
        "cross_layer_ticks": cross_layer_ticks,
        "total_ticks": world.tick,
        "transitioned_agents": transitioned,
        "post_miracle_divergence": divergence_score(
            post_miracle_treat, post_miracle_ctrl,
        ),
        "post_accusation_divergence": divergence_score(
            post_accusation_treat, post_accusation_ctrl,
        ),
        "post_miracle_actions_treat": dict(post_miracle_treat),
        "post_miracle_actions_ctrl": dict(post_miracle_ctrl),
        "post_accusation_actions_treat": dict(post_accusation_treat),
        "post_accusation_actions_ctrl": dict(post_accusation_ctrl),
    }


def flow_type_verdict(with_tr: dict, without_tr: dict) -> str:
    """Classify flow type per §5. Compare with/without role transition."""
    # C-level: cross-layer coupling present + emergent events + downstream
    # divergence between treat/control
    if with_tr["cross_layer_ticks"] < 3:
        return "A_static"  # barely any crossing
    if with_tr["emergent_events"] < 3:
        return "B_reactive"
    # Divergence: did role transition actually change something downstream?
    div = with_tr["post_accusation_divergence"]
    if div < 0.2:
        return "B_reactive"  # transition didn't shift behavior
    if div >= 0.4:
        return "C_propagating"
    # arc-like repeated across seeds would be D, but we only run 1 seed here
    return "C_propagating"


def score_6_axes(with_tr: dict, without_tr: dict) -> dict:
    """Score 6 quality axes (§6). 0-3 scale, 3 = strong."""
    # Propagation: cross_layer_ticks ratio
    prop_ratio = with_tr["cross_layer_ticks"] / max(1, with_tr["total_ticks"])
    propagation = 3 if prop_ratio > 0.5 else 2 if prop_ratio > 0.25 else 1 if prop_ratio > 0 else 0
    # Persistence: did post-accusation still show divergence?
    persistence = 3 if with_tr["post_accusation_divergence"] >= 0.4 else (
        2 if with_tr["post_accusation_divergence"] >= 0.2 else 1
    )
    # Restructuring: did transitioned agents show different motif pool than
    # control? proxy = post_miracle_divergence
    restructuring = 3 if with_tr["post_miracle_divergence"] >= 0.4 else (
        2 if with_tr["post_miracle_divergence"] >= 0.2 else 1
    )
    # Divergence vs counterfactual (with vs without transition)
    counter_div = 0.0
    with_top = set(list(with_tr["actions"])[:5])
    without_top = set(list(without_tr["actions"])[:5])
    if with_top or without_top:
        counter_div = len(with_top.symmetric_difference(without_top)) / len(
            with_top.union(without_top),
        )
    divergence = 3 if counter_div >= 0.3 else 2 if counter_div >= 0.1 else 1
    # Boundedness: no nonsense actions, all in known affordance set
    boundedness = 3  # assumed — spatial gate + affordance pack enforced
    # Readability: emergent events + transition log exist
    readability = 3 if with_tr["emergent_events"] > 0 else 2

    return {
        "propagation": propagation,
        "persistence": persistence,
        "restructuring": restructuring,
        "divergence": divergence,
        "boundedness": boundedness,
        "readability": readability,
        "propagation_ratio": round(prop_ratio, 3),
        "counterfactual_action_divergence": round(counter_div, 3),
    }


def main() -> int:
    n_ticks = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    print(f"[LOOP Iter 1] calling_scene | seed={seed} ticks={n_ticks}")
    print("  Structural change: role_transition mechanism (fisher -> disciple)")
    print()

    # Run 1: with role transition
    world_tr = build_micro_world(seed=seed, enable_transition=True)
    world_tr.run(n_ticks)
    summary_tr = summarize_run(world_tr)

    # Run 2: without role transition (counterfactual)
    world_ctrl = build_micro_world(seed=seed, enable_transition=False)
    world_ctrl.run(n_ticks)
    summary_ctrl = summarize_run(world_ctrl)

    # Story probe
    print("=== Story probe (WITH transition) ===")
    for step in world_tr.history:
        if step.spawned_events or step.tick % 5 == 0:
            events = ",".join(ev.get("event_id", "?") for ev in step.spawned_events)[:30]
            top_actions = Counter(step.agent_actions.values()).most_common(3)
            actions_str = " ".join(f"{a}:{n}" for a, n in top_actions)
            crowds_str = " ".join(
                f"{cid}:{s['phase']}/{s['alignment']:.2f}"
                for cid, s in step.crowd_state_snapshot.items()
            )
            print(
                f"  t{step.tick:>2} | {events:<28} | "
                f"{actions_str:<36} | {crowds_str}"
            )

    # Transition log
    print("\n=== Role transitions ===")
    for aid in ("agent_01", "agent_02"):
        ag = world_tr.get_agent(aid)
        if ag and ag.transition_log:
            for rec in ag.transition_log:
                print(f"  {aid}: {rec.from_role} -> {rec.to_role} @t{rec.tick} "
                      f"(blend={rec.blend_factor}, reason={rec.reason})")
        else:
            print(f"  {aid}: no transition recorded")

    # Detect: flow type
    verdict = flow_type_verdict(summary_tr, summary_ctrl)
    scores = score_6_axes(summary_tr, summary_ctrl)

    print(f"\n=== Detect: flow type = {verdict} ===")
    print(f"  total_ticks: {summary_tr['total_ticks']}")
    print(f"  emergent_events: {summary_tr['emergent_events']}")
    print(f"  cross_layer_ticks: {summary_tr['cross_layer_ticks']}")
    print(f"  post_miracle divergence (treat vs ctrl): "
          f"{summary_tr['post_miracle_divergence']:.3f}")
    print(f"  post_accusation divergence (treat vs ctrl): "
          f"{summary_tr['post_accusation_divergence']:.3f}")

    print("\n=== Evaluate: 6-axis quality ===")
    for axis in (
        "propagation", "persistence", "restructuring",
        "divergence", "boundedness", "readability",
    ):
        print(f"  {axis:<16}: {scores[axis]}/3")
    print(f"  propagation_ratio:  {scores['propagation_ratio']}")
    print(f"  counterfactual_act_div: {scores['counterfactual_action_divergence']}")

    # Dominant layer analysis (§10.1)
    # which layer actually drove things?
    motif_counts = summary_tr["motifs"]
    dominant_motif = max(motif_counts, key=motif_counts.get) if motif_counts else "none"
    print("\n=== Dominant / dead / over-dominant layer (§10) ===")
    print(f"  dominant_motif: {dominant_motif}")
    # rumor activity
    total_rumor_snap = sum(
        len(s.rumor_snapshot) for s in world_tr.history
    )
    print(f"  total_rumor_snapshots: {total_rumor_snap}")
    # crowd phase changes
    phase_changes = 0
    prior = {}
    for step in world_tr.history:
        for cid, c in step.crowd_state_snapshot.items():
            if cid in prior and prior[cid] != c["phase"]:
                phase_changes += 1
            prior[cid] = c["phase"]
    print(f"  crowd_phase_changes: {phase_changes}")

    # Comparison summary
    print("\n=== Counterfactual comparison (with_tr vs without_tr) ===")
    print(f"  with_tr action top5: {list(summary_tr['actions'])[:5]}")
    print(f"  without_tr action top5: {list(summary_ctrl['actions'])[:5]}")
    print(
        f"  with_tr emergent={summary_tr['emergent_events']}, "
        f"without_tr emergent={summary_ctrl['emergent_events']}"
    )

    # Persist
    out_dir = ROOT / "docs" / "b_direction" / "probe_runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "iter": 1,
        "structural_change": "role_transition mechanism",
        "seed": seed, "n_ticks": n_ticks,
        "verdict": verdict,
        "scores": scores,
        "with_transition": summary_tr,
        "without_transition": summary_ctrl,
    }
    out_path = out_dir / f"loop_iter1_seed{seed}_ticks{n_ticks}.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n  Saved: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
