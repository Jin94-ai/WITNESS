"""Initial Parameter Importance Ranking.

이전 test_initial_perturbation.py: Judas disill만 스윕 (arrest 313→125).
이번엔 4개 핵심 초기값을 같은 범위로 스윕해서 importance 비교:
- Judas disill (baseline 3.0)
- Judas greed (baseline 4.0)
- Judas messiah_expectation (baseline 7.0)
- Caiaphas threat_assessment (baseline 3.0)

각 parameter를 ±2 범위에서 sweep → arrest_tick 변화 측정 → rank.

이는 "어떤 초기 조건이 가장 중요한가?"를 정량화하는 global sensitivity.
SALib Sobol 유사하지만 single-factor, 이미 동적 parameter는 ablation.
"""

import statistics
from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_interventions,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run_with_override(
    judas_override: dict | None = None,
    caiaphas_override: dict | None = None,
    seed: int = 0,
) -> int | None:
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT_DIR / "crowd" / "initial_state.json")

    if judas_override:
        new_ds = judas.domain_state.model_copy(update=judas_override)
        judas = judas.model_copy(update={"domain_state": new_ds})
    if caiaphas_override:
        new_ds = caiaphas.domain_state.model_copy(update=caiaphas_override)
        caiaphas = caiaphas.model_copy(update={"domain_state": new_ds})

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
        max_tick=500, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )
    r = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)
    arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
    return arrests[0]["tick"] if arrests else None


def _mean_arrest(override_fn, values: list[float], n_seeds: int = 5) -> dict[float, float]:
    """Override the single parameter at each value and return {value: mean_arrest_tick}."""
    means = {}
    for v in values:
        ticks = []
        for seed in range(n_seeds):
            t = _run_with_override(seed=seed, **override_fn(v))
            ticks.append(t if t is not None else 500)
        means[v] = statistics.mean(ticks)
    return means


@pytest.mark.slow
class TestParamImportance:
    def test_param_sweep_ranking(self):
        """4개 초기 파라미터의 arrest_tick 영향 비교."""
        # Peter 시나리오의 진짜 baseline 값을 파일에서 읽기
        j = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
        c = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")

        base_disill = j.domain_state.disillusionment
        base_greed = j.domain_state.greed
        base_messiah = j.domain_state.messiah_expectation
        base_threat = c.domain_state.threat_assessment

        # ±2 range, 5 points
        def range_5(base: float) -> list[float]:
            step = 1.0
            return [base - 2 * step, base - step, base, base + step, base + 2 * step]

        params = [
            ("judas.disill", lambda v: {"judas_override": {"disillusionment": v}}, base_disill),
            ("judas.greed", lambda v: {"judas_override": {"greed": v}}, base_greed),
            ("judas.messiah_exp", lambda v: {"judas_override": {"messiah_expectation": v}}, base_messiah),
            ("caiaphas.threat", lambda v: {"caiaphas_override": {"threat_assessment": v}}, base_threat),
        ]

        n_seeds = 5
        print(f"\n=== Parameter Importance Sweep (n={n_seeds} seeds per value) ===")

        results = {}
        for name, fn, base in params:
            vals = range_5(base)
            means = _mean_arrest(fn, vals, n_seeds=n_seeds)
            # Sensitivity: max-min across sweep range
            sensitivity = max(means.values()) - min(means.values())
            # Directional: sign of slope
            slope = (means[vals[-1]] - means[vals[0]]) / (vals[-1] - vals[0])
            results[name] = (sensitivity, slope, means, base)

        # 출력 (sensitivity 순 정렬)
        ranked = sorted(results.items(), key=lambda kv: -kv[1][0])
        print(f"\n{'Parameter':>25} | {'baseline':>10} | {'range':>8} | "
              f"{'sensitivity':>12} | {'slope':>9}")
        print("-" * 85)
        for name, (sens, slope, means, base) in ranked:
            lo = min(means.values())
            hi = max(means.values())
            print(f"{name:>25} | {base:>10.1f} | [{lo:>4.0f},{hi:>4.0f}] | "
                  f"{sens:>11.1f} | {slope:>9.2f}")

        # 가장 영향 큰 파라미터가 Judas disill이어야 함 (기존 발견)
        top_param = ranked[0][0]
        print(f"\nMost important: {top_param}")

        # sensitivity 순위 출력
        for i, (name, (sens, _, _, _)) in enumerate(ranked, 1):
            print(f"  {i}. {name}: sensitivity = {sens:.0f} ticks")

        # 최상위 파라미터의 sensitivity >= 40 tick (meaningful)
        assert ranked[0][1][0] >= 40, \
            f"Top parameter sensitivity {ranked[0][1][0]:.0f} below 40 ticks (too weak)"

        # Judas disill이 top 2 안에 있어야 함
        top_names = [r[0] for r in ranked[:2]]
        assert "judas.disill" in top_names, \
            f"judas.disill should be top-2 but ranking is {[r[0] for r in ranked]}"
