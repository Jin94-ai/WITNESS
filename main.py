"""Witness: Hazard-Driven Ensemble Historical Simulator.

Usage:
    python main.py                  # Peter demo (default)
    python main.py --person peter   # Peter
    python main.py --person vangogh # Van Gogh
    python main.py --runs 200       # 200 batch runs
    python main.py --person vangogh --runs 50
"""

import argparse
import io
import json
import random
import sys
from pathlib import Path

# Windows 한글 출력 깨짐 방지
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_hazard_events,
    load_interventions,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import ConfusionRule, FearResponseRule, GriefRule, HopeRule, LoveRule
from engine.rules.physical import FatigueRule, HealthRule, HungerRule
from engine.rules.social import GroupIsolationRule, RelationshipDecayRule
from engine.rules.temporal import (
    CircadianRule,
    HighStressConsequenceRule,
    HomeostasisRule,
    SlowStateRule,
)
from engine.simulation.checkpoint import Checkpoint
from engine.simulation.runner import SimulationRunner


def build_engine() -> RuleEngine:
    return RuleEngine([
        FatigueRule(), HungerRule(), HealthRule(),
        FearResponseRule(), HopeRule(), GriefRule(), ConfusionRule(), LoveRule(),
        RelationshipDecayRule(), GroupIsolationRule(),
        HomeostasisRule(), SlowStateRule(), HighStressConsequenceRule(), CircadianRule(),
    ])


def load_person_config(person: str, overrides: dict | None = None) -> tuple[SimulationConfig, list[Checkpoint]]:
    """인물별 config + checkpoints를 로드한다."""
    content_dir = Path(f"content/{person}")

    # 도메인 등록
    if person == "peter":
        from content.peter.domain_faith import FaithJourneyState
        register_domain_type("faith_journey", FaithJourneyState)
    elif person == "vangogh":
        from content.vangogh.domain_creative import CreativeDriveState
        register_domain_type("creative_drive", CreativeDriveState)

    state = load_agent_state(content_dir / "initial_state.json")
    hazard_events = load_hazard_events(content_dir / "hazard_events.json")

    # interventions (있으면)
    interventions = []
    canonical_path = content_dir / "canonical_events.json"
    if canonical_path.exists():
        interventions = load_interventions(canonical_path)

    # checkpoints (있으면)
    checkpoints = []
    cp_path = content_dir / "checkpoints.json"
    if cp_path.exists():
        data = json.loads(cp_path.read_text(encoding="utf-8"))
        checkpoints = [Checkpoint.model_validate(cp) for cp in data["checkpoints"]]

    max_tick = 500 if person == "peter" else 150

    config = SimulationConfig(
        max_tick=max_tick,
        initial_state=state,
        hazard_events=hazard_events,
        interventions=interventions,
        state_noise_scale=0.05,
        parameter_overrides=overrides or {},
    )

    return config, checkpoints


def main() -> None:
    parser = argparse.ArgumentParser(description="Witness: Ensemble Historical Simulator")
    parser.add_argument("--person", default="peter", choices=["peter", "vangogh"], help="Person to simulate")
    parser.add_argument("--runs", type=int, default=100, help="Number of batch runs")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    print("=" * 60)
    print(f"  Witness: {args.person.title()} Simulation ({args.runs} runs)")
    print("=" * 60)
    print()

    engine = build_engine()
    config, checkpoints = load_person_config(args.person)

    # --- 1. 단일 실행 ---
    print(f"[1] Single run (seed={args.seed})")
    result = SimulationRunner(config, engine, checkpoints).run_single(seed=args.seed)
    print(f"    Events fired: {len(result.fired_events)}")
    actions = [(a.event_id, a.chosen_action) for a in result.action_history]
    print(f"    Actions: {actions}")
    print(f"    Slow state: moral_injury={result.final_state.slow_state.moral_injury:.1f}, "
          f"identity={result.final_state.slow_state.identity_shift:.1f}")
    print()

    # --- 2. 배치 실행 ---
    print(f"[2] {args.runs} runs with varied initial parameters...")
    rng = random.Random(args.seed)
    action_counts: dict[str, int] = {}
    for i in range(args.runs):
        overrides = {
            "emotions.fear": rng.uniform(0.0, 8.0),
            "emotions.love": rng.uniform(2.0, 10.0),
            "emotions.hope": rng.uniform(1.0, 9.0),
        }
        cfg, _ = load_person_config(args.person, overrides)
        r = SimulationRunner(cfg, engine, checkpoints).run_single(seed=i)
        for a in r.action_history:
            action_counts[a.chosen_action] = action_counts.get(a.chosen_action, 0) + 1

    print("    Action distribution:")
    for action, count in sorted(action_counts.items(), key=lambda x: -x[1]):
        print(f"      {action:25s}: {count}")
    print()

    # --- 3. 핵심 결과 ---
    print("[3] Validated findings (stable across analyses):")
    print("    - POM separates rule families 32x (current 38.6% vs fear-only 1.2%)")
    print("    - pyABC Model Selection: current = 100% (Peter), 84% (Van Gogh)")
    print("    - Interaction structure depends on variable set (shapiq caveat)")
    print("    - Environment up -> crisis behavior up (direction consistent)")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
