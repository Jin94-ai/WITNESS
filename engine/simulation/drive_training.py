"""v1.0 Stage 2: Latent Drive Training Pipeline (Skeleton).

DESIGN_LATENT_DRIVE.md §3.2 학습 설계를 위한 골격:
1. collect_trajectories(n_runs) — simulator 다중 실행 → trajectory 수집
2. train_drive_model(trajectories, d) — predictive bottleneck 학습 (현재 placeholder)
3. validate_drive_model(model) — 기존 POM/counterfactual 프레임워크 재사용

실제 학습은 Stage 2 구현 단계에서 PyTorch MLP로 교체.
현재 단계: API 공식화 + collect/validate는 실제 작동.

참조:
- DESIGN_LATENT_DRIVE.md §3, §7 (구현 단계)
- TRACE_SCHEMA.md §2 (trajectory 로깅)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from engine.core.latent_drive import (
    IdentityEncoder,
    IdentityPolicy,
    IdentitySlowUpdate,
    IdentitySusceptibility,
    LatentDriveEncoder,
    LatentDriveModel,
)
from engine.simulation.training_samples import (
    SampleStatistics,
    TrainingSample,
    extract_samples,
    samples_to_feature_matrix,
    summarize_samples,
)


@dataclass
class TrainingConfig:
    """Stage 2 학습 설정 (DESIGN_LATENT_DRIVE.md §4 권장값)."""

    drive_dim: int = 5  # 3~8 권장
    n_runs: int = 100  # trajectory 수
    # Loss weight (§3.2)
    alpha_action: float = 1.0  # action prediction
    beta_event: float = 1.0  # event prediction
    gamma_continuity: float = 0.5  # state continuity
    lambda_kl: float = 0.01  # drive distribution regularization
    # 학습 hyper (PyTorch 사용 시)
    lr: float = 1e-3
    n_epochs: int = 50
    batch_size: int = 64
    # Seed
    random_seed: int = 42
    # Iter 61: non-identity encoder opt-in (PyTorch 학습 전 bridge).
    # True = FixedProjectionEncoder (numpy-based seeded projection)
    # False = IdentityEncoder (trivial fallback)
    use_fixed_projection: bool = False
    # Iter 73: sklearn LDA-based **실제 학습된** encoder opt-in.
    # True일 때 train_drive_model이 samples로 LDA fit 수행 → LearnedLinearEncoder 반환.
    # use_learned_linear가 use_fixed_projection보다 우선.
    use_learned_linear: bool = False


@dataclass
class ValidationReport:
    """검증 결과 (기존 POM/counterfactual 프레임워크 재사용 요약)."""

    n_samples: int
    pom_pass_rate: float | None
    behavioral_signal_preserved: bool | None
    linear_trajectory_r2: float | None
    sample_stats: SampleStatistics | None = None
    notes: str = ""


def collect_trajectories(
    run_fn: Callable[[int], Any],
    n_runs: int,
    seeds: list[int] | None = None,
) -> list[Any]:
    """여러 seed로 시뮬 실행 → SimulationResult 목록.

    Args:
        run_fn: seed → MultiAgentResult (or similar)
        n_runs: 실행 횟수
        seeds: 특정 seed 목록 (None이면 0~n_runs)

    Returns:
        [MultiAgentResult, ...]
    """
    if seeds is None:
        seeds = list(range(n_runs))
    return [run_fn(s) for s in seeds[:n_runs]]


def trajectories_to_samples(results: list[Any]) -> list[TrainingSample]:
    """여러 trajectory → 모든 training sample 합침."""
    all_samples: list[TrainingSample] = []
    for r in results:
        all_samples.extend(extract_samples(r))
    return all_samples


def train_drive_model(
    samples: list[TrainingSample],
    config: TrainingConfig,
) -> LatentDriveModel:
    """Predictive latent drive bottleneck 학습 (SKELETON).

    실제 PyTorch 구현은 Stage 2 full implementation에서.
    현재는 identity fallback을 반환 (학습 없음).

    Target architecture (DESIGN_LATENT_DRIVE.md §1):
        Encoder(state + history) → drive ∈ R^d
        Policy(state, drive) → action probs
        Susceptibility(state, drive, trigger) → threshold multiplier
        SlowUpdate(state, drive) → update modulation

    Loss (DESIGN_LATENT_DRIVE.md §3.2):
        L = α·action_pred + β·event_pred + γ·state_continuity
          + λ·KL(drive || prior)

    Raises:
        NotImplementedError: 실제 학습 루프는 미구현 (Stage 2 작업)
    """
    # TODO(Stage 2): PyTorch MLP encoder + decoder 구현
    # 현재는 identity stack을 반환하여 plumbing만 검증
    if not samples:
        raise ValueError("Empty samples")

    # Dry-run: feature matrix 생성 가능 여부 확인
    X, Y, actions = samples_to_feature_matrix(samples)
    assert len(X) == len(samples), "feature matrix size mismatch"

    # Stage 2 실제 구현 시 여기서 PyTorch 학습 루프
    # model = _train_pytorch_encoder(X, Y, actions, config)
    # return model

    # Iter 61: opt-in non-identity encoder (FixedProjectionEncoder) —
    # 실제 학습은 아니지만, Identity 대신 12-feature → d-dim tanh projection을
    # 주입하여 Stage 2 PyTorch 구현 전에도 drive plumbing 변화를 관측 가능.
    encoder: LatentDriveEncoder
    if config.use_learned_linear:
        # Iter 73: LDA로 실제 학습.
        from engine.core.latent_drive import LearnedLinearEncoder
        lda = LearnedLinearEncoder(dim=config.drive_dim)
        lda.fit(samples)
        encoder = lda
    elif config.use_fixed_projection:
        from engine.core.latent_drive import FixedProjectionEncoder
        encoder = FixedProjectionEncoder(
            dim=config.drive_dim, seed=config.random_seed,
        )
    else:
        encoder = IdentityEncoder(dim=config.drive_dim)

    return LatentDriveModel(
        encoder=encoder,
        policy=IdentityPolicy(),
        susceptibility=IdentitySusceptibility(),
        slow_update=IdentitySlowUpdate(),
        dim=config.drive_dim,
    )


def validate_drive_model(
    model: LatentDriveModel,
    baseline_run_fn: Callable[[int], Any] | None = None,
    n_validation_runs: int = 20,
) -> ValidationReport:
    """학습된 drive model이 기존 POM/counterfactual을 통과하는지 검증 (SKELETON).

    DESIGN_LATENT_DRIVE.md §5.1 필수 통과 기준 (example Peter scenario):
    - POM all_pass rate >= 40%
    - Counterfactual agent removal → spontaneous 0%
    - Event-relative checkpoint >= 70%
    - Linear trajectory R² >= 0.95

    현재 구현: API 확립, 실제 검증은 v1.0 학습 완료 후.
    """
    report = ValidationReport(
        n_samples=0,
        pom_pass_rate=None,
        behavioral_signal_preserved=None,
        linear_trajectory_r2=None,
        notes="Skeleton — full validation deferred to Stage 2 trained model.",
    )

    if baseline_run_fn is not None:
        results_baseline = collect_trajectories(baseline_run_fn, n_validation_runs)
        samples_baseline = trajectories_to_samples(results_baseline)
        stats = summarize_samples(samples_baseline)
        report.n_samples = stats.n_samples
        report.sample_stats = stats
        report.notes += (
            f" {n_validation_runs} baseline runs, "
            f"{stats.n_samples} samples, "
            f"{stats.n_agents} agents, "
            f"event_rate={stats.event_rate:.2%}, "
            f"action_imbalance={stats.action_imbalance_ratio:.1f}x."
        )

    return report


def train_and_validate(
    run_fn: Callable[[int], Any],
    config: TrainingConfig | None = None,
) -> tuple[LatentDriveModel, ValidationReport]:
    """End-to-end Stage 2 pipeline entry point (SKELETON).

    1. Collect trajectories
    2. Extract training samples
    3. Train drive model
    4. Validate against POM/counterfactual framework
    """
    if config is None:
        config = TrainingConfig()
    results = collect_trajectories(run_fn, config.n_runs)
    samples = trajectories_to_samples(results)
    model = train_drive_model(samples, config)
    report = validate_drive_model(
        model, baseline_run_fn=run_fn, n_validation_runs=config.n_runs,
    )
    return model, report
