"""Peter Emotional Trajectory (fear/grief/hope).

Arrest-relative normalization으로 평균 궤적 계산.
phase: pre_arrest_early (-100~-50), pre_arrest_late (-50~0), post_arrest (0~100).

검증:
- fear peak는 언제? (arrest 직전/직후)
- grief peak는? (denial 후)
- hope trough 위치? (가장 낮은 시점)

의의: "Peter의 감정 궤적이 성서 내러티브와 일치하는가?"
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


def _get_emotion_at_offset(r, arrest_tick: int, offset: int, emotion: str) -> float | None:
    target = arrest_tick + offset
    snapshots = r.state_snapshots.get("peter", {})
    candidates = [t for t in snapshots if t <= target]
    if not candidates:
        return None
    best = max(candidates)
    emo = snapshots[best].emotions
    return getattr(emo, emotion)


@pytest.mark.slow
class TestPeterEmotionArc:
    def test_emotion_trajectory_around_arrest(self):
        """Arrest-relative 궤적 평균 (offset -100, -50, 0, +50, +100)."""
        n_seeds = 20
        offsets = [-100, -75, -50, -25, 0, 25, 50, 75, 100]
        emotions = ["fear", "grief", "hope"]

        data: dict[str, dict[int, list[float]]] = {
            e: {o: [] for o in offsets} for e in emotions
        }

        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if not arrests:
                continue
            at = arrests[0]["tick"]
            for e in emotions:
                for o in offsets:
                    v = _get_emotion_at_offset(r, at, o, e)
                    if v is not None:
                        data[e][o].append(v)

        print(f"\n=== Peter Emotion Arc (arrest-relative, n={n_seeds}) ===")
        header = f"{'offset':>8}" + "".join(f" | {e:>8}" for e in emotions)
        print(header)
        print("-" * len(header))
        means: dict[str, dict[int, float]] = {e: {} for e in emotions}
        for o in offsets:
            row = f"{o:>+8}"
            for e in emotions:
                vals = data[e][o]
                if vals:
                    m = statistics.mean(vals)
                    means[e][o] = m
                    row += f" | {m:>8.2f}"
                else:
                    row += " | " + " " * 8
            print(row)

        # Fear peak location
        fear_peak_o = max(means["fear"].keys(), key=lambda k: means["fear"][k])
        print(f"\nFear peak at offset {fear_peak_o:+} (value {means['fear'][fear_peak_o]:.2f})")
        # Grief peak
        grief_peak_o = max(means["grief"].keys(), key=lambda k: means["grief"][k])
        print(f"Grief peak at offset {grief_peak_o:+} (value {means['grief'][grief_peak_o]:.2f})")
        # Hope trough
        hope_trough_o = min(means["hope"].keys(), key=lambda k: means["hope"][k])
        print(f"Hope trough at offset {hope_trough_o:+} (value {means['hope'][hope_trough_o]:.2f})")

        # 검증 1: fear peak는 arrest 이후 영역에 있어야 함 (체포 후 두려움 누적)
        # 실측: +75 (75 ticks after arrest) — 지속 공포 단계
        assert fear_peak_o >= 0, \
            f"Fear peak at offset {fear_peak_o} should be post-arrest (>=0)"

        # 검증 2: grief peak는 arrest 이후에 있어야 함 (denial 후 통곡)
        # 실측: +25 (denial 직후)
        assert grief_peak_o >= 0, \
            f"Grief peak at offset {grief_peak_o} should be >= 0 (post-arrest)"

        # 검증 3: hope trough 위치 (arrest 전후 근처)
        assert abs(hope_trough_o) <= 50, \
            f"Hope trough at offset {hope_trough_o} far from arrest"

        # 검증 4: 감정 peak 순서 (grief가 fear보다 먼저 peak)
        # 실측: grief +25 vs fear +75
        # denial 직후 즉각적 grief, 이후 지속적 fear accumulation
        assert grief_peak_o <= fear_peak_o, \
            f"Grief peak ({grief_peak_o}) should be before/same as fear peak ({fear_peak_o})"

        # 검증 5: post-arrest fear가 pre-arrest early fear보다 높음
        fear_pre = means["fear"].get(-100, 5.0)
        fear_post = means["fear"].get(50, 5.0)
        print(f"\nFear pre (-100) = {fear_pre:.2f}, post (+50) = {fear_post:.2f}")
        assert fear_post >= fear_pre - 0.5, \
            f"Post-arrest fear {fear_post:.2f} much lower than pre {fear_pre:.2f}"

    def test_grief_exceeds_trauma_threshold(self):
        """POM grief_peak >= 8.0 기준 충족 runs 비율."""
        n_seeds = 30
        reach_8 = 0
        peak_grief = []

        for seed in range(n_seeds):
            r = _run(seed)
            snapshots = r.state_snapshots.get("peter", {})
            max_grief = max(
                (s.emotions.grief for s in snapshots.values()),
                default=0,
            )
            peak_grief.append(max_grief)
            if max_grief >= 8.0:
                reach_8 += 1

        mean_peak = statistics.mean(peak_grief)
        median_peak = statistics.median(peak_grief)
        print(f"\n=== Peter Peak Grief Distribution (n={n_seeds}) ===")
        print(f"Mean peak grief: {mean_peak:.2f}")
        print(f"Median peak grief: {median_peak:.2f}")
        print(f"Reach >=8.0 (POM grief_peak): {reach_8}/{n_seeds} ({reach_8/n_seeds:.0%})")

        # POM에서 grief_peak가 100% pass하는 것과 일관
        assert reach_8 / n_seeds >= 0.9, \
            f"grief_peak 8.0 rate {reach_8}/{n_seeds} below 90% (POM expects near 100%)"

    def test_hope_recovery_post_intervention(self):
        """Canonical intervention 후 hope가 회복되는가."""
        n_seeds = 20
        # canonical intervention (요한 21장)은 시뮬 후반에 발생
        # 최종 hope가 중간 trough보다 높아야 함

        min_hopes = []
        final_hopes = []
        for seed in range(n_seeds):
            r = _run(seed)
            snapshots = r.state_snapshots.get("peter", {})
            if not snapshots:
                continue
            hopes = [s.emotions.hope for s in snapshots.values()]
            min_hopes.append(min(hopes))
            final_hopes.append(r.final_states["peter"].emotions.hope)

        mean_min = statistics.mean(min_hopes)
        mean_final = statistics.mean(final_hopes)
        recovery = mean_final - mean_min
        print(f"\n=== Peter Hope Recovery (n={n_seeds}) ===")
        print(f"Mean min hope: {mean_min:.2f}")
        print(f"Mean final hope: {mean_final:.2f}")
        print(f"Recovery: +{recovery:.2f}")

        # 회복 존재: final > min
        assert recovery > 1.0, f"Hope recovery only +{recovery:.2f}"
        # POM eventual_hope >= 3.0 기준 충족
        reach_3 = sum(1 for h in final_hopes if h >= 3.0)
        print(f"Final hope >= 3.0 (POM eventual_hope): {reach_3}/{n_seeds}")
        assert reach_3 / len(final_hopes) >= 0.8, \
            f"Only {reach_3}/{len(final_hopes)} reach hope 3"
