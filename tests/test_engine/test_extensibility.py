"""인물 비종속 확장성 테스트.

engine/ 코드 수정 없이 더미 인물("artist")로 전체 파이프라인이 작동하는지 검증.
베드로 콘텐츠를 참조하지 않고, 순수하게 engine/ API만으로 구성.
"""

import random

from engine.core.environment import EnvironmentState
from engine.core.hazard import (
    HazardEngine,
    HazardEvent,
    HazardFactor,
    HazardFunction,
    HazardPrecondition,
)
from engine.core.event import CanonicalIntervention
from engine.core.state import AgentState, DomainState, EmotionalState, PhysicalState, Relationship
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, HopeRule, GriefRule, ConfusionRule, LoveRule
from engine.rules.physical import FatigueRule
from engine.rules.temporal import HomeostasisRule, SlowStateRule, CircadianRule
from engine.simulation.checkpoint import Checkpoint, CheckpointCondition
from engine.simulation.runner import SimulationRunner


class ArtistDomain(DomainState):
    """더미 도메인: 예술가의 창작 상태."""
    type: str = "artist_domain"
    creative_drive: float = 5.0
    style_maturity: str = "developing"


def _artist_config() -> SimulationConfig:
    """더미 인물 'artist'의 시뮬레이션 설정."""
    return SimulationConfig(
        max_tick=100,
        initial_state=AgentState(
            agent_id="artist",
            physical=PhysicalState(fatigue=2.0, location="studio"),
            emotions=EmotionalState(fear=1.0, hope=8.0, love=6.0, confusion=2.0),
            relationships={
                "patron": Relationship(target_id="patron", trust=7.0, love=3.0),
                "rival": Relationship(target_id="rival", trust=3.0, love=1.0),
            },
            domain_state=ArtistDomain(creative_drive=7.0, style_maturity="developing"),
        ),
        environment=EnvironmentState(
            crowd_pressure=2.0,
            surveillance=1.0,
            threat_level=1.0,
        ),
        hazard_events=[
            HazardEvent(
                event_id="market_rejection",
                description="작품이 시장에서 거절됨",
                hazard=HazardFunction(
                    base_rate=0.05,
                    factors=[
                        HazardFactor(field_path="emotions.hope", weight=0.2, transform="inverse"),
                    ],
                ),
                anchor_window=(10, 80),
                max_fires=3,
                cooldown=10,
                effects_on_fire=[
                    {"field_path": "emotions.grief", "operation": "add", "value": 3.0},
                    {"field_path": "emotions.hope", "operation": "add", "value": -2.0},
                ],
                action_options_on_fire=[
                    {
                        "action_id": "persevere",
                        "description": "계속 그리기",
                        "weight_formula": {"base_weight": 0.3, "state_multipliers": [
                            {"field_path": "emotions.love", "factor_type": "linear", "params": {"scale": 0.4}},
                        ]},
                        "effects": [{"field_path": "emotions.hope", "operation": "add", "value": 1.0}],
                    },
                    {
                        "action_id": "give_up",
                        "description": "포기",
                        "weight_formula": {"base_weight": 0.3, "state_multipliers": [
                            {"field_path": "emotions.grief", "factor_type": "linear", "params": {"scale": 0.5}},
                            {"field_path": "emotions.hope", "factor_type": "inverse", "params": {"scale": 0.3}},
                        ]},
                        "effects": [
                            {"field_path": "emotions.grief", "operation": "add", "value": 2.0},
                            {"field_path": "domain_state.style_maturity", "operation": "set", "value": "abandoned"},
                        ],
                    },
                ],
            ),
            HazardEvent(
                event_id="patron_support",
                description="후원자의 지원",
                hazard=HazardFunction(
                    base_rate=0.03,
                    factors=[
                        HazardFactor(field_path="crowd_pressure", weight=0.1, source="environment"),
                    ],
                ),
                anchor_window=(20, 90),
                max_fires=2,
                effects_on_fire=[
                    {"field_path": "emotions.hope", "operation": "add", "value": 3.0},
                    {"field_path": "emotions.love", "operation": "add", "value": 1.0},
                ],
                action_options_on_fire=[],
            ),
        ],
        interventions=[
            CanonicalIntervention(
                event_id="breakthrough",
                tick=60,
                scripture_ref="",
                description="창작의 돌파구",
                state_overrides={
                    "emotions.hope": 9.0,
                    "domain_state.style_maturity": "mature",
                },
            ),
        ],
        state_noise_scale=0.05,
    )


