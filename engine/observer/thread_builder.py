"""Thread builder — Moment linking + StoryThread mining.

Per `docs/WITNESS_NARRATIVE_MINING_PLAN.md` §4.3, §5.1–5.4, §7, §8.

Phase 2 (link_moments): produce a deterministic list of MomentLink edges
over a list of Moments.

Phase 3 (build_story_threads): collapse linked components / paths into
StoryThread objects with conflict/arc inference and a potential score.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from engine.observer.moment import Moment
from engine.observer.thread import ArcDirection, MomentLink, StoryThread


# ---------------------------------------------------------------------------
# Linking thresholds
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LinkThresholds:
    """Tuning surface for link_moments.

    max_gap is the *primary* tick distance budget. Beyond max_gap, only
    unresolved-thread Moments may extend the budget (max_gap_unresolved).
    """
    max_gap: int = 30
    max_gap_unresolved: int = 60
    same_agent_weight: float = 0.85
    same_group_weight: float = 0.65
    same_pressure_weight: float = 0.55
    same_conflict_axis_weight: float = 0.75
    temporal_continuity_weight: float = 0.30
    causal_order_weight: float = 0.50
    # decay scales weight by tick distance:
    #   weight_eff = base * max(0, 1 - gap / decay_horizon)
    decay_horizon: int = 50


DEFAULT_LINK_THRESHOLDS = LinkThresholds()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decay(weight: float, gap: int, horizon: int) -> float:
    if horizon <= 0:
        return weight
    return max(0.0, weight * max(0.0, 1.0 - gap / horizon))


def _tick_gap(a: Moment, b: Moment) -> int:
    """Smallest gap between the two moments' tick spans."""
    a_lo, a_hi = a.tick_range
    b_lo, b_hi = b.tick_range
    if a_hi < b_lo:
        return b_lo - a_hi
    if b_hi < a_lo:
        return a_lo - b_hi
    return 0  # overlapping ranges


def _allowed_gap(a: Moment, b: Moment, th: LinkThresholds) -> int:
    """Apply the unresolved-thread bonus when either side is sustained."""
    if "unresolved_thread" in (a.moment_type, b.moment_type):
        return th.max_gap_unresolved
    return th.max_gap


# ---------------------------------------------------------------------------
# Conflict-axis mapping (deterministic, content-free)
# ---------------------------------------------------------------------------

# Pressure → conflict family. Used by same_conflict_axis link inference.
# A conflict family is a coarse cluster of pressures that frequently co-fire.
_PRESSURE_TO_FAMILY: dict[str, str] = {
    "fear": "internal_collapse",
    "hope": "internal_collapse",
    "shame_self": "internal_collapse",
    "group_tension": "collective_pressure",
    "blame_concentration": "collective_pressure",
    "public_suspicion": "collective_pressure",
    "authority_vigilance": "external_authority",
    "crowd_mood": "atmosphere",
}


def _conflict_families(m: Moment) -> set[str]:
    return {_PRESSURE_TO_FAMILY[p] for p in m.pressures if p in _PRESSURE_TO_FAMILY}


# ---------------------------------------------------------------------------
# Phase 2 — link_moments
# ---------------------------------------------------------------------------

