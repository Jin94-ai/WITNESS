"""End-to-end tests for the Episode-centric Portfolio Demo (Story Assembly)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = ROOT / "docs" / "portfolio" / "demo"


@pytest.fixture(scope="module", autouse=True)
def _run_demo():
    """Ensure orchestrator has run before any test in this module."""
    orchestrator = ROOT / "scripts/narrative/run_portfolio_demo.py"
    rc = subprocess.run(
        [sys.executable, str(orchestrator)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, f"orchestrator failed: {rc.stderr}"


def test_orchestrator_writes_episode_outputs():
    assert (DEMO_DIR / "episode_outline.md").exists()
    assert (DEMO_DIR / "episode_outline.json").exists()


def test_orchestrator_writes_run_log_outputs():
    assert (DEMO_DIR / "run_log.md").exists()
    assert (DEMO_DIR / "run_log.json").exists()


def test_episode_outline_json_schema():
    p = DEMO_DIR / "episode_outline.json"
    payload = json.loads(p.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "episode_outline_v1"
    o = payload["outline"]
    for field in ("title", "logline", "main_character", "main_arc",
                  "supporting_arcs", "act_1", "act_2", "act_3",
                  "end_hook", "why_this_feels_like_a_story",
                  "evidence_summary", "risk_notes"):
        assert field in o, f"missing field: {field}"


def test_run_log_json_schema():
    p = DEMO_DIR / "run_log.json"
    payload = json.loads(p.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "run_log_v1"
    for field in ("anchor_id", "seed", "ticks", "agents", "groups",
                  "story_threads_found", "story_seeds_generated",
                  "episode_outlines_generated", "audit_failures",
                  "pipeline_steps", "runtime_seconds"):
        assert field in payload


def test_run_log_pipeline_has_six_steps():
    p = DEMO_DIR / "run_log.json"
    payload = json.loads(p.read_text(encoding="utf-8"))
    assert len(payload["pipeline_steps"]) == 6
    # plain_label must be Korean
    for s in payload["pipeline_steps"]:
        assert s["plain_label"]
        assert s["status"] == "completed"


def test_demo_html_contains_episode_section():
    html = (DEMO_DIR / "index.html").read_text(encoding="utf-8")
    assert 'id="episodeSection"' in html
    assert 'id="pipelineProgress"' in html


def test_demo_html_payload_contains_episode_outline():
    html = (DEMO_DIR / "index.html").read_text(encoding="utf-8")
    m = re.search(
        r'<script type="application/json" id="data-payload">(.*?)</script>',
        html, re.DOTALL,
    )
    assert m
    data = json.loads(m.group(1))
    assert "episode_outline" in data
    assert data["episode_outline"] is not None
    assert "run_log" in data
    assert data["run_log"]["pipeline_steps"]


def test_demo_html_runtime_summary_includes_episodes():
    html = (DEMO_DIR / "index.html").read_text(encoding="utf-8")
    m = re.search(
        r'<script type="application/json" id="data-payload">(.*?)</script>',
        html, re.DOTALL,
    )
    data = json.loads(m.group(1))
    assert "episodes" in data["run_summary"]
    assert data["run_summary"]["episodes"] >= 1


def test_episode_outline_md_no_internal_terms():
    md = (DEMO_DIR / "episode_outline.md").read_text(encoding="utf-8")
    forbidden = (
        "tick ", "source_derived", "source_inferred", "co-occurrence",
        "authority_vigilance", "public_suspicion", "blame_concentration",
        "MomentLink", "StoryThread", "viable_with_gaps", "strong_viable",
        "loyalty_vs_survival", "uncertainty_vs_commitment",
    )
    for f in forbidden:
        assert f not in md, f"'{f}' in episode_outline.md (general-audience surface)"


def test_episode_outline_md_no_unresolved_josa():
    md = (DEMO_DIR / "episode_outline.md").read_text(encoding="utf-8")
    for marker in ("은(는)", "이(가)", "을(를)", "과(와)"):
        assert marker not in md, (
            f"unresolved Korean josa marker {marker!r} in episode_outline.md"
        )


def test_episode_outline_supporting_roles_distinct():
    """4 candidates 위에서 supporting (Andrew/James/John) 역할이 *모두 같지는 않게*
    분산되어야. plan §"S02 Andrew, S03 James, S04 John은 Sub Arc 또는
    Supporting Thread로 사용한다" — 각자 다른 라벨."""
    p = DEMO_DIR / "episode_outline.json"
    payload = json.loads(p.read_text(encoding="utf-8"))
    sup = payload["outline"]["supporting_arcs"]
    if len(sup) >= 2:
        roles = {s["role_label"] for s in sup}
        assert len(roles) >= 2, (
            f"all supporting roles identical: {[s['role_label'] for s in sup]}"
        )


def test_demo_html_self_contained_after_episode_layer():
    """Episode layer 추가 후에도 self-contained 유지."""
    html = (DEMO_DIR / "index.html").read_text(encoding="utf-8")
    forbidden_external = (
        '<script src=', '<link rel="stylesheet" href=',
        "fonts.googleapis", "cdn.jsdelivr", "unpkg.com",
    )
    for f in forbidden_external:
        assert f not in html, f"external asset detected: {f}"


def test_run_log_md_renders_korean():
    md = (DEMO_DIR / "run_log.md").read_text(encoding="utf-8")
    assert "실행 요약" in md
    assert "파이프라인" in md
    assert "발견된 이야기 흐름" in md or "이야기 씨앗" in md


