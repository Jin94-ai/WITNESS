"""v1.0 Latent Drive Skeleton tests.

Stage 1 plumbing validation: AgentState.drive_state 필드 + LatentDriveModel 인터페이스.
학습 모델은 Stage 2에서 구현 예정.
"""

from engine.core.latent_drive import IdentityEncoder, LatentDriveModel
from engine.core.state import (
    AgentState,
    EmotionalState,
    LatentDriveState,
    SlowState,
)


class TestLatentDriveStateField:
    def test_agent_state_drive_default_none(self):
        """AgentState.drive_state 기본값은 None (backward compat)."""
        agent = AgentState(agent_id="test")
        assert agent.drive_state is None

    def test_drive_state_can_be_set(self):
        """drive_state 필드 정상 할당."""
        drive = LatentDriveState(values=[0.1, 0.2, 0.3], dim=3)
        agent = AgentState(agent_id="test", drive_state=drive)
        assert agent.drive_state is not None
        assert agent.drive_state.dim == 3
        assert agent.drive_state.values == [0.1, 0.2, 0.3]

    def test_drive_state_empty_by_default(self):
        """LatentDriveState 기본값은 empty."""
        drive = LatentDriveState()
        assert drive.values == []
        assert drive.dim == 0


class TestLatentDriveModelInterface:
    def test_model_inactive_when_no_encoder(self):
        """Encoder 없으면 모델 비활성 (v0.x 모드)."""
        model = LatentDriveModel()
        assert model.is_active() is False
        assert model.encode_safe(AgentState(agent_id="test")) is None

    def test_model_active_with_encoder(self):
        """Encoder 주입 시 활성화."""
        model = LatentDriveModel(encoder=IdentityEncoder(dim=5))
        assert model.is_active() is True

    def test_identity_encoder_output_dim(self):
        """IdentityEncoder가 정확한 dim 반환."""
        model = LatentDriveModel(encoder=IdentityEncoder(dim=5))
        agent = AgentState(
            agent_id="test",
            emotions=EmotionalState(fear=3.0, grief=5.0, hope=7.0),
            slow_state=SlowState(moral_injury=2.0, identity_shift=-1.0),
        )
        drive = model.encode_safe(agent)
        assert drive is not None
        assert drive.dim == 5
        assert len(drive.values) == 5
        # 정규화 확인 (fear 3/10 = 0.3)
        assert abs(drive.values[0] - 0.3) < 1e-6
        assert abs(drive.values[1] - 0.5) < 1e-6  # grief 5/10
        assert abs(drive.values[2] - 0.7) < 1e-6  # hope 7/10

    def test_identity_encoder_different_dims(self):
        """dim 변경 시 정상 작동."""
        for d in [3, 5, 8]:
            model = LatentDriveModel(encoder=IdentityEncoder(dim=d))
            drive = model.encode_safe(AgentState(agent_id="test"))
            assert drive.dim == d
            assert len(drive.values) == d


class TestBackwardCompatibility:
    def test_existing_tests_unaffected(self):
        """drive_state=None 경로가 기존 rules/trigger에 영향 없음.

        스모크: 간단한 AgentState 생성/복사가 여전히 작동.
        """
        agent = AgentState(agent_id="peter")
        # model_copy 패턴이 drive_state 필드 때문에 깨지지 않아야 함
        updated = agent.model_copy(
            update={"emotions": EmotionalState(fear=5.0)}
        )
        assert updated.agent_id == "peter"
        assert updated.drive_state is None
        assert updated.emotions.fear == 5.0
