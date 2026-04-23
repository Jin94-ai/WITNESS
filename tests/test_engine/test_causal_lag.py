"""Causal Lag Analysis.

인과 체인의 시간 지연을 측정한다:
1. 유다의 첫 inform_authorities -> 첫 surveillance_escalation 트리거까지의 지연
2. 첫 surveillance_escalation -> 유다의 첫 betray까지의 지연
3. 첫 betray -> arrest_trigger까지의 지연

이 지연이 시드에 따라 변동하는가? 어느 구간이 가장 긴가?
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


def _run_4agent(seed):
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


def _extract_causal_timeline(result):
    """인과 체인의 ���요 이벤트 tick을 추출한다."""
    judas_history = result.action_histories.get("judas", [])

    first_inform = next(
        (a.tick for a in judas_history if a.chosen_action == "inform_authorities"), None
    )
    first_betray = next(
        (a.tick for a in judas_history if a.chosen_action == "betray"), None
    )

    first_surv = next(
        (t["tick"] for t in result.fired_triggers if t["trigger_id"] == "surveillance_escalation"), None
    )
    arrest_tick = next(
        (t["tick"] for t in result.fired_triggers if t["trigger_id"] == "arrest_trigger"), None
    )

    return {
        "first_inform": first_inform,
        "first_surveillance": first_surv,
        "first_betray": first_betray,
        "arrest": arrest_tick,
    }


@pytest.mark.slow
class TestCausalLag:
    def test_causal_chain_timing(self):
        """인과 체인의 시간 지연을 측정한다."""
        lags_inform_surv = []
        lags_surv_betray = []
        lags_betray_arrest = []
        lags_total = []

        n_seeds = 20
        for seed in range(n_seeds):
            r = _run_4agent(seed)
            timeline = _extract_causal_timeline(r)

            if all(v is not None for v in timeline.values()):
                lag_is = timeline["first_surveillance"] - timeline["first_inform"]
                lag_sb = timeline["first_betray"] - timeline["first_surveillance"]
                lag_ba = timeline["arrest"] - timeline["first_betray"]
                lag_total = timeline["arrest"] - timeline["first_inform"]

                lags_inform_surv.append(lag_is)
                lags_surv_betray.append(lag_sb)
                lags_betray_arrest.append(lag_ba)
                lags_total.append(lag_total)

        print(f"\n=== Causal Lag Analysis ({len(lags_total)}/{n_seeds} complete chains) ===")
        if lags_inform_surv:
            print(f"  inform -> surveillance: mean={statistics.mean(lags_inform_surv):.0f} "
                  f"+/- {statistics.stdev(lags_inform_surv):.0f} ticks")
        if lags_surv_betray:
            print(f"  surveillance -> betray: mean={statistics.mean(lags_surv_betray):.0f} "
                  f"+/- {statistics.stdev(lags_surv_betray):.0f} ticks")
        if lags_betray_arrest:
            print(f"  betray -> arrest:       mean={statistics.mean(lags_betray_arrest):.0f} "
                  f"+/- {statistics.stdev(lags_betray_arrest):.0f} ticks")
        if lags_total:
            print(f"  total (inform->arrest): mean={statistics.mean(lags_total):.0f} "
                  f"+/- {statistics.stdev(lags_total):.0f} ticks")

        # 인과 체인이 대부분의 시드에서 완전해야 함
        assert len(lags_total) >= n_seeds * 0.5

    def test_bottleneck_identification(self):
        """인과 체인에서 가장 긴 지연 구간(bottleneck)을 식별한다."""
        segment_totals = {"inform_surv": 0, "surv_betray": 0, "betray_arrest": 0}
        n_valid = 0

        for seed in range(15):
            r = _run_4agent(seed)
            t = _extract_causal_timeline(r)
            if all(v is not None for v in t.values()):
                segment_totals["inform_surv"] += t["first_surveillance"] - t["first_inform"]
                segment_totals["surv_betray"] += t["first_betray"] - t["first_surveillance"]
                segment_totals["betray_arrest"] += t["arrest"] - t["first_betray"]
                n_valid += 1

        if n_valid > 0:
            means = {k: v / n_valid for k, v in segment_totals.items()}
            bottleneck = max(means, key=means.get)
            print(f"\n=== Bottleneck Analysis ({n_valid} valid chains) ===")
            for seg, mean in means.items():
                marker = " <-- BOTTLENECK" if seg == bottleneck else ""
                print(f"  {seg:20s}: {mean:.0f} ticks{marker}")
