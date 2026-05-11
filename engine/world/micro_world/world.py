"""MicroWorld — multi-agent simulation wiring persona + crowd + rumor + spatial.

Phase 5 minimal implementation. Each agent runs a persona engine; world
layers provide shared context.

Rule #1: All IDs generic. Content provides role_bindings.
Rule #12: World layers compute state only. Agents decide actions.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from engine.persona import PersonaProfile, activate_motifs, select_action
from engine.population.transitions import (
    RoleTransitionRecord,
    apply_role_transition,
)
from engine.world.crowd_dynamics import CrowdState, compute_phase, step_crowd
from engine.world.crowd_dynamics.state import inject_crowd_event
from engine.world.information import RumorRegistry
from engine.world.spatial import Location, SpatialRegistry


@dataclass
class AgentHandle:
    """Lightweight agent representation for MicroWorld.

    Not the full PersonV3Loop — that was single-agent. MicroWorld runs
    many agents in parallel, each with its own state + profile + relations.
    """
    agent_id: str
    role_id: str
    profile: PersonaProfile
    state: dict[str, Any]                  # Active state dict (copy of ActiveState fields)
    relations: dict[str, Any]
    location_id: str | None = None
    affordance_pack: list[str] = field(default_factory=list)
    info_access_level: str = "default"
    transition_log: list[RoleTransitionRecord] = field(default_factory=list)


@dataclass
class WorldStep:
    """Single tick record of micro-world evolution."""
    tick: int
    agent_actions: dict[str, str]          # agent_id → chosen action
    agent_motifs: dict[str, str]           # agent_id → selected motif
    crowd_state_snapshot: dict[str, dict]  # crowd_id → {phase, alignment, blame}
    rumor_snapshot: list[dict]             # active rumors summary
    spawned_events: list[dict]             # emergent events this tick


@dataclass
class MicroWorldConfig:
    """Config bundle for MicroWorld construction."""
    agents: list[AgentHandle]
    locations: list[Location]
    initial_placements: dict[str, str]     # agent_id → location_id
    crowd_instances: dict[str, CrowdState] = field(default_factory=dict)
    social_network: dict[str, set[str]] = field(default_factory=dict)
    seed_events: list[dict] = field(default_factory=list)
    seed_rumors: list[dict] = field(default_factory=list)
    seed: int = 0
    # Iter 56: ablation toggle for forgiveness rumor Phase 2a loop.
    # Default True (production). Set False to disable Phase 2a counter-
    # pressure for cycle-source ablation testing.
    forgiveness_phase_enabled: bool = True
    # Iter 58: forgiveness rumor decay override. Default None = use
    # RumorRegistry default (0.08). Set to override forgiveness rumor
    # decay rate for cycle-period scaling tests (P2 prediction).
    forgiveness_rumor_decay_override: float | None = None
    # Iter 59: deny blame-inject intensity override. Default None = use
    # baseline 0.3. Set to probe whether blame rebuild time scales with
    # deny intensity (P4 prediction from Iter 58 two-term model).
    deny_blame_intensity_override: float | None = None
    # Iter 61: blend_power for selector.select_action top-2 motif blend.
    # Default 2.0 (Iter 3 quadratic). Set to 1.0 for linear blend
    # ablation test (uncertain item in Iter 52 ledger).
    blend_power: float = 2.0
    # Iter 65: forgiveness rumor intensity override for P3 test.
    # Default None = 1.5 (Iter 31 tuning). Set to probe P3 (intensity
    # -> amplitude, not period).
    forgiveness_rumor_intensity_override: float | None = None
    # Iter 67: layer-specific Phase 2a toggles. Default both True
    # (production; same as forgiveness_phase_enabled=True). Set one
    # to False to ablate only the crowd-layer OR only the agent-layer
    # recovery pressure, isolating which sub-mechanism of Phase 2a is
    # load-bearing. Only applied when forgiveness_phase_enabled=True.
    forgiveness_crowd_layer_enabled: bool = True
    forgiveness_agent_layer_enabled: bool = True
    # Iter 71: state-field ablation within agent-layer recovery.
    # Default all True (production). Each False skips the
    # corresponding decrement. Only applied when
    # forgiveness_agent_layer_enabled=True.
    forgiveness_agent_shame_enabled: bool = True
    forgiveness_agent_guilt_enabled: bool = True
    forgiveness_agent_fear_enabled: bool = True
    # Iter 72: magnitude overrides for per-field decrements.
    # Default None = production values (shame 0.4, guilt 0.3,
    # fear 0.2). Used to test whether Iter 71's "shame dominance"
    # is structural or parameter-tuned (equalize to probe).
    forgiveness_agent_shame_multiplier: float | None = None
    forgiveness_agent_guilt_multiplier: float | None = None
    forgiveness_agent_fear_multiplier: float | None = None
    # Iter 92-93: AUXILIARY RECOVERY CHANNEL (Branch B core).
    # Awe-driven calm: when agent.state.awe > threshold, slow shame
    # decay independent of Phase 2a forgiveness rumor. Activates Iter 78
    # decoupled awe field. First non-Phase-2a recovery channel.
    # Iter 93 sweep [0.05, 0.1, 0.2, 0.3, 0.5]:
    #   - 0.05: too weak (Iter 92 found below effect floor)
    #   - 0.1: peak cycling rate (rev_inj 3.2 → 5.7), moderate final
    #   - 0.2: balanced cycling + deep recovery (final_inj 0.44)
    #   - 0.3: low cycling, deepest recovery (final_inj 0.23)
    #   - 0.5: aux dominates Phase 2a — too strong
    # Production default 0.2 — balanced narrative regime where
    # awe-elevated agents reach deep recovery while still cycling.
    # See ITER_93_AUX_SWEEP.md.
    awe_recovery_enabled: bool = True
    awe_recovery_threshold: float = 5.0       # awe must exceed this
    awe_recovery_shame_decay: float = 0.2     # shame -= this per tick when active
    # Iter 94: Awe decay rule. Awe is not permanent — it fades back
    # to baseline (3.0) over time. Without this, injected awe stays
    # at 8 forever (artificial). Default 0.05/tick → injected awe=8
    # decays past threshold 5.0 in ~60 ticks (HL ~14 ticks toward
    # baseline 3). Disable for simulations needing perpetual awe.
    awe_decay_enabled: bool = True
    awe_baseline: float = 3.0
    awe_decay_rate: float = 0.05
    # Iter 103: Aux CROWD-LAYER (symmetric to Phase 2a crowd-layer).
    # Iter 102 found agent-only aux can't sustain at 500t -- blame_
    # concentration keeps re-supplying shame. This adds crowd-side
    # aux: when crowd dominant_emotion == "awe" AND alignment > threshold,
    # reduce blame_concentration[role] and shame_climate. Default ON.
    awe_crowd_layer_enabled: bool = True
    awe_crowd_alignment_threshold: float = 0.2
    awe_crowd_blame_decay: float = 0.1         # per-target blame reduction
    awe_crowd_shame_climate_decay: float = 0.05  # crowd shame_climate reduction


# =============================================================================
# MicroWorld
# =============================================================================

class MicroWorld:
    """Multi-agent micro-world runner.

    Tick loop:
        1. Decay all layers (crowd step, rumor step).
        2. For each agent: compute motif + action (via persona engine).
        3. Apply action → world layer updates (crowd / rumor inject).
        4. Record WorldStep.
    """

    def __init__(self, config: MicroWorldConfig) -> None:
        self._rng = random.Random(config.seed)
        self._config = config

        # Build spatial registry + place agents
        self._spatial = SpatialRegistry(config.locations)
        self._agents: dict[str, AgentHandle] = {
            a.agent_id: a for a in config.agents
        }
        for agent_id, location_id in config.initial_placements.items():
            self._spatial.place(agent_id, location_id)
            if agent_id in self._agents:
                self._agents[agent_id].location_id = location_id

        # Build rumor registry with provided network
        self._rumors = RumorRegistry(network=config.social_network)
        for seed_rumor in config.seed_rumors:
            self._rumors.spawn(
                content_tag=seed_rumor["content_tag"],
                target_role=seed_rumor.get("target_role"),
                origin_source=seed_rumor.get("origin_source", "_seed"),
                origin_tick=0,
                initial_reach=set(seed_rumor.get("initial_reach", [])),
                intensity=seed_rumor.get("intensity", 0.8),
                credibility=seed_rumor.get("credibility", 0.5),
            )

        # Crowd instances (can be multiple, keyed by location or id)
        self._crowds: dict[str, CrowdState] = dict(config.crowd_instances)

        # Seed events queue: {tick: [events]}
        self._seed_event_schedule: dict[int, list[dict]] = {}
        for ev in config.seed_events:
            self._seed_event_schedule.setdefault(ev["tick"], []).append(ev)

        # History
        self.history: list[WorldStep] = []
        self._tick: int = 0

    # -----------------------------------------------------------------
    # Main tick
    # -----------------------------------------------------------------

    def step(self) -> WorldStep:
        self._tick += 1
        tick = self._tick
        spawned_events: list[dict] = []

        # Phase 1: Fire seed events for this tick (crowd + direct agent state impact)
        for ev in self._seed_event_schedule.get(tick, []):
            self._apply_seed_event(ev)
            spawned_events.append(ev)

        # Phase 2: Layer decay
        for crowd_state in self._crowds.values():
            step_crowd(crowd_state)
        self._rumors.step(tick=tick, rng=self._rng)

        # Phase 2a (Iter 30): Active forgiveness rumors apply strong
        # counter-pressure on crowd state AND per-agent shame/guilt.
        # Per-tick decrements must exceed crisis loop's accumulation
        # rate (~0.3-0.5/tick per blamed role) to escape crisis basin.
        # Iter 56: config.forgiveness_phase_enabled gates this block
        # (ablation test for cycle-source identification).
        if self._config.forgiveness_phase_enabled:
            for rumor in self._rumors.get_active():
                if (rumor.content_tag == "forgiveness"
                        and rumor.target_role):
                    # Crowd-layer: blame, alignment, shame_climate
                    # Iter 67: gated by forgiveness_crowd_layer_enabled.
                    if self._config.forgiveness_crowd_layer_enabled:
                        for crowd in self._crowds.values():
                            if rumor.target_role in crowd.blame_concentration:
                                reduction = rumor.intensity * 0.5
                                crowd.blame_concentration[rumor.target_role] = max(
                                    0.0,
                                    crowd.blame_concentration[rumor.target_role]
                                    - reduction,
                                )
                                if (crowd.blame_concentration[rumor.target_role]
                                        < 0.01):
                                    del crowd.blame_concentration[rumor.target_role]
                            crowd.alignment_strength = max(
                                0.0,
                                crowd.alignment_strength - rumor.intensity * 0.15,
                            )
                            crowd.shame_climate = max(
                                0.0,
                                crowd.shame_climate - rumor.intensity * 0.1,
                            )
                            # Iter 90: forgiveness also lowers public_suspicion.
                            crowd.public_suspicion = max(
                                0.0,
                                crowd.public_suspicion - rumor.intensity * 0.03,
                            )
                    # Agent-layer: active recovery pressure on target_role
                    # Iter 67: gated by forgiveness_agent_layer_enabled.
                    # Iter 71: per-field toggles for shame/guilt/fear.
                    if self._config.forgiveness_agent_layer_enabled:
                        for aid, agent in self._agents.items():
                            if agent.role_id != rumor.target_role:
                                continue
                            # Iter 72: magnitude overrides default
                            # to Iter 31 production values.
                            sham_mul = (
                                self._config.forgiveness_agent_shame_multiplier
                                if self._config.forgiveness_agent_shame_multiplier is not None
                                else 0.4
                            )
                            guilt_mul = (
                                self._config.forgiveness_agent_guilt_multiplier
                                if self._config.forgiveness_agent_guilt_multiplier is not None
                                else 0.3
                            )
                            fear_mul = (
                                self._config.forgiveness_agent_fear_multiplier
                                if self._config.forgiveness_agent_fear_multiplier is not None
                                else 0.2
                            )
                            if self._config.forgiveness_agent_shame_enabled:
                                shame = agent.state.setdefault("shame", {})
                                for k in ("self", "public_group"):
                                    shame[k] = max(
                                        0.0,
                                        shame.get(k, 0.0) - rumor.intensity * sham_mul,
                                    )
                            if self._config.forgiveness_agent_guilt_enabled:
                                guilt = agent.state.setdefault("guilt", {})
                                guilt["primary_focus"] = max(
                                    0.0,
                                    guilt.get("primary_focus", 0.0)
                                    - rumor.intensity * guilt_mul,
                                )
                            if self._config.forgiveness_agent_fear_enabled:
                                agent.state["fear"] = max(
                                    0.0,
                                    agent.state.get("fear", 0.0)
                                    - rumor.intensity * fear_mul,
                                )

        # Phase 2a' (Iter 92): AUXILIARY RECOVERY — awe-driven calm.
        # Independent of Phase 2a forgiveness loop. Couples Iter 78
        # decoupled awe field to cycle mechanism. Branch B core feature
        # to break single-loop collapse (Scale-4 Recovery Diversity).

        # Iter 94: awe decay — independent of aux recovery so that
        # awe field stays realistic regardless of aux toggle.
        if self._config.awe_decay_enabled:
            awe_baseline = self._config.awe_baseline
            awe_dec = self._config.awe_decay_rate
            for agent in self._agents.values():
                cur_awe = agent.state.get("awe", awe_baseline)
                if cur_awe > awe_baseline:
                    agent.state["awe"] = max(
                        awe_baseline, cur_awe - awe_dec,
                    )

        # Iter 92: aux recovery -- agent-layer (uses post-decay awe value).
        if self._config.awe_recovery_enabled:
            threshold = self._config.awe_recovery_threshold
            decay = self._config.awe_recovery_shame_decay
            for agent in self._agents.values():
                if agent.state.get("awe", 0.0) > threshold:
                    shame = agent.state.setdefault("shame", {})
                    for k in ("self", "public_group"):
                        shame[k] = max(0.0, shame.get(k, 0.0) - decay)

        # Iter 103: aux CROWD-LAYER. Symmetric to Phase 2a crowd-layer.
        # Reduces blame_concentration + shame_climate when crowd is
        # awe-dominant. Addresses Iter 102 finding (sustained recovery
        # needs blame reduction, not just shame reduction).
        if self._config.awe_crowd_layer_enabled:
            align_thresh = self._config.awe_crowd_alignment_threshold
            blame_decay_aux = self._config.awe_crowd_blame_decay
            shame_climate_decay_aux = self._config.awe_crowd_shame_climate_decay
            for crowd in self._crowds.values():
                if (crowd.dominant_emotion == "awe"
                        and crowd.alignment_strength > align_thresh):
                    for target in list(crowd.blame_concentration.keys()):
                        crowd.blame_concentration[target] = max(
                            0.0,
                            crowd.blame_concentration[target] - blame_decay_aux,
                        )
                        if crowd.blame_concentration[target] < 0.01:
                            del crowd.blame_concentration[target]
                    crowd.shame_climate = max(
                        0.0,
                        crowd.shame_climate - shame_climate_decay_aux,
                    )

        # Phase 2b: **State feedback** — world pressure → agent.state
        # (Previous gap: MicroWorld had no pressure→state loop.)
        for agent in self._agents.values():
            self._update_agent_state_from_world(agent)

        # Phase 3: Agent decisions
        agent_actions: dict[str, str] = {}
        agent_motifs: dict[str, str] = {}

        for agent_id, agent in self._agents.items():
            action, motif_name = self._agent_decide(agent, tick)
            agent_actions[agent_id] = action
            agent_motifs[agent_id] = motif_name

        # Phase 4: Apply actions → world layer updates AND action consequences on self-state
        for agent_id, action in agent_actions.items():
            self._apply_agent_action(agent_id, action, tick, spawned_events)
            self._apply_action_consequences_to_self(
                self._agents[agent_id], action,
            )

        # Phase 5: Record snapshot
        step = WorldStep(
            tick=tick,
            agent_actions=dict(agent_actions),
            agent_motifs=dict(agent_motifs),
            crowd_state_snapshot={
                cid: {
                    "phase": compute_phase(cs),
                    "alignment": round(cs.alignment_strength, 3),
                    "density": round(cs.density, 3),
                    "blame": dict(cs.blame_concentration),
                    "accusation_amp": round(cs.accusation_amplification, 3),
                    "shame_climate": round(cs.shame_climate, 3),
                    "authority_vigilance": round(cs.authority_vigilance, 3),
                }
                for cid, cs in self._crowds.items()
            },
            rumor_snapshot=[
                {
                    "id": r.rumor_id,
                    "tag": r.content_tag,
                    "target": r.target_role,
                    "intensity": round(r.intensity, 3),
                    "reach_size": len(r.reach),
                    "distortion": round(r.distortion, 3),
                }
                for r in self._rumors.get_active()
            ],
            spawned_events=list(spawned_events),
        )
        self.history.append(step)
        return step

    def run(self, n_ticks: int) -> list[WorldStep]:
        for _ in range(n_ticks):
            self.step()
        return self.history

    # -----------------------------------------------------------------
    # Agent decide (simplified persona engine call)
    # -----------------------------------------------------------------

    def _agent_decide(
        self, agent: AgentHandle, tick: int,
    ) -> tuple[str, str]:
        """Compute motif + pick action for one agent.

        Uses persona engine (activate_motifs + select_action). Pressures are
        derived from world state (crowd, rumor, spatial).
        """
        # Build pressures from world state
        pressures = self._compute_agent_pressures(agent)

        # Events recent: dict of events recently fired at agent's location
        events_recent = self._compute_recent_events(agent, tick)

        # Activate motifs
        motif_result = activate_motifs(
            state=agent.state,
            pressures=pressures,
            events_recent=events_recent,
            profile=agent.profile,
        )

        # Availability filter via spatial affordances.
        # NOTE: psychological actions (deny/weep/confess/withdraw/flee/pray)
        # are cross-role — role.affordance_pack gates only special primitives
        # (arrest, draw_sword). Spatial gate is primary.
        CROSS_ROLE_ACTIONS = {
            "deny", "weep", "confess", "withdraw_in_fear", "flee",
            "follow_closely", "follow_at_distance", "stay_hiding",
            "stay_awake", "fall_asleep", "pray", "discuss_with_disciples",
            "assert_loyalty", "watch_quietly",
        }

        def _available(action: str) -> bool:
            ok, _ = self._spatial.is_action_affordable(agent.agent_id, action)
            if not ok:
                return False
            # Cross-role = always psychologically available (if spatial OK)
            if action in CROSS_ROLE_ACTIONS:
                return True
            # Role-specific action must be in pack
            if agent.affordance_pack and action not in agent.affordance_pack:
                return False
            return True

        selection = select_action(
            motif_result=motif_result,
            profile=agent.profile,
            availability_filter=_available,
            rng=self._rng,
            default_action="follow_closely",
            blend_power=self._config.blend_power,
        )

        return selection.action, selection.selected_motif

    def _compute_agent_pressures(self, agent: AgentHandle) -> dict[str, float]:
        """Derive pressure dict for agent from world state AND internal state.

        Motif activator reads these as proxies. Agent's accumulated
        shame/fear also contribute as baseline pressure (not only acute
        world-state peaks).
        """
        # ---- Internal-state baseline (new — Phase 3 iteration 2) ----
        # Agent's own shame_public contributes to shame_exposure pressure
        agent_shame_public = agent.state.get("shame", {}).get("public_group", 0.0)
        agent_guilt_self = agent.state.get("guilt", {}).get("self", 0.0)

        pressures = {
            "social_threat": 0.0,
            "physical_threat": 0.0,
            "shame_exposure": agent_shame_public,          # state-backed baseline
            "loyalty_pull": 0.0,
            "uncertainty": agent_guilt_self * 0.3,          # self-doubt
            "urgency": 0.0,
            "isolation_pressure": 0.0,
            "sacred_salience": 0.0,
        }

        # Crowd at agent's location (if any)
        location_id = agent.location_id
        if location_id:
            location = self._spatial.get(location_id)
            # Locate crowd associated with location (if any)
            for cid, crowd in self._crowds.items():
                if cid == location_id or cid.startswith(location_id):
                    # social_threat = alignment × accusation_amplification × 10
                    pressures["social_threat"] = max(
                        pressures["social_threat"],
                        crowd.alignment_strength
                        * (0.5 + crowd.accusation_amplification)
                        * 10,
                    )
                    # shame_exposure = blame on agent's role × 10
                    blame_on_role = crowd.blame_concentration.get(
                        agent.role_id, 0.0,
                    )
                    pressures["shame_exposure"] = max(
                        pressures["shame_exposure"], blame_on_role * 10,
                    )

            # Authority reach → physical_threat + social_threat
            pressures["physical_threat"] = location.authority_reach * 5
            pressures["social_threat"] = max(
                pressures["social_threat"], location.authority_reach * 3,
            )

            # World memory: shame_climate + authority_vigilance (Iter 4).
            # Iter 5: role-conditional coefficient via role.climate_sensitivity.
            # Iter 37: climate_sensitivity retained (sacred D-flow needs it).
            # Iter 38: ablate authority_vigilance coupling to test LOW-EFFECT
            # classification (revert if regression).
            from engine.population.role_cluster import ROLE_CLUSTERS
            role = ROLE_CLUSTERS.get(agent.role_id)
            role_cs = role.climate_sensitivity if role else 1.0
            for cid, crowd in self._crowds.items():
                if cid == location_id or cid.startswith(location_id):
                    pressures["shame_exposure"] = min(
                        10.0,
                        pressures["shame_exposure"]
                        + crowd.shame_climate * 3 * role_cs,
                    )
                    # Iter 38: authority_vigilance coupling removed.
                    # Iter 90: public_suspicion → social_threat coupling.
                    # Distinct from blame_concentration (target-specific);
                    # this is general crowd suspicion. WORLD_MESO_SCALE.md §1.5.
                    pressures["social_threat"] = min(
                        10.0,
                        pressures["social_threat"]
                        + crowd.public_suspicion * 2,
                    )

            # Sacred proximity → sacred_salience
            pressures["sacred_salience"] = location.sacred_proximity * 8

            # Visibility + low concealment → shame_exposure boost
            if location.visibility > 0.6 and location.concealment < 0.3:
                pressures["shame_exposure"] = min(
                    10, pressures["shame_exposure"] + location.visibility * 3,
                )

        # Rumor targeting agent → uncertainty + shame_exposure
        rumors_about_self = self._rumors.get_about(agent.agent_id)
        rumors_about_role = self._rumors.get_about(agent.role_id)
        all_relevant = list(rumors_about_self) + list(rumors_about_role)
        if all_relevant:
            max_intensity = max(r.intensity for r in all_relevant)
            pressures["uncertainty"] = max(
                pressures["uncertainty"], max_intensity * 6,
            )
            pressures["shame_exposure"] = min(
                10, pressures["shame_exposure"] + max_intensity * 2,
            )

        # No allies present (loneliness) → isolation_pressure
        if location_id:
            agents_here = self._spatial.agents_at(location_id)
            if len(agents_here) <= 1:
                pressures["isolation_pressure"] = 7.0

        return pressures

    # -----------------------------------------------------------------
    # State feedback (Phase 2b additions)
    # -----------------------------------------------------------------

    def _update_agent_state_from_world(self, agent: AgentHandle) -> None:
        """Apply world pressure → agent state (emotional response).

        Without this, agents never accumulate fear/shame/guilt from events
        and never reach motif activation thresholds.
        """
        state = agent.state
        pressures = self._compute_agent_pressures(agent)

        # Get crowd at agent's location (if any)
        location_id = agent.location_id
        local_crowd = self._crowds.get(location_id) if location_id else None

        # === Passive decay (small, keeps state from saturating) ===
        for field_name, rate in (
            ("fear", 0.08),
            ("confusion", 0.06),
            ("anger", 0.08),
        ):
            cur = state.get(field_name, 0.0)
            if cur > 0:
                state[field_name] = max(0.0, cur - rate)

        # === Pressure → state ===

        # shame_exposure → shame[public_group] + self + fear
        if pressures["shame_exposure"] > 3.0:
            scale = pressures["shame_exposure"] / 10
            state.setdefault("shame", {})
            state["shame"]["public_group"] = min(
                10.0,
                state["shame"].get("public_group", 0.0) + 0.4 * scale,
            )
            state["shame"]["self"] = min(
                10.0, state["shame"].get("self", 0.0) + 0.2 * scale,
            )
            state["fear"] = min(10.0, state.get("fear", 0.0) + 0.3 * scale)

        # social_threat → fear + confusion
        if pressures["social_threat"] > 3.0:
            scale = pressures["social_threat"] / 10
            state["fear"] = min(10.0, state.get("fear", 0.0) + 0.4 * scale)
            state["confusion"] = min(
                10.0, state.get("confusion", 0.0) + 0.2 * scale,
            )

        # physical_threat → fear + anger
        if pressures["physical_threat"] > 3.0:
            scale = pressures["physical_threat"] / 10
            state["fear"] = min(10.0, state.get("fear", 0.0) + 0.5 * scale)
            state["anger"] = min(10.0, state.get("anger", 0.0) + 0.2 * scale)

        # Rumor targeting agent → doubt + guilt[self]
        rumors_about_self = (
            self._rumors.get_about(agent.agent_id)
            + self._rumors.get_about(agent.role_id)
        )
        if rumors_about_self:
            max_intensity = max(r.intensity for r in rumors_about_self)
            state["doubt"] = min(
                10.0, state.get("doubt", 0.0) + 0.3 * max_intensity,
            )
            # Accusatory rumor → guilt[self] rise
            if any(r.content_tag in ("accusation", "misdeed")
                   for r in rumors_about_self):
                state.setdefault("guilt", {})
                state["guilt"]["self"] = min(
                    10.0,
                    state["guilt"].get("self", 0.0) + 0.3 * max_intensity,
                )

        # Lynch-mode crowd → fear surge for target role
        if local_crowd and compute_phase(local_crowd) == "lynch_mode":
            if agent.role_id in local_crowd.blame_concentration:
                state["fear"] = min(10.0, state.get("fear", 0.0) + 1.0)

        # isolation_pressure → confusion + fear (chronic)
        if pressures["isolation_pressure"] > 5.0:
            state["confusion"] = min(
                10.0, state.get("confusion", 0.0) + 0.2,
            )

    def _apply_action_consequences_to_self(
        self, agent: AgentHandle, action: str,
    ) -> None:
        """Action → agent self-state impact (parallel to PersonV3Loop logic)."""
        state = agent.state
        if action == "deny":
            state.setdefault("guilt", {})["primary_focus"] = min(
                10.0, state["guilt"].get("primary_focus", 0.0) + 1.0,
            )
            state.setdefault("shame", {})["self"] = min(
                10.0, state["shame"].get("self", 0.0) + 0.6,
            )
        elif action == "confess":
            state["resolve"] = min(10.0, state.get("resolve", 0.0) + 0.5)
            gp = state.get("guilt", {}).get("primary_focus", 0.0)
            state.setdefault("guilt", {})["primary_focus"] = max(0.0, gp - 0.5)
        elif action == "weep":
            state["grief"] = min(10.0, state.get("grief", 0.0) + 0.4)
            if "self" in state.get("shame", {}):
                state["shame"]["self"] = max(0.0, state["shame"]["self"] - 0.15)
        elif action == "flee":
            state["fear"] = min(10.0, state.get("fear", 0.0) + 0.5)
        elif action == "assert_loyalty":
            state["resolve"] = min(10.0, state.get("resolve", 0.0) + 0.2)
        elif action == "withdraw_in_fear":
            state["grief"] = min(10.0, state.get("grief", 0.0) + 0.1)

    def _compute_recent_events(
        self, agent: AgentHandle, tick: int,
    ) -> dict[str, int]:
        """Build event_recent flags for motif activation.

        Simple heuristic: look back 3 ticks in history for events that
        affected agent (via spawned_events).
        """
        recent: dict[str, int] = {}
        lookback = max(0, len(self.history) - 3)
        for step in self.history[lookback:]:
            for ev in step.spawned_events:
                # Include all spawned events as "recent" (coarse)
                event_id = ev.get("event_id")
                if event_id:
                    recent[event_id] = 1
        return recent

    # -----------------------------------------------------------------
    # Action → world feedback
    # -----------------------------------------------------------------

    def _apply_agent_action(
        self, agent_id: str, action: str, tick: int, spawned: list[dict],
    ) -> None:
        """Apply action effects on world layers (crowd / rumor)."""
        agent = self._agents[agent_id]
        location_id = agent.location_id

        # Actions that affect crowd
        if location_id and location_id in self._crowds:
            crowd = self._crowds[location_id]
            if action == "assert_loyalty":
                inject_crowd_event(crowd, "assert_loyalty_public", intensity=0.4)
            elif action == "deny":
                # Iter 42: gate removed. Iter 41 showed Arc D emerges
                # independently of the gate (agents never denied in
                # private_crisis scenario regardless). Gate was never
                # exercised; reverting to direct public_denial cascade.
                # Iter 59: deny_blame_intensity_override for P4 test.
                deny_intensity = (
                    self._config.deny_blame_intensity_override
                    if self._config.deny_blame_intensity_override is not None
                    else 0.3
                )
                inject_crowd_event(
                    crowd, "public_accusation",
                    target=agent.role_id, intensity=deny_intensity,
                )
                self._rumors.spawn(
                    content_tag="public_denial",
                    target_role=agent.agent_id,
                    origin_source=agent_id,
                    origin_tick=tick,
                    intensity=0.5,
                    credibility=0.6,
                )
                spawned.append({
                    "tick": tick, "event_id": "public_denial",
                    "by": agent_id,
                })
            elif action == "flee":
                # Individual flee is minor — only collective flees really
                # scatter density. Use low intensity.
                inject_crowd_event(crowd, "panic_scatter", intensity=0.1)
            elif action == "confess":
                # Public confession spawns rumor + forgiveness signal.
                # Iter 31: confess is the agent-level recovery generator.
                self._rumors.spawn(
                    content_tag="confession",
                    target_role=agent.agent_id,
                    origin_source=agent_id,
                    origin_tick=tick,
                    intensity=0.6,
                    credibility=0.7,
                )
                # Spawn forgiveness rumor targeting confessor's ROLE.
                # Iter 31 tune: intensity 1.5 (confess is a dramatic
                # narrative act; its recovery effect should be dramatic).
                # Iter 65: intensity override for P3 amplitude test.
                fg_intensity = (
                    self._config.forgiveness_rumor_intensity_override
                    if self._config.forgiveness_rumor_intensity_override
                    is not None
                    else 1.5
                )
                forgiveness_rumor = self._rumors.spawn(
                    content_tag="forgiveness",
                    target_role=agent.role_id,
                    origin_source=agent_id,
                    origin_tick=tick,
                    intensity=fg_intensity,
                    credibility=0.6,
                )
                # Iter 58: optional decay override for P2 cycle-period
                # scaling test.
                if self._config.forgiveness_rumor_decay_override is not None:
                    forgiveness_rumor.decay_rate = (
                        self._config.forgiveness_rumor_decay_override
                    )
                spawned.append({
                    "tick": tick, "event_id": "public_confession",
                    "by": agent_id,
                })
                spawned.append({
                    "tick": tick, "event_id": "forgiveness_emitted",
                    "by": agent_id, "target_role": agent.role_id,
                })
            elif action == "weep":
                spawned.append({
                    "tick": tick, "event_id": "visible_grief",
                    "by": agent_id,
                })
                # Weeping in public may fragment crowd (sympathy)
                inject_crowd_event(crowd, "defiant_voice", intensity=0.3)
            elif action == "withdraw_in_fear":
                # Visible withdrawal from a crowd location seeds a weak
                # "suspicious absence" rumor — dead-layer amplification
                # (Iter 3 change: make common actions emit world signal).
                location = self._spatial.get(location_id)
                if location.visibility > 0.5:
                    self._rumors.spawn(
                        content_tag="visible_withdrawal",
                        target_role=agent_id,
                        origin_source=agent_id,
                        origin_tick=tick,
                        intensity=0.25, credibility=0.4,
                    )
                    spawned.append({
                        "tick": tick, "event_id": "visible_withdrawal",
                        "by": agent_id,
                    })
            elif action == "discuss_with_disciples":
                # Discussion spreads low-intensity "talk" rumor — no
                # target role, just flavor. Tracks information diffusion.
                self._rumors.spawn(
                    content_tag="discussion",
                    target_role=None,
                    origin_source=agent_id,
                    origin_tick=tick,
                    intensity=0.2, credibility=0.35,
                )
                spawned.append({
                    "tick": tick, "event_id": "discussion_emitted",
                    "by": agent_id,
                })
            elif action == "pray":
                # Public prayer in high-sacred location emits a devotion
                # signal that boosts crowd awe.
                location = self._spatial.get(location_id)
                if location.sacred_proximity > 0.4:
                    inject_crowd_event(
                        crowd, "assert_loyalty_public", intensity=0.2,
                    )
                    spawned.append({
                        "tick": tick, "event_id": "public_devotion",
                        "by": agent_id,
                    })
            elif action == "assert_loyalty":
                # Loyalty assertion already triggers crowd event above,
                # but in high-visibility location also spawns rumor.
                location = self._spatial.get(location_id)
                if location.visibility > 0.6:
                    self._rumors.spawn(
                        content_tag="loyalty_declaration",
                        target_role=agent.agent_id,
                        origin_source=agent_id,
                        origin_tick=tick,
                        intensity=0.35, credibility=0.55,
                    )
                    spawned.append({
                        "tick": tick, "event_id": "public_loyalty",
                        "by": agent_id,
                    })

    def _apply_seed_event(self, ev: dict) -> None:
        """Apply a seeded canonical event. Strengthened (Phase 3 iteration 2):
        - dominant_emotion set
        - density boost
        - alignment_strength boost
        - direct state effect for agents of target_role at location
        """
        from engine.world.crowd_dynamics.state import set_dominant_emotion

        event_id = ev.get("event_id")
        location_id = ev.get("location")

        if event_id == "public_accusation" and location_id in self._crowds:
            target = ev.get("target_role", "outsider")
            crowd = self._crowds[location_id]
            inject_crowd_event(
                crowd, "public_accusation",
                target=target, intensity=1.0,  # stronger
            )
            # Crowd emotion becomes anger (drives toward lynch)
            set_dominant_emotion(crowd, "anger", strength_boost=0.3)
            # Density jumps — accusation event pulls crowd
            crowd.density = min(1.0, crowd.density + 0.25)

            # Also direct state impact on target_role agents at location
            for agent_id in self._spatial.agents_at(location_id):
                agent = self._agents.get(agent_id)
                if agent and agent.role_id == target:
                    agent.state.setdefault("shame", {})
                    agent.state["shame"]["public_group"] = min(
                        10.0,
                        agent.state["shame"].get("public_group", 0.0) + 2.0,
                    )
                    agent.state["fear"] = min(
                        10.0, agent.state.get("fear", 0.0) + 2.0,
                    )

            # Also spawn rumor
            self._rumors.spawn(
                content_tag="accusation",
                target_role=target,
                origin_source="_seed",
                origin_tick=self._tick,
                intensity=0.7, credibility=0.5,
            )
        elif event_id == "guard_approaches":
            # Iter 91 fix: previous version silently no-op'd when
            # location had no CrowdState (e.g., upper_room in
            # accusation scenario). Now applies per-agent fear bump
            # at any location, plus crowd-side authority_suppression
            # only where a crowd exists.
            if location_id in self._crowds:
                inject_crowd_event(
                    self._crowds[location_id], "authority_suppression",
                )
            # Per-agent fear regardless of crowd presence.
            for aid in self._spatial.agents_at(location_id):
                agent = self._agents.get(aid)
                if agent is None:
                    continue
                agent.state["fear"] = min(
                    10.0, agent.state.get("fear", 0.0) + 1.0,
                )
        elif event_id == "prayer_invitation":
            # Iter 95: WIRE prayer_invitation event (was DORMANT per
            # Iter 77). Boosts awe for agents at the location, with
            # crowd-side awe-emotion shift. Sustains aux recovery
            # window in sacred scenarios. See ITER_95_SACRED_WIRING.md.
            for aid in self._spatial.agents_at(location_id):
                agent = self._agents.get(aid)
                if agent is None:
                    continue
                cur = agent.state.get("awe", 3.0)
                agent.state["awe"] = min(10.0, cur + 2.0)
            if location_id in self._crowds:
                from engine.world.crowd_dynamics.state import set_dominant_emotion
                set_dominant_emotion(
                    self._crowds[location_id], "awe", strength_boost=0.15,
                )
        elif event_id == "miracle_witnessed":
            # Iter 95: WIRE miracle_witnessed event. Stronger awe boost
            # than prayer_invitation. See ITER_95_SACRED_WIRING.md.
            for aid in self._spatial.agents_at(location_id):
                agent = self._agents.get(aid)
                if agent is None:
                    continue
                cur = agent.state.get("awe", 3.0)
                agent.state["awe"] = min(10.0, cur + 4.0)
            if location_id in self._crowds:
                from engine.world.crowd_dynamics.state import set_dominant_emotion
                set_dominant_emotion(
                    self._crowds[location_id], "awe", strength_boost=0.3,
                )
        elif event_id == "role_transition":
            agent_id = ev.get("agent_id")
            new_role = ev.get("new_role_id")
            if agent_id and new_role and agent_id in self._agents:
                self.transition_role(
                    agent_id,
                    new_role,
                    reason=ev.get("reason", "seeded"),
                    blend_factor=float(ev.get("blend_factor", 0.6)),
                    merge_affordances=bool(ev.get("merge_affordances", True)),
                )
        elif event_id == "shame_repair":
            # Iter 28 -- recovery mechanism. Reduces shame/guilt for
            # agents of target_role at location (or all agents at
            # location if target_role omitted). Also reduces
            # shame_climate on local crowd.
            target = ev.get("target_role")  # None = all agents
            intensity = float(ev.get("intensity", 0.5))
            if location_id in self._crowds:
                crowd = self._crowds[location_id]
                # Reduce shame_climate (slow-decaying field) directly
                crowd.shame_climate = max(
                    0.0, crowd.shame_climate - intensity * 0.5,
                )
                # Slight alignment decrease (crowd disperses from
                # accusation focus)
                crowd.alignment_strength = max(
                    0.0, crowd.alignment_strength - intensity * 0.2,
                )
                # Iter 90: shame_repair lowers general public_suspicion.
                crowd.public_suspicion = max(
                    0.0, crowd.public_suspicion - intensity * 0.1,
                )

            for aid in self._spatial.agents_at(location_id):
                agent = self._agents.get(aid)
                if agent is None:
                    continue
                if target and agent.role_id != target:
                    continue
                # Reduce agent's shame[self, public_group] and
                # guilt[primary_focus]. Preserves other relation state.
                shame = agent.state.setdefault("shame", {})
                for k in ("self", "public_group"):
                    shame[k] = max(
                        0.0, shame.get(k, 0.0) - intensity * 3.0,
                    )
                guilt = agent.state.setdefault("guilt", {})
                guilt["primary_focus"] = max(
                    0.0,
                    guilt.get("primary_focus", 0.0) - intensity * 2.5,
                )
                # Partial fear relief
                agent.state["fear"] = max(
                    0.0, agent.state.get("fear", 0.0) - intensity * 1.5,
                )
                # Hope + resolve small rise
                agent.state["hope"] = min(
                    10.0, agent.state.get("hope", 0.0) + intensity * 0.8,
                )

            # Iter 30 -- spawn forgiveness rumor so the repair effect
            # persists via per-tick counter-pressure on blame.
            if target:
                self._rumors.spawn(
                    content_tag="forgiveness",
                    target_role=target,
                    origin_source="_seed_repair",
                    origin_tick=self._tick,
                    intensity=intensity,
                    credibility=0.6,
                )

    # -----------------------------------------------------------------
    # Role transitions (B direction §14 cond 1 / Batch 6)
    # -----------------------------------------------------------------

    def transition_role(
        self,
        agent_id: str,
        new_role_id: str,
        *,
        reason: str = "",
        blend_factor: float = 0.6,
        merge_affordances: bool = True,
    ) -> RoleTransitionRecord:
        """Transition an agent to a new role cluster mid-simulation.

        Rule #12-safe: only shifts profile + affordances, never sets action.
        State (fear, shame, guilt, relations) is preserved — the agent
        carries their history across the transition.
        """
        agent = self._agents.get(agent_id)
        if agent is None:
            raise KeyError(f"unknown agent '{agent_id}'")

        result = apply_role_transition(
            current_profile=agent.profile,
            current_role_id=agent.role_id,
            new_role_id=new_role_id,
            tick=self._tick,
            blend_factor=blend_factor,
            reason=reason,
            rng=self._rng,
            merge_affordances=merge_affordances,
        )

        agent.profile = result.new_profile
        agent.role_id = result.new_role_id
        if merge_affordances:
            merged = list(agent.affordance_pack)
            for a in result.new_affordance_pack:
                if a not in merged:
                    merged.append(a)
            agent.affordance_pack = merged
        else:
            agent.affordance_pack = result.new_affordance_pack
        agent.info_access_level = result.new_info_access_level
        agent.transition_log.append(result.record)
        return result.record

    # -----------------------------------------------------------------
    # Queries
    # -----------------------------------------------------------------

    def get_crowd(self, crowd_id: str) -> CrowdState | None:
        return self._crowds.get(crowd_id)

    def get_agent(self, agent_id: str) -> AgentHandle | None:
        return self._agents.get(agent_id)

    def get_spatial(self) -> SpatialRegistry:
        return self._spatial

    def get_rumors(self) -> RumorRegistry:
        return self._rumors

    @property
    def tick(self) -> int:
        return self._tick
