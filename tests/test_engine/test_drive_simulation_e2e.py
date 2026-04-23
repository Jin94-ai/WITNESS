"""SimulationWorld + LatentDriveModel(FixedProjectionEncoder) E2E (Iter 62).

drive_model 주입 → 매 tick 각 agent의 drive_state 업데이트 →
snapshots에 drive가 기록됨. FixedProjection이 non-identity이므로
state 변화에 따라 drive values도 변화.

Stage 2 PyTorch 학습 전이지만 trace pipeline이 drive-aware로 작동함을 증명.
"""

from __future__ import annotations

from engine.core.latent_drive import (
    FixedProjectionEncoder,
    IdentityEncoder,
    LatentDriveModel,
)
from engine.core.state import AgentState, EmotionalState, SlowState
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, HopeRule
from engine.simulation.world import SimulationWorld


def _agent(aid: str, fear: float = 2.0, hope: float = 6.0) -> AgentState:
    return AgentState(
        agent_id=aid,
        emotions=EmotionalState(fear=fear, hope=hope),
        slow_state=SlowState(),
    )


def _run(drive_model: LatentDriveModel | None, seed: int = 0, max_tick: int = 20):
    a = _agent("a", fear=4.0)
    config = SimulationConfig(
        initial_state=a, initial_states=[a],
        max_tick=max_tick, state_noise_scale=0.0,
    )
    rules = RuleEngine([FearResponseRule(), HopeRule()])
    world = SimulationWorld(config, rules, drive_model=drive_model)
    return world.run(seed=seed)


class TestDriveStatePopulated:
    def test_no_drive_model_leaves_drive_state_none(self):
        r = _run(drive_model=None)
        final = r.final_states["a"]
        assert final.drive_state is None

    def test_identity_encoder_populates_drive_state(self):
        dm = LatentDriveModel(encoder=IdentityEncoder(dim=5), dim=5)
        r = _run(drive_model=dm)
        final = r.final_states["a"]
        assert final.drive_state is not None
        assert len(final.drive_state.values) == 5

    def test_fixed_projection_populates_drive_state(self):
        dm = LatentDriveModel(encoder=FixedProjectionEncoder(dim=5, seed=0), dim=5)
        r = _run(drive_model=dm)
        final = r.final_states["a"]
        assert final.drive_state is not None
        assert len(final.drive_state.values) == 5


class TestFixedProjectionBehaviorInPipeline:
    def test_fixed_projection_drive_differs_from_identity(self):
        """같은 run에서 Identity vs FixedProjection은 final drive 값이 다름."""
        dm_id = LatentDriveModel(encoder=IdentityEncoder(dim=5), dim=5)
        dm_fp = LatentDriveModel(
            encoder=FixedProjectionEncoder(dim=5, seed=0), dim=5,
        )
        r_id = _run(drive_model=dm_id, seed=42)
        r_fp = _run(drive_model=dm_fp, seed=42)
        assert (
            r_id.final_states["a"].drive_state.values
            != r_fp.final_states["a"].drive_state.values
        )

    def test_fixed_projection_drive_within_tanh_range(self):
        """tanh projection이므로 모든 값이 [-1, 1] 범위."""
        dm = LatentDriveModel(encoder=FixedProjectionEncoder(dim=5, seed=0), dim=5)
        r = _run(drive_model=dm)
        final = r.final_states["a"]
        for v in final.drive_state.values:
            assert -1.0 <= v <= 1.0

    def test_drive_updates_tick_by_tick(self):
        """state가 변하면 drive도 변함 — state_snapshots에 다양한 drive 기록됨."""
        dm = LatentDriveModel(encoder=FixedProjectionEncoder(dim=5, seed=0), dim=5)
        r = _run(drive_model=dm, max_tick=20)
        snaps = r.state_snapshots.get("a", {})
        # snapshot에 저장된 drive_state 모음
        drives = [
            tuple(s.drive_state.values) for s in snaps.values()
            if s.drive_state is not None
        ]
        # 최소 2개 이상 다른 drive vector (state evolution 반영)
        unique = {d for d in drives}
        assert len(unique) >= 2


class TestSeedReproducibility:
    def test_same_seed_same_drive(self):
        dm = LatentDriveModel(encoder=FixedProjectionEncoder(dim=5, seed=0), dim=5)
        r1 = _run(drive_model=dm, seed=7)
        r2 = _run(drive_model=LatentDriveModel(
            encoder=FixedProjectionEncoder(dim=5, seed=0), dim=5,
        ), seed=7)
        assert (
            r1.final_states["a"].drive_state.values
            == r2.final_states["a"].drive_state.values
        )


class TestStage2ReadinessSignals:
    """이 iteration은 Stage 2 PyTorch 진입 전 plumbing 검증 층."""

    def test_pipeline_accepts_12_feature_encoder(self):
        enc = FixedProjectionEncoder(dim=5)
        assert enc.NUM_FEATURES == 12

    def test_batch_api_available_for_future_training(self):
        enc = FixedProjectionEncoder(dim=3, seed=0)
        X = [[1.0] * 12, [2.0] * 12, [3.0] * 12]
        batch = enc.encode_batch(X)
        assert len(batch) == 3
        for row in batch:
            assert len(row) == 3
