"""Trigger Sensitivity Audit.

LLM 리뷰 피드백: "트리거가 지나치게 잘 설계되면 세계가 너무 순응적이 된다."
트리거 조건을 흔들고, 제거하고, 결과 분포가 적절히 변하는지 확인한다.

핵심 검증:
1. 트리거 조건 ±20% 시 결과 분포가 부드럽게 변하는가?
2. 트리거 제거 시 체포가 deadline에만 의존하는가? (counterfactual)
3. cross-agent effect 차단 시 행동 분포가 변하는가? (ablation)
4. spontaneous vs deadline-assisted 비율 분리
"""

import statistics
from pathlib import Path

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.trigger import ActionTriggerCondition, Trigger, TriggerCondition
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
from engine.rules.emotional import FearResponseRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"
N_SEEDS = 20


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), HopeRule(), HomeostasisRule()])


def _load_all():
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
    profiles = {
        "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
    }
    return peter, judas, caiaphas, hazards, interventions, profiles


def _run_batch(config, profiles, n_seeds=N_SEEDS):
    """배치 실행 후 체포 분류 반환."""
    spontaneous = 0
    deadline_assisted = 0
    no_arrest = 0
    arrest_ticks = []

    for seed in range(n_seeds):
        r = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)
        arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
        if not arrests:
            no_arrest += 1
        elif arrests[0]["tick"] >= 400:
            deadline_assisted += 1
            arrest_ticks.append(arrests[0]["tick"])
        else:
            spontaneous += 1
            arrest_ticks.append(arrests[0]["tick"])

    mean_tick = statistics.mean(arrest_ticks) if arrest_ticks else 500
    return {
        "spontaneous": spontaneous,
        "deadline": deadline_assisted,
        "no_arrest": no_arrest,
        "mean_tick": mean_tick,
        "ticks": arrest_ticks,
    }


class TestTriggerSensitivity:
    """트리거 조건 ±20% 흔들기."""

    def test_baseline(self):
        """기준선: 원래 트리거 조건."""
        peter, judas, caiaphas, hazards, interventions, profiles = _load_all()
        triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
        config = SimulationConfig(
            max_tick=500, initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            hazard_events=hazards, interventions=interventions,
            triggers=triggers, state_noise_scale=0.05,
        )
        result = _run_batch(config, profiles)
        print(f"\n[Baseline] spontaneous={result['spontaneous']}/{N_SEEDS}, "
              f"deadline={result['deadline']}, no_arrest={result['no_arrest']}, "
              f"mean_tick={result['mean_tick']:.0f}")
        # 기준선: 대부분 spontaneous
        assert result["spontaneous"] > 0

    def test_tighter_threshold(self):
        """트리거 조건 강화 (+20%): disillusionment >= 9.6, threat >= 8.4."""
        peter, judas, caiaphas, hazards, interventions, profiles = _load_all()
        tight_trigger = Trigger(
            trigger_id="arrest_trigger",
            state_conditions=[
                TriggerCondition(agent_id="judas", field_path="domain_state.disillusionment",
                                 operator="gte", value=9.6),
                TriggerCondition(agent_id="caiaphas", field_path="domain_state.threat_assessment",
                                 operator="gte", value=8.4),
            ],
            action_conditions=[ActionTriggerCondition(agent_id="judas", action_id="betray")],
            event_template_id="arrest_event",
            effects_on_fire=[
                {"field_path": "emotions.fear", "operation": "set", "value": 8.5, "target_agent_id": "peter"},
            ],
            max_fires=1, deadline_tick=400,
        )
        surveillance = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
        surv = [t for t in surveillance if t.trigger_id == "surveillance_escalation"]

        config = SimulationConfig(
            max_tick=500, initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            hazard_events=hazards, interventions=interventions,
            triggers=[tight_trigger] + surv, state_noise_scale=0.05,
        )
        result = _run_batch(config, profiles)
        print(f"\n[Tighter +20%] spontaneous={result['spontaneous']}/{N_SEEDS}, "
              f"deadline={result['deadline']}, mean_tick={result['mean_tick']:.0f}")
        # 조건 강화 -> 체포 시점이 늦어짐 (mean tick 증가)
        assert result["mean_tick"] > 200, "Tighter conditions should delay arrest"

    def test_looser_threshold(self):
        """트리거 조건 완화 (-20%): disillusionment >= 6.4, threat >= 5.6."""
        peter, judas, caiaphas, hazards, interventions, profiles = _load_all()
        loose_trigger = Trigger(
            trigger_id="arrest_trigger",
            state_conditions=[
                TriggerCondition(agent_id="judas", field_path="domain_state.disillusionment",
                                 operator="gte", value=6.4),
                TriggerCondition(agent_id="caiaphas", field_path="domain_state.threat_assessment",
                                 operator="gte", value=5.6),
            ],
            action_conditions=[ActionTriggerCondition(agent_id="judas", action_id="betray")],
            event_template_id="arrest_event",
            effects_on_fire=[
                {"field_path": "emotions.fear", "operation": "set", "value": 8.5, "target_agent_id": "peter"},
            ],
            max_fires=1, deadline_tick=400,
        )
        surveillance = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
        surv = [t for t in surveillance if t.trigger_id == "surveillance_escalation"]

        config = SimulationConfig(
            max_tick=500, initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            hazard_events=hazards, interventions=interventions,
            triggers=[loose_trigger] + surv, state_noise_scale=0.05,
        )
        result = _run_batch(config, profiles)
        print(f"\n[Looser -20%] spontaneous={result['spontaneous']}/{N_SEEDS}, "
              f"deadline={result['deadline']}, mean_tick={result['mean_tick']:.0f}")
        # 조건 완화 -> 더 빠른 체포, spontaneous 증가
        assert result["spontaneous"] >= N_SEEDS * 0.5


