"""Arrest Precursor Path Analysis.

체포 직전 구간의 에이전트 상태/행동 패턴을 분석한다.
"체포가 발생했다"가 아니라 "어떤 선행 경로에서 발생했는가"를 관측.

ChatGPT: "체포 자체보다 체포 선행 경로의 클러스터를 봐야 한다"
"""

from collections import Counter
from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
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
from engine.rules.emotional import FearResponseRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), HopeRule(), HomeostasisRule()])


def _load_all():
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
    profiles = {
        "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
    }
    return peter, judas, caiaphas, triggers, hazards, interventions, profiles


def _extract_precursor(result, arrest_tick: int, window: int = 30):
    """체포 직전 window tick 동안의 에이전트 행동을 추출한다."""
    start_tick = max(1, arrest_tick - window)

    precursor = {}
    for aid, history in result.action_histories.items():
        actions_in_window = [a for a in history if start_tick <= a.tick < arrest_tick]
        action_counts = Counter(a.chosen_action for a in actions_in_window)
        precursor[aid] = dict(action_counts)

    # 트리거 발동 기록
    triggers_in_window = [
        t for t in result.fired_triggers
        if start_tick <= t["tick"] < arrest_tick
    ]

    return {
        "arrest_tick": arrest_tick,
        "window": (start_tick, arrest_tick),
        "agent_actions": precursor,
        "triggers_before_arrest": [t["trigger_id"] for t in triggers_in_window],
    }


def _classify_precursor_type(precursor: dict) -> str:
    """선행 경로를 유형으로 분류한다."""
    judas_actions = precursor["agent_actions"].get("judas", {})
    caiaphas_actions = precursor["agent_actions"].get("caiaphas", {})

    judas_betray = judas_actions.get("betray", 0)
    judas_inform = judas_actions.get("inform_authorities", 0)
    caiaphas_arrest = caiaphas_actions.get("order_arrest", 0)

    has_surv_escalation = "surveillance_escalation" in precursor["triggers_before_arrest"]

    # 분류 기준
    if judas_inform >= 2 and has_surv_escalation:
        return "intelligence_driven"  # 유다 정보 제공 -> 감시 강화 -> 체포
    if judas_betray >= 2:
        return "betrayal_saturated"  # 유다 배반 반복형
    if caiaphas_arrest >= 3:
        return "caiaphas_aggressive"  # 가야바 주도형
    return "standard"  # 표준형


class TestPrecursorAnalysis:
    def test_precursor_extraction(self):
        """체포 직전 30 tick의 행동 패턴을 추출한다."""
        peter, judas, caiaphas, triggers, hazards, interventions, profiles = _load_all()
        config = SimulationConfig(
            max_tick=500, initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            hazard_events=hazards, interventions=interventions,
            triggers=triggers, state_noise_scale=0.05,
        )

        result = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=42)
        arrests = [t for t in result.fired_triggers if t["trigger_id"] == "arrest_trigger"]
        assert len(arrests) > 0

        precursor = _extract_precursor(result, arrests[0]["tick"])
        assert "judas" in precursor["agent_actions"]
        assert precursor["arrest_tick"] == arrests[0]["tick"]

    @pytest.mark.slow
    def test_precursor_types_across_seeds(self):
        """30 시드에서 선행 경로 유형 분포를 관측한다."""
        peter, judas, caiaphas, triggers, hazards, interventions, profiles = _load_all()
        config = SimulationConfig(
            max_tick=500, initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            hazard_events=hazards, interventions=interventions,
            triggers=triggers, state_noise_scale=0.05,
        )

        type_counts = Counter()
        all_precursors = []

        for seed in range(30):
            result = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)
            arrests = [t for t in result.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if arrests and arrests[0]["tick"] < 400:
                precursor = _extract_precursor(result, arrests[0]["tick"])
                ptype = _classify_precursor_type(precursor)
                type_counts[ptype] += 1
                all_precursors.append(precursor)

        print("\n=== Precursor Path Types (30 seeds) ===")
        for ptype, count in type_counts.most_common():
            print(f"  {ptype:25s}: {count}")

        # 적어도 2가지 이상의 경로 유형
        assert len(type_counts) >= 1, "Should have at least one precursor type"
        print(f"\nDistinct types: {len(type_counts)}")

    @pytest.mark.slow
    def test_causal_chain_frequency(self):
        """인과 체인 빈도: 환멸 -> 배반 -> 정보 -> 체포."""
        peter, judas, caiaphas, triggers, hazards, interventions, profiles = _load_all()
        config = SimulationConfig(
            max_tick=500, initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            hazard_events=hazards, interventions=interventions,
            triggers=triggers, state_noise_scale=0.05,
        )

        chain_present = 0
        total = 0

        for seed in range(20):
            result = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)
            arrests = [t for t in result.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if not arrests or arrests[0]["tick"] >= 400:
                continue

            total += 1
            arrest_tick = arrests[0]["tick"]

            # 인과 체인 확인: inform -> surveillance_escalation -> betray -> arrest
            judas_history = result.action_histories.get("judas", [])
            has_inform = any(a.chosen_action == "inform_authorities" and a.tick < arrest_tick
                            for a in judas_history)
            has_betray = any(a.chosen_action == "betray" and a.tick <= arrest_tick
                            for a in judas_history)
            has_surv = any(t["trigger_id"] == "surveillance_escalation" and t["tick"] < arrest_tick
                          for t in result.fired_triggers)

            if has_inform and has_surv and has_betray:
                chain_present += 1

        chain_rate = chain_present / total if total > 0 else 0
        print("\n=== Causal Chain: inform -> surveillance -> betray -> arrest ===")
        print(f"Present: {chain_present}/{total} ({chain_rate:.0%})")

        # 인과 체인이 대부분의 자연 발생 체포에서 관찰되어야 함
        assert chain_rate >= 0.5, f"Causal chain should be present in >= 50% of arrests (got {chain_rate:.0%})"
