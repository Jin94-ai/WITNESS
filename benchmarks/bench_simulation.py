"""Simulation benchmark — 시나리오별 실행 속도/메모리 측정.

Usage:
    python benchmarks/bench_simulation.py              # Peter + VG 둘 다
    python benchmarks/bench_simulation.py --runs 50    # 50회 앙상블
    python benchmarks/bench_simulation.py --scenario peter
    python benchmarks/bench_simulation.py --json output/bench.json

측정 항목 (run 1회 기준):
- total_time_s: 실행 벽시계 시간
- ticks_per_sec: tick/sec throughput
- peak_memory_mb: 피크 메모리 (tracemalloc)
- action_count / trigger_count / event_count
"""

from __future__ import annotations

import argparse
import io
import json
import statistics
import sys
import time
import tracemalloc
from dataclasses import asdict, dataclass
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from content.caiaphas.domain_politics import PoliticalCalculationState  # noqa: E402
from content.crowd.domain_crowd import CrowdDynamicsState  # noqa: E402
from content.gauguin.domain_artistic_ego import ArtisticEgoState  # noqa: E402
from content.judas.domain_betrayal import BetrayalPsychologyState  # noqa: E402
from content.peter.domain_faith import FaithJourneyState  # noqa: E402
from content.theo.domain_patron import PatronState  # noqa: E402
from content.vangogh.domain_creative import CreativeDriveState  # noqa: E402
from engine.core.world import SimulationConfig  # noqa: E402
from engine.io.loader import (  # noqa: E402
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_interventions,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine  # noqa: E402
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule  # noqa: E402
from engine.rules.temporal import HomeostasisRule  # noqa: E402
from engine.simulation.world import SimulationWorld  # noqa: E402

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"


def _register_all() -> None:
    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
    register_domain_type("political_calculation", PoliticalCalculationState)
    register_domain_type("crowd_dynamics", CrowdDynamicsState)
    register_domain_type("creative_drive", CreativeDriveState)
    register_domain_type("artistic_ego", ArtisticEgoState)
    register_domain_type("patron", PatronState)


def _rule_engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


@dataclass
class BenchResult:
    scenario: str
    seed: int
    max_tick: int
    total_time_s: float
    ticks_per_sec: float
    peak_memory_mb: float
    action_count: int
    trigger_count: int
    event_count: int


def _peter_config(max_tick: int) -> tuple[SimulationConfig, dict]:
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT_DIR / "crowd" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
    profiles = {
        "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
        "crowd": load_behavior_profile(CONTENT_DIR / "crowd" / "behavior_profile.json"),
    }
    return SimulationConfig(
        max_tick=max_tick, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    ), profiles


def _vangogh_config(max_tick: int) -> tuple[SimulationConfig, dict]:
    vg = load_agent_state(CONTENT_DIR / "vangogh" / "initial_state.json")
    gauguin = load_agent_state(CONTENT_DIR / "gauguin" / "initial_state.json")
    theo = load_agent_state(CONTENT_DIR / "theo" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "vangogh" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "vangogh" / "hazard_events.json")
    profiles = {
        "vangogh": load_behavior_profile(CONTENT_DIR / "vangogh" / "behavior_profile.json"),
        "gauguin": load_behavior_profile(CONTENT_DIR / "gauguin" / "behavior_profile.json"),
        "theo": load_behavior_profile(CONTENT_DIR / "theo" / "behavior_profile.json"),
    }
    return SimulationConfig(
        max_tick=max_tick, initial_state=vg,
        initial_states=[vg, gauguin, theo],
        hazard_events=hazards, interventions=[],
        triggers=triggers, state_noise_scale=0.05,
    ), profiles


SCENARIOS = {
    "peter": _peter_config,
    "vangogh": _vangogh_config,
}


def run_one(scenario: str, seed: int, max_tick: int) -> BenchResult:
    config_fn = SCENARIOS[scenario]
    config, profiles = config_fn(max_tick)

    tracemalloc.start()
    t0 = time.perf_counter()
    world = SimulationWorld(config, _rule_engine(), behavior_profiles=profiles)
    result = world.run(seed=seed)
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    n_actions = sum(len(h) for h in result.action_histories.values())
    n_triggers = len(result.fired_triggers)
    n_events = len(result.fired_events)

    return BenchResult(
        scenario=scenario, seed=seed, max_tick=max_tick,
        total_time_s=elapsed,
        ticks_per_sec=max_tick / elapsed if elapsed > 0 else 0.0,
        peak_memory_mb=peak / (1024 * 1024),
        action_count=n_actions, trigger_count=n_triggers, event_count=n_events,
    )


def aggregate(results: list[BenchResult]) -> dict:
    if not results:
        return {}
    times = [r.total_time_s for r in results]
    tps = [r.ticks_per_sec for r in results]
    mem = [r.peak_memory_mb for r in results]
    return {
        "n_runs": len(results),
        "scenario": results[0].scenario,
        "max_tick": results[0].max_tick,
        "time_s": {
            "mean": statistics.mean(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
            "min": min(times), "max": max(times),
        },
        "ticks_per_sec": {
            "mean": statistics.mean(tps),
            "stdev": statistics.stdev(tps) if len(tps) > 1 else 0.0,
        },
        "peak_memory_mb": {
            "mean": statistics.mean(mem),
            "max": max(mem),
        },
        "actions_mean": statistics.mean([r.action_count for r in results]),
        "triggers_mean": statistics.mean([r.trigger_count for r in results]),
        "events_mean": statistics.mean([r.event_count for r in results]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Witness simulation benchmark")
    parser.add_argument("--scenario", choices=["peter", "vangogh", "both"], default="both")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--max-tick", type=int, default=250)
    parser.add_argument("--json", type=str, default=None, help="Optional JSON output path")
    args = parser.parse_args()

    _register_all()

    targets = ["peter", "vangogh"] if args.scenario == "both" else [args.scenario]
    all_aggregates = {}
    all_raw: list[dict] = []

    for scenario in targets:
        print(f"\n[{scenario}] running {args.runs} x {args.max_tick} ticks...")
        results = []
        for seed in range(args.runs):
            r = run_one(scenario, seed, args.max_tick)
            results.append(r)
            all_raw.append(asdict(r))
            print(f"  seed={seed:>3}  {r.total_time_s:.2f}s  "
                  f"{r.ticks_per_sec:.0f} tick/s  "
                  f"{r.peak_memory_mb:.1f} MB  "
                  f"A={r.action_count} T={r.trigger_count} E={r.event_count}")
        agg = aggregate(results)
        all_aggregates[scenario] = agg
        print(f"  [{scenario}] time: {agg['time_s']['mean']:.2f}+-{agg['time_s']['stdev']:.2f}s  "
              f"throughput: {agg['ticks_per_sec']['mean']:.0f} tick/s  "
              f"peak mem: {agg['peak_memory_mb']['max']:.1f} MB")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "config": {"runs": args.runs, "max_tick": args.max_tick},
            "aggregates": all_aggregates,
            "raw": all_raw,
        }
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nJSON written: {out}")


if __name__ == "__main__":
    main()