def link_moments(
    moments: list[Moment],
    thresholds: LinkThresholds | None = None,
) -> list[MomentLink]:
    """Produce a deterministic, sorted list of MomentLink edges.

    For every ordered pair (a, b) with a.tick <= b.tick and within the gap
    budget, evaluate each link family and emit the best link (one per
    family per pair).
    """
    th = thresholds or DEFAULT_LINK_THRESHOLDS
    # Sort moments to give deterministic iteration order
    moms = sorted(moments, key=lambda m: (m.tick, m.moment_id))
    out: list[MomentLink] = []

    for i, a in enumerate(moms):
        for b in moms[i + 1:]:
            gap = _tick_gap(a, b)
            allowed = _allowed_gap(a, b, th)
            if gap > allowed:
                # Past the budget — no further b can be closer because moms is sorted
                break  # since b.tick is monotonic non-decreasing

            # Each link family is independent; emit at most one per family per pair
            agents_a = set(a.agents)
            agents_b = set(b.agents)
            shared_agents = agents_a & agents_b
            if shared_agents:
                w = _decay(th.same_agent_weight, gap, th.decay_horizon)
                if w > 0:
                    out.append(MomentLink(
                        source_moment_id=a.moment_id,
                        target_moment_id=b.moment_id,
                        link_type="same_agent",
                        weight=w,
                        rationale=(
                            f"shared agent(s): {', '.join(sorted(shared_agents))}; gap={gap}"
                        ),
                    ))

            groups_a = set(a.groups)
            groups_b = set(b.groups)
            shared_groups = groups_a & groups_b
            if shared_groups:
                w = _decay(th.same_group_weight, gap, th.decay_horizon)
                if w > 0:
                    out.append(MomentLink(
                        source_moment_id=a.moment_id,
                        target_moment_id=b.moment_id,
                        link_type="same_group",
                        weight=w,
                        rationale=(
                            f"shared group(s): {', '.join(sorted(shared_groups))}; gap={gap}"
                        ),
                    ))

            press_a = set(a.pressures)
            press_b = set(b.pressures)
            shared_press = press_a & press_b
            if shared_press:
                w = _decay(th.same_pressure_weight, gap, th.decay_horizon)
                if w > 0:
                    out.append(MomentLink(
                        source_moment_id=a.moment_id,
                        target_moment_id=b.moment_id,
                        link_type="same_pressure",
                        weight=w,
                        rationale=(
                            f"shared pressure(s): {', '.join(sorted(shared_press))}; gap={gap}"
                        ),
                    ))

            fams_a = _conflict_families(a)
            fams_b = _conflict_families(b)
            shared_fam = fams_a & fams_b
            if shared_fam and not shared_press:
                # Only emit when conflict family overlaps but raw pressure does NOT
                # (otherwise same_pressure already captures the relation).
                w = _decay(th.same_conflict_axis_weight, gap, th.decay_horizon)
                if w > 0:
                    out.append(MomentLink(
                        source_moment_id=a.moment_id,
                        target_moment_id=b.moment_id,
                        link_type="same_conflict_axis",
                        weight=w,
                        rationale=(
                            f"shared conflict family: {', '.join(sorted(shared_fam))}; "
                            f"gap={gap}"
                        ),
                    ))

            # Causal order: source emits a pressure that the target later
            # uses as one of its signal triggers. Heuristic: a source
            # 'world_pressure_shift' that raises authority_vigilance is a
            # plausible cause of a later 'agent_state_shift' in fear.
            if (a.moment_type == "world_pressure_shift"
                    and "authority_vigilance" in a.pressures
                    and "rises" in a.summary
                    and b.moment_type == "agent_state_shift"
                    and "fear" in b.pressures
                    and "rises" in b.summary
                    and gap > 0):
                w = _decay(th.causal_order_weight, gap, th.decay_horizon)
                if w > 0:
                    out.append(MomentLink(
                        source_moment_id=a.moment_id,
                        target_moment_id=b.moment_id,
                        link_type="causal_order",
                        weight=w,
                        rationale=(
                            f"authority_vigilance rise → agent fear rise (gap={gap})"
                        ),
                    ))

            # Temporal continuity is a *fallback* link — emit only when no
            # other link family fired for this pair.
            already_linked = any(
                l.source_moment_id == a.moment_id and l.target_moment_id == b.moment_id
                for l in out[-5:]  # only check tail (we just appended for this pair)
            )
            if not already_linked and gap <= th.max_gap // 2:
                w = _decay(th.temporal_continuity_weight, gap, th.decay_horizon)
                if w > 0:
                    out.append(MomentLink(
                        source_moment_id=a.moment_id,
                        target_moment_id=b.moment_id,
                        link_type="temporal_continuity",
                        weight=w,
                        rationale=f"close-in-time fallback link (gap={gap})",
                    ))

    # Deterministic sort: by (source, target, type)
    out.sort(key=lambda l: (l.source_moment_id, l.target_moment_id, l.link_type))
    return out


