"""Drive-action separability diagnostic (Iter 64).

Stage 2 학습 전 classifier-feasibility 점검: action class가 drive 공간에서
얼마나 구별되는가. 분리되지 않으면 학습이 수렴하기 어려우므로
feature 확장 또는 모델 용량 증가 신호.
"""

from __future__ import annotations

from engine.core.latent_drive import FixedProjectionEncoder, IdentityEncoder
from engine.core.state import AgentState, EmotionalState, SlowState
from engine.simulation.training_samples import (
    DriveActionDiagnostic,
    TrainingSample,
    compute_drive_action_diagnostics,
    drive_class_separability,
)


def _sample(action: str | None, fear: float = 2.0) -> TrainingSample:
    s = AgentState(
        agent_id="t",
        emotions=EmotionalState(fear=fear),
        slow_state=SlowState(),
    )
    return TrainingSample(
        agent_id="t", tick=0, state=s,
        action=action, event_ids=[],
        next_state=s, next_tick=1,
    )


class TestDriveActionDiagnosticShape:
    def test_empty_samples_returns_empty(self):
        result = compute_drive_action_diagnostics([], IdentityEncoder(dim=5))
        assert result == []

    def test_all_none_actions_returns_empty(self):
        samples = [_sample(None) for _ in range(5)]
        result = compute_drive_action_diagnostics(samples, IdentityEncoder(dim=5))
        assert result == []

    def test_single_sample_per_action_is_dropped(self):
        """n_samples<2이면 std 의미없으므로 drop."""
        samples = [_sample("a"), _sample("b")]
        result = compute_drive_action_diagnostics(samples, IdentityEncoder(dim=5))
        assert result == []

    def test_diagnostic_has_correct_fields(self):
        samples = [_sample("a", fear=i) for i in range(1, 6)]
        result = compute_drive_action_diagnostics(
            samples, FixedProjectionEncoder(dim=3, seed=0),
        )
        assert len(result) == 1
        d = result[0]
        assert isinstance(d, DriveActionDiagnostic)
        assert d.action_id == "a"
        assert d.n_samples == 5
        assert len(d.drive_mean) == 3
        assert len(d.drive_std) == 3


class TestSortedByCount:
    def test_results_sorted_by_n_samples_desc(self):
        samples = (
            [_sample("rare", fear=i) for i in range(1, 3)]
            + [_sample("common", fear=i) for i in range(1, 8)]
        )
        result = compute_drive_action_diagnostics(
            samples, FixedProjectionEncoder(dim=3, seed=0),
        )
        assert result[0].action_id == "common"
        assert result[0].n_samples == 7
        assert result[1].action_id == "rare"
        assert result[1].n_samples == 2


class TestSeparability:
    def test_zero_when_fewer_than_two_actions(self):
        samples = [_sample("only", fear=i) for i in range(1, 6)]
        diags = compute_drive_action_diagnostics(
            samples, FixedProjectionEncoder(dim=3, seed=0),
        )
        assert drive_class_separability(diags) == 0.0

    def test_positive_when_actions_separated(self):
        """두 action class가 서로 다른 fear 범위 → drive mean 다름 → 분리 가능."""
        low_fear = [_sample("calm", fear=1.0) for _ in range(5)]
        low_fear = [_sample("calm", fear=1.0 + 0.1 * i) for i in range(5)]
        high_fear = [_sample("crisis", fear=9.0 + 0.1 * i) for i in range(5)]
        diags = compute_drive_action_diagnostics(
            low_fear + high_fear,
            FixedProjectionEncoder(dim=5, seed=0),
        )
        sep = drive_class_separability(diags)
        # 극단 fear 차이 → 분리 가능 신호
        assert sep > 0.0

    def test_zero_when_within_variance_zero_and_between_zero(self):
        """모든 sample이 동일 state → drive 동일, separability 0."""
        samples = (
            [_sample("a", fear=5.0) for _ in range(3)]
            + [_sample("b", fear=5.0) for _ in range(3)]
        )
        diags = compute_drive_action_diagnostics(
            samples, FixedProjectionEncoder(dim=3, seed=0),
        )
        sep = drive_class_separability(diags)
        # between = 0 (두 mean 동일), within = 0 → 0
        assert sep == 0.0
