"""Tests for scripts.observer.narrative_summary (Phase O7)."""

from __future__ import annotations

from engine.observer.core import Observer
from engine.observer.snapshot_schema import (
    AgentSnapshot,
    Snapshot,
    WorldSnapshot,
)
from scripts.observer.narrative_summary import (
    narrate_event_ripple,
    narrate_person_arc,
    narrate_seed_comparison,
    narrate_world_arc,
)


def _make_stream() -> list[Snapshot]:
    """3-tick stream: calm → tense → agitated."""
    return [
        Snapshot(
            tick=0,
            world=WorldSnapshot(crowd_mood="calm"),
            agents=[AgentSnapshot(id="a1", role="follower", fear=2.0, hope=5.0)],
        ),
        Snapshot(
            tick=1,
            active_events=["public_accusation"],
            world=WorldSnapshot(crowd_mood="tense", blame_concentration=0.5),
            agents=[
                AgentSnapshot(id="a1", role="follower", fear=5.0, delta=["fear_up"])
            ],
        ),
        Snapshot(
            tick=2,
            active_events=["public_accusation"],
            world=WorldSnapshot(crowd_mood="agitated", blame_concentration=0.8),
            agents=[AgentSnapshot(id="a1", role="follower", fear=8.0)],
        ),
    ]


class TestNarrateWorldArc:
    def test_basic_world_arc(self) -> None:
        obs = Observer(_make_stream())
        text = narrate_world_arc(obs)
        assert "tick 0부터 2" in text
        assert "고요" in text  # calm
        assert "동요" in text  # agitated
        assert "비난" in text or "의심" in text  # metric mention

    def test_empty_window(self) -> None:
        obs = Observer(_make_stream())
        # Window outside stream
        text = narrate_world_arc(obs, tick_from=100, tick_to=200)
        assert "관찰 가능한 tick이 없다" in text

    def test_active_events_mentioned(self) -> None:
        obs = Observer(_make_stream())
        text = narrate_world_arc(obs)
        assert "public_accusation" in text


class TestNarratePersonArc:
    def test_basic_person_arc(self) -> None:
        obs = Observer(_make_stream())
        text = narrate_person_arc(obs, "a1")
        assert "a1" in text
        assert "follower" in text
        assert "두려움" in text  # fear changed +6 → biggest delta

    def test_absent_agent(self) -> None:
        obs = Observer(_make_stream())
        text = narrate_person_arc(obs, "ghost")
        assert "이 구간에 등장하지 않는다" in text

    def test_delta_count_mentioned(self) -> None:
        obs = Observer(_make_stream())
        text = narrate_person_arc(obs, "a1")
        # tick 1 has fear_up delta — text should mention 1 delta tick
        assert "변화" in text


class TestNarrateEventRipple:
    def test_event_ripple_two_ticks(self) -> None:
        obs = Observer(_make_stream())
        text = narrate_event_ripple(obs, "public_accusation")
        assert "public_accusation" in text
        assert "tick 1" in text and "2" in text
        assert "총 2개 tick" in text

    def test_event_absent(self) -> None:
        obs = Observer(_make_stream())
        text = narrate_event_ripple(obs, "ghost_event")
        assert "어떤 tick에서도 활성화되지 않았다" in text

    def test_single_tick_event(self) -> None:
        snaps = [
            Snapshot(tick=0),
            Snapshot(tick=1, active_events=["one_off"]),
            Snapshot(tick=2),
        ]
        obs = Observer(snaps)
        text = narrate_event_ripple(obs, "one_off")
        assert "단발적으로 활성" in text


class TestNarrateSeedComparison:
    def test_two_streams(self) -> None:
        obs1 = Observer(_make_stream())
        # Build different stream
        snaps2 = [
            Snapshot(tick=0, world=WorldSnapshot(crowd_mood="calm")),
            Snapshot(
                tick=1, world=WorldSnapshot(crowd_mood="calm", blame_concentration=0.1)
            ),
            Snapshot(
                tick=2, world=WorldSnapshot(crowd_mood="calm", blame_concentration=0.2)
            ),
        ]
        obs2 = Observer(snaps2)
        text = narrate_seed_comparison({"hot": obs1, "calm": obs2})
        assert "2개 stream" in text
        assert "비난" in text
        # peak_blame: hot=0.8, calm=0.2 — different
        assert "0.20" in text or "0.80" in text or "0.2" in text or "0.8" in text

    def test_empty_streams(self) -> None:
        text = narrate_seed_comparison({})
        assert "제공되지 않았다" in text

    def test_single_stream_warning(self) -> None:
        obs = Observer(_make_stream())
        text = narrate_seed_comparison({"only": obs})
        assert "비교가 의미 없다" in text or "단일" in text

    def test_disclaimer_present(self) -> None:
        # Comparison should disclaim non-evaluative
        obs1 = Observer(_make_stream())
        snaps2 = [Snapshot(tick=0), Snapshot(tick=1), Snapshot(tick=2)]
        obs2 = Observer(snaps2)
        text = narrate_seed_comparison({"a": obs1, "b": obs2})
        assert "평가 아님" in text or "어느" in text  # disclaimer wording

    def test_diverging_final_moods(self) -> None:
        obs1 = Observer(_make_stream())  # final mood = agitated
        snaps2 = [
            Snapshot(tick=0, world=WorldSnapshot(crowd_mood="calm")),
            Snapshot(tick=1, world=WorldSnapshot(crowd_mood="calm")),
            Snapshot(tick=2, world=WorldSnapshot(crowd_mood="calm")),
        ]
        obs2 = Observer(snaps2)
        text = narrate_seed_comparison({"hot": obs1, "calm": obs2})
        assert "갈렸다" in text or "동일" in text  # mood diversity mention