def serialize_links(
    links: Iterable[MomentLink],
    *,
    schema_version: str = "moment_links_v1",
) -> dict:
    link_list = list(links)
    by_type: dict[str, int] = {}
    for l in link_list:
        by_type[l.link_type] = by_type.get(l.link_type, 0) + 1
    return {
        "schema_version": schema_version,
        "links": [l.to_dict() for l in link_list],
        "summary": {
            "total": len(link_list),
            "by_type": by_type,
        },
    }


# ===========================================================================
# Phase 3 — StoryThread mining
# ===========================================================================

@dataclass(frozen=True)
class ThreadThresholds:
    """Tuning surface for build_story_threads."""
    min_moments_per_thread: int = 3
    min_score_for_inclusion: float = 0.40
    strong_score: float = 0.80
    usable_score: float = 0.60
    weak_score: float = 0.40
    # Weight balance for story_potential_score (must sum to 1.0)
    w_change: float = 0.20
    w_continuity: float = 0.15
    w_conflict: float = 0.20
    w_relationship: float = 0.15
    w_pressure: float = 0.10
    w_resolution_gap: float = 0.10
    w_multi_agent: float = 0.05
    w_creative_use: float = 0.05


DEFAULT_THREAD_THRESHOLDS = ThreadThresholds()


# ---------------------------------------------------------------------------
# Connected components on the moment graph
# ---------------------------------------------------------------------------

def _connected_components(
    moments: list[Moment],
    links: list[MomentLink],
    *,
    allowed_link_types: frozenset[str] = frozenset({"same_agent", "same_group"}),
) -> list[list[Moment]]:
    """Union-Find over a *filtered* link graph.

    Only links whose `link_type` is in `allowed_link_types` participate in
    component detection. This prevents weak links (temporal_continuity,
    same_pressure across disjoint agents) from collapsing the graph into a
    single mega-component.

    Defaults to *structural* links only: same_agent and same_group. Use
    same_pressure or same_conflict_axis only when you specifically want
    cross-agent threads.
    """
    parent: dict[str, str] = {m.moment_id: m.moment_id for m in moments}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    moment_ids = {m.moment_id for m in moments}
    for l in links:
        if l.link_type not in allowed_link_types:
            continue
        if l.source_moment_id in moment_ids and l.target_moment_id in moment_ids:
            union(l.source_moment_id, l.target_moment_id)

    by_root: dict[str, list[Moment]] = {}
    for m in moments:
        by_root.setdefault(find(m.moment_id), []).append(m)

    comps = list(by_root.values())
    for c in comps:
        c.sort(key=lambda m: (m.tick, m.moment_id))
    comps.sort(key=lambda c: (c[0].tick, c[0].moment_id))
    return comps


