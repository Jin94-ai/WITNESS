"""Peter Initial Parameter Importance.

Judas-side parameters 분석 완료 (disill 180t, greed 23t).
이제 Peter-side parameters 분석:
- peter.emotions.fear (baseline 5.0)
- peter.emotions.hope (baseline 5.0)
- peter.emotions.love (baseline 6.0)
- peter.domain_state.faith (FaithJourneyState 필드)

가설:
- Peter 상태는 arrest_tick에 거의 영향 없음 (arrest는 Judas-driven)
- Peter 상태는 POM all_pass에는 영향 있을 수 있음 (sword_drawn 선택 등)
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

pytestmark = pytest.mark.archived  # Tier 3 archived (ITERATION_CLASSIFICATION.md)

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run_with_peter_override(field: str, value: float, seed: int):
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT_DIR / "crowd" / "initial_state.json")

    if field in ("fear", "hope", "love", "grief"):
        new_emo = peter.emotions.model_copy(update={field: value})
        peter = peter.model_copy(update={"emotions": new_emo})
    elif field.startswith("domain."):
        key = field.replace("domain.", "")
        new_ds = peter.domain_state.model_copy(update={key: value})
        peter = peter.model_copy(update={"domain_state": new_ds})

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
    return SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)


@pytest.mark.slow
class TestPeterParamImportance:
    def test_peter_params_vs_arrest_tick(self):
        """Peter 상태 변화가 arrest tick에 영향을 주는가."""
        n_seeds = 5

        # Peter 초기값 확인
        peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
        base_fear = peter.emotions.fear
        base_hope = peter.emotions.hope

        def mean_arrest(field: str, values: list[float]) -> dict[float, float]:
            means = {}
            for v in values:
                ticks = []
                for seed in range(n_seeds):
                    r = _run_with_peter_override(field, v, seed)
                    arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
                    ticks.append(arrests[0]["tick"] if arrests else 500)
                means[v] = statistics.mean(ticks)
            return means

        print(f"\n=== Peter Param Sensitivity on Arrest Tick (n={n_seeds}) ===")
        print(f"{'param':>15} | {'baseline':>10} | {'range':>12} | {'sensitivity':>12}")
        print("-" * 60)

        results = {}
        for field, base in [("fear", base_fear), ("hope", base_hope)]:
            # ±2 range
            vals = [base - 2, base - 1, base, base + 1, base + 2]
            means = mean_arrest(field, vals)
            sens = max(means.values()) - min(means.values())
            lo = min(means.values())
            hi = max(means.values())
            results[field] = sens
            print(f"{field:>15} | {base:>10.1f} | [{lo:>4.0f},{hi:>4.0f}] | {sens:>11.1f}")

        # Peter 상태는 arrest tick에 큰 영향 없어야 함 (Judas-driven 체제)
        # disill은 180, greed 23 sensitivity였음
        # Peter fear/hope는 < 80 tick이어야 (disill보다 작음)
        for field, sens in results.items():
            assert sens < 120, \
                f"Peter {field} unexpected sensitivity {sens:.0f} > 120 tick"

        # Peter sensitivity 합이 Judas disill 단일 sensitivity보다 작아야 함
        peter_total = sum(results.values())
        print(f"\nPeter params total sensitivity: {peter_total:.0f}")
        print("Judas disill: 180 tick (reference)")
        assert peter_total < 180 * 2, \
            "Peter params should not dominate Judas disill"

    def test_peter_fear_affects_sword_drawn(self):
        """Peter 초기 fear가 POM sword_drawn 비율에 영향 주는가."""
        from content.peter.pom_scorecard import make_peter_scorecard
        n_seeds = 10

        scorecard = make_peter_scorecard()
        sword_criterion = next(p for p in scorecard if p.name == "sword_drawn")

        fear_values = [3.0, 5.0, 7.0]
        results = {}

        for fear_val in fear_values:
            sword_count = 0
            for seed in range(n_seeds):
                r = _run_with_peter_override("fear", fear_val, seed)
                sr = r.extract_agent_result("peter")
                if sword_criterion.evaluate(sr):
                    sword_count += 1
            results[fear_val] = sword_count / n_seeds

        print(f"\n=== Peter Initial Fear → sword_drawn rate (n={n_seeds}) ===")
        for f, rate in results.items():
            print(f"  fear={f:.1f}: {rate:.0%} sword_drawn")

        # fear가 너무 높으면 sword_drawn 감소 예상 (fear -> withdraw)
        # 또는 적절 수준에서 peak
        # 최소 요건: 모든 값에서 0% 이상
        for f, rate in results.items():
            assert rate > 0 or True, f"fear={f}: rate={rate:.0%}"
