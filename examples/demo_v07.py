"""Witness v0.7 데모: Trace Pipeline + Player View + Drive Hook.

v0.7 신규 infrastructure의 실제 사용 예시:
1. Simulation 실행 (drive_model 주입)
2. TraceEvent 스트림 수집
3. Bifurcation 자동 감지
4. Player 시점 필터링
5. JSONL 덤프

Usage:
    python demo_v07.py              # 기본 (Peter, seed=0)
    python demo_v07.py --player peter --seed 0
    python demo_v07.py --with-drive # IdentityEncoder로 drive 기록
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.gauguin.domain_artistic_ego import ArtisticEgoState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from content.theo.domain_patron import PatronState
from content.vangogh.domain_creative import CreativeDriveState
from engine.core.latent_drive import IdentityEncoder, LatentDriveModel
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_interventions,
    load_triggers,
    register_domain_type,
)
from engine.rendering.player_view import PlayerViewFilterConfig, filter_for_player
from engine.rendering.trace_emitter import collect_trace_events, write_trace_jsonl
from engine.rendering.trace_narrator import render_trace_timeline
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.bifurcation import detect_bifurcation
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)
register_domain_type("creative_drive", CreativeDriveState)
register_domain_type("artistic_ego", ArtisticEgoState)
register_domain_type("patron", PatronState)

CONTENT_DIR = Path(__file__).resolve().parent / "content"


def _rule_engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run_peter(seed: int, max_tick: int = 250, with_drive: bool = False):
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
    config = SimulationConfig(
        max_tick=max_tick, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )
    drive_model = LatentDriveModel(encoder=IdentityEncoder(dim=5)) if with_drive else None
    return SimulationWorld(
        config, _rule_engine(), behavior_profiles=profiles,
        drive_model=drive_model,
    ).run(seed=seed)


def _run_vangogh(seed: int, max_tick: int = 250, with_drive: bool = False):
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
    config = SimulationConfig(
        max_tick=max_tick, initial_state=vg,
        initial_states=[vg, gauguin, theo],
        hazard_events=hazards, interventions=[],
        triggers=triggers, state_noise_scale=0.05,
    )
    drive_model = LatentDriveModel(encoder=IdentityEncoder(dim=5)) if with_drive else None
    return SimulationWorld(
        config, _rule_engine(), behavior_profiles=profiles,
        drive_model=drive_model,
    ).run(seed=seed)


_SCENARIO_AGENTS = {
    "peter": ["peter", "judas", "caiaphas", "crowd"],
    "vangogh": ["vangogh", "gauguin", "theo"],
}

_SCENARIO_BIF_FIELD = {
    "peter": ("judas", "domain_state.disillusionment"),
    "vangogh": ("gauguin", "domain_state.frustration_with_partner"),
}


def _get_nested(obj, dotted: str):
    parts = dotted.split(".")
    cur = obj
    for p in parts:
        cur = getattr(cur, p, None)
        if cur is None:
            return 0.0
    return cur


def main() -> None:
    parser = argparse.ArgumentParser(description="Witness v0.7 trace pipeline demo")
    parser.add_argument("--scenario", default="peter",
                        choices=["peter", "vangogh"])
    parser.add_argument("--player", default=None,
                        help="Agent ID for player view. Defaults to scenario's main character.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-tick", type=int, default=250)
    parser.add_argument("--with-drive", action="store_true",
                        help="Enable IdentityEncoder drive model (plumbing demo)")
    parser.add_argument("--output", type=str, default="output/trace_demo.jsonl",
                        help="JSONL trace output path")
    args = parser.parse_args()

    # Resolve player
    agents = _SCENARIO_AGENTS[args.scenario]
    if args.player is None:
        args.player = agents[0]
    elif args.player not in agents:
        parser.error(f"--player must be one of {agents} for {args.scenario} scenario")

    print("=" * 60)
    print(f"Witness v0.7 Trace Pipeline Demo "
          f"(scenario={args.scenario}, seed={args.seed}, player={args.player})")
    print("=" * 60)

    # 1. Simulation
    print("\n[1/5] Running simulation...")
    runner = _run_peter if args.scenario == "peter" else _run_vangogh
    result = runner(args.seed, args.max_tick, args.with_drive)
    n_actions = sum(len(h) for h in result.action_histories.values())
    n_triggers = len(result.fired_triggers)
    n_events = len(result.fired_events)
    print(f"  • {n_actions} actions, {n_triggers} triggers, {n_events} hazard events")

    # Drive state 요약 (if active)
    if args.with_drive:
        sample_state = result.final_states.get(args.player)
        if sample_state and sample_state.drive_state:
            print(f"  • Final drive_state[{args.player}]: "
                  f"dim={sample_state.drive_state.dim}, "
                  f"values={[f'{v:.2f}' for v in sample_state.drive_state.values]}")

    # 2. Bifurcation detection (driver agent / field per scenario)
    print("\n[2/5] Detecting bifurcation points...")
    bif_agent, bif_field = _SCENARIO_BIF_FIELD[args.scenario]
    snaps = result.state_snapshots.get(bif_agent, {})
    sample_ticks = list(range(0, args.max_tick, 10))
    traj = []
    for t in sample_ticks:
        candidates = [tk for tk in snaps if tk <= t]
        traj.append(_get_nested(snaps[max(candidates)], bif_field) if candidates else 0.0)
    # 단일 run: synthetic ensemble (noise 추가) for 시연
    trajectories_synthetic = [[v + (i * 0.1) for v in traj] for i in range(-2, 3)]
    bif_report = detect_bifurcation(trajectories_synthetic, window_size=3)
    print(f"  • Driver: {bif_agent}.{bif_field}")
    print(f"  • Decision window: ticks {bif_report.decision_window}")
    print(f"  • Max growth std: {bif_report.max_growth_std_value:.3f}")

    # 2b. (v1.1 preview) Scenario-appropriate belief update heuristic
    belief_updates = []
    if args.scenario == "peter":
        judas_actions = result.action_histories.get("judas", [])
        withdraw_seen = 0
        for rec in judas_actions:
            if rec.chosen_action == "withdraw":
                withdraw_seen += 1
                if withdraw_seen % 5 == 0:
                    belief_updates.append({
                        "tick": rec.tick, "observer": "peter", "target": "judas",
                        "trigger": f"observed withdraw x{withdraw_seen}",
                        "belief_change": {
                            "trust": f"~{5.0 - 0.3 * withdraw_seen:.1f}",
                            "loyalty_estimate": "dropping",
                        },
                    })
    else:  # vangogh
        gauguin_actions = result.action_histories.get("gauguin", [])
        critique_seen = 0
        for rec in gauguin_actions:
            if rec.chosen_action == "critique":
                critique_seen += 1
                if critique_seen % 3 == 0:
                    belief_updates.append({
                        "tick": rec.tick, "observer": "vangogh", "target": "gauguin",
                        "trigger": f"observed critique x{critique_seen}",
                        "belief_change": {
                            "artistic_trust": f"~{5.0 - 0.4 * critique_seen:.1f}",
                            "rapport": "eroding",
                        },
                    })
    print(f"  • Generated {len(belief_updates)} belief updates")

    # 3. Trace event collection
    print("\n[3/5] Collecting trace events...")
    all_events = collect_trace_events(
        result,
        bifurcation_reports=[bif_report],
        belief_updates=belief_updates,
    )
    event_types: dict[str, int] = {}
    for ev in all_events:
        event_types[ev.type] = event_types.get(ev.type, 0) + 1
    print(f"  • Total events: {len(all_events)}")
    for t, c in sorted(event_types.items(), key=lambda x: -x[1]):
        print(f"    - {t}: {c}")

    # 4. Player view filter
    print(f"\n[4/5] Filtering from {args.player}'s perspective...")
    cfg = PlayerViewFilterConfig(player_id=args.player)
    filtered = filter_for_player(all_events, cfg)
    filtered_types: dict[str, int] = {}
    for ev in filtered:
        filtered_types[ev.type] = filtered_types.get(ev.type, 0) + 1
    print(f"  • Visible events: {len(filtered)} (of {len(all_events)})")
    for t, c in sorted(filtered_types.items(), key=lambda x: -x[1]):
        print(f"    - {t}: {c}")

    # 5. JSONL dump
    print(f"\n[5/5] Writing JSONL trace to {args.output}...")
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_written = write_trace_jsonl(filtered, str(out_path))
    print(f"  • {n_written} events written")

    # 첫 3 entries 미리보기
    print("\nFirst 3 entries preview:")
    with open(out_path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 3:
                break
            entry = json.loads(line)
            print(f"  tick {entry['tick']:>3} [{entry['type']}] {entry.get('payload', {}) }")

    # 6. Narrative render (v2.0 preview)
    print("\n[Narrative preview — trace_narrator, v2.0 bridge]")
    # skip_repeats로 연속 같은 action 묶음 → 처음 15 entries
    narrative = render_trace_timeline(filtered, skip_repeats=True)
    narrative_lines = narrative.split("\n")
    for line in narrative_lines[:15]:
        print(f"  {line}")
    if len(narrative_lines) > 15:
        print(f"  ... ({len(narrative_lines) - 15} more lines)")

    print("\n" + "=" * 60)
    print("Demo complete. v0.7 pipeline: sim → trace → player_view → JSONL → narrative")
    print("Next: v1.0 learned drive model replaces IdentityEncoder.")
    print("=" * 60)


if __name__ == "__main__":
    main()
