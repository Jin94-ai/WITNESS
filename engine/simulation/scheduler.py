"""에이전트 스케줄러.

다중 에이전트 시뮬레이션에서 에이전트의 활성화 순서를 관리한다.
Mesa의 BaseScheduler를 참고하되 자체 구현.
"""

from __future__ import annotations

import random
from typing import Literal


class AgentScheduler:
    """에이전트 활성화 순서 관리.

    지원 모드:
    - sequential: 고정 순서로 활성화 (결정적)
    - random: 매 tick 랜덤 순서 (순서 효과 제거)
    - simultaneous: 모든 에이전트가 같은 상태를 보고 동시 행동 (상태는 tick 끝에 일괄 반영)
    """

    def __init__(
        self,
        agent_ids: list[str],
        mode: Literal["sequential", "random", "simultaneous"] = "random",
    ) -> None:
        self._agent_ids = list(agent_ids)
        self._mode = mode

    @property
    def agent_ids(self) -> list[str]:
        return list(self._agent_ids)

    @property
    def mode(self) -> str:
        return self._mode

    def get_activation_order(self, rng: random.Random) -> list[str]:
        """이번 tick의 에이전트 활성화 순서를 반환한다."""
        if self._mode == "random":
            order = list(self._agent_ids)
            rng.shuffle(order)
            return order
        # sequential, simultaneous: 고정 순서
        return list(self._agent_ids)

    def add_agent(self, agent_id: str) -> None:
        """에이전트를 추가한다."""
        if agent_id not in self._agent_ids:
            self._agent_ids.append(agent_id)

    def remove_agent(self, agent_id: str) -> None:
        """에이전트를 제거한다."""
        self._agent_ids = [a for a in self._agent_ids if a != agent_id]
