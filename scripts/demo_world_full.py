"""demo_world_full.py — 4-layer world demo (Spike 1A + 1B + 1C + 1D).

Runs the full agent-less world for 90 days:

- Layer 1 (calendar)   : feast + shabbat + pilgrim influx target.
- Layer 5 (crowd)      : aggregate density driven by Layer 1.
- Layer 2 (economy)    : staple_price driven by Layer 1 (3-day IIR demand).
- Layer 3 (politics)   : roman_alertness driven by Layer 1 + Layer 5 (threshold).
- SyncLayer            : bridge skeleton (empty aggregated_effects — no agents).

Usage::

    python scripts/demo_world_full.py
    python scripts/demo_world_full.py --seed 3
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from world.core.world_config import WorldConfig  # noqa: E402
from world.economy.economy import EconomyLayer  # noqa: E402
from world.environment.calendar import CalendarLayer  # noqa: E402
from world.factions.factions import FactionLayer  # noqa: E402
from world.politics.politics import PoliticsLayer  # noqa: E402
from world.simulation.sync_layer import SyncLayer  # noqa: E402
from world.simulation.world_tick import WorldTick  # noqa: E402
from world.social.crowd import CrowdLayer  # noqa: E402

WORLD_CONFIG_PATH = (
    ROOT / "content" / "worlds" / "jerusalem_ad30" / "world_config.json"
)


def _load(seed: int) -> WorldConfig:
    payload = json.loads(WORLD_CONFIG_PATH.read_text(encoding="utf-8"))
    cfg = WorldConfig.from_json(payload)
    return replace(cfg, rng_seed=seed)


def run(seed: int, *, verbose: bool = True) -> dict:
    cfg = _load(seed)
    runner = WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        economy_layer=EconomyLayer(),
        politics_layer=PoliticsLayer(),
        faction_layer=FactionLayer(),
        config=cfg,
    )
    sync = SyncLayer(cfg, substeps_per_day=12)
    state = runner.initial_world_state()

    trace: list[dict] = []
    for _ in range(cfg.total_ticks):
        # Spike 1D: agent-less bridge — produces empty aggregated_effects.
        aggregated = sync.step_without_agents()
        state = runner.tick(state, aggregated=aggregated)
        fac_row = None
        if state.factions is not None:
            fac_row = {
                fid: round(snap.influence, 3)
                for fid, snap in state.factions.factions.items()
            }
        trace.append({
            "t": state.calendar.day_index,
            "month": state.calendar.hebrew_month,
            "dom": state.calendar.day_of_month,
            "feast": state.calendar.active_feast,
            "is_shabbat": state.calendar.is_shabbat,
            "crowd": round(state.crowd.crowd_density, 3),
            "price": round(state.economy.staple_price, 3) if state.economy else None,
            "alert": round(state.politics.roman_alertness, 3) if state.politics else None,
            "pilate": state.politics.pilate_location if state.politics else None,
            "factions": fac_row,
        })

    if verbose:
        hdr = (
            f"{'t':>3} {'month':>6} {'dom':>3} {'feast':<18} "
            f"{'shab':>5} {'crowd':>6} {'price':>6} {'alert':>6} {'pilate':<10}"
        )
        print(hdr)
        print("-" * len(hdr))
        # Print salient days: Passover approach, UB, Shavuot.
        for row in trace:
            t = row["t"]
            if t <= 25 or 60 <= t <= 75:
                print(
                    f"{t:3d} {row['month']:>6} {row['dom']:3d} "
                    f"{row['feast']:<18} {int(row['is_shabbat']):5d} "
                    f"{row['crowd']:6.2f} {row['price']:6.2f} "
                    f"{row['alert']:6.2f} {row['pilate']:<10}"
                )

    # Summary statistics used by tests / paper.
    prices = [r["price"] for r in trace]
    alerts = [r["alert"] for r in trace]
    crowds = [r["crowd"] for r in trace]
    jerusalem_ticks = sum(1 for r in trace if r["pilate"] == "jerusalem")
    return {
        "seed": seed,
        "total_ticks": cfg.total_ticks,
        "max_crowd": max(crowds),
        "max_price": max(prices),
        "price_at_passover": trace[13]["price"],
        "price_at_day_30": trace[30]["price"],
        "max_alert": max(alerts),
        "alert_at_passover": trace[13]["alert"],
        "alert_at_day_30": trace[30]["alert"],
        "jerusalem_ticks": jerusalem_ticks,
        "runaway_report": runner.runaway_detector.report.as_dict(),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    print(f"== Witness world full demo (seed={args.seed}) ==")
    summary = run(args.seed, verbose=True)
    print()
    print("summary:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
