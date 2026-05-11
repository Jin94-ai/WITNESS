"""Minimal Story Selector — J-Alpha Step A4.

Per `docs/CREATIVE_TRACK_TRANSITION.md` §7 + `WITNESS_CREATIVE_IP_TRACK_IMPROVED_DIRECTIVE.md` §4.4 A4:

J-Alpha selector는 검색기가 아니라 **anchor variation bundler** 수준으로 제한.
2가지 기능만:
1. 같은 anchor의 5개 seed를 묶어서 가져오기
2. 현재 curated set에서 "가장 읽을 가치 있는" anchor 고르기

Full query API (`get_top_arcs`, `get_ip_candidates` 등)는 J-Beta로 연기.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from engine.world.micro_world.world import MicroWorld


@dataclass
class AnchorBundle:
    """같은 anchor의 5 seed variation 묶음."""

    anchor_id: str
    scenario: str  # "scarcity", "accusation", "sacred"
    seed_count: int  # 보통 5
    builder: Callable  # MicroWorld factory: builder(seed: int) -> MicroWorld
    description: str = ""
    expected_outcome_diversity: int = 0  # 1-5 (예측 distinct outcome 수)
    notes: list[str] = field(default_factory=list)


def get_variations(bundle: AnchorBundle, max_seeds: int = 5) -> list[tuple[int, "MicroWorld"]]:
    """Return list of (seed, MicroWorld) pairs for the anchor.

    J-Alpha: 단순 seeds 0..max_seeds-1 enumerate. J-Beta에서 더 정교한
    seed 선택 (most-diverse, most-extreme 등) 추가 가능.
    """
    return [(seed, bundle.builder(seed)) for seed in range(max_seeds)]


# ============================================================
# J-Alpha Curated Anchor Bundles
# ============================================================
# Per docs/creative/CURATED_ANCHOR_SET_ALPHA.md §2-§3.

def _make_peter_scarcity_anchor() -> AnchorBundle:
    """Peter passion week — scarcity slice. baseline cast/placement, 1 accusation."""
    from scripts.b_direction.generate_scarcity_depth_variations import build_scarcity_depth_world

    def builder(seed: int):
        return build_scarcity_depth_world(seed=seed, event_count="single", crowd_density="baseline")

    return AnchorBundle(
        anchor_id="peter_scarcity_baseline",
        scenario="scarcity",
        seed_count=5,
        builder=builder,
        description="Peter scarcity baseline — single accusation against merchant, baseline crowd density",
        expected_outcome_diversity=3,  # cross-seed: SAT/REC/PARTIAL mix
        notes=[
            "Branch C cross-seed test 데이터 기반 expected diversity",
            "fisher_laborer top blame target deterministic",
            "Korean opening: 곡식이 비어 가는 계절...",
        ],
    )


def _make_vangogh_sacred_anchor() -> AnchorBundle:
    """Van Gogh→sacred substitute — med density miracles, baseline placement."""
    from scripts.b_direction.generate_event_density_variations import build_sacred_density_world

    def builder(seed: int):
        return build_sacred_density_world(seed=seed, miracle_ticks=[10, 100, 190])

    return AnchorBundle(
        anchor_id="vangogh_sacred_baseline",
        scenario="sacred",
        seed_count=5,
        builder=builder,
        description="Van Gogh→sacred substitute — 3 miracles even-spaced, baseline cast",
        expected_outcome_diversity=2,  # sacred는 cross-seed 안정적 (Branch C 측정)
        notes=[
            "Van Gogh 별도 simulator는 J-Beta에서 직접 적용",
            "sacred 시나리오가 spiritual collapse 톤에 가장 가까운 substitute",
            "Korean opening: 성전 바깥뜰에 사람들이 모여 있었다...",
        ],
    )


def _make_peter_scarcity_high_density_anchor() -> AnchorBundle:
    """J-Alpha follow-up — Van Gogh→sacred FAIL 대체 후보.

    test_anchor_diversity.py 측정: 5 seeds → 3 distinct outcomes
    (SAT 2 / REC 2 / PARTIAL 1) — Peter scarcity baseline과 동일 분포 패턴.
    """
    from scripts.b_direction.generate_scarcity_depth_variations import build_scarcity_depth_world

    def builder(seed: int):
        return build_scarcity_depth_world(seed=seed, event_count="single", crowd_density="high")

    return AnchorBundle(
        anchor_id="peter_scarcity_high_density",
        scenario="scarcity",
        seed_count=5,
        builder=builder,
        description="Peter scarcity high-density crowd — single accusation + high marketplace/poor_quarter density",
        expected_outcome_diversity=3,  # measured: 3 distinct
        notes=[
            "test_anchor_diversity.py 측정 기반 (자율 발견)",
            "Van Gogh→sacred 5/5 PARTIAL FAIL 대체 후보",
            "scarcity baseline anchor와 cross-anchor 비교 가능 (같은 시나리오, 다른 density)",
        ],
    )


def _make_scarcity_double_anchor() -> AnchorBundle:
    """J-Beta — scarcity 2 accusations cell (Branch C S2 측정에 기반).

    Cross-seed: SAT 3 / REC 2 (2 distinct, mostly saturating). nonmonotonic
    역설 — 더 많은 accusation이 더 깊은 saturation을 만들지 않음.
    """
    from scripts.b_direction.generate_scarcity_depth_variations import build_scarcity_depth_world

    def builder(seed: int):
        return build_scarcity_depth_world(seed=seed, event_count="double", crowd_density="baseline")

    return AnchorBundle(
        anchor_id="peter_scarcity_double",
        scenario="scarcity",
        seed_count=5,
        builder=builder,
        description="Peter scarcity 2 accusations — escalation cell, mostly saturating",
        expected_outcome_diversity=2,
        notes=[
            "Branch C S2 cross-seed 측정: SAT 3 / REC 2",
            "scarcity 1→2 accusations escalation 비교용",
        ],
    )


def _make_scarcity_triple_anchor() -> AnchorBundle:
    """J-Beta — scarcity 3 accusations cell. Nonmonotonic finding.

    Cross-seed: REC 3 / SAT 2 — 더 많은 accusation이 *오히려* recovery
    유도 (Branch C S2 LOOP 69 발견의 reproduce).
    """
    from scripts.b_direction.generate_scarcity_depth_variations import build_scarcity_depth_world

    def builder(seed: int):
        return build_scarcity_depth_world(seed=seed, event_count="triple", crowd_density="baseline")

    return AnchorBundle(
        anchor_id="peter_scarcity_triple",
        scenario="scarcity",
        seed_count=5,
        builder=builder,
        description="Peter scarcity 3 accusations — nonmonotonic recovery cell",
        expected_outcome_diversity=2,
        notes=[
            "Branch C S2 LOOP 69 nonmonotonic finding cell",
            "더 많은 accusation → 더 많은 recovery (counterintuitive)",
            "scarcity_baseline (1 acc) + scarcity_double (2 acc) + this (3 acc) = trilogy",
        ],
    )


def get_curated_anchors() -> list[AnchorBundle]:
    """Curated anchor set. J-Alpha + J-Beta expanded (2026-04-28).

    J-Alpha (3):
    - peter_scarcity_baseline (PASS 5/6, 3 distinct)
    - vangogh_sacred_baseline (FAIL 1/6, transparency 보존)
    - peter_scarcity_high_density (READY, 3 distinct, 자율 follow-up)

    J-Beta (2 added):
    - peter_scarcity_double (2 distinct, escalation 비교용)
    - peter_scarcity_triple (2 distinct, nonmonotonic finding)

    → scarcity *trilogy* (1/2/3 accusations) + density variant + sacred substitute.
    """
    return [
        _make_peter_scarcity_anchor(),
        _make_vangogh_sacred_anchor(),
        _make_peter_scarcity_high_density_anchor(),
        _make_scarcity_double_anchor(),
        _make_scarcity_triple_anchor(),
    ]


# ============================================================
# J-Beta Query API extension
# ============================================================

def get_anchor_by_id(anchor_id: str, anchors: Optional[list[AnchorBundle]] = None) -> Optional[AnchorBundle]:
    """Find anchor by exact id. None if not found."""
    if anchors is None:
        anchors = get_curated_anchors()
    for a in anchors:
        if a.anchor_id == anchor_id:
            return a
    return None


def get_variations_by_anchor_id(anchor_id: str, max_seeds: int = 5) -> list[tuple[int, "MicroWorld"]]:
    """Convenience: anchor_id로 직접 5 variations 가져오기."""
    anchor = get_anchor_by_id(anchor_id)
    if anchor is None:
        raise ValueError(f"Unknown anchor_id: {anchor_id}")
    return get_variations(anchor, max_seeds=max_seeds)


def query_anchors(
    scenario: Optional[str] = None,
    min_diversity: Optional[int] = None,
    anchors: Optional[list[AnchorBundle]] = None,
) -> list[AnchorBundle]:
    """J-Beta — filter anchors by scenario / diversity threshold.

    Examples:
        query_anchors(scenario="scarcity")  # all scarcity anchors
        query_anchors(min_diversity=3)       # READY anchors only
        query_anchors(scenario="scarcity", min_diversity=2)  # MARGINAL+ scarcity
    """
    if anchors is None:
        anchors = get_curated_anchors()
    out = anchors
    if scenario is not None:
        out = [a for a in out if a.scenario == scenario]
    if min_diversity is not None:
        out = [a for a in out if a.expected_outcome_diversity >= min_diversity]
    return out


def get_top_arcs(arc_type: str, anchors: Optional[list[AnchorBundle]] = None) -> list[AnchorBundle]:
    """J-Beta — anchors that PRIMARILY produce the given arc type.

    arc_type ∈ {"recovery", "saturation", "mixed", "partial", "low_activity"}
    Returns anchors whose scenario semantic suggests this arc dominance.
    Note: J-Beta minimal — actual arc measurement은 trajectory labeling 후.
    """
    if anchors is None:
        anchors = get_curated_anchors()
    arc_to_scenario_hint = {
        "recovery": "sacred",  # sacred 시나리오가 recovery 경향
        "saturation": "scarcity",  # scarcity 일부 cell이 saturation 경향
        "mixed": None,  # MIXED는 cell-specific
        "partial": "sacred",  # sacred는 PARTIAL도 자주
        "low_activity": "sacred",  # LOW_ACTIVITY는 sacred clustered에서만
    }
    hint = arc_to_scenario_hint.get(arc_type)
    if hint is None:
        return []
    return [a for a in anchors if a.scenario == hint]


def pick_most_readable_anchor(anchors: Optional[list[AnchorBundle]] = None) -> AnchorBundle:
    """현재 curated set에서 가장 '읽을 가치 있는' anchor.

    J-Alpha: outcome diversity가 높은 anchor 선택 (variation 풍부함).
    Tie-break: 이름 알파벳순.
    """
    if anchors is None:
        anchors = get_curated_anchors()
    return max(
        anchors,
        key=lambda a: (a.expected_outcome_diversity, -ord(a.anchor_id[0])),
    )
