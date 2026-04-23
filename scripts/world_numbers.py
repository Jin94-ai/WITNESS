"""world_numbers.py — canonical numeric snapshot of the World Engine.

Parallel to scripts/paper_numbers.py (which snapshots the Person Engine).
Extracts current Spike 1 + Spike 2 numeric behaviour into a single JSON
so future regressions are detectable and external reviewers have one
authoritative data file.

Sections:
- spike1_world_only: 90-day agent-less full-stack world run (calendar +
  crowd + economy + politics), per-seed + aggregated peaks / troughs.
- spike2_integrated_peter: 90-day Peter 4-agent integrated run, agent +
  world cross-slice summary.
- spike2_judas_removed: same 90-day integrated run minus Judas, for
  counterfactual comparison.

Output: docs/world/paper_data/world_numbers.json
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

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
from world.economy.economy import EconomyLayer  # noqa: E402
from world.environment.calendar import PASSOVER_DAY, SHAVUOT_DAY, CalendarLayer  # noqa: E402
from world.factions.factions import FactionLayer  # noqa: E402
from world.politics.politics import PoliticsLayer  # noqa: E402
from world.simulation.integrated_runner import IntegratedWorldRunner  # noqa: E402
from world.simulation.world_tick import WorldTick  # noqa: E402
from world.social.crowd import CrowdLayer  # noqa: E402
from world.social.rumors import RumorLayer  # noqa: E402

CONTENT = ROOT / "content"
WORLD_CFG_PATH = CONTENT / "worlds" / "jerusalem_ad30" / "world_config.json"
OUT_DIR = ROOT / "docs" / "world" / "paper_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_SEEDS = 5  # small ensemble for the snapshot


def _register_domains() -> None:
    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
    register_domain_type("political_calculation", PoliticalCalculationState)
    register_domain_type("crowd_dynamics", CrowdDynamicsState)


def _world_cfg(seed: int) -> WorldConfig:
    payload = json.loads(WORLD_CFG_PATH.read_text(encoding="utf-8"))
    return replace(WorldConfig.from_json(payload), rng_seed=seed)


def _fresh_runner(seed: int) -> WorldTick:
    return WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        economy_layer=EconomyLayer(),
        politics_layer=PoliticsLayer(),
        faction_layer=FactionLayer(),
        rumor_layer=RumorLayer(),
        config=_world_cfg(seed),
    )


# --------------------------------------------------------------------------
# Spike 1: agent-less world, per-seed ensemble

def spike1_world_only(n_seeds: int = N_SEEDS, n_days: int = 90) -> dict[str, Any]:
    per_seed = []
    for seed in range(n_seeds):
        runner = _fresh_runner(seed)
        state = runner.initial_world_state()
        densities: list[float] = []
        prices: list[float] = []
        alerts: list[float] = []
        overflows: list[float] = []
        # Phase 3B: track zealot militancy trajectory to measure the
        # crowd→militancy threshold brake in aggregate.
        zealot_militancy: list[float] = []
        faction_final: dict[str, float] = {}
        for _ in range(n_days):
            state = runner.tick(state)
            densities.append(state.crowd.crowd_density)
            overflows.append(state.crowd.overflow_pressure)
            prices.append(state.economy.staple_price if state.economy else 0.0)
            alerts.append(state.politics.roman_alertness if state.politics else 0.0)
            if state.factions is not None:
                z = state.factions.get("zealots")
                zealot_militancy.append(z.militancy if z is not None else 0.0)
            else:
                zealot_militancy.append(0.0)
        if state.factions is not None:
            faction_final = {
                fid: round(snap.influence, 3)
                for fid, snap in state.factions.factions.items()
            }

        def _at(seq: list[float], idx: int) -> float:
            return seq[idx] if idx < len(seq) else 0.0

        per_seed.append({
            "seed": seed,
            "max_crowd": max(densities) if densities else 0.0,
            "max_overflow": max(overflows) if overflows else 0.0,
            "max_price": max(prices) if prices else 0.0,
            "max_alert": max(alerts) if alerts else 0.0,
            "passover_crowd": _at(densities, PASSOVER_DAY),
            "shavuot_crowd": _at(densities, SHAVUOT_DAY),
            "day_30_crowd": _at(densities, 30),
            "runaway_ceiling_hits": runner.runaway_detector.report.ceiling_hits,
            "factions_final_influence": faction_final,
            # Phase 3B militancy signature.
            "zealot_militancy_initial": (
                zealot_militancy[0] if zealot_militancy else 0.0
            ),
            "zealot_militancy_max": (
                max(zealot_militancy) if zealot_militancy else 0.0
            ),
            "zealot_militancy_at_passover": _at(zealot_militancy, PASSOVER_DAY),
            "zealot_militancy_day_30": _at(zealot_militancy, 30),
            "militancy_threshold_hits": (
                runner.faction_layer.militancy_threshold_hits
                if runner.faction_layer is not None else 0
            ),
        })
    faction_ids: set[str] = set()
    for s in per_seed:
        faction_ids |= set(s["factions_final_influence"].keys())
    faction_means: dict[str, float] = {}
    for fid in sorted(faction_ids):
        values = [
            s["factions_final_influence"][fid]
            for s in per_seed if fid in s["factions_final_influence"]
        ]
        if values:
            faction_means[fid] = round(statistics.fmean(values), 3)

    return {
        "n_seeds": n_seeds,
        "n_days": n_days,
        "per_seed": per_seed,
        "aggregate": {
            "max_crowd_mean": statistics.fmean(s["max_crowd"] for s in per_seed),
            "max_price_mean": statistics.fmean(s["max_price"] for s in per_seed),
            "max_alert_mean": statistics.fmean(s["max_alert"] for s in per_seed),
            "passover_crowd_mean": statistics.fmean(s["passover_crowd"] for s in per_seed),
            "shavuot_crowd_mean": statistics.fmean(s["shavuot_crowd"] for s in per_seed),
            "faction_influence_mean": faction_means,
            "zealot_militancy_max_mean": round(statistics.fmean(
                s["zealot_militancy_max"] for s in per_seed
            ), 3),
            "zealot_militancy_passover_mean": round(statistics.fmean(
                s["zealot_militancy_at_passover"] for s in per_seed
            ), 3),
            "militancy_threshold_hits_mean": round(statistics.fmean(
                s["militancy_threshold_hits"] for s in per_seed
            ), 2),
        },
    }


# --------------------------------------------------------------------------
# Spike 2 integrated helpers

def _load_profiles(agent_ids: list[str]):
    return {
        aid: load_behavior_profile(CONTENT / aid / "behavior_profile.json")
        for aid in agent_ids
    }


def _make_base_config(agent_ids: list[str]) -> SimulationConfig:
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


def _rule_engine() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(), HomeostasisRule(),
    ])


def _run_integrated(agent_ids: list[str], seed: int, n_days: int = 90):
    world_cfg = _world_cfg(seed)
    # Spike 3 integrated mode: FactionLayer + RumorLayer active so
    # agent-emitted rumor_seed effects route through the world and
    # factions see the post-Passover militancy boost.
    world_tick = WorldTick(
        calendar_layer=CalendarLayer(),
        crowd_layer=CrowdLayer(),
        economy_layer=EconomyLayer(),
        politics_layer=PoliticsLayer(),
        faction_layer=FactionLayer(),
        rumor_layer=RumorLayer(),
        config=world_cfg,
    )
    runner = IntegratedWorldRunner(
        world_tick=world_tick,
        world_config=world_cfg,
        base_config=_make_base_config(agent_ids),
        rule_engine=_rule_engine(),
        behavior_profiles=_load_profiles(agent_ids),
        substeps_per_day=12,
    )
    return runner.run(n_days=n_days, seed=seed)


def _summarise_integrated(agent_ids: list[str], n_seeds: int, label: str) -> dict[str, Any]:
    per_seed = []
    for seed in range(n_seeds):
        result = _run_integrated(agent_ids, seed=seed)
        peter_final = result.final_agent_states.get("peter")
        fear = peter_final.emotions.fear if peter_final else None
        hope = peter_final.emotions.hope if peter_final else None
        judas_final = result.final_agent_states.get("judas")
        disill = (
            getattr(judas_final.domain_state, "disillusionment", None)
            if judas_final else None
        )
        effect_days = sum(
            1 for d in result.days if any(d.aggregated_effects_out.values())
        )
        # Phase 3C rumour metrics from the final world state.
        fw = result.final_world
        rumors_seeded = rumors_expired = rumors_active = 0
        max_intensity = 0.0
        if fw is not None and fw.rumors is not None:
            rumors_seeded = fw.rumors.seeded_total
            rumors_expired = fw.rumors.expired_total
            rumors_active = len(fw.rumors.rumors)
            # Observe max intensity across days to capture peak rumour weight.
            for d in result.days:
                if d.world.rumors is not None:
                    inten = d.world.rumors.active_intensity()
                    if inten > max_intensity:
                        max_intensity = inten
        per_seed.append({
            "seed": seed,
            "peter_final_fear": fear,
            "peter_final_hope": hope,
            "judas_final_disillusionment": disill,
            "total_triggers": len(result.total_triggers),
            "total_hazard_events": len(result.total_events),
            "days_with_effect": effect_days,
            "n_days": result.n_days,
            "rumors_seeded_total": rumors_seeded,
            "rumors_expired_total": rumors_expired,
            "rumors_active_final": rumors_active,
            "rumor_intensity_max": round(max_intensity, 3),
            # Phase 3D signature — track rumour-sensitive (jesus_movement)
            # and non-sensitive (pharisees) factions so the edge effect is
            # directly measurable.
            "jesus_movement_final_influence": (
                round(fw.factions.factions["jesus_movement"].influence, 3)
                if fw is not None and fw.factions is not None
                and "jesus_movement" in fw.factions.factions
                else None
            ),
            "pharisees_final_influence": (
                round(fw.factions.factions["pharisees"].influence, 3)
                if fw is not None and fw.factions is not None
                and "pharisees" in fw.factions.factions
                else None
            ),
        })
    return {
        "label": label,
        "n_seeds": n_seeds,
        "agent_ids": agent_ids,
        "per_seed": per_seed,
        "aggregate": {
            "peter_fear_mean": statistics.fmean(
                s["peter_final_fear"] for s in per_seed if s["peter_final_fear"] is not None
            ),
            "trigger_count_mean": statistics.fmean(
                s["total_triggers"] for s in per_seed
            ),
            "hazard_count_mean": statistics.fmean(
                s["total_hazard_events"] for s in per_seed
            ),
            "effect_days_mean": statistics.fmean(
                s["days_with_effect"] for s in per_seed
            ),
            "rumors_seeded_mean": round(statistics.fmean(
                s["rumors_seeded_total"] for s in per_seed
            ), 2),
            "rumor_intensity_max_mean": round(statistics.fmean(
                s["rumor_intensity_max"] for s in per_seed
            ), 3),
            "jesus_movement_final_influence_mean": _maybe_mean(
                s["jesus_movement_final_influence"] for s in per_seed
            ),
            "pharisees_final_influence_mean": _maybe_mean(
                s["pharisees_final_influence"] for s in per_seed
            ),
        },
    }


def _maybe_mean(values) -> float | None:
    xs = [v for v in values if v is not None]
    if not xs:
        return None
    return round(statistics.fmean(xs), 3)


# --------------------------------------------------------------------------
# Entry point

def main() -> None:
    t0 = time.time()
    _register_domains()
    out: dict[str, Any] = {
        "schema_version": 1,
        "generated_at_seconds": time.time(),
        "notes": (
            "World Engine v2.0 numeric snapshot (Spike 1 + Spike 2). "
            "Person Engine analog is docs/person/paper_data/paper_numbers.json."
        ),
    }
    print("[spike1_world_only] ...")
    out["spike1_world_only"] = spike1_world_only()
    print("[spike2_integrated_peter] ...")
    out["spike2_integrated_peter"] = _summarise_integrated(
        ["peter", "judas", "caiaphas", "crowd"],
        n_seeds=3, label="full_agents",
    )
    print("[spike2_judas_removed] ...")
    out["spike2_judas_removed"] = _summarise_integrated(
        ["peter", "caiaphas", "crowd"],
        n_seeds=3, label="judas_removed",
    )
    out["total_runtime_seconds"] = round(time.time() - t0, 2)

    dest = OUT_DIR / "world_numbers.json"
    dest.write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    print(f"[done] wrote {dest} (total {out['total_runtime_seconds']}s)")


if __name__ == "__main__":
    main()
