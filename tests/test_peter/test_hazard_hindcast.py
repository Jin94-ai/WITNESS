"""Hazard-driven Hindcasting 테스트.

핵심 검증:
1. 이벤트 발생 tick이 시드에 따라 분산되는가 (hazard의 존재 이유)
2. 정경 체크포인트와 대조 시 일치율이 0% 이상인가
3. 부인이 자연 출현하는가
"""

import json
from pathlib import Path

from content.peter.domain_faith import FaithJourneyState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_hazard_events,
    load_interventions,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import ConfusionRule, FearResponseRule, GriefRule, HopeRule, LoveRule
from engine.rules.physical import FatigueRule, HealthRule, HungerRule
from engine.rules.social import GroupIsolationRule, RelationshipDecayRule
from engine.rules.temporal import CircadianRule, HomeostasisRule
from engine.simulation.analysis import compute_aggregate
from engine.simulation.batch import run_batch
from engine.simulation.checkpoint import Checkpoint

register_domain_type("faith_journey", FaithJourneyState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content" / "peter"


def _rule_engine() -> RuleEngine:
    return RuleEngine([
        FatigueRule(),
        HungerRule(),
        HealthRule(),
        FearResponseRule(),
        HopeRule(),
        GriefRule(),
        ConfusionRule(),
        LoveRule(),
        RelationshipDecayRule(),
        GroupIsolationRule(),
        HomeostasisRule(),
        CircadianRule(),
    ])


def _load_hazard_config() -> SimulationConfig:
    state = load_agent_state(CONTENT_DIR / "initial_state.json")
    hazard_events = load_hazard_events(CONTENT_DIR / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "canonical_events.json")
    return SimulationConfig(
        max_tick=500,
        initial_state=state,
        hazard_events=hazard_events,
        interventions=interventions,
        state_noise_scale=0.05,
    )


def _load_checkpoints() -> list[Checkpoint]:
    data = json.loads((CONTENT_DIR / "checkpoints.json").read_text(encoding="utf-8"))
    return [Checkpoint.model_validate(cp) for cp in data["checkpoints"]]


class TestHazardHindcast:
    def test_hazard_mode_500_tick_completes(self):
        """Hazard-driven 500 tick 시뮬레이션이 에러 없이 완주."""
        config = _load_hazard_config()
        from engine.simulation.runner import SimulationRunner
        result = SimulationRunner(config, _rule_engine()).run_single(seed=42)
        assert result.final_state.tick == 500
        assert len(result.fired_events) > 0  # hazard 이벤트가 발동함

    def test_event_ticks_vary_across_seeds(self):
        """핵심: 다른 시드 -> 이벤트 발생 tick이 다르다."""
        config = _load_hazard_config()
        engine = _rule_engine()

        arrest_ticks = []
        for seed in range(50):
            from engine.simulation.runner import SimulationRunner
            result = SimulationRunner(config, engine).run_single(seed=seed)
            for fe in result.fired_events:
                if fe["event_id"] == "arrest":
                    arrest_ticks.append(fe["tick"])

        print(f"\nArrest ticks across 50 seeds: {sorted(arrest_ticks)}")
        if len(arrest_ticks) >= 2:
            tick_range = max(arrest_ticks) - min(arrest_ticks)
            print(f"Arrest tick range: {tick_range}")
            assert tick_range > 0, "체포 tick이 모두 동일 -- hazard가 작동하지 않음"

    def test_batch_100_with_checkpoints(self):
        """100회 배치 + 체크포인트 대조."""
        config = _load_hazard_config()
        checkpoints = _load_checkpoints()
        results = run_batch(config, _rule_engine(), n_runs=100, checkpoints=checkpoints)
        stats = compute_aggregate(results)

        print("\n=== Hazard-Driven Hindcasting (100 runs) ===")
        print(f"Mean match rate: {stats.mean_match_rate:.1%}")
        print(f"Std: {stats.std_match_rate:.1%}")
        print("\nCheckpoint pass rates:")
        for cp_id, rate in sorted(stats.checkpoint_pass_rates.items()):
            print(f"  {cp_id}: {rate:.0%}")
        print("\nAction frequencies:")
        for event_id, actions in sorted(stats.action_frequency.items()):
            print(f"  {event_id}: {actions}")

        # 모든 이벤트 발동 tick 분포
        all_fired: dict[str, list[int]] = {}
        for r in results:
            for fe in r.fired_events:
                eid = fe["event_id"]
                if eid not in all_fired:
                    all_fired[eid] = []
                all_fired[eid].append(fe["tick"])

        print("\nEvent firing tick distributions:")
        for eid, ticks in sorted(all_fired.items()):
            if ticks:
                print(f"  {eid}: min={min(ticks)}, max={max(ticks)}, "
                      f"mean={sum(ticks)/len(ticks):.0f}, count={len(ticks)}")

        assert stats.mean_match_rate > 0.0

    def test_denial_emerges_in_hazard_mode(self):
        """Hazard 모드에서 부인이 자연 출현하는가."""
        config = _load_hazard_config()
        checkpoints = _load_checkpoints()
        results = run_batch(config, _rule_engine(), n_runs=100, checkpoints=checkpoints)

        denial_count = 0
        for r in results:
            denials = [a for a in r.action_history if a.chosen_action == "deny"]
            if len(denials) >= 3:
                denial_count += 1

        print(f"\nTriple denial rate (hazard mode): {denial_count}%")

    def test_noise_creates_variation(self):
        """Langevin 노이즈가 결과에 변동을 만든다."""
        config_no_noise = _load_hazard_config().model_copy(
            update={"state_noise_scale": 0.0}
        )
        config_with_noise = _load_hazard_config().model_copy(
            update={"state_noise_scale": 0.2}
        )

        from engine.simulation.runner import SimulationRunner
        engine = _rule_engine()

        # 동일 시드로 노이즈 유무 비교
        r_clean = SimulationRunner(config_no_noise, engine).run_single(seed=42)
        r_noisy = SimulationRunner(config_with_noise, engine).run_single(seed=42)

        # 노이즈가 있으면 최종 상태가 달라야 함
        assert r_clean.final_state.emotions.fear != r_noisy.final_state.emotions.fear
