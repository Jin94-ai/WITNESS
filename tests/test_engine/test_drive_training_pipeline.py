"""v1.0 Stage 2 pipeline skeleton tests.

drive_training.py의 collect/train/validate 인터페이스 검증.
실제 학습은 Stage 2 full implementation에서.
"""

from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.latent_drive import LatentDriveModel
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_interventions,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.drive_training import (
    TrainingConfig,
    ValidationReport,
    collect_trajectories,
    train_and_validate,
    train_drive_model,
    trajectories_to_samples,
    validate_drive_model,
)
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _make_run_fn(max_tick: int = 20):
    """Small simulator run function for pipeline testing."""
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT_DIR / "crowd" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
    profiles = {
        "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
        "crowd": load_behavior_profile(CONTENT_DIR / "crowd" / "behavior_profile.json"),
    }
    config = SimulationConfig(
        max_tick=max_tick, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.01,
    )
    engine = RuleEngine([FearResponseRule(), HopeRule(), HomeostasisRule()])

    def run_fn(seed: int):
        return SimulationWorld(config, engine, behavior_profiles=profiles).run(seed=seed)

    return run_fn


class TestTrainingConfig:
    def test_default_values(self):
        cfg = TrainingConfig()
        assert cfg.drive_dim == 5
        assert cfg.n_runs == 100
        # Loss weights
        assert cfg.alpha_action == 1.0
        assert cfg.lambda_kl == 0.01


class TestCollectTrajectories:
    def test_collect_n_runs(self):
        run_fn = _make_run_fn(max_tick=15)
        results = collect_trajectories(run_fn, n_runs=3)
        assert len(results) == 3
        # 각 결과가 state_snapshots 보유
        for r in results:
            assert hasattr(r, "state_snapshots")

    def test_custom_seeds(self):
        run_fn = _make_run_fn(max_tick=15)
        results = collect_trajectories(run_fn, n_runs=2, seeds=[42, 99])
        assert len(results) == 2
        # Seed 적용됨 — seed 파라미터는 유지되는가
        assert hasattr(results[0], "seed")


class TestTrajectoriesToSamples:
    def test_sample_extraction(self):
        run_fn = _make_run_fn(max_tick=20)
        results = collect_trajectories(run_fn, n_runs=2)
        samples = trajectories_to_samples(results)
        # 최소 agent_id × time_pairs 개수
        assert len(samples) > 0
        # 각 sample이 state + next_state 보유
        s = samples[0]
        assert s.state is not None
        assert s.next_state is not None
        assert s.next_tick > s.tick


