"""배치 시뮬레이션 실행.

동일 설정으로 N회 시뮬레이션을 실행하고 결과를 수집한다.
단일 에이전트(SimulationRunner)와 다중 에이전트(SimulationWorld) 모두 지원.
"""

from __future__ import annotations

from typing import Literal

from engine.core.action import AgentBehaviorProfile
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.simulation.checkpoint import Checkpoint
from engine.simulation.runner import SimulationResult, SimulationRunner
from engine.simulation.world import MultiAgentResult, SimulationWorld


def run_batch(
    config: SimulationConfig,
    rule_engine: RuleEngine,
    n_runs: int,
    checkpoints: list[Checkpoint] | None = None,
    seed_base: int = 0,
) -> list[SimulationResult]:
    """N회 단일 에이전트 시뮬레이션을 순차 실행한다.

    Args:
        config: 시뮬레이션 설정
        rule_engine: 규칙 엔진
        n_runs: 실행 횟수
        checkpoints: 체크포인트 목록
        seed_base: 시드 기준값. 각 run의 시드는 seed_base + i.

    Returns:
        SimulationResult 목록
    """
    runner = SimulationRunner(config, rule_engine, checkpoints)
    return [runner.run_single(seed=seed_base + i) for i in range(n_runs)]


def run_multi_batch(
    config: SimulationConfig,
    rule_engine: RuleEngine,
    n_runs: int,
    behavior_profiles: dict[str, AgentBehaviorProfile] | None = None,
    checkpoints: dict[str, list[Checkpoint]] | None = None,
    scheduler_mode: Literal["sequential", "random", "simultaneous"] = "random",
    seed_base: int = 0,
) -> list[MultiAgentResult]:
    """N회 다중 에이전트 시뮬레이션을 순차 실행한다.

    Args:
        config: 시뮬레이션 설정 (initial_states에 여러 에이전트)
        rule_engine: 규칙 엔진
        n_runs: 실행 횟수
        behavior_profiles: 에이전트별 행동 프로파일
        checkpoints: 에이전트별 체크포인트 목록
        scheduler_mode: 활성화 순서 모드
        seed_base: 시드 기준값

    Returns:
        MultiAgentResult 목록
    """
    results = []
    for i in range(n_runs):
        world = SimulationWorld(
            config, rule_engine,
            behavior_profiles=behavior_profiles,
            checkpoints=checkpoints,
            scheduler_mode=scheduler_mode,
        )
        results.append(world.run(seed=seed_base + i))
    return results
