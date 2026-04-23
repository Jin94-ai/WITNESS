"""IdentityPolicy / IdentitySusceptibility / IdentitySlowUpdate 테스트.

v1.0 학습 모델이 없을 때 drive-integrated simulation이 symbolic 동작과 동등함을 보장하는
identity (no-op) 구현체 검증.

v1.0 Stage 2에서 실제 neural policy 교체 시 이 identity들이 baseline.
"""

from engine.core.latent_drive import (
    IdentityPolicy,
    IdentitySlowUpdate,
    IdentitySusceptibility,
    LatentDriveModel,
)
from engine.core.state import AgentState, LatentDriveState


def _drive(dim: int = 5) -> LatentDriveState:
    return LatentDriveState(values=[0.0] * dim, dim=dim)


class TestIdentityPolicy:
    def test_uniform_weights(self):
        policy = IdentityPolicy()
        state = AgentState(agent_id="test")
        drive = _drive()
        weights = policy.action_weights(state, drive, ["a", "b", "c"])
        assert weights == {"a": 1.0, "b": 1.0, "c": 1.0}

    def test_empty_actions(self):
        policy = IdentityPolicy()
        state = AgentState(agent_id="test")
        drive = _drive()
        assert policy.action_weights(state, drive, []) == {}


class TestIdentitySusceptibility:
    def test_multiplier_is_one(self):
        susc = IdentitySusceptibility()
        state = AgentState(agent_id="test")
        drive = _drive()
        assert susc.susceptibility_multiplier(state, drive, "arrest_trigger") == 1.0

    def test_regardless_of_trigger_id(self):
        susc = IdentitySusceptibility()
        state = AgentState(agent_id="test")
        drive = _drive()
        for tid in ["a", "b", "c", ""]:
            assert susc.susceptibility_multiplier(state, drive, tid) == 1.0


class TestIdentitySlowUpdate:
    def test_all_multipliers_one(self):
        su = IdentitySlowUpdate()
        state = AgentState(agent_id="test")
        drive = _drive()
        result = su.modulated_update(state, drive)
        for key, val in result.items():
            assert val == 1.0, f"{key}={val} should be 1.0"

    def test_keys_cover_slow_state(self):
        su = IdentitySlowUpdate()
        state = AgentState(agent_id="test")
        drive = _drive()
        result = su.modulated_update(state, drive)
        # slow_state의 주요 필드가 모두 포함되어야 함
        for expected in ["moral_injury", "identity_shift", "event_trauma", "trust_scar"]:
            assert expected in result


class TestLatentDriveModelFullStack:
    """네 Protocol 모두 주입했을 때도 정상 동작."""

    def test_full_identity_stack(self):
        from engine.core.latent_drive import IdentityEncoder

        model = LatentDriveModel(
            encoder=IdentityEncoder(dim=5),
            policy=IdentityPolicy(),
            susceptibility=IdentitySusceptibility(),
            slow_update=IdentitySlowUpdate(),
            dim=5,
        )
        assert model.is_active()

        state = AgentState(agent_id="test")
        drive = model.encode_safe(state)
        assert drive is not None

        # policy/susc/slow_update가 모두 호출 가능
        weights = model.policy.action_weights(state, drive, ["a", "b"])
        assert weights["a"] == 1.0

        mult = model.susceptibility.susceptibility_multiplier(state, drive, "t")
        assert mult == 1.0

        upd = model.slow_update.modulated_update(state, drive)
        assert upd["moral_injury"] == 1.0