class TestTrainDriveModel:
    def test_train_returns_model(self):
        run_fn = _make_run_fn(max_tick=15)
        results = collect_trajectories(run_fn, n_runs=2)
        samples = trajectories_to_samples(results)
        cfg = TrainingConfig(drive_dim=3, n_runs=2)
        model = train_drive_model(samples, cfg)
        assert isinstance(model, LatentDriveModel)
        assert model.dim == 3

    def test_train_identity_fallback_active(self):
        """현재 skeleton은 identity 반환하므로 is_active = True."""
        run_fn = _make_run_fn(max_tick=15)
        results = collect_trajectories(run_fn, n_runs=1)
        samples = trajectories_to_samples(results)
        cfg = TrainingConfig(drive_dim=5, n_runs=1)
        model = train_drive_model(samples, cfg)
        assert model.is_active()  # encoder=IdentityEncoder

    def test_empty_samples_raises(self):
        cfg = TrainingConfig()
        with pytest.raises(ValueError):
            train_drive_model([], cfg)

    def test_use_fixed_projection_returns_non_identity(self):
        """Iter 61: use_fixed_projection=True → FixedProjectionEncoder, drive가 state 변화에 반응."""
        from engine.core.latent_drive import (
            FixedProjectionEncoder,
            IdentityEncoder,
        )
        from engine.core.state import AgentState, EmotionalState
        run_fn = _make_run_fn(max_tick=15)
        results = collect_trajectories(run_fn, n_runs=1)
        samples = trajectories_to_samples(results)

        cfg_identity = TrainingConfig(drive_dim=5, n_runs=1, use_fixed_projection=False)
        cfg_fixed = TrainingConfig(drive_dim=5, n_runs=1, use_fixed_projection=True, random_seed=7)

        m_id = train_drive_model(samples, cfg_identity)
        m_fp = train_drive_model(samples, cfg_fixed)

        assert isinstance(m_id.encoder, IdentityEncoder)
        assert isinstance(m_fp.encoder, FixedProjectionEncoder)

        # 두 encoder가 같은 state에 대해 다른 drive 반환
        probe = AgentState(
            agent_id="probe",
            emotions=EmotionalState(fear=7.0, hope=3.0),
        )
        d_id = m_id.encoder.encode(probe).values
        d_fp = m_fp.encoder.encode(probe).values
        assert d_id != d_fp

    def test_fixed_projection_seed_affects_output(self):
        """random_seed가 FixedProjection 초기화 seed로 전달됨."""
        from engine.core.state import AgentState, EmotionalState
        run_fn = _make_run_fn(max_tick=15)
        samples = trajectories_to_samples(collect_trajectories(run_fn, n_runs=1))

        cfg_a = TrainingConfig(drive_dim=5, n_runs=1, use_fixed_projection=True, random_seed=0)
        cfg_b = TrainingConfig(drive_dim=5, n_runs=1, use_fixed_projection=True, random_seed=99)

        m_a = train_drive_model(samples, cfg_a)
        m_b = train_drive_model(samples, cfg_b)
        probe = AgentState(agent_id="p", emotions=EmotionalState(fear=5.0))
        assert m_a.encoder.encode(probe).values != m_b.encoder.encode(probe).values

    def test_use_learned_linear_returns_fit_encoder(self):
        """Iter 73: use_learned_linear=True → LearnedLinearEncoder, 자동 fit됨."""
        from engine.core.latent_drive import (
            FixedProjectionEncoder,
            LearnedLinearEncoder,
        )
        from engine.core.state import AgentState, EmotionalState

        # 최소 action 다양성 있는 run (multi-agent Peter)
        run_fn = _make_run_fn(max_tick=40)
        samples = trajectories_to_samples(collect_trajectories(run_fn, n_runs=2))
        # n_classes >= 2 필요 — action 있는 샘플 필터링 후 확인
        actions = {s.action for s in samples if s.action is not None}
        # Multi-agent 40 tick면 통상 2+ action
        if len(actions) < 2:
            return  # skip if test run produced too few classes

        cfg = TrainingConfig(
            drive_dim=5, n_runs=2, use_learned_linear=True,
        )
        model = train_drive_model(samples, cfg)
        assert isinstance(model.encoder, LearnedLinearEncoder)
        assert model.encoder._model is not None  # 내부 LDA fit됨

        # encode 가능
        probe = AgentState(agent_id="probe", emotions=EmotionalState(fear=5.0))
        drive = model.encoder.encode(probe)
        assert len(drive.values) == 5
        assert not isinstance(model.encoder, FixedProjectionEncoder)

    def test_use_learned_linear_precedes_fixed_projection(self):
        """두 flag 모두 True면 learned_linear가 우선."""
        from engine.core.latent_drive import LearnedLinearEncoder

        run_fn = _make_run_fn(max_tick=40)
        samples = trajectories_to_samples(collect_trajectories(run_fn, n_runs=2))
        if len({s.action for s in samples if s.action is not None}) < 2:
            return

        cfg = TrainingConfig(
            drive_dim=5, n_runs=2,
            use_learned_linear=True,
            use_fixed_projection=True,
        )
        model = train_drive_model(samples, cfg)
        assert isinstance(model.encoder, LearnedLinearEncoder)


class TestValidateDriveModel:
    def test_validate_returns_report(self):
        model = LatentDriveModel()
        report = validate_drive_model(model)
        assert isinstance(report, ValidationReport)
        assert "Skeleton" in report.notes

    def test_validate_with_baseline(self):
        run_fn = _make_run_fn(max_tick=15)
        model = LatentDriveModel()
        report = validate_drive_model(model, baseline_run_fn=run_fn, n_validation_runs=2)
        # n_samples = total TrainingSample tuples across 2 baseline runs (agent × tick pair)
        assert report.n_samples > 0
        assert report.sample_stats is not None
        assert report.sample_stats.n_agents >= 1

    def test_validate_stats_fields_populated(self):
        run_fn = _make_run_fn(max_tick=20)
        model = LatentDriveModel()
        report = validate_drive_model(model, baseline_run_fn=run_fn, n_validation_runs=2)
        stats = report.sample_stats
        assert stats is not None
        assert stats.feature_dim == 12
        assert stats.avg_tick_delta > 0
        assert 0.0 <= stats.event_rate <= 1.0


class TestEndToEndPipeline:
    def test_train_and_validate_flow(self):
        """E2E: collect → train → validate 파이프라인 작동."""
        run_fn = _make_run_fn(max_tick=15)
        cfg = TrainingConfig(drive_dim=3, n_runs=2)
        model, report = train_and_validate(run_fn, cfg)
        assert model.is_active()
        assert report.n_samples > 0
        assert report.sample_stats is not None
