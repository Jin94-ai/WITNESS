"""FixedProjectionEncoder 검증 (Iter 59).

Stage 1 IdentityEncoder → Stage 2 PyTorch learned encoder 사이의 bridge.
non-identity behavior + Protocol compatibility + seed reproducibility.
"""

from __future__ import annotations

import pytest

from engine.core.latent_drive import (
    FixedProjectionEncoder,
    IdentityEncoder,
    LatentDriveEncoder,
    LatentDriveModel,
)
from engine.core.state import (
    AgentState,
    EmotionalState,
    PhysicalState,
    SlowState,
)


def _state(fear: float = 5.0, hope: float = 5.0) -> AgentState:
    return AgentState(
        agent_id="t",
        emotions=EmotionalState(fear=fear, hope=hope),
        physical=PhysicalState(),
        slow_state=SlowState(),
    )


class TestProtocolCompatibility:
    def test_implements_encoder_protocol(self):
        enc: LatentDriveEncoder = FixedProjectionEncoder(dim=5)
        assert hasattr(enc, "encode")

    def test_accepted_by_latent_drive_model(self):
        enc = FixedProjectionEncoder(dim=5)
        model = LatentDriveModel(encoder=enc)
        assert model.is_active()

    def test_returns_latent_drive_state_of_correct_dim(self):
        enc = FixedProjectionEncoder(dim=3)
        drive = enc.encode(_state())
        assert len(drive.values) == 3

    def test_dim_range_accepts_3_to_8(self):
        for d in [3, 5, 8]:
            enc = FixedProjectionEncoder(dim=d)
            assert enc.dim == d


class TestNonIdentityBehavior:
    def test_output_differs_across_inputs(self):
        """IdentityEncoder와 달리 projection encoder는 상태 차이를 **전역으로** 반영."""
        enc = FixedProjectionEncoder(dim=5, seed=0)
        d1 = enc.encode(_state(fear=1.0))
        d2 = enc.encode(_state(fear=9.0))
        # 두 결과가 다름 (fear 변화가 전 drive 차원에 영향)
        assert d1.values != d2.values

    def test_tanh_range(self):
        """출력은 tanh으로 [-1, 1] 범위."""
        enc = FixedProjectionEncoder(dim=5, seed=0)
        drive = enc.encode(_state(fear=10.0, hope=10.0))
        for v in drive.values:
            assert -1.0 <= v <= 1.0

    def test_differs_from_identity_encoder(self):
        """같은 state에서 IdentityEncoder와 결과 다름."""
        s = _state(fear=7.0, hope=3.0)
        idn = IdentityEncoder(dim=5).encode(s)
        fp = FixedProjectionEncoder(dim=5, seed=0).encode(s)
        assert idn.values != fp.values


class TestReproducibility:
    def test_same_seed_same_output(self):
        enc1 = FixedProjectionEncoder(dim=5, seed=42)
        enc2 = FixedProjectionEncoder(dim=5, seed=42)
        s = _state(fear=3.0, hope=7.0)
        assert enc1.encode(s).values == enc2.encode(s).values

    def test_different_seeds_different_outputs(self):
        enc_a = FixedProjectionEncoder(dim=5, seed=0)
        enc_b = FixedProjectionEncoder(dim=5, seed=1)
        s = _state(fear=5.0)
        assert enc_a.encode(s).values != enc_b.encode(s).values


class TestValidation:
    def test_dim_zero_raises(self):
        with pytest.raises(ValueError, match="dim"):
            FixedProjectionEncoder(dim=0)

    def test_dim_over_8_raises(self):
        with pytest.raises(ValueError, match="dim"):
            FixedProjectionEncoder(dim=10)


class TestFeatureCoverage:
    """12개 입력 feature가 실제로 drive에 반영 (Iter 60 — training_samples 정렬)."""

    def test_num_features_is_12(self):
        assert FixedProjectionEncoder.NUM_FEATURES == 12

    def test_all_emotion_axes_affect_drive(self):
        """fear/hope/grief/confusion/love 각각 변경 시 drive 변경."""
        enc = FixedProjectionEncoder(dim=5, seed=0)
        base = enc.encode(_state()).values
        for field in ["fear", "hope", "grief", "confusion", "love"]:
            kwargs = {field: 8.0}
            modified_state = _state()
            modified_state.emotions = EmotionalState(**kwargs)
            modified = enc.encode(modified_state).values
            assert modified != base, f"{field} change not reflected in drive"

    def test_slow_state_fields_reflected(self):
        enc = FixedProjectionEncoder(dim=5, seed=0)
        base = enc.encode(_state()).values
        injured = _state()
        injured.slow_state = SlowState(moral_injury=7.0)
        assert enc.encode(injured).values != base


class TestTrainingSamplesAlignment:
    """`state_to_feature_vector`와 동일 shape — Stage 2 training loop 호환."""

    def test_feature_vector_same_shape_as_training_samples(self):
        from engine.simulation.training_samples import state_to_feature_vector
        s = _state(fear=3.0, hope=7.0)
        ts_features = state_to_feature_vector(s)
        enc = FixedProjectionEncoder(dim=5, seed=0)
        enc_features = enc._features(s)
        assert len(ts_features) == len(enc_features) == 12
        # 순서 동일
        assert ts_features == enc_features

    def test_encode_from_features_matches_encode(self):
        from engine.simulation.training_samples import state_to_feature_vector
        enc = FixedProjectionEncoder(dim=5, seed=0)
        s = _state(fear=5.0, hope=3.0)
        via_state = enc.encode(s).values
        via_features = enc.encode_from_features(state_to_feature_vector(s)).values
        assert via_state == via_features

    def test_encode_from_features_wrong_length_raises(self):
        enc = FixedProjectionEncoder(dim=5)
        with pytest.raises(ValueError, match="expected 12 features"):
            enc.encode_from_features([1.0, 2.0, 3.0])

    def test_encode_batch_matches_single(self):
        from engine.simulation.training_samples import state_to_feature_vector
        enc = FixedProjectionEncoder(dim=5, seed=0)
        s1 = _state(fear=3.0)
        s2 = _state(fear=9.0)
        X = [state_to_feature_vector(s1), state_to_feature_vector(s2)]
        batch_drives = enc.encode_batch(X)
        single1 = enc.encode(s1).values
        single2 = enc.encode(s2).values
        # tolerance for numpy float precision
        for a, b in zip(batch_drives[0], single1):
            assert abs(a - b) < 1e-12
        for a, b in zip(batch_drives[1], single2):
            assert abs(a - b) < 1e-12

    def test_encode_batch_wrong_shape_raises(self):
        enc = FixedProjectionEncoder(dim=5)
        with pytest.raises(ValueError, match=r"expected \(n, 12\)"):
            enc.encode_batch([[1.0, 2.0, 3.0]])