class TestCounterfactual:
    """Counterfactual: 트리거 제거, 에이전트 제거."""

    def test_no_triggers(self):
        """트리거 완전 제거 -> 체포 미발생."""
        peter, judas, caiaphas, hazards, interventions, profiles = _load_all()
        config = SimulationConfig(
            max_tick=500, initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            hazard_events=hazards, interventions=interventions,
            triggers=[],  # 트리거 없음
            state_noise_scale=0.05,
        )
        result = _run_batch(config, profiles, n_seeds=5)
        print(f"\n[No triggers] spontaneous={result['spontaneous']}, "
              f"deadline={result['deadline']}, no_arrest={result['no_arrest']}")
        # 트리거 없으면 체포 트리거 미발동
        assert result["spontaneous"] == 0
        assert result["deadline"] == 0

    def test_no_judas(self):
        """유다 제거 -> 체포가 deadline에만 의존."""
        peter, judas, caiaphas, hazards, interventions, profiles = _load_all()
        triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
        # 유다 없이 peter + caiaphas만
        profiles_no_judas = {k: v for k, v in profiles.items() if k != "judas"}
        config = SimulationConfig(
            max_tick=500, initial_state=peter,
            initial_states=[peter, caiaphas],
            hazard_events=hazards, interventions=interventions,
            triggers=triggers, state_noise_scale=0.05,
        )
        result = _run_batch(config, profiles_no_judas, n_seeds=5)
        print(f"\n[No Judas] spontaneous={result['spontaneous']}, "
              f"deadline={result['deadline']}, no_arrest={result['no_arrest']}")
        # 유다 없으면 betray 행동 없음 -> spontaneous 불가
        assert result["spontaneous"] == 0

    def test_no_cross_agent_effects(self):
        """cross-agent effect 제거 -> 에이전트 간 영향 차단."""
        peter, judas, caiaphas, hazards, interventions, profiles = _load_all()
        # arrest_trigger에서 cross-agent effect 제거
        trigger_no_cross = Trigger(
            trigger_id="arrest_trigger",
            state_conditions=[
                TriggerCondition(agent_id="judas", field_path="domain_state.disillusionment",
                                 operator="gte", value=8.0),
                TriggerCondition(agent_id="caiaphas", field_path="domain_state.threat_assessment",
                                 operator="gte", value=7.0),
            ],
            action_conditions=[ActionTriggerCondition(agent_id="judas", action_id="betray")],
            event_template_id="arrest_event",
            effects_on_fire=[],  # cross-agent effect 없음
            max_fires=1, deadline_tick=400,
        )
        # surveillance에서도 cross-agent effect 제거
        surv_no_cross = Trigger(
            trigger_id="surveillance_escalation",
            action_conditions=[ActionTriggerCondition(agent_id="judas", action_id="inform_authorities")],
            event_template_id="intelligence_received",
            effects_on_fire=[],  # cross-agent effect 없음
            max_fires=5, cooldown=20,
        )
        config = SimulationConfig(
            max_tick=500, initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            hazard_events=hazards, interventions=interventions,
            triggers=[trigger_no_cross, surv_no_cross], state_noise_scale=0.05,
        )
        result = _run_batch(config, profiles, n_seeds=10)
        print(f"\n[No cross-agent] spontaneous={result['spontaneous']}/{10}, "
              f"deadline={result['deadline']}, mean_tick={result['mean_tick']:.0f}")
        # surveillance_escalation이 가야바 threat를 올리지 않으므로
        # 가야바 threat 조건(>= 7.0)이 충족되기 어려움 -> deadline 증가
        # 하지만 가야바 자체 행동(order_surveillance)이 threat를 올릴 수 있음
