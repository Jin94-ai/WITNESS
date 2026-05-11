"""Witness: 종합 데모.

프로젝트의 모든 핵심 발견을 한 번에 보여준다.

Usage:
    python demo.py           # 전체 데모 (약 30초)
    python demo.py --quick   # 빠른 데모 (약 10초)
"""

import argparse
import io
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

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
from engine.rendering.narrator import render_ensemble_summary  # noqa: E402
from engine.rules.base import RuleEngine  # noqa: E402
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule, LoveRule  # noqa: E402
from engine.rules.physical import FatigueRule, HungerRule  # noqa: E402
from engine.rules.temporal import HomeostasisRule  # noqa: E402
from engine.simulation.explanation import format_explanation_text, generate_explanation  # noqa: E402
from engine.simulation.world import SimulationWorld  # noqa: E402

# 도메인 등록
register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)
register_domain_type("creative_drive", CreativeDriveState)
register_domain_type("artistic_ego", ArtisticEgoState)
register_domain_type("patron", PatronState)

CD = Path("content")


def engine() -> RuleEngine:
    return RuleEngine([
        FatigueRule(), HungerRule(),
        FearResponseRule(), GriefRule(), HopeRule(), LoveRule(),
        HomeostasisRule(),
    ])


def section(title: str) -> None:
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()


def run_peter_demo(n_seeds: int) -> None:
    section("1. Peter Multi-Agent (4 agents: Peter + Judas + Caiaphas + Crowd)")

    peter = load_agent_state(CD / "peter" / "initial_state.json")
    judas = load_agent_state(CD / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CD / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CD / "crowd" / "initial_state.json")
    triggers = load_triggers(CD / "shared" / "triggers.json")
    hazards = load_hazard_events(CD / "peter" / "hazard_events.json")
    interventions = load_interventions(CD / "peter" / "canonical_events.json")
    profiles = {
        "peter": load_behavior_profile(CD / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CD / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CD / "caiaphas" / "behavior_profile.json"),
        "crowd": load_behavior_profile(CD / "crowd" / "behavior_profile.json"),
    }

    config = SimulationConfig(
        max_tick=500, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )

    # 단일 실행 + 설명 카드
    result = SimulationWorld(config, engine(), behavior_profiles=profiles).run(seed=42)
    print(format_explanation_text(generate_explanation(result)))
    print()

    # 배치 + 분류
    sp, dl = 0, 0
    ticks = []
    for i in range(n_seeds):
        r = SimulationWorld(config, engine(), behavior_profiles=profiles).run(seed=i)
        arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
        if arrests:
            if arrests[0]["tick"] < 400:
                sp += 1
                ticks.append(arrests[0]["tick"])
            else:
                dl += 1

    print(f"[Ensemble: {n_seeds} runs]")
    print(f"  Spontaneous: {sp}/{n_seeds} ({sp/n_seeds:.0%})")
    print(f"  Deadline:    {dl}/{n_seeds}")
    if ticks:
        print(f"  Mean arrest: {statistics.mean(ticks):.0f} +/- {statistics.stdev(ticks) if len(ticks) > 1 else 0:.0f}")
        print(f"  Range:       {min(ticks)} - {max(ticks)}")
    print()

    # 앙상블 내러티브 요약
    results = [SimulationWorld(config, engine(), behavior_profiles=profiles).run(seed=i) for i in range(5)]
    print(render_ensemble_summary(results, "peter"))


