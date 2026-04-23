"""Extended Explanation Faithfulness (n=30+, per-agent ablation).

LLM 리뷰 4차 피드백 (ChatGPT Q12):
"설명에 언급된 요인을 제거하면 결과가 바뀌는지 점검해야."

기존 test_explanation_faithfulness.py는 n=10 + 전체 Judas 제거만.
확장:
1. n=30 baseline chain 수집
2. Chain에서 언급된 각 에이전트별 제거 → outcome 변화 측정
3. Per-chain agent importance score 계산 (removed → spontaneous arrest rate drop)
4. Explanation이 언급한 순서대로 중요도가 나오는가? (인과 순서 충실성)
"""

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
from engine.simulation.explanation import generate_explanation
from engine.simulation.statistics import proportion_ci
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _load_all():
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
    return {
        "peter": peter, "judas": judas, "caiaphas": caiaphas, "crowd": crowd,
        "triggers": triggers, "hazards": hazards, "interventions": interventions,
        "profiles": profiles,
    }


def _run_baseline(seed: int, ctx: dict):
    config = SimulationConfig(
        max_tick=500, initial_state=ctx["peter"],
        initial_states=[ctx["peter"], ctx["judas"], ctx["caiaphas"], ctx["crowd"]],
        hazard_events=ctx["hazards"], interventions=ctx["interventions"],
        triggers=ctx["triggers"], state_noise_scale=0.05,
    )
    return SimulationWorld(config, _engine(), behavior_profiles=ctx["profiles"]).run(seed=seed)


def _run_without(agent_to_remove: str, seed: int, ctx: dict):
    all_agents = {
        "peter": ctx["peter"], "judas": ctx["judas"],
        "caiaphas": ctx["caiaphas"], "crowd": ctx["crowd"],
    }
    states = [v for k, v in all_agents.items() if k != agent_to_remove]
    profiles = {k: v for k, v in ctx["profiles"].items() if k != agent_to_remove}
    config = SimulationConfig(
        max_tick=500, initial_state=ctx["peter"],
        initial_states=states,
        hazard_events=ctx["hazards"], interventions=ctx["interventions"],
        triggers=ctx["triggers"], state_noise_scale=0.05,
    )
    return SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)


def _spontaneous_rate(results: list) -> tuple[int, int]:
    """(n_spontaneous, n_total) where spontaneous = arrest tick < 400."""
    n_total = len(results)
    n_spontaneous = sum(
        1 for r in results
        if any(
            t["trigger_id"] == "arrest_trigger" and t["tick"] < 400
            for t in r.fired_triggers
        )
    )
    return n_spontaneous, n_total


