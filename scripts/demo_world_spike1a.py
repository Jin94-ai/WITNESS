"""demo_world_spike1a.py — 90-day world simulation (WORLD_SPIKE_1A.md).

Runs the Spike 1A two-layer world (calendar + crowd) for 90 days and prints:

- Per-tick day label (hebrew month + day_of_month + active feast).
- crowd_density timeseries.
- Feast-window peak / baseline ratio.
- Shabbat count + spacing check.
- Runaway-detector report.

No agent participation; this is the "agent-less world" sanity test that
WORLD_SPIKE_1A.md success criteria #1-#4 target.

Usage::

    python scripts/demo_world_spike1a.py
    python scripts/demo_world_spike1a.py --seed 7
    python scripts/demo_world_spike1a.py --seeds-flatline 100
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from world.core.world_config import WorldConfig  # noqa: E402
from world.environment.calendar import CalendarLayer  # noqa: E402
from world.simulation.world_tick import WorldTick  # noqa: E402
from world.social.crowd import CrowdLayer  # noqa: E402

WORLD_CONFIG_PATH = (
    ROOT / "content" / "worlds" / "jerusalem_ad30" / "world_config.json"
)


def _load_config(seed: int) -> WorldConfig:
    payload = json.loads(WORLD_CONFIG_PATH.read_text(encoding="utf-8"))
    cfg = WorldConfig.from_json(payload)
    return replace(cfg, rng_seed=seed)


def run_one(seed: int, *, verbose: bool = True) -> dict:
    cfg = _load_config(seed)
    cal = CalendarLayer()
    crowd = CrowdLayer()
    runner = WorldTick(calendar_layer=cal, crowd_layer=crowd, config=cfg)
    state = runner.initial_world_state()

    densities: list[float] = [state.crowd.crowd_density]
    feast_peak_by_name: dict[str, float] = {}
    shabbats: list[int] = []

    for _ in range(cfg.total_ticks):
        state = runner.tick(state)
        densities.append(state.crowd.crowd_density)
        if state.calendar.is_shabbat:
            shabbats.append(state.calendar.day_index)
        feast = state.calendar.active_feast
        if feast != "none":
            feast_peak_by_name[feast] = max(
                feast_peak_by_name.get(feast, 0.0),
                state.crowd.crowd_density,
            )
        if verbose and (
            state.calendar.day_index <= 25
            or abs(state.calendar.day_index - 64) <= 3
        ):
            print(
                f"t={state.calendar.day_index:3d} "
                f"{state.calendar.hebrew_month:>6} "
                f"{state.calendar.day_of_month:2d} "
                f"feast={state.calendar.active_feast:<18} "
                f"shabbat={int(state.calendar.is_shabbat)} "
                f"influx={state.calendar.pilgrim_influx_target:5.2f} "
                f"density={state.crowd.crowd_density:5.2f}"
            )

    baseline = cfg.crowd_config.get("baseline_density", 1.0)
    max_density = max(densities)
    passover_window = densities[10:20]  # days 10-19 (pre-peak through UB)
    shavuot_window = densities[60:70]   # days 60-69 (around Shavuot)

    result = {
        "seed": seed,
        "total_ticks": cfg.total_ticks,
        "baseline_density": baseline,
        "max_density": max_density,
        "max_density_over_baseline": max_density / baseline,
        "passover_peak": max(passover_window),
        "shavuot_peak": max(shavuot_window),
        "post_passover_day30_density": densities[30] if len(densities) > 30 else None,
        "density_stdev": statistics.pstdev(densities),
        "shabbat_count": len(shabbats),
        "shabbat_days": shabbats,
        "feast_peak_by_name": feast_peak_by_name,
        "runaway_report": runner.runaway_detector.report.as_dict(),
        "clamp_hits": crowd.clamp_hits,
    }
    return result


def summarize_flatline(n_seeds: int) -> dict:
    flatlined = 0
    all_stdevs = []
    for s in range(n_seeds):
        r = run_one(s, verbose=False)
        all_stdevs.append(r["density_stdev"])
        # "Flatline" = trivially no variation (stdev < 0.01) OR peak below 1.5x baseline.
        if r["density_stdev"] < 0.01 or r["max_density_over_baseline"] < 1.5:
            flatlined += 1
    return {
        "n_seeds": n_seeds,
        "flatline_count": flatlined,
        "flatline_rate": flatlined / n_seeds if n_seeds else 0.0,
        "stdev_mean": statistics.fmean(all_stdevs) if all_stdevs else 0.0,
        "stdev_min": min(all_stdevs) if all_stdevs else 0.0,
        "stdev_max": max(all_stdevs) if all_stdevs else 0.0,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--seeds-flatline", type=int, default=0,
                   help="If >0, run this many seeds and report flatline rate.")
    args = p.parse_args()

    print(f"== Witness world Spike 1A demo (seed={args.seed}) ==")
    one = run_one(args.seed, verbose=True)
    print()
    print("summary:")
    print(json.dumps(one, indent=2, ensure_ascii=False))

    if args.seeds_flatline > 0:
        print()
        print(f"== Flatline check over {args.seeds_flatline} seeds ==")
        summary = summarize_flatline(args.seeds_flatline)
        print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
