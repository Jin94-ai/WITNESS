"""v1.0 Latent Drive Bottleneck Model — Skeleton.

ChatGPT 5차 리뷰 "E안" 구현 기초. 현 단계에서는 **인터페이스 정의만**.
실제 학습 구현은 Stage 2 (월 1.5-2.5) 작업.

아키텍처:
    state + history → Encoder → drive ∈ R^d → {action policy, trigger susceptibility, slow update}

참조:
    DESIGN_LATENT_DRIVE.md — 전체 설계
    TRACE_SCHEMA.md — 로그 구조
"""

from __future__ import annotations

from typing import Any, Protocol

from engine.core.state import AgentState, LatentDriveState


class LatentDriveEncoder(Protocol):
    """State + history → latent drive vector.

    v1.0 Stage 2에서 PyTorch MLP로 구현 예정.
    v0.x 시점 구현체는 identity 또는 random (학습 전).
    """

    def encode(
        self,
        state: AgentState,
        history: list[dict] | None = None,
    ) -> LatentDriveState:
        """현재 state + 최근 history를 latent drive로 인코딩.

        Args:
            state: 현재 agent 상태
            history: 최근 k=10 tick의 action/event 기록 (선택)

        Returns:
            LatentDriveState (values of dim d)
        """
        ...


class LatentDriveActionPolicy(Protocol):
    """Drive-modulated action policy π(a | state, drive)."""

    def action_weights(
        self,
        state: AgentState,
        drive: LatentDriveState,
        available_actions: list[str],
    ) -> dict[str, float]:
        """Drive가 반영된 action별 weight.

        v0.x behavior_profile.json을 대체. 학습 모델이 준비되기 전에는
        symbolic fallback (기존 weights) 사용.
        """
        ...


class LatentDriveTriggerSusceptibility(Protocol):
    """Drive → trigger threshold modulator.

    예: d[shame] 높음 → "withdraw" 이후 "inform_authorities"로 전환 susceptibility 상승.
    """

    def susceptibility_multiplier(
        self,
        state: AgentState,
        drive: LatentDriveState,
        trigger_id: str,
    ) -> float:
        """Trigger threshold에 곱할 multiplier [0.5, 2.0] 권장."""
        ...


class LatentDriveSlowUpdate(Protocol):
    """Drive-modulated slow state evolution.

    예: d[shame] 높고 arrest event 발생 → moral_injury 누적률 상승.
    """

    def modulated_update(
        self,
        state: AgentState,
        drive: LatentDriveState,
    ) -> dict[str, float]:
        """slow_state 각 필드의 update 증폭 계수."""
        ...


class LatentDriveModel:
    """통합 drive 모델 컨테이너.

    v1.0 Stage 2에서 각 컴포넌트를 학습된 neural module로 교체.
    v0.x에서는 skeleton으로 두어 backward compatibility 보장.

    사용 예 (v1.0+, example):
        model = LatentDriveModel.load("<agent_drive>.pt")
        drive = model.encoder.encode(state, history)
        weights = model.policy.action_weights(state, drive, actions)
    """

    def __init__(
        self,
        encoder: LatentDriveEncoder | None = None,
        policy: LatentDriveActionPolicy | None = None,
        susceptibility: LatentDriveTriggerSusceptibility | None = None,
        slow_update: LatentDriveSlowUpdate | None = None,
        dim: int = 5,
    ) -> None:
        """
        Args:
            encoder: state → drive. None이면 모델 비활성화 (v0.x 모드).
            policy: drive → action weights. None이면 symbolic fallback.
            susceptibility: drive → trigger modulation.
            slow_update: drive → slow state modulation.
            dim: latent drive 차원 (권장 3~8, 기본 5).
        """
        self.encoder = encoder
        self.policy = policy
        self.susceptibility = susceptibility
        self.slow_update = slow_update
        self.dim = dim

    def is_active(self) -> bool:
        """학습된 모델이 로드되어 있는지."""
        return self.encoder is not None

    def encode_safe(
        self,
        state: AgentState,
        history: list[dict] | None = None,
    ) -> LatentDriveState | None:
        """Encoder 있으면 drive 반환, 없으면 None.

        v0.x 코드가 이 함수를 호출해도 안전 (None 반환).
        """
        if self.encoder is None:
            return None
        return self.encoder.encode(state, history)


# ============================================================
# Stage 1 placeholder implementations (not learned yet)
# ============================================================


class IdentityEncoder:
    """디버그/테스트용 encoder: state의 일부 필드를 그대로 drive로.

    학습 모델 도입 전 plumbing 검증용.
    """

    def __init__(self, dim: int = 5) -> None:
        self.dim = dim

    def encode(
        self,
        state: AgentState,
        history: list[dict] | None = None,
    ) -> LatentDriveState:
        # 단순 mapping: fear, grief, hope 정규화 + slow_state 2축
        values = [
            state.emotions.fear / 10.0,
            state.emotions.grief / 10.0,
            state.emotions.hope / 10.0,
            state.slow_state.moral_injury / 10.0,
            min(abs(state.slow_state.identity_shift) / 5.0, 1.0),
        ][: self.dim]
        # 부족한 차원은 0으로 채움
        values.extend([0.0] * (self.dim - len(values)))
        return LatentDriveState(values=values, dim=self.dim)


