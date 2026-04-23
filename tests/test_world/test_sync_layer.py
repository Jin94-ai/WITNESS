"""Unit tests — SyncLayer bridge (Spike 1D)."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from world.core.world_config import (
    AggregationMode,
    WorldConfig,
    WorldEffect,
    WorldEffectChannel,
)
from world.economy.economy import EconomyLayer
from world.environment.calendar import PASSOVER_DAY, CalendarLayer
from world.politics.politics import PoliticsLayer
from world.simulation.sync_layer import AgentPercept, SyncLayer
from world.simulation.world_tick import WorldTick
from world.social.crowd import CrowdLayer

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT / "content" / "worlds" / "jerusalem_ad30" / "world_config.json"


def _make_cfg(seed: int = 0) -> WorldConfig:
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return replace(WorldConfig.from_json(payload), rng_seed=seed)


def _make_full_runner(seed: int = 0) -> WorldTick:
    cfg = _make_cfg(seed)
    return WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        economy_layer=EconomyLayer(),
        politics_layer=PoliticsLayer(),
        config=cfg,
    )


def test_sync_layer_builds_buffers_from_config() -> None:
    cfg = _make_cfg()
    sync = SyncLayer(cfg, substeps_per_day=12)
    # world_config.json declares 3 channels: publicity_shock, authority_threat, rumor_seed.
    assert {"publicity_shock", "authority_threat", "rumor_seed"} <= set(sync.buffers)


def test_step_without_agents_returns_empty_dict() -> None:
    cfg = _make_cfg()
    sync = SyncLayer(cfg)
    assert sync.step_without_agents() == {}


def test_make_percept_exposes_calendar_and_crowd() -> None:
    runner = _make_full_runner()
    state = runner.initial_world_state()
    state = runner.tick(state)
    sync = SyncLayer(runner.config)
    percept = sync.make_percept(state, day_index=state.calendar.day_index, substep=3)
    assert isinstance(percept, AgentPercept)
    assert percept.world_day_index == state.calendar.day_index
    assert percept.person_substep == 3
    assert percept.local_crowd_density == state.crowd.crowd_density
    assert percept.days_to_next_passover == state.calendar.days_to_next_passover
    assert percept.is_shabbat == state.calendar.is_shabbat


def test_make_percept_normalises_economic_stress_to_unit_interval() -> None:
    """Reviewer #5 — percept values are normalised, not raw world state."""
    runner = _make_full_runner()
    state = runner.initial_world_state()
    for _ in range(20):
        state = runner.tick(state)
    sync = SyncLayer(runner.config)
    percept = sync.make_percept(state, day_index=state.calendar.day_index, substep=0)
    assert 0.0 <= percept.economic_stress <= 1.0
    assert 0.0 <= percept.perceived_authority <= 1.0


def test_make_percept_without_economy_or_politics_yields_zeros() -> None:
    """Spike 1A-only worlds (no economy/politics) still produce valid percepts."""
    cfg = _make_cfg()
    runner = WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        config=cfg,
    )
    state = runner.initial_world_state()
    state = runner.tick(state)
    sync = SyncLayer(cfg)
    percept = sync.make_percept(state, day_index=0, substep=0)
    assert percept.economic_stress == 0.0
    assert percept.perceived_authority == 0.0


def test_submit_effect_respects_channel_aggregation_sum() -> None:
    cfg = _make_cfg()
    sync = SyncLayer(cfg)
    for i in range(3):
        sync.submit_effect(
            WorldEffect(channel_id="authority_threat", value=1.5, origin_agent=f"a{i}"),
        )
    result = sync.drain_aggregated()
    # authority_threat is SUM in world_config.json.
    assert result["authority_threat"] == pytest.approx(4.5)
    # Remaining channels (publicity_shock MAX, rumor_seed THRESHOLD) drain to default 0.0.
    assert result["publicity_shock"] == 0.0
    assert result["rumor_seed"] == 0.0


def test_submit_effect_respects_channel_aggregation_max() -> None:
    cfg = _make_cfg()
    sync = SyncLayer(cfg)
    for v in (0.1, 0.9, 0.3):
        sync.submit_effect(
            WorldEffect(channel_id="publicity_shock", value=v, origin_agent="x"),
        )
    result = sync.drain_aggregated()
    assert result["publicity_shock"] == pytest.approx(0.9)


def test_submit_effect_respects_channel_aggregation_threshold() -> None:
    cfg = _make_cfg()
    sync = SyncLayer(cfg)
    # rumor_seed threshold is 0.5 in world_config.json.
    sync.submit_effect(
        WorldEffect(channel_id="rumor_seed", value=0.2, origin_agent="x"),
    )
    sync.submit_effect(
        WorldEffect(channel_id="rumor_seed", value=0.4, origin_agent="y"),
    )
    assert sync.drain_aggregated()["rumor_seed"] == 0.0  # nobody exceeded

    sync.submit_effect(
        WorldEffect(channel_id="rumor_seed", value=0.6, origin_agent="z"),
    )
    assert sync.drain_aggregated()["rumor_seed"] == 1.0


def test_submit_effect_unknown_channel_silently_dropped() -> None:
    cfg = _make_cfg()
    sync = SyncLayer(cfg)
    # Should not raise; forward-compat for future channels.
    sync.submit_effect(
        WorldEffect(channel_id="nonexistent", value=99.0, origin_agent="x"),
    )
    result = sync.drain_aggregated()
    assert "nonexistent" not in result


def test_aggregation_mode_mean_via_custom_channel() -> None:
    channels = [
        WorldEffectChannel(
            channel_id="mood_delta", aggregation=AggregationMode.MEAN, default=0.0,
        ),
    ]
    cfg = replace(_make_cfg(), effect_channels=channels)
    sync = SyncLayer(cfg)
    for v in (1.0, 2.0, 3.0, 4.0):
        sync.submit_effect(
            WorldEffect(channel_id="mood_delta", value=v, origin_agent="crowd"),
        )
    assert sync.drain_aggregated()["mood_delta"] == pytest.approx(2.5)


def test_drain_clears_buffers() -> None:
    cfg = _make_cfg()
    sync = SyncLayer(cfg)
    sync.submit_effect(
        WorldEffect(channel_id="authority_threat", value=2.0, origin_agent="x"),
    )
    first = sync.drain_aggregated()["authority_threat"]
    second = sync.drain_aggregated()["authority_threat"]
    assert first == 2.0
    assert second == 0.0


def test_integration_with_world_tick_runs_end_to_end() -> None:
    """Full 4-layer world + sync bridge, 90 days, no crash, state is coherent."""
    runner = _make_full_runner()
    sync = SyncLayer(runner.config)
    state = runner.initial_world_state()
    percepts = []
    for _ in range(runner.config.total_ticks):
        aggregated = sync.step_without_agents()
        state = runner.tick(state, aggregated=aggregated)
        percepts.append(sync.make_percept(
            state, day_index=state.calendar.day_index, substep=0,
        ))
    assert state.calendar.day_index == runner.config.total_ticks
    # Passover economic pressure should be materially above baseline.
    passover_percept = percepts[PASSOVER_DAY + 2]
    baseline_percept = percepts[0]
    assert passover_percept.economic_stress > baseline_percept.economic_stress
    assert passover_percept.perceived_authority > baseline_percept.perceived_authority
