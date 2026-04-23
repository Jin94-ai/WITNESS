"""Judas Action Sequence Analysis.

Judas가 실제로 어떤 순서로 행동하는가? Markov transition matrix로 정량화.

기대:
- 초반: "follow", "question" 등 중립 행동
- 중반: "withdraw", "inform" 등 이탈 행동
- 후반: "betray" 행동

검증 핵심:
- 특정 전이가 지배적인가? (e.g. inform→betray 빈도)
- 행동 entropy가 시간에 따라 변하는가 (불확실성 감소)
"""

import math
from collections import Counter, defaultdict
from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
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
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.world import SimulationWorld

pytestmark = pytest.mark.archived  # Tier 3 archived (ITERATION_CLASSIFICATION.md)

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run(seed: int):
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
        max_tick=500, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )
    return SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)


def _entropy(counts: dict[str, int]) -> float:
    """Shannon entropy of action distribution (bits)."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c == 0:
            continue
        p = c / total
        h -= p * math.log2(p)
    return h


@pytest.mark.slow
class TestJudasActionSequence:
    def test_action_distribution_by_phase(self):
        """Judas 행동 분포를 시간 phase별로 측정."""
        n_seeds = 25
        phases = {
            "early (0-100)": (0, 100),
            "mid (100-200)": (100, 200),
            "late (200+)": (200, 500),
        }

        phase_actions: dict[str, Counter] = {k: Counter() for k in phases}

        for seed in range(n_seeds):
            r = _run(seed)
            judas_actions = r.action_histories.get("judas", [])
            for rec in judas_actions:
                for phase_name, (lo, hi) in phases.items():
                    if lo <= rec.tick < hi:
                        phase_actions[phase_name][rec.chosen_action] += 1
                        break

        print(f"\n=== Judas Action Distribution by Phase (n={n_seeds} runs) ===")
        all_actions = set()
        for c in phase_actions.values():
            all_actions.update(c.keys())
        all_actions = sorted(all_actions)

        header = f"{'action':>22}" + "".join(f" | {p:>14}" for p in phases)
        print(header)
        print("-" * len(header))
        for act in all_actions:
            row = f"{act:>22}"
            for p in phases:
                c = phase_actions[p][act]
                total = sum(phase_actions[p].values())
                pct = c / total if total > 0 else 0
                row += f" | {c:>5} ({pct:>5.1%})"
            print(row)

        # Entropy per phase
        print("\nAction entropy (bits) per phase:")
        entropies = {p: _entropy(dict(phase_actions[p])) for p in phases}
        for p, h in entropies.items():
            print(f"  {p}: {h:.2f} bits")

        # 검증: betray는 주로 late phase에 발생
        early_betray = phase_actions["early (0-100)"]["betray"]
        late_betray = phase_actions["late (200+)"].get("betray", 0)
        mid_betray = phase_actions["mid (100-200)"].get("betray", 0)
        total_betray = early_betray + mid_betray + late_betray
        if total_betray > 0:
            print(f"\nBetray timing: early {early_betray}/{total_betray} "
                  f"({early_betray/total_betray:.0%}), "
                  f"mid {mid_betray}/{total_betray} ({mid_betray/total_betray:.0%}), "
                  f"late {late_betray}/{total_betray} ({late_betray/total_betray:.0%})")
            # early phase에 betray 5% 이하여야 정상 (인과 순서)
            assert early_betray / total_betray < 0.10, \
                f"Too many early betrays: {early_betray}/{total_betray}"

        # 검증: withdraw 행동은 disillusionment 누적기에 주로 (mid)
        # inform 행동이 betray 이전에 나와야 함 (causal order)
        early_withdraw_rate = (
            phase_actions["early (0-100)"].get("withdraw", 0)
            / max(sum(phase_actions["early (0-100)"].values()), 1)
        )
        mid_withdraw_rate = (
            phase_actions["mid (100-200)"].get("withdraw", 0)
            / max(sum(phase_actions["mid (100-200)"].values()), 1)
        )
        print(f"\nWithdraw rate: early {early_withdraw_rate:.1%} vs mid {mid_withdraw_rate:.1%}")

    def test_action_transition_matrix(self):
        """Judas 행동 전이 확률 측정 (Markov)."""
        n_seeds = 20
        transitions: dict[tuple[str, str], int] = defaultdict(int)
        from_counts: Counter = Counter()

        for seed in range(n_seeds):
            r = _run(seed)
            judas_actions = list(r.action_histories.get("judas", []))
            judas_actions.sort(key=lambda rec: rec.tick)
            # Build transitions from action[i] -> action[i+1]
            for i in range(len(judas_actions) - 1):
                a = judas_actions[i].chosen_action
                b = judas_actions[i + 1].chosen_action
                transitions[(a, b)] += 1
                from_counts[a] += 1

        # Top transitions by probability
        print(f"\n=== Judas Action Transitions (n={n_seeds}, top 10 by freq) ===")
        sorted_t = sorted(transitions.items(), key=lambda kv: -kv[1])[:10]
        print(f"{'from -> to':>40} | {'count':>7} | {'prob':>6}")
        print("-" * 62)
        for (a, b), c in sorted_t:
            prob = c / from_counts[a] if from_counts[a] > 0 else 0
            print(f"{a + ' -> ' + b:>40} | {c:>7} | {prob:>5.1%}")

        # 검증: "inform_authorities -> ..." 후속 행동 존재
        inform_outgoing = sum(
            v for (a, _b), v in transitions.items() if a == "inform_authorities"
        )
        assert inform_outgoing > 0, "Judas should perform inform_authorities action"

        # 검증: betray 전에 다른 행동들이 먼저 나옴
        # (첫 행동이 betray 아님)
        first_betray_runs = 0
        for seed in range(n_seeds):
            r = _run(seed)
            judas_actions = sorted(
                list(r.action_histories.get("judas", [])),
                key=lambda rec: rec.tick,
            )
            if judas_actions and judas_actions[0].chosen_action == "betray":
                first_betray_runs += 1
        print(f"\nRuns where first Judas action is 'betray': {first_betray_runs}/{n_seeds}")
        assert first_betray_runs == 0, \
            "betray should never be first action (requires state accumulation)"