class FixedProjectionEncoder:
    """Non-identity encoder: seeded random projection of state features → drive (Iter 59/60).

    IdentityEncoder → FixedProjection → (future) LearnedPyTorchEncoder 3단계 bridge.
    Stage 2 PyTorch 학습 전이지만, 다음을 증명:
    - Encoder Protocol이 non-identity 구현을 수용
    - drive 값이 state 전체 feature의 비선형 함수로 emerge (tanh projection)
    - 고정 seed로 재현 가능
    - 내부 feature set이 `engine.simulation.training_samples.state_to_feature_vector`
      와 **동일한 12차원** → Stage 2 training loop의 batch input을 그대로 수용

    numpy만 의존 (torch 설치 불필요). 향후 학습 단계에서 PyTorch MLP로 교체 예정;
    이 class의 interface는 동일.

    Feature 벡터 (12차원, **raw scale**, training_samples.state_to_feature_vector와 동일):
        [fear, hope, grief, confusion, love,
         fatigue, hunger, health,
         moral_injury, identity_shift, event_trauma, trust_scar]
    """

    NUM_FEATURES = 12

    def __init__(self, dim: int = 5, seed: int = 0, scale: float = 0.3) -> None:
        import numpy as np
        if dim < 1:
            raise ValueError("dim must be >= 1")
        if dim > 8:
            raise ValueError("FixedProjectionEncoder dim capped at 8 (design guideline)")
        rng = np.random.default_rng(seed)
        self._W = rng.standard_normal((self.NUM_FEATURES, dim)) * scale
        self.dim = dim
        self.seed = seed

    def _features(self, state: AgentState) -> list[float]:
        """State → 12-feature vector (training_samples.state_to_feature_vector와 동일 shape)."""
        # 순환 import 방지: 위치 기반 함수
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

    def encode(
        self,
        state: AgentState,
        history: list[dict] | None = None,
    ) -> LatentDriveState:
        """Single-state → drive. Feature 자동 추출."""
        return self.encode_from_features(self._features(state))

    def encode_from_features(self, features: list[float]) -> LatentDriveState:
        """이미 추출된 12-feature 벡터 → drive (Stage 2 training loop 진입점).

        `training_samples.state_to_feature_vector` 출력 또는
        `samples_to_feature_matrix` X 행을 직접 입력 가능.
        """
        import numpy as np
        if len(features) != self.NUM_FEATURES:
            raise ValueError(
                f"expected {self.NUM_FEATURES} features, got {len(features)}"
            )
        # 10.0으로 정규화 (raw scale 입력을 가정, [0,10] 범위로 들어옴)
        x = np.array(features, dtype=np.float64) / 10.0
        drive = np.tanh(x @ self._W)
        return LatentDriveState(values=[float(v) for v in drive], dim=self.dim)

    def encode_batch(self, feature_matrix: list[list[float]]) -> list[list[float]]:
        """Batch: (n, 12) features → (n, dim) drive values.

        Stage 2 training loop에서 mini-batch 처리에 사용. numpy vectorize.
        """
        import numpy as np
        X = np.array(feature_matrix, dtype=np.float64)
        if X.shape[1] != self.NUM_FEATURES:
            raise ValueError(
                f"expected (n, {self.NUM_FEATURES}), got {X.shape}"
            )
        drives = np.tanh((X / 10.0) @ self._W)
        result: list[list[float]] = drives.tolist()
        return result


