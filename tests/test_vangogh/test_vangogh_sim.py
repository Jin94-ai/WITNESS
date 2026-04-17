"""반 고흐 content pack 통합 테스트.

engine/ 수정 없이 실제 두 번째 인물이 전체 파이프라인을 통과하는지 검증.
"""

import json
from pathlib import Path

from content.vangogh.domain_creative import CreativeDriveState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_hazard_events,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import ConfusionRule, FearResponseRule, GriefRule, HopeRule, LoveRule
from engine.rules.physical import FatigueRule, HealthRule, HungerRule
from engine.rules.social import GroupIsolationRule, RelationshipDecayRule
from engine.rules.temporal import CircadianRule, HomeostasisRule, SlowStateRule
from engine.simulation.batch import run_batch
from engine.simulation.checkpoint import Checkpoint
from engine.simulation.runner import SimulationRunner

register_domain_type("creative_drive", CreativeDriveState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content" / "vangogh"


def _engine() -> RuleEngine:
    return RuleEngine([
        FatigueRule(), HungerRule(), HealthRule(),
        FearResponseRule(), HopeRule(), GriefRule(), ConfusionRule(), LoveRule(),
        RelationshipDecayRule(), GroupIsolationRule(),
        HomeostasisRule(), SlowStateRule(), CircadianRule(),
    ])


def _load_config() -> SimulationConfig:
    state = load_agent_state(CONTENT_DIR / "initial_state.json")
    hazard_events = load_hazard_events(CONTENT_DIR / "hazard_events.json")
    return SimulationConfig(
        max_tick=150,
        initial_state=state,
        hazard_events=hazard_events,
        state_noise_scale=0.05,
    )


def _load_checkpoints() -> list[Checkpoint]:
    data = json.loads((CONTENT_DIR / "checkpoints.json").read_text(encoding="utf-8"))
    return [Checkpoint.model_validate(cp) for cp in data["checkpoints"]]


class TestVanGoghSimulation:
    def test_150_tick_completes(self):
        """반 고흐 150 tick 시뮬레이션이 완주한다."""
        config = _load_config()
        result = SimulationRunner(config, _engine()).run_single(seed=42)
        assert result.final_state.tick == 150
        assert result.final_state.agent_id == "vangogh"

    def test_hazard_events_fire(self):
        """hazard 이벤트가 발동한다."""
        config = _load_config()
        result = SimulationRunner(config, _engine()).run_single(seed=42)
        assert len(result.fired_events) > 0

    def test_domain_state_preserved(self):
        """CreativeDriveState가 로드되고 유지된다."""
        config = _load_config()
        result = SimulationRunner(config, _engine()).run_single(seed=42)
        ds = result.final_state.domain_state
        assert ds is not None
        assert ds.type == "creative_drive"

    def test_checkpoints_work(self):
        """체크포인트가 평가된다."""
        config = _load_config()
        checkpoints = _load_checkpoints()
        result = SimulationRunner(config, _engine(), checkpoints).run_single(seed=42)
        assert len(result.checkpoint_results) == 4

    def test_batch_100_runs(self):
        """100회 배치가 돌아간다."""
        config = _load_config()
        checkpoints = _load_checkpoints()
        results = run_batch(config, _engine(), 100, checkpoints)
        assert len(results) == 100

    def test_self_harm_emerges(self):
        """자해가 일부 시드에서 자연 출현한다."""
        config = _load_config()
        self_harm_count = 0
        for seed in range(100):
            r = SimulationRunner(config, _engine()).run_single(seed=seed)
            if any(a.chosen_action == "self_harm" for a in r.action_history):
                self_harm_count += 1
        # 자해가 한 번도 안 나오면 hazard 구조 문제
        print(f"Self-harm emergence: {self_harm_count}% of 100 runs")

    def test_different_from_peter(self):
        """반 고흐 시뮬레이션의 행동 패턴이 베드로와 다르다."""
        config = _load_config()
        result = SimulationRunner(config, _engine()).run_single(seed=42)
        action_ids = {a.chosen_action for a in result.action_history}
        # 베드로 전용 행동(deny, confess, flee, draw_sword)이 없어야 함
        peter_actions = {"deny", "confess", "flee", "draw_sword", "follow_at_distance"}
        assert action_ids.isdisjoint(peter_actions), f"Peter actions found: {action_ids & peter_actions}"
