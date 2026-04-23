"""Success-criteria integration tests (WORLD_SPIKE_1A.md §성공 기준).

All five criteria are turned into pytest assertions so CI can enforce them.

1. Passover window peak ≥ 3x baseline.
2. Post-Passover decline (density < 0.5 x peak by day 30).
3. Shavuot produces a second peak ≥ 3x baseline.
4. Shabbat recurs exactly every 7 days.
5. 100-seed flatline rate < 10%.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import replace
from pathlib import Path

import pytest

from world.core.world_config import WorldConfig
from world.environment.calendar import PASSOVER_DAY, CalendarLayer
from world.simulation.world_tick import WorldTick
from world.social.crowd import CrowdLayer

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT / "content" / "worlds" / "jerusalem_ad30" / "world_config.json"


def _run(seed: int) -> dict:
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cfg = replace(WorldConfig.from_json(payload), rng_seed=seed)
    runner = WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        config=cfg,
    )
    state = runner.initial_world_state()
    densities = [state.crowd.crowd_density]
    shabbat_days = []
    for _ in range(cfg.total_ticks):
        state = runner.tick(state)
        densities.append(state.crowd.crowd_density)
        if state.calendar.is_shabbat:
            shabbat_days.append(state.calendar.day_index)
    return {
        "seed": seed,
        "densities": densities,
        "baseline": state.crowd.baseline_density,
        "shabbat_days": shabbat_days,
        "stdev": statistics.pstdev(densities),
    }


def test_criterion_1_passover_peak_over_3x_baseline() -> None:
    r = _run(seed=0)
    passover_window = r["densities"][PASSOVER_DAY - 3: PASSOVER_DAY + 5]
    assert max(passover_window) >= 3.0 * r["baseline"]


def test_criterion_2_post_passover_decline() -> None:
    r = _run(seed=0)
    passover_window = r["densities"][PASSOVER_DAY - 2: PASSOVER_DAY + 5]
    passover_peak = max(passover_window)
    assert r["densities"][30] < 0.5 * passover_peak


def test_criterion_3_shavuot_second_peak() -> None:
    r = _run(seed=0)
    shavuot_window = r["densities"][60:70]
    peak = max(shavuot_window)
    assert peak >= 3.0 * r["baseline"]


def test_criterion_4_shabbat_every_7_days() -> None:
    r = _run(seed=0)
    shabbats = r["shabbat_days"]
    assert len(shabbats) >= 12  # 90-day window yields ~12-13 shabbats
    diffs = {b - a for a, b in zip(shabbats, shabbats[1:])}
    assert diffs == {7}


@pytest.mark.slow
def test_criterion_5_flatline_rate_under_10_percent() -> None:
    """Running 100 seeds, <10% should be trivial flatlines.

    Marked slow because it runs 100 × 90 = 9,000 ticks. Fast on Spike 1A but
    kept in the slow tier to match the repo's pytest marker convention.
    """
    flatline_count = 0
    stdevs = []
    peaks = []
    for s in range(100):
        r = _run(seed=s)
        stdevs.append(r["stdev"])
        peak = max(r["densities"])
        peaks.append(peak)
        # Trivial flatline: stdev < 0.01 or peak < 1.5 x baseline.
        if r["stdev"] < 0.01 or peak < 1.5 * r["baseline"]:
            flatline_count += 1
    rate = flatline_count / 100.0
    assert rate < 0.10, (
        f"flatline rate {rate:.2%} exceeds 10%. "
        f"stdev_mean={statistics.fmean(stdevs):.3f}, peak_mean={statistics.fmean(peaks):.2f}"
    )


def test_fast_flatline_spotcheck_small_seed_pool() -> None:
    """Fast version of criterion #5 — 10 seeds, <10% flatlines."""
    flatlines = 0
    for s in range(10):
        r = _run(seed=s)
        peak = max(r["densities"])
        if r["stdev"] < 0.01 or peak < 1.5 * r["baseline"]:
            flatlines += 1
    assert flatlines <= 1  # 10% of 10 seeds
