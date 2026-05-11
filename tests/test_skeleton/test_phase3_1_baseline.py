"""Phase 3.1 prep tests — GenreProfile + Flesh Baseline (No-ML weighted score).

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §22 + §26 + §27.

검증 대상 (외부 의존 0):
    - engine/observer/genre_profile.py
    - engine/observer/flesh_baseline.py
    - scripts/narrative/build_genre_profiles.py
    - scripts/narrative/run_flesh_baseline.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *cmd],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )


# ---------------------------------------------------------------------------
# 1. GenreProfile dataclass
# ---------------------------------------------------------------------------

def test_genre_profile_roundtrip():
    from engine.observer.genre_profile import GenreProfile, GENRE_PROFILE_VERSION
    p = GenreProfile(
        schema_version=GENRE_PROFILE_VERSION,
        genre_id="korean_morning_melodrama",
        feature_weights={"conflict_intensity_peak": 0.5, "cliffhanger_strength": 0.5},
        compatible_conflict_axes=("loyalty_vs_survival",),
        compatible_pressures=("authority_vigilance",),
        data_source="phase3_pilot",
        n_records_basis=10,
    )
    d = p.to_dict()
    restored = GenreProfile.from_dict(d)
    assert restored == p


def test_normalize_weights_sums_to_one():
    from engine.observer.genre_profile import normalize_weights
    w = normalize_weights({"a": 2.0, "b": 1.0, "c": 1.0})
    assert abs(sum(w.values()) - 1.0) < 1e-3
    assert w["a"] == 0.5


def test_build_profile_from_rulebook():
    """Rulebook + KEEP feature → GenreProfile. compatibility 자동 추출."""
    from engine.observer.genre_profile import build_profile_from_rulebook
    from engine.observer.genre_rulebook import load_rulebook
    rb = load_rulebook("korean_morning_melodrama")
    keep = ["conflict_intensity_peak", "dangling_thread_generation"]
    p = build_profile_from_rulebook(
        genre_id="korean_morning_melodrama",
        rulebook=rb,
        keep_features=keep,
    )
    assert p.genre_id == "korean_morning_melodrama"
    # uniform weights when feature_weights=None
    assert len(p.feature_weights) == 2
    assert all(abs(w - 0.5) < 1e-3 for w in p.feature_weights.values())
    # compatible axes from amplifiers
    assert "loyalty_vs_survival" in p.compatible_conflict_axes
    # compatible pressures from rulebook.pressure_mappings
    assert "authority_vigilance" in p.compatible_pressures


def test_build_profile_filters_keep_only():
    """feature_weights에서 KEEP에 없는 feature는 제거."""
    from engine.observer.genre_profile import build_profile_from_rulebook
    from engine.observer.genre_rulebook import load_rulebook
    rb = load_rulebook("korean_morning_melodrama")
    keep = ["conflict_intensity_peak"]
    weights = {
        "conflict_intensity_peak": 0.6,
        "non_keep_feature": 0.4,  # 제거되어야
    }
    p = build_profile_from_rulebook(
        genre_id="km", rulebook=rb,
        keep_features=keep, feature_weights=weights,
    )
    assert "non_keep_feature" not in p.feature_weights
    assert "conflict_intensity_peak" in p.feature_weights
    # normalized to 1.0
    assert abs(sum(p.feature_weights.values()) - 1.0) < 1e-3


# ---------------------------------------------------------------------------
# 2. Flesh Baseline scoring
# ---------------------------------------------------------------------------

def test_compute_compatibility_score_axis_match():
    from engine.observer.flesh_baseline import compute_compatibility_score
    from engine.observer.genre_profile import GenreProfile
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="loyal_under_pressure",
        dominant_pressures=("authority_vigilance",),
    )
    profile = GenreProfile(
        schema_version="genre_profile_v1",
        genre_id="km",
        feature_weights={},
        compatible_conflict_axes=("loyalty_vs_survival",),
        compatible_pressures=("authority_vigilance",),
    )
    score, reasons = compute_compatibility_score(seed, profile)
    assert score == 1.0  # 0.5 axis + 0.5 pressure
    assert any("conflict_axis:loyalty_vs_survival" in r for r in reasons)
    assert any("pressure:authority_vigilance" in r for r in reasons)


def test_compute_compatibility_score_no_match():
    from engine.observer.flesh_baseline import compute_compatibility_score
    from engine.observer.genre_profile import GenreProfile
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="nonexistent_axis",
        main_role="protagonist", main_archetype="x",
        dominant_pressures=("nonexistent_pressure",),
    )
    profile = GenreProfile(
        schema_version="genre_profile_v1", genre_id="km",
        feature_weights={},
        compatible_conflict_axes=("loyalty_vs_survival",),
        compatible_pressures=("authority_vigilance",),
    )
    score, reasons = compute_compatibility_score(seed, profile)
    assert score == 0.0
    assert reasons == []


def test_compute_annotation_score_linear():
    """Phase 3.1 §23.1 weighted rule score."""
    from engine.observer.flesh_baseline import compute_annotation_score
    from engine.observer.genre_profile import GenreProfile
    profile = GenreProfile(
        schema_version="genre_profile_v1", genre_id="km",
        feature_weights={
            "conflict_intensity_peak": 0.4,
            "dangling_thread_generation": 0.3,
            "cliffhanger_strength": 0.3,
        },
        compatible_conflict_axes=(), compatible_pressures=(),
    )
    # 모든 score = 5 (max) → normalized 1.0 → score = sum(weights) = 1.0
    ann = {
        "conflict_intensity_peak": 5,
        "dangling_thread_generation": 5,
        "cliffhanger_strength": 5,
    }
    score, reasons, breakdown = compute_annotation_score(ann, profile)
    assert abs(score - 1.0) < 1e-3
    assert len(reasons) == 3  # top-3 contributors


def test_fit_label_thresholds():
    from engine.observer.flesh_baseline import fit_label_for_score
    assert fit_label_for_score(0.95) == "strong_fit"
    assert fit_label_for_score(0.7) == "strong_fit"
    assert fit_label_for_score(0.6) == "moderate_fit"
    assert fit_label_for_score(0.5) == "moderate_fit"
    assert fit_label_for_score(0.3) == "weak_fit"
    assert fit_label_for_score(0.1) == "no_fit"


def test_recommend_seed_compatibility_only():
    from engine.observer.flesh_baseline import recommend_seed
    from engine.observer.genre_profile import GenreProfile
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="loyal_under_pressure",
        dominant_pressures=("authority_vigilance",),
    )
    profile = GenreProfile(
        schema_version="genre_profile_v1", genre_id="km",
        feature_weights={"conflict_intensity_peak": 1.0},
        compatible_conflict_axes=("loyalty_vs_survival",),
        compatible_pressures=("authority_vigilance",),
    )
    rec = recommend_seed(seed, profile)
    assert rec.source_seed_id == "S01"
    assert rec.genre_id == "km"
    assert rec.fit_label == "strong_fit"
    assert rec.score == 1.0


def test_recommend_seed_blends_annotation_and_compatibility():
    from engine.observer.flesh_baseline import recommend_seed
    from engine.observer.genre_profile import GenreProfile
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="loyal_under_pressure",
        dominant_pressures=("authority_vigilance",),
    )
    profile = GenreProfile(
        schema_version="genre_profile_v1", genre_id="km",
        feature_weights={"conflict_intensity_peak": 1.0},
        compatible_conflict_axes=("loyalty_vs_survival",),
        compatible_pressures=("authority_vigilance",),
    )
    # compatibility=1.0, annotation=0.4 (score 2/5) → blend = 0.7
    rec = recommend_seed(
        seed, profile, annotation_features={"conflict_intensity_peak": 2},
    )
    assert 0.65 < rec.score < 0.75


# ---------------------------------------------------------------------------
# 3. run_flesh_baseline (top-level)
# ---------------------------------------------------------------------------

def _make_skeleton_with_two_seeds():
    from engine.observer.skeleton_output import (
        AnchorMetadata, AuditTrail, EvidenceLedger, LifeStoryFlow, SkeletonOutput,
    )
    from engine.observer.universal_story_seed import UniversalStorySeed
    s1 = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="loyal_under_pressure",
        dominant_pressures=("authority_vigilance",),
        flow_role="main_arc",
    )
    s2 = UniversalStorySeed(
        seed_id="S02", conflict_axis_id="uncertainty_vs_commitment",
        main_role="supporting_actor", main_archetype="uncertain_actor",
        dominant_pressures=("confusion",),
        flow_role="supporting_uncertainty",
    )
    return SkeletonOutput(
        seeds=(s1, s2),
        flow=LifeStoryFlow(
            ordered_seed_ids=("S01", "S02"),
            flow_roles={"S01": "main_arc", "S02": "supporting_uncertainty"},
        ),
        evidence_ledger=EvidenceLedger(),
        anchor_metadata=AnchorMetadata(anchor_id="test_anchor"),
        audit_trail=AuditTrail(),
    )


def test_run_flesh_baseline_produces_recommendations_per_seed_per_profile():
    from engine.observer.flesh_baseline import run_flesh_baseline
    from engine.observer.genre_profile import GenreProfile

    sk = _make_skeleton_with_two_seeds()
    profiles = [
        GenreProfile(
            schema_version="genre_profile_v1", genre_id="km",
            feature_weights={"conflict_intensity_peak": 1.0},
            compatible_conflict_axes=("loyalty_vs_survival",),
            compatible_pressures=("authority_vigilance",),
        ),
        GenreProfile(
            schema_version="genre_profile_v1", genre_id="jp",
            feature_weights={"silence_or_avoidance": 1.0},
            compatible_conflict_axes=("uncertainty_vs_commitment",),
            compatible_pressures=("confusion",),
        ),
    ]
    out = run_flesh_baseline(sk, profiles)
    # 2 seeds × 2 profiles = 4 recommendations
    assert len(out.recommendations) == 4
    assert out.schema_version == "flesh_baseline_output_v1"
    assert out.model_trained is False
    assert out.audit_raw_text_used is False
    # S01 → km strong_fit (loyalty axis match)
    s01_km = next(
        r for r in out.recommendations
        if r.source_seed_id == "S01" and r.genre_id == "km"
    )
    assert s01_km.fit_label == "strong_fit"
    # S02 → jp strong_fit (uncertainty axis match)
    s02_jp = next(
        r for r in out.recommendations
        if r.source_seed_id == "S02" and r.genre_id == "jp"
    )
    assert s02_jp.fit_label == "strong_fit"
    # cross: S01 → jp / S02 → km는 약함
    s01_jp = next(
        r for r in out.recommendations
        if r.source_seed_id == "S01" and r.genre_id == "jp"
    )
    assert s01_jp.score < 0.5


def test_flesh_baseline_to_dict_serializable():
    from engine.observer.flesh_baseline import run_flesh_baseline
    from engine.observer.genre_profile import GenreProfile
    sk = _make_skeleton_with_two_seeds()
    profile = GenreProfile(
        schema_version="genre_profile_v1", genre_id="km",
        feature_weights={"f1": 1.0},
        compatible_conflict_axes=("loyalty_vs_survival",),
        compatible_pressures=("authority_vigilance",),
    )
    out = run_flesh_baseline(sk, [profile])
    d = out.to_dict()
    # JSON serializable
    s = json.dumps(d, ensure_ascii=False)
    assert "flesh_baseline_output_v1" in s
    # audit fields present
    assert d["audit"]["raw_text_used"] is False
    assert d["audit"]["evidence_preserved"] is True
    assert d["model"]["type"] == "weighted_rule_score"
    assert d["model"]["trained"] is False


# ---------------------------------------------------------------------------
# 4. CLI: build_genre_profiles.py
# ---------------------------------------------------------------------------

BUILD_PROFILES = ROOT / "scripts/narrative/build_genre_profiles.py"


def test_build_profiles_help():
    rc = _run([str(BUILD_PROFILES), "--help"])
    assert rc.returncode == 0


def test_build_profiles_rulebook_only(tmp_path):
    out = tmp_path / "profiles.json"
    rc = _run([
        str(BUILD_PROFILES),
        "--genres", "korean_morning_melodrama",
        "--output", str(out),
        "--allow-rulebook-only",
    ])
    assert rc.returncode == 0, rc.stderr
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["schema_version"] == "genre_profiles_index_v1"
    assert len(d["profiles"]) == 1
    assert d["profiles"][0]["genre_id"] == "korean_morning_melodrama"
    assert d["profiles"][0]["data_source"] == "rulebook_only"


def test_build_profiles_requires_reliability_or_flag(tmp_path):
    out = tmp_path / "profiles.json"
    rc = _run([
        str(BUILD_PROFILES),
        "--genres", "korean_morning_melodrama",
        "--output", str(out),
        # no --reliability and no --allow-rulebook-only → fail
    ])
    assert rc.returncode == 1
    assert "allow-rulebook-only" in rc.stderr


def test_build_profiles_with_reliability(tmp_path):
    """reliability.json + KEEP features 사용."""
    rel = tmp_path / "rel.json"
    rel.write_text(json.dumps({
        "schema_version": "phase3_reliability_report_v1",
        "n_records": 10,
        "n_annotators": 2,
        "feature_reliability": {
            "conflict_intensity_peak": {"mean_r": 0.85, "decision": "KEEP"},
            "dangling_thread_generation": {"mean_r": 0.78, "decision": "KEEP"},
            "cliffhanger_strength": {"mean_r": 0.74, "decision": "KEEP"},
            "relationship_pressure": {"mean_r": 0.72, "decision": "KEEP"},
            "hidden_information_pressure": {"mean_r": 0.65, "decision": "REVISE"},
        },
        "summary": {
            "keep": [
                "conflict_intensity_peak",
                "dangling_thread_generation",
                "cliffhanger_strength",
                "relationship_pressure",
            ],
            "revise": ["hidden_information_pressure"],
            "drop": [],
            "needs_more_data": [],
            "n_keep": 4,
            "phase3_threshold_pass": True,
        },
    }), encoding="utf-8")
    out = tmp_path / "profiles.json"
    rc = _run([
        str(BUILD_PROFILES),
        "--reliability", str(rel),
        "--genres", "korean_morning_melodrama",
        "--output", str(out),
    ])
    assert rc.returncode == 0, rc.stderr
    d = json.loads(out.read_text(encoding="utf-8"))
    p = d["profiles"][0]
    # 4 KEEP features만 weight
    assert len(p["feature_weights"]) == 4
    assert "hidden_information_pressure" not in p["feature_weights"]
    assert p["data_source"] == "phase3_pilot"
    assert p["n_records_basis"] == 10


def test_build_profiles_low_keep_fails_without_flag(tmp_path):
    rel = tmp_path / "rel.json"
    rel.write_text(json.dumps({
        "schema_version": "phase3_reliability_report_v1",
        "feature_reliability": {},
        "summary": {"keep": ["only_one"], "n_keep": 1, "phase3_threshold_pass": False},
    }), encoding="utf-8")
    out = tmp_path / "profiles.json"
    rc = _run([
        str(BUILD_PROFILES),
        "--reliability", str(rel),
        "--genres", "korean_morning_melodrama",
        "--output", str(out),
        "--require-min-keep", "4",
    ])
    assert rc.returncode == 1
    assert "Phase 3.1" in rc.stderr or "allow-rulebook-only" in rc.stderr


# ---------------------------------------------------------------------------
# 5. CLI: run_flesh_baseline.py
# ---------------------------------------------------------------------------

RUN_BASELINE = ROOT / "scripts/narrative/run_flesh_baseline.py"
DEPLOYED_SKELETON = ROOT / "docs/portfolio/demo/skeleton_output.json"


def test_run_baseline_help():
    rc = _run([str(RUN_BASELINE), "--help"])
    assert rc.returncode == 0


def test_run_baseline_e2e_on_deployed(tmp_path):
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()

    # 1. build profiles (rulebook-only mode)
    profiles_path = tmp_path / "profiles.json"
    rc = _run([
        str(BUILD_PROFILES),
        "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
        "--output", str(profiles_path),
        "--allow-rulebook-only",
    ])
    assert rc.returncode == 0, rc.stderr

    # 2. run baseline
    out = tmp_path / "baseline.json"
    rc = _run([
        str(RUN_BASELINE),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--profiles", str(profiles_path),
        "--output", str(out),
    ])
    assert rc.returncode == 0, rc.stderr
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["schema_version"] == "flesh_baseline_output_v1"
    assert len(d["genre_profiles_used"]) == 2
    # 4 seeds × 2 profiles = 8 recommendations
    assert len(d["recommendations"]) == 8
    # raw text 노출 0
    s = json.dumps(d, ensure_ascii=False)
    assert "synopsis_text" not in s
    # 모든 rec에 reason_features 또는 score_breakdown
    for rec in d["recommendations"]:
        assert isinstance(rec["reason_features"], list)
        assert "fit_label" in rec
        assert rec["recommended_adapter"] == "rulebook_v2_8"


def test_run_baseline_exit_2_on_missing_skeleton(tmp_path):
    rc = _run([
        str(RUN_BASELINE),
        "--skeleton", str(tmp_path / "missing.json"),
        "--profiles", str(tmp_path / "p.json"),
        "--output", str(tmp_path / "out.json"),
    ])
    assert rc.returncode == 2


# ---------------------------------------------------------------------------
# 6. CLI: build_flesh_baseline_demo.py (Phase 3.1 §28 demo)
# ---------------------------------------------------------------------------

BUILD_DEMO = ROOT / "scripts/narrative/build_flesh_baseline_demo.py"


def test_build_demo_help():
    rc = _run([str(BUILD_DEMO), "--help"])
    assert rc.returncode == 0


def test_build_demo_e2e_on_deployed(tmp_path):
    """e2e — skeleton + profiles → baseline → demo HTML + MD + JSON."""
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()

    # 1. profiles
    profiles_path = tmp_path / "profiles.json"
    rc = _run([
        str(BUILD_PROFILES),
        "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
        "--output", str(profiles_path),
        "--allow-rulebook-only",
    ])
    assert rc.returncode == 0, rc.stderr

    # 2. baseline output
    baseline_path = tmp_path / "baseline.json"
    rc = _run([
        str(RUN_BASELINE),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--profiles", str(profiles_path),
        "--output", str(baseline_path),
    ])
    assert rc.returncode == 0, rc.stderr

    # 3. demo
    out_dir = tmp_path / "demo_flesh_baseline"
    rc = _run([
        str(BUILD_DEMO),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--baseline", str(baseline_path),
        "--output", str(out_dir),
    ])
    assert rc.returncode == 0, rc.stderr

    # 4. files
    for fname in ("index.html", "baseline.md", "flesh_baseline_output.json"):
        assert (out_dir / fname).exists(), f"missing {fname}"


def test_demo_html_self_contained(tmp_path):
    """index.html 외부 CDN / asset 의존 0."""
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()
    profiles_path = tmp_path / "profiles.json"
    _run([str(BUILD_PROFILES),
           "--genres", "korean_morning_melodrama",
           "--output", str(profiles_path),
           "--allow-rulebook-only"])
    baseline_path = tmp_path / "baseline.json"
    _run([str(RUN_BASELINE),
           "--skeleton", str(DEPLOYED_SKELETON),
           "--profiles", str(profiles_path),
           "--output", str(baseline_path)])
    out_dir = tmp_path / "demo"
    _run([str(BUILD_DEMO),
           "--skeleton", str(DEPLOYED_SKELETON),
           "--baseline", str(baseline_path),
           "--output", str(out_dir)])

    html = (out_dir / "index.html").read_text(encoding="utf-8")
    forbidden = (
        '<script src="http', '<link rel="stylesheet" href="http',
        'cdn.jsdelivr', 'googleapis.com', 'cdnjs.cloudflare', 'fonts.gstatic',
    )
    for tok in forbidden:
        assert tok not in html, f"HTML uses external resource: {tok}"
    assert "Phase 3.1" in html or "Flesh Baseline" in html
    assert "weighted_rule_score" in html


def test_demo_no_synopsis_text_leakage(tmp_path):
    """raw text 노출 0 — synopsis_text가 baseline output에도 demo에도 없어야."""
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()
    profiles_path = tmp_path / "profiles.json"
    _run([str(BUILD_PROFILES),
           "--genres", "korean_morning_melodrama",
           "--output", str(profiles_path),
           "--allow-rulebook-only"])
    baseline_path = tmp_path / "baseline.json"
    _run([str(RUN_BASELINE),
           "--skeleton", str(DEPLOYED_SKELETON),
           "--profiles", str(profiles_path),
           "--output", str(baseline_path)])
    out_dir = tmp_path / "demo"
    _run([str(BUILD_DEMO),
           "--skeleton", str(DEPLOYED_SKELETON),
           "--baseline", str(baseline_path),
           "--output", str(out_dir)])

    # synopsis_text는 baseline output / demo HTML / md 어디에도 없어야
    for fname in ("index.html", "baseline.md", "flesh_baseline_output.json"):
        content = (out_dir / fname).read_text(encoding="utf-8")
        assert "synopsis_text" not in content, (
            f"{fname}: synopsis_text leaked"
        )


def test_demo_md_includes_per_seed_top():
    """md 산출물에 각 skeleton seed별 top recommendation 포함."""
    deployed = ROOT / "docs/portfolio/demo_flesh_baseline/baseline.md"
    if not deployed.exists():
        pytest.skip("deployed flesh baseline demo missing")
    md = deployed.read_text(encoding="utf-8")
    # deployed skeleton has 4 seeds (S01-S04)
    for sid in ("S01", "S02", "S03", "S04"):
        assert sid in md, f"baseline.md missing seed {sid}"
    # data_source visible
    assert "data_source" in md or "rulebook_only" in md or "phase3_pilot" in md


def test_demo_html_audit_tags_present():
    """deployed HTML에 raw_text_used / evidence_preserved / model.trained tag."""
    deployed = ROOT / "docs/portfolio/demo_flesh_baseline/index.html"
    if not deployed.exists():
        pytest.skip()
    html = deployed.read_text(encoding="utf-8")
    assert "raw_text_used" in html
    assert "evidence_preserved" in html
    assert "model.trained" in html
    # all should show false (Phase 3.1 prep mode)
    assert "raw_text_used: false" in html
    assert "model.trained: false" in html


# ---------------------------------------------------------------------------
# 7. Full pipeline e2e — fixture → reliability → profiles → flesh_baseline
# ---------------------------------------------------------------------------

PUBLIC_SAFE_FIXTURE = ROOT / "tests/fixtures/annotation_public_safe"
NORM_SCRIPT = ROOT / "scripts/data/normalize_synopsis.py"
VAL_DS_SCRIPT = ROOT / "scripts/data/validate_synopsis_dataset.py"
VAL_OUT_SCRIPT = ROOT / "scripts/annotation/validate_annotation_outputs.py"
BUILD_MAT_SCRIPT = ROOT / "scripts/annotation/build_feature_matrix.py"
BUILD_REL_SCRIPT = ROOT / "scripts/annotation/build_reliability_report.py"


def test_full_pipeline_e2e_fixture_to_baseline(tmp_path):
    """Phase 3.0 v1.1 + 3.1 prep 통합 e2e — fixture에서 시작, recommendations까지.

    이 test는 12 모듈 (7 pipeline + 5 baseline) 모두를 한 번에 검증한다:
        1. normalize_synopsis (fixture raw → JSONL)
        2. validate_synopsis_dataset (JSONL schema)
        3. validate_annotation_outputs (fixture outputs → hallucination 0)
        4. build_feature_matrix (CSV)
        5. build_reliability_report (KEEP/REVISE/DROP)
        6. build_genre_profiles (reliability → profiles)
        7. run_flesh_baseline (skeleton + profiles → recommendations)
        8. build_flesh_baseline_demo (recommendations → HTML/MD)
    """
    raw_dir = PUBLIC_SAFE_FIXTURE / "synopsis_raw_demo"
    outputs_dir = PUBLIC_SAFE_FIXTURE / "annotation_outputs_demo"
    if not (raw_dir.exists() and outputs_dir.exists()):
        pytest.skip("public-safe fixture missing")

    # Step 1: normalize
    norm = tmp_path / "norm.jsonl"
    rc = _run([str(NORM_SCRIPT),
                "--input", str(raw_dir),
                "--output", str(norm)])
    assert rc.returncode == 0, rc.stderr

    # Step 2: validate dataset
    rc = _run([str(VAL_DS_SCRIPT),
                "--input", str(norm),
                "--strict-min-records", "5"])
    assert rc.returncode == 0, rc.stderr

    # Step 3: validate annotation outputs
    halluc = tmp_path / "halluc.json"
    rc = _run([str(VAL_OUT_SCRIPT),
                "--input", str(outputs_dir),
                "--synopsis", str(norm),
                "--hallucination-report", str(halluc)])
    assert rc.returncode == 0, rc.stderr
    halluc_data = json.loads(halluc.read_text(encoding="utf-8"))
    assert halluc_data["phase3_threshold_pass"] is True

    # Step 4: feature matrix
    feat_csv = tmp_path / "feat.csv"
    rc = _run([str(BUILD_MAT_SCRIPT),
                "--input", str(outputs_dir),
                "--output", str(feat_csv)])
    assert rc.returncode == 0

    # Step 5: reliability
    rel = tmp_path / "rel.json"
    rc = _run([str(BUILD_REL_SCRIPT),
                "--features", str(feat_csv),
                "--output", str(rel)])
    assert rc.returncode == 0
    rel_data = json.loads(rel.read_text(encoding="utf-8"))
    # fixture: 2 models 거의 일치 → 4+ KEEP features
    assert rel_data["summary"]["phase3_threshold_pass"] is True
    assert len(rel_data["summary"]["keep"]) >= 4

    # Step 6: genre profiles (실제 reliability 사용)
    profiles = tmp_path / "profiles.json"
    rc = _run([str(BUILD_PROFILES),
                "--reliability", str(rel),
                "--genres", "korean_morning_melodrama",
                "--output", str(profiles)])
    assert rc.returncode == 0, rc.stderr
    profile_data = json.loads(profiles.read_text(encoding="utf-8"))
    assert profile_data["profiles"][0]["data_source"] == "phase3_pilot"
    # KEEP feature만 weight (≥ 4)
    assert len(profile_data["profiles"][0]["feature_weights"]) >= 4

    # Step 7: flesh baseline
    if not DEPLOYED_SKELETON.exists():
        pytest.skip("deployed skeleton missing")
    baseline = tmp_path / "baseline.json"
    rc = _run([str(RUN_BASELINE),
                "--skeleton", str(DEPLOYED_SKELETON),
                "--profiles", str(profiles),
                "--output", str(baseline)])
    assert rc.returncode == 0, rc.stderr
    baseline_data = json.loads(baseline.read_text(encoding="utf-8"))
    # Phase 3.0 데이터 backed (rulebook_only 아님)
    assert baseline_data["model"]["data_source"] == "phase3_pilot"
    # raw text 노출 0
    assert baseline_data["audit"]["raw_text_used"] is False
    assert baseline_data["audit"]["evidence_preserved"] is True
    assert baseline_data["model"]["trained"] is False
    # recommendations 존재
    assert len(baseline_data["recommendations"]) >= 1

    # Step 8: demo HTML
    demo_dir = tmp_path / "demo"
    rc = _run([str(BUILD_DEMO),
                "--skeleton", str(DEPLOYED_SKELETON),
                "--baseline", str(baseline),
                "--output", str(demo_dir)])
    assert rc.returncode == 0, rc.stderr
    html = (demo_dir / "index.html").read_text(encoding="utf-8")
    # phase3_pilot data source banner (cycle 4 §10 정직성 패턴)
    assert "phase3_pilot" in html or "Phase 3.0" in html
    # synopsis_text 노출 0 — 모든 layer
    for fname in ("index.html", "baseline.md", "flesh_baseline_output.json"):
        assert "synopsis_text" not in (demo_dir / fname).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 8. EpisodeIntensity (cycle 8 — Plan §22.2)
# ---------------------------------------------------------------------------

RUN_INTENSITY = ROOT / "scripts/annotation/run_episode_intensity.py"


def test_episode_intensity_aggregate_features():
    """Long-form rows → {record_id: ({feature: mean}, n_annotators)}."""
    from engine.observer.episode_intensity import aggregate_features_by_record
    rows = [
        {"record_id": "r1", "annotator_id": "A", "feature": "x", "score": 4},
        {"record_id": "r1", "annotator_id": "B", "feature": "x", "score": 2},
        {"record_id": "r1", "annotator_id": "A", "feature": "y", "score": 5},
        {"record_id": "r2", "annotator_id": "A", "feature": "x", "score": 3},
    ]
    out = aggregate_features_by_record(rows)
    assert out["r1"][0]["x"] == 3.0    # mean of 4,2
    assert out["r1"][0]["y"] == 5.0
    assert out["r1"][1] == 2          # 2 annotators
    assert out["r2"][1] == 1


def test_episode_intensity_aggregate_with_kept_filter():
    """kept_features 지정 시 다른 feature는 무시."""
    from engine.observer.episode_intensity import aggregate_features_by_record
    rows = [
        {"record_id": "r1", "annotator_id": "A", "feature": "keep_me", "score": 4},
        {"record_id": "r1", "annotator_id": "A", "feature": "drop_me", "score": 5},
    ]
    out = aggregate_features_by_record(rows, kept_features=["keep_me"])
    assert "keep_me" in out["r1"][0]
    assert "drop_me" not in out["r1"][0]


def test_episode_intensity_compute_record():
    """Single record × profile → intensity."""
    from engine.observer.episode_intensity import compute_episode_intensity
    from engine.observer.genre_profile import GenreProfile, GENRE_PROFILE_VERSION
    profile = GenreProfile(
        schema_version=GENRE_PROFILE_VERSION,
        genre_id="korean_morning_melodrama",
        feature_weights={"silence_or_avoidance": 0.5, "cliffhanger_strength": 0.5},
        compatible_conflict_axes=(),
        compatible_pressures=(),
    )
    # both at level 5 → normalized 1.0 → intensity = 0.5*1 + 0.5*1 = 1.0
    record = compute_episode_intensity(
        "r1", {"silence_or_avoidance": 5.0, "cliffhanger_strength": 5.0},
        n_annotators=2, profile=profile,
    )
    assert record.intensity_score == 1.0
    assert record.fit_label == "strong_fit"
    # mid-level → mid score
    record2 = compute_episode_intensity(
        "r2", {"silence_or_avoidance": 2.0, "cliffhanger_strength": 3.0},
        n_annotators=2, profile=profile,
    )
    # (2/5)*0.5 + (3/5)*0.5 = 0.2 + 0.3 = 0.5
    assert abs(record2.intensity_score - 0.5) < 1e-3
    assert record2.fit_label == "moderate_fit"


def test_episode_intensity_missing_feature_zero_contribution():
    """Profile feature가 record에 없으면 contribution 0."""
    from engine.observer.episode_intensity import compute_episode_intensity
    from engine.observer.genre_profile import GenreProfile, GENRE_PROFILE_VERSION
    profile = GenreProfile(
        schema_version=GENRE_PROFILE_VERSION,
        genre_id="g1",
        feature_weights={"a": 0.5, "missing": 0.5},
        compatible_conflict_axes=(),
        compatible_pressures=(),
    )
    rec = compute_episode_intensity("r1", {"a": 5.0}, 1, profile)
    # only "a" contributes: 1.0 * 0.5 = 0.5
    assert rec.intensity_score == 0.5
    assert rec.feature_contributions["missing"] == 0.0


def test_episode_intensity_runner_top_level():
    """run_episode_intensity → multi-record × multi-profile output."""
    from engine.observer.episode_intensity import run_episode_intensity
    from engine.observer.genre_profile import GenreProfile, GENRE_PROFILE_VERSION

    rows = [
        {"record_id": "r1", "annotator_id": "A", "feature": "f1", "score": 5},
        {"record_id": "r1", "annotator_id": "B", "feature": "f1", "score": 4},
        {"record_id": "r2", "annotator_id": "A", "feature": "f1", "score": 1},
    ]
    p1 = GenreProfile(
        schema_version=GENRE_PROFILE_VERSION,
        genre_id="g1", feature_weights={"f1": 1.0},
        compatible_conflict_axes=(), compatible_pressures=(),
    )
    p2 = GenreProfile(
        schema_version=GENRE_PROFILE_VERSION,
        genre_id="g2", feature_weights={"f1": 0.5},
        compatible_conflict_axes=(), compatible_pressures=(),
    )
    out = run_episode_intensity(rows, [p1, p2])
    d = out.to_dict()
    assert d["schema_version"] == "episode_intensity_v1"
    assert d["n_records"] == 2
    assert d["n_genres"] == 2
    # 2 records × 2 profiles = 4 records
    assert len(d["intensity_records"]) == 4
    assert d["model"]["trained"] is False
    assert d["audit"]["raw_text_used"] is False


def test_episode_intensity_cli_help():
    rc = _run([str(RUN_INTENSITY), "--help"])
    assert rc.returncode == 0


def test_episode_intensity_cli_e2e_on_fixture(tmp_path):
    """e2e: fixture → feature_matrix → reliability → profiles → intensity."""
    fixture = ROOT / "tests/fixtures/annotation_public_safe"
    raw = fixture / "synopsis_raw_demo"
    outputs = fixture / "annotation_outputs_demo"
    if not (raw.exists() and outputs.exists()):
        pytest.skip("fixture missing")

    # 1. normalize
    norm = tmp_path / "norm.jsonl"
    rc = _run([str(NORM_SCRIPT), "--input", str(raw), "--output", str(norm)])
    assert rc.returncode == 0, rc.stderr
    # 2. feature matrix
    feat = tmp_path / "feat.csv"
    rc = _run([str(BUILD_MAT_SCRIPT), "--input", str(outputs), "--output", str(feat)])
    assert rc.returncode == 0
    # 3. reliability
    rel = tmp_path / "rel.json"
    rc = _run([str(BUILD_REL_SCRIPT), "--features", str(feat), "--output", str(rel)])
    assert rc.returncode == 0
    # 4. profiles (with reliability)
    profiles = tmp_path / "profiles.json"
    rc = _run([str(BUILD_PROFILES),
                "--reliability", str(rel),
                "--genres", "korean_morning_melodrama",
                "--output", str(profiles)])
    assert rc.returncode == 0, rc.stderr
    # 5. episode intensity
    intensity = tmp_path / "intensity.json"
    rc = _run([str(RUN_INTENSITY),
                "--feature-matrix", str(feat),
                "--profiles", str(profiles),
                "--reliability", str(rel),
                "--output", str(intensity),
                "--strict-min-records", "10"])
    assert rc.returncode == 0, rc.stderr
    d = json.loads(intensity.read_text(encoding="utf-8"))
    assert d["schema_version"] == "episode_intensity_v1"
    assert d["n_records"] == 10                # 2 titles × 5 episodes
    assert d["n_genres"] == 1
    assert d["model"]["trained"] is False
    assert d["audit"]["raw_text_used"] is False
    # Phase 3.1 GO 임계 (≥4 KEEP) → KEEP feature만 사용됨
    assert len(d["kept_features_used"]) >= 4
    # 모든 record에 score가 있고 [0,1] 범위
    for rec in d["intensity_records"]:
        assert 0.0 <= rec["intensity_score"] <= 1.0
        assert rec["fit_label"] in ("strong_fit", "moderate_fit", "weak_fit", "no_fit")
        assert rec["genre_id"] == "korean_morning_melodrama"
    # synopsis_text 노출 0
    s = json.dumps(d, ensure_ascii=False)
    assert "synopsis_text" not in s


def test_episode_intensity_cli_exit_2_on_missing(tmp_path):
    rc = _run([str(RUN_INTENSITY),
                "--feature-matrix", str(tmp_path / "missing.csv"),
                "--profiles", str(tmp_path / "p.json"),
                "--output", str(tmp_path / "o.json")])
    assert rc.returncode == 2


# ---------------------------------------------------------------------------
# 9. EpisodeIntensity Demo HTML (cycle 10 — Plan §22.2 + §28)
# ---------------------------------------------------------------------------

BUILD_INTENSITY_DEMO = ROOT / "scripts/annotation/build_episode_intensity_demo.py"


def test_episode_intensity_demo_help():
    rc = _run([str(BUILD_INTENSITY_DEMO), "--help"])
    assert rc.returncode == 0


def test_episode_intensity_demo_parse_record_id():
    """record_id parsing for title × genre grouping."""
    from scripts.annotation.build_episode_intensity_demo import parse_record_id
    assert parse_record_id("km_titleA_ep001") == ("km_titleA", 1)
    assert parse_record_id("km_titleB_ep042") == ("km_titleB", 42)
    # 매칭 실패 → fallback
    assert parse_record_id("not_matching_format") == ("not_matching_format", None)


def test_episode_intensity_demo_e2e_on_fixture(tmp_path):
    """e2e: fixture → intensity → demo HTML. raw text 노출 0."""
    fixture = ROOT / "tests/fixtures/annotation_public_safe"
    raw = fixture / "synopsis_raw_demo"
    outputs = fixture / "annotation_outputs_demo"
    if not (raw.exists() and outputs.exists()):
        pytest.skip("fixture missing")

    # 1. feature matrix (skip normalize since intensity demo doesn't need synopsis)
    feat = tmp_path / "feat.csv"
    rc = _run([str(BUILD_MAT_SCRIPT), "--input", str(outputs), "--output", str(feat)])
    assert rc.returncode == 0
    # 2. reliability
    rel = tmp_path / "rel.json"
    rc = _run([str(BUILD_REL_SCRIPT), "--features", str(feat), "--output", str(rel)])
    assert rc.returncode == 0
    # 3. profiles
    profiles = tmp_path / "profiles.json"
    rc = _run([str(BUILD_PROFILES),
                "--reliability", str(rel),
                "--genres", "korean_morning_melodrama",
                "--output", str(profiles)])
    assert rc.returncode == 0, rc.stderr
    # 4. intensity
    intensity = tmp_path / "intensity.json"
    rc = _run([str(RUN_INTENSITY),
                "--feature-matrix", str(feat),
                "--profiles", str(profiles),
                "--reliability", str(rel),
                "--output", str(intensity)])
    assert rc.returncode == 0, rc.stderr
    # 5. demo
    demo_dir = tmp_path / "demo_episode_intensity"
    rc = _run([str(BUILD_INTENSITY_DEMO),
                "--intensity", str(intensity),
                "--output", str(demo_dir)])
    assert rc.returncode == 0, rc.stderr

    # 산출 3종
    html = (demo_dir / "index.html").read_text(encoding="utf-8")
    md = (demo_dir / "intensity.md").read_text(encoding="utf-8")
    json_mirror = (demo_dir / "episode_intensity.json").read_text(encoding="utf-8")

    # synopsis_text 노출 0 — 모든 layer
    for s in (html, md, json_mirror):
        assert "synopsis_text" not in s

    # data_source 표기 (phase3_pilot or rulebook_only banner 둘 중 하나)
    assert "phase3_pilot" in html or "rulebook_only" in html or "Phase 3.0" in html
    # arc 시각화 존재
    assert "arc-bar" in html
    # title × genre 그룹 — fixture는 titleA, titleB 두 개
    assert "km_titleA" in html
    assert "km_titleB" in html
    # KEEP feature 4개 표시
    assert "kept_features" in html
    # audit row
    assert "raw_text_used" in html
    assert "model.trained" in html
    # self-contained — 외부 CDN/<script src> 0
    assert "<script src=" not in html.lower()
    # 한국어 Plan §22.2 메시지
    assert "Episode Intensity" in html


def test_episode_intensity_demo_exit_2_on_missing(tmp_path):
    rc = _run([str(BUILD_INTENSITY_DEMO),
                "--intensity", str(tmp_path / "missing.json"),
                "--output", str(tmp_path / "out")])
    assert rc.returncode == 2


# ---------------------------------------------------------------------------
# 10. Phase 3.05 — score_breakdown 정직성 (Step 1)
# ---------------------------------------------------------------------------

def test_compute_compatibility_detail_axis_and_pressure():
    """Phase 3.05 — axis_match / pressure_overlap 분리 산출."""
    from engine.observer.flesh_baseline import compute_compatibility_detail
    from engine.observer.genre_profile import GenreProfile
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="x",
        dominant_pressures=("authority_vigilance", "social_stigma"),
    )
    profile = GenreProfile(
        schema_version="genre_profile_v1", genre_id="km",
        feature_weights={},
        compatible_conflict_axes=("loyalty_vs_survival",),
        compatible_pressures=("authority_vigilance",),
    )
    score, reasons, components = compute_compatibility_detail(seed, profile)
    # axis match = 0.5
    assert components["axis_match"] == 0.5
    # 1/2 pressures matched → 0.5 * 0.5 = 0.25
    assert components["pressure_overlap"] == 0.25
    # total
    assert score == 0.75


def test_recommend_seed_rulebook_only_score_breakdown():
    """Phase 3.05 — rulebook_only mode에서도 score_breakdown 항상 채워짐."""
    from engine.observer.flesh_baseline import recommend_seed
    from engine.observer.genre_profile import GenreProfile
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="x",
        dominant_pressures=("authority_vigilance",),
    )
    profile = GenreProfile(
        schema_version="genre_profile_v1", genre_id="km",
        feature_weights={"x": 1.0},
        compatible_conflict_axes=("loyalty_vs_survival",),
        compatible_pressures=("authority_vigilance",),
    )
    rec = recommend_seed(seed, profile)  # annotation_features=None → rulebook_only
    bd = rec.score_breakdown
    # Phase 3.05 acceptance — 빈 dict 0건
    assert bd != {}
    # 핵심 필드 모두 존재
    assert bd["mode"] == "rulebook_only"
    assert bd["annotation_score"] is None  # rulebook_only → null
    assert bd["annotation_components"] == {}
    assert bd["axis_match"] == 0.5
    assert bd["pressure_overlap"] == 0.5
    assert bd["compatibility_score"] == 1.0
    assert bd["final_score"] == 1.0


def test_recommend_seed_annotation_blended_score_breakdown():
    """Phase 3.05 — annotation 있을 때 mode=annotation_blended + annotation_score 채워짐."""
    from engine.observer.flesh_baseline import recommend_seed
    from engine.observer.genre_profile import GenreProfile
    from engine.observer.universal_story_seed import UniversalStorySeed
    seed = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="loyalty_vs_survival",
        main_role="protagonist", main_archetype="x",
        dominant_pressures=("authority_vigilance",),
    )
    profile = GenreProfile(
        schema_version="genre_profile_v1", genre_id="km",
        feature_weights={"silence_or_avoidance": 1.0},
        compatible_conflict_axes=("loyalty_vs_survival",),
        compatible_pressures=("authority_vigilance",),
    )
    rec = recommend_seed(
        seed, profile,
        annotation_features={"silence_or_avoidance": 5},
    )
    bd = rec.score_breakdown
    assert bd["mode"] == "annotation_blended"
    assert isinstance(bd["annotation_score"], float)
    assert bd["annotation_score"] == 1.0  # 5/5 * weight 1.0
    assert "silence_or_avoidance" in bd["annotation_components"]
    assert bd["compatibility_score"] == 1.0
    # 50/50 blend → 1.0
    assert bd["final_score"] == 1.0


def test_recommendation_to_dict_serializes_none_in_breakdown():
    """Phase 3.05 — to_dict에서 None / nested dict 모두 직렬화 가능."""
    from engine.observer.flesh_baseline import FleshRecommendation
    rec = FleshRecommendation(
        source_seed_id="S01", genre_id="km", score=1.0,
        fit_label="strong_fit", reason_features=(),
        score_breakdown={
            "axis_match": 0.5,
            "pressure_overlap": 0.5,
            "compatibility_score": 1.0,
            "annotation_score": None,
            "annotation_components": {},
            "final_score": 1.0,
            "mode": "rulebook_only",
        },
    )
    d = rec.to_dict()
    bd = d["score_breakdown"]
    assert bd["annotation_score"] is None
    assert bd["mode"] == "rulebook_only"
    assert bd["axis_match"] == 0.5
    # JSON 직렬화 테스트
    assert json.dumps(d, ensure_ascii=False)


def test_run_flesh_baseline_no_empty_score_breakdown_on_deployed(tmp_path):
    """Phase 3.05 acceptance — deployed prep output의 모든 recommendation에 non-empty score_breakdown."""
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()
    profiles = tmp_path / "profiles.json"
    rc = _run([
        str(BUILD_PROFILES),
        "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
        "--output", str(profiles),
        "--allow-rulebook-only",
    ])
    assert rc.returncode == 0
    out = tmp_path / "baseline.json"
    rc = _run([
        str(RUN_BASELINE),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--profiles", str(profiles),
        "--output", str(out),
    ])
    assert rc.returncode == 0
    d = json.loads(out.read_text(encoding="utf-8"))
    # 모든 recommendation이 non-empty score_breakdown
    for rec in d["recommendations"]:
        bd = rec["score_breakdown"]
        assert bd, f"empty score_breakdown for {rec['source_seed_id']} × {rec['genre_id']}"
        assert "mode" in bd
        assert bd["mode"] == "rulebook_only"  # rulebook_only profiles
        assert bd["annotation_score"] is None
        assert "compatibility_score" in bd
        assert "final_score" in bd


def test_demo_html_displays_rulebook_only_label(tmp_path):
    """Phase 3.05 — rulebook_only일 때 HTML에 (rulebook-only) 명시."""
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()
    # 1. profiles + baseline
    profiles = tmp_path / "profiles.json"
    _run([str(BUILD_PROFILES),
          "--genres", "korean_morning_melodrama",
          "--output", str(profiles),
          "--allow-rulebook-only"])
    baseline = tmp_path / "baseline.json"
    _run([str(RUN_BASELINE),
          "--skeleton", str(DEPLOYED_SKELETON),
          "--profiles", str(profiles),
          "--output", str(baseline)])
    # 2. demo
    demo_dir = tmp_path / "demo"
    rc = _run([str(BUILD_DEMO),
                "--skeleton", str(DEPLOYED_SKELETON),
                "--baseline", str(baseline),
                "--output", str(demo_dir)])
    assert rc.returncode == 0, rc.stderr
    html = (demo_dir / "index.html").read_text(encoding="utf-8")
    md = (demo_dir / "baseline.md").read_text(encoding="utf-8")
    # rulebook-only 명시
    assert "rulebook-only" in html
    assert "rulebook-only" in md
    # data-backed처럼 보이지 않음 — prep banner 강화
    assert "Prep mode" in html
    # score_breakdown 표시
    assert "compatibility_score" in html or "compatibility=" in html
    # JSON에 mode 필드
    json_mirror = (demo_dir / "flesh_baseline_output.json").read_text(encoding="utf-8")
    assert "rulebook_only" in json_mirror


# ---------------------------------------------------------------------------
# 11. Phase 3.05 통합 e2e — 4 layer 정직성 검증 (cycle 4)
# ---------------------------------------------------------------------------

def test_phase3_05_integrity_e2e_rulebook_only_path(tmp_path):
    """Phase 3.05 통합 e2e — rulebook_only 경로의 4 layer 정직성.

    검증:
    - (a) JSON layer: score_breakdown 항상 채워짐, mode=rulebook_only, annotation_score=None
    - (b) Demo HTML/MD layer: Prep banner / rulebook-only 병기 / breakdown 표시
    - (c) Validator layer: strict + synopsis 강제 (synopsis 없으면 exit 2)
    - (d) 운영 layer: Operating Guide §9 Deploy Status Matrix 존재
    """
    if not DEPLOYED_SKELETON.exists():
        pytest.skip("deployed skeleton missing")

    # === (a) JSON layer ===
    profiles = tmp_path / "profiles.json"
    rc = _run([
        str(BUILD_PROFILES),
        "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
        "--output", str(profiles),
        "--allow-rulebook-only",
    ])
    assert rc.returncode == 0, rc.stderr

    baseline = tmp_path / "baseline.json"
    rc = _run([
        str(RUN_BASELINE),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--profiles", str(profiles),
        "--output", str(baseline),
    ])
    assert rc.returncode == 0, rc.stderr
    d = json.loads(baseline.read_text(encoding="utf-8"))

    # 모든 recommendation에 비어있지 않은 score_breakdown
    for rec in d["recommendations"]:
        bd = rec["score_breakdown"]
        assert bd, f"empty score_breakdown for {rec['source_seed_id']}"
        # Phase 3.05 4 필수 키
        assert bd["mode"] == "rulebook_only"
        assert bd["annotation_score"] is None
        assert "compatibility_score" in bd
        assert "axis_match" in bd
        assert "pressure_overlap" in bd
        assert "final_score" in bd
        # numeric value 검증
        assert 0.0 <= bd["compatibility_score"] <= 1.0
        assert 0.0 <= bd["final_score"] <= 1.0

    # === (b) Demo HTML/MD layer ===
    demo_dir = tmp_path / "demo"
    rc = _run([
        str(BUILD_DEMO),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--baseline", str(baseline),
        "--output", str(demo_dir),
    ])
    assert rc.returncode == 0, rc.stderr
    html = (demo_dir / "index.html").read_text(encoding="utf-8")
    md = (demo_dir / "baseline.md").read_text(encoding="utf-8")
    # Prep banner + rulebook-only 병기
    assert "Prep mode" in html
    assert "rulebook-only" in html
    assert "rulebook-only" in md
    # breakdown 표시 (HTML)
    assert "compatibility_score" in html or "compatibility=" in html
    assert "mode" in html
    # raw text 노출 0
    for fname in ("index.html", "baseline.md", "flesh_baseline_output.json"):
        assert "synopsis_text" not in (demo_dir / fname).read_text(encoding="utf-8")

    # === (c) Validator layer — strict + synopsis 강제 ===
    fixture = ROOT / "tests/fixtures/annotation_public_safe"
    outputs = fixture / "annotation_outputs_demo"
    if not outputs.exists():
        pytest.skip("fixture outputs missing")
    # synopsis 없이 strict → exit 2
    rc = _run([str(VAL_OUT_SCRIPT),
                "--input", str(outputs),
                "--strict"])
    assert rc.returncode == 2
    assert "synopsis" in rc.stderr.lower()

    # === (d) 운영 layer — Operating Guide Deploy Status Matrix ===
    op_guide = ROOT / "docs/plans/PHASE_3_0_PIPELINE_OPERATING_GUIDE.md"
    op_text = op_guide.read_text(encoding="utf-8")
    assert "Deploy Status Matrix" in op_text
    assert "deployed-prep" in op_text
    assert "script-only" in op_text
    assert "generated-after-approval" in op_text
    # 파일 요청 원칙
    assert "파일 요청 원칙" in op_text or "요청 우선순위" in op_text


def test_phase3_05_integrity_e2e_phase3_pilot_path(tmp_path):
    """Phase 3.05 통합 e2e — phase3_pilot (fixture annotation) 경로의 정직성.

    검증:
    - score_breakdown.mode = "annotation_blended" (annotation 적용됨)
    - annotation_score 채워짐 (None이 아님)
    - hallucination report 3 layer 분리 존재 (valid_files_only / all_files / invalid_files)
    """
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()
    fixture = ROOT / "tests/fixtures/annotation_public_safe"
    raw = fixture / "synopsis_raw_demo"
    outputs = fixture / "annotation_outputs_demo"
    if not (raw.exists() and outputs.exists()):
        pytest.skip("fixture missing")

    # 1. normalize + feature_matrix + reliability + profiles (phase3_pilot)
    norm = tmp_path / "norm.jsonl"
    _run([str(NORM_SCRIPT), "--input", str(raw), "--output", str(norm)])
    feat = tmp_path / "feat.csv"
    _run([str(BUILD_MAT_SCRIPT), "--input", str(outputs), "--output", str(feat)])
    rel = tmp_path / "rel.json"
    _run([str(BUILD_REL_SCRIPT), "--features", str(feat), "--output", str(rel)])
    profiles = tmp_path / "profiles.json"
    _run([str(BUILD_PROFILES),
          "--reliability", str(rel),
          "--genres", "korean_morning_melodrama",
          "--output", str(profiles)])

    # 2. validator strict + synopsis (Phase 3.05 Step 3)
    halluc_report = tmp_path / "halluc.json"
    rc = _run([str(VAL_OUT_SCRIPT),
                "--input", str(outputs),
                "--synopsis", str(norm),
                "--hallucination-report", str(halluc_report),
                "--strict"])
    assert rc.returncode == 0, rc.stderr  # valid fixture: strict 통과
    halluc = json.loads(halluc_report.read_text(encoding="utf-8"))
    # Phase 3.05 Step 4 — 3 layer 모두 존재
    assert "valid_files_only_summary" in halluc
    assert "all_files_summary" in halluc
    assert "invalid_files" in halluc
    # fixture는 모두 valid → invalid_files 0
    assert len(halluc["invalid_files"]) == 0
    # threshold = valid_files_only 기준 PASS
    assert halluc["phase3_threshold_pass"] is True

    # 3. annotation 기반 flesh baseline (phase3_pilot)
    # Note: run_flesh_baseline.py는 현재 annotation_features를 받지 않음 — rulebook_only이므로 직접 engine 호출
    from engine.observer.flesh_baseline import recommend_seed
    from engine.observer.universal_story_seed import UniversalStorySeed
    from engine.observer.genre_profile import load_profiles
    profile_list = load_profiles(profiles)
    assert len(profile_list) == 1
    p = profile_list[0]
    # annotation_features 제공해서 annotation_blended path 검증
    seed = UniversalStorySeed(
        seed_id="S99", conflict_axis_id=p.compatible_conflict_axes[0],
        main_role="protagonist", main_archetype="x",
        dominant_pressures=tuple(p.compatible_pressures[:1]),
    )
    rec = recommend_seed(seed, p, annotation_features={
        f: 4.0 for f in p.feature_weights.keys()
    })
    bd = rec.score_breakdown
    # annotation_blended path 검증
    assert bd["mode"] == "annotation_blended"
    assert isinstance(bd["annotation_score"], float)
    assert bd["annotation_score"] > 0
    assert "annotation_components" in bd
    assert len(bd["annotation_components"]) > 0


def test_phase3_05_no_empty_score_breakdown_anywhere(tmp_path):
    """Phase 3.05 acceptance — *어디에도* 빈 score_breakdown 0건 (No-Go 회피)."""
    from engine.observer.flesh_baseline import recommend_seed
    from engine.observer.universal_story_seed import UniversalStorySeed
    from engine.observer.genre_profile import GenreProfile

    # Worst case: no axis match, no pressure match, no annotation
    seed = UniversalStorySeed(
        seed_id="S01", conflict_axis_id="nonexistent",
        main_role="protagonist", main_archetype="x",
        dominant_pressures=("nonexistent",),
    )
    profile = GenreProfile(
        schema_version="genre_profile_v1", genre_id="g1",
        feature_weights={"f1": 1.0},
        compatible_conflict_axes=("other_axis",),
        compatible_pressures=("other_pressure",),
    )
    rec = recommend_seed(seed, profile)  # annotation_features=None
    # 빈 dict 아님
    assert rec.score_breakdown != {}
    # 모든 필수 키 존재 (값이 0이거나 None이어도)
    bd = rec.score_breakdown
    assert "axis_match" in bd
    assert "pressure_overlap" in bd
    assert "compatibility_score" in bd
    assert "annotation_score" in bd
    assert "annotation_components" in bd
    assert "final_score" in bd
    assert "mode" in bd
    # 값 검증
    assert bd["axis_match"] == 0.0
    assert bd["pressure_overlap"] == 0.0
    assert bd["compatibility_score"] == 0.0
    assert bd["final_score"] == 0.0
    assert bd["mode"] == "rulebook_only"
    assert bd["annotation_score"] is None


# ---------------------------------------------------------------------------
# 12. Phase 3.05 + cycle 5/7 통합 e2e (cycle 9 — 전체 acceptance flow)
# ---------------------------------------------------------------------------

VERIFY_ACCEPTANCE = ROOT / "scripts/data/verify_phase3_0_acceptance.py"


def test_phase3_full_pipeline_with_acceptance_checker(tmp_path):
    """Phase 3.0 + 3.1 + 3.05 + acceptance checker 전체 e2e (cycle 9 통합).

    검증 시나리오:
    1. fixture 기반 normalize + validate + matrix + reliability + profiles 실행
    2. flesh_baseline + episode_intensity + 두 demo 생성
    3. acceptance checker 돌려서 §18 12 항목 상태 확인
    4. pilot 산출물 모두 존재 → AUTO PASS (§18.3 raw 미존재라 FAIL이지만 다른 7개는 PASS)
    5. approval checklist 미체크 → PENDING (§18.1/2)
    6. exit code = 1 (AUTO FAIL §18.3 존재)
    """
    fixture = ROOT / "tests/fixtures/annotation_public_safe"
    raw = fixture / "synopsis_raw_demo"
    outputs = fixture / "annotation_outputs_demo"
    if not (raw.exists() and outputs.exists()):
        pytest.skip("fixture missing")
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()

    # === Phase 3.0 운영 (fixture로 시뮬레이션) ===
    pilot_dir = tmp_path / "phase3_pilot"
    pilot_dir.mkdir()

    # normalize → matrix → reliability
    norm = pilot_dir / "normalized_synopsis.jsonl"
    rc = _run([str(NORM_SCRIPT), "--input", str(raw), "--output", str(norm)])
    assert rc.returncode == 0

    annotation_inputs = pilot_dir / "annotation_inputs"
    annotation_outputs = pilot_dir / "annotation_outputs"
    annotation_inputs.mkdir()
    annotation_outputs.mkdir()
    # fixture annotation_outputs를 pilot_dir에 복사 (Step 5 시뮬레이션)
    import shutil
    for f in outputs.glob("*.json"):
        shutil.copy(f, annotation_outputs / f.name)
    # annotation_inputs는 비어있어도 디렉토리만 존재하면 §18.5 PASS
    (annotation_inputs / "placeholder.json").write_text("{}", encoding="utf-8")

    # validate outputs (Phase 3.05 strict + report 3 layer)
    halluc_report = pilot_dir / "reports" / "hallucination_report.json"
    halluc_report.parent.mkdir(parents=True, exist_ok=True)
    rc = _run([str(VAL_OUT_SCRIPT),
                "--input", str(annotation_outputs),
                "--synopsis", str(norm),
                "--hallucination-report", str(halluc_report),
                "--strict"])
    assert rc.returncode == 0, rc.stderr

    # feature matrix
    feat_csv = pilot_dir / "features" / "feature_matrix.csv"
    feat_csv.parent.mkdir(parents=True, exist_ok=True)
    rc = _run([str(BUILD_MAT_SCRIPT),
                "--input", str(annotation_outputs),
                "--output", str(feat_csv)])
    assert rc.returncode == 0

    # reliability
    rel = pilot_dir / "reports" / "reliability.json"
    rc = _run([str(BUILD_REL_SCRIPT),
                "--features", str(feat_csv),
                "--output", str(rel)])
    assert rc.returncode == 0

    # === Phase 3.1 baseline (rulebook_only — but phase3_pilot reliability available) ===
    profiles = pilot_dir / "genre_profiles.json"
    rc = _run([str(BUILD_PROFILES),
                "--reliability", str(rel),
                "--genres", "korean_morning_melodrama",
                "--output", str(profiles)])
    assert rc.returncode == 0, rc.stderr

    baseline = pilot_dir / "flesh_baseline_output.json"
    rc = _run([str(RUN_BASELINE),
                "--skeleton", str(DEPLOYED_SKELETON),
                "--profiles", str(profiles),
                "--output", str(baseline)])
    assert rc.returncode == 0

    # === Acceptance checker (cycle 5+7) ===
    accept_report = pilot_dir / "reports" / "acceptance_check.json"
    rc = _run([str(VERIFY_ACCEPTANCE),
                "--pilot-dir", str(pilot_dir),
                "--raw-private-dir", str(raw),       # fixture가 raw 역할 — 10 episodes
                # approval doc — 실제 doc (현재 0/7 unchecked)
                # data card / pilot report 미존재 → HEURISTIC FAIL
                "--data-card", str(tmp_path / "no_card.md"),
                "--pilot-report", str(tmp_path / "no_report.md"),
                "--output", str(accept_report)])
    # 결과 분석
    data = json.loads(accept_report.read_text(encoding="utf-8"))
    summary = data["summary"]

    # === Phase 3.0 §18 acceptance 매핑 검증 ===
    by_id = {c["item_id"]: c for c in data["checks"]}

    # §18.1: PENDING (실제 checklist 0/7 unchecked)
    assert by_id[1]["status"] == "PENDING"
    assert by_id[1]["category"] == "AUTO"
    # §18.2: PENDING (checklist #2 unchecked)
    assert by_id[2]["status"] == "PENDING"
    # §18.3: PASS (fixture 10 episodes)
    assert by_id[3]["status"] == "PASS"
    # §18.4: PASS or FAIL depending on .gitignore
    assert by_id[4]["status"] in ("PASS", "FAIL")
    # §18.5: PASS (annotation_inputs/ exists with placeholder)
    assert by_id[5]["status"] == "PASS"
    # §18.6: PASS (20 annotation outputs)
    assert by_id[6]["status"] == "PASS"
    # §18.7: PASS (no invalid files in hallucination report)
    assert by_id[7]["status"] == "PASS"
    # §18.8: PASS (fixture quotes all substrings → 0 hallucination)
    assert by_id[8]["status"] == "PASS"
    # §18.9: PASS (≥4 KEEP features in reliability)
    assert by_id[9]["status"] == "PASS"
    # §18.10: PASS (KEEP/REVISE/DROP all present)
    assert by_id[10]["status"] == "PASS"
    # §18.11: FAIL (no data card)
    assert by_id[11]["status"] == "FAIL"
    # §18.12: FAIL (no pilot report)
    assert by_id[12]["status"] == "FAIL"

    # AUTO 통계
    # §18.1/2 PENDING + §18.3-10 모두 PASS → auto_pass = 8, auto_pending = 2
    assert summary["auto_pending"] == 2
    assert summary["auto_pass"] >= 7  # §18.4 .gitignore 의존
    assert summary["heuristic_fail"] == 2  # §18.11/12 모두 FAIL

    # 핵심 검증: pilot 실행 후 acceptance check가 *진짜 상태* 정확 반영
    # (cycle 5+7+9 통합 — fixture로 시뮬한 pilot이 12 항목 매트릭스로 표현됨)
    # exit code = 0 (AUTO PASS 또는 PENDING) 또는 1 (§18.4 FAIL이면)
    if by_id[4]["status"] == "PASS":
        assert rc.returncode == 0  # PENDING은 FAIL 아님 (cycle 7)
    else:
        assert rc.returncode == 1


def test_phase3_acceptance_with_full_approval_reaches_auto_10_pass(tmp_path):
    """approval 7/7 ☑ + pilot 모든 산출 → AUTO 10/10 PASS (cycle 7 PENDING → PASS 전환)."""
    pilot_dir = tmp_path / "pilot"
    pilot_dir.mkdir()
    raw = tmp_path / "raw"
    raw.mkdir()
    # 10 raw synopses (§18.3 PASS)
    for i in range(1, 11):
        (raw / f"titleX_ep{i:02d}.json").write_text("{}", encoding="utf-8")
    # annotation_inputs/outputs (§18.5/6)
    (pilot_dir / "annotation_inputs").mkdir()
    (pilot_dir / "annotation_inputs" / "a.json").write_text("{}", encoding="utf-8")
    (pilot_dir / "annotation_outputs").mkdir()
    (pilot_dir / "annotation_outputs" / "a.json").write_text("{}", encoding="utf-8")
    # reports (§18.7-10)
    (pilot_dir / "reports").mkdir()
    (pilot_dir / "reports" / "hallucination_report.json").write_text(json.dumps({
        "invalid_files": [],
        "valid_files_only_summary": {
            "n_files": 10, "hallucination_rate": 0.0, "phase3_threshold_pass": True,
        },
    }), encoding="utf-8")
    (pilot_dir / "reports" / "reliability.json").write_text(json.dumps({
        "summary": {"keep": ["f1", "f2", "f3", "f4"], "revise": [], "drop": []}
    }), encoding="utf-8")

    # approval checklist 7/7 ☑
    approval = tmp_path / "approval.md"
    approval.write_text(
        "## 1. 5+2\n\n"
        "### ☑ 1. fetch\n\n"
        "### ☑ 2. ToS\n\n"
        "### ☑ 3. LLM API\n\n"
        "### ☑ 4. 비용\n\n"
        "### ☑ 5. 저장\n\n"
        "### ☑ 6. (보조) repo\n\n"
        "### ☑ 7. (보조) mini pilot\n",
        encoding="utf-8",
    )

    rc = _run([str(VERIFY_ACCEPTANCE),
                "--pilot-dir", str(pilot_dir),
                "--raw-private-dir", str(raw),
                "--approval-doc", str(approval),
                "--data-card", str(tmp_path / "no_card.md"),
                "--pilot-report", str(tmp_path / "no_report.md"),
                "--gitignore", str(tmp_path / "no_gi"),  # raw가 outside repo여야 §18.4 PASS
                "--output", str(tmp_path / "report.json")])
    assert rc.returncode == 0, rc.stdout + rc.stderr  # AUTO 모두 PASS

    data = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    summary = data["summary"]
    # AUTO 10/10 PASS (cycle 5 8개 + cycle 7 격상 2개)
    assert summary["auto_pass"] == 10
    assert summary["auto_fail"] == 0
    assert summary["auto_pending"] == 0
    # §18.1+2 모두 PASS (approval 7/7 ☑)
    by_id = {c["item_id"]: c for c in data["checks"]}
    assert by_id[1]["status"] == "PASS"
    assert by_id[1]["category"] == "AUTO"
    assert by_id[2]["status"] == "PASS"
    assert by_id[2]["category"] == "AUTO"


# ---------------------------------------------------------------------------
# Phase 3.1 §22.3 Target C — Adaptation Recommendation (cycle 17, 2026-05-11)
# ---------------------------------------------------------------------------

def test_adaptation_recommendation_groups_by_seed_with_top_k():
    """Target C: seed별 grouped + ranked top-K (default 3)."""
    from engine.observer.adaptation_recommendation import (
        run_adaptation_recommendation,
        ADAPTATION_RECOMMENDATION_VERSION,
    )
    from engine.observer.genre_profile import GenreProfile

    sk = _make_skeleton_with_two_seeds()
    profiles = [
        GenreProfile(
            schema_version="genre_profile_v1", genre_id="km",
            feature_weights={"conflict_intensity_peak": 1.0},
            compatible_conflict_axes=("loyalty_vs_survival",),
            compatible_pressures=("authority_vigilance",),
        ),
        GenreProfile(
            schema_version="genre_profile_v1", genre_id="jp",
            feature_weights={"silence_or_avoidance": 1.0},
            compatible_conflict_axes=("uncertainty_vs_commitment",),
            compatible_pressures=("confusion",),
        ),
    ]
    out = run_adaptation_recommendation(sk, profiles, top_k=3)
    assert out.schema_version == ADAPTATION_RECOMMENDATION_VERSION
    # 2 seeds → 2 grouped recommendations
    assert len(out.recommendations) == 2
    seed_ids = {r.source_seed_id for r in out.recommendations}
    assert seed_ids == {"S01", "S02"}
    # 각 seed별 modes 수 ≤ top_k
    for rec in out.recommendations:
        assert len(rec.recommended_modes) <= 3


def test_adaptation_recommendation_ranks_by_score_descending():
    """Top-K은 score 내림차순 정렬."""
    from engine.observer.adaptation_recommendation import (
        run_adaptation_recommendation,
    )
    from engine.observer.genre_profile import GenreProfile

    sk = _make_skeleton_with_two_seeds()
    profiles = [
        GenreProfile(
            schema_version="genre_profile_v1", genre_id="km",
            feature_weights={"conflict_intensity_peak": 1.0},
            compatible_conflict_axes=("loyalty_vs_survival",),
            compatible_pressures=("authority_vigilance",),
        ),
        GenreProfile(
            schema_version="genre_profile_v1", genre_id="jp",
            feature_weights={"silence_or_avoidance": 1.0},
            compatible_conflict_axes=("uncertainty_vs_commitment",),
            compatible_pressures=("confusion",),
        ),
    ]
    out = run_adaptation_recommendation(sk, profiles, top_k=3)
    for rec in out.recommendations:
        scores = [m.score for m in rec.recommended_modes]
        assert scores == sorted(scores, reverse=True), \
            f"seed {rec.source_seed_id} modes not sorted: {scores}"
    # S01의 1순위는 km (axis match)
    s01 = next(r for r in out.recommendations if r.source_seed_id == "S01")
    assert s01.recommended_modes[0].genre_id == "km"
    # S02의 1순위는 jp (axis match)
    s02 = next(r for r in out.recommendations if r.source_seed_id == "S02")
    assert s02.recommended_modes[0].genre_id == "jp"


def test_adaptation_recommendation_min_score_filter():
    """min_score 이하 모드는 제외."""
    from engine.observer.adaptation_recommendation import (
        run_adaptation_recommendation,
    )
    from engine.observer.genre_profile import GenreProfile

    sk = _make_skeleton_with_two_seeds()
    profiles = [
        GenreProfile(
            schema_version="genre_profile_v1", genre_id="km",
            feature_weights={"f1": 1.0},
            compatible_conflict_axes=("loyalty_vs_survival",),
            compatible_pressures=("authority_vigilance",),
        ),
        GenreProfile(
            schema_version="genre_profile_v1", genre_id="jp",
            feature_weights={"f2": 1.0},
            compatible_conflict_axes=("uncertainty_vs_commitment",),
            compatible_pressures=("confusion",),
        ),
    ]
    # min_score=0.6으로 mismatched seed-genre 제외
    out = run_adaptation_recommendation(sk, profiles, min_score=0.6)
    for rec in out.recommendations:
        for mode in rec.recommended_modes:
            assert mode.score >= 0.6


def test_adaptation_recommendation_to_dict_serializable():
    """Output JSON 직렬화 가능 + §22.3 schema 필드 보유."""
    import json
    from engine.observer.adaptation_recommendation import (
        run_adaptation_recommendation,
    )
    from engine.observer.genre_profile import GenreProfile

    sk = _make_skeleton_with_two_seeds()
    profile = GenreProfile(
        schema_version="genre_profile_v1", genre_id="km",
        feature_weights={"f1": 1.0},
        compatible_conflict_axes=("loyalty_vs_survival",),
        compatible_pressures=("authority_vigilance",),
    )
    out = run_adaptation_recommendation(sk, [profile])
    payload = out.to_dict()
    # JSON 직렬화 통과
    serialized = json.dumps(payload, ensure_ascii=False)
    assert "adaptation_recommendation_v1" in serialized
    # §22.3 spec 필드
    assert payload["schema_version"] == "adaptation_recommendation_v1"
    assert "recommendations" in payload
    assert payload["top_k"] == 3
    assert payload["model"]["trained"] is False
    assert payload["audit"]["raw_text_used"] is False
    assert payload["calibration_status"] == "uncalibrated_phase3_placeholder"
    # 첫 seed의 recommended_modes 항목 검사
    first = payload["recommendations"][0]
    assert "source_seed_id" in first
    assert "recommended_modes" in first
    if first["recommended_modes"]:
        mode = first["recommended_modes"][0]
        assert "genre_id" in mode
        assert "score" in mode
        assert "fit_label" in mode
        assert "reason" in mode
        assert "mode" in mode  # rulebook_only or annotation_blended


def test_adaptation_recommendation_mode_field_reflects_annotation_state():
    """annotation_features 없으면 mode=rulebook_only, 있으면 annotation_blended."""
    from engine.observer.adaptation_recommendation import (
        run_adaptation_recommendation,
    )
    from engine.observer.genre_profile import GenreProfile

    sk = _make_skeleton_with_two_seeds()
    profile = GenreProfile(
        schema_version="genre_profile_v1", genre_id="km",
        feature_weights={"f1": 1.0},
        compatible_conflict_axes=("loyalty_vs_survival",),
        compatible_pressures=("authority_vigilance",),
    )
    # rulebook_only mode
    out_rb = run_adaptation_recommendation(sk, [profile])
    for rec in out_rb.recommendations:
        for mode in rec.recommended_modes:
            assert mode.mode == "rulebook_only"
    # annotation_blended mode
    out_ann = run_adaptation_recommendation(
        sk, [profile],
        annotation_features_by_seed={"S01": {"f1": 4.0}, "S02": {"f1": 2.0}},
    )
    for rec in out_ann.recommendations:
        for mode in rec.recommended_modes:
            assert mode.mode == "annotation_blended"


def test_adaptation_recommendation_no_external_fetch_or_raw_text():
    """Phase 3.05 정직성: model_trained=False / audit_raw_text_used=False / calibration_status."""
    from engine.observer.adaptation_recommendation import (
        run_adaptation_recommendation,
    )
    from engine.observer.genre_profile import GenreProfile

    sk = _make_skeleton_with_two_seeds()
    profile = GenreProfile(
        schema_version="genre_profile_v1", genre_id="km",
        feature_weights={"f1": 1.0},
        compatible_conflict_axes=("loyalty_vs_survival",),
        compatible_pressures=("authority_vigilance",),
    )
    out = run_adaptation_recommendation(sk, [profile])
    assert out.model_trained is False
    assert out.audit_raw_text_used is False
    assert out.audit_evidence_preserved is True
    assert out.calibration_status == "uncalibrated_phase3_placeholder"


# ---------------------------------------------------------------------------
# Phase 3.1 §22.3 Target C — CLI: run_adaptation_recommendation.py (cycle 18)
# ---------------------------------------------------------------------------

RUN_ADAPT = ROOT / "scripts/narrative/run_adaptation_recommendation.py"


def test_run_adaptation_recommendation_help():
    rc = _run([str(RUN_ADAPT), "--help"])
    assert rc.returncode == 0


def test_run_adaptation_recommendation_e2e_on_deployed(tmp_path):
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()

    # 1. build profiles (rulebook-only mode)
    profiles_path = tmp_path / "profiles.json"
    rc = _run([
        str(BUILD_PROFILES),
        "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
        "--output", str(profiles_path),
        "--allow-rulebook-only",
    ])
    assert rc.returncode == 0, rc.stderr

    # 2. run adaptation recommendation
    out = tmp_path / "adaptation.json"
    rc = _run([
        str(RUN_ADAPT),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--profiles", str(profiles_path),
        "--output", str(out),
        "--top-k", "3",
    ])
    assert rc.returncode == 0, rc.stderr
    d = json.loads(out.read_text(encoding="utf-8"))
    # §22.3 schema 검증
    assert d["schema_version"] == "adaptation_recommendation_v1"
    assert d["top_k"] == 3
    assert d["model"]["trained"] is False
    assert d["audit"]["raw_text_used"] is False
    assert d["calibration_status"] == "uncalibrated_phase3_placeholder"
    # seed별 grouped
    assert isinstance(d["recommendations"], list)
    assert len(d["recommendations"]) >= 1
    for rec in d["recommendations"]:
        assert "source_seed_id" in rec
        assert "recommended_modes" in rec
        # top-K 제한 준수
        assert len(rec["recommended_modes"]) <= 3
        # score 내림차순
        scores = [m["score"] for m in rec["recommended_modes"]]
        assert scores == sorted(scores, reverse=True)
        # 각 mode에 §22.3 필드
        for mode in rec["recommended_modes"]:
            assert "genre_id" in mode
            assert "score" in mode
            assert "fit_label" in mode
            assert "reason" in mode
            assert "mode" in mode
    # raw text 노출 0
    s = json.dumps(d, ensure_ascii=False)
    assert "synopsis_text" not in s


def test_run_adaptation_recommendation_exit_2_on_missing_skeleton(tmp_path):
    rc = _run([
        str(RUN_ADAPT),
        "--skeleton", str(tmp_path / "missing.json"),
        "--profiles", str(tmp_path / "p.json"),
        "--output", str(tmp_path / "out.json"),
    ])
    assert rc.returncode == 2


def test_run_adaptation_recommendation_rejects_invalid_top_k(tmp_path):
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()
    profiles_path = tmp_path / "profiles.json"
    _run([
        str(BUILD_PROFILES),
        "--genres", "korean_morning_melodrama",
        "--output", str(profiles_path),
        "--allow-rulebook-only",
    ])
    rc = _run([
        str(RUN_ADAPT),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--profiles", str(profiles_path),
        "--output", str(tmp_path / "out.json"),
        "--top-k", "0",
    ])
    assert rc.returncode == 2


# ---------------------------------------------------------------------------
# Phase 3.1 §22.3 Target C — Demo builder (cycle 19)
# ---------------------------------------------------------------------------

BUILD_ADAPT_DEMO = ROOT / "scripts/narrative/build_adaptation_recommendation_demo.py"


def test_build_adaptation_recommendation_demo_help():
    rc = _run([str(BUILD_ADAPT_DEMO), "--help"])
    assert rc.returncode == 0


def test_build_adaptation_recommendation_demo_e2e(tmp_path):
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()

    profiles_path = tmp_path / "profiles.json"
    rc = _run([
        str(BUILD_PROFILES),
        "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
        "--output", str(profiles_path),
        "--allow-rulebook-only",
    ])
    assert rc.returncode == 0, rc.stderr

    rec_path = tmp_path / "adaptation.json"
    rc = _run([
        str(RUN_ADAPT),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--profiles", str(profiles_path),
        "--output", str(rec_path),
    ])
    assert rc.returncode == 0, rc.stderr

    demo_dir = tmp_path / "demo"
    rc = _run([
        str(BUILD_ADAPT_DEMO),
        "--recommendation", str(rec_path),
        "--output", str(demo_dir),
    ])
    assert rc.returncode == 0, rc.stderr

    html_path = demo_dir / "index.html"
    md_path = demo_dir / "recommendations.md"
    json_mirror = demo_dir / "adaptation_recommendation.json"
    assert html_path.exists()
    assert md_path.exists()
    assert json_mirror.exists()

    html = html_path.read_text(encoding="utf-8")
    # Phase 3.05 정직성 4 layer — HTML banners
    assert "Non-Claims" in html
    assert "uncalibrated_phase3_placeholder" in html
    assert "Rule #14" in html
    assert "candidate" in html.lower()
    # raw text 노출 0
    assert "synopsis_text" not in html
    # schema 표시
    assert "adaptation_recommendation_v1" in html
    # 외부 CDN 0 (self-contained)
    assert "<script src=" not in html
    assert "https://" not in html or "://cdn." not in html

    md = md_path.read_text(encoding="utf-8")
    assert "Non-Claims" in md
    assert "Target C" in md
    assert "uncalibrated_phase3_placeholder" in md
    # 재현 명령
    assert "run_adaptation_recommendation.py" in md
    assert "build_adaptation_recommendation_demo.py" in md


def test_build_adaptation_recommendation_demo_exit_2_on_missing():
    rc = _run([
        str(BUILD_ADAPT_DEMO),
        "--recommendation", "/nonexistent/path.json",
        "--output", "/tmp/out",
    ])
    assert rc.returncode == 2


def test_deployed_demo_html_is_clean():
    """Smoke test: deployed `docs/portfolio/demo_adaptation_recommendation/index.html` 검사."""
    deployed = ROOT / "docs" / "portfolio" / "demo_adaptation_recommendation" / "index.html"
    if not deployed.exists():
        pytest.skip("Deployed demo not present (run build_adaptation_recommendation_demo.py first)")
    html = deployed.read_text(encoding="utf-8")
    assert "Non-Claims" in html
    assert "adaptation_recommendation_v1" in html
    assert "uncalibrated_phase3_placeholder" in html
    assert "synopsis_text" not in html  # raw 노출 금지


# ---------------------------------------------------------------------------
# Phase 3.1 Cross-Target Integration (cycle 21, 2026-05-11)
# - Target A (flesh_baseline) + Target C (adaptation_recommendation) consistency:
#   둘 다 동일한 recommend_seed()를 호출하므로, seed별 top-1 genre가 *반드시*
#   일치해야 한다. cross-target invariant.
# ---------------------------------------------------------------------------


def test_target_a_and_c_top_recommendation_agree():
    """Target A flat (seed × profile) score top = Target C ranked top-1 per seed.

    invariant: 두 Target은 동일한 `recommend_seed()`를 사용하므로 seed별 top-1
    genre가 일치해야 한다. 일치하지 않으면 *Target C의 grouping 버그* 또는
    *Target A의 정렬 가정 오류*를 의미.
    """
    from engine.observer.adaptation_recommendation import (
        run_adaptation_recommendation,
    )
    from engine.observer.flesh_baseline import run_flesh_baseline
    from engine.observer.genre_profile import GenreProfile

    sk = _make_skeleton_with_two_seeds()
    profiles = [
        GenreProfile(
            schema_version="genre_profile_v1", genre_id="km",
            feature_weights={"f1": 1.0},
            compatible_conflict_axes=("loyalty_vs_survival",),
            compatible_pressures=("authority_vigilance",),
        ),
        GenreProfile(
            schema_version="genre_profile_v1", genre_id="jp",
            feature_weights={"f2": 1.0},
            compatible_conflict_axes=("uncertainty_vs_commitment",),
            compatible_pressures=("confusion",),
        ),
    ]

    # Target A: flat (seed × profile)
    a = run_flesh_baseline(sk, profiles)
    # Target C: seed별 ranked top-K
    c = run_adaptation_recommendation(sk, profiles, top_k=3)

    # Target A에서 seed별 top genre 추출 (score 내림차순 1순위)
    a_top_by_seed: dict[str, str] = {}
    for rec in sorted(a.recommendations, key=lambda r: -r.score):
        if rec.source_seed_id not in a_top_by_seed:
            a_top_by_seed[rec.source_seed_id] = rec.genre_id

    # Target C에서 seed별 top genre 추출 (recommended_modes[0])
    c_top_by_seed: dict[str, str] = {}
    for rec in c.recommendations:
        if rec.recommended_modes:
            c_top_by_seed[rec.source_seed_id] = rec.recommended_modes[0].genre_id

    # invariant
    assert a_top_by_seed == c_top_by_seed, (
        f"Target A/C inconsistency: A={a_top_by_seed}, C={c_top_by_seed}"
    )


def test_target_a_and_c_agree_with_annotation_features():
    """annotation_blended mode에서도 Target A/C top-1 일치 invariant."""
    from engine.observer.adaptation_recommendation import (
        run_adaptation_recommendation,
    )
    from engine.observer.flesh_baseline import run_flesh_baseline
    from engine.observer.genre_profile import GenreProfile

    sk = _make_skeleton_with_two_seeds()
    profiles = [
        GenreProfile(
            schema_version="genre_profile_v1", genre_id="km",
            feature_weights={"f1": 1.0},
            compatible_conflict_axes=("loyalty_vs_survival",),
            compatible_pressures=("authority_vigilance",),
        ),
        GenreProfile(
            schema_version="genre_profile_v1", genre_id="jp",
            feature_weights={"f2": 1.0},
            compatible_conflict_axes=("uncertainty_vs_commitment",),
            compatible_pressures=("confusion",),
        ),
    ]
    annot = {"S01": {"f1": 4.0, "f2": 1.0}, "S02": {"f1": 1.0, "f2": 4.0}}

    a = run_flesh_baseline(sk, profiles, annotation_features_by_seed=annot)
    c = run_adaptation_recommendation(
        sk, profiles, annotation_features_by_seed=annot, top_k=3,
    )

    a_top_by_seed: dict[str, str] = {}
    for rec in sorted(a.recommendations, key=lambda r: -r.score):
        if rec.source_seed_id not in a_top_by_seed:
            a_top_by_seed[rec.source_seed_id] = rec.genre_id

    c_top_by_seed: dict[str, str] = {}
    for rec in c.recommendations:
        if rec.recommended_modes:
            c_top_by_seed[rec.source_seed_id] = rec.recommended_modes[0].genre_id

    assert a_top_by_seed == c_top_by_seed
    # Target C 모든 mode가 annotation_blended로 표시
    for rec in c.recommendations:
        for mode in rec.recommended_modes:
            assert mode.mode == "annotation_blended"


# ---------------------------------------------------------------------------
# Phase 3.1 §24 Step 2 — apply_top_recommendation.py bridge (cycle 25)
# Target C recommendation → genre_adapter 연결
# ---------------------------------------------------------------------------

APPLY_TOP_REC = ROOT / "scripts/narrative/apply_top_recommendation.py"


def test_select_modal_top_genre_handles_ties():
    """Tie-break은 알파벳 순 첫 번째."""
    from scripts.narrative.apply_top_recommendation import select_modal_top_genre

    rec = {
        "calibration_status": "uncalibrated_phase3_placeholder",
        "recommendations": [
            {"source_seed_id": "S01", "recommended_modes": [{"genre_id": "z_late", "score": 1.0, "mode": "rulebook_only"}]},
            {"source_seed_id": "S02", "recommended_modes": [{"genre_id": "a_first", "score": 1.0, "mode": "rulebook_only"}]},
            {"source_seed_id": "S03", "recommended_modes": [{"genre_id": "m_mid", "score": 1.0, "mode": "rulebook_only"}]},
        ],
    }
    genre, info = select_modal_top_genre(rec)
    # 3 seeds × 3 genres, 각 count=1 → 동률 → 알파벳 첫번째
    assert info["tie_break_applied"] is True
    assert genre == "a_first"
    assert set(info["tied_candidates"]) == {"a_first", "m_mid", "z_late"}


def test_select_modal_top_genre_picks_most_frequent():
    from scripts.narrative.apply_top_recommendation import select_modal_top_genre

    rec = {
        "calibration_status": "uncalibrated_phase3_placeholder",
        "recommendations": [
            {"source_seed_id": "S01", "recommended_modes": [{"genre_id": "km", "score": 0.9, "mode": "rulebook_only"}]},
            {"source_seed_id": "S02", "recommended_modes": [{"genre_id": "km", "score": 0.8, "mode": "rulebook_only"}]},
            {"source_seed_id": "S03", "recommended_modes": [{"genre_id": "jp", "score": 0.7, "mode": "rulebook_only"}]},
        ],
    }
    genre, info = select_modal_top_genre(rec)
    assert genre == "km"
    assert info["modal_count"] == 2
    assert info["tie_break_applied"] is False
    assert info["all_counts"] == {"km": 2, "jp": 1}


def test_select_modal_top_genre_empty_recommendations():
    from scripts.narrative.apply_top_recommendation import select_modal_top_genre

    rec = {"calibration_status": "uncalibrated", "recommendations": []}
    genre, info = select_modal_top_genre(rec)
    assert genre is None
    assert "reason" in info


def test_apply_top_recommendation_help():
    rc = _run([str(APPLY_TOP_REC), "--help"])
    assert rc.returncode == 0


def test_apply_top_recommendation_e2e_on_deployed(tmp_path):
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()

    profiles_path = tmp_path / "profiles.json"
    rc = _run([
        str(BUILD_PROFILES),
        "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
        "--output", str(profiles_path),
        "--allow-rulebook-only",
    ])
    assert rc.returncode == 0, rc.stderr

    rec_path = tmp_path / "rec.json"
    rc = _run([
        str(RUN_ADAPT),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--profiles", str(profiles_path),
        "--output", str(rec_path),
    ])
    assert rc.returncode == 0, rc.stderr

    adapted_path = tmp_path / "adapted.json"
    rc = _run([
        str(APPLY_TOP_REC),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--recommendation", str(rec_path),
        "--output", str(adapted_path),
    ])
    assert rc.returncode == 0, rc.stderr + rc.stdout
    # stdout에 선택 근거 노출
    assert "Selected genre:" in rc.stdout
    assert "calibration_status" in rc.stdout
    # adapted output 파일 생성
    assert adapted_path.exists()
    adapted = json.loads(adapted_path.read_text(encoding="utf-8"))
    # GenreAdaptedOutput schema 확인
    assert "schema_version" in adapted


def test_apply_top_recommendation_genre_override(tmp_path):
    """--genre override 시 modal 자동 선택 무시."""
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()

    profiles_path = tmp_path / "profiles.json"
    _run([
        str(BUILD_PROFILES),
        "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
        "--output", str(profiles_path),
        "--allow-rulebook-only",
    ])

    rec_path = tmp_path / "rec.json"
    _run([
        str(RUN_ADAPT),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--profiles", str(profiles_path),
        "--output", str(rec_path),
    ])

    adapted_path = tmp_path / "adapted.json"
    rc = _run([
        str(APPLY_TOP_REC),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--recommendation", str(rec_path),
        "--genre", "japanese_quiet_drama",  # override
        "--output", str(adapted_path),
    ])
    assert rc.returncode == 0, rc.stderr + rc.stdout
    assert "japanese_quiet_drama" in rc.stdout
    assert '"override": true' in rc.stdout


def test_apply_top_recommendation_exit_2_on_missing_files(tmp_path):
    rc = _run([
        str(APPLY_TOP_REC),
        "--skeleton", str(tmp_path / "missing_sk.json"),
        "--recommendation", str(tmp_path / "missing_rec.json"),
        "--output", str(tmp_path / "out.json"),
    ])
    assert rc.returncode == 2


def test_target_a_and_c_e2e_on_deployed_skeleton(tmp_path):
    """E2E: deployed skeleton → Target A CLI + Target C CLI → top-1 일치 invariant."""
    if not DEPLOYED_SKELETON.exists():
        pytest.skip()

    profiles_path = tmp_path / "profiles.json"
    rc = _run([
        str(BUILD_PROFILES),
        "--genres", "korean_morning_melodrama", "japanese_quiet_drama",
        "--output", str(profiles_path),
        "--allow-rulebook-only",
    ])
    assert rc.returncode == 0, rc.stderr

    # Target A
    a_out = tmp_path / "a.json"
    rc = _run([
        str(RUN_BASELINE),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--profiles", str(profiles_path),
        "--output", str(a_out),
    ])
    assert rc.returncode == 0, rc.stderr
    a = json.loads(a_out.read_text(encoding="utf-8"))

    # Target C
    c_out = tmp_path / "c.json"
    rc = _run([
        str(RUN_ADAPT),
        "--skeleton", str(DEPLOYED_SKELETON),
        "--profiles", str(profiles_path),
        "--output", str(c_out),
    ])
    assert rc.returncode == 0, rc.stderr
    c = json.loads(c_out.read_text(encoding="utf-8"))

    # 일관성: Target A의 seed별 top-1과 Target C의 1순위 일치
    a_top: dict[str, tuple[str, float]] = {}
    for rec in sorted(a["recommendations"], key=lambda r: -r["score"]):
        if rec["source_seed_id"] not in a_top:
            a_top[rec["source_seed_id"]] = (rec["genre_id"], rec["score"])

    c_top: dict[str, tuple[str, float]] = {}
    for rec in c["recommendations"]:
        modes = rec["recommended_modes"]
        if modes:
            c_top[rec["source_seed_id"]] = (modes[0]["genre_id"], modes[0]["score"])

    # genre_id 일치
    a_genres = {sid: g for sid, (g, _) in a_top.items()}
    c_genres = {sid: g for sid, (g, _) in c_top.items()}
    assert a_genres == c_genres
    # score도 동일 (소수점 4자리)
    for sid in a_top:
        assert abs(a_top[sid][1] - c_top[sid][1]) < 1e-4


# ---------------------------------------------------------------------------
# Phase 3.1 §29 — Acceptance verifier (cycle 29)
# ---------------------------------------------------------------------------

VERIFY_PHASE31 = ROOT / "scripts/data/verify_phase3_1_acceptance.py"


def test_verify_phase3_1_acceptance_help():
    rc = _run([str(VERIFY_PHASE31), "--help"])
    assert rc.returncode == 0


def test_verify_phase3_1_acceptance_all_pending_when_nothing(tmp_path):
    """Phase 3.1 deploys 0건 → 9개 모두 FAIL/PENDING. exit 1 (AUTO FAIL > 0)."""
    output = tmp_path / "report.json"
    rc = _run([
        str(VERIFY_PHASE31),
        "--baseline-output", str(tmp_path / "no_baseline.json"),
        "--profiles", str(tmp_path / "no_profiles.json"),
        "--demo-dir", str(tmp_path / "no_demo"),
        "--baseline-cover-doc", str(tmp_path / "no_cover.md"),
        "--output", str(output),
    ])
    assert rc.returncode == 1  # AUTO FAIL > 0
    data = json.loads(output.read_text(encoding="utf-8"))
    summary = data["summary"]
    # §29.1 PENDING (Phase 3.0 dep) + §29.2-6/8 AUTO FAIL (6건, baseline/profile/demo 없음)
    # §29.7 PASS (bridge script 존재) + §29.9 HEURISTIC FAIL (AUTO에 안 들어감)
    assert summary["auto_fail"] >= 5
    # §29.1은 PENDING으로 분리
    by_id = {c["item_id"]: c for c in data["checks"]}
    assert by_id[1]["status"] == "PENDING"
    assert by_id[1]["category"] == "PENDING"
    # §29.7 bridge는 deploys 무관하게 PASS (capability check)
    assert by_id[7]["status"] == "PASS"


def test_verify_phase3_1_acceptance_e2e_passes_on_deployed(tmp_path):
    """Real deployed Phase 3.1 deploys → AUTO PASS 7+ / PENDING 1."""
    baseline_path = ROOT / "data/narrative/phase3_1_demo/flesh_baseline_output.json"
    profiles_path = ROOT / "data/narrative/phase3_1_demo/genre_profiles.json"
    demo_dir = ROOT / "docs/portfolio/demo_flesh_baseline"
    cover_doc = ROOT / "docs/portfolio/FLESH_BASELINE_DEMO.md"

    if not all(p.exists() for p in [baseline_path, profiles_path, demo_dir, cover_doc]):
        pytest.skip("Phase 3.1 deploys not all present")

    output = tmp_path / "report.json"
    rc = _run([
        str(VERIFY_PHASE31),
        "--baseline-output", str(baseline_path),
        "--profiles", str(profiles_path),
        "--demo-dir", str(demo_dir),
        "--baseline-cover-doc", str(cover_doc),
        "--output", str(output),
    ])
    assert rc.returncode == 0, rc.stdout + rc.stderr
    data = json.loads(output.read_text(encoding="utf-8"))
    summary = data["summary"]
    # 8 AUTO PASS (§29.2-8) + 1 HEURISTIC PASS (§29.9)
    assert summary["auto_pass"] >= 7
    assert summary["auto_fail"] == 0
    # §29.1은 reliability report 없으면 PENDING
    by_id = {c["item_id"]: c for c in data["checks"]}
    assert by_id[1]["status"] in ("PENDING", "PASS")  # PENDING (없음) or PASS (있고 keep≥4)


def test_verify_phase3_1_acceptance_with_reliability(tmp_path):
    """reliability.json 제공 → §29.1 PASS (keep ≥ 4) 또는 FAIL."""
    baseline_path = ROOT / "data/narrative/phase3_1_demo/flesh_baseline_output.json"
    profiles_path = ROOT / "data/narrative/phase3_1_demo/genre_profiles.json"
    demo_dir = ROOT / "docs/portfolio/demo_flesh_baseline"
    cover_doc = ROOT / "docs/portfolio/FLESH_BASELINE_DEMO.md"

    if not all(p.exists() for p in [baseline_path, profiles_path, demo_dir, cover_doc]):
        pytest.skip("Phase 3.1 deploys not all present")

    rel = tmp_path / "reliability.json"
    rel.write_text(
        json.dumps({"summary": {"keep": 5}, "features": {}}),
        encoding="utf-8",
    )

    output = tmp_path / "report.json"
    rc = _run([
        str(VERIFY_PHASE31),
        "--baseline-output", str(baseline_path),
        "--profiles", str(profiles_path),
        "--demo-dir", str(demo_dir),
        "--baseline-cover-doc", str(cover_doc),
        "--reliability-report", str(rel),
        "--output", str(output),
    ])
    assert rc.returncode == 0
    data = json.loads(output.read_text(encoding="utf-8"))
    by_id = {c["item_id"]: c for c in data["checks"]}
    assert by_id[1]["status"] == "PASS"
    assert by_id[1]["category"] == "AUTO"


def test_verify_phase3_1_acceptance_reliability_below_threshold(tmp_path):
    """reliability summary.keep < 4 → §29.1 FAIL."""
    baseline_path = ROOT / "data/narrative/phase3_1_demo/flesh_baseline_output.json"
    profiles_path = ROOT / "data/narrative/phase3_1_demo/genre_profiles.json"
    demo_dir = ROOT / "docs/portfolio/demo_flesh_baseline"
    cover_doc = ROOT / "docs/portfolio/FLESH_BASELINE_DEMO.md"

    if not all(p.exists() for p in [baseline_path, profiles_path, demo_dir, cover_doc]):
        pytest.skip("Phase 3.1 deploys not all present")

    rel = tmp_path / "reliability.json"
    rel.write_text(
        json.dumps({"summary": {"keep": 2}}),
        encoding="utf-8",
    )

    output = tmp_path / "report.json"
    rc = _run([
        str(VERIFY_PHASE31),
        "--baseline-output", str(baseline_path),
        "--profiles", str(profiles_path),
        "--demo-dir", str(demo_dir),
        "--baseline-cover-doc", str(cover_doc),
        "--reliability-report", str(rel),
        "--output", str(output),
    ])
    assert rc.returncode == 1  # §29.1 FAIL
    data = json.loads(output.read_text(encoding="utf-8"))
    by_id = {c["item_id"]: c for c in data["checks"]}
    assert by_id[1]["status"] == "FAIL"


# ---------------------------------------------------------------------------
# Phase 3.1 cycle 33 — FLESH_BASELINE_DEMO.md cover doc currency:
# §5.1-5.3에서 언급한 script paths와 데모 경로가 실제로 존재하는지 강제.
# ---------------------------------------------------------------------------

# Phase 3.05 cycle 37 (L86 generic detector per L85 pattern: 3+ instances → systemic):
# 4 specific tests (cycle 33-34-35-36) → single registry-driven meta-test. New doc
# joins by adding one dict entry — no new test function.

_DOC_REALITY_REGISTRY = {
    "README.md": {
        # cycle 47 — root README highest-traffic GitHub entry
        "required_paths": [
            "docs/witness_rubric_design.md",
            "docs/WITNESS_V3_RUBRIC_DESIGN_REVIEW.md",
        ],
        "required_keywords": [
            "Target A",
            "Target B",
            "Target C",
            "adaptation_recommendation",
            "apply_top_recommendation",
            "verify_phase3_1_acceptance",
            "Rubric directive",
            "fixture-only",
        ],
        "any_of_keywords": [
            ["Candidate Classifier", "8-step flowchart"],
            ["29 cycle", "29-cycle", "Rubric"],
        ],
    },
    "docs/PROJECT_STRUCTURE.md": {
        # cycle 47 — file structure reference doc
        "required_paths": [
            "engine/observer/adaptation_recommendation.py",
            "scripts/narrative/run_adaptation_recommendation.py",
            "scripts/narrative/apply_top_recommendation.py",
            "scripts/data/verify_phase3_1_acceptance.py",
        ],
        "required_keywords": [
            "adaptation_recommendation.py",
            "apply_top_recommendation",
            "verify_phase3_1_acceptance",
            "engine/rubric",
            "Target B",
            "Target C",
        ],
        "any_of_keywords": [
            ["Candidate Classifier", "Rubric"],
            ["fixture-only", "fictional"],
        ],
    },
    "DESIGN.md": {
        # cycle 45 — architecture doc currency for cycle 16-42 additions
        "required_paths": [
            "docs/witness_rubric_design.md",
            "docs/WITNESS_V3_RUBRIC_DESIGN_REVIEW.md",
            "docs/portfolio/demo_adaptation_recommendation/index.html",
            "docs/portfolio/demo_episode_intensity/index.html",
        ],
        "required_keywords": [
            "Rubric directive",
            "Target C",
            "adaptation_recommendation_v1",
            "apply_top_recommendation",
            "verify_phase3_1_acceptance",
            "Phase 3.1 §29",
            "fixture-only",
            "calibration_status",
        ],
        "any_of_keywords": [
            ["L86", "L87", "doc-reality"],
            ["29 cycle", "29-cycle", "Rubric directive"],
        ],
    },
    "CLAUDE.md": {
        "required_paths": [
            "docs/witness_rubric_design.md",
            "docs/WITNESS_V3_RUBRIC_DESIGN_REVIEW.md",
            "docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md",
            "docs/WITNESS_PHASE_3_05_PREP_INTEGRITY_AND_VALIDATOR_HARDENING_PLAN.md",
            "docs/plans/PHASE_3_0_PIPELINE_OPERATING_GUIDE.md",
            "docs/portfolio/demo_episode_intensity/index.html",  # cycle 42 — Target B fixture-only mention
        ],
        "required_keywords": [
            "run_adaptation_recommendation",
            "build_adaptation_recommendation_demo",
            "apply_top_recommendation",
            "verify_phase3_1_acceptance",
            "Rubric directive",
            "fixture-only",  # cycle 42 — Target B deploy category 명시
        ],
        "any_of_keywords": [
            ["Target A", "adaptation_recommendation.py"],
            ["Target B", "episode_intensity.py"],
            ["Target C", "adaptation_recommendation_v1"],
            ["29 cycle", "29-cycle"],
            ["L84", "L85", "generic detector"],
        ],
    },
    "docs/portfolio/FLESH_BASELINE_DEMO.md": {
        "required_paths": [
            "engine/observer/flesh_baseline.py",
            "engine/observer/episode_intensity.py",
            "engine/observer/adaptation_recommendation.py",
            "scripts/narrative/run_adaptation_recommendation.py",
            "scripts/narrative/build_adaptation_recommendation_demo.py",
            "scripts/narrative/apply_top_recommendation.py",
            "scripts/data/verify_phase3_1_acceptance.py",
        ],
        "required_keywords": [
            "adaptation_recommendation_v1",
            "calibration_status",
            "verify_phase3_1_acceptance",
        ],
        "any_of_keywords": [
            ["Cross-target", "cross-target", "Target A"],
            ["--md-report", "md-report"],
        ],
    },
    "docs/portfolio/README.md": {
        "required_paths": [
            "docs/portfolio/demo_adaptation_recommendation/index.html",
            "docs/portfolio/demo_episode_intensity/index.html",
            "docs/portfolio/demo_rubric/README.md",
            "docs/portfolio/demo_rubric/ensemble_visualization.html",
            "docs/portfolio/demo_rubric/character_discrimination.json",
            "docs/portfolio/demo_rubric/character_discrimination.md",
        ],
        "required_keywords": [
            "demo_adaptation_recommendation/index.html",
            "demo_episode_intensity/index.html",
            "demo_rubric/README.md",
            "demo_rubric/ensemble_visualization.html",
            "character_discrimination",
            "witness_rubric_design.md",
            "WITNESS_V3_RUBRIC_DESIGN_REVIEW.md",
            "run_adaptation_recommendation",
            "build_adaptation_recommendation_demo",
            "episode_intensity_v1",
            "fixture-only",  # cycle 40 Target B 카테고리
        ],
        "any_of_keywords": [
            ["29 cycle", "Rubric"],
            ["Target B", "demo_episode_intensity"],
        ],
    },
}


def test_doc_reality_registry_invariant():
    """L86 generic detector (cycle 37): registry-driven doc-reality test.

    각 registered doc에 대해:
      1. required_paths 모두 *repo에 존재*
      2. required_keywords 모두 *doc 내 존재*
      3. any_of_keywords 각 그룹에서 *적어도 하나* doc 내 존재

    새 doc은 _DOC_REALITY_REGISTRY에 dict 항목 1개 추가로 join. 별도 test 추가 0.
    """
    failures: list[str] = []
    for doc_rel_path, expectations in _DOC_REALITY_REGISTRY.items():
        doc_path = ROOT / doc_rel_path
        if not doc_path.exists():
            failures.append(f"{doc_rel_path}: doc itself missing")
            continue
        text = doc_path.read_text(encoding="utf-8")

        # 1. required_paths 실재 확인
        for required in expectations.get("required_paths", []):
            if not (ROOT / required).exists():
                failures.append(
                    f"{doc_rel_path}: required path missing on disk: {required}",
                )

        # 2. required_keywords doc 내 존재
        for kw in expectations.get("required_keywords", []):
            if kw not in text:
                failures.append(
                    f"{doc_rel_path}: required keyword missing in doc: {kw!r}",
                )

        # 3. any_of_keywords: 각 그룹에서 적어도 하나 doc 내 존재
        for group in expectations.get("any_of_keywords", []):
            if not any(kw in text for kw in group):
                failures.append(
                    f"{doc_rel_path}: none of any_of group present: {group}",
                )

    assert not failures, (
        f"L86 doc-reality registry violations:\n"
        + "\n".join(failures)
    )


def test_operating_guide_script_references_match_reality():
    """L86 pattern (cycle 35) — Operating Guide §2 스크립트 인덱스 표가 *현재* repo와
    일관해야 한다. 모든 markdown link `[name](../../scripts/.../foo.py)` 의 target이 실재해야 한다.
    """
    import re as _re
    op_guide = ROOT / "docs/plans/PHASE_3_0_PIPELINE_OPERATING_GUIDE.md"
    if not op_guide.exists():
        pytest.skip()
    text = op_guide.read_text(encoding="utf-8")

    # markdown link 패턴: [label](../../scripts/path/script.py)
    link_pattern = _re.compile(r"\[([^\]]+)\]\(\.\./\.\./(scripts/[^)]+\.py)\)")
    missing: list[str] = []
    paths_checked: list[str] = []
    for m in link_pattern.finditer(text):
        rel_path = m.group(2)
        paths_checked.append(rel_path)
        if not (ROOT / rel_path).exists():
            missing.append(f"{m.group(1)}: {rel_path}")
    assert not missing, (
        f"Operating Guide §2 references nonexistent scripts:\n"
        + "\n".join(missing)
    )
    # 최소 12개 이상 script 참조해야 함 (Phase 3.0 7개 + Phase 3.1 5+)
    assert len(paths_checked) >= 12, (
        f"Operating Guide §2 only references {len(paths_checked)} scripts; "
        "stale list?"
    )
    # cycle 25/29/31 산출이 포함돼 있어야 함
    assert any("apply_top_recommendation" in p for p in paths_checked)
    assert any("verify_phase3_1_acceptance" in p for p in paths_checked)
    assert any("run_adaptation_recommendation" in p for p in paths_checked)


def test_deployed_episode_intensity_demo_has_fixture_only_banner():
    """L86 doc-reality (cycle 40, Target B 1번째 portfolio asset) —
    fixture-only deploy는 *prominent banner*로 fictional 표시 강제.
    """
    demo_dir = ROOT / "docs/portfolio/demo_episode_intensity"
    html_path = demo_dir / "index.html"
    md_path = demo_dir / "intensity.md"
    json_path = demo_dir / "episode_intensity.json"

    if not (html_path.exists() and md_path.exists() and json_path.exists()):
        pytest.skip("episode_intensity demo not deployed")

    html = html_path.read_text(encoding="utf-8")
    md = md_path.read_text(encoding="utf-8")

    # banner 강제
    assert "Fictional fixture-only" in html, (
        "demo_episode_intensity HTML missing fictional fixture-only banner"
    )
    assert "Fictional fixture-only" in md, (
        "demo_episode_intensity MD missing fictional fixture-only banner"
    )
    # fixture path 노출 — reviewer가 어디서 왔는지 추적 가능
    assert "annotation_public_safe" in html
    # Operating Guide §9 카테고리 명시
    assert "fixture-only" in html.lower()
    # raw text 노출 0
    assert "synopsis_text" not in html
    # schema 검증
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "episode_intensity_v1"
    assert data["audit"]["raw_text_used"] is False
    assert data["model"]["trained"] is False
    # phase3_pilot data_source (reliability 사용했으므로) — 정직성 유지
    assert data["model"]["data_source"] in ("phase3_pilot", "rulebook_only")


def test_all_markdown_internal_links_resolve():
    """L86 generic detector (cycle 38) — cycle 35 regex pattern을 *전체 docs/portfolio
    + docs/plans subtree*로 확장. 모든 internal markdown link (`[label](relative.ext)`)의
    target이 repo에 실재해야 한다.

    cycle 35는 단일 doc (Operating Guide §2 scripts/ only). cycle 38은 docs/portfolio
    + docs/plans의 모든 *.md의 모든 .py/.md/.html/.json/.csv/.jsonl/.yaml 링크.
    """
    import re as _re

    link_rx = _re.compile(
        r"\[([^\]]+)\]\(((?:\.\./)*[a-zA-Z0-9_./-]+\."
        r"(?:py|md|html|json|csv|jsonl|yaml|yml))\)",
    )

    scan_dirs = [ROOT / "docs/portfolio", ROOT / "docs/plans"]
    broken: list[str] = []
    total = 0
    for d in scan_dirs:
        if not d.exists():
            continue
        for md_file in d.glob("*.md"):
            text = md_file.read_text(encoding="utf-8")
            doc_dir = md_file.parent
            for m in link_rx.finditer(text):
                target = m.group(2)
                # skip anchors and external URLs (defensive — regex already excludes
                # most http:// patterns)
                if "#" in target or "://" in target:
                    continue
                total += 1
                resolved = (doc_dir / target).resolve()
                if not resolved.exists():
                    rel_doc = md_file.relative_to(ROOT)
                    broken.append(
                        f"{rel_doc}: '{m.group(1)}' → {target}",
                    )
    # 최소 50+ 링크 scan되어야 (현재 130 — stale 가드)
    assert total >= 50, (
        f"Only {total} markdown links scanned across docs/portfolio + docs/plans; "
        "scan pattern broken?"
    )
    assert not broken, (
        f"{len(broken)} broken markdown links across docs/:\n"
        + "\n".join(broken[:20])
    )


# Note (cycle 37): `test_flesh_baseline_demo_doc_references_match_reality` and
# `test_portfolio_readme_references_match_reality` (cycle 33/36) were absorbed into
# `test_doc_reality_registry_invariant` (registry-driven). Operating Guide test
# (cycle 35) stays separate — uses regex auto-extract, complementary check.


def test_verify_phase3_1_acceptance_md_report(tmp_path):
    """--md-report flag → markdown report 생성 (Phase 3.0 verifier 대칭)."""
    baseline_path = ROOT / "data/narrative/phase3_1_demo/flesh_baseline_output.json"
    profiles_path = ROOT / "data/narrative/phase3_1_demo/genre_profiles.json"
    demo_dir = ROOT / "docs/portfolio/demo_flesh_baseline"
    cover_doc = ROOT / "docs/portfolio/FLESH_BASELINE_DEMO.md"

    if not all(p.exists() for p in [baseline_path, profiles_path, demo_dir, cover_doc]):
        pytest.skip("Phase 3.1 deploys not all present")

    md_path = tmp_path / "report.md"
    rc = _run([
        str(VERIFY_PHASE31),
        "--baseline-output", str(baseline_path),
        "--profiles", str(profiles_path),
        "--demo-dir", str(demo_dir),
        "--baseline-cover-doc", str(cover_doc),
        "--md-report", str(md_path),
    ])
    assert rc.returncode == 0, rc.stdout + rc.stderr
    assert md_path.exists()
    md = md_path.read_text(encoding="utf-8")
    # Phase 3.0 verifier와 동일한 섹션 구조 확인
    assert "# Phase 3.1 §29 Acceptance Verification Report" in md
    assert "## Summary" in md
    assert "## Items" in md
    assert "## Status / Category Legend" in md
    # 9 항목 모두 표시
    for i in range(1, 10):
        assert f"| 29.{i} |" in md
    # legend entries
    assert "PASS" in md
    assert "PENDING" in md
    assert "AUTO" in md
    assert "HEURISTIC" in md