@pytest.mark.slow
class TestExplanationFaithfulnessExtended:
    def test_per_agent_ablation_matches_chain_mention(self):
        """Chain에서 언급된 에이전트별로 제거하고 impact 측정.
        Chain이 더 자주 언급한 에이전트 = 더 큰 impact여야 (faithfulness).
        """
        ctx = _load_all()
        N_BASELINE = 30
        N_ABLATION = 15

        # Phase 1: n=30 baseline runs + chain 수집
        chain_mentions: dict[str, int] = {}
        baseline_results = []
        for seed in range(N_BASELINE):
            r = _run_baseline(seed, ctx)
            baseline_results.append(r)
            card = generate_explanation(r)
            for step in card.get("causal_chain", []):
                agent = step.get("agent", "")
                if agent and agent != "system":
                    chain_mentions[agent] = chain_mentions.get(agent, 0) + 1

        baseline_spont, baseline_n = _spontaneous_rate(baseline_results)
        baseline_rate = baseline_spont / baseline_n

        print(f"\n=== Chain Mention Frequency (n={N_BASELINE} baseline runs) ===")
        for agent, count in sorted(chain_mentions.items(), key=lambda kv: -kv[1]):
            print(f"  {agent}: {count} mentions")

        # Phase 2: 언급된 각 에이전트 제거 → spontaneous rate 측정
        print(f"\n=== Per-Agent Ablation (n={N_ABLATION} runs each) ===")
        print(f"Baseline spontaneous rate: {baseline_rate:.1%}")
        print(f"{'removed':>10} | {'chain mentions':>14} | {'ablation rate':>13} | "
              f"{'impact (drop)':>13}")
        print("-" * 60)

        impact_ranking = []
        all_ablatable = ["judas", "caiaphas", "crowd"]  # peter 제거 시 전체 붕괴
        for agent in all_ablatable:
            ablation_results = [_run_without(agent, s, ctx) for s in range(N_ABLATION)]
            abl_spont, abl_n = _spontaneous_rate(ablation_results)
            abl_rate = abl_spont / abl_n
            impact = baseline_rate - abl_rate
            mentions = chain_mentions.get(agent, 0)
            impact_ranking.append((agent, mentions, abl_rate, impact))
            print(f"{agent:>10} | {mentions:>14} | {abl_rate:>12.1%} | {impact:>+12.1%}")

        # Faithfulness: chain mention 순위 = impact 순위 (Kendall's tau-like)
        # 즉, 가장 많이 언급된 에이전트가 가장 큰 impact
        impact_ranking.sort(key=lambda x: -x[1])  # by mentions
        mention_order = [x[0] for x in impact_ranking]
        impact_order_by_impact = sorted(
            impact_ranking, key=lambda x: -x[3]
        )
        impact_order = [x[0] for x in impact_order_by_impact]

        print("\nRanking by mentions :", mention_order)
        print("Ranking by impact   :", impact_order)

        # 핵심 faithfulness 검증:
        # 가장 많이 언급된 에이전트 = 가장 큰 impact agent여야 함
        top_mentioned = mention_order[0]
        top_impact = impact_order[0]

        assert top_mentioned == top_impact, \
            f"Faithfulness violation: top mentioned={top_mentioned}, " \
            f"top impact={top_impact}"

        # Judas는 반드시 top mentioned (이전 결과와 일치)
        assert top_mentioned == "judas", \
            f"Expected Judas as top mentioned, got {top_mentioned}"

        # Judas ablation impact가 유의미 (>=30pp drop)
        judas_impact = next(x[3] for x in impact_ranking if x[0] == "judas")
        assert judas_impact >= 0.30, \
            f"Judas removal impact {judas_impact:+.1%} too small (expected >=30pp)"

        print(f"\n**FAITHFULNESS VERDICT**: Chain's most-mentioned agent ({top_mentioned}) "
              f"IS the highest-impact agent. Explanation faithful.")

    def test_chain_frequency_aligns_with_spearman(self):
        """Chain에서 특정 에이전트가 언급된 빈도와,
        그 에이전트 제거 시 impact의 Spearman rank correlation.
        Faithful이면 rank = rank (ρ=1).
        """
        ctx = _load_all()
        N_BASELINE = 30
        N_ABLATION = 10

        # Gather mention counts
        chain_mentions: dict[str, int] = {}
        for seed in range(N_BASELINE):
            r = _run_baseline(seed, ctx)
            card = generate_explanation(r)
            for step in card.get("causal_chain", []):
                agent = step.get("agent", "")
                if agent and agent != "system":
                    chain_mentions[agent] = chain_mentions.get(agent, 0) + 1

        # Baseline rate
        baseline = [_run_baseline(s, ctx) for s in range(N_ABLATION)]
        base_spont, _ = _spontaneous_rate(baseline)
        base_rate = base_spont / N_ABLATION

        # Per-agent ablation
        impacts = {}
        for agent in ["judas", "caiaphas", "crowd"]:
            abl = [_run_without(agent, s, ctx) for s in range(N_ABLATION)]
            abl_spont, _ = _spontaneous_rate(abl)
            impacts[agent] = base_rate - abl_spont / N_ABLATION

        # Rank comparison
        mention_rank = sorted(impacts.keys(), key=lambda a: -chain_mentions.get(a, 0))
        impact_rank = sorted(impacts.keys(), key=lambda a: -impacts[a])

        print("\n=== Mention rank vs Impact rank ===")
        print(f"Mention rank: {mention_rank}")
        print(f"Impact rank : {impact_rank}")
        print("\nDetailed:")
        for agent in impacts:
            print(f"  {agent}: {chain_mentions.get(agent, 0)} mentions, "
                  f"impact {impacts[agent]:+.1%}")

        # Spearman rho (for 3 elements)
        # rho=1 if perfect rank match, -1 if reversed
        # with 3 elements: rho = 1 - 6*sum(d²)/(n*(n²-1)) = 1 - 6*sum(d²)/24
        mention_ranks_dict = {a: i for i, a in enumerate(mention_rank)}
        impact_ranks_dict = {a: i for i, a in enumerate(impact_rank)}
        d_sq_sum = sum(
            (mention_ranks_dict[a] - impact_ranks_dict[a]) ** 2
            for a in impacts
        )
        n = len(impacts)
        rho = 1 - 6 * d_sq_sum / (n * (n ** 2 - 1))
        print(f"\nSpearman rho (mention rank vs impact rank): {rho:+.3f}")

        assert rho >= 0.5, \
            f"Rank correlation {rho:.3f} too low (explanation not faithful)"

    def test_explanation_chain_length_consistency(self):
        """Chain 길이의 일관성: n=30에서 chain 길이 분포."""
        ctx = _load_all()
        chain_lengths = []
        for seed in range(30):
            r = _run_baseline(seed, ctx)
            card = generate_explanation(r)
            chain_lengths.append(len(card.get("causal_chain", [])))

        import statistics
        mean_len = statistics.mean(chain_lengths)
        std_len = statistics.stdev(chain_lengths)
        print("\n=== Chain Length (n=30) ===")
        print(f"Mean: {mean_len:.1f}, std: {std_len:.2f}")
        print(f"Range: [{min(chain_lengths)}, {max(chain_lengths)}]")
        print(f"Distribution: {sorted(chain_lengths)}")

        # Chain이 거의 항상 생성되어야 함
        nonzero_count = sum(1 for length in chain_lengths if length > 0)
        ci = proportion_ci(nonzero_count, len(chain_lengths))
        print(f"Non-empty chain rate: {ci.mean:.0%} [{ci.lower:.0%}, {ci.upper:.0%}]")

        assert ci.lower > 0.80, \
            f"Chains generated in too few runs ({ci.lower:.0%} lower bound)"
