"""World Observer — Candidate Curation (Phase Q1).

Per `docs/observer/CANDIDATE_CURATION_PLAN.md` + Lee directive
`WITNESS_CANDIDATE_CURATION_AND_NEXT_STEPS.md`.

Raw StoryCandidate를 *분류*: story_ready / observation_only / low_activity_hold.

원칙:
    - 시스템은 *분류*만, *quality verdict* 아님
    - 새 scoring system 크게 만들지 않음 — *얇은 2차 필터*
    - candidate 버리지 않음, *어떻게 쓸지* 분리

Curation pipeline:
    1. near_duplicate_reduce — 비슷한 인접 candidate 군집화
    2. assign_use_mode — 3 bucket 분류
    3. temporal_diversity — story_ready bucket 내 min tick gap 적용

ABSOLUTE Rule #1: no person hardcoding.
ABSOLUTE Rule #6: existing candidate.py API 무수정 (additive only).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from engine.observer.candidate import StoryCandidate
from engine.observer.core import Observer

UseMode = Literal["story_ready", "observation_only", "low_activity_hold"]
StrongestLens = Literal["person", "event", "world"]


# ============================================================
# Curated dataclasses
# ============================================================


@dataclass
class CuratedCandidate:
    """Wrapper over StoryCandidate with curation metadata.

    Original candidate preserved as-is. Curation = thin overlay.
    """

    candidate: StoryCandidate
    use_mode: UseMode
    strongest_lens: StrongestLens
    related_candidate_ids: list[str] = field(default_factory=list)


@dataclass
class CuratedSet:
    """Three buckets — story_ready / observation_only / low_activity_hold."""

    story_ready: list[CuratedCandidate] = field(default_factory=list)
    observation_only: list[CuratedCandidate] = field(default_factory=list)
    low_activity_hold: list[CuratedCandidate] = field(default_factory=list)

    def total_count(self) -> int:
        return (
            len(self.story_ready)
            + len(self.observation_only)
            + len(self.low_activity_hold)
        )


# ============================================================
# Lens substance check
# ============================================================


def _has_person_substance(candidate: StoryCandidate, observer: Observer) -> bool:
    """Person lens has material if any agent shows non-trivial state delta."""
    snap = observer._tick_index.get(candidate.tick)
    if snap is None:
        return False
    # Need at least one agent with delta — i.e. visible state movement
    return any(a.delta for a in snap.agents)


def _has_event_substance(candidate: StoryCandidate, observer: Observer) -> bool:
    """Event lens has material if a multi-tick event ripple exists.

    Single-tick blip is *observation*, not *story-ready*.
    """
    if not candidate.events_involved:
        return False
    # Look across the candidate's tick_range — check if any event spans 2+ ticks
    t_from, t_to = candidate.tick_range
    span_counts: dict[str, int] = {}
    for t in range(t_from, t_to + 1):
        snap = observer._tick_index.get(t)
        if snap is None:
            continue
        for ev in snap.active_events:
            span_counts[ev] = span_counts.get(ev, 0) + 1
    return any(count >= 2 for count in span_counts.values())


def _has_world_substance(candidate: StoryCandidate, observer: Observer) -> bool:
    """World lens has material if any major metric exceeds threshold."""
    snap = observer._tick_index.get(candidate.tick)
    if snap is None:
        return False
    return any(
        [
            snap.world.blame_concentration > 0.3,
            snap.world.scarcity_pressure > 0.3,
            snap.world.public_suspicion > 0.3,
            snap.world.authority_vigilance > 0.3,
        ]
    )


def pick_strongest_lens(
    candidate: StoryCandidate, observer: Observer
) -> StrongestLens:
    """Pick the lens with most material. Heuristic, not ranking.

    Priority by candidate_type, fallback to substance availability.
    """
    type_to_lens: dict[str, StrongestLens] = {
        "person": "person",
        "event": "event",
        "world": "world",
    }
    if candidate.candidate_type in type_to_lens:
        return type_to_lens[candidate.candidate_type]
    # mixed: pick by which lens has substance, prefer world (cohort overview)
    if _has_world_substance(candidate, observer):
        return "world"
    if _has_event_substance(candidate, observer):
        return "event"
    if _has_person_substance(candidate, observer):
        return "person"
    return "world"  # fallback


# ============================================================
# Use mode assignment
# ============================================================


def assign_use_mode(candidate: StoryCandidate, observer: Observer) -> UseMode:
    """Assign 3-bucket use mode.

    Decision tree:
        1. low_activity_hold: dominant_mode == low_activity AND salience_score <= 1
        2. story_ready: strongest lens has substance AND salience_score >= 2
        3. observation_only: otherwise (signal exists but lens not substantial)
    """
    # low_activity_hold — weakly active, hold for tension seed exploration
    if (
        candidate.dominant_mode == "low_activity"
        and candidate.salience_score <= 1
    ):
        return "low_activity_hold"

    # Check if strongest lens has substance
    strongest = pick_strongest_lens(candidate, observer)
    substance_check = {
        "person": _has_person_substance,
        "event": _has_event_substance,
        "world": _has_world_substance,
    }
    has_substance = substance_check[strongest](candidate, observer)

    # story_ready: substance + meaningful signal count
    if has_substance and candidate.salience_score >= 2:
        return "story_ready"

    return "observation_only"


# ============================================================
# Temporal diversity filter
# ============================================================


def temporal_diversity_filter(
    candidates: list[StoryCandidate], min_gap: int = 5
) -> list[StoryCandidate]:
    """Greedy filter — keep only candidates separated by min_gap ticks.

    Greedy by salience_score (desc): higher-scored candidates picked first.
    Tie-broken by candidate_id for determinism.

    Returns same-type candidates with min tick gap satisfied.
    """
    if min_gap <= 0:
        return list(candidates)

    sorted_c = sorted(
        candidates,
        key=lambda c: (-c.salience_score, c.candidate_id),
    )
    kept: list[StoryCandidate] = []
    for c in sorted_c:
        if all(abs(c.tick - k.tick) >= min_gap for k in kept):
            kept.append(c)
    return kept


# ============================================================
# Near-duplicate reduction
# ============================================================


def _signals_similar(
    sig_a: list[str], sig_b: list[str], min_overlap: float = 0.5
) -> bool:
    """Two signal sets are similar if Jaccard overlap >= min_overlap."""
    if not sig_a and not sig_b:
        return True
    set_a, set_b = set(sig_a), set(sig_b)
    if not set_a or not set_b:
        return False
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union >= min_overlap


def near_duplicate_reduce(
    candidates: list[StoryCandidate],
    tick_window: int = 3,
    signal_overlap: float = 0.5,
) -> list[tuple[StoryCandidate, list[str]]]:
    """Group candidates that are temporally close + signal-similar.

    Args:
        candidates: input candidates
        tick_window: max tick gap for near-duplicate
        signal_overlap: min Jaccard overlap of signal sets

    Returns:
        list of (representative, related_candidate_ids).
        Representative = highest salience_score in group.
    """
    if not candidates:
        return []

    # Sort by tick for sequential grouping
    by_tick = sorted(candidates, key=lambda c: (c.tick, c.candidate_id))
    groups: list[list[StoryCandidate]] = []
    current: list[StoryCandidate] = []

    for c in by_tick:
        if not current:
            current = [c]
            continue
        last = current[-1]
        # Group if: tick gap small AND same candidate_type AND signals similar
        is_near = (
            c.tick - last.tick <= tick_window
            and c.candidate_type == last.candidate_type
            and _signals_similar(c.signals, last.signals, signal_overlap)
        )
        if is_near:
            current.append(c)
        else:
            groups.append(current)
            current = [c]
    if current:
        groups.append(current)

    # Pick representative + collect related IDs
    result: list[tuple[StoryCandidate, list[str]]] = []
    for g in groups:
        rep = max(g, key=lambda c: (c.salience_score, c.candidate_id))
        related = [c.candidate_id for c in g if c.candidate_id != rep.candidate_id]
        result.append((rep, related))
    return result


# ============================================================
# Curation pipeline
# ============================================================


def curate_candidates(
    candidates: list[StoryCandidate],
    observer: Observer,
    min_tick_gap: int = 5,
    near_dup_window: int = 3,
    near_dup_signal_overlap: float = 0.5,
) -> CuratedSet:
    """Apply curation pipeline: near-dup → bucket → temporal diversity.

    Steps:
        1. near_duplicate_reduce — group similar adjacent candidates
        2. assign_use_mode + pick_strongest_lens for each representative
        3. temporal_diversity_filter on story_ready bucket only

    Returns CuratedSet with 3 buckets.
    """
    # Step 1: near-dup reduce
    reduced = near_duplicate_reduce(
        candidates,
        tick_window=near_dup_window,
        signal_overlap=near_dup_signal_overlap,
    )

    # Step 2: bucket assign
    buckets: dict[UseMode, list[CuratedCandidate]] = {
        "story_ready": [],
        "observation_only": [],
        "low_activity_hold": [],
    }
    for rep, related_ids in reduced:
        use_mode = assign_use_mode(rep, observer)
        strongest = pick_strongest_lens(rep, observer)
        cc = CuratedCandidate(
            candidate=rep,
            use_mode=use_mode,
            strongest_lens=strongest,
            related_candidate_ids=related_ids,
        )
        buckets[use_mode].append(cc)

    # Step 3: temporal diversity within story_ready
    if min_tick_gap > 0 and buckets["story_ready"]:
        sr_raw = [cc.candidate for cc in buckets["story_ready"]]
        kept_raw = temporal_diversity_filter(sr_raw, min_gap=min_tick_gap)
        kept_ids = {c.candidate_id for c in kept_raw}
        # Demoted (gap-violating) candidates → observation_only
        demoted = [
            cc for cc in buckets["story_ready"]
            if cc.candidate.candidate_id not in kept_ids
        ]
        buckets["story_ready"] = [
            cc for cc in buckets["story_ready"]
            if cc.candidate.candidate_id in kept_ids
        ]
        for cc in demoted:
            cc.use_mode = "observation_only"
            buckets["observation_only"].append(cc)

    return CuratedSet(
        story_ready=buckets["story_ready"],
        observation_only=buckets["observation_only"],
        low_activity_hold=buckets["low_activity_hold"],
    )
