"""Cross-scenario Stage 2 feasibility spectrum (Iter 66).

FixedProjectionEncoder (12-feature, 5-dim) 위에서 세 시나리오 action
class 분리도 측정:
- Peter (passion): ≈ 1.93 (Stage 2 feasible)
- Van Gogh (Arles): ≈ 6.04 (very feasible)
- Talleyrand (50-year career): **≈ 0.05 (NOT feasible!)**

**발견**: 12-feature 벡터는 emotions/physical/slow_state만 포함하고
domain_state의 Literal 필드(e.g., current_regime, alignment_stance)는 누락.
Talleyrand의 action 선택은 regime/alignment에 의존 → 현 feature로 분리 불가.

**의미**: Stage 2 PyTorch 학습이 "universal"하려면 각 시나리오의 domain_state를
feature set에 포함시켜야 함. 현재 state_to_feature_vector는 Peter/VG에 편향.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from content.talleyrand.domain_diplomacy import DiplomacyState
from engine.core.latent_drive import FixedProjectionEncoder
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_events,
    register_domain_type,
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


@pytest.fixture(scope="module")
def _setup():
    register_domain_type("diplomacy", DiplomacyState)
    return None


def _rules_talleyrand() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(), ConfusionRule(),
        FatigueRule(), HomeostasisRule(),
    ])


def _run_talleyrand(seed: int):
    t = load_agent_state(CONTENT / "talleyrand" / "initial_state.json")
    events = load_events(CONTENT / "talleyrand" / "canonical_events.json")
    profile = load_behavior_profile(CONTENT / "talleyrand" / "behavior_profile.json")
    config = SimulationConfig(
        initial_state=t, initial_states=[t],
        max_tick=300, state_noise_scale=0.02,
        events=events,
    )
    return SimulationWorld(
        config, _rules_talleyrand(),
        behavior_profiles={"talleyrand": profile},
    ).run(seed=seed)


class TestTalleyrandLowSeparability:
    """Talleyrand 시나리오는 현 12-feature 셋으로 학습 불가능 신호."""

    def test_separability_below_threshold(self, _setup):
        """separability이 0.5 미만 — domain_state 미포함 feature의 한계 증명.

        Peter 1.93, VG 6.04 대비 Talleyrand < 0.5이면 **feature 확장 필요** 신호.
        """
        results = collect_trajectories(_run_talleyrand, n_runs=3)
        samples = trajectories_to_samples(results)
        enc = FixedProjectionEncoder(dim=5, seed=0)
        diags = compute_drive_action_diagnostics(samples, enc)
        sep = drive_class_separability(diags)
        assert sep < 0.5, (
            f"Talleyrand separability={sep:.3f}, expected < 0.5 for "
            "feature-gap diagnosis. 수치가 크게 올라갔다면 "
            "feature set이 확장되어 domain_state를 포함한 것. "
            "이 테스트의 의미(=Talleyrand는 domain-aware feature 필요)를 "
            "재평가하고 업데이트 필요."
        )

    def test_at_least_three_actions_observed(self, _setup):
        """Talleyrand 3-seed run에서 최소 3개 action 관측."""
        results = collect_trajectories(_run_talleyrand, n_runs=3)
        samples = trajectories_to_samples(results)
        enc = FixedProjectionEncoder(dim=5, seed=0)
        diags = compute_drive_action_diagnostics(samples, enc)
        assert len(diags) >= 3


class TestStage2FeatureGapDocumentation:
    """Feature gap 발견을 regression test로 고정.

    이 테스트가 실패하면 Iter 66의 finding이 이미 해결되었거나 feature가
    변경된 것이므로 `lessons.md` / `DESIGN_LATENT_DRIVE.md`를 업데이트.
    """

    def test_diplomacy_state_not_in_current_feature_vector(self):
        """state_to_feature_vector는 domain_state를 무시함을 확인."""
        from engine.core.state import AgentState
        from engine.simulation.training_samples import state_to_feature_vector

        a = AgentState(
            agent_id="t",
            domain_state=DiplomacyState(
                current_regime="empire",
                alignment_stance="covert_maneuver",
                leverage=9.0,
                network_regime_span=5,
            ),
        )
        b = AgentState(
            agent_id="t",
            domain_state=DiplomacyState(
                current_regime="ancien_regime",
                alignment_stance="overt_loyal",
                leverage=2.0,
                network_regime_span=1,
            ),
        )
        # 두 agent가 domain_state만 다르고 emotions/physical/slow_state 동일 →
        # 현 feature 추출기는 동일 feature 반환.
        assert state_to_feature_vector(a) == state_to_feature_vector(b)