def _mine_threads_by_agent(
    moments: list[Moment],
    links: list[MomentLink],
) -> list[list[Moment]]:
    """Agent-centric mining: for each agent, the moments where they appear,
    connected by same_agent links, form a candidate thread.

    A moment with 0 agents (e.g. `world_pressure_shift` with no actor) is
    *broadcast* to every component it shares a `same_pressure` or
    `same_conflict_axis` link with — those world-level moments belong to
    multiple threads (the same authority spike participates in several
    agent stories).
    """
    # Bucket by primary agent (first agent in moment.agents)
    by_agent: dict[str, list[Moment]] = {}
    no_agent: list[Moment] = []
    for m in moments:
        if m.agents:
            by_agent.setdefault(m.agents[0], []).append(m)
        else:
            no_agent.append(m)

    # For each agent's bucket, attach world/group moments that share
    # pressures or conflict axis with at least one of the agent's moments.
    threads: list[list[Moment]] = []
    for aid, agent_moments in by_agent.items():
        # Build a moment_id set for cheap lookup
        bucket_ids = {m.moment_id for m in agent_moments}
        bucket = list(agent_moments)

        # Gather world/group moments linked into this agent's bucket via
        # *bridge* links (same_pressure / same_conflict_axis)
        bridge_types = {"same_pressure", "same_conflict_axis"}
        for m in no_agent:
            for l in links:
                if l.link_type not in bridge_types:
                    continue
                if (l.source_moment_id == m.moment_id and l.target_moment_id in bucket_ids) \
                        or (l.target_moment_id == m.moment_id
                            and l.source_moment_id in bucket_ids):
                    if m.moment_id not in bucket_ids:
                        bucket.append(m)
                        bucket_ids.add(m.moment_id)
                    break  # one bridge is enough

        bucket.sort(key=lambda m: (m.tick, m.moment_id))
        threads.append(bucket)

    threads.sort(key=lambda b: (b[0].tick if b else 0, b[0].moment_id if b else ""))
    return threads


def _mine_threads_by_group(
    moments: list[Moment],
    links: list[MomentLink],
) -> list[list[Moment]]:
    """Group-centric mining for moments where no single agent dominates."""
    by_group: dict[str, list[Moment]] = {}
    for m in moments:
        if m.groups and not m.agents:
            for g in m.groups:
                by_group.setdefault(g, []).append(m)
    threads: list[list[Moment]] = []
    for gid, group_moments in by_group.items():
        bucket = sorted(group_moments, key=lambda m: (m.tick, m.moment_id))
        threads.append(bucket)
    return threads


# ---------------------------------------------------------------------------
# Conflict / arc inference (deterministic rules; plan §7-8)
# ---------------------------------------------------------------------------

def _infer_core_conflict(component: list[Moment]) -> str:
    """Map combined pressure profile to a conflict label."""
    pressures: set[str] = set()
    for m in component:
        pressures.update(m.pressures)

    has = lambda *names: any(n in pressures for n in names)
    fear_up = any("fear" in m.pressures and "rises" in m.summary for m in component)
    hope_down = any("hope" in m.pressures and "falls" in m.summary for m in component)
    shame_up = any("shame_self" in m.pressures and "rises" in m.summary for m in component)
    auth_up = any("authority_vigilance" in m.pressures and "rises" in m.summary for m in component)
    sus_up = any("public_suspicion" in m.pressures and "rises" in m.summary for m in component)
    blame_up = any("blame_concentration" in m.pressures and "rises" in m.summary for m in component)
    tension_up = any("group_tension" in m.pressures and "rises" in m.summary for m in component)

    if fear_up and (auth_up or sus_up):
        return "loyalty_vs_survival"
    if tension_up and blame_up:
        return "collective_fear_vs_scapegoating"
    if auth_up and sus_up:
        return "control_vs_exposure"
    if hope_down and shame_up:
        return "identity_vs_failure"
    if has("fear") and has("hope"):
        return "trust_vs_self_protection"
    if any(m.moment_type == "unresolved_thread" for m in component):
        return "uncertainty_vs_commitment"
    if has("crowd_mood"):
        return "atmosphere_vs_action"
    return "unknown"


