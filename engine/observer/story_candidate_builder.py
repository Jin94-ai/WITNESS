"""StoryCandidate builder — Stage 6 + Phase C TurningPoint selector.

Per `docs/WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md` §6.1-§6.5.

Pipeline:
    StoryThread + Moment list + IdentityResolver
        ↓ select_turning_points(thread, moments)
        ↓ build_premise(thread, identity)
        ↓ build_arc_summary(moments_in_thread)
        ↓ build_relationship_dynamics(thread, moments, identity)
        ↓ build_adaptation_hooks(thread)
        → StoryCandidate

ABSOLUTE rules (plan §10.2):
    - No completed prose / dialogue / screenplay / over-narrated emotion.
    - All sentences traceable to a moment + provenance class.
    - Premise template selected by *enriched* conflict + identity, not
      raw conflict label.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.observer.identity_resolver import (
    AgentIdentity,
    IdentityResolver,
    translate_pressure,
)
from engine.observer.moment import Moment
from engine.observer.story_candidate import StoryCandidate, TurningPoint
from engine.observer.thread import StoryThread


# ---------------------------------------------------------------------------
# Phase C — Turning Point selector
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TurningPointThresholds:
    max_points: int = 4
    salience_floor: float = 0.50           # below = skip


def select_turning_points(
    thread: StoryThread,
    moments_by_id: dict[str, Moment],
    thresholds: TurningPointThresholds | None = None,
    identity: IdentityResolver | None = None,
) -> list[TurningPoint]:
    """Select up to N narratively prominent moments from a thread.

    Selection priority (plan §6.3):
      1. conflict_marker moments (always include — these mark co-firing signals)
      2. unresolved_thread *start* (the moment where sustained pressure begins)
      3. world_pressure_shift with high salience
      4. agent_state_shift with high salience
      5. group_tension_shift with high salience

    Output is sorted by tick. At most `max_points` retained, but conflict
    markers are kept regardless of cap.
    """
    th = thresholds or TurningPointThresholds()
    moms = [m for mid in thread.moment_ids if (m := moments_by_id.get(mid))]
    if not moms:
        return []

    selected: list[Moment] = []
    seen: set[str] = set()

    # Pass 1: conflict markers always
    for m in moms:
        if m.moment_type == "conflict_marker" and m.moment_id not in seen:
            selected.append(m)
            seen.add(m.moment_id)

    # Pass 2: unresolved_thread starts
    for m in moms:
        if m.moment_type == "unresolved_thread" and m.moment_id not in seen:
            selected.append(m)
            seen.add(m.moment_id)

    # Pass 3: high-salience world / group / agent shifts
    high_sal = [m for m in moms
                if m.moment_id not in seen
                and m.salience_score >= th.salience_floor]
    high_sal.sort(key=lambda m: -m.salience_score)
    for m in high_sal:
        if len(selected) >= th.max_points and m.moment_type != "conflict_marker":
            break
        selected.append(m)
        seen.add(m.moment_id)

    # Cap (but always keep conflict_markers)
    conflict_keep = [m for m in selected if m.moment_type == "conflict_marker"]
    other = [m for m in selected if m.moment_type != "conflict_marker"]
    if len(other) > th.max_points - len(conflict_keep):
        # Keep highest-salience among the non-conflict
        other.sort(key=lambda m: -m.salience_score)
        other = other[: max(0, th.max_points - len(conflict_keep))]
    final = sorted(conflict_keep + other, key=lambda m: m.tick)

    return [_moment_to_turning_point(m, identity) for m in final]


_TURNING_POINT_LABELS = {
    "conflict_marker":      "co-occurring pressure",
    "unresolved_thread":    "sustained pressure begins",
    "world_pressure_shift": "world pressure shift",
    "agent_state_shift":    "agent state shift",
    "group_tension_shift":  "group tension shift",
    "event_ripple":         "event ripple",
    "choice_pattern":       "choice pattern",
    "relationship_drift":   "relationship drift",
}


def _moment_to_turning_point(
    m: Moment,
    identity: IdentityResolver | None = None,
) -> TurningPoint:
    label = _TURNING_POINT_LABELS.get(m.moment_type, m.moment_type)
    summary = m.summary
    # Apply identity translation if resolver provided. Keep numeric values
    # verbatim — only swap leading agent IDs for display names.
    if identity is not None:
        for aid in m.agents:
            label_str = identity.agent_label(aid)
            # Only substitute if the label is genuinely different from the ID
            # (resolver returns ID itself when no mapping exists).
            if label_str != aid:
                summary = summary.replace(aid, label_str)
        for gid in m.groups:
            glabel = identity.group_label(gid)
            if glabel != gid:
                summary = summary.replace(f"group {gid}", f"group {glabel}")
    return TurningPoint(
        tick=m.tick,
        moment_ids=(m.moment_id,),
        label=label,
        summary=summary,
        provenance=m.provenance,
    )


# ---------------------------------------------------------------------------
# Stage 6.1 — One-line Premise
# ---------------------------------------------------------------------------

# Conflict + main archetype combinations → premise template.
# Templates use {main} placeholder for the resolved name(s).
_PREMISE_BY_KEY: dict[tuple[str, str], str] = {
    ("loyalty_vs_survival", "loyal_under_pressure"):
        "{main} tries to stay present as fear and public pressure slowly turn loyalty into silence.",
    ("loyalty_vs_survival", "loyal_presence"):
        "{main} stays close to the group while authority pressure rises and fear quietly accumulates.",
    ("trust_vs_self_protection", "loyal_under_pressure"):
        "{main}'s trust gives way to self-protection as the surrounding pressure does not relent.",
    ("collective_fear_vs_scapegoating", "background_presence"):
        "Fear inside {group} concentrates blame on someone visible, even without an explicit decision.",
    ("control_vs_exposure", "skeptic_witness"):
        "{main} watches authority tighten its watch as suspicion spreads through the crowd.",
    ("identity_vs_failure", "loyal_under_pressure"):
        "{main}'s hope falters and shame accumulates over the run, with no clear restoration.",
    ("uncertainty_vs_commitment", "loyal_under_pressure"):
        "{main} stays under pressure without a commitment moment — drift continues.",
    ("uncertainty_vs_commitment", "peripheral_disciple"):
        "{main} stays near the group but remains uncommitted as pressure rises around them.",
    ("uncertainty_vs_commitment", "skeptic_witness"):
        "{main} watches without committing as conditions shift around them.",
    ("uncertainty_vs_commitment", "background_presence"):
        "An uncommitted figure drifts through pressure shifts without a decision.",
    ("atmosphere_vs_action", "background_presence"):
        "The world's mood shifts but no decisive action follows from {main}.",
}


_GENERIC_PREMISE = (
    "{main} moves through accumulated pressure within {group}; the run "
    "does not resolve the question."
)


def build_premise(
    thread: StoryThread,
    identity: IdentityResolver,
) -> str:
    """Choose a premise template by (conflict, main_archetype). Substitute names."""
    main_id = thread.main_agents[0] if thread.main_agents else None
    main_archetype = "background_presence"
    main_name = "Someone in the world"
    if main_id:
        ident = identity.agent_identity(main_id)
        main_archetype = ident.archetype or "background_presence"
        main_name = ident.display_name

    key = (thread.core_conflict, main_archetype)
    template = _PREMISE_BY_KEY.get(key, _GENERIC_PREMISE)

    group_label = (
        identity.group_label(thread.groups[0]) if thread.groups else "the group"
    )
    return template.format(main=main_name, group=group_label)


# ---------------------------------------------------------------------------
# Stage 6.2 — Arc Summary
# ---------------------------------------------------------------------------

def build_arc_summary(
    thread: StoryThread,
    moments_by_id: dict[str, Moment],
    identity: IdentityResolver,
) -> str:
    """Compress thread moments into an arc summary.

    Format:
        translated_pressure_1 → translated_pressure_2 → unresolved_state
    """
    moms = [m for mid in thread.moment_ids if (m := moments_by_id.get(mid))]
    moms.sort(key=lambda m: m.tick)

    seen_phrase: list[str] = []
    for m in moms:
        for p in m.pressures:
            direction = "rise" if "rises" in m.summary else (
                "fall" if "falls" in m.summary else "rise"
            )
            phrase = translate_pressure(p, direction)
            if phrase not in seen_phrase:
                seen_phrase.append(phrase)
            if len(seen_phrase) >= 4:
                break
        if len(seen_phrase) >= 4:
            break

    # Add unresolved tail if applicable
    has_unresolved = any(
        m.moment_type == "unresolved_thread" for m in moms
    )
    if has_unresolved and "unresolved tension lingers" not in seen_phrase:
        seen_phrase.append("unresolved tension lingers")

    if not seen_phrase:
        return "no major pressure transitions detected"
    return " → ".join(seen_phrase)


# ---------------------------------------------------------------------------
# Stage 6.4 — Relationship Dynamics (Phase D scaffolding)
# ---------------------------------------------------------------------------

def build_relationship_dynamics(
    thread: StoryThread,
    moments_by_id: dict[str, Moment],
    identity: IdentityResolver,
) -> list[str]:
    """Emit conservative relationship-context lines.

    Plan §6.4 / §10.2: do NOT overstate "relationships". The engine does
    not yet emit relationship deltas. We only have:
      - group co-presence (which agent is in which group)
      - group_tension_shift moments
      - co-firing of agent state shifts within the same tick window
    So the output language is hedged. Every line ends with provenance
    qualifier ("group context only", "co-occurring fear", etc.).
    """
    moms = [m for mid in thread.moment_ids if (m := moments_by_id.get(mid))]
    main_name = (
        identity.agent_label(thread.main_agents[0]) if thread.main_agents else "the central agent"
    )

    lines: list[str] = []

    # 1. Main ↔ primary group line (always, if there is a group)
    if thread.groups:
        group_label = identity.group_label(thread.groups[0])
        has_group_tension_rise = any(
            m.moment_type == "group_tension_shift" and "rises" in m.summary
            for m in moms
        )
        has_unresolved = any(m.moment_type == "unresolved_thread" for m in moms)
        if has_group_tension_rise:
            lines.append(
                f"{main_name} ↔ {group_label}: group tension rises while "
                f"{main_name} stays in-frame (group context only)."
            )
        elif has_unresolved:
            lines.append(
                f"{main_name} ↔ {group_label}: sustained pressure on "
                f"{main_name} while group co-presence persists "
                f"(group context only)."
            )
        else:
            lines.append(
                f"{main_name} ↔ {group_label}: co-presence persists; "
                f"engine does not emit per-pair relationship deltas."
            )

    # 2. Supporting agent co-occurrences (when their fear/hope shifts at same window)
    if thread.supporting_agents:
        for sup_id in thread.supporting_agents[:2]:
            sup_name = identity.agent_label(sup_id)
            if sup_name == main_name:
                continue
            # Did this supporting agent show a state shift in any of this thread's moments?
            sup_moments = [m for m in moms if sup_id in m.agents]
            if not sup_moments:
                continue
            # Find pressure overlap with main
            main_pressures = {
                p for m in moms if thread.main_agents and thread.main_agents[0] in m.agents
                for p in m.pressures
            }
            sup_pressures = {p for m in sup_moments for p in m.pressures}
            shared = main_pressures & sup_pressures
            if shared:
                lines.append(
                    f"{main_name} ↔ {sup_name}: parallel pressure shifts in "
                    f"{', '.join(sorted(shared))} (co-occurring within thread, "
                    f"not a directional relationship signal)."
                )

    # 3. Cross-group context if the thread spans multiple groups
    if len(thread.groups) >= 2:
        groups_label = ", ".join(identity.group_label(g) for g in thread.groups)
        lines.append(
            f"Cross-group context: {main_name}'s thread spans {groups_label} "
            f"(group co-presence only)."
        )

    return lines


# ---------------------------------------------------------------------------
# Stage 6.5 — Adaptation Hooks
# ---------------------------------------------------------------------------

_HOOKS_BY_CONFLICT: dict[str, dict[str, str]] = {
    "loyalty_vs_survival": {
        "film_scene":
            "A quiet scene where {main} stays physically present but emotionally "
            "withdraws as authority pressure enters the room.",
        "novel_chapter":
            "A chapter tracking the slow conversion of loyalty into fear-driven silence.",
        "game_quest_branch":
            "The player must choose to confess, hide, or stay silent as public "
            "suspicion rises around {main}.",
    },
    "trust_vs_self_protection": {
        "novel_chapter":
            "A chapter on the moment trust becomes a luxury {main} can no longer afford.",
        "drama_episode":
            "An episode where small protective moves accumulate into a visible distance.",
    },
    "collective_fear_vs_scapegoating": {
        "drama_episode":
            "An episode where the group finds its scapegoat without ever naming the choice.",
        "documentary_segment":
            "A segment tracking how {group}'s fear concentrates on one figure over time.",
    },
    "control_vs_exposure": {
        "film_scene":
            "Authority gestures tighten as a small public sound spreads — no dialogue needed.",
        "drama_episode":
            "Two halves: surveillance perspective and surveilled perspective on the same window.",
    },
    "identity_vs_failure": {
        "novel_chapter":
            "{main}'s self-image fractures across small failures that nobody else marks.",
        "short_story":
            "A short piece where shame, not fear, becomes the primary engine of withdrawal.",
    },
    "uncertainty_vs_commitment": {
        "short_story":
            "A piece on a character who stays in the room but never makes the move.",
        "game_branch":
            "A branch where postponed decisions compound into a closed door.",
    },
    "atmosphere_vs_action": {
        "documentary_segment":
            "A segment where the change is in atmosphere only — no overt action follows.",
    },
}


def build_adaptation_hooks(
    thread: StoryThread,
    identity: IdentityResolver,
) -> dict[str, str]:
    """Return creative-use → one-line hook map. {main} / {group} substituted."""
    main_name = (
        identity.agent_label(thread.main_agents[0]) if thread.main_agents else "the central figure"
    )
    group_label = (
        identity.group_label(thread.groups[0]) if thread.groups else "the group"
    )
    raw = _HOOKS_BY_CONFLICT.get(thread.core_conflict, {})
    return {
        fmt: hook.format(main=main_name, group=group_label)
        for fmt, hook in raw.items()
    }


# ---------------------------------------------------------------------------
# Stage 6.0 — Top-level builder
# ---------------------------------------------------------------------------

def _world_pressure_context(
    thread: StoryThread,
    moments_by_id: dict[str, Moment],
) -> list[str]:
    """Translate world-level pressure shifts in this thread."""
    out: list[str] = []
    for mid in thread.moment_ids:
        m = moments_by_id.get(mid)
        if not m or m.moment_type != "world_pressure_shift":
            continue
        for p in m.pressures:
            direction = "rise" if "rises" in m.summary else "fall"
            phrase = translate_pressure(p, direction)
            if phrase not in out:
                out.append(phrase)
    return out


def _evidence_summary(
    thread: StoryThread,
    moments_by_id: dict[str, Moment],
) -> str:
    moms = [moments_by_id[mid] for mid in thread.moment_ids if mid in moments_by_id]
    pressures = sorted({p for m in moms for p in m.pressures})
    types = sorted({m.moment_type for m in moms})
    return (
        f"Built from {len(moms)} linked moments across "
        f"{len(pressures)} pressure type(s) and {len(types)} moment type(s)."
    )


def _provenance_summary(
    thread: StoryThread,
    moments_by_id: dict[str, Moment],
) -> dict[str, int]:
    out = {"source_derived": 0, "source_inferred": 0, "not_used": 0}
    for mid in thread.moment_ids:
        m = moments_by_id.get(mid)
        if not m:
            continue
        out[m.provenance] = out.get(m.provenance, 0) + 1
    return out


_RISK_NOTES_BASE = (
    "No dialogue generated.",
    "No unstated event added.",
    "Premise is inferred from pressure pattern, not directly authored by the engine.",
)


def build_story_candidate(
    thread: StoryThread,
    moments_by_id: dict[str, Moment],
    identity: IdentityResolver,
    *,
    candidate_index: int,
) -> StoryCandidate:
    main_chars = tuple(
        identity.agent_label(aid) for aid in thread.main_agents
    )
    supporting = tuple(
        identity.agent_label(aid) for aid in thread.supporting_agents
    ) + tuple(
        identity.group_label(gid) for gid in thread.groups
    )

    turning_points = tuple(select_turning_points(thread, moments_by_id, identity=identity))
    premise = build_premise(thread, identity)
    arc = build_arc_summary(thread, moments_by_id, identity)
    relationships = tuple(
        build_relationship_dynamics(thread, moments_by_id, identity)
    )
    pressure_ctx = tuple(_world_pressure_context(thread, moments_by_id))
    hooks = build_adaptation_hooks(thread, identity)

    return StoryCandidate(
        story_candidate_id=f"S{candidate_index:02d}",
        source_thread_id=thread.thread_id,
        title=thread.title,
        one_line_premise=premise,
        main_characters=main_chars,
        supporting_characters_or_groups=supporting,
        core_conflict=thread.core_conflict,
        arc_summary=arc,
        key_turning_points=turning_points,
        relationship_dynamics=relationships,
        world_pressure_context=pressure_ctx,
        unresolved_question=thread.unresolved_question,
        usable_formats=tuple(hooks.keys()),
        adaptation_hooks=hooks,
        evidence_summary=_evidence_summary(thread, moments_by_id),
        provenance_summary=_provenance_summary(thread, moments_by_id),
        risk_notes=_RISK_NOTES_BASE,
    )


def build_story_candidates(
    threads: list[StoryThread],
    moments: list[Moment],
    identity: IdentityResolver,
) -> list[StoryCandidate]:
    moments_by_id = {m.moment_id: m for m in moments}
    out: list[StoryCandidate] = []
    for i, t in enumerate(threads, start=1):
        out.append(build_story_candidate(
            t, moments_by_id, identity, candidate_index=i,
        ))
    return out


def serialize_candidates(
    candidates: list[StoryCandidate],
    *,
    run_label: str,
    schema_version: str = "story_candidates_v1",
) -> dict:
    by_rank: dict[str, int] = {}
    return {
        "run_label": run_label,
        "schema_version": schema_version,
        "summary": {
            "total": len(candidates),
        },
        "candidates": [c.to_dict() for c in candidates],
    }
