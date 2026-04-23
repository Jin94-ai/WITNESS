"""Training sample extraction for v1.0 Latent Drive learning.

MultiAgentResult → (state_t, action_t, event_t, state_{t+1}) 튜플.
v1.0 Stage 2 학습 파이프라인(DESIGN_LATENT_DRIVE.md §3.2)의 데이터 준비 계층.

형식 (example):
    TrainingSample(
        agent_id="<agent>",
        tick=150,
        state=AgentState @tick 150,
        action="withdraw",
        event_ids=["voluntary"],  # 이 tick에 발동한 event
        next_state=AgentState @tick 151 (또는 다음 snapshot)
    )

설계 원칙:
- Neural model에 입력할 raw tuple만 반환 (feature 추출은 학습 코드에서)
- snapshot_interval 다를 수 있으므로 next_state는 "next recorded tick"의 상태
- event 시퀀스는 state 전이에 영향 준 것만 (tick-local)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.core.state import AgentState


@dataclass
class TrainingSample:
    """단일 학습 샘플 — (state, action, event, next_state)."""

    agent_id: str
    tick: int
    state: AgentState
    action: str | None
    """이 tick에 선택된 행동 (여러 개면 첫 action)."""
    event_ids: list[str]
    """이 tick에 발생한 external/hazard/trigger event IDs."""
    next_state: AgentState
    """다음 recorded snapshot의 상태."""
    next_tick: int

    @property
    def tick_delta(self) -> int:
        return self.next_tick - self.tick


def extract_samples(result: Any) -> list[TrainingSample]:
    """MultiAgentResult (또는 호환 객체) → TrainingSample 목록.

    Args:
        result: state_snapshots, action_histories, fired_events,
                fired_triggers 속성을 갖는 객체.

    Returns:
        시간 정렬된 agent-tick 샘플 목록.
    """
    snapshots: dict[str, dict[int, AgentState]] = getattr(result, "state_snapshots", {})
    actions: dict[str, list] = getattr(result, "action_histories", {})
    fired_events: list[dict] = getattr(result, "fired_events", [])
    fired_triggers: list[dict] = getattr(result, "fired_triggers", [])

    # tick → event IDs 매핑 (모든 agent 공유; 향후 agent별 분리 가능)
    tick_events: dict[int, list[str]] = {}
    for ev in fired_events:
        tick_events.setdefault(ev.get("tick", -1), []).append(ev.get("event_id", "?"))
    for trig in fired_triggers:
        t = trig.get("tick", -1)
        tick_events.setdefault(t, []).append(f"trigger:{trig.get('trigger_id', '?')}")

    # agent별 action 인덱스 (tick → chosen_action)
    per_agent_action: dict[str, dict[int, str]] = {}
    for agent_id, records in actions.items():
        per_agent_action[agent_id] = {r.tick: r.chosen_action for r in records}

    samples: list[TrainingSample] = []
    for agent_id, agent_snaps in snapshots.items():
        sorted_ticks = sorted(agent_snaps.keys())
        for i in range(len(sorted_ticks) - 1):
            t = sorted_ticks[i]
            t_next = sorted_ticks[i + 1]
            state = agent_snaps[t]
            next_state = agent_snaps[t_next]
            action = per_agent_action.get(agent_id, {}).get(t)
            events = tick_events.get(t, [])
            samples.append(TrainingSample(
                agent_id=agent_id,
                tick=t,
                state=state,
                action=action,
                event_ids=events,
                next_state=next_state,
                next_tick=t_next,
            ))

    # agent_id 다음 tick 순 정렬
    samples.sort(key=lambda s: (s.agent_id, s.tick))
    return samples


def state_to_feature_vector(state: AgentState) -> list[float]:
    """AgentState → 플랫 feature vector (학습 입력용, 12-dim baseline).

    **v1.0 baseline**: 12-feature (emotions + physical + slow_state). backward
    compat + emotion-driven 시나리오에 충분.

    Domain-driven (e.g. regime-transition) 시나리오는
    `state_to_feature_vector_extended`를 사용 (Iter 67).
    """
    return [
        state.emotions.fear,
        state.emotions.hope,
        state.emotions.grief,
        state.emotions.confusion,
        state.emotions.love,
        state.physical.fatigue,
        state.physical.hunger,
        state.physical.health,
        state.slow_state.moral_injury,
        state.slow_state.identity_shift,
        state.slow_state.event_trauma,
        state.slow_state.trust_scar,
    ]


def state_to_feature_vector_extended(state: AgentState) -> list[float]:
    """12 baseline + domain_state.to_feature_vector() 동적 append (Iter 67).

    `state.domain_state`가 `to_feature_vector()` 메서드를 정의하면 그 벡터를
    base 뒤에 붙인다. 미정의면 base만 반환 (=state_to_feature_vector와 동일).

    길이는 scenario마다 다를 수 있음. 학습 pipeline은 첫 sample 길이로 고정.
    """
    base = state_to_feature_vector(state)
    domain = state.domain_state
    if domain is not None and hasattr(domain, "to_feature_vector"):
        try:
            extra = list(domain.to_feature_vector())
            return base + [float(x) for x in extra]
        except Exception:
            # domain feature 추출 실패 시 base만 반환 (안전)
            return base
    return base


def samples_to_feature_matrix(
    samples: list[TrainingSample],
) -> tuple[list[list[float]], list[list[float]], list[str | None]]:
    """샘플 목록 → (X, Y, actions) feature matrix.

    Returns:
        X: state feature vectors (n × 12)
        Y: next_state feature vectors
        actions: 각 샘플의 action (문자열 또는 None)
    """
    X = [state_to_feature_vector(s.state) for s in samples]
    Y = [state_to_feature_vector(s.next_state) for s in samples]
    actions = [s.action for s in samples]
    return X, Y, actions


@dataclass
class SampleStatistics:
    """Training dataset sanity check (Stage 2 pre-training 진단).

    DESIGN_LATENT_DRIVE.md §3.3 — class imbalance / event sparsity 감지용.
    """

    n_samples: int
    n_agents: int
    agent_counts: dict[str, int]
    action_counts: dict[str, int]
    event_rate: float
    """비어있지 않은 event_ids를 가진 샘플 비율."""
    avg_tick_delta: float
    """state_snapshot 간 평균 tick 간격."""
    feature_dim: int

    @property
    def most_common_action(self) -> tuple[str, int] | None:
        if not self.action_counts:
            return None
        return max(self.action_counts.items(), key=lambda kv: kv[1])

    @property
    def action_imbalance_ratio(self) -> float:
        """max/min action count 비율. 1.0=완벽 균등, ∞=극단 불균형.

        Stage 2 학습 시 class weight 조정 기준으로 사용.
        """
        if not self.action_counts:
            return 0.0
        counts = list(self.action_counts.values())
        lo = min(counts)
        return (max(counts) / lo) if lo > 0 else float("inf")


def summarize_samples(samples: list[TrainingSample]) -> SampleStatistics:
    """TrainingSample 목록 → 분포 요약.

    Stage 2 학습 전 diagnostic. 실제 학습은 이 통계를 보고
    minority action에 class weight를 줄지 결정.
    """
    if not samples:
        return SampleStatistics(
            n_samples=0, n_agents=0,
            agent_counts={}, action_counts={},
            event_rate=0.0, avg_tick_delta=0.0, feature_dim=12,
        )
    agent_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    n_with_events = 0
    total_delta = 0
    for s in samples:
        agent_counts[s.agent_id] = agent_counts.get(s.agent_id, 0) + 1
        if s.action is not None:
            action_counts[s.action] = action_counts.get(s.action, 0) + 1
        if s.event_ids:
            n_with_events += 1
        total_delta += s.tick_delta
    return SampleStatistics(
        n_samples=len(samples),
        n_agents=len(agent_counts),
        agent_counts=agent_counts,
        action_counts=action_counts,
        event_rate=n_with_events / len(samples),
        avg_tick_delta=total_delta / len(samples),
        feature_dim=12,
    )


# =====================================================================
# Drive-action separability diagnostic (Iter 64)
# =====================================================================
# Stage 2 pre-training 진단: 각 action class가 현재 drive space에서
# 얼마나 구별되는가? drive_mean이 action 간 크게 다르면 classifier가
# 학습 가능; 비슷하면 feature 증가 또는 모델 용량 확장 필요 지표.


@dataclass
class DriveActionDiagnostic:
    """특정 action class의 drive 분포 요약.

    action 필드가 같은 sample들을 묶어 drive vector의 per-dim 평균/std 계산.
    Stage 2에서 action classifier loss 수렴성 미리 점검용.
    """

    action_id: str
    n_samples: int
    drive_mean: list[float]
    drive_std: list[float]


def compute_drive_action_diagnostics(
    samples: list[TrainingSample],
    encoder: Any,  # LatentDriveEncoder (duck typed to avoid circular import)
) -> list[DriveActionDiagnostic]:
    """각 action에 대해 해당 샘플 상태의 drive 분포 계산.

    Args:
        samples: TrainingSample 목록.
        encoder: `.encode(state, history)` 메서드를 가진 encoder.

    Returns:
        action_id별 DriveActionDiagnostic (n_samples>=2일 때만).
        None action (voluntary skip)은 제외.
    """
    import numpy as np

    by_action: dict[str, list[list[float]]] = {}
    for s in samples:
        if s.action is None:
            continue
        drive = encoder.encode(s.state, history=None)
        by_action.setdefault(s.action, []).append(drive.values)

    results: list[DriveActionDiagnostic] = []
    for action_id, vectors in by_action.items():
        if len(vectors) < 2:
            continue
        arr = np.array(vectors, dtype=np.float64)
        results.append(DriveActionDiagnostic(
            action_id=action_id,
            n_samples=arr.shape[0],
            drive_mean=[float(m) for m in arr.mean(axis=0)],
            drive_std=[float(s) for s in arr.std(axis=0)],
        ))
    # n_samples 내림차순
    results.sort(key=lambda d: d.n_samples, reverse=True)
    return results


def drive_class_separability(
    diagnostics: list[DriveActionDiagnostic],
) -> float:
    """Between-class / within-class variance ratio (일종의 Fisher 척도).

    클수록 action class가 drive 공간에서 잘 분리. Stage 2 학습 prior.

    Returns:
        1.0 이상이면 "분리 가능" 신호, 1.0 미만이면 클래스 섞임.
        action이 2개 미만이면 0.0 반환.
    """
    import numpy as np
    if len(diagnostics) < 2:
        return 0.0

    all_means = np.array([d.drive_mean for d in diagnostics])  # (K, d)
    overall_mean = all_means.mean(axis=0)
    between = float(((all_means - overall_mean) ** 2).sum())

    total_within = 0.0
    for d in diagnostics:
        # per-class variance in drive space = sum of per-dim variance
        total_within += float(sum(v ** 2 for v in d.drive_std))
    if total_within == 0:
        return 0.0
    return between / total_within
