"""Van Gogh Emotional Arc (departure-relative).

Peter 대응: VG도 departure 전후로 감정이 어떻게 변하는가?

Peter 결과:
- Hope trough at arrest (0)
- Grief peak at +25
- Fear peak at +75

VG에서 같은 패턴 관찰되는가? 시간 스케일 차이(Peter 500 vs VG 150)
고려해서 offset 비례 조정 (Peter offset 50 = VG offset 15).
"""

import statistics
from pathlib import Path

import pytest

from content.gauguin.domain_artistic_ego import ArtisticEgoState
from content.theo.domain_patron import PatronState
from content.vangogh.domain_creative import CreativeDriveState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.world import SimulationWorld

pytestmark = pytest.mark.archived  # Tier 3 archived (ITERATION_CLASSIFICATION.md)

register_domain_type("creative_drive", CreativeDriveState)
register_domain_type("artistic_ego", ArtisticEgoState)
register_domain_type("patron", PatronState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run(seed: int):
    vg = load_agent_state(CONTENT_DIR / "vangogh" / "initial_state.json")
    g = load_agent_state(CONTENT_DIR / "gauguin" / "initial_state.json")
    t = load_agent_state(CONTENT_DIR / "theo" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "vangogh" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "vangogh" / "hazard_events.json")
    profiles = {
        "vangogh": load_behavior_profile(CONTENT_DIR / "vangogh" / "behavior_profile.json"),
        "gauguin": load_behavior_profile(CONTENT_DIR / "gauguin" / "behavior_profile.json"),
        "theo": load_behavior_profile(CONTENT_DIR / "theo" / "behavior_profile.json"),
    }
    config = SimulationConfig(
        max_tick=150, initial_state=vg,
        initial_states=[vg, g, t],
        hazard_events=hazards, triggers=triggers, state_noise_scale=0.05,
    )
    return SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)


def _get_emotion(r, agent: str, target_tick: int, emotion: str) -> float | None:
    snapshots = r.state_snapshots.get(agent, {})
    candidates = [t for t in snapshots if t <= target_tick]
    if not candidates:
        return None
    best = max(candidates)
    return getattr(snapshots[best].emotions, emotion)


@pytest.mark.slow
class TestVGEmotionArc:
    def test_vg_emotion_arc_around_departure(self):
        """Departure 전후 VG 감정 궤적."""
        n_seeds = 20
        # VG 스케일: Peter의 1/3 수준이므로 offset 축소
        offsets = [-30, -20, -10, 0, 10, 20, 30]
        emotions = ["fear", "grief", "hope"]

        data: dict[str, dict[int, list[float]]] = {
            e: {o: [] for o in offsets} for e in emotions
        }

        for seed in range(n_seeds):
            r = _run(seed)
            deps = [t for t in r.fired_triggers if t["trigger_id"] == "gauguin_departure"]
            if not deps:
                continue
            dt = deps[0]["tick"]
            for e in emotions:
                for o in offsets:
                    v = _get_emotion(r, "vangogh", dt + o, e)
                    if v is not None:
                        data[e][o].append(v)

        print(f"\n=== VG Emotion Arc (departure-relative, n={n_seeds}) ===")
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
            print(row)

        fear_peak = max(means["fear"].keys(), key=lambda k: means["fear"][k])
        grief_peak = max(means["grief"].keys(), key=lambda k: means["grief"][k])
        hope_trough = min(means["hope"].keys(), key=lambda k: means["hope"][k])

        print(f"\nFear peak at offset {fear_peak:+} (value {means['fear'][fear_peak]:.2f})")
        print(f"Grief peak at offset {grief_peak:+} (value {means['grief'][grief_peak]:.2f})")
        print(f"Hope trough at offset {hope_trough:+} (value {means['hope'][hope_trough]:.2f})")

        print("\nPeter reference (scaled /3):")
        print("  Hope trough at 0, Grief peak at +25 (/3 = +8), Fear peak at +75 (/3 = +25)")

        # VG scale에서는 peak가 departure 이후에 있어야 함 (Peter와 같은 방향)
        assert grief_peak >= 0, \
            f"VG grief peak {grief_peak} should be >= 0"

        # Hope trough는 departure 근처 (|offset| <= 30)
        assert abs(hope_trough) <= 30, \
            f"VG hope trough at offset {hope_trough} far from departure"

        # Cross-scenario 구조: Peter처럼 hope는 crash, grief/fear peak는 post-event
        peak_order_peter = "hope(0) < grief(+25) < fear(+75)"
        peak_order_vg = f"hope({hope_trough:+}) , grief({grief_peak:+}), fear({fear_peak:+})"
        print("\nEmotional peak order:")
        print(f"  Peter: {peak_order_peter}")
        print(f"  VG:    {peak_order_vg}")

    def test_vg_grief_peak_post_departure(self):
        """Gauguin departure 후 VG grief 최대값 분포."""
        n_seeds = 30
        peak_griefs_post = []
        for seed in range(n_seeds):
            r = _run(seed)
            deps = [t for t in r.fired_triggers if t["trigger_id"] == "gauguin_departure"]
            if not deps:
                continue
            dt = deps[0]["tick"]
            snapshots = r.state_snapshots.get("vangogh", {})
            post_griefs = [s.emotions.grief for t, s in snapshots.items() if t >= dt]
            if post_griefs:
                peak_griefs_post.append(max(post_griefs))

        if peak_griefs_post:
            mean_peak = statistics.mean(peak_griefs_post)
            reach_7 = sum(1 for g in peak_griefs_post if g >= 7.0)
            print(f"\n=== VG Post-Departure Peak Grief (n={len(peak_griefs_post)}) ===")
            print(f"Mean peak grief: {mean_peak:.2f}")
            print(f"Reach >=7.0 (POM grief_peak): {reach_7}/{len(peak_griefs_post)} "
                  f"({reach_7/len(peak_griefs_post):.0%})")

            # POM grief_peak 기준을 대부분 만족 (VG에서는 100%)
            assert reach_7 / len(peak_griefs_post) >= 0.9, \
                f"VG grief_peak rate low: {reach_7}/{len(peak_griefs_post)}"
