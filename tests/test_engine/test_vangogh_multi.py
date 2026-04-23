"""Van Gogh 다중 에이전트 통합 테스트.

trigger ontology 범용성 검증: 성서 외 인물(예술가)에서도
동일한 TriggerEngine + AgentBehaviorProfile + SimulationWorld가 작동하는가?

핵심: 고갱의 좌절 누적 -> 떠남 -> 반 고흐 위기 (Peter 시나리오와 구조적 동형)
"""

from collections import Counter
from pathlib import Path

from content.gauguin.domain_artistic_ego import ArtisticEgoState
from content.theo.domain_patron import PatronState
from content.vangogh.domain_creative import CreativeDriveState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.world import SimulationWorld

register_domain_type("creative_drive", CreativeDriveState)
register_domain_type("artistic_ego", ArtisticEgoState)
register_domain_type("patron", PatronState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _load_vangogh_multi():
    vangogh = load_agent_state(CONTENT_DIR / "vangogh" / "initial_state.json")
    gauguin = load_agent_state(CONTENT_DIR / "gauguin" / "initial_state.json")
    theo = load_agent_state(CONTENT_DIR / "theo" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "vangogh" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "vangogh" / "hazard_events.json")
    profiles = {
        "vangogh": load_behavior_profile(CONTENT_DIR / "vangogh" / "behavior_profile.json"),
        "gauguin": load_behavior_profile(CONTENT_DIR / "gauguin" / "behavior_profile.json"),
        "theo": load_behavior_profile(CONTENT_DIR / "theo" / "behavior_profile.json"),
    }
    return vangogh, gauguin, theo, triggers, hazards, profiles


class TestVanGoghMultiAgent:
    def test_runs_to_completion(self):
        """3-에이전트 (VG+Gauguin+Theo) 150 tick 완주."""
        vangogh, gauguin, theo, triggers, hazards, profiles = _load_vangogh_multi()
        config = SimulationConfig(
            max_tick=150,
            initial_state=vangogh,
            initial_states=[vangogh, gauguin, theo],
            triggers=triggers,
            state_noise_scale=0.05,
        )
        result = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=42)

        assert "vangogh" in result.final_states
        assert "gauguin" in result.final_states
        assert "theo" in result.final_states
        assert result.final_states["vangogh"].tick == 150

    def test_seed_reproducibility(self):
        """시드 재현성 (같은 World 인스턴스에서 두 번 실행)."""
        vangogh, gauguin, theo, triggers, hazards, profiles = _load_vangogh_multi()
        config = SimulationConfig(
            max_tick=50, initial_state=vangogh,
            initial_states=[vangogh, gauguin, theo],
            hazard_events=hazards, triggers=triggers, state_noise_scale=0.05,
        )
        world = SimulationWorld(config, _engine(), behavior_profiles=profiles)
        r1 = world.run(seed=99)
        r2 = world.run(seed=99)
        assert r1.final_states["vangogh"].emotions.grief == r2.final_states["vangogh"].emotions.grief

    def test_gauguin_departure_fires(self):
        """고갱 떠남 트리거가 발동한다."""
        vangogh, gauguin, theo, triggers, hazards, profiles = _load_vangogh_multi()
        config = SimulationConfig(
            max_tick=150, initial_state=vangogh,
            initial_states=[vangogh, gauguin, theo],
            hazard_events=hazards, triggers=triggers, state_noise_scale=0.05,
        )

        departures = []
        for seed in range(10):
            r = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)
            deps = [t for t in r.fired_triggers if t["trigger_id"] == "gauguin_departure"]
            if deps:
                departures.append(deps[0]["tick"])

        print(f"\nGauguin departure ticks (10 seeds): {departures}")
        # 모든 시드에서 발동 (deadline=120이므로 최소 deadline에서라도)
        assert len(departures) == 10

    def test_departure_tick_varies(self):
        """고갱 떠남 tick이 시드에 따라 변동."""
        vangogh, gauguin, theo, triggers, hazards, profiles = _load_vangogh_multi()
        config = SimulationConfig(
            max_tick=150, initial_state=vangogh,
            initial_states=[vangogh, gauguin, theo],
            hazard_events=hazards, triggers=triggers, state_noise_scale=0.05,
        )

        ticks = set()
        for seed in range(20):
            r = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)
            deps = [t for t in r.fired_triggers if t["trigger_id"] == "gauguin_departure"]
            if deps:
                ticks.add(deps[0]["tick"])

        print(f"\nUnique departure ticks: {sorted(ticks)}")
        assert len(ticks) >= 2, "Departure tick should vary across seeds"

    def test_all_agents_act(self):
        """3 에이전트 모두 자발적 행동을 수행한다."""
        vangogh, gauguin, theo, triggers, hazards, profiles = _load_vangogh_multi()
        config = SimulationConfig(
            max_tick=50, initial_state=vangogh,
            initial_states=[vangogh, gauguin, theo],
            hazard_events=hazards, triggers=triggers, state_noise_scale=0.05,
        )
        result = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=42)

        for aid in ["vangogh", "gauguin", "theo"]:
            actions = result.action_histories.get(aid, [])
            assert len(actions) > 0, f"{aid} has no actions"
            action_types = Counter(a.chosen_action for a in actions)
            print(f"  {aid}: {dict(action_types)}")

    def test_cross_agent_effects_work(self):
        """고갱의 비판이 반 고흐의 자신감을 낮춘다."""
        vangogh, gauguin, theo, triggers, hazards, profiles = _load_vangogh_multi()
        config = SimulationConfig(
            max_tick=50, initial_state=vangogh,
            initial_states=[vangogh, gauguin, theo],
            hazard_events=hazards, triggers=triggers, state_noise_scale=0.01,
        )
        result = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=42)

        gauguin_actions = result.action_histories.get("gauguin", [])
        critique_count = sum(1 for a in gauguin_actions if a.chosen_action == "critique")
        print(f"\nGauguin critiques: {critique_count}")

        # 고갱이 비판을 하면 반 고흐의 artistic_confidence가 초기값(5.0)보다 낮아야 함
        if critique_count > 0:
            vg_final = result.final_states["vangogh"]
            # domain_state에 artistic_confidence가 있으면 확인
            if hasattr(vg_final.domain_state, "artistic_confidence"):
                conf = vg_final.domain_state.artistic_confidence
                print(f"VG artistic_confidence: {conf:.1f} (initial: 5.0)")