def _infer_arc_direction(component: list[Moment]) -> ArcDirection:
    """Map start→end signal pattern to an arc label."""
    fear_up = any("fear" in m.pressures and "rises" in m.summary for m in component)
    hope_down = any("hope" in m.pressures and "falls" in m.summary for m in component)
    shame_up = any("shame_self" in m.pressures and "rises" in m.summary for m in component)
    tension_up = any("group_tension" in m.pressures and "rises" in m.summary for m in component)
    has_unresolved = any(m.moment_type == "unresolved_thread" for m in component)

    if fear_up and (shame_up or has_unresolved):
        return "fear_to_withdrawal"
    if hope_down and shame_up:
        return "stability_to_breakdown"
    if tension_up and any("conflict_marker" == m.moment_type for m in component):
        return "tension_to_collective_action"
    if fear_up and tension_up:
        return "trust_to_distance"
    if has_unresolved and not fear_up:
        return "isolation_to_dependence"
    return "unknown"


# ---------------------------------------------------------------------------
# Score factors (each in [0, 1])
# ---------------------------------------------------------------------------

def _score_change(component: list[Moment]) -> float:
    """Magnitude of state change across the component span."""
    if not component:
        return 0.0
    # Use max salience as proxy for change magnitude
    return min(1.0, max(m.salience_score for m in component))


def _score_continuity(component: list[Moment]) -> float:
    """How tightly the moments cluster in time."""
    if len(component) < 2:
        return 0.5
    span = component[-1].tick - component[0].tick
    if span == 0:
        return 1.0
    avg_gap = span / max(1, len(component) - 1)
    # Smaller avg_gap → higher continuity. Normalize: gap 5 → 1.0, gap 50 → 0.0
    return max(0.0, min(1.0, 1.0 - (avg_gap - 5) / 45.0))


def _score_conflict(component: list[Moment]) -> float:
    has_conflict = any(m.moment_type == "conflict_marker" for m in component)
    pressures = {p for m in component for p in m.pressures}
    has_diverse = len(pressures) >= 3
    if has_conflict and has_diverse:
        return 1.0
    if has_conflict or has_diverse:
        return 0.7
    if len(pressures) >= 2:
        return 0.4
    return 0.2


def _score_relationship(component: list[Moment]) -> float:
    """Engine doesn't yet emit relationship deltas — reserved.

    Use group_tension_shift as a weak proxy: when group tension changes
    *and* multiple agents are involved, treat as relationship signal.
    """
    has_group_tension = any(
        m.moment_type == "group_tension_shift" for m in component
    )
    multi_agents = len({a for m in component for a in m.agents}) >= 2
    if has_group_tension and multi_agents:
        return 0.7
    if has_group_tension or multi_agents:
        return 0.4
    return 0.1


def _score_pressure(component: list[Moment]) -> float:
    """Pressure accumulation: how many distinct pressures are involved."""
    pressures = {p for m in component for p in m.pressures}
    return min(1.0, len(pressures) / 4.0)


def _score_resolution_gap(component: list[Moment]) -> float:
    """Strength of the unresolved question.

    Strong unresolved signal → high score. Bonus if final moment is an
    unresolved_thread (the story doesn't resolve).
    """
    has_unresolved = any(m.moment_type == "unresolved_thread" for m in component)
    final_unresolved = component and component[-1].moment_type == "unresolved_thread"
    if final_unresolved:
        return 1.0
    if has_unresolved:
        return 0.7
    return 0.3


def _score_multi_agent(component: list[Moment]) -> float:
    agents = {a for m in component for a in m.agents}
    groups = {g for m in component for g in m.groups}
    if len(agents) >= 3:
        return 1.0
    if len(agents) >= 2 or len(groups) >= 2:
        return 0.6
    if len(agents) == 1:
        return 0.3
    return 0.0


def _score_creative_use(component: list[Moment]) -> float:
    """Does the component look like a usable scene/episode seed?

    Simple proxy: has *both* an agent-level moment *and* a world-level moment.
    """
    has_agent = any(m.moment_type == "agent_state_shift" for m in component)
    has_world = any(m.moment_type == "world_pressure_shift" for m in component)
    has_group = any(m.moment_type == "group_tension_shift" for m in component)
    layers = sum([has_agent, has_world, has_group])
    return layers / 3.0


