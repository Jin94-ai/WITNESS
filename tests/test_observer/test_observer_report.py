"""Tests for scripts.observer.observer_report (Phase O3)."""

from __future__ import annotations

from engine.observer.core import Observer
from engine.observer.snapshot_schema import (
    AgentSnapshot,
    GroupSnapshot,
    Snapshot,
    WorldSnapshot,
)
from scripts.observer.observer_report import (
    format_event_view,
    format_full_report,
    format_group_arc,
    format_group_view,
    format_person_arc,
    format_person_view,
    format_salience_summary,
    format_unstable_agents_summary,
    format_world_trace,
    format_world_view,
)


def _make_stream() -> list[Snapshot]:
    return [
        Snapshot(
            tick=0,
            world=WorldSnapshot(crowd_mood="calm"),
            groups=[GroupSnapshot(id="L1", dominant_mode="low_activity")],
            agents=[AgentSnapshot(id="a1", fear=3.0)],
        ),
        Snapshot(
            tick=1,
            active_events=["public_accusation"],
            world=WorldSnapshot(
                crowd_mood="tense", blame_concentration=0.7
            ),
            groups=[GroupSnapshot(id="L1", dominant_mode="saturation", tension=0.8)],
            agents=[AgentSnapshot(id="a1", fear=7.0, delta=["fear_up"])],
            salience_hints=["pressure_spike"],
        ),
    ]


class TestWorldView:
    def test_format_world_view(self) -> None:
        obs = Observer(_make_stream())
        text = format_world_view(obs, tick=1)
        assert "World View" in text
        assert "tick 1" in text
        assert "긴장" in text  # tense → 긴장
        assert "0.70" in text or "0.7" in text  # blame value
        assert "public_accusation" in text
        assert "pressure_spike" in text

    def test_invalid_tick(self) -> None:
        obs = Observer(_make_stream())
        text = format_world_view(obs, tick=99)
        assert "not in snapshot stream" in text

    def test_world_trace(self) -> None:
        obs = Observer(_make_stream())
        text = format_world_trace(obs)
        assert "World Trace" in text
        assert "tick" in text
        # Both tick rows present
        assert "0" in text and "1" in text


class TestPersonView:
    def test_format_person_view(self) -> None:
        obs = Observer(_make_stream())
        text = format_person_view(obs, "a1", tick=1)
        assert "a1" in text
        assert "Fear" in text
        assert "fear_up" in text  # delta tag visible

    def test_absent_agent(self) -> None:
        obs = Observer(_make_stream())
        text = format_person_view(obs, "ghost", tick=0)
        assert "not present" in text

    def test_person_arc(self) -> None:
        obs = Observer(_make_stream())
        text = format_person_arc(obs, "a1")
        assert "a1" in text
        assert "tick" in text


class TestGroupView:
    def test_format_group_view(self) -> None:
        obs = Observer(_make_stream())
        text = format_group_view(obs, "L1", tick=1)
        assert "L1" in text
        assert "고착" in text  # saturation → 고착

    def test_absent_group(self) -> None:
        obs = Observer(_make_stream())
        text = format_group_view(obs, "L99", tick=0)
        assert "not present" in text

    def test_group_arc(self) -> None:
        obs = Observer(_make_stream())
        text = format_group_arc(obs, "L1")
        assert "L1" in text
        assert "saturation" in text or "low_activity" in text


class TestEventView:
    def test_format_event_view(self) -> None:
        obs = Observer(_make_stream())
        text = format_event_view(obs, "public_accusation")
        assert "public_accusation" in text
        assert "First tick" in text
        assert "1" in text

    def test_event_absent(self) -> None:
        obs = Observer(_make_stream())
        text = format_event_view(obs, "ghost_event")
        assert "not active" in text


class TestSalienceSummary:
    def test_top_salient(self) -> None:
        # Stream that triggers cohort_split + agent_state_shift
        snaps = [
            Snapshot(
                tick=0,
                groups=[
                    GroupSnapshot(id="L1", dominant_mode="saturation"),
                    GroupSnapshot(id="L2", dominant_mode="recovery"),
                ],
                agents=[AgentSnapshot(id="a1", delta=["fear_up"])],
            )
        ]
        obs = Observer(snaps)
        text = format_salience_summary(obs)
        assert "Salient" in text
        assert "cohort_split" in text or "agent_state_shift" in text

    def test_no_salient(self) -> None:
        snaps = [Snapshot(tick=0)]
        obs = Observer(snaps)
        text = format_salience_summary(obs)
        assert "no salient" in text or "Salient" in text


class TestUnstableAgents:
    def test_format(self) -> None:
        snaps = [
            Snapshot(
                tick=0,
                agents=[AgentSnapshot(id="a1", delta=["fear_up"])],
            ),
            Snapshot(
                tick=1,
                agents=[AgentSnapshot(id="a1", delta=["hope_down"])],
            ),
        ]
        obs = Observer(snaps)
        text = format_unstable_agents_summary(obs)
        assert "a1" in text
        assert "shifts=2" in text


class TestFullReport:
    def test_full_report_default_tick(self) -> None:
        obs = Observer(_make_stream())
        text = format_full_report(obs)
        assert "World View" in text
        assert "Salient" in text or "no salient" in text
