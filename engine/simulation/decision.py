"""행동 결정 시스템.

에이전트가 이벤트에서 어떤 행동을 선택할지 확률적으로 결정한다.
모든 확률 계산은 rng를 통해 시드 재현성을 보장한다.
v0.3: 환경(EnvironmentState)도 가중치 계산에 참여.
Spike 6: 선택적 DecisionPolicy(학습된 정책)를 주입 가능. ``policy=None``이면
기존 규칙 기반 로직과 bit-identical로 동작 (Rule #6 generic 확장 준수,
Rule #11 dual-path fallback 보장).
"""

from __future__ import annotations

import random
from typing import Any

from engine.core.event import ActionOption
from engine.core.state import AgentState


def decide_action(
    state: AgentState,
    options: list[ActionOption],
    rng: random.Random,
    environment: Any = None,
    policy: Any = None,
) -> ActionOption | None:
    """현재 상태/환경을 기반으로 행동을 확률적으로 선택한다.

    Args:
        state: 현재 에이전트 상태
        options: 가능한 행동 목록
        rng: 시드 주입 가능한 난수 생성기
        environment: 환경 상태 (있으면 WeightFormula에 전달)
        policy: 선택적 DecisionPolicy (``weights(state, options, environment)``
                반환). ``None``이면 기존 규칙 기반 로직. ``weights`` 합이 0이면
                abstain으로 간주 → 규칙 기반 폴백 (Rule #11).

    Returns:
        선택된 ActionOption. 유효한 옵션이 없으면 None.
    """
    if not options:
        return None

    valid = [
        opt for opt in options
        if all(p.evaluate(state) for p in opt.preconditions)
    ]

    if not valid:
        return None

    weights: list[float]
    if policy is not None:
        weights = list(policy.weights(state, valid, environment))
        if sum(weights) <= 0:
            # policy abstains → rule-based fallback (Rule #11)
            weights = [
                opt.weight_formula.compute_weight(state, environment)
                for opt in valid
            ]
    else:
        weights = [
            opt.weight_formula.compute_weight(state, environment)
            for opt in valid
        ]

    chosen = rng.choices(valid, weights=weights, k=1)[0]
    return chosen
