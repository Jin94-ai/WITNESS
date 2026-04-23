"""demo_spike4_interventions.py — Spike 4 Phase 4E/F.

Run 3 canonical interventions and dump per-experiment results +
a comparison summary table.

Usage::

    python scripts/demo_spike4_interventions.py
    python scripts/demo_spike4_interventions.py --seeds 3 --days 45
    python scripts/demo_spike4_interventions.py --intervention remove_judas

Each experiment writes to
``docs/world/paper_data/intervention_<id>.json`` and prints a
one-row summary to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from content.caiaphas.domain_politics import PoliticalCalculationState  # noqa: E402
from content.crowd.domain_crowd import CrowdDynamicsState  # noqa: E402
from content.judas.domain_betrayal import BetrayalPsychologyState  # noqa: E402
from content.peter.domain_faith import FaithJourneyState  # noqa: E402
from engine.core.world import SimulationConfig  # noqa: E402
from engine.io.loader import (  # noqa: E402
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine  # noqa: E402
from engine.rules.emotional import (  # noqa: E402
    ConfusionRule,
    FearResponseRule,
    GriefRule,
    HopeRule,
    LoveRule,
)
from engine.rules.temporal import HomeostasisRule  # noqa: E402
from world.core.world_config import WorldConfig  # noqa: E402
from world.intervention.batch import BatchInterventionRunner  # noqa: E402
from world.intervention.spec import InterventionSpec  # noqa: E402

CONTENT = ROOT / "content"
WORLD_CFG_PATH = CONTENT / "worlds" / "jerusalem_ad30" / "world_config.json"
INTERVENTION_DIR = CONTENT / "interventions"
OUT_DIR = ROOT / "docs" / "world" / "paper_data"

DEFAULT_INTERVENTIONS = ["remove_judas", "hazard_half", "lenient_pilate"]


def _register_domains() -> None:
    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
    register_domain_type("political_calculation", PoliticalCalculationState)
    register_domain_type("crowd_dynamics", CrowdDynamicsState)


def _rule_engine() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(), HomeostasisRule(),
    ])


def _profiles(agent_ids: list[str]):
    return {
        aid: load_behavior_profile(CONTENT / aid / "behavior_profile.json")
        for aid in agent_ids
    }


def _sim_config(agent_ids: list[str]) -> SimulationConfig:
    states = [
        load_agent_state(CONTENT / aid / "initial_state.json")
        for aid in agent_ids
    ]
    triggers = load_triggers(CONTENT / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT / "peter" / "hazard_events.json")
    return SimulationConfig(
        initial_state=states[0], initial_states=states,
        triggers=triggers, hazard_events=hazards,
        state_noise_scale=0.02, max_tick=12,
        events=[], interventions=[],
    )


def _world_cfg() -> WorldConfig:
    payload = json.loads(WORLD_CFG_PATH.read_text(encoding="utf-8"))
    return replace(WorldConfig.from_json(payload), rng_seed=0)


def run_intervention(
    intervention_id: str, n_seeds: int, n_days: int,
) -> dict:
    spec = InterventionSpec.load(INTERVENTION_DIR / f"{intervention_id}.json")
    agent_ids = ["peter", "judas", "caiaphas", "crowd"]
    runner = BatchInterventionRunner(
        world_config_base=_world_cfg(),
        sim_config_base=_sim_config(agent_ids),
        rule_engine=_rule_engine(),
        behavior_profiles=_profiles(agent_ids),
    )
    result = runner.run_experiment(spec, n_seeds=n_seeds, n_days=n_days)
    payload = result.as_dict()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = OUT_DIR / f"intervention_{intervention_id}.json"
    dest.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    return payload


def _fmt_cell(v) -> str:
    if v is None:
        return "   -"
    if isinstance(v, float):
        if abs(v) >= 100:
            return f"{v:7.1f}"
        return f"{v:7.2f}"
    return f"{v:>7}"


def _print_comparison_table(results: list[dict]) -> None:
    metrics = [
        ("trigger_count", "triggers"),
        ("hazard_count", "hazards"),
        ("rumors_seeded", "rumours"),
        ("jesus_movement_final_influence", "JM infl"),
        ("pharisees_final_influence", "Phar infl"),
        ("peter_final_fear", "P fear"),
        ("peter_fear_crosses_9_day", "fear→9 day"),
        ("roman_alertness_auc", "alert AUC"),
    ]
    # Header.
    header = (
        f"{'intervention':<22} "
        f"{'metric':<14} "
        f"{'ctrl μ':>8} "
        f"{'intv μ':>8} "
        f"{'Δ mean':>8} "
        f"{'Cohen d':>8} "
        f"{'perm p':>8}"
    )
    print(header)
    print("-" * len(header))
    for payload in results:
        iid = payload["intervention_id"]
        comp = payload["comparison"]
        for key, pretty in metrics:
            entry = comp.get(key)
            if entry is None:
                continue
            print(
                f"{iid:<22} "
                f"{pretty:<14} "
                f"{_fmt_cell(entry['control_mean']):>8} "
                f"{_fmt_cell(entry['intervention_mean']):>8} "
                f"{_fmt_cell(entry['mean_delta']):>8} "
                f"{_fmt_cell(entry['cohens_d']):>8} "
                f"{_fmt_cell(entry['permutation_p_value']):>8}"
            )
        print()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, default=3)
    p.add_argument("--days", type=int, default=45,
                   help="days per run — default kept small for demo speed.")
    p.add_argument("--intervention", default=None,
                   help="Run only this intervention id (omit to run all 3).")
    args = p.parse_args()

    _register_domains()

    ids = [args.intervention] if args.intervention else DEFAULT_INTERVENTIONS
    print(
        f"== Spike 4 intervention demo (n_seeds={args.seeds}, "
        f"n_days={args.days}) =="
    )
    results = []
    for iid in ids:
        print(f"\n[run] {iid} ...")
        payload = run_intervention(iid, args.seeds, args.days)
        results.append(payload)

    print("\n== Comparison summary ==")
    _print_comparison_table(results)
    print(f"[done] per-intervention JSONs in {OUT_DIR}")


if __name__ == "__main__":
    main()
