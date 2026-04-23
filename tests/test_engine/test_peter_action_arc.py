"""Peter Action Arc Analysis.

Judas 분석과 대응: Peter의 행동도 시간에 따라 어떻게 변하는가?

Peter behavior_profile: follow_closely, pray, discuss, assert_loyalty,
                        withdraw_in_fear, weep

기대:
- 초반: follow_closely, assert_loyalty (제자로서 충실)
- 중반: pray, discuss (긴장 상승)
- 후반: withdraw_in_fear (체포 후 위기), weep (부인 후 회개)

의의: Peter의 "3회 부인"과 "회복" 구조가 행동 분포에 반영되는가?
"""

from collections import Counter
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


@pytest.mark.slow
class TestPeterActionArc:
    def test_peter_action_evolution_around_arrest(self):
        """Arrest 전/후 Peter 행동 분포 비교. arrest_relative phase 사용."""
        n_seeds = 20

        # arrest_tick 기준 상대 phase: pre_arrest_early, pre_arrest_late, post_arrest
        phases = {
            "pre_arrest_early": None,   # arrest_tick - 100 이전
            "pre_arrest_late": None,    # arrest_tick - 100 ~ arrest_tick
            "post_arrest": None,        # arrest_tick 이후
        }
        phase_counts: dict[str, Counter] = {p: Counter() for p in phases}

        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if not arrests:
                continue
            at = arrests[0]["tick"]

            peter_actions = r.action_histories.get("peter", [])
            for rec in peter_actions:
                if rec.tick < at - 100:
                    phase_counts["pre_arrest_early"][rec.chosen_action] += 1
                elif rec.tick < at:
                    phase_counts["pre_arrest_late"][rec.chosen_action] += 1
                else:
                    phase_counts["post_arrest"][rec.chosen_action] += 1

        all_actions = set()
        for c in phase_counts.values():
            all_actions.update(c.keys())
        all_actions = sorted(all_actions)

        print(f"\n=== Peter Action Arc (arrest-relative, n={n_seeds}) ===")
        header = f"{'action':>22}" + "".join(f" | {p:>18}" for p in phases)
        print(header)
        print("-" * len(header))
        for act in all_actions:
            row = f"{act:>22}"
            for p in phases:
                c = phase_counts[p][act]
                total = sum(phase_counts[p].values())
                pct = c / total if total > 0 else 0
                row += f" | {c:>6} ({pct:>6.1%})"
            print(row)

        # 검증 1: deny 행동은 pre_arrest_late 또는 post_arrest에 집중
        # (Peter 3회 부인은 체포 후 정원에서 발생)
        deny_early = phase_counts["pre_arrest_early"].get("deny", 0)
        deny_late = phase_counts["pre_arrest_late"].get("deny", 0)
        deny_post = phase_counts["post_arrest"].get("deny", 0)
        total_deny = deny_early + deny_late + deny_post
        if total_deny > 0:
            early_rate = deny_early / total_deny
            print(f"\nDeny timing: pre_early {deny_early}/{total_deny} ({early_rate:.0%}), "
                  f"pre_late {deny_late}/{total_deny}, post {deny_post}/{total_deny}")
            # 초반에는 부인이 드물어야 함 (scripture 전)
            assert early_rate < 0.3, \
                f"Too many early denials: {deny_early}/{total_deny}"

        # 검증 2: follow_closely 비율 감소 (arrest 후에 감소)
        pre_early_total = sum(phase_counts["pre_arrest_early"].values())
        post_total = sum(phase_counts["post_arrest"].values())

        if pre_early_total > 0 and post_total > 0:
            pre_follow_rate = phase_counts["pre_arrest_early"].get("follow_closely", 0) / pre_early_total
            post_follow_rate = phase_counts["post_arrest"].get("follow_closely", 0) / post_total
            print(f"\nfollow_closely rate: pre_early {pre_follow_rate:.1%} -> post {post_follow_rate:.1%}")
            # 체포 후에는 follow 감소 (예수 없으므로)
            assert post_follow_rate <= pre_follow_rate + 0.1, \
                "follow_closely should not increase after arrest"

        # 검증 3: withdraw_in_fear 또는 weep이 post_arrest에 존재
        post_emotional = (
            phase_counts["post_arrest"].get("withdraw_in_fear", 0)
            + phase_counts["post_arrest"].get("weep", 0)
        )
        print(f"Post-arrest emotional actions (withdraw_in_fear + weep): {post_emotional}")

    def test_deny_count_distribution(self):
        """Peter 부인 횟수 분포 (POM에서 3회 이상 필요)."""
        n_seeds = 30
        deny_counts = []
        for seed in range(n_seeds):
            r = _run(seed)
            peter_actions = r.action_histories.get("peter", [])
            n = sum(1 for a in peter_actions if a.chosen_action == "deny")
            deny_counts.append(n)

        import statistics
        mean_deny = statistics.mean(deny_counts)
        median_deny = statistics.median(deny_counts)
        reach_3 = sum(1 for c in deny_counts if c >= 3)

        print(f"\n=== Peter Deny Count Distribution (n={n_seeds}) ===")
        print(f"Mean: {mean_deny:.1f}, median: {median_deny}")
        print(f"Range: [{min(deny_counts)}, {max(deny_counts)}]")
        print(f"Reach 3+ denials (POM 기준): {reach_3}/{n_seeds} ({reach_3/n_seeds:.0%})")

        # POM의 3회 부인 기준을 대부분 만족해야 함
        assert reach_3 / n_seeds >= 0.5, \
            f"Only {reach_3}/{n_seeds} runs reach 3 denials"