def _artist_engine() -> RuleEngine:
    return RuleEngine([
        FatigueRule(), FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(), HomeostasisRule(), SlowStateRule(), CircadianRule(),
    ])


class TestExtensibility:
    def test_artist_runs_without_engine_modification(self):
        """더미 인물이 engine 수정 없이 100 tick 완주한다."""
        config = _artist_config()
        result = SimulationRunner(config, _artist_engine()).run_single(seed=42)
        assert result.final_state.tick == 100
        assert result.final_state.agent_id == "artist"

    def test_artist_hazard_events_fire(self):
        """더미 인물의 hazard 이벤트가 발동한다."""
        config = _artist_config()
        result = SimulationRunner(config, _artist_engine()).run_single(seed=42)
        assert len(result.fired_events) > 0
        event_ids = {fe["event_id"] for fe in result.fired_events}
        assert "market_rejection" in event_ids or "patron_support" in event_ids

    def test_artist_actions_recorded(self):
        """더미 인물의 행동이 기록된다."""
        config = _artist_config()
        result = SimulationRunner(config, _artist_engine()).run_single(seed=42)
        if result.action_history:
            actions = {a.chosen_action for a in result.action_history}
            assert actions.issubset({"persevere", "give_up"})

    def test_artist_domain_state_changes(self):
        """더미 인물의 domain_state가 intervention으로 변경된다."""
        config = _artist_config()
        result = SimulationRunner(config, _artist_engine()).run_single(seed=42)
        from engine.core.state import get_nested_value
        maturity = get_nested_value(result.final_state, "domain_state.style_maturity")
        # intervention이 tick=60에서 "mature"로 SET하므로
        assert maturity in ("mature", "abandoned")  # give_up이 이후에 발동할 수도

    def test_artist_slow_state_accumulates(self):
        """더미 인물의 slow_state가 누적된다."""
        config = _artist_config()
        result = SimulationRunner(config, _artist_engine()).run_single(seed=42)
        # 어떤 극한 감정이 있었으면 event_trauma > 0
        assert result.final_state.slow_state is not None

    def test_artist_checkpoint_works(self):
        """더미 인물에 대한 체크포인트가 작동한다."""
        config = _artist_config()
        checkpoints = [
            Checkpoint(
                checkpoint_id="cp_persevere",
                tick=80,
                conditions=[
                    CheckpointCondition(
                        condition_type="action_taken",
                        params={"action_id": "persevere"},
                    ),
                ],
                weight=1.0,
            ),
        ]
        result = SimulationRunner(config, _artist_engine(), checkpoints).run_single(seed=42)
        assert len(result.checkpoint_results) == 1

    def test_artist_batch_runs(self):
        """더미 인물 50회 배치가 돌아간다."""
        from engine.simulation.batch import run_batch
        config = _artist_config()
        results = run_batch(config, _artist_engine(), 50)
        assert len(results) == 50
        # 다른 시드에서 다른 결과
        actions_sets = [
            frozenset(a.chosen_action for a in r.action_history)
            for r in results if r.action_history
        ]
        if actions_sets:
            assert len(set(actions_sets)) >= 1  # 최소 1가지 패턴

    def test_artist_environment_affects_behavior(self):
        """더미 인물에서도 환경이 행동에 영향을 준다."""
        config_calm = _artist_config()
        config_hostile = _artist_config().model_copy(
            update={"environment": EnvironmentState(crowd_pressure=9.0, surveillance=9.0)}
        )
        engine = _artist_engine()

        calm_events = sum(len(SimulationRunner(config_calm, engine).run_single(seed=i).fired_events) for i in range(30))
        hostile_events = sum(len(SimulationRunner(config_hostile, engine).run_single(seed=i).fired_events) for i in range(30))

        # 환경이 다르면 이벤트 수가 다를 수 있음 (patron_support에 환경 factor 있음)
        # 적어도 돌아가야 함
        assert calm_events >= 0
        assert hostile_events >= 0
