"""World Observer — Story Candidate Extractor (Phase P1).

Per `docs/observer/OBSERVER_TO_STORY_PIPELINE.md` §3-§4.

Observer가 잡은 흐름을 *story candidate*로 변환. *추천*만, *판정* 안 함.

ABSOLUTE Rule #1: no person hardcoding. agent_id는 caller-provided.
ABSOLUTE Rule #6: existing Observer API 무수정 (additive only).

Categories:
    - story (mixed type, top salient overall)
    - world (world-heavy moments)
    - person (person-arc moments)
    - event (event ripple moments)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from engine.observer.core import Observer
from engine.observer.salience import (
    detect_salience_tags,
    top_salient_moments,
    top_unstable_agents,
)

CandidateType = Literal["person", "event", "world", "mixed"]


@dataclass
class StoryCandidate:
    """Story-worthy moment recommendation from Observer.

    *추천*만. Quality verdict 없음.
    """

    candidate_id: str
    source_run: str
    tick: int
    tick_range: tuple[int, int]
    candidate_type: CandidateType

    # Why surfaced — measurable signals
    salience_score: int = 0  # tag count at the tick
    signals: list[str] = field(default_factory=list)  # salience tags + extras

    # World signal at this tick
    dominant_pressure: str = "none_clear"
    crowd_mood: str = "calm"

    # Group / agent involvement
    dominant_mode: str = "low_activity"  # most-saturated group's mode at tick
    agents_involved: list[str] = field(default_factory=list)
    events_involved: list[str] = field(default_factory=list)

    # Notes
    rationale: str = ""


# ============================================================
# Helper: snapshot → tick-level signals
# ============================================================


def _tick_signals(observer: Observer, tick: int) -> dict[str, Any]:
    """Compute per-tick measurable signals for candidate ranking."""
    snap = observer._tick_index[tick]
    snapshots = [observer._tick_index[t] for t in observer.list_ticks()]
    salience_tags = detect_salience_tags(snapshots, tick)

    # World signal strength — max world metric
    world_signal = max(
        snap.world.blame_concentration,
        snap.world.public_suspicion,
        snap.world.authority_vigilance,
        snap.world.scarcity_pressure,
    )

    # Split signal — distinct dominant_modes among groups
    mode_set = {g.dominant_mode for g in snap.groups}
    split_signal = len(mode_set)

    # Event ripple strength
    event_ripple = len(snap.active_events)

    # Person arc movement — number of agents with non-empty delta
    person_arc_movement = sum(1 for a in snap.agents if a.delta)

    # Closure potential — turning point or saturation_lock present
    closure = (
        "recovery_turning_point" in salience_tags
        or "saturation_lock" in salience_tags
    )

    # Dominant mode — most common group mode at tick (tie broken by alphabet)
    if snap.groups:
        mode_counts: dict[str, int] = {}
        for g in snap.groups:
            mode_counts[g.dominant_mode] = mode_counts.get(g.dominant_mode, 0) + 1
        dominant_mode = max(
            mode_counts.items(), key=lambda kv: (kv[1], -ord(kv[0][0]))
        )[0]
    else:
        dominant_mode = "low_activity"

    return {
        "salience_tags": salience_tags,
        "salience_score": len(salience_tags),
        "world_signal": world_signal,
        "split_signal": split_signal,
        "event_ripple": event_ripple,
        "person_arc_movement": person_arc_movement,
        "closure": closure,
        "crowd_mood": snap.world.crowd_mood,
        "dominant_mode": dominant_mode,
        "active_events": list(snap.active_events),
        "agents_present": [a.id for a in snap.agents],
        "agents_with_delta": [a.id for a in snap.agents if a.delta],
    }


def _classify_type(signals: dict[str, Any]) -> CandidateType:
    """Classify candidate type by dominant signal."""
    world_signal = float(signals["world_signal"])
    event_ripple = int(signals["event_ripple"])
    person_arc = int(signals["person_arc_movement"])
    split_signal = int(signals["split_signal"])

    # Priority: split (mixed) > person > event > world
    if split_signal >= 3:
        return "mixed"
    if person_arc >= 2:
        return "person"
    if event_ripple >= 2:
        return "event"
    if world_signal >= 0.4:
        return "world"
    # Fallback: mixed if salience_score >= 2 else person/world by signal
    if int(signals["salience_score"]) >= 2:
        return "mixed"
    return "world" if world_signal > person_arc / 5.0 else "person"


def _build_candidate(
    observer: Observer,
    tick: int,
    source_run: str,
    candidate_id: str,
    tick_range: tuple[int, int] | None = None,
) -> StoryCandidate:
    """Build StoryCandidate from observer + tick."""
    signals = _tick_signals(observer, tick)
    snap = observer._tick_index[tick]

    candidate_type = _classify_type(signals)
    tick_range = tick_range or (max(0, tick - 2), tick + 2)

    # Rationale
    salience_tags = signals["salience_tags"]
    if salience_tags:
        rationale = "Surfaced by " + ", ".join(salience_tags)
    elif float(signals["world_signal"]) > 0.3:
        rationale = f"Surfaced by world signal strength ({signals['world_signal']:.2f})"
    elif int(signals["event_ripple"]) > 1:
        rationale = f"Surfaced by event ripple ({signals['event_ripple']} active events)"
    elif int(signals["split_signal"]) >= 2:
        rationale = f"Surfaced by group divergence ({signals['split_signal']} distinct modes)"
    else:
        rationale = "Surfaced by aggregate signal"

    # Dominant pressure inference (simple — based on active events keywords)
    pressure = "none_clear"
    events_str = " ".join(snap.active_events).lower()
    if "accusation" in events_str:
        pressure = "accusation"
    elif "scarcity" in events_str:
        pressure = "scarcity"
    elif any(k in events_str for k in ["sacred", "miracle", "prayer"]):
        pressure = "sacred"
    elif snap.world.blame_concentration > 0.3:
        pressure = "accusation"  # heuristic
    elif snap.world.scarcity_pressure > 0.3:
        pressure = "scarcity"

    return StoryCandidate(
        candidate_id=candidate_id,
        source_run=source_run,
        tick=tick,
        tick_range=tick_range,
        candidate_type=candidate_type,
        salience_score=int(signals["salience_score"]),
        signals=list(signals["salience_tags"]),
        dominant_pressure=pressure,
        crowd_mood=str(signals["crowd_mood"]),
        dominant_mode=str(signals["dominant_mode"]),
        agents_involved=list(signals["agents_present"]),
        events_involved=list(signals["active_events"]),
        rationale=rationale,
    )


# ============================================================
# Public API — Phase P1 §6.2
# ============================================================


def extract_story_candidates(
    observer: Observer,
    source_run: str = "unknown",
    top_k: int = 5,
) -> list[StoryCandidate]:
    """Top-K story candidates by salience score.

    Mixed criteria — most informative moments overall.
    """
    snapshots = [observer._tick_index[t] for t in observer.list_ticks()]
    moments = top_salient_moments(snapshots, top_n=top_k * 3)  # over-sample then dedupe-ish
    # Use top_k but ensure tick uniqueness
    seen_ticks: set[int] = set()
    candidates: list[StoryCandidate] = []
    for i, m in enumerate(moments):
        if m["tick"] in seen_ticks:
            continue
        seen_ticks.add(m["tick"])
        cid = f"C{i+1:02d}_t{m['tick']}"
        candidates.append(_build_candidate(observer, m["tick"], source_run, cid))
        if len(candidates) >= top_k:
            break
    return candidates


def extract_world_candidates(
    observer: Observer, source_run: str = "unknown", top_k: int = 3
) -> list[StoryCandidate]:
    """Top-K world-heavy candidates — moments where world signal dominates."""
    snapshots = [observer._tick_index[t] for t in observer.list_ticks()]
    scored: list[tuple[int, float]] = []
    for snap in snapshots:
        world_signal = max(
            snap.world.blame_concentration,
            snap.world.public_suspicion,
            snap.world.authority_vigilance,
            snap.world.scarcity_pressure,
        )
        scored.append((snap.tick, world_signal))
    scored.sort(key=lambda kv: (-kv[1], kv[0]))
    candidates: list[StoryCandidate] = []
    for i, (tick, score) in enumerate(scored[:top_k]):
        if score < 0.15:  # below noise threshold
            break
        cid = f"W{i+1:02d}_t{tick}"
        cand = _build_candidate(observer, tick, source_run, cid)
        cand.candidate_type = "world"  # force type — world category
        candidates.append(cand)
    return candidates


def extract_person_candidates(
    observer: Observer, source_run: str = "unknown", top_k: int = 3
) -> list[StoryCandidate]:
    """Top-K person-arc candidates — agents with most state shifts.

    Returns candidates centered on each unstable agent's most-shifted tick.
    """
    snapshots = [observer._tick_index[t] for t in observer.list_ticks()]
    unstable = top_unstable_agents(snapshots, top_n=top_k)
    candidates: list[StoryCandidate] = []
    for i, entry in enumerate(unstable):
        agent_id = str(entry["agent_id"])
        ticks_with_shift: list[int] = list(entry["ticks_with_shift"])  # type: ignore[arg-type]
        if not ticks_with_shift:
            continue
        # Pick middle shift tick
        mid_tick = ticks_with_shift[len(ticks_with_shift) // 2]
        cid = f"P{i+1:02d}_t{mid_tick}_{agent_id}"
        cand = _build_candidate(observer, mid_tick, source_run, cid)
        cand.candidate_type = "person"  # force type
        # Narrow agents_involved to focal agent
        cand.agents_involved = [agent_id]
        candidates.append(cand)
    return candidates


def extract_event_candidates(
    observer: Observer, source_run: str = "unknown", top_k: int = 3
) -> list[StoryCandidate]:
    """Top-K event-ripple candidates — events with longest span × agent involvement."""
    candidates_by_event: list[tuple[str, dict]] = []
    for ev_id in observer.list_events():
        ev_view = observer.get_event_view(ev_id)
        if not ev_view["active_ticks"]:
            continue
        ripple_score = len(ev_view["active_ticks"]) * len(ev_view["agent_ids_present"])
        candidates_by_event.append((ev_id, {"view": ev_view, "score": ripple_score}))

    candidates_by_event.sort(key=lambda kv: -kv[1]["score"])

    candidates: list[StoryCandidate] = []
    for i, (ev_id, info) in enumerate(candidates_by_event[:top_k]):
        ev_view = info["view"]
        first_tick = ev_view["first_tick"]
        last_tick = ev_view["last_tick"]
        # Centered tick of the event span
        center_tick = (first_tick + last_tick) // 2
        cid = f"E{i+1:02d}_t{center_tick}_{ev_id}"
        cand = _build_candidate(
            observer,
            center_tick,
            source_run,
            cid,
            tick_range=(first_tick, last_tick),
        )
        cand.candidate_type = "event"  # force type
        # Focus on this event
        cand.events_involved = [ev_id]
        candidates.append(cand)
    return candidates
