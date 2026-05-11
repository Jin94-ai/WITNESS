"""Phase 3.1 §29 Acceptance Criteria — 자동 검증 CLI.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §29.

목표:
    Phase 3.1 baseline 배포 후 한 명령으로 9개 acceptance 항목 자동 점검.

검증 분류:
    AUTO  — 산출물 존재 / 필드 / 임계 자동 체크
    PENDING — Phase 3.0 의존 항목 (pilot 통과 전 N/A)
    HEURISTIC — 작성 완료 여부 약한 검사

Plan §29 항목 (9개):
    1. Phase 3.0 reliability report 통과 (PENDING — Phase 3.0 dep)
    2. GenreProfile v1 생성 (AUTO)
    3. weighted score baseline 생성 (AUTO — flesh_baseline_output_v1)
    4. SkeletonOutput seed별 genre fit score 생성 (AUTO)
    5. reason_features가 설명 가능 (AUTO — 각 rec에 reason_features 비어 있지 않음)
    6. raw synopsis를 출력에 포함하지 않음 (AUTO — audit.raw_text_used==False)
    7. rule-based adapter와 연결 가능 (AUTO — apply_top_recommendation.py 존재 + recommended_adapter 필드)
    8. demo_flesh_baseline/index.html 생성 (AUTO)
    9. baseline report 작성 (HEURISTIC — FLESH_BASELINE_DEMO.md or similar)

사용:
    python scripts/data/verify_phase3_1_acceptance.py \\
        --baseline-output data/narrative/phase3_1_demo/flesh_baseline_output.json \\
        --profiles data/narrative/phase3_1_demo/genre_profiles.json \\
        --demo-dir docs/portfolio/demo_flesh_baseline \\
        --baseline-cover-doc docs/portfolio/FLESH_BASELINE_DEMO.md \\
        --reliability-report data/annotation/phase3_pilot/reports/reliability.json \\
        [--output report.json]

Exit:
    0 — 모든 AUTO PASS (PENDING은 exit 0 유지)
    1 — 1+ AUTO FAIL
    2 — 입력 누락 또는 사용 오류

원칙:
    - 외부 fetch 0 / LLM API 0 / engine simulation 수정 0
    - Phase 3.0 통과 전에도 정상 실행 가능 (Phase 3.0 의존 항목은 PENDING)
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _force_utf8_stdout() -> None:
    if hasattr(sys.stdout, "buffer"):
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace",
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace",
            )
        except Exception:
            pass


@dataclass
class AcceptanceCheck:
    """Phase 3.1 §29 단일 acceptance 항목 검증 결과."""
    item_id: int                    # 1-9
    name: str
    status: str                     # "PASS" | "FAIL" | "PENDING" | "MANUAL"
    category: str                   # "AUTO" | "PENDING" | "HEURISTIC"
    detail: str = ""
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "status": self.status,
            "category": self.category,
            "detail": self.detail,
            "evidence": self.evidence,
        }


# ---------------------------------------------------------------------------
# Plan §29 — 9 항목 자동 체크
# ---------------------------------------------------------------------------

def check_01_phase30_reliability(
    *, reliability_report: Path | None,
) -> AcceptanceCheck:
    """§29.1 — Phase 3.0 reliability report 통과 (PENDING — Phase 3.0 dep)."""
    if reliability_report is None or not reliability_report.exists():
        return AcceptanceCheck(
            item_id=1, name="Phase 3.0 reliability report",
            status="PENDING", category="PENDING",
            detail="reliability.json 미존재 — Phase 3.0 pilot 통과 후 자동 PASS 평가",
        )
    try:
        data = json.loads(reliability_report.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return AcceptanceCheck(
            item_id=1, name="Phase 3.0 reliability report",
            status="FAIL", category="AUTO",
            detail=f"reliability.json 파싱 실패: {e}",
        )
    summary = data.get("summary", {})
    keep_count = summary.get("keep", 0)
    if keep_count >= 4:
        return AcceptanceCheck(
            item_id=1, name="Phase 3.0 reliability report",
            status="PASS", category="AUTO",
            detail=f"summary.keep = {keep_count} ≥ 4",
            evidence={"keep_count": keep_count},
        )
    return AcceptanceCheck(
        item_id=1, name="Phase 3.0 reliability report",
        status="FAIL", category="AUTO",
        detail=f"summary.keep = {keep_count} < 4 (Phase 3.1 진입 조건 미충족)",
        evidence={"keep_count": keep_count},
    )


def check_02_genre_profile(*, profiles_path: Path | None) -> AcceptanceCheck:
    """§29.2 — GenreProfile v1 생성."""
    if profiles_path is None or not profiles_path.exists():
        return AcceptanceCheck(
            item_id=2, name="GenreProfile v1 생성",
            status="FAIL", category="AUTO",
            detail=f"profiles JSON 미존재: {profiles_path}",
        )
    try:
        data = json.loads(profiles_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return AcceptanceCheck(
            item_id=2, name="GenreProfile v1 생성",
            status="FAIL", category="AUTO",
            detail=f"profiles JSON 파싱 실패: {e}",
        )
    profiles = data if isinstance(data, list) else data.get("profiles", [])
    if not profiles:
        return AcceptanceCheck(
            item_id=2, name="GenreProfile v1 생성",
            status="FAIL", category="AUTO",
            detail="profiles 0개",
        )
    expected_schema = "genre_profile_v1"
    schemas = {p.get("schema_version") for p in profiles}
    if schemas != {expected_schema}:
        return AcceptanceCheck(
            item_id=2, name="GenreProfile v1 생성",
            status="FAIL", category="AUTO",
            detail=f"schema_version mismatch: {schemas} != {{'{expected_schema}'}}",
            evidence={"schemas": list(schemas)},
        )
    return AcceptanceCheck(
        item_id=2, name="GenreProfile v1 생성",
        status="PASS", category="AUTO",
        detail=f"{len(profiles)} profile(s) loaded with schema {expected_schema}",
        evidence={"profile_count": len(profiles),
                  "genres": [p.get("genre_id") for p in profiles]},
    )


def check_03_baseline_output(*, baseline_path: Path | None) -> AcceptanceCheck:
    """§29.3 — weighted score baseline 생성 (flesh_baseline_output_v1)."""
    if baseline_path is None or not baseline_path.exists():
        return AcceptanceCheck(
            item_id=3, name="weighted score baseline 생성",
            status="FAIL", category="AUTO",
            detail=f"baseline output 미존재: {baseline_path}",
        )
    try:
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return AcceptanceCheck(
            item_id=3, name="weighted score baseline 생성",
            status="FAIL", category="AUTO",
            detail=f"baseline 파싱 실패: {e}",
        )
    schema = data.get("schema_version")
    if schema != "flesh_baseline_output_v1":
        return AcceptanceCheck(
            item_id=3, name="weighted score baseline 생성",
            status="FAIL", category="AUTO",
            detail=f"schema_version != flesh_baseline_output_v1 (got {schema})",
        )
    return AcceptanceCheck(
        item_id=3, name="weighted score baseline 생성",
        status="PASS", category="AUTO",
        detail=f"schema={schema}, model_type={data.get('model', {}).get('type')}",
        evidence={"schema_version": schema,
                  "recommendations": len(data.get("recommendations", []))},
    )


def check_04_seed_fit_scores(*, baseline_path: Path | None) -> AcceptanceCheck:
    """§29.4 — SkeletonOutput seed별 genre fit score 생성."""
    if baseline_path is None or not baseline_path.exists():
        return AcceptanceCheck(
            item_id=4, name="seed별 genre fit score",
            status="FAIL", category="AUTO",
            detail="baseline output 미존재",
        )
    try:
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return AcceptanceCheck(
            item_id=4, name="seed별 genre fit score",
            status="FAIL", category="AUTO", detail="baseline 파싱 실패",
        )
    recs = data.get("recommendations", [])
    if not recs:
        return AcceptanceCheck(
            item_id=4, name="seed별 genre fit score",
            status="FAIL", category="AUTO",
            detail="recommendations 0개",
        )
    seeds = {r.get("source_seed_id") for r in recs}
    # 각 rec에 score + fit_label 모두 존재 확인
    missing = [
        r for r in recs
        if "score" not in r or "fit_label" not in r
    ]
    if missing:
        return AcceptanceCheck(
            item_id=4, name="seed별 genre fit score",
            status="FAIL", category="AUTO",
            detail=f"{len(missing)} recs missing score/fit_label",
        )
    return AcceptanceCheck(
        item_id=4, name="seed별 genre fit score",
        status="PASS", category="AUTO",
        detail=f"{len(recs)} recs across {len(seeds)} seeds, all with score+fit_label",
        evidence={"rec_count": len(recs), "seed_count": len(seeds)},
    )


def check_05_reason_features(*, baseline_path: Path | None) -> AcceptanceCheck:
    """§29.5 — reason_features가 설명 가능."""
    if baseline_path is None or not baseline_path.exists():
        return AcceptanceCheck(
            item_id=5, name="reason_features 설명 가능",
            status="FAIL", category="AUTO", detail="baseline 미존재",
        )
    data = json.loads(baseline_path.read_text(encoding="utf-8"))
    recs = data.get("recommendations", [])
    if not recs:
        return AcceptanceCheck(
            item_id=5, name="reason_features 설명 가능",
            status="FAIL", category="AUTO", detail="recs 0개",
        )
    # 각 rec에 reason_features 또는 score_breakdown 중 하나는 있어야 함
    no_reason = [
        r for r in recs
        if not r.get("reason_features") and not r.get("score_breakdown")
    ]
    if no_reason:
        return AcceptanceCheck(
            item_id=5, name="reason_features 설명 가능",
            status="FAIL", category="AUTO",
            detail=f"{len(no_reason)} recs without reason_features/score_breakdown",
        )
    return AcceptanceCheck(
        item_id=5, name="reason_features 설명 가능",
        status="PASS", category="AUTO",
        detail=f"all {len(recs)} recs have reason_features or score_breakdown",
    )


def check_06_no_raw_text(*, baseline_path: Path | None) -> AcceptanceCheck:
    """§29.6 — raw synopsis를 출력에 포함하지 않음."""
    if baseline_path is None or not baseline_path.exists():
        return AcceptanceCheck(
            item_id=6, name="raw synopsis 출력에 미포함",
            status="FAIL", category="AUTO", detail="baseline 미존재",
        )
    data = json.loads(baseline_path.read_text(encoding="utf-8"))
    audit = data.get("audit", {})
    if audit.get("raw_text_used") is not False:
        return AcceptanceCheck(
            item_id=6, name="raw synopsis 출력에 미포함",
            status="FAIL", category="AUTO",
            detail=f"audit.raw_text_used = {audit.get('raw_text_used')} (expected False)",
        )
    # 추가 string scan: "synopsis_text" 노출 0
    raw = baseline_path.read_text(encoding="utf-8")
    if "synopsis_text" in raw:
        return AcceptanceCheck(
            item_id=6, name="raw synopsis 출력에 미포함",
            status="FAIL", category="AUTO",
            detail="JSON에 'synopsis_text' 문자열 존재",
        )
    return AcceptanceCheck(
        item_id=6, name="raw synopsis 출력에 미포함",
        status="PASS", category="AUTO",
        detail="audit.raw_text_used=False + 'synopsis_text' 노출 0",
    )


def check_07_adapter_bridge(*, baseline_path: Path | None) -> AcceptanceCheck:
    """§29.7 — rule-based adapter와 연결 가능."""
    bridge = ROOT / "scripts/narrative/apply_top_recommendation.py"
    if not bridge.exists():
        return AcceptanceCheck(
            item_id=7, name="rule-based adapter와 연결 가능",
            status="FAIL", category="AUTO",
            detail=f"bridge script 미존재: {bridge}",
        )
    # baseline에 recommended_adapter 필드도 확인
    if baseline_path and baseline_path.exists():
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
        recs = data.get("recommendations", [])
        no_adapter = [r for r in recs if not r.get("recommended_adapter")]
        if no_adapter:
            return AcceptanceCheck(
                item_id=7, name="rule-based adapter와 연결 가능",
                status="FAIL", category="AUTO",
                detail=f"{len(no_adapter)} recs missing recommended_adapter",
            )
    return AcceptanceCheck(
        item_id=7, name="rule-based adapter와 연결 가능",
        status="PASS", category="AUTO",
        detail="apply_top_recommendation.py 존재 + recommended_adapter 필드 보유",
    )


def check_08_demo_html(*, demo_dir: Path | None) -> AcceptanceCheck:
    """§29.8 — demo_flesh_baseline/index.html 생성."""
    if demo_dir is None or not demo_dir.exists():
        return AcceptanceCheck(
            item_id=8, name="demo_flesh_baseline/index.html 생성",
            status="FAIL", category="AUTO",
            detail=f"demo dir 미존재: {demo_dir}",
        )
    index_html = demo_dir / "index.html"
    if not index_html.exists():
        return AcceptanceCheck(
            item_id=8, name="demo_flesh_baseline/index.html 생성",
            status="FAIL", category="AUTO",
            detail=f"index.html 미존재 in {demo_dir}",
        )
    size = index_html.stat().st_size
    if size < 500:
        return AcceptanceCheck(
            item_id=8, name="demo_flesh_baseline/index.html 생성",
            status="FAIL", category="AUTO",
            detail=f"index.html 너무 작음 ({size} bytes)",
        )
    return AcceptanceCheck(
        item_id=8, name="demo_flesh_baseline/index.html 생성",
        status="PASS", category="AUTO",
        detail=f"index.html 존재 ({size} bytes)",
        evidence={"size_bytes": size},
    )


def check_09_baseline_report(
    *, baseline_cover_doc: Path | None,
) -> AcceptanceCheck:
    """§29.9 — baseline report 작성."""
    if baseline_cover_doc is None or not baseline_cover_doc.exists():
        return AcceptanceCheck(
            item_id=9, name="baseline report 작성",
            status="FAIL", category="HEURISTIC",
            detail=f"cover doc 미존재: {baseline_cover_doc}",
        )
    text = baseline_cover_doc.read_text(encoding="utf-8")
    if len(text) < 500:
        return AcceptanceCheck(
            item_id=9, name="baseline report 작성",
            status="FAIL", category="HEURISTIC",
            detail=f"cover doc 너무 짧음 ({len(text)} chars)",
        )
    return AcceptanceCheck(
        item_id=9, name="baseline report 작성",
        status="PASS", category="HEURISTIC",
        detail=f"cover doc 존재 ({len(text)} chars)",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--baseline-output", type=Path, default=None,
                     help="flesh_baseline_output.json 경로")
    ap.add_argument("--profiles", type=Path, default=None,
                     help="genre_profiles.json 경로")
    ap.add_argument("--demo-dir", type=Path, default=None,
                     help="docs/portfolio/demo_flesh_baseline/ 디렉토리")
    ap.add_argument("--baseline-cover-doc", type=Path, default=None,
                     help="FLESH_BASELINE_DEMO.md 또는 baseline report 문서")
    ap.add_argument("--reliability-report", type=Path, default=None,
                     help="Phase 3.0 reliability.json (없으면 §29.1 PENDING)")
    ap.add_argument("--output", type=Path, default=None,
                     help="report JSON 출력 (없으면 stdout 표만)")
    ap.add_argument("--md-report", type=Path, default=None,
                     help="markdown 보고서 출력 (Phase 3.0 verifier와 대칭)")
    args = ap.parse_args(argv)

    checks: list[AcceptanceCheck] = [
        check_01_phase30_reliability(reliability_report=args.reliability_report),
        check_02_genre_profile(profiles_path=args.profiles),
        check_03_baseline_output(baseline_path=args.baseline_output),
        check_04_seed_fit_scores(baseline_path=args.baseline_output),
        check_05_reason_features(baseline_path=args.baseline_output),
        check_06_no_raw_text(baseline_path=args.baseline_output),
        check_07_adapter_bridge(baseline_path=args.baseline_output),
        check_08_demo_html(demo_dir=args.demo_dir),
        check_09_baseline_report(baseline_cover_doc=args.baseline_cover_doc),
    ]

    auto_pass = sum(1 for c in checks if c.category == "AUTO" and c.status == "PASS")
    auto_fail = sum(1 for c in checks if c.category == "AUTO" and c.status == "FAIL")
    pending = sum(1 for c in checks if c.status == "PENDING")
    heur_pass = sum(1 for c in checks if c.category == "HEURISTIC" and c.status == "PASS")

    summary = {
        "total": len(checks),
        "auto_pass": auto_pass,
        "auto_fail": auto_fail,
        "pending": pending,
        "heuristic_pass": heur_pass,
    }

    # Pretty print
    print(f"Phase 3.1 §29 Acceptance Verification:")
    print(f"  AUTO PASS:      {auto_pass}")
    print(f"  AUTO FAIL:      {auto_fail}")
    print(f"  PENDING:        {pending}")
    print(f"  HEURISTIC PASS: {heur_pass}")
    print()
    for c in checks:
        print(f"  [{c.status:8s}] §29.{c.item_id} {c.name}")
        if c.detail:
            print(f"             {c.detail}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps({
                "summary": summary,
                "checks": [c.to_dict() for c in checks],
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nReport written to {args.output}")

    if args.md_report:
        args.md_report.parent.mkdir(parents=True, exist_ok=True)
        args.md_report.write_text(
            _render_markdown(checks, summary),
            encoding="utf-8",
        )
        print(f"Markdown report → {args.md_report}")

    return 1 if auto_fail > 0 else 0


def _render_markdown(checks: list, summary: dict) -> str:
    """Phase 3.1 §29 verifier markdown report (Phase 3.0 verifier 대칭)."""
    from datetime import datetime
    lines: list[str] = []
    lines.append("# Phase 3.1 §29 Acceptance Verification Report")
    lines.append("")
    lines.append(
        f"> Generated by `scripts/data/verify_phase3_1_acceptance.py` at "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.",
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total items**: {summary['total']}")
    lines.append(f"- **AUTO PASS**: {summary['auto_pass']}")
    lines.append(f"- **AUTO FAIL**: {summary['auto_fail']}")
    lines.append(f"- **PENDING**: {summary['pending']}")
    lines.append(f"- **HEURISTIC PASS**: {summary['heuristic_pass']}")
    lines.append("")
    status_icon = {"PASS": "[O]", "FAIL": "[X]", "PENDING": "[~]", "MANUAL": "[?]"}
    lines.append("## Items")
    lines.append("")
    lines.append("| § | Item | Status | Category | Detail |")
    lines.append("|---|---|---|---|---|")
    for c in checks:
        icon = status_icon.get(c.status, "[?]")
        detail = c.detail.replace("\n", " ").replace("|", "/")
        lines.append(
            f"| 29.{c.item_id} | {c.name} | {icon} {c.status} | {c.category} | {detail} |",
        )
    lines.append("")
    lines.append("## Status / Category Legend")
    lines.append("")
    lines.append("- **`[O]` PASS**: 모든 조건 통과.")
    lines.append("- **`[X]` FAIL**: 필수 조건 미충족 (AUTO는 exit 1 트리거).")
    lines.append("- **`[~]` PENDING**: Phase 3.0 의존 항목 (pilot 통과 전 N/A, exit 0 유지).")
    lines.append("- **AUTO**: 산출물 / 필드 자동 체크.")
    lines.append("- **HEURISTIC**: 길이 / 작성 여부 약한 검사.")
    lines.append("- **PENDING**: Phase 3.0 reliability 의존.")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