class LearnedLinearEncoder:
    """Stage 2 **실제 학습된** linear encoder (Iter 72).

    sklearn `LinearDiscriminantAnalysis` 로 state feature → d-차원 drive.
    Fisher-style between/within variance ratio를 직접 최대화 (action class
    separability를 최적화).

    FixedProjectionEncoder (random W) → LearnedLinearEncoder (LDA-trained W)
    → (future) LearnedMLPEncoder (PyTorch 비선형). Stage 2 첫 실제 학습 단계.

    torch 불필요 — numpy + sklearn만 사용.

    Usage:
        enc = LearnedLinearEncoder(dim=5)
        enc.fit(training_samples)
        drive = enc.encode(state)

    주의:
    - `fit` 전에 `encode` 호출 시 `RuntimeError`.
    - sklearn LDA는 d <= (n_classes - 1) 제약. 예: 24 actions이면 d=5 OK.
      action class 수가 dim보다 적으면 LDA가 자동으로 실제 d 축소.
    """

    def __init__(self, dim: int = 5) -> None:
        if dim < 1:
            raise ValueError("dim must be >= 1")
        if dim > 8:
            raise ValueError("LearnedLinearEncoder dim capped at 8 (design guideline)")
        self.dim = dim
        self._model: object | None = None  # sklearn LDA after fit
        self._n_features: int | None = None
        self._effective_dim: int | None = None  # after LDA clamp

    def fit(self, samples: list[Any]) -> None:
        """TrainingSample 목록으로 학습. action == None인 샘플은 무시."""
        import numpy as np
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

        from engine.simulation.training_samples import state_to_feature_vector

        valid = [s for s in samples if getattr(s, "action", None) is not None]
        if len(valid) < 2:
            raise ValueError("need >= 2 samples with non-None action to fit")

        X = np.array([state_to_feature_vector(s.state) for s in valid])
        y = np.array([s.action for s in valid])

        unique = len(set(y))
        n_components = min(self.dim, unique - 1)
        if n_components < 1:
            raise ValueError(
                "need >= 2 distinct actions in samples (got {})".format(unique)
            )

        lda = LinearDiscriminantAnalysis(n_components=n_components)
        lda.fit(X, y)
        self._model = lda
        self._n_features = X.shape[1]
        self._effective_dim = n_components

    def encode(
        self,
        state: AgentState,
        history: list[dict] | None = None,
    ) -> LatentDriveState:
        import numpy as np

        from engine.simulation.training_samples import state_to_feature_vector

        if self._model is None:
            raise RuntimeError(
                "LearnedLinearEncoder must be fit() before encode()"
            )
        x = np.array(state_to_feature_vector(state)).reshape(1, -1)
        projected = self._model.transform(x)  # type: ignore[attr-defined]
        # tanh squashing to match [-1, 1] drive convention
        values = np.tanh(projected[0]).tolist()
        # Pad to self.dim if effective < dim
        if self._effective_dim is not None and self._effective_dim < self.dim:
            values = values + [0.0] * (self.dim - self._effective_dim)
        return LatentDriveState(values=values, dim=self.dim)


class ExtensibleFixedProjectionEncoder:
    """Variable-width projection encoder (Iter 67).

    FixedProjectionEncoder 가 12 feature로 고정된 반면, 이 class는
    `state_to_feature_vector_extended(state)` 결과를 받아 그 길이에 맞게
    W 매트릭스를 **첫 호출 시 lazy 생성**. 길이는 처음 encode된 state로 고정.

    Talleyrand 류 domain-driven scenario에서 domain_state.to_feature_vector()
    가 추가 feature를 제공하면 그것까지 projection에 반영.
    """

    def __init__(self, dim: int = 5, seed: int = 0, scale: float = 0.3) -> None:
        import numpy as np  # noqa: F401
        if dim < 1:
            raise ValueError("dim must be >= 1")
        if dim > 8:
            raise ValueError("ExtensibleFixedProjectionEncoder dim capped at 8")
        self.dim = dim
        self.seed = seed
        self.scale = scale
        self._W: object | None = None  # numpy array, lazy
        self._feature_len: int | None = None

    def _init_weights(self, n_features: int) -> None:
        import numpy as np
        rng = np.random.default_rng(self.seed)
        self._W = rng.standard_normal((n_features, self.dim)) * self.scale
        self._feature_len = n_features

    def _features(self, state: AgentState) -> list[float]:
        from engine.simulation.training_samples import (
            state_to_feature_vector_extended,
        )
        return state_to_feature_vector_extended(state)

    def encode(
        self,
        state: AgentState,
        history: list[dict] | None = None,
    ) -> LatentDriveState:
        import numpy as np
        features = self._features(state)
        if self._W is None:
            self._init_weights(len(features))
        if len(features) != self._feature_len:
            raise ValueError(
                f"feature length changed: expected {self._feature_len}, "
                f"got {len(features)}. Extensible encoder fixes length at first call."
            )
        x = np.array(features, dtype=np.float64) / 10.0
        drive = np.tanh(x @ self._W)  # type: ignore[operator]
        return LatentDriveState(values=[float(v) for v in drive], dim=self.dim)


class IdentityPolicy:
    """디버그/테스트용 action policy: drive 무시, symbolic weight 그대로 반환.

    실제 drive 기반 policy가 없을 때 fallback. v0.x 동작과 완전 동등.
    """

    def action_weights(
        self,
        state: AgentState,
        drive: LatentDriveState,
        available_actions: list[str],
    ) -> dict[str, float]:
        # 모든 action에 동일 weight 1.0 (caller가 symbolic weight와 곱해 사용)
        return {action_id: 1.0 for action_id in available_actions}


class IdentitySusceptibility:
    """디버그용 trigger susceptibility: drive 무시, multiplier=1.0 (기본 threshold 유지)."""

    def susceptibility_multiplier(
        self,
        state: AgentState,
        drive: LatentDriveState,
        trigger_id: str,
    ) -> float:
        return 1.0


class IdentitySlowUpdate:
    """디버그용 slow update modulation: 변화 없음 (기본 rule-based update 유지)."""

    def modulated_update(
        self,
        state: AgentState,
        drive: LatentDriveState,
    ) -> dict[str, float]:
        return {
            "moral_injury": 1.0,
            "identity_shift": 1.0,
            "event_trauma": 1.0,
            "trust_scar": 1.0,
        }
