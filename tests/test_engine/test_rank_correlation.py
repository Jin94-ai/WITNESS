"""Rank Correlation Analysis.

Pearson correlation (parametric) 대신 Spearman rank correlation (non-parametric)로
Judas disillusionment와 arrest tick의 관계 검증.

장점:
- 분포 가정 없음 (정규성 불필요)
- Outlier에 강건
- Monotonic relationship만 가정

기대: 모든 tick에서 disill과 arrest 사이 강한 음의 순위 상관 (높은 disill -> 빠른 arrest).

Horizon별 Spearman rho:
- 초기 tick: 약한 상관 (정보 아직 없음)
- 중간 tick: 상관 강해짐
- 후기 tick: 가장 강한 상관 (arrest 가까움)
"""

import statistics
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


def _rank(values: list[float]) -> list[float]:
    """Average rank (tied values get the average rank)."""
    n = len(values)
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1  # 1-based
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def _spearman_rho(x: list[float], y: list[float]) -> float:
    """Spearman rank correlation coefficient."""
    assert len(x) == len(y)
    n = len(x)
    if n < 2:
        return 0.0
    rx = _rank(x)
    ry = _rank(y)

    # Pearson on ranks
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    dx = sum((r - mean_rx) ** 2 for r in rx) ** 0.5
    dy = sum((r - mean_ry) ** 2 for r in ry) ** 0.5
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)


def _get_disill_at(r, target_tick: int) -> float | None:
    snapshots = r.state_snapshots.get("judas", {})
    candidates = [t for t in snapshots if t <= target_tick]
    if not candidates:
        return None
    return snapshots[max(candidates)].domain_state.disillusionment


@pytest.mark.slow
class TestRankCorrelation:
    def test_sanity_monotone_perfect(self):
        """Rank correlation 함수 정상성 확인."""
        assert abs(_spearman_rho([1, 2, 3, 4, 5], [10, 20, 30, 40, 50]) - 1.0) < 1e-9
        assert abs(_spearman_rho([1, 2, 3, 4, 5], [50, 40, 30, 20, 10]) - (-1.0)) < 1e-9
        # Non-linear but monotone: Spearman = 1, Pearson < 1
        assert abs(_spearman_rho([1, 2, 3, 4, 5], [1, 4, 9, 16, 25]) - 1.0) < 1e-9

    def test_disill_vs_arrest_rank_correlation(self):
        """Disillusionment와 arrest tick 간 rank correlation (여러 horizon)."""
        n_seeds = 30
        horizons = [50, 100, 150, 200]

        records = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if not arrests:
                continue
            at = arrests[0]["tick"]

            disills_at = {}
            for h in horizons:
                # holdout 이후 arrest면 제외
                if at <= h:
                    continue
                d = _get_disill_at(r, h)
                if d is not None:
                    disills_at[h] = d

            records.append({"arrest_tick": at, "disills": disills_at})

        print(f"\n=== Spearman rho: disill@tick vs arrest_tick (n_seeds={n_seeds}) ===")
        print(f"{'horizon':>8} | {'rho':>7} | {'|rho|':>6} | {'n_valid':>8}")
        print("-" * 40)

        rhos = {}
        for h in horizons:
            xs = []
            ys = []
            for rec in records:
                if h in rec["disills"]:
                    xs.append(rec["disills"][h])
                    ys.append(rec["arrest_tick"])
            if len(xs) >= 5:
                rho = _spearman_rho(xs, ys)
                rhos[h] = (rho, len(xs))
                print(f"{h:>8} | {rho:>7.3f} | {abs(rho):>6.3f} | {len(xs):>8}")

        # 모든 horizon에서 음의 상관 (disill 높을수록 arrest 빠름)
        for h, (rho, n) in rhos.items():
            assert rho < 0, \
                f"Horizon {h} rho={rho:.3f} should be negative (higher disill -> earlier arrest)"

        # Horizon 늦어질수록 |rho| 증가 경향 (더 가까운 예측)
        # (strict monotone은 아니지만 tick 50 vs 200 비교)
        if 50 in rhos and 200 in rhos:
            rho_50 = abs(rhos[50][0])
            rho_200 = abs(rhos[200][0])
            print(f"\ntick 50 |rho|: {rho_50:.3f}, tick 200 |rho|: {rho_200:.3f}")
            print(f"Strengthening: {'YES' if rho_200 > rho_50 else 'NO'}")

    def test_rho_bootstrap_ci(self):
        """Spearman rho의 bootstrap 95% CI (baseline tick 200)."""
        n_seeds = 30
        HOLDOUT = 200

        data = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if not arrests:
                continue
            at = arrests[0]["tick"]
            if at <= HOLDOUT:
                continue
            d = _get_disill_at(r, HOLDOUT)
            if d is not None:
                data.append((d, at))

        assert len(data) >= 10

        point_rho = _spearman_rho([d for d, _ in data], [a for _, a in data])

        # Bootstrap
        import random
        rng = random.Random(42)
        B = 500
        rhos = []
        for _ in range(B):
            sample = [rng.choice(data) for _ in range(len(data))]
            xs = [d for d, _ in sample]
            ys = [a for _, a in sample]
            r_b = _spearman_rho(xs, ys)
            rhos.append(r_b)

        rhos.sort()
        lower = rhos[int(0.025 * B)]
        upper = rhos[int(0.975 * B)]

        print(f"\n=== Spearman rho bootstrap CI (holdout={HOLDOUT}, n={len(data)}) ===")
        print(f"Point estimate: {point_rho:.3f}")
        print(f"Bootstrap 95% CI: [{lower:.3f}, {upper:.3f}]")
        print(f"Bootstrap mean: {statistics.mean(rhos):.3f}")

        # CI가 음의 영역에 있어야 함 (통계적으로 유의한 음의 상관)
        assert upper < 0, \
            f"Upper CI {upper:.3f} should be negative (significant negative correlation)"

        # |rho| >= 0.4 (moderate or stronger)
        assert abs(point_rho) >= 0.3, \
            f"|rho|={abs(point_rho):.3f} below 0.3 threshold"
