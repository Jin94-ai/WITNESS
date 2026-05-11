"""Tests for evidence_quote validator (LLM hallucination guard).

Per `docs/annotation/ANNOTATION_GUIDE.md` §3.2:
    "evidence_quote는 줄거리 원문에서 직접 인용 — LLM이 새로 만들어내면 안 됨."

이 검증기는 어노테이션의 evidence_quotes 각 quote_ko가 *원본 줄거리* 안에
substring으로 실제 등장하는지 검사. 매칭 안 되면 LLM 환각으로 의심.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ANNOTATE_SCRIPT = ROOT / "scripts/annotation/annotate_with_llm.py"


# ============================================================================
# 1. Unit: validate_evidence_quotes
# ============================================================================

ANNOTATION_FEATURES = (
    "conflict_intensity_peak",
    "revelation_density",
    "coincidence_frequency",
    "relationship_polarization",
    "new_conflict_introduction_rate",
    "dangling_thread_generation",
    "cliffhanger_intensity",
)


def _make_annotation(quotes: list[dict]) -> dict:
    return {
        "schema_version": "annotation_v1",
        "title_id": "x",
        "episode_no": 1,
        "annotator_id": "test",
        "annotated_at_iso": "2026-05-09T00:00:00Z",
        "features": {f: 0.5 for f in ANNOTATION_FEATURES},
        "evidence_quotes": quotes,
        "confidence": 0.7,
    }


def test_validate_quotes_passes_when_quote_in_synopsis():
    from scripts.annotation.prompt_templates import validate_evidence_quotes
    synopsis = "베드로는 그 자리에 남았지만, 결국 침묵을 선택했다."
    a = _make_annotation([
        {"feature": "revelation_density", "quote_ko": "결국 침묵을 선택했다"},
    ])
    errs = validate_evidence_quotes(a, synopsis)
    assert errs == []


def test_validate_quotes_flags_hallucination():
    from scripts.annotation.prompt_templates import validate_evidence_quotes
    synopsis = "베드로는 그 자리에 남았지만, 결국 침묵을 선택했다."
    a = _make_annotation([
        {"feature": "revelation_density", "quote_ko": "베드로가 도망쳤다"},
    ])
    errs = validate_evidence_quotes(a, synopsis)
    assert len(errs) == 1
    assert "not found in synopsis" in errs[0]
    assert "도망쳤다" in errs[0]


def test_validate_quotes_normalized_strategy_handles_whitespace():
    """공백 정규화 모드: '   결국  침묵을' (여러 공백) → '결국 침묵을' (단일)
    해서 매칭."""
    from scripts.annotation.prompt_templates import validate_evidence_quotes
    synopsis = "베드로는  그 자리에   남았지만, 결국 침묵을  선택했다."
    a = _make_annotation([
        {"feature": "revelation_density", "quote_ko": "결국 침묵을 선택했다"},
    ])
    errs = validate_evidence_quotes(a, synopsis, strategy="normalized")
    assert errs == []


def test_validate_quotes_strict_strategy_rejects_whitespace_diff():
    from scripts.annotation.prompt_templates import validate_evidence_quotes
    synopsis = "베드로는  그 자리에   남았지만,  결국  침묵을  선택했다."
    a = _make_annotation([
        # synopsis에는 공백이 다중인데 quote는 단일 — strict는 fail
        {"feature": "revelation_density", "quote_ko": "결국 침묵을 선택했다"},
    ])
    errs = validate_evidence_quotes(a, synopsis, strategy="strict_substring")
    # strict matching: synopsis의 다중 공백 포함 substring 으로는 매치 못함
    # (synopsis 안에 "결국 침묵을 선택했다" 정확히 단일 공백으로는 없음)
    assert len(errs) == 1


def test_validate_quotes_handles_missing_quote_text():
    from scripts.annotation.prompt_templates import validate_evidence_quotes
    a = _make_annotation([{"feature": "revelation_density", "quote_ko": ""}])
    errs = validate_evidence_quotes(a, "synopsis text")
    assert any("empty" in e for e in errs)


def test_validate_quotes_handles_non_dict_quote():
    from scripts.annotation.prompt_templates import validate_evidence_quotes
    a = _make_annotation([])  # type: ignore
    a["evidence_quotes"] = ["just a string"]
    errs = validate_evidence_quotes(a, "synopsis")
    assert any("must be a dict" in e for e in errs)


def test_validate_quotes_empty_list_passes():
    from scripts.annotation.prompt_templates import validate_evidence_quotes
    a = _make_annotation([])
    assert validate_evidence_quotes(a, "synopsis") == []


# ============================================================================
# 2. hallucination_rate metric
# ============================================================================

def test_hallucination_rate_zero_when_all_verified():
    from scripts.annotation.prompt_templates import hallucination_rate
    synopsis = "베드로는 그 자리에 남았지만, 결국 침묵을 선택했다."
    a = _make_annotation([
        {"feature": "revelation_density", "quote_ko": "결국 침묵을 선택했다"},
        {"feature": "cliffhanger_intensity", "quote_ko": "그 자리에 남았지만"},
    ])
    assert hallucination_rate(a, synopsis) == 0.0


def test_hallucination_rate_one_when_all_hallucinated():
    from scripts.annotation.prompt_templates import hallucination_rate
    synopsis = "베드로는 그 자리에 남았다."
    a = _make_annotation([
        {"feature": "revelation_density", "quote_ko": "베드로가 떠났다"},
        {"feature": "cliffhanger_intensity", "quote_ko": "예수께서 사라졌다"},
    ])
    assert hallucination_rate(a, synopsis) == 1.0


def test_hallucination_rate_partial():
    from scripts.annotation.prompt_templates import hallucination_rate
    synopsis = "베드로는 그 자리에 남았다."
    a = _make_annotation([
        {"feature": "revelation_density", "quote_ko": "베드로는 그 자리에 남았다"},  # verified
        {"feature": "cliffhanger_intensity", "quote_ko": "예수께서 사라졌다"},  # hallucinated
    ])
    assert hallucination_rate(a, synopsis) == 0.5


def test_hallucination_rate_zero_when_no_quotes():
    from scripts.annotation.prompt_templates import hallucination_rate
    a = _make_annotation([])
    assert hallucination_rate(a, "synopsis") == 0.0


# ============================================================================
# 3. CLI integration: annotate_with_llm fixture --synopsis
# ============================================================================

def _make_synopsis(text: str) -> dict:
    return {
        "schema_version": "synopsis_v1",
        "title_id": "x",
        "title_ko": "테스트 작품",
        "title_en": "Test",
        "category": "melodrama",
        "episode_no": 1,
        "synopsis_text_ko": text,
        "source_url": "http://example.com",
        "source_license": "CC-BY-SA-4.0",
        "fetched_at_iso": "2026-05-09T00:00:00Z",
    }


def test_fixture_with_synopsis_warns_on_hallucination(tmp_path):
    """--synopsis 제공 시 환각 quote에 WARNING + (default) 저장은 진행."""
    synopsis_text = "베드로는 그 자리에 남았다."
    syn_path = tmp_path / "ep01.json"
    syn_path.write_text(json.dumps(_make_synopsis(synopsis_text)), encoding="utf-8")

    response = _make_annotation([
        {"feature": "revelation_density", "quote_ko": "베드로가 떠났다"},  # 환각
    ])
    response["title_id"] = "x"
    response["episode_no"] = 1
    rsp_path = tmp_path / "response.json"
    rsp_path.write_text(json.dumps(response), encoding="utf-8")

    out = tmp_path / "annotated" / "x" / "01.json"
    rc = subprocess.run(
        [sys.executable, str(ANNOTATE_SCRIPT), "fixture",
         "--response", str(rsp_path),
         "--synopsis", str(syn_path),
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    # default mode: warning만 (저장 진행)
    assert rc.returncode == 0, rc.stderr
    assert out.exists()
    assert "WARNING" in rc.stderr or "WARNING" in rc.stdout
    assert "hallucination_rate" in rc.stdout


def test_fixture_strict_quotes_rejects_hallucination(tmp_path):
    """--strict-quotes: 환각 발견 시 저장 거부 + exit 1."""
    synopsis_text = "베드로는 그 자리에 남았다."
    syn_path = tmp_path / "ep01.json"
    syn_path.write_text(json.dumps(_make_synopsis(synopsis_text)), encoding="utf-8")

    response = _make_annotation([
        {"feature": "revelation_density", "quote_ko": "베드로가 떠났다"},
    ])
    response["title_id"] = "x"
    response["episode_no"] = 1
    rsp_path = tmp_path / "response.json"
    rsp_path.write_text(json.dumps(response), encoding="utf-8")

    out = tmp_path / "annotated" / "x" / "01.json"
    rc = subprocess.run(
        [sys.executable, str(ANNOTATE_SCRIPT), "fixture",
         "--response", str(rsp_path),
         "--synopsis", str(syn_path),
         "--output", str(out),
         "--strict-quotes"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 1
    assert not out.exists()
    assert "hallucination" in rc.stderr.lower() or "not found" in rc.stderr


def test_fixture_with_synopsis_passes_when_quotes_verified(tmp_path):
    synopsis_text = "베드로는 그 자리에 남았지만, 결국 침묵을 선택했다."
    syn_path = tmp_path / "ep01.json"
    syn_path.write_text(json.dumps(_make_synopsis(synopsis_text)), encoding="utf-8")

    response = _make_annotation([
        {"feature": "revelation_density", "quote_ko": "결국 침묵을 선택했다"},
    ])
    response["title_id"] = "x"
    response["episode_no"] = 1
    rsp_path = tmp_path / "response.json"
    rsp_path.write_text(json.dumps(response), encoding="utf-8")

    out = tmp_path / "annotated" / "x" / "01.json"
    rc = subprocess.run(
        [sys.executable, str(ANNOTATE_SCRIPT), "fixture",
         "--response", str(rsp_path),
         "--synopsis", str(syn_path),
         "--output", str(out),
         "--strict-quotes"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    # 모든 quote verified → strict-quotes에서도 OK
    assert rc.returncode == 0, rc.stderr
    assert out.exists()
    assert "hallucination_rate: 0.00" in rc.stdout