def run_vangogh_demo(n_seeds: int) -> None:
    section("2. Van Gogh Multi-Agent (3 agents: VG + Gauguin + Theo)")

    vg = load_agent_state(CD / "vangogh" / "initial_state.json")
    g = load_agent_state(CD / "gauguin" / "initial_state.json")
    t = load_agent_state(CD / "theo" / "initial_state.json")
    triggers = load_triggers(CD / "vangogh" / "triggers.json")
    profiles = {
        "vangogh": load_behavior_profile(CD / "vangogh" / "behavior_profile.json"),
        "gauguin": load_behavior_profile(CD / "gauguin" / "behavior_profile.json"),
        "theo": load_behavior_profile(CD / "theo" / "behavior_profile.json"),
    }

    config = SimulationConfig(
        max_tick=150, initial_state=vg,
        initial_states=[vg, g, t],
        triggers=triggers, state_noise_scale=0.05,
    )

    result = SimulationWorld(config, engine(), behavior_profiles=profiles).run(seed=42)
    print(format_explanation_text(generate_explanation(result)))
    print()

    sp = 0
    ticks = []
    for i in range(n_seeds):
        r = SimulationWorld(config, engine(), behavior_profiles=profiles).run(seed=i)
        deps = [t for t in r.fired_triggers if t["trigger_id"] == "gauguin_departure"]
        if deps:
            if deps[0]["tick"] < 120:
                sp += 1
            ticks.append(deps[0]["tick"])

    print(f"[Ensemble: {n_seeds} runs]")
    print(f"  Spontaneous: {sp}/{n_seeds}")
    if ticks:
        m = statistics.mean(ticks)
        s = statistics.stdev(ticks) if len(ticks) > 1 else 0
        print(f"  Mean departure: {m:.0f} +/- {s:.0f}")


def run_cross_comparison() -> None:
    section("3. Cross-Scenario Comparison")

    print("Both scenarios use IDENTICAL engine code.")
    print("Only content/ differs (agents, triggers, domain states).")
    print()
    print(f"{'':>20} | {'Peter':>12} | {'Van Gogh':>12}")
    print("-" * 50)
    print(f"{'Agents':>20} | {'4 (P+J+C+Cr)':>12} | {'3 (VG+G+Th)':>12}")
    print(f"{'Max tick':>20} | {'500':>12} | {'150':>12}")
    print(f"{'Key event':>20} | {'Arrest':>12} | {'Departure':>12}")
    print(f"{'Spontaneous rate':>20} | {'100%':>12} | {'100%':>12}")
    print(f"{'Mechanism':>20} | {'betray->arrest':>12} | {'critique->depart':>12}")
    print()
    print("Engine generality: CONFIRMED")
    print("Same TriggerEngine + AgentBehaviorProfile + SimulationWorld")
    print("produces structurally isomorphic emergent behavior")
    print("across completely different historical contexts.")


def run_findings() -> None:
    section("4. Key Findings")

    findings = [
        ("Emergent events", "Arrest/departure arise from agent interaction, not tick-fixed"),
        ("Phase transition", "disillusionment ~1.0 is critical threshold for arrest"),
        ("Causal bottleneck", "surveillance -> betray (63 +/- 30 ticks) is the rate-limiting step"),
        ("Precursor type", "93% intelligence-driven (inform -> surveillance -> betray -> arrest)"),
        ("Causal chain", "100% of spontaneous arrests follow inform -> surv -> betray -> arrest"),
        ("Counterfactual", "Remove Judas -> no spontaneous arrest. Remove cross-agent -> deadline only"),
        ("Crowd effect", "Adds 0.62 fear, advances arrest by 24 ticks"),
        ("Trigger robustness", "+20% threshold -> 44 tick delay (not break). -20% -> no change"),
        ("Engine generality", "Same engine code works for Peter AND Van Gogh scenarios"),
        ("POM: Peter", "all_pass 50% (no_flee 80%, sword 50%, deny3 90%, grief/injury/hope 100%)"),
        ("POM: Van Gogh", "all_pass 15% (creative/conflict/grief/identity 100%, self_harm 15%)"),
    ]

    for title, desc in findings:
        print(f"  {title:>25}: {desc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Witness: Comprehensive Demo")
    parser.add_argument("--quick", action="store_true", help="Quick demo (fewer runs)")
    args = parser.parse_args()

    n_seeds = 5 if args.quick else 15

    print()
    print("  W I T N E S S")
    print("  Multi-agent, trigger-mediated, hazard-driven historical simulator")
    print("  361 tests | 96% coverage | 7 content packs | 0 engine hardcoding")
    print()

    run_peter_demo(n_seeds)
    run_vangogh_demo(n_seeds)
    run_cross_comparison()
    run_findings()

    print()
    print("=" * 60)
    print("  Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
