"""ExtensibleFixedProjectionEncoder + DomainState.to_feature_vector (Iter 67).

Iter 66 gap 해소: Talleyrand 같은 regime-driven scenario에서
domain_state 필드를 feature에 포함하여 drive separability 회복.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from content.talleyrand.domain_diplomacy import DiplomacyState
from engine.core.latent_drive import (
    ExtensibleFixedProjectionEncoder,
    FixedProjectionEncoder,
)
from engine.core.state import AgentState, EmotionalState
from engine.io.loader import register_domain_type
from engine.simulation.training_samples import (
    state_to_feature_vector,
    state_to_feature_vector_extended,
)


@pytest.fixture(scope="module")
def _setup():
    register_domain_type("diplomacy", DiplomacyState)
    return None


class TestExtendedFeatureVector:
    def test_without_domain_fv_returns_base(self, _setup):
        """domain_state에 to_feature_vector 없으면 extended == baseline."""
        s = AgentState(agent_id="plain", emotions=EmotionalState())
        assert state_to_feature_vector_extended(s) == state_to_feature_vector(s)

    def test_talleyrand_extended_is_longer(self, _setup):
        s = AgentState(
            agent_id="t",
            domain_state=DiplomacyState(
                current_regime="empire", alignment_stance="covert_maneuver",
                leverage=8.0, network_regime_span=4, compromise_count=3,
            ),
        )
        base = state_to_feature_vector(s)
        ext = state_to_feature_vector_extended(s)
        assert len(base) == 12
        # regime 7 + stance 5 + scalars 3 = 15 extra
        assert len(ext) == 27

    def test_different_regimes_produce_different_features(self, _setup):
        s1 = AgentState(
            agent_id="t",
            domain_state=DiplomacyState(current_regime="empire"),
        )
        s2 = AgentState(
            agent_id="t",
            domain_state=DiplomacyState(current_regime="ancien_regime"),
        )
        # emotions/physical/slow_state 모두 동일, regime만 다름
        assert state_to_feature_vector_extended(s1) != state_to_feature_vector_extended(s2)


class TestDiplomacyStateToFeatureVector:
    def test_regime_onehot(self, _setup):
        ds = DiplomacyState(current_regime="empire")
        fv = ds.to_feature_vector()
        # empire = regime index 4 (0-indexed)
        regime_slice = fv[0:7]
        assert regime_slice[4] == 1.0
        assert sum(regime_slice) == 1.0

    def test_stance_onehot(self, _setup):
        ds = DiplomacyState(alignment_stance="covert_maneuver")
        fv = ds.to_feature_vector()
        stance_slice = fv[7:12]
        # covert_maneuver = stance index 2
        assert stance_slice[2] == 1.0
        assert sum(stance_slice) == 1.0

    def test_scalars_normalized(self, _setup):
        ds = DiplomacyState(
            leverage=5.0, network_regime_span=7, compromise_count=5,
        )
        fv = ds.to_feature_vector()
        assert abs(fv[12] - 0.5) < 1e-9  # leverage
        assert abs(fv[13] - 1.0) < 1e-9  # span = 7/7
        assert abs(fv[14] - 0.5) < 1e-9  # compromise 5/10


class TestExtensibleEncoder:
    def test_lazy_weight_init(self, _setup):
        enc = ExtensibleFixedProjectionEncoder(dim=5, seed=0)
        assert enc._W is None
        s = AgentState(agent_id="t", emotions=EmotionalState())
        enc.encode(s)
        assert enc._W is not None
        assert enc._feature_len == 12  # plain base

    def test_talleyrand_encoder_uses_27_features(self, _setup):
        enc = ExtensibleFixedProjectionEncoder(dim=5, seed=0)
        s = AgentState(
            agent_id="t",
            domain_state=DiplomacyState(),
        )
        enc.encode(s)
        assert enc._feature_len == 27

    def test_feature_len_locked_after_first(self, _setup):
        """첫 호출로 length 고정 — 이후 다른 길이 state는 예외."""
        enc = ExtensibleFixedProjectionEncoder(dim=5, seed=0)
        s_plain = AgentState(agent_id="t", emotions=EmotionalState())
        enc.encode(s_plain)  # 12 features
        s_talleyrand = AgentState(
            agent_id="t", domain_state=DiplomacyState(),
        )
        # 27 features → length mismatch
        with pytest.raises(ValueError, match="feature length changed"):
            enc.encode(s_talleyrand)

    def test_different_regimes_different_drive(self, _setup):
        """같은 감정 상태에서 regime만 다르면 drive도 다름."""
        enc = ExtensibleFixedProjectionEncoder(dim=5, seed=0)
        s1 = AgentState(
            agent_id="t",
            domain_state=DiplomacyState(current_regime="empire"),
        )
        s2 = AgentState(
            agent_id="t",
            domain_state=DiplomacyState(current_regime="ancien_regime"),
        )
        d1 = enc.encode(s1).values
        d2 = enc.encode(s2).values
        assert d1 != d2


class TestFeatureGapDocumentation:
    """Iter 67 empirical finding: random projection만으로는 domain feature의
    separability 이득을 **자동으로** 내지 못한다.

    Extended encoder (27 feature)가 FixedProjection (12 feature) 대비
    separability를 유의하게 높이지 않음 (0.19 vs 0.24). 이유:
    random W가 sparse one-hot에 유의한 가중치를 주지 않고, 추가 차원이
    within-variance를 오히려 늘려 Fisher ratio를 희석.

    **결론**: domain feature gap은 feature 추가만으로 해소되지 않음.
    **Stage 2 PyTorch 학습 (구조화 feature에 가중치를 실제 학습)**이
    필요. 또는 one-hot feature를 직접 drive 차원에 주입하는 smart projection.

    이 테스트는 그 empirical 사실을 regression lock-in.
    """

    def test_extended_encoder_produces_valid_drive(self, _setup):
        """Extensible encoder가 Talleyrand state에 대해 정상 작동 — drive값 생성."""
        from engine.io.loader import load_agent_state

        CONTENT = Path(__file__).resolve().parent.parent.parent / "content"
        t = load_agent_state(CONTENT / "talleyrand" / "initial_state.json")
        enc = ExtensibleFixedProjectionEncoder(dim=5, seed=0)
        drive = enc.encode(t)
        assert len(drive.values) == 5
        for v in drive.values:
            assert -1.0 <= v <= 1.0

    def test_random_projection_does_not_auto_solve_gap(self, _setup):
        """Fixed 12-feature vs Extended 27-feature — random projection 하에서는
        두 separability가 similar order (both < 0.5). Learning 필요.
        """
        from engine.core.world import SimulationConfig
        from engine.io.loader import (
            load_agent_state,
            load_behavior_profile,
            load_events,
        )
        from engine.rules.base import RuleEngine
        from engine.rules.emotional import (
            ConfusionRule,
            FearResponseRule,
            GriefRule,
            HopeRule,
        )
        from engine.rules.physical import FatigueRule
        from engine.rules.temporal import HomeostasisRule
        from engine.simulation.drive_training import (
            collect_trajectories,
            trajectories_to_samples,
        )
        from engine.simulation.training_samples import (
            compute_drive_action_diagnostics,
            drive_class_separability,
        )
        from engine.simulation.world import SimulationWorld

        CONTENT = Path(__file__).resolve().parent.parent.parent / "content"

        def run(seed: int):
            t = load_agent_state(CONTENT / "talleyrand" / "initial_state.json")
            events = load_events(CONTENT / "talleyrand" / "canonical_events.json")
            profile = load_behavior_profile(
                CONTENT / "talleyrand" / "behavior_profile.json",
            )
            config = SimulationConfig(
                initial_state=t, initial_states=[t],
                max_tick=200, state_noise_scale=0.02, events=events,
            )
            rules = RuleEngine([
                FearResponseRule(), HopeRule(), GriefRule(), ConfusionRule(),
                FatigueRule(), HomeostasisRule(),
            ])
            return SimulationWorld(
                config, rules, behavior_profiles={"talleyrand": profile},
            ).run(seed=seed)

        results = collect_trajectories(run, n_runs=3)
        samples = trajectories_to_samples(results)

        sep_fixed = drive_class_separability(
            compute_drive_action_diagnostics(
                samples, FixedProjectionEncoder(dim=5, seed=0),
            ),
        )
        sep_ext = drive_class_separability(
            compute_drive_action_diagnostics(
                samples, ExtensibleFixedProjectionEncoder(dim=5, seed=0),
            ),
        )
        # 둘 다 0.5 미만으로 Stage 2 feasibility 기준 미달
        assert sep_fixed < 0.5
        assert sep_ext < 0.5
