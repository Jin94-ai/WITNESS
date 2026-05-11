"""Tests for scripts.observer.compare_views (Phase O5)."""

from __future__ import annotations

from engine.observer.core import Observer
from engine.observer.snapshot_schema import (
    AgentSnapshot,
    GroupSnapshot,
    Snapshot,
    WorldSnapshot,
)
from scripts.observer.compare_views import (
    compare_seeds,
    format_multi_lens_at_tick,
    format_seed_comparison,
    multi_lens_at_tick,
    stream_summary,
)


def _make_stream(label: str = "default") -> list[Snapshot]:
    """Stream with characteristic peak values per label."""
    if label == "high_blame":
        peak_blame = 0.9
    elif label == "low_blame":
        peak_blame = 0.2
    else:
        peak_blame = 0.5
    return [
        Snapshot(
            tick=0,
            world=WorldSnapshot(crowd_mood="calm", blame_concentration=0.0),
            groups=[GroupSnapshot(id="L1", dominant_mode="low_activity")],
            agents=[AgentSnapshot(id="a1")],
        ),
        Snapshot(
            tick=1,
            active_events=["public_accusation"],
            world=WorldSnapshot(
                crowd_mood="tense", blame_concentration=peak_blame
            ),
            groups=[GroupSnapshot(id="L1", dominant_mode="saturation", tension=0.7)],
            agents=[AgentSnapshot(id="a1", fear=7.0, delta=["fear_up"])],
        ),
        Snapshot(
            tick=2,
            active_events=["public_accusation"],
            world=WorldSnapshot(
                crowd_mood="agitated", blame_concentration=peak_blame
            ),
            groups=[GroupSnapshot(id="L1", dominant_mode="saturation", tension=0.8)],
            agents=[AgentSnapshot(id="a1", fear=8.0)],
        ),
    ]


class TestStreamSummary:
    def test_basic_summary(self) -> None:
        obs = Observer(_make_stream("default"))
        summary = stream_summary(obs)
        assert summary["n_ticks"] == 3
        assert summary["n_agents"] == 1
        assert summary["n_groups"] == 1
        assert summary["peak_blame"] == 0.5
        assert summary["final_crowd_mood"] == "agitated"
        assert "public_accusation" in summary["events_seen"]

    def test_tick_range(self) -> None:
        obs = Observer(_make_stream())
        summary = stream_summary(obs)
        assert summary["tick_range"] == (0, 2)


class TestCompareSeeds:
    def test_two_streams(self) -> None:
        obs1 = Observer(_make_stream("high_blame"))
        obs2 = Observer(_make_stream("low_blame"))
        summaries = compare_seeds({"seed_0": obs1, "seed_1": obs2})
        assert summaries["seed_0"]["peak_blame"] == 0.9
        assert summaries["seed_1"]["peak_blame"] == 0.2

    def test_format_seed_comparison_table(self) -> None:
        obs1 = Observer(_make_stream("high_blame"))
        obs2 = Observer(_make_stream("low_blame"))
        text = format_seed_comparison({"seed_0": obs1, "seed_1": obs2})
        assert "Stream Comparison" in text
        assert "seed_0" in text
        assert "seed_1" in text
        assert "peak_blame" in text
        # Both peak values in output
        assert "0.90" in text
        assert "0.20" in text
        # Disclaimer (관찰기 ≠ 평가기)
        assert "not quality verdict" in text

    def test_empty_streams(self) -> None:
        text = format_seed_comparison({})
        assert "no streams" in text


class TestMultiLensAtTick:
    def test_all_lenses(self) -> None:
        obs = Observer(_make_stream())
        data = multi_lens_at_tick(obs, tick=1)
        assert data["tick"] == 1
        assert data["world"].crowd_mood == "tense"
        assert "public_accusation" in data["active_events"]
        assert "a1" in data["agents"]
        assert "L1" in data["groups"]

    def test_filter_agent_ids(self) -> None:
        obs = Observer(_make_stream())
        data = multi_lens_at_tick(obs, tick=1, agent_ids=["a1"])
        assert "a1" in data["agents"]
        assert len(data["agents"]) == 1

    def test_filter_excludes_unwanted(self) -> None:
        obs = Observer(_make_stream())
        data = multi_lens_at_tick(obs, tick=1, agent_ids=["nonexistent"])
        assert data["agents"] == {}

    def test_format_multi_lens(self) -> None:
        obs = Observer(_make_stream())
        text = format_multi_lens_at_tick(obs, tick=1)
        assert "Multi-lens" in text
        assert "tick 1" in text
        assert "[World]" in text
        assert "[Groups]" in text
        assert "[Agents]" in text
        assert "a1" in text
        assert "L1" in text