def _compute_score(component: list[Moment], th: ThreadThresholds) -> float:
    return (
        th.w_change          * _score_change(component)
        + th.w_continuity      * _score_continuity(component)
        + th.w_conflict        * _score_conflict(component)
        + th.w_relationship    * _score_relationship(component)
        + th.w_pressure        * _score_pressure(component)
        + th.w_resolution_gap  * _score_resolution_gap(component)
        + th.w_multi_agent     * _score_multi_agent(component)
        + th.w_creative_use    * _score_creative_use(component)
    )


# ---------------------------------------------------------------------------
# Title + question generation (deterministic, content-free)
# ---------------------------------------------------------------------------

_TITLE_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival": "Loyalty Strained by Survival Pressure",
    "trust_vs_self_protection": "Trust Yields to Self-Protection",
    "collective_fear_vs_scapegoating": "Group Fear Concentrates Blame",
    "control_vs_exposure": "Authority Tightens as Suspicion Spreads",
    "identity_vs_failure": "Identity Falters Under Failure",
    "uncertainty_vs_commitment": "Uncertainty Lingers Without Commitment",
    "atmosphere_vs_action": "Atmosphere Shifts Without Resolution",
    "unknown": "Unresolved Pressure Sequence",
}

_QUESTION_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival": "Will the central agents stay in place or withdraw under pressure?",
    "trust_vs_self_protection": "Does internal protection survive the relationship test?",
    "collective_fear_vs_scapegoating": "Where does the group's fear settle next?",
    "control_vs_exposure": "Does the surveilled relax or escalate?",
    "identity_vs_failure": "What identity remains after this loss?",
    "uncertainty_vs_commitment": "Is a commitment moment coming, or does drift continue?",
    "atmosphere_vs_action": "Does the changed atmosphere translate into visible action?",
    "unknown": "What does this pressure pattern lead to?",
}


