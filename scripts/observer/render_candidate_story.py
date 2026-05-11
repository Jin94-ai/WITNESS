"""World Observer — Candidate-to-Story Render Link (Phase P3).

Per `docs/observer/OBSERVER_TO_STORY_PIPELINE.md` §6.

선택된 candidate를 story renderer로 연결. MVP: light narrative (한국어 prose)
+ detail view (관찰표). 기존 narrative_summary + observer_report 활용.

Out of scope: full IR + render_story_ko (probe-shaped data 입력 필요 — 별도 phase).
"""

from __future__ import annotations

from typing import Literal

from engine.observer.candidate import StoryCandidate
from engine.observer.core import Observer
from scripts.observer.narrative_summary import (
    narrate_event_ripple,
    narrate_person_arc,
    narrate_world_arc,
)
from scripts.observer.observer_report import (
    format_event_view,
    format_person_arc,
    format_world_trace,
    format_world_view,
)

Lens = Literal["person", "event", "world"]


def render_candidate_story(
    candidate: StoryCandidate,
    observer: Observer,
    lens: Lens = "world",
    detail: bool = True,
) -> str:
    """Render candidate as story-ready text in given lens.

    lens=person/event/world. detail=True adds observer_report table view.
    """
    lines = [
        f"=== Story render — {candidate.candidate_id} (lens: {lens}) ===",
        "",
    ]

    if lens == "person":
        if not candidate.agents_involved:
            return "\n".join(lines + ["[Person lens] (인물 정보 없음)"])
        focal_agent = candidate.agents_involved[0]
        # Light narrative
        lines.append("[Narrative]")
        lines.append(narrate_person_arc(
            observer,
            focal_agent,
            tick_from=candidate.tick_range[0],
            tick_to=candidate.tick_range[1],
        ))
        lines.append("")
        if detail:
            lines.append("[Detail — Person Arc Table]")
            lines.append(format_person_arc(
                observer,
                focal_agent,
                tick_from=candidate.tick_range[0],
                tick_to=candidate.tick_range[1],
            ))

    elif lens == "event":
        if not candidate.events_involved:
            return "\n".join(lines + ["[Event lens] (활성 이벤트 없음)"])
        focal_event = candidate.events_involved[0]
        lines.append("[Narrative]")
        lines.append(narrate_event_ripple(observer, focal_event))
        lines.append("")
        if detail:
            lines.append("[Detail — Event View]")
            lines.append(format_event_view(observer, focal_event))

    elif lens == "world":
        lines.append("[Narrative]")
        lines.append(narrate_world_arc(
            observer,
            tick_from=candidate.tick_range[0],
            tick_to=candidate.tick_range[1],
        ))
        lines.append("")
        if detail:
            lines.append("[Detail — World View at peak tick]")
            lines.append(format_world_view(observer, tick=candidate.tick))
            lines.append("")
            lines.append("[Detail — World Trace in candidate window]")
            lines.append(format_world_trace(
                observer,
                tick_from=candidate.tick_range[0],
                tick_to=candidate.tick_range[1],
            ))

    else:
        raise ValueError(f"Unknown lens: {lens}")

    return "\n".join(lines)


def compare_lenses(
    candidate: StoryCandidate, observer: Observer
) -> str:
    """Render same candidate from 3 lenses (person / event / world).

    같은 흐름이 다른 lens에서 어떻게 다르게 읽히는지 비교.
    """
    sections = [
        f"=== Compare lenses — {candidate.candidate_id} ===",
        "",
        "[Person lens]",
        narrate_person_arc(
            observer,
            candidate.agents_involved[0] if candidate.agents_involved else "ghost",
            tick_from=candidate.tick_range[0],
            tick_to=candidate.tick_range[1],
        ),
        "",
        "[Event lens]",
        narrate_event_ripple(
            observer,
            candidate.events_involved[0] if candidate.events_involved else "ghost",
        ),
        "",
        "[World lens]",
        narrate_world_arc(
            observer,
            tick_from=candidate.tick_range[0],
            tick_to=candidate.tick_range[1],
        ),
    ]
    return "\n".join(sections)
