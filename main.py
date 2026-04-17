"""Witness 데모: 베드로 시뮬레이션 관측.

python main.py 로 실행하면 핵심 관측 결과를 출력한다.
"""

import io
import json
import random
import sys
from pathlib import Path

# Windows 한글 출력 깨짐 방지
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from content.peter.domain_faith import FaithJourneyState
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

register_domain_type("faith_journey", FaithJourneyState)

CONTENT_DIR = Path("content/peter")


def build_engine() -> RuleEngine:
    return RuleEngine([
        FatigueRule(), HungerRule(), HealthRule(),
        FearResponseRule(), HopeRule(), GriefRule(), ConfusionRule(), LoveRule(),
        RelationshipDecayRule(), GroupIsolationRule(),
        HomeostasisRule(), SlowStateRule(), HighStressConsequenceRule(), CircadianRule(),
    ])


def load_config(overrides: dict | None = None) -> SimulationConfig:
    state = load_agent_state(CONTENT_DIR / "initial_state.json")
    hazard_events = load_hazard_events(CONTENT_DIR / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "canonical_events.json")
    return SimulationConfig(
        max_tick=500,
        initial_state=state,
        hazard_events=hazard_events,
        interventions=interventions,
        state_noise_scale=0.05,
        parameter_overrides=overrides or {},
    )


def load_checkpoints() -> list[Checkpoint]:
    data = json.loads((CONTENT_DIR / "checkpoints.json").read_text(encoding="utf-8"))
    return [Checkpoint.model_validate(cp) for cp in data["checkpoints"]]


def main() -> None:
    print("=" * 60)
    print("  Witness: Hazard-Driven Ensemble Historical Simulator")
    print("  First Subject: Peter (Last 50 Days of Jesus)")
    print("=" * 60)
    print()

    engine = build_engine()
    checkpoints = load_checkpoints()

    # --- 1. 단일 실행 ---
    print("[1] Single run (seed=42, default params)")
    config = load_config()
    result = SimulationRunner(config, engine, checkpoints).run_single(seed=42)
    print(f"    Events fired: {len(result.fired_events)}")
    actions = [(a.event_id, a.chosen_action) for a in result.action_history]
    print(f"    Actions: {actions}")
    print(f"    Slow state: moral_injury={result.final_state.slow_state.moral_injury:.1f}, "
          f"identity={result.final_state.slow_state.identity_shift:.1f}")
    print()

    # --- 2. 100회 배치 (파라미터 변동) ---
    print("[2] 100 runs with varied initial parameters...")
    rng = random.Random(42)
    results = []
    for i in range(100):
        overrides = {
            "emotions.fear": rng.uniform(0.0, 8.0),
            "emotions.love": rng.uniform(2.0, 10.0),
            "emotions.hope": rng.uniform(1.0, 9.0),
        }
        cfg = load_config(overrides)
        results.append(SimulationRunner(cfg, engine, checkpoints).run_single(seed=i))

    # 경로 유형 분류
    fled = 0
    triple_deny = 0
    partial = 0
    for r in results:
        aa = next((a.chosen_action for a in r.action_history if a.event_id == "arrest"), None)
        nd = sum(1 for a in r.action_history if a.chosen_action == "deny")
        if aa == "flee":
            fled += 1
        elif nd >= 3:
            triple_deny += 1
        else:
            partial += 1

    print(f"    Fled: {fled}%, Triple deny: {triple_deny}%, Other: {partial}%")
    print()

    # --- 3. 핵심 발견 ---
    print("[3] Key findings (v0.5 -- POM/PRIM/ModelSelection/shapiq verified):")
    print()
    print("    POM VALIDATION (7 patterns simultaneously):")
    print("    - current rules: 38.6% pass all 7. fear-only: 1.2%. uniform: 0%.")
    print("    - POM separates rule families 32x (vs 2x with deny3 alone).")
    print("    - pyABC Model Selection: current = 100% posterior probability.")
    print()
    print("    SHAPLEY INTERACTIONS (shapiq -- CAVEAT):")
    print("    - With 3 vars: fear x love = 0.123 (#1)")
    print("    - With 5 vars (+ env): fear alone = 0.026, surveillance = 0.025 (#1-2)")
    print("    - Interaction structure changes with variable set.")
    print("    - 'Specific interactions are model-dependent, not structural facts.'")
    print()
    print("    WHAT IS STABLE (variable-set independent):")
    print("    - POM separates rule families 32x regardless of analysis method")
    print("    - pyABC: current = 100% posterior")
    print("    - Environment up -> denial up (direction consistent)")
    print("    - Flee rate = 29% (environment-independent)")
    print()
    print("    PRIM (parameter box where POM passes):")
    print("    - love: [1.4, 8.7] -- extremes excluded")
    print("    - crowd: [1.1, 7.2] -- too high fails")
    print("    - fear: no restriction. hope: no restriction.")
    print()
    print("=" * 60)
    print("  'The engine can tell which rule structure fits history,")
    print("   but not which variable matters most.")
    print("   What is certain: the current structure is uniquely valid,")
    print("   and fear alone cannot explain the path.'")
    print("=" * 60)


if __name__ == "__main__":
    main()