def _creative_uses_for(conflict: str, score: float) -> tuple[str, ...]:
    """Map conflict category + score to creative-use tags."""
    if score < 0.4:
        return ()
    base: dict[str, tuple[str, ...]] = {
        "loyalty_vs_survival": ("film_scene", "novel_chapter", "game_quest_branch"),
        "trust_vs_self_protection": ("novel_chapter", "drama_episode"),
        "collective_fear_vs_scapegoating": ("drama_episode", "documentary_segment"),
        "control_vs_exposure": ("film_scene", "drama_episode"),
        "identity_vs_failure": ("novel_chapter", "short_story"),
        "uncertainty_vs_commitment": ("short_story", "game_branch"),
        "atmosphere_vs_action": ("documentary_segment",),
        "unknown": ("inspectable_only",),
    }
    return base.get(conflict, ("inspectable_only",))


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build_story_threads(
    moments: list[Moment],
    links: list[MomentLink],
    thresholds: ThreadThresholds | None = None,
) -> list[StoryThread]:
    """Build a deterministic, sorted list of StoryThread from moments+links.

    Steps:
      1. Connected-component partition over the link graph.
      2. Filter components by min_moments_per_thread.
      3. Infer core_conflict, arc_direction, score, title, question.
      4. Filter by min_score_for_inclusion.
      5. Sort by descending score, then by start_tick.
    """
    th = thresholds or DEFAULT_THREAD_THRESHOLDS
    # Strategy: agent-centric mining first (gives one thread per active agent),
    # then group-centric for orphan group/world moments. This avoids the
    # mega-component problem where temporal_continuity links collapse all
    # 100+ moments into a single thread.
    agent_comps = _mine_threads_by_agent(moments, links)
    group_comps = _mine_threads_by_group(moments, links)
    comps = agent_comps + group_comps
    # Stable sort: by earliest tick
    comps.sort(key=lambda b: (b[0].tick if b else 0, b[0].moment_id if b else ""))

    threads: list[StoryThread] = []
    for idx, comp in enumerate(comps):
        if len(comp) < th.min_moments_per_thread:
            continue
        score = _compute_score(comp, th)
        if score < th.min_score_for_inclusion:
            continue

        conflict = _infer_core_conflict(comp)
        arc = _infer_arc_direction(comp)

        # Aggregate metadata
        agents = sorted({a for m in comp for a in m.agents})
        groups = sorted({g for m in comp for g in m.groups})
        # main vs supporting: split by frequency in component
        agent_freq: dict[str, int] = {}
        for m in comp:
            for a in m.agents:
                agent_freq[a] = agent_freq.get(a, 0) + 1
        sorted_agents = sorted(agent_freq.items(), key=lambda kv: (-kv[1], kv[0]))
        cutoff = max(1, len(sorted_agents) // 2) if sorted_agents else 0
        main_agents = tuple(a for a, _ in sorted_agents[:cutoff])
        supporting_agents = tuple(a for a, _ in sorted_agents[cutoff:])

        pressures = []
        for m in comp:
            for p in m.pressures:
                if p not in pressures:
                    pressures.append(p)

        rel_drift: tuple[str, ...] = ()
        if any(m.moment_type == "group_tension_shift" and "rises" in m.summary
               for m in comp):
            rel_drift = ("distance_up",)
        elif any(m.moment_type == "group_tension_shift" and "falls" in m.summary
                 for m in comp):
            rel_drift = ("distance_down",)

        thread = StoryThread(
            thread_id=f"T{idx + 1:02d}",
            title=_TITLE_BY_CONFLICT.get(conflict, _TITLE_BY_CONFLICT["unknown"]),
            main_agents=main_agents or tuple(agents[:1]),
            supporting_agents=supporting_agents,
            groups=tuple(groups),
            core_conflict=conflict,
            arc_direction=arc,
            moment_ids=tuple(m.moment_id for m in comp),
            start_tick=comp[0].tick,
            end_tick=comp[-1].tick,
            pressure_history=tuple(pressures),
            relationship_drift=rel_drift,
            unresolved_question=_QUESTION_BY_CONFLICT.get(
                conflict, _QUESTION_BY_CONFLICT["unknown"]
            ),
            story_potential_score=score,
            usable_as=_creative_uses_for(conflict, score),
            provenance="source_inferred",
        )
        threads.append(thread)

    # Sort: descending score, then start_tick asc, then thread_id asc
    threads.sort(key=lambda t: (-t.story_potential_score, t.start_tick, t.thread_id))
    # Re-assign thread_id after sort to keep T01 = strongest
    final: list[StoryThread] = []
    for i, t in enumerate(threads, start=1):
        final.append(StoryThread(
            **{**t.to_dict(),
               "thread_id": f"T{i:02d}",
               "main_agents": t.main_agents,
               "supporting_agents": t.supporting_agents,
               "groups": t.groups,
               "moment_ids": t.moment_ids,
               "pressure_history": t.pressure_history,
               "relationship_drift": t.relationship_drift,
               "usable_as": t.usable_as}
        ))
    return final


def serialize_threads(
    threads: Iterable[StoryThread],
    *,
    run_label: str,
    schema_version: str = "story_threads_v1",
    th: ThreadThresholds | None = None,
) -> dict:
    th = th or DEFAULT_THREAD_THRESHOLDS
    thread_list = list(threads)
    strong = sum(1 for t in thread_list if t.story_potential_score >= th.strong_score)
    usable = sum(1 for t in thread_list
                 if th.usable_score <= t.story_potential_score < th.strong_score)
    weak = sum(1 for t in thread_list
               if th.weak_score <= t.story_potential_score < th.usable_score)
    return {
        "run_label": run_label,
        "schema_version": schema_version,
        "threads": [t.to_dict() for t in thread_list],
        "summary": {
            "total": len(thread_list),
            "strong": strong,
            "usable": usable,
            "weak": weak,
        },
    }

