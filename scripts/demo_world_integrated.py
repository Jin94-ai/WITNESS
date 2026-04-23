"""demo_world_integrated.py — Spike 2 B-5: Person × World integrated demo.

Runs the full Jerusalem AD 30 world with 4 agents (peter + judas + caiaphas
+ crowd) for 90 days. Shows side-by-side per-day world state + agent
actions + aggregated WorldEffects so both directions of causation are
visible.

Usage::

    python scripts/demo_world_integrated.py
    python scripts/demo_world_integrated.py --seed 3 --days 45
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
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
from world.economy.economy import EconomyLayer  # noqa: E402
from world.environment.calendar import CalendarLayer  # noqa: E402
from world.factions.factions import FactionLayer  # noqa: E402
from world.politics.politics import PoliticsLayer  # noqa: E402
from world.simulation.integrated_runner import IntegratedWorldRunner  # noqa: E402
from world.simulation.world_tick import WorldTick  # noqa: E402
from world.social.crowd import CrowdLayer  # noqa: E402
from world.social.rumors import RumorLayer  # noqa: E402

CONTENT = ROOT / "content"
WORLD_CONFIG_PATH = CONTENT / "worlds" / "jerusalem_ad30" / "world_config.json"


def _register_domains() -> None:
    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
    register_domain_type("political_calculation", PoliticalCalculationState)
    register_domain_type("crowd_dynamics", CrowdDynamicsState)


def _make_rule_engine() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(), HomeostasisRule(),
    ])


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


def _format_day_row(snap, agent_ids: list[str]) -> list[str]:
    w = snap.world
    lines = []
    price = w.economy.staple_price if w.economy else float("nan")
    alert = w.politics.roman_alertness if w.politics else float("nan")
    pilate = w.politics.pilate_location if w.politics else "?"
    feast_tag = f"[{w.calendar.active_feast.upper()}]" if w.calendar.active_feast != "none" else ""
    header = (
        f"Day {snap.day_index:3d}: "
        f"{w.calendar.hebrew_month:>6} {w.calendar.day_of_month:2d} "
        f"{feast_tag:<22} "
        f"crowd={w.crowd.crowd_density:5.2f} "
        f"price={price:4.2f} "
        f"alert={alert:4.2f} "
        f"pilate={pilate:<9}"
    )
    lines.append(header)

    for aid in agent_ids:
        state = snap.agent_states[aid]
        actions = snap.agent_actions.get(aid, [])
        action_counts = Counter(r.chosen_action for r in actions)
        top_actions = ", ".join(
            f"{name}×{count}" for name, count in action_counts.most_common(3)
        ) or "—"
        lines.append(
            f"  [{aid:<8}] fear={state.emotions.fear:4.2f} "
            f"hope={state.emotions.hope:4.2f} "
            f"grief={state.emotions.grief:4.2f} "
            f"actions: {top_actions}"
        )

    if any(snap.aggregated_effects_out.values()):
        effects_str = ", ".join(
            f"{k}={v:.2f}" for k, v in snap.aggregated_effects_out.items() if v != 0.0
        )
        lines.append(f"  → WorldEffects: {effects_str}")

    return lines


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--days", type=int, default=90)
    p.add_argument("--verbose-days", type=int, default=25,
                   help="Print detailed rows for days 0..VERBOSE-1 + Passover + Shavuot")
    args = p.parse_args()

    _register_domains()
    agent_ids = ["peter", "judas", "caiaphas", "crowd"]
    payload = json.loads(WORLD_CONFIG_PATH.read_text(encoding="utf-8"))
    world_cfg = replace(WorldConfig.from_json(payload), rng_seed=args.seed)
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
        rule_engine=_make_rule_engine(),
        behavior_profiles=_load_profiles(agent_ids),
        substeps_per_day=12,
    )

    print(f"== Witness World - Jerusalem AD 30 (Integrated, seed={args.seed}) ==")
    print(f"Agents: {', '.join(agent_ids)}")
    print()

    result = runner.run(n_days=args.days, seed=args.seed)

    salient_days = set(range(args.verbose_days)) | {13, 14, 15, 20, 30, 63, 64, 65}
    for snap in result.days:
        if snap.day_index in salient_days or snap.aggregated_effects_out.get(
            "publicity_shock", 0.0,
        ):
            for line in _format_day_row(snap, agent_ids):
                try:
                    print(line)
                except UnicodeEncodeError:
                    print(line.encode("ascii", errors="replace").decode("ascii"))

    # Summary.
    peter = result.final_agent_states["peter"]
    judas = result.final_agent_states.get("judas")
    total_trig = len(result.total_triggers)
    total_evt = len(result.total_events)
    any_effect_days = sum(
        1 for d in result.days if any(d.aggregated_effects_out.values())
    )
    print()
    print("== Summary ==")
    print(f"  Peter final fear = {peter.emotions.fear:.3f}, hope = {peter.emotions.hope:.3f}")
    if judas is not None:
        disill = getattr(judas.domain_state, "disillusionment", None)
        print(f"  Judas final disillusionment = {disill}")
    print(f"  Fired triggers over 90 days = {total_trig}")
    print(f"  Fired hazard events over 90 days = {total_evt}")
    print(f"  Days with non-zero WorldEffect = {any_effect_days}/{args.days}")


if __name__ == "__main__":
    main()
