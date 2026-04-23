"""LearnedLinearEncoder (sklearn LDA) 검증 (Iter 72).

Stage 2 첫 실제 학습 단계: random FixedProjection → LDA-trained projection.
separability가 class-optimal로 증가함을 empirical 확인.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.core.latent_drive import (
    FixedProjectionEncoder,
    LearnedLinearEncoder,
)
from engine.core.state import (
    AgentState,
    EmotionalState,
    PhysicalState,
    SlowState,
)
from engine.simulation.training_samples import TrainingSample


def _sample(action: str, fear: float = 2.0, hope: float = 5.0) -> TrainingSample:
    s = AgentState(
        agent_id="t",
        emotions=EmotionalState(fear=fear, hope=hope),
        physical=PhysicalState(),
        slow_state=SlowState(),
    )
    return TrainingSample(
        agent_id="t", tick=0, state=s,
        action=action, event_ids=[],
        next_state=s, next_tick=1,
    )


class TestLearnedLinearEncoderContract:
    def test_default_dim(self):
        enc = LearnedLinearEncoder(dim=5)
        assert enc.dim == 5
        assert enc._model is None

    def test_encode_before_fit_raises(self):
        enc = LearnedLinearEncoder(dim=5)
        s = AgentState(agent_id="t")
        with pytest.raises(RuntimeError, match="fit"):
            enc.encode(s)

    def test_dim_out_of_range(self):
        with pytest.raises(ValueError):
            LearnedLinearEncoder(dim=0)
        with pytest.raises(ValueError):
            LearnedLinearEncoder(dim=9)


class TestFitWithFakeSamples:
    def test_fit_on_well_separated_classes(self):
        """fear-dominated vs hope-dominated actions — 학습 가능."""
        samples = []
        for i in range(8):
            samples.append(_sample("panic", fear=9.0 - 0.1 * i, hope=1.0))
            samples.append(_sample("rejoice", fear=1.0, hope=9.0 - 0.1 * i))
        enc = LearnedLinearEncoder(dim=2)
        enc.fit(samples)
        assert enc._model is not None
        assert enc._n_features == 12

    def test_encode_returns_dim_values(self):
        samples = []
        # noise 포함한 두 class (LDA는 per-class covariance 필요)
        for i in range(8):
            samples.append(_sample("a", fear=8.0 + 0.1 * i, hope=1.0 + 0.05 * i))
            samples.append(_sample("b", fear=1.0 + 0.05 * i, hope=8.0 + 0.1 * i))
        enc = LearnedLinearEncoder(dim=5)
        enc.fit(samples)
        probe = AgentState(
            agent_id="probe",
            emotions=EmotionalState(fear=8.0, hope=1.0),
        )
        drive = enc.encode(probe)
        assert len(drive.values) == 5

    def test_fit_error_on_too_few_samples(self):
        samples = [_sample("only_one")]
        enc = LearnedLinearEncoder()
        with pytest.raises(ValueError, match="samples"):
            enc.fit(samples)

    def test_fit_error_on_single_class(self):
        samples = [_sample("only_one", fear=i) for i in range(1, 6)]
        enc = LearnedLinearEncoder()
        with pytest.raises(ValueError, match="distinct actions"):
            enc.fit(samples)


class TestPeterLearnedSeparability:
    """Peter 실제 trajectory에서 학습된 projection이 random보다 훨씬 높은
    separability를 보이는지 empirical 확인.
    """

    def test_learned_beats_random_on_peter(self):
        from content.caiaphas.domain_politics import PoliticalCalculationState
        from content.crowd.domain_crowd import CrowdDynamicsState
        from content.judas.domain_betrayal import BetrayalPsychologyState
        from content.peter.domain_faith import FaithJourneyState
        from engine.core.world import SimulationConfig
        from engine.io.loader import (
            load_agent_state,
            load_behavior_profile,
            load_events,
            load_hazard_events,
            load_triggers,
            register_domain_type,
        )
        from engine.rules.base import RuleEngine
        from engine.rules.emotional import (
            ConfusionRule,
            FearResponseRule,
            GriefRule,
            HopeRule,
            LoveRule,
        )
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

        for t, c in [
            ("faith_journey", FaithJourneyState),
            ("betrayal_psychology", BetrayalPsychologyState),
            ("political_calculation", PoliticalCalculationState),
            ("crowd_dynamics", CrowdDynamicsState),
        ]:
            register_domain_type(t, c)

        CONTENT = Path(__file__).resolve().parent.parent.parent / "content"

        def _run(seed: int):
            peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
            judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
            cai = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
            crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
            events = load_events(CONTENT / "peter" / "canonical_events.json")
            triggers = load_triggers(CONTENT / "shared" / "triggers.json")
            hazards = load_hazard_events(CONTENT / "peter" / "hazard_events.json")
            profiles = {
                n: load_behavior_profile(CONTENT / n / "behavior_profile.json")
                for n in ["peter", "judas", "caiaphas", "crowd"]
            }
            config = SimulationConfig(
                initial_state=peter,
                initial_states=[peter, judas, cai, crowd],
                max_tick=150, state_noise_scale=0.02,
                events=events, triggers=triggers, hazard_events=hazards,
            )
            rules = RuleEngine([
                FearResponseRule(), HopeRule(), GriefRule(), ConfusionRule(),
                LoveRule(), HomeostasisRule(),
            ])
            return SimulationWorld(
                config, rules, behavior_profiles=profiles,
            ).run(seed=seed)

        results = collect_trajectories(_run, n_runs=3)
        samples = [
            s for s in trajectories_to_samples(results) if s.action is not None
        ]
        # 드문 class 제거
        from collections import Counter
        cnt = Counter(s.action for s in samples)
        keep = {a for a, n in cnt.items() if n >= 3}
        samples = [s for s in samples if s.action in keep]

        # Random projection baseline
        fixed = FixedProjectionEncoder(dim=5, seed=0)
        diags_fixed = compute_drive_action_diagnostics(samples, fixed)
        sep_fixed = drive_class_separability(diags_fixed)

        # Learned LDA projection
        learned = LearnedLinearEncoder(dim=5)
        learned.fit(samples)
        diags_learned = compute_drive_action_diagnostics(samples, learned)
        sep_learned = drive_class_separability(diags_learned)

        # 학습된 버전이 random 대비 훨씬 높음 (LDA = Fisher ratio optimal).
        # 같은 샘플에서 측정하므로 overfitting 포함이지만 비교는 의미 있음.
        assert sep_learned > sep_fixed * 2.0, (
            f"fixed={sep_fixed:.2f}, learned={sep_learned:.2f} — "
            "학습된 projection이 random 대비 기대만큼 개선 안 됨"
        )
