"""Phase A -- Forced Action Sampling.

ChatGPT/Gemini 공통 지적 (`WITNESS_SPIKE_6_LEARNABLE_DATA.md` §2):
이전 파이프라인은 initial-state 설정 후 rollout 돌리면 `follow_closely`
attractor로 몇 tick 안에 흡수되어 rare action sample 확보 실패. 이번엔
``DecisionPolicy`` weight-mask로 각 target state에서 해당 action을
강제 선택 (Phase 1 진단 §1.5에서 100% 작동 확인).

Scope: behavior_profile의 voluntary 6 action만 (follow_closely, pray,
discuss_with_disciples, assert_loyalty, withdraw_in_fear, weep).
Canonical event action 9개는 별도 phase.

Rule #6 범위 확인 (spec §0.3 verbatim):
  "engine 수정 금지이지만 scripts/ 에서 SimulationWorld state를 직접
   patching하는 것은 허용. 이전 파이프라인에서 이를 회피해서
   initial-state로 근사한 결과 rare action 실패. 이번에는 허용되는
   범위 내에서 '난폭한 확충' 가능."

즉 forced-policy 주입은 Rule #6 **문구 안**. engine 시그니처 무수정.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.core.event import ActionOption  # noqa: E402
from engine.core.state import AgentState  # noqa: E402
from engine.simulation.training_samples import (  # noqa: E402
    state_to_feature_vector,
)
from scripts.data_pipeline._common import (  # noqa: E402
    make_peter_state,
    register_domain_types,
    run_peter_with_policy,
)

# ---------------------------------------------------------------------
# Boundary state definitions -- diag 1 action means + weight_formula 방향
# ---------------------------------------------------------------------
#
# 각 action의 boundary 영역은 두 원칙으로:
#  (1) action의 preconditions가 반드시 만족 (가능성 유지)
#  (2) weight_formula의 linear factor가 높은 값 쪽으로 (자연 선호 영역)
#
# 이 영역을 grid sampling으로 덮고, 각 state에서 forced policy로
# target action을 강제 선택. 결과 (state, action) 쌍 수집.

BOUNDARY_ZONES: dict[str, dict[str, tuple[float, float]]] = {
    "follow_closely": {
        "love": (6.0, 10.0),  # weight +0.15 × love
        "fear": (0.0, 3.0),   # weight -0.1 × fear (inverse)
        "hope": (5.0, 10.0),
        "confusion": (0.0, 5.0),
        "grief": (0.0, 3.0),
    },
    "pray": {
        "grief": (3.0, 8.0),  # weight +0.15 × grief
        "hope": (5.0, 10.0),  # weight +0.1 × hope
        "fatigue": (6.0, 10.0),
        "confusion": (4.0, 8.0),
        "moral_injury": (1.0, 6.0),
    },
    "discuss_with_disciples": {
        "confusion": (3.0, 8.0),  # weight +0.1 × confusion
        "love": (5.0, 10.0),      # weight +0.05 × love
        "hope": (5.0, 10.0),
        "fear": (0.0, 5.0),
    },
    "assert_loyalty": {
        # precondition: love >= 6.0
        "love": (7.0, 10.0),  # weight +0.2 × love
        "fear": (0.0, 4.0),   # weight -0.15 × fear (inverse)
        "hope": (7.0, 10.0),
        "confusion": (0.0, 4.0),
    },
    "withdraw_in_fear": {
        # precondition: fear >= 6.0
        "fear": (7.0, 10.0),  # weight +0.3 × fear
        "love": (0.0, 4.0),   # weight -0.1 × love (inverse)
        "hope": (0.0, 5.0),
        "fatigue": (3.0, 9.0),
        "moral_injury": (0.0, 7.0),
    },
    "weep": {
        # precondition: moral_injury >= 3.0
        "moral_injury": (5.0, 10.0),
        "grief": (5.0, 10.0),
        "fear": (3.0, 9.0),
        "event_trauma": (2.0, 9.0),
        "identity_shift": (-6.0, -1.0),
    },
}


# ---------------------------------------------------------------------
# Forced-policy adapter (engine/policies 에 둘 수도 있지만 scope은
# pipeline 전용이라 여기에 둠)
# ---------------------------------------------------------------------

class ForcingPolicy:
    """Return weight=100 for target action, 0 for all others.

    Implements the DecisionPolicy Protocol:
        weights(state, options, environment) -> list[float]

    Phase 1 진단 §1.5: weight mask를 통한 forced action 100% 달성.
    """

    def __init__(self, target_action_id: str) -> None:
        self.target = target_action_id

    def weights(
        self, state: AgentState, options: list[ActionOption], environment: Any = None,
    ) -> list[float]:
        return [100.0 if opt.action_id == self.target else 0.0 for opt in options]


# ---------------------------------------------------------------------
# Sampling loop
# ---------------------------------------------------------------------

def _sample_state_in_zone(
    action_id: str, zone: dict[str, tuple[float, float]],
    rng: np.random.Generator,
) -> AgentState:
    """Draw a state uniformly in the boundary zone."""
    kwargs: dict[str, float] = {}
    for field, (lo, hi) in zone.items():
        kwargs[field] = float(rng.uniform(lo, hi))
    # Fill defaults for fields not in the zone (kept mid-range but distinct
    # from baseline constants to move them off the constant plane)
    defaults = {
        "fear": 5.0, "hope": 5.0, "grief": 1.0,
        "confusion": 5.0, "love": 5.0,
        "fatigue": float(rng.uniform(2, 7)),
        "hunger": float(rng.uniform(1, 5)),
        "health": float(rng.uniform(5, 9)),
        "moral_injury": float(rng.uniform(0, 4)),
        "identity_shift": float(rng.uniform(-3, 3)),
        "event_trauma": float(rng.uniform(0, 3)),
        "trust_scar": float(rng.uniform(0, 2)),
    }
    for k, v in defaults.items():
        kwargs.setdefault(k, v)
    return make_peter_state(**kwargs)


def _force_sample_one(
    action_id: str, zone: dict[str, tuple[float, float]],
    rng: np.random.Generator, seed_base: int, idx: int,
) -> tuple[list[float], str] | None:
    """Run a 1-tick simulation with forced policy.

    Returns (feature_vector, action_id) if the forced action fires,
    else None (action not available due to preconditions).
    """
    peter = _sample_state_in_zone(action_id, zone, rng)
    policy = ForcingPolicy(action_id)
    try:
        result = run_peter_with_policy(
            seed=seed_base + idx, max_tick=1,
            peter_override=peter, policies={"peter": policy},
        )
    except Exception:
        return None

    # extract_samples only pairs ticks < max_tick, so with max_tick=1 we
    # cannot read the action-at-tick-1 via samples. Read the action record
    # directly, and pair it with the state the engine saw at selection time
    # (post-rule-engine state at tick 1, from snapshots).
    action_records = result.action_histories.get("peter", [])
    if not action_records:
        return None
    chosen = action_records[0].chosen_action
    if chosen != action_id:
        return None
    snap = result.state_snapshots.get("peter", {})
    state_for_pair = snap.get(1, peter)
    return state_to_feature_vector(state_for_pair), chosen


def harvest_forced(
    *, samples_per_action: int = 300, seed_base: int = 50_000,
) -> dict[str, Any]:
    register_domain_types()
    rng = np.random.default_rng(0)
    all_X: list[list[float]] = []
    all_actions: list[str] = []
    per_action_saved: dict[str, int] = {}
    per_action_attempts: dict[str, int] = {}
    per_action_rejected: dict[str, int] = {}

    for action_id, zone in BOUNDARY_ZONES.items():
        saved = 0
        attempts = 0
        rejected = 0
        # Cap attempts at 4x target to avoid infinite loop on impossible zones
        max_attempts = samples_per_action * 4
        while saved < samples_per_action and attempts < max_attempts:
            res = _force_sample_one(
                action_id, zone, rng, seed_base, attempts + saved * 13,
            )
            attempts += 1
            if res is None:
                rejected += 1
                continue
            feat, aid = res
            all_X.append(feat)
            all_actions.append(aid)
            saved += 1
        per_action_saved[action_id] = saved
        per_action_attempts[action_id] = attempts
        per_action_rejected[action_id] = rejected
        print(
            f"  [forced] {action_id:<26} saved={saved}/{samples_per_action}  "
            f"attempts={attempts}  rejected={rejected}",
        )

    X = np.asarray(all_X, dtype=np.float32) if all_X else np.zeros((0, 12), dtype=np.float32)
    return {
        "X": X,
        "actions": all_actions,
        "source": "forced",
        "per_action_saved": per_action_saved,
        "per_action_attempts": per_action_attempts,
        "per_action_rejected": per_action_rejected,
    }


def main() -> int:
    out = ROOT / "data" / "person" / "pipeline_v2" / "forced"
    out.mkdir(parents=True, exist_ok=True)
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 300

    print(f"[Phase A] Forced sampling -- target {target}/action × "
          f"{len(BOUNDARY_ZONES)} actions")
    harvest = harvest_forced(samples_per_action=target)
    print(f"\n  total samples: {harvest['X'].shape[0]}")
    from collections import Counter
    print(f"  distribution:  {dict(Counter(harvest['actions']))}")

    np.save(out / "X.npy", harvest["X"])
    (out / "meta.json").write_text(
        json.dumps({
            "source": harvest["source"],
            "actions": harvest["actions"],
            "n_samples": int(harvest["X"].shape[0]),
            "per_action_saved": harvest["per_action_saved"],
            "per_action_attempts": harvest["per_action_attempts"],
            "per_action_rejected": harvest["per_action_rejected"],
            "target_per_action": target,
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  saved to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