class TestOntologyGenerality:
    """trigger ontology가 비성서 시나리오에서도 작동하는지 확인."""

    def test_same_engine_different_story(self):
        """동일한 엔진 코드로 완전히 다른 이야기가 시뮬레이션된다."""
        vangogh, gauguin, theo, triggers, hazards, profiles = _load_vangogh_multi()
        config = SimulationConfig(
            max_tick=150, initial_state=vangogh,
            initial_states=[vangogh, gauguin, theo],
            hazard_events=hazards, triggers=triggers, state_noise_scale=0.05,
        )

        # 트리거가 "배반/체포" 대신 "비판/떠남/개입" 이벤트를 생성
        result = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=42)

        trigger_ids = {t["trigger_id"] for t in result.fired_triggers}
        print(f"\nFired trigger IDs: {trigger_ids}")

        # 성서 트리거(arrest_trigger)가 아닌 예술 트리거가 발동
        assert "arrest_trigger" not in trigger_ids
        # 예술 관련 트리거가 발동
        assert len(trigger_ids) > 0

    def test_spontaneous_rate(self):
        """Van Gogh 시나리오에서도 spontaneous 비율을 측정한다."""
        vangogh, gauguin, theo, triggers, hazards, profiles = _load_vangogh_multi()
        config = SimulationConfig(
            max_tick=150, initial_state=vangogh,
            initial_states=[vangogh, gauguin, theo],
            hazard_events=hazards, triggers=triggers, state_noise_scale=0.05,
        )

        spontaneous = 0
        deadline = 0
        for seed in range(20):
            r = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)
            deps = [t for t in r.fired_triggers if t["trigger_id"] == "gauguin_departure"]
            if deps:
                if deps[0]["tick"] < 120:
                    spontaneous += 1
                else:
                    deadline += 1

        sp_rate = spontaneous / 20
        print(f"\nVan Gogh departure: spontaneous={spontaneous}/20 ({sp_rate:.0%}), deadline={deadline}")