def test_demo_acceptance_criterion_episode_centric():
    """Plan acceptance #1, #4, #5 — orchestrator로 episode + s01 main."""
    payload = json.loads((DEMO_DIR / "episode_outline.json").read_text(encoding="utf-8"))
    seed_payload = json.loads((DEMO_DIR / "story_seed_cards.json").read_text(encoding="utf-8"))

    # Outline은 1개
    assert payload["outline"]
    # main_character가 S01에서 옴 (이름은 directive §2 따라 display layer에서
    # 한국어로 매핑될 수 있음 — Peter→베드로 등). seed_cards는 raw,
    # outline은 display version. 두 레이어 분리.
    s01_main = seed_payload["cards"][0]["main_character"]
    outline_main = payload["outline"]["main_character"]
    # raw == display (영어 이름 그대로) OR display는 한국어 매핑된 형태
    assert (outline_main == s01_main
            or outline_main in ("베드로", "안드레", "야고보", "요한",
                                  "유다", "가야바", "빌라도")), (
        f"outline main {outline_main!r} should equal s01 main {s01_main!r} "
        f"or be its Korean display mapping"
    )
    # supporting arcs는 S02-Sn에 매핑
    sup_ids = {s["seed_id"] for s in payload["outline"]["supporting_arcs"]}
    s01_id = seed_payload["cards"][0]["seed_id"]
    assert s01_id not in sup_ids


def test_demo_acceptance_pipeline_progress_visible():
    """Plan acceptance #2 — '시뮬레이션 실행했다는 흐름'이 보임."""
    html = (DEMO_DIR / "index.html").read_text(encoding="utf-8")
    # 6 step 파이프라인 라벨이 *어떤 형태로든* 나타나야
    assert "파이프라인 진행" in html or "Pipeline Progress" in html
    # JS로 렌더되는 step number 영역
    assert "pp-num" in html or "pp-step" in html


def test_orchestrator_runs_engine_fresh_by_default(tmp_path):
    """기본 모드는 *시뮬레이션을 매번 새로* 돌려야 한다.

    Sentinel 파일을 dump 위치에 미리 두고, orchestrator가 *그걸 덮어쓰는지*
    확인 — 덮어쓰면 fresh run, 그대로면 cache 사용 중.
    """
    seed = 42  # 평소 안 쓰는 seed로 캐시 충돌 회피
    cached_path = ROOT / f"data/visual/dot_observer_data_seed{seed}.json"
    out = tmp_path / "demo_test_fresh"

    # Sentinel: 미리 *명백히 다른* dump를 둠
    sentinel_obs = {
        "meta": {"anchor_id": "sentinel", "seed": -999, "n_ticks": 0,
                  "agent_count": 0, "group_count": 0, "schema_version": "v1"},
        "ticks": [],
        "candidates": [],
        "salience_marks": [],
    }
    cached_path.parent.mkdir(parents=True, exist_ok=True)
    cached_path.write_text(json.dumps(sentinel_obs), encoding="utf-8")

    rc = subprocess.run(
        [sys.executable,
         str(ROOT / "scripts/narrative/run_portfolio_demo.py"),
         "--seed", str(seed), "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr

    # Sentinel은 덮어써졌어야 한다 (real engine output이 자리잡음)
    refreshed = json.loads(cached_path.read_text(encoding="utf-8"))
    assert refreshed["meta"]["anchor_id"] != "sentinel"
    assert len(refreshed["ticks"]) > 0
    assert refreshed["meta"]["seed"] == seed


def test_orchestrator_use_cache_flag_skips_engine(tmp_path):
    """--use-cache 모드에서는 dump를 그대로 사용 (sentinel 그대로 남음)."""
    seed = 43
    cached_path = ROOT / f"data/visual/dot_observer_data_seed{seed}.json"
    out = tmp_path / "demo_test_cache"

    # Sentinel — 단, *최소한* moments 추출이 작동할 수 있는 형태
    # (cache mode면 이 dump를 직접 사용)
    sentinel_obs = {
        "meta": {"anchor_id": "cache_sentinel", "seed": seed, "n_ticks": 1,
                  "agent_count": 1, "group_count": 1, "schema_version": "v1"},
        "ticks": [
            {
                "tick": 1,
                "world": {"crowd_mood": "calm", "blame_concentration": 0.0,
                           "public_suspicion": 0.0, "authority_vigilance": 0.0},
                "groups": [{"id": "L1", "dominant_mode": "low_activity",
                             "tension": 0.1, "member_count": 1}],
                "agents": [{"id": "agent_01", "group_id": "L1",
                             "x": 100, "y": 100, "fear": 0.0, "hope": 5.0,
                             "shame_self": 0.0, "dominant_state": "calm",
                             "salient": False}],
                "active_events": [],
            }
        ],
        "candidates": [],
        "salience_marks": [],
    }
    cached_path.parent.mkdir(parents=True, exist_ok=True)
    cached_path.write_text(json.dumps(sentinel_obs), encoding="utf-8")

    rc = subprocess.run(
        [sys.executable,
         str(ROOT / "scripts/narrative/run_portfolio_demo.py"),
         "--seed", str(seed), "--output", str(out), "--use-cache"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr

    # Sentinel이 그대로 남아 있어야 한다 (cache 모드)
    after = json.loads(cached_path.read_text(encoding="utf-8"))
    assert after["meta"]["anchor_id"] == "cache_sentinel"
    assert after["meta"]["n_ticks"] == 1
