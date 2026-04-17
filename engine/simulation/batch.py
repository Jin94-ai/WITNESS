"""배치 시뮬레이션 실행.

동일 설정으로 N회 시뮬레이션을 실행하고 결과를 수집한다.
"""

from __future__ import annotations

from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.simulation.checkpoint import Checkpoint
from engine.simulation.runner import SimulationResult, SimulationRunner


def run_batch(
    config: SimulationConfig,
    rule_engine: RuleEngine,
    n_runs: int,
    checkpoints: list[Checkpoint] | None = None,
    seed_base: int = 0,
) -> list[SimulationResult]:
    """N회 시뮬레이션을 순차 실행한다.

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
