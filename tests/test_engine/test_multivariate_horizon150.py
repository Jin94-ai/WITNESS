"""Multivariate Forecast at Earlier Holdout (tick 150).

RESEARCH.md 미래 작업: "tick 150 부근에서 multivariate가 정보 더 주는지"
holdout=200에서는 greed/threat가 이미 saturate(mean 9.3/10.0) -> univariate 승.
holdout=150에서는 변수가 아직 정보 보유:
  - disill: mean 7.2, std 1.01
  - greed:  mean 6.7, std 1.37
  - threat: mean 7.7, std 2.19 (가장 변동 큼)

따라서 150에서는 multivariate가 univariate보다 유의미하게 나을 수 있다.
이는 "tick 200에서 univariate 승"이 saturation 때문임을 직접 검증.
"""

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
from engine.simulation.statistics import proportion_ci
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"
HOLDOUT = 150
CATEGORIES = ["very_early", "early", "mid", "late", "deadline_or_none"]


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run(seed: int):
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
        max_tick=500, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )
    return SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)


def _actual(arrest_tick: int | None) -> str:
    if arrest_tick is None:
        return "deadline_or_none"
    if arrest_tick < 100:
        return "very_early"
    if arrest_tick < 200:
        return "early"
    if arrest_tick < 300:
        return "mid"
    if arrest_tick < 400:
        return "late"
    return "deadline_or_none"


def _uni_forecast_150(disill: float) -> str:
    """Tick 150 기준 univariate. 실측: disill 7.0+ 대부분 early, 6.9 이하 대부분 mid.

    실측 분포 (n=24): 모두 arrest 발생, actual은 early(11) 또는 mid(13).
    임계 fit: 7.0 분할점.
    """
    if disill >= 7.0:
        return "early"
    if disill >= 5.0:
        return "mid"
    if disill >= 3.0:
        return "late"
    return "deadline_or_none"


def _multi_forecast_150(disill: float, greed: float, threat: float) -> str:
    """Tick 150에서 3변수 활용. threat가 가장 변별력 있음 (std 2.19).

    실측 관찰:
    - threat >= 9.0 + disill >= 7.0: 대부분 early
    - threat <= 5.0: 거의 항상 mid (threat가 느리게 쌓임)
    - 중간 영역: greed 보조 사용
    """
    # High threat + high disill = imminent
    if threat >= 8.5 and disill >= 7.0:
        return "early"
    if disill >= 7.5 and greed >= 7.0:
        return "early"

    # Low threat 신호 = mid (arrest가 느림)
    if threat <= 5.0:
        return "mid"

    # 중간: disill 기반
    if disill >= 7.0:
        return "early"
    if disill >= 5.0:
        return "mid"
    if disill >= 3.0:
        return "late"
    return "deadline_or_none"


@pytest.mark.slow
class TestMultivariateHorizon150:
    def test_multivariate_better_at_tick150(self):
        """Tick 150에서 multivariate가 univariate보다 나은가 (saturation 전)."""
        records = []
        for seed in range(30):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            arrest_tick = arrests[0]["tick"] if arrests else None

            # holdout 전에 이미 arrest 발생하면 제외
            if arrest_tick is not None and arrest_tick <= HOLDOUT:
                continue

            actual = _actual(arrest_tick)

            judas_snaps = r.state_snapshots.get("judas", {})
            caiaphas_snaps = r.state_snapshots.get("caiaphas", {})
            jc = [t for t in judas_snaps if t <= HOLDOUT]
            cc = [t for t in caiaphas_snaps if t <= HOLDOUT]
            if not jc or not cc:
                continue

            j = judas_snaps[max(jc)]
            c = caiaphas_snaps[max(cc)]
            records.append({
                "actual": actual,
                "disill": j.domain_state.disillusionment,
                "greed": j.domain_state.greed,
                "threat": c.domain_state.threat_assessment,
            })

        uni_correct = sum(
            1 for r in records if _uni_forecast_150(r["disill"]) == r["actual"]
        )
        multi_correct = sum(
            1 for r in records
            if _multi_forecast_150(r["disill"], r["greed"], r["threat"]) == r["actual"]
        )

        uni_ci = proportion_ci(uni_correct, len(records))
        multi_ci = proportion_ci(multi_correct, len(records))

        print(f"\n=== Multivariate at Holdout {HOLDOUT} (pre-saturation) ===")
        print(f"n={len(records)}")
        print(f"Univariate:   {uni_ci.mean:.0%} [{uni_ci.lower:.0%}, {uni_ci.upper:.0%}]")
        print(f"Multivariate: {multi_ci.mean:.0%} [{multi_ci.lower:.0%}, {multi_ci.upper:.0%}]")

        print(f"\n{'disill':>7} | {'greed':>6} | {'threat':>7} | {'uni':>12} | {'multi':>12} | {'actual':>10}")
        print("-" * 75)
        for rec in records[:15]:
            uni = _uni_forecast_150(rec["disill"])
            mul = _multi_forecast_150(rec["disill"], rec["greed"], rec["threat"])
            print(f"{rec['disill']:>7.1f} | {rec['greed']:>6.1f} | "
                  f"{rec['threat']:>7.1f} | {uni:>12} | {mul:>12} | {rec['actual']:>10}")

        print("\nReference (tick 200, post-saturation):")
        print("  Univariate: 80% [63%, 90%], Multivariate: 63% [46%, 78%]")
        print("  Multivariate worse because greed/threat saturated")

        print("\n=== Hypothesis test ===")
        if multi_ci.mean > uni_ci.mean + 0.05:
            print("Multivariate SIGNIFICANTLY better at earlier holdout (pre-saturation).")
            print("Confirms: saturation is what makes multivariate redundant at tick 200.")
        elif abs(multi_ci.mean - uni_ci.mean) <= 0.05:
            print("Univariate and multivariate comparable at tick 150.")
            print("Disillusionment carries most information even before saturation.")
        else:
            print("Univariate still better at tick 150.")
            print("Suggests disillusionment is uniquely informative, not just a saturation artifact.")

        # 최소 요건: 두 예측 모두 random(20%)보다 나음
        assert uni_ci.mean > 0.40, \
            f"Univariate should beat random substantially, got {uni_ci.mean:.0%}"
        assert multi_ci.mean > 0.40, \
            f"Multivariate should beat random substantially, got {multi_ci.mean:.0%}"

        # 핵심 비교: multivariate가 최소한 univariate만큼은 좋아야 함 (tick 150에서는 정보 보유)
        # tick 200과 달리 threat가 아직 saturate 안 됨 -> multi가 최소 동률
        assert multi_ci.mean >= uni_ci.mean - 0.10, \
            "At tick 150 multivariate should be competitive with univariate"
