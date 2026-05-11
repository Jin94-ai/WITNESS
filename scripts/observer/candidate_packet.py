"""World Observer — Candidate Packet Builder (Phase P2).

Per `docs/observer/OBSERVER_TO_STORY_PIPELINE.md` §5 + §7.

Story candidate를 사람이 빠르게 읽을 수 있는 packet으로 변환.

원칙: 시스템은 *추천*만, *판정*은 사람에게.

Output formats:
    text — compact 1-page text
    markdown — markdown formatted
    compact — single paragraph summary
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from engine.observer.candidate import StoryCandidate
from engine.observer.core import Observer
from scripts.observer.narrative_summary import (
    narrate_event_ripple,
    narrate_person_arc,
    narrate_world_arc,
)

HumanCheck = Literal["keep", "interesting", "revise_later", "skip"]
UseMode = Literal["story_ready", "observation_only", "low_activity_hold"]


@dataclass
class CandidatePacket:
    """Human-readable packet derived from StoryCandidate.

    Lee directive §7 6-fields format + v2 curation fields (Phase Q3):
    A. Basic / B. Why surfaced / C. Lens summaries / D. Story potential /
    E. Render link / F. Human check (placeholder) /
    G. Curation (use_mode + strongest_lens + related)
    """

    # A. Basic
    candidate_id: str
    source_run: str
    tick: int
    tick_range: tuple[int, int]
    dominant_pressure: str
    dominant_mode: str
    candidate_type: str  # person / event / world / mixed

    # B. Why surfaced
    signals: list[str] = field(default_factory=list)
    rationale: str = ""

    # C. Lens summaries
    person_lens: str = ""
    event_lens: str = ""
    world_lens: str = ""

    # D. Story potential
    potential_arcs: list[str] = field(default_factory=list)
    notes: str = ""

    # E. Render link
    render_recommended: bool = False
    render_lens: str | None = None  # "person" / "event" / "world" / None

    # F. Human check (placeholder — caller fills)
    human_check: HumanCheck | None = None

    # G. Curation (Phase Q3 v2 — None when un-curated)
    use_mode: UseMode | None = None  # story_ready / observation_only / low_activity_hold
    strongest_lens: str | None = None  # person / event / world
    related_candidate_ids: list[str] = field(default_factory=list)


# ============================================================
# Builder
# ============================================================


def _person_lens(candidate: StoryCandidate, observer: Observer) -> str:
    """Per-candidate person-lens summary (2-3 lines)."""
    if not candidate.agents_involved:
        return "(인물 활동 신호 없음)"
    # Pick first agent (or focal if person-type)
    focal_agent = candidate.agents_involved[0]
    arc_text = narrate_person_arc(
        observer,
        focal_agent,
        tick_from=candidate.tick_range[0],
        tick_to=candidate.tick_range[1],
    )
    return arc_text


def _event_lens(candidate: StoryCandidate, observer: Observer) -> str:
    """Per-candidate event-lens summary."""
    if not candidate.events_involved:
        return "(활성 이벤트 없음)"
    focal_event = candidate.events_involved[0]
    return narrate_event_ripple(observer, focal_event)


def _world_lens(candidate: StoryCandidate, observer: Observer) -> str:
    """Per-candidate world-lens summary (in candidate tick range window)."""
    return narrate_world_arc(
        observer,
        tick_from=candidate.tick_range[0],
        tick_to=candidate.tick_range[1],
    )


def _potential_arcs(candidate: StoryCandidate) -> list[str]:
    """Which lens directions this candidate suggests.

    Values follow Lee directive `WITNESS_CANDIDATE_CURATION_AND_NEXT_STEPS.md`
    §3.4 verbatim: person_arc / event_arc / world_arc / mixed_arc.
    """
    arcs: list[str] = []
    if candidate.agents_involved:
        arcs.append("person_arc")
    if candidate.events_involved:
        arcs.append("event_arc")
    # World lens always available (world-level state always present)
    arcs.append("world_arc")
    # mixed_arc when multiple lens directions co-active
    if candidate.candidate_type == "mixed":
        arcs.append("mixed_arc")
    return arcs


def _notes(candidate: StoryCandidate) -> str:
    """Note on candidate strength + use hint."""
    if candidate.salience_score >= 3:
        base = "strong candidate"
    elif candidate.salience_score >= 2:
        base = "candidate"
    else:
        base = "weak signal"

    if candidate.candidate_type == "person":
        return f"{base} — person arc 후보 (focal agent 흔들림)"
    if candidate.candidate_type == "event":
        return f"{base} — event ripple 후보"
    if candidate.candidate_type == "world":
        return f"{base} — world-level 후보 (개인보다 세계 흐름 강함)"
    if candidate.candidate_type == "mixed":
        return f"{base} — mixed 후보 (cohort split / 다중 신호)"
    return base


def _render_recommendation(candidate: StoryCandidate) -> tuple[bool, str | None]:
    """Render link decision — recommended? which lens?"""
    # Recommend render if salience_score >= 2 (multiple signals)
    if candidate.salience_score < 2:
        return False, None
    # Lens choice: candidate_type → matching lens
    type_to_lens = {
        "person": "person",
        "event": "event",
        "world": "world",
        "mixed": "world",  # mixed → world (cohort overview)
    }
    return True, type_to_lens.get(candidate.candidate_type, "world")


def build_packet(
    candidate: StoryCandidate, observer: Observer
) -> CandidatePacket:
    """Build CandidatePacket from candidate + observer.

    Curation fields (use_mode / strongest_lens / related_candidate_ids) are
    None unless `build_curated_packet` is used or fields are filled by caller.
    """
    person_lens = _person_lens(candidate, observer)
    event_lens = _event_lens(candidate, observer)
    world_lens = _world_lens(candidate, observer)
    potential_arcs = _potential_arcs(candidate)
    notes = _notes(candidate)
    render_recommended, render_lens = _render_recommendation(candidate)

    return CandidatePacket(
        candidate_id=candidate.candidate_id,
        source_run=candidate.source_run,
        tick=candidate.tick,
        tick_range=candidate.tick_range,
        dominant_pressure=candidate.dominant_pressure,
        dominant_mode=candidate.dominant_mode,
        candidate_type=candidate.candidate_type,
        signals=list(candidate.signals),
        rationale=candidate.rationale,
        person_lens=person_lens,
        event_lens=event_lens,
        world_lens=world_lens,
        potential_arcs=potential_arcs,
        notes=notes,
        render_recommended=render_recommended,
        render_lens=render_lens,
        human_check=None,  # caller fills
    )


def build_curated_packet(
    curated: "CuratedCandidate", observer: Observer  # noqa: F821 — forward ref
) -> CandidatePacket:
    """Build CandidatePacket from CuratedCandidate (Phase Q3).

    Adds curation metadata (use_mode / strongest_lens / related) to base packet.
    """
    packet = build_packet(curated.candidate, observer)
    packet.use_mode = curated.use_mode
    packet.strongest_lens = curated.strongest_lens
    packet.related_candidate_ids = list(curated.related_candidate_ids)
    return packet


# ============================================================
# Format functions
# ============================================================


def format_packet_text(packet: CandidatePacket) -> str:
    """Plain-text packet (compact 1-page)."""
    lines = [
        f"=== Candidate {packet.candidate_id} ===",
        f"Source: {packet.source_run} (tick {packet.tick}, range {packet.tick_range[0]}-{packet.tick_range[1]})",
        f"Type: {packet.candidate_type}  |  Pressure: {packet.dominant_pressure}  |  Mode: {packet.dominant_mode}",
        "",
        "[Why surfaced]",
        f"  {packet.rationale}",
        f"  Signals: {', '.join(packet.signals) if packet.signals else '(none)'}",
        "",
        "[Person lens]",
        f"  {packet.person_lens}",
        "",
        "[Event lens]",
        f"  {packet.event_lens}",
        "",
        "[World lens]",
        f"  {packet.world_lens}",
        "",
        "[Story potential]",
        f"  Arcs: {', '.join(packet.potential_arcs)}",
        f"  Notes: {packet.notes}",
        "",
    ]
    # Curation block (Phase Q3 v2) — present only when curated
    if packet.use_mode is not None:
        lines.extend([
            "[Use mode]",
            f"  {packet.use_mode}",
            "",
            "[Strongest lens]",
            f"  {packet.strongest_lens}",
            "",
        ])
        if packet.related_candidate_ids:
            lines.extend([
                "[Related candidates] (near-duplicate, 접힘)",
                f"  {', '.join(packet.related_candidate_ids)}",
                "",
            ])
    lines.append("[Render link]")
    if packet.render_recommended:
        lines.append(f"  Recommended: yes (lens = {packet.render_lens})")
    else:
        lines.append("  Recommended: no")
    lines.extend([
        "",
        "[Human check] (caller fills)",
        "  ☐ keep   ☐ interesting   ☐ revise_later   ☐ skip",
    ])
    return "\n".join(lines)


def format_packet_markdown(packet: CandidatePacket) -> str:
    """Markdown-formatted packet."""
    lines = [
        f"## Candidate `{packet.candidate_id}`",
        "",
        f"**Source**: `{packet.source_run}` (tick {packet.tick}, range {packet.tick_range[0]}–{packet.tick_range[1]})",
        (
            f"**Type**: `{packet.candidate_type}` · "
            f"**Pressure**: `{packet.dominant_pressure}` · "
            f"**Mode**: `{packet.dominant_mode}`"
        ),
        "",
        "### Why surfaced",
        f"- Rationale: {packet.rationale}",
        f"- Signals: `{', '.join(packet.signals) if packet.signals else '(none)'}`",
        "",
        "### Person lens",
        f"> {packet.person_lens}",
        "",
        "### Event lens",
        f"> {packet.event_lens}",
        "",
        "### World lens",
        f"> {packet.world_lens}",
        "",
        "### Story potential",
        f"- Arcs: {', '.join(packet.potential_arcs)}",
        f"- Notes: {packet.notes}",
        "",
    ]
    if packet.use_mode is not None:
        lines.extend([
            "### Curation",
            f"- Use mode: `{packet.use_mode}`",
            f"- Strongest lens: `{packet.strongest_lens}`",
        ])
        if packet.related_candidate_ids:
            lines.append(
                f"- Related (near-duplicate, 접힘): "
                f"{', '.join(f'`{rid}`' for rid in packet.related_candidate_ids)}"
            )
        lines.append("")
    lines.append("### Render link")
    if packet.render_recommended:
        lines.append(f"- Recommended: ✅ (lens = `{packet.render_lens}`)")
    else:
        lines.append("- Recommended: ❌")
    lines.extend([
        "",
        "### Human check",
        "- [ ] keep",
        "- [ ] interesting",
        "- [ ] revise_later",
        "- [ ] skip",
    ])
    return "\n".join(lines)


def format_packet_compact(packet: CandidatePacket) -> str:
    """Single paragraph summary — 한 줄 요약."""
    parts = [
        f"[{packet.candidate_id}]",
        f"tick {packet.tick} ({packet.candidate_type})",
        f"signals={', '.join(packet.signals) or 'none'}",
        f"pressure={packet.dominant_pressure}",
        f"mode={packet.dominant_mode}",
    ]
    if packet.use_mode is not None:
        parts.append(f"use={packet.use_mode}")
        parts.append(f"lens={packet.strongest_lens}")
        if packet.related_candidate_ids:
            parts.append(f"+{len(packet.related_candidate_ids)} related")
    elif packet.render_recommended:
        parts.append(f"render→{packet.render_lens}")
    return " | ".join(parts)
