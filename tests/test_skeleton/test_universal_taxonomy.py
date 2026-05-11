"""Tests for Phase 0 universal taxonomy + SkeletonOutput contract.

Per `docs/witness_narrative_mode_plan.md` §3.3:
    SkeletonOutput contract가 동결된 후에야 살 엔진 작업을 시작한다.
    → 이 테스트가 contract의 freeze guard 역할을 한다.

Verifies:
    1. Universal taxonomy JSON 3개 schema valid
    2. UniversalStorySeed dataclass roundtrip
    3. SkeletonOutput contract 필드 존재 (기존 시드 변경 시 fail)
    4. AnchorRegistry separation (engine.observer는 anchor 정보 X)
    5. Adapter: 기존 (StoryCandidate, StorySeedCard) → UniversalStorySeed
       에서 anchor-specific 정보 (raw 인물명) 제거 확인
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


# ============================================================================
# 1. Universal taxonomy JSON
# ============================================================================

def test_pressure_taxonomy_loads_and_has_required_pressures():
    from engine.observer.universal_story_seed import load_pressure_taxonomy
    pressures = load_pressure_taxonomy()
    # 핵심 압력은 모두 존재해야
    for required in ("fear", "shame_self", "hope", "authority_vigilance",
                      "public_suspicion", "blame_concentration"):
        assert required in pressures, f"missing pressure: {required}"
    # 각 항목에 plain_label_ko + polarity 존재
    for pid, entry in pressures.items():
        assert "plain_label_ko" in entry
        assert "polarity" in entry
        assert entry["polarity"] in ("aversive", "appetitive", "neutral")


def test_desire_taxonomy_loads_and_has_required_desires():
    from engine.observer.universal_story_seed import load_desire_taxonomy
    desires = load_desire_taxonomy()
    for required in ("loyalty", "survival", "control", "exposure_avoidance",
                      "identity_preservation", "commitment", "trust",
                      "group_safety"):
        assert required in desires, f"missing desire: {required}"
    for did, entry in desires.items():
        assert "plain_label_ko" in entry
        assert "category" in entry


def test_conflict_axes_loads_and_covers_existing_conflicts():
    from engine.observer.universal_story_seed import load_conflict_axes
    axes = load_conflict_axes()
    # 기존 episode_outline conflict ID와 동일한 axis가 있어야
    for required in ("loyalty_vs_survival", "uncertainty_vs_commitment",
                      "control_vs_exposure", "collective_fear_vs_scapegoating",
                      "identity_vs_failure", "atmosphere_vs_action",
                      "trust_vs_self_protection", "unknown"):
        assert required in axes, f"missing conflict axis: {required}"
    for aid, entry in axes.items():
        assert "plain_label_ko" in entry


# ============================================================================
# 2. UniversalStorySeed dataclass
# ============================================================================

def test_universal_story_seed_roundtrip():
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01",
        conflict_axis_id="loyalty_vs_survival",
        main_role="main_loyal_under_pressure",
        main_archetype="loyal_under_pressure",
        dominant_pressures=("fear", "authority_vigilance"),
        dominant_desires=("loyalty", "survival"),
        supporting_roles=("supporting_uncertain", "supporting_watcher"),
        confidence_label="strong_viable",
        audit_status="pass",
        evidence_count=21,
    )
    d = seed.to_dict()
    s = json.dumps(d, ensure_ascii=False)
    parsed = json.loads(s)
    restored = UniversalStorySeed.from_dict(parsed)
    assert restored == seed


def test_universal_seed_is_anchor_clean():
    """UniversalStorySeed module source must NOT contain anchor-specific names."""
    src = (ROOT / "engine/observer/universal_story_seed.py").read_text(encoding="utf-8")
    forbidden = ("Peter", "베드로", "Andrew", "안드레", "James", "야고보",
                  "John", "요한", "Vangogh", "Gauguin", "Talleyrand",
                  "judas", "caiaphas")
    for tok in forbidden:
        assert tok not in src, f"anchor-specific token in universal seed module: {tok!r}"


# ============================================================================
# 3. SkeletonOutput contract
# ============================================================================

def test_skeleton_output_has_required_fields():
    """**FROZEN CONTRACT**. 변경 시 RFC 필수."""
    from engine.observer.skeleton_output import (
        SkeletonOutput, EvidenceLedger, AuditTrail,
    )
    out = SkeletonOutput()
    # required field presence
    assert hasattr(out, "schema_version")
    assert hasattr(out, "seeds")
    assert hasattr(out, "flow")
    assert hasattr(out, "evidence_ledger")
    assert hasattr(out, "anchor_metadata")
    assert hasattr(out, "audit_trail")
    # versioned schema
    assert out.schema_version.startswith("skeleton_output_v")
    # to_dict roundtrip
    d = out.to_dict()
    assert "schema_version" in d
    assert "seeds" in d
    assert "evidence_ledger" in d


def test_evidence_ledger_audit_count_fields():
    from engine.observer.skeleton_output import EvidenceLedger
    el = EvidenceLedger(
        total_signals=21,
        signals_per_seed={"S01": 8, "S02": 9, "S03": 4},
        audit_pass_count=4,
        audit_fail_count=0,
    )
    d = el.to_dict()
    assert d["total_signals"] == 21
    assert d["audit_pass_count"] == 4


# ============================================================================
# 4. AnchorRegistry separation
# ============================================================================

def test_anchor_registry_lists_peter_anchor():
    from engine.anchor import AnchorRegistry
    reg = AnchorRegistry()
    anchors = reg.list_anchors()
    assert "peter_scarcity_baseline" in anchors


def test_peter_binding_maps_english_to_korean_names():
    from engine.anchor import AnchorRegistry
    reg = AnchorRegistry()
    binding = reg.get("peter_scarcity_baseline")
    assert binding is not None
    assert binding.display_name_for_raw("Peter") == "베드로"
    assert binding.display_name_for_raw("Andrew") == "안드레"
    assert binding.display_name_for_raw("Unknown") == "Unknown"  # passthrough


def test_engine_observer_module_has_no_anchor_specific_dicts():
    """engine/observer 안에 PETER_ANCHOR / 베드로 매핑이 없어야.
    이런 매핑은 content/anchors / engine/anchor 로 분리되어야 한다."""
    obs_dir = ROOT / "engine" / "observer"
    for py_file in obs_dir.glob("*.py"):
        src = py_file.read_text(encoding="utf-8")
        # 단, episode_outline.py는 *display_name_overrides 인자*만 받는 형태
        # 이미 (Iter 24 후) — 안에 직접 dict가 없는지 확인.
        for forbidden in ("PETER_ANCHOR_NAME_OVERRIDES_KO",
                          'display_name_overrides = {"Peter":'):
            assert forbidden not in src, (
                f"engine/observer/{py_file.name} contains anchor-specific dict "
                f"({forbidden!r}). Move to content/anchors or engine/anchor."
            )


# ============================================================================
# 5. Adapter: existing seeds → UniversalStorySeed
# ============================================================================

def _build_existing_inputs():
    """Run the existing pipeline once to get StoryCandidate + StorySeedCard list."""
    from engine.observer.identity_resolver import IdentityResolver
    from engine.observer.moment_extractor import extract_moments
    from engine.observer.scene_brief import build_scene_brief
    from engine.observer.story_candidate_builder import build_story_candidates
    from engine.observer.story_seed_card import build_seed_card
    from engine.observer.story_viability import score_candidate
    from engine.observer.thread_builder import build_story_threads, link_moments
    from engine.observer.treatment import build_treatment

    p = ROOT / "data/visual/dot_observer_data_seed0.json"
    if not p.exists():
        pytest.skip("observer dump for seed 0 missing")
    obs = json.loads(p.read_text(encoding="utf-8"))
    moments = extract_moments(obs)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    identity = IdentityResolver.from_observer(obs)
    cands = build_story_candidates(threads, moments, identity)
    cards = []
    for c in cands:
        b = build_scene_brief(c)
        t = build_treatment(c, b)
        sc = score_candidate(c, b, t)
        cards.append(build_seed_card(c, b, sc))
    return cands, cards


def test_adapter_produces_universal_seed_with_no_raw_names():
    cands, cards = _build_existing_inputs()
    from engine.observer.universal_seed_adapter import (
        candidate_to_universal_seed, DEFAULT_ARCHETYPE_BY_SEED,
    )
    archetype = DEFAULT_ARCHETYPE_BY_SEED.get(cards[0].seed_id, "loyal_under_pressure")
    seed = candidate_to_universal_seed(cands[0], cards[0], archetype=archetype)
    # universal seed에 영어 raw 이름 / 한국어 인명 0
    s = json.dumps(seed.to_dict(), ensure_ascii=False)
    forbidden = ("Peter", "Andrew", "James", "John", "베드로", "안드레",
                 "야고보", "요한")
    for tok in forbidden:
        assert tok not in s, (
            f"universal seed leaked anchor-specific name: {tok!r}\nSeed: {s}"
        )
    # conflict axis는 보존
    assert seed.conflict_axis_id in (
        "loyalty_vs_survival", "uncertainty_vs_commitment",
        "control_vs_exposure", "unknown",
    )


def test_skeleton_output_assembles_from_existing_pipeline():
    cands, cards = _build_existing_inputs()
    from engine.observer.universal_seed_adapter import assemble_skeleton_output
    out = assemble_skeleton_output(
        cands, cards,
        anchor_id="peter_scarcity_baseline",
    )
    assert out.schema_version.startswith("skeleton_output_v")
    assert len(out.seeds) == len(cards)
    assert out.anchor_metadata is not None
    assert out.anchor_metadata.anchor_id == "peter_scarcity_baseline"
    # universal seeds 자체는 anchor-clean
    for seed in out.seeds:
        s = json.dumps(seed.to_dict(), ensure_ascii=False)
        assert "Peter" not in s and "베드로" not in s


# ============================================================================
# 6. Phase 1 infrastructure — selection criteria + data card template
# ============================================================================

def test_selection_criteria_doc_exists_and_covers_required_sections():
    p = ROOT / "docs" / "data" / "SELECTION_CRITERIA.md"
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    for required in (
        "막장 작품",
        "비교군",
        "ToS",
        "robots.txt",
        "선정 결과 기록 형식",
    ):
        assert required in text, f"SELECTION_CRITERIA.md missing section: {required}"


def test_data_card_template_exists():
    p = ROOT / "docs" / "data" / "DATA_CARD_TEMPLATE.md"
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    for required in ("출처", "라이선스", "어노테이션", "분할", "편향"):
        assert required in text


def test_raw_data_dirs_have_selection_log_skeletons():
    for cat in ("melodrama", "control"):
        p = ROOT / "data" / "raw" / cat / "_selection_log.json"
        assert p.exists()
        d = json.loads(p.read_text(encoding="utf-8"))
        assert d["_meta"]["category"] == cat
        assert isinstance(d["candidates"], list)


# ============================================================================
# 7. Phase 2.5: Taxonomy consistency fixes (Plan §B)
# ============================================================================

def test_desire_taxonomy_split_collisions_into_desires_and_pressures():
    """Phase 2.5 §B.1: natural_collisions → colliding_desires + colliding_pressures."""
    from engine.observer.universal_story_seed import (
        load_desire_taxonomy, load_pressure_taxonomy,
    )
    desires = load_desire_taxonomy()
    pressures = load_pressure_taxonomy()

    for did, entry in desires.items():
        assert "colliding_desires" in entry, (
            f"desire {did} missing colliding_desires (Phase 2.5)"
        )
        assert "colliding_pressures" in entry, (
            f"desire {did} missing colliding_pressures (Phase 2.5)"
        )
        # 모든 colliding_desires id는 desire_taxonomy에 존재
        for d_id in entry["colliding_desires"]:
            assert d_id in desires, (
                f"desire {did}.colliding_desires references unknown desire: {d_id}"
            )
        # 모든 colliding_pressures id는 pressure_taxonomy에 존재
        for p_id in entry["colliding_pressures"]:
            assert p_id in pressures, (
                f"desire {did}.colliding_pressures references unknown pressure: {p_id}"
            )


def test_unknown_axis_is_fallback_only():
    """Phase 2.5 §B.2: unknown axis must be fallback_only."""
    from engine.observer.universal_story_seed import load_conflict_axes
    axes = load_conflict_axes()
    unknown = axes.get("unknown")
    assert unknown is not None
    assert unknown.get("status") == "fallback_only", (
        "unknown axis must declare status=fallback_only (Plan §B.2)"
    )
    assert unknown.get("valid_for_training") is False, (
        "unknown axis must declare valid_for_training=false (Plan §B.2)"
    )


def test_normal_axes_have_status_normal():
    """Phase 2.5 §B.2: 모든 정상 axis는 status=normal + valid_for_training=true."""
    from engine.observer.universal_story_seed import load_conflict_axes
    axes = load_conflict_axes()
    for aid, entry in axes.items():
        if aid == "unknown":
            continue
        assert entry.get("status") == "normal", (
            f"axis {aid} missing status=normal (Phase 2.5)"
        )
        assert entry.get("valid_for_training") is True, (
            f"axis {aid} missing valid_for_training=true (Phase 2.5)"
        )


def test_crowd_mood_marked_as_environmental_state():
    """Phase 2.5 §B.3: crowd_mood is environmental_pressure_state, not aversive."""
    from engine.observer.universal_story_seed import load_pressure_taxonomy
    pressures = load_pressure_taxonomy()
    crowd_mood = pressures.get("crowd_mood")
    assert crowd_mood is not None
    assert crowd_mood.get("kind") == "environmental_pressure_state", (
        "crowd_mood must declare kind=environmental_pressure_state (Plan §B.3)"
    )
    assert crowd_mood.get("deprecated_as_pressure") is True, (
        "crowd_mood must mark deprecated_as_pressure=true (Plan §B.3)"
    )


def test_crowd_tension_added_as_aversive_pressure():
    """Phase 2.5 §B.3: crowd_tension is the new aversive collective pressure."""
    from engine.observer.universal_story_seed import load_pressure_taxonomy
    pressures = load_pressure_taxonomy()
    crowd_tension = pressures.get("crowd_tension")
    assert crowd_tension is not None, (
        "crowd_tension must be added as new pressure (Plan §B.3)"
    )
    assert crowd_tension.get("polarity") == "aversive"
    assert crowd_tension.get("kind") == "pressure"


# ============================================================================
# 8. Phase 2.5 §C — UniversalStorySeed v1.1 contract (RFC-0001)
# ============================================================================

def test_universal_seed_v1_1_has_change_pattern_field():
    """RFC-0001: change_pattern은 top-level field로 승격됨."""
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="loyal_under_pressure",
        change_pattern="stay_present_then_withdraw",
    )
    assert seed.change_pattern == "stay_present_then_withdraw"
    d = seed.to_dict()
    assert d["change_pattern"] == "stay_present_then_withdraw"


def test_universal_seed_v1_1_has_flow_role_field():
    """RFC-0001: flow_role은 top-level field."""
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="loyal_under_pressure",
        flow_role="main_arc",
    )
    assert seed.flow_role == "main_arc"
    d = seed.to_dict()
    assert d["flow_role"] == "main_arc"


def test_universal_seed_v1_1_has_turning_points_count():
    """RFC-0001: turning_points_count는 pressure_pattern dict 안이 아닌 top-level."""
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="loyal_under_pressure",
        turning_points_count=3,
    )
    assert seed.turning_points_count == 3
    d = seed.to_dict()
    assert d["turning_points_count"] == 3


def test_universal_seed_v1_1_supporting_archetypes_distinct():
    """RFC-0001: supporting_archetypes (인물 유형)와 supporting_roles
    (서사 기능)는 별개 필드."""
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="loyal_under_pressure",
        supporting_archetypes=("uncertain_actor", "watcher"),
        supporting_roles=("supporting_actor", "witness"),
    )
    assert seed.supporting_archetypes == ("uncertain_actor", "watcher")
    assert seed.supporting_roles == ("supporting_actor", "witness")
    # roundtrip
    restored = UniversalStorySeed.from_dict(seed.to_dict())
    assert restored == seed


def test_rfc_0001_document_exists():
    """Phase 2.5 §C: UniversalStorySeed v1.1 contract change requires RFC."""
    p = ROOT / "docs" / "plans" / "RFC_UNIVERSAL_STORY_SEED_V1_1.md"
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    for required in ("RFC-0001", "동기", "대안", "마이그레이션", "schema_version",
                      "approved", "main_archetype", "main_role", "flow_role"):
        assert required in text, f"RFC-0001 missing: {required}"


# ============================================================================
# 9. Phase 2.5 §D — Adapter Lossless
# ============================================================================

def test_adapter_requires_archetype():
    """Phase 2.5 §D.2.1: archetype은 lossless conversion에 필수."""
    cands, cards = _build_existing_inputs()
    from engine.observer.universal_seed_adapter import candidate_to_universal_seed
    with pytest.raises(ValueError, match="archetype is required"):
        candidate_to_universal_seed(cands[0], cards[0], archetype="")


def test_adapter_no_supporting_placeholder():
    """Phase 2.5 §D.2.3: supporting_roles에 'supporting_1'/'supporting_2'
    같은 numeric placeholder 금지. 'supporting_actor'는 legitimate role."""
    from engine.observer.universal_seed_adapter import (
        assemble_skeleton_output,
    )
    import re
    cands, cards = _build_existing_inputs()
    out = assemble_skeleton_output(cands, cards, anchor_id="peter_scarcity_baseline")
    placeholder_re = re.compile(r"^supporting_\d+$")
    for seed in out.seeds:
        for role in seed.supporting_roles:
            assert not placeholder_re.match(role), (
                f"supporting_roles contains numeric placeholder: {role!r}"
            )


def test_adapter_main_role_not_main():
    """Phase 2.5 §D.2: main_role은 protagonist/witness 등 의미 있는 값."""
    from engine.observer.universal_seed_adapter import (
        assemble_skeleton_output,
    )
    cands, cards = _build_existing_inputs()
    out = assemble_skeleton_output(cands, cards, anchor_id="peter_scarcity_baseline")
    for seed in out.seeds:
        assert seed.main_role != "main", (
            f"main_role placeholder leaked: {seed.seed_id} → {seed.main_role}"
        )
        assert seed.main_role != "", f"empty main_role: {seed.seed_id}"


def test_adapter_main_archetype_filled():
    """Phase 2.5 §D.5: 모든 seed에 main_archetype 존재."""
    from engine.observer.universal_seed_adapter import (
        assemble_skeleton_output,
    )
    cands, cards = _build_existing_inputs()
    out = assemble_skeleton_output(cands, cards, anchor_id="peter_scarcity_baseline")
    for seed in out.seeds:
        assert seed.main_archetype, f"empty main_archetype: {seed.seed_id}"


def test_adapter_pressures_4tier_fallback_phrase_to_axis():
    """Phase 2.5 §D.3: phrase가 매핑 안 되면 conflict_axis pole로 fallback."""
    from engine.observer.universal_seed_adapter import infer_pressures
    # uncertainty_vs_commitment의 pole_a = confusion (pressure)
    pressures, unmapped, tier = infer_pressures(
        [], "uncertainty_vs_commitment", "uncertain_actor",
    )
    assert "confusion" in pressures
    assert tier == "conflict_axis"


def test_adapter_pressures_4tier_fallback_axis_to_archetype():
    """Phase 2.5 §D.3: conflict_axis에 pressure pole 없으면 archetype default."""
    from engine.observer.universal_seed_adapter import infer_pressures
    # loyalty_vs_survival은 desire-vs-desire (pressure pole 없음)
    pressures, unmapped, tier = infer_pressures(
        [], "loyalty_vs_survival", "loyal_under_pressure",
    )
    assert "authority_vigilance" in pressures or "fear" in pressures
    assert tier == "archetype_default"


def test_adapter_unmapped_phrase_audited():
    """Phase 2.5 §D.4: unmapped phrase는 silent failure 대신 audit 누적."""
    from engine.observer.universal_seed_adapter import map_pressure_phrases
    mapped, unmapped = map_pressure_phrases([
        "fear intensifies",
        "this phrase is not in the map",
        "another unmapped phrase",
    ])
    assert "fear" in mapped
    assert "this phrase is not in the map" in unmapped
    assert "another unmapped phrase" in unmapped


def test_adapter_supporting_archetypes_populated():
    """Phase 2.5 §D.2.3: supporting_archetypes도 채워져야 (v1.1 신규 필드)."""
    from engine.observer.universal_seed_adapter import (
        assemble_skeleton_output, DEFAULT_SUPPORTING_ARCHETYPES_BY_SEED,
    )
    cands, cards = _build_existing_inputs()
    out = assemble_skeleton_output(cands, cards, anchor_id="peter_scarcity_baseline")
    for seed in out.seeds:
        if seed.seed_id in DEFAULT_SUPPORTING_ARCHETYPES_BY_SEED:
            expected = DEFAULT_SUPPORTING_ARCHETYPES_BY_SEED[seed.seed_id]
            assert seed.supporting_archetypes == expected


def test_adapter_audit_records_unmapped_phrases():
    """Phase 2.5 §D.4: assemble_skeleton_output가 unmapped phrase를 AuditTrail에
    기록해야."""
    from engine.observer.universal_seed_adapter import (
        assemble_skeleton_output, DEFAULT_ARCHETYPE_BY_SEED,
    )
    cands, cards = _build_existing_inputs()
    # 첫 candidate의 phrases를 모두 unmappable로 교체
    bad_cand = cands[0].__class__(
        **{**cands[0].__dict__,
           "world_pressure_context": ("totally_invented_phrase",)}
    ) if hasattr(cands[0], "__dict__") else None
    if bad_cand is None:
        pytest.skip("StoryCandidate not mutable for this test")
    cands_modified = [bad_cand] + list(cands[1:])
    out = assemble_skeleton_output(
        cands_modified, cards, anchor_id="peter_scarcity_baseline"
    )
    assert "totally_invented_phrase" in out.audit_trail.unmapped_pressure_phrases


# ============================================================================
# 10. Phase 2.5 §E — SkeletonOutput.flow not null
# ============================================================================

def test_skeleton_flow_not_null_by_default():
    """Phase 2.5 §E: SkeletonOutput.flow가 null이 아니어야."""
    from engine.observer.universal_seed_adapter import assemble_skeleton_output
    cands, cards = _build_existing_inputs()
    out = assemble_skeleton_output(cands, cards, anchor_id="peter_scarcity_baseline")
    assert out.flow is not None


def test_skeleton_flow_orders_main_arc_first():
    """Phase 2.5 §E.3: flow ordering — main_arc 먼저."""
    from engine.observer.universal_seed_adapter import assemble_skeleton_output
    cands, cards = _build_existing_inputs()
    out = assemble_skeleton_output(cands, cards, anchor_id="peter_scarcity_baseline")
    if not out.flow.ordered_seed_ids:
        pytest.skip("flow has no seeds")
    first_seed_id = out.flow.ordered_seed_ids[0]
    first_role = out.flow.flow_roles.get(first_seed_id)
    assert first_role == "main_arc", (
        f"flow ordering wrong: first seed {first_seed_id} role is {first_role}"
    )


def test_skeleton_flow_roles_cover_all_seeds():
    """Phase 2.5 §E.4: flow_roles가 모든 seed_id를 포함."""
    from engine.observer.universal_seed_adapter import assemble_skeleton_output
    cands, cards = _build_existing_inputs()
    out = assemble_skeleton_output(cands, cards, anchor_id="peter_scarcity_baseline")
    seed_ids = {s.seed_id for s in out.seeds}
    flow_role_keys = set(out.flow.flow_roles.keys())
    assert seed_ids == flow_role_keys


def test_skeleton_flow_can_be_disabled():
    """Phase 2.5 §E: fill_flow_default=False면 None 유지 (호환성)."""
    from engine.observer.universal_seed_adapter import assemble_skeleton_output
    cands, cards = _build_existing_inputs()
    out = assemble_skeleton_output(
        cands, cards, anchor_id="peter_scarcity_baseline",
        fill_flow_default=False,
    )
    assert out.flow is None


# ============================================================================
# 11. Phase 2.5 follow-up — Semantic validator (Phase 3 Go gate as code)
# ============================================================================

def test_skeleton_semantic_validator_passes_default_assembly():
    """기본 assemble로 만든 SkeletonOutput은 strict 통과해야 (Phase 3 Go)."""
    from engine.observer.universal_seed_adapter import (
        assemble_skeleton_output, validate_skeleton_semantic,
    )
    cands, cards = _build_existing_inputs()
    out = assemble_skeleton_output(cands, cards, anchor_id="peter_scarcity_baseline")
    errors = validate_skeleton_semantic(out, strict=True)
    assert errors == [], f"strict semantic validation failed: {errors}"


def test_skeleton_phase3_ready_helper():
    """is_skeleton_phase3_ready는 (True, []) 반환해야 한다."""
    from engine.observer.universal_seed_adapter import (
        assemble_skeleton_output, is_skeleton_phase3_ready,
    )
    cands, cards = _build_existing_inputs()
    out = assemble_skeleton_output(cands, cards, anchor_id="peter_scarcity_baseline")
    ready, errors = is_skeleton_phase3_ready(out)
    assert ready is True, errors


def test_semantic_validator_catches_main_role_placeholder():
    """main_role == 'main' 누수 catch."""
    from engine.observer.universal_story_seed import UniversalStorySeed
    from engine.observer.skeleton_output import SkeletonOutput, LifeStoryFlow
    from engine.observer.universal_seed_adapter import validate_skeleton_semantic

    bad = UniversalStorySeed(
        seed_id="S99", conflict_axis_id="loyalty_vs_survival",
        main_role="main",   # placeholder
        main_archetype="loyal_under_pressure",
        dominant_pressures=("fear",),
    )
    out = SkeletonOutput(
        seeds=(bad,),
        flow=LifeStoryFlow(ordered_seed_ids=("S99",), flow_roles={"S99": "main_arc"}),
    )
    errors = validate_skeleton_semantic(out, strict=True)
    assert any("main_role placeholder" in e for e in errors)


def test_semantic_validator_catches_silent_empty_pressures():
    """dominant_pressures 빈 채로 audit 기록 없으면 fail."""
    from engine.observer.universal_story_seed import UniversalStorySeed
    from engine.observer.skeleton_output import SkeletonOutput, LifeStoryFlow
    from engine.observer.universal_seed_adapter import validate_skeleton_semantic

    bad = UniversalStorySeed(
        seed_id="S99", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="loyal_under_pressure",
        dominant_pressures=(),
    )
    out = SkeletonOutput(
        seeds=(bad,),
        flow=LifeStoryFlow(ordered_seed_ids=("S99",), flow_roles={"S99": "main_arc"}),
    )
    errors = validate_skeleton_semantic(out, strict=True)
    assert any("silent empty" in e for e in errors)


def test_semantic_validator_catches_unknown_axis_strict():
    """unknown axis on normal seed → strict fail."""
    from engine.observer.universal_story_seed import UniversalStorySeed
    from engine.observer.skeleton_output import SkeletonOutput, LifeStoryFlow
    from engine.observer.universal_seed_adapter import validate_skeleton_semantic

    bad = UniversalStorySeed(
        seed_id="S99", conflict_axis_id="unknown",
        main_role="protagonist", main_archetype="loyal_under_pressure",
        dominant_pressures=("fear",),
    )
    out = SkeletonOutput(
        seeds=(bad,),
        flow=LifeStoryFlow(ordered_seed_ids=("S99",), flow_roles={"S99": "main_arc"}),
    )
    strict_errors = validate_skeleton_semantic(out, strict=True)
    assert any("unknown axis" in e for e in strict_errors)
    # lenient는 통과
    lenient_errors = validate_skeleton_semantic(out, strict=False)
    assert not any("unknown axis" in e for e in lenient_errors)


def test_semantic_validator_catches_missing_flow():
    """flow=None은 fail."""
    from engine.observer.universal_story_seed import UniversalStorySeed
    from engine.observer.skeleton_output import SkeletonOutput
    from engine.observer.universal_seed_adapter import validate_skeleton_semantic

    seed = UniversalStorySeed(
        seed_id="S99", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="loyal_under_pressure",
        dominant_pressures=("fear",),
    )
    out = SkeletonOutput(seeds=(seed,), flow=None)
    errors = validate_skeleton_semantic(out, strict=True)
    assert any("flow is None" in e for e in errors)


def test_semantic_validator_catches_flow_roles_missing_seed():
    """flow_roles가 어떤 seed를 빠뜨리면 fail."""
    from engine.observer.universal_story_seed import UniversalStorySeed
    from engine.observer.skeleton_output import SkeletonOutput, LifeStoryFlow
    from engine.observer.universal_seed_adapter import validate_skeleton_semantic

    s1 = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="loyal_under_pressure",
        dominant_pressures=("fear",),
    )
    s2 = UniversalStorySeed(
        seed_id="S02", conflict_axis_id="uncertainty_vs_commitment",
        main_role="supporting_actor", main_archetype="uncertain_actor",
        dominant_pressures=("confusion",),
    )
    flow = LifeStoryFlow(
        ordered_seed_ids=("S01", "S02"),
        flow_roles={"S01": "main_arc"},   # S02 missing
    )
    out = SkeletonOutput(seeds=(s1, s2), flow=flow)
    errors = validate_skeleton_semantic(out, strict=True)
    assert any("flow.flow_roles missing seeds" in e for e in errors)


# ============================================================================
# 12. Renderer v1.1 fields
# ============================================================================

def test_assemble_strict_axis_rejects_unknown(monkeypatch):
    """Phase 2.5 cycle 8 §B.2: strict_axis=True는 unknown axis seed를 assembly 시점 거부."""
    from engine.observer.universal_seed_adapter import assemble_skeleton_output
    cands, cards = _build_existing_inputs()
    # 첫 candidate의 conflict를 강제로 unknown으로 변경
    if hasattr(cands[0], "__dict__"):
        bad_cand = cands[0].__class__(
            **{**cands[0].__dict__, "core_conflict": "unknown"}
        )
    else:
        pytest.skip("StoryCandidate immutable")
    cands_with_unknown = [bad_cand] + list(cands[1:])

    # strict_axis=False (default) → 통과 (audit에만 기록)
    out_lenient = assemble_skeleton_output(
        cands_with_unknown, cards, anchor_id="peter_scarcity_baseline",
    )
    assert out_lenient.audit_trail.unknown_axis_count >= 1

    # strict_axis=True → ValueError
    with pytest.raises(ValueError, match="unknown.*conflict axis"):
        assemble_skeleton_output(
            cands_with_unknown, cards,
            anchor_id="peter_scarcity_baseline",
            strict_axis=True,
        )


def test_assemble_strict_axis_passes_clean_input():
    """strict_axis=True가 정상 입력에는 영향 없음."""
    from engine.observer.universal_seed_adapter import assemble_skeleton_output
    cands, cards = _build_existing_inputs()
    out = assemble_skeleton_output(
        cands, cards, anchor_id="peter_scarcity_baseline", strict_axis=True,
    )
    assert out.audit_trail.unknown_axis_count == 0
    assert len(out.seeds) == len(cards)


def test_renderer_dict_exposes_v1_1_fields():
    """Phase 2.5 follow-up: render_universal_seed_to_dict가 v1.1 신규 필드 노출."""
    from engine.anchor.universal_seed_renderer import render_universal_seed_to_dict
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="loyal_under_pressure",
        change_pattern="stay_present_then_withdraw",
        arc_direction="visibility_to_silence",
        relationship_function="group_presence_without_action",
        flow_role="main_arc",
        supporting_archetypes=("uncertain_actor", "watcher"),
        turning_points_count=3,
    )
    d = render_universal_seed_to_dict(seed, binding=None)
    for key in ("main_archetype", "main_role", "change_pattern", "arc_direction",
                "relationship_function", "flow_role", "supporting_archetypes",
                "turning_points_count"):
        assert key in d, f"renderer dict missing v1.1 field: {key}"
    assert d["change_pattern"] == "stay_present_then_withdraw"
    assert d["flow_role"] == "main_arc"
    assert d["turning_points_count"] == 3
