"""Phase 3.0 §18 Acceptance Criteria — 자동 검증 CLI.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §18.

목표:
    Phase 3.0 pilot 종료 후 한 명령으로 12개 acceptance 항목 자동 점검.
    사용자가 "내가 정말 다 했나?" 일관되게 확인 가능.

검증 분류:
    AUTO  — 산출물 존재 / 수치 임계 자동 체크
    MANUAL — 사용자 외부 활동 (승인 / ToS 검토) — N/A로 표시, 사용자가 별도 확인
    HEURISTIC — template 채워졌는지 약한 검사 (작성 여부 추정)

사용:
    python scripts/data/verify_phase3_0_acceptance.py \\
        --pilot-dir data/annotation/phase3_pilot \\
        [--raw-private-dir data/external_private/synopsis_raw] \\
        [--data-card docs/plans/PHASE_3_0_DATA_CARD.md] \\
        [--pilot-report docs/plans/PHASE_3_0_DATA_PILOT_REPORT.md] \\
        [--min-records 10] \\
        [--output report.json]

Exit:
    0 — 모든 자동 검증 PASS (manual 항목은 N/A로 카운트 제외)
    1 — 1+ 자동 검증 FAIL
    2 — 입력 누락 또는 사용 오류

원칙:
    - 외부 fetch 0 / LLM API 0 / engine simulation 수정 0
    - script-only — 사용자 승인 5+2건 *전*에도 정상 실행 가능 (모든 항목이 N/A 또는 FAIL로 표시됨)
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
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Check result dataclass
# ---------------------------------------------------------------------------

@dataclass
class AcceptanceCheck:
    """Phase 3.0 §18 단일 acceptance 항목 검증 결과."""
    item_id: int                    # 1-12
    name: str                       # 한글 항목명
    status: str                     # "PASS" | "FAIL" | "N/A" | "MANUAL" | "PENDING"
    category: str                   # "AUTO" | "MANUAL" | "HEURISTIC"
    detail: str = ""                # 검증 상세 (PASS/FAIL 사유)
    evidence: dict = field(default_factory=dict)  # 검증 시 참조한 데이터

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
# Approval checklist parser (Phase 3.05 cycle 7 — MANUAL → AUTO 하이브리드)
# ---------------------------------------------------------------------------

import re

_APPROVAL_HEADER_RE = re.compile(
    r"^###\s+([☐☑])\s+(\d+)\.\s+(.+)$",
    re.MULTILINE,
)


def parse_approval_checklist(text: str) -> list[dict]:
    """`### ☐ 1. ...` 또는 `### ☑ 1. ...` 헤더를 파싱.

    Returns:
        [{"item_no": int, "checked": bool, "title": str}, ...]
    """
    items = []
    for m in _APPROVAL_HEADER_RE.finditer(text):
        items.append({
            "item_no": int(m.group(2)),
            "checked": m.group(1) == "☑",
            "title": m.group(3).strip(),
        })
    return items


def _checklist_summary(items: list[dict]) -> dict:
    """전체/체크 갯수 + 미체크 list."""
    n_total = len(items)
    checked = [i for i in items if i["checked"]]
    n_checked = len(checked)
    unchecked = [i for i in items if not i["checked"]]
    return {
        "n_total": n_total,
        "n_checked": n_checked,
        "n_unchecked": len(unchecked),
        "unchecked_titles": [u["title"] for u in unchecked],
    }


# ---------------------------------------------------------------------------
# Individual checks (Plan §18 — 12 항목)
# ---------------------------------------------------------------------------

def check_01_approval(*, approval_doc: Path | None) -> AcceptanceCheck:
    """§18.1 — 사용자 승인 5+2건 완료.

    Phase 3.05 cycle 7: PHASE_3_0_APPROVAL_CHECKLIST.md가 존재하면 *체크박스 파싱*으로
    AUTO 판정 시도:
        - all checked (7/7) → PASS
        - partial → PENDING (N/A 카테고리)
        - 0 checked → PENDING (PHASE 시작 전)
    파일 없으면 MANUAL fallback.
    """
    if approval_doc is None or not approval_doc.exists():
        return AcceptanceCheck(
            item_id=1, name="사용자 승인 5+2건 완료",
            status="MANUAL", category="MANUAL",
            detail="approval checklist doc 미존재 — 사용자 외부 확인 필요",
        )

    items = parse_approval_checklist(approval_doc.read_text(encoding="utf-8"))
    s = _checklist_summary(items)
    if s["n_total"] == 0:
        return AcceptanceCheck(
            item_id=1, name="사용자 승인 5+2건 완료",
            status="MANUAL", category="MANUAL",
            detail=f"checklist 헤더 파싱 실패: {approval_doc.name} (`### ☐/☑ N. ...` 형식 필요)",
        )

    if s["n_checked"] == s["n_total"]:
        return AcceptanceCheck(
            item_id=1, name="사용자 승인 5+2건 완료",
            status="PASS", category="AUTO",
            detail=f"체크리스트 {s['n_checked']}/{s['n_total']} 모두 ☑ — 승인 완료",
            evidence={"n_checked": s["n_checked"], "n_total": s["n_total"]},
        )

    # partial — PENDING
    return AcceptanceCheck(
        item_id=1, name="사용자 승인 5+2건 완료",
        status="PENDING", category="AUTO",
        detail=(
            f"체크리스트 {s['n_checked']}/{s['n_total']} 체크됨. 미체크: "
            + ", ".join(s["unchecked_titles"][:3])
            + (f" 외 {len(s['unchecked_titles']) - 3}건" if len(s["unchecked_titles"]) > 3 else "")
        ),
        evidence={
            "n_checked": s["n_checked"],
            "n_total": s["n_total"],
            "unchecked_titles": s["unchecked_titles"],
        },
    )


def check_02_tos_review(
    *, source_review_doc: Path | None,
    approval_doc: Path | None = None,
) -> AcceptanceCheck:
    """§18.2 — source 후보 ToS / robots.txt 검토 완료.

    Phase 3.05 cycle 7: approval checklist 항목 #2 ("출처별 ToS / robots.txt 검토 승인")
    체크 여부로 AUTO 판정 시도. 없으면 doc 존재 여부로 약한 MANUAL.
    """
    # AUTO 판정 시도 — approval checklist #2 체크 여부
    if approval_doc and approval_doc.exists():
        items = parse_approval_checklist(approval_doc.read_text(encoding="utf-8"))
        tos_item = next((i for i in items if i["item_no"] == 2), None)
        if tos_item is not None:
            if tos_item["checked"]:
                return AcceptanceCheck(
                    item_id=2, name="source 후보 ToS / robots.txt 검토 완료",
                    status="PASS", category="AUTO",
                    detail=f"approval checklist #2 ☑: {tos_item['title']}",
                    evidence={"checklist_item_2_checked": True},
                )
            return AcceptanceCheck(
                item_id=2, name="source 후보 ToS / robots.txt 검토 완료",
                status="PENDING", category="AUTO",
                detail=f"approval checklist #2 ☐: {tos_item['title']} — 사용자 승인 대기",
                evidence={"checklist_item_2_checked": False},
            )

    # MANUAL fallback
    detail = "ToS / robots.txt 검토는 외부 활동 (manual)."
    if source_review_doc and source_review_doc.exists():
        detail += f" 후보 검토 doc: {source_review_doc.name}"
    return AcceptanceCheck(
        item_id=2, name="source 후보 ToS / robots.txt 검토 완료",
        status="MANUAL", category="MANUAL", detail=detail,
    )


def check_03_min_records(
    *, raw_private_dir: Path | None, min_records: int = 10,
) -> AcceptanceCheck:
    """§18.3 — N+ episode synopsis 확보. AUTO."""
    if raw_private_dir is None or not raw_private_dir.exists():
        return AcceptanceCheck(
            item_id=3, name=f"{min_records}+ episode synopsis 확보",
            status="FAIL", category="AUTO",
            detail=f"raw_private_dir 미지정 또는 미존재: {raw_private_dir}",
        )
    files = list(raw_private_dir.glob("*.json")) + list(raw_private_dir.glob("*.txt"))
    n = len(files)
    status = "PASS" if n >= min_records else "FAIL"
    return AcceptanceCheck(
        item_id=3, name=f"{min_records}+ episode synopsis 확보",
        status=status, category="AUTO",
        detail=f"raw synopsis 파일 {n} / 임계 {min_records}",
        evidence={"n_files": n, "threshold": min_records},
    )


def check_04_private_storage(
    *, raw_private_dir: Path | None, gitignore_path: Path,
) -> AcceptanceCheck:
    """§18.4 — raw synopsis가 공개 repo 밖이거나 gitignore 보호. AUTO."""
    # raw_private_dir이 git tracked area 안에 있다면 .gitignore에 명시되었는지
    if raw_private_dir is None:
        return AcceptanceCheck(
            item_id=4, name="raw synopsis가 공개 repo 밖 또는 gitignore 보호",
            status="FAIL", category="AUTO",
            detail="raw_private_dir 미지정",
        )
    gi_text = ""
    if gitignore_path.exists():
        gi_text = gitignore_path.read_text(encoding="utf-8")

    # raw_private_dir이 ROOT/data/external_private/ 같은 .gitignore 보호 path인지 휴리스틱 체크
    rel = None
    try:
        rel = raw_private_dir.resolve().relative_to(ROOT.resolve())
    except ValueError:
        rel = None  # ROOT 밖 (공개 repo 밖)

    if rel is None:
        return AcceptanceCheck(
            item_id=4, name="raw synopsis가 공개 repo 밖 또는 gitignore 보호",
            status="PASS", category="AUTO",
            detail=f"{raw_private_dir} is outside repo root → 공개 repo 밖",
            evidence={"location": "outside_repo"},
        )

    # repo 안: .gitignore 명시 필요
    rel_str = str(rel).replace("\\", "/")
    gitignore_patterns = [
        "data/external_private/",
        "external_private/",
        "data/annotation/phase3_pilot/per_annotator/",
        "data/annotation/phase3_pilot/synopsis_cache/",
    ]
    matched = [p for p in gitignore_patterns if p in gi_text]
    if any(rel_str.startswith(p.rstrip("/")) for p in matched):
        return AcceptanceCheck(
            item_id=4, name="raw synopsis가 공개 repo 밖 또는 gitignore 보호",
            status="PASS", category="AUTO",
            detail=f"{rel_str} matched in .gitignore",
            evidence={"location": "in_repo_gitignored", "matched_patterns": matched},
        )

    return AcceptanceCheck(
        item_id=4, name="raw synopsis가 공개 repo 밖 또는 gitignore 보호",
        status="FAIL", category="AUTO",
        detail=f"{rel_str} not protected by .gitignore",
        evidence={"location": "in_repo_unprotected"},
    )


def check_05_annotation_inputs(*, pilot_dir: Path) -> AcceptanceCheck:
    """§18.5 — annotation_inputs/*.json 생성. AUTO."""
    d = pilot_dir / "annotation_inputs"
    if not d.exists():
        return AcceptanceCheck(
            item_id=5, name="annotation_inputs/*.json 생성",
            status="FAIL", category="AUTO",
            detail=f"디렉토리 미존재: {d}",
        )
    files = list(d.glob("*.json"))
    n = len(files)
    status = "PASS" if n > 0 else "FAIL"
    return AcceptanceCheck(
        item_id=5, name="annotation_inputs/*.json 생성",
        status=status, category="AUTO",
        detail=f"annotation_inputs 파일 {n}",
        evidence={"n_files": n},
    )


def check_06_annotation_outputs(*, pilot_dir: Path) -> AcceptanceCheck:
    """§18.6 — annotation_outputs/*.json 확보. AUTO."""
    d = pilot_dir / "annotation_outputs"
    if not d.exists():
        return AcceptanceCheck(
            item_id=6, name="annotation_outputs/*.json 확보",
            status="FAIL", category="AUTO",
            detail=f"디렉토리 미존재: {d}",
        )
    files = list(d.glob("*.json"))
    n = len(files)
    status = "PASS" if n > 0 else "FAIL"
    return AcceptanceCheck(
        item_id=6, name="annotation_outputs/*.json 확보",
        status=status, category="AUTO",
        detail=f"annotation_outputs 파일 {n}",
        evidence={"n_files": n},
    )


def check_07_schema_validation(*, pilot_dir: Path) -> AcceptanceCheck:
    """§18.7 — schema validation 통과. AUTO."""
    report_path = pilot_dir / "reports" / "hallucination_report.json"
    if not report_path.exists():
        return AcceptanceCheck(
            item_id=7, name="annotation output schema validation 통과",
            status="FAIL", category="AUTO",
            detail=f"hallucination_report.json 미존재: {report_path}",
        )
    data = json.loads(report_path.read_text(encoding="utf-8"))
    invalid = data.get("invalid_files", [])
    n_invalid = len(invalid)
    if n_invalid > 0:
        return AcceptanceCheck(
            item_id=7, name="annotation output schema validation 통과",
            status="FAIL", category="AUTO",
            detail=f"invalid files {n_invalid} 존재 — schema 위반",
            evidence={"n_invalid_files": n_invalid,
                      "invalid_files_preview": invalid[:3]},
        )
    valid = data.get("valid_files_only_summary", {})
    n_valid = valid.get("n_files", 0)
    return AcceptanceCheck(
        item_id=7, name="annotation output schema validation 통과",
        status="PASS", category="AUTO",
        detail=f"valid files {n_valid} / invalid 0",
        evidence={"n_valid_files": n_valid, "n_invalid_files": 0},
    )


def check_08_hallucination_rate(
    *, pilot_dir: Path, threshold: float = 0.05,
) -> AcceptanceCheck:
    """§18.8 — hallucination rate < 5%. AUTO."""
    report_path = pilot_dir / "reports" / "hallucination_report.json"
    if not report_path.exists():
        return AcceptanceCheck(
            item_id=8, name="evidence quote hallucination rate < 5%",
            status="FAIL", category="AUTO",
            detail=f"hallucination_report.json 미존재: {report_path}",
        )
    data = json.loads(report_path.read_text(encoding="utf-8"))
    # Phase 3.05 — valid_files_only 기준
    valid = data.get("valid_files_only_summary", data)
    rate = float(valid.get("hallucination_rate", 1.0))
    status = "PASS" if rate < threshold else "FAIL"
    return AcceptanceCheck(
        item_id=8, name="evidence quote hallucination rate < 5%",
        status=status, category="AUTO",
        detail=f"hallucination_rate (valid_files_only) = {rate:.4f} / 임계 {threshold}",
        evidence={"hallucination_rate": rate, "threshold": threshold},
    )


def check_09_reliability(*, pilot_dir: Path, min_keep: int = 4) -> AcceptanceCheck:
    """§18.9 — 최소 4 feature r ≥ 0.7 (KEEP). AUTO."""
    rel_path = pilot_dir / "reports" / "reliability.json"
    if not rel_path.exists():
        return AcceptanceCheck(
            item_id=9, name="최소 4 feature inter-annotator r ≥ 0.7",
            status="FAIL", category="AUTO",
            detail=f"reliability.json 미존재: {rel_path}",
        )
    data = json.loads(rel_path.read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    keep = summary.get("keep", [])
    n_keep = len(keep) if isinstance(keep, list) else 0
    status = "PASS" if n_keep >= min_keep else "FAIL"
    return AcceptanceCheck(
        item_id=9, name=f"최소 {min_keep} feature inter-annotator r ≥ 0.7",
        status=status, category="AUTO",
        detail=f"KEEP feature {n_keep} / 임계 {min_keep}: {keep}",
        evidence={"n_keep": n_keep, "keep_features": keep, "threshold": min_keep},
    )


def check_10_verdict(*, pilot_dir: Path) -> AcceptanceCheck:
    """§18.10 — KEEP / REVISE / DROP 판정 완료. AUTO."""
    rel_path = pilot_dir / "reports" / "reliability.json"
    if not rel_path.exists():
        return AcceptanceCheck(
            item_id=10, name="feature KEEP / REVISE / DROP 판정 완료",
            status="FAIL", category="AUTO",
            detail=f"reliability.json 미존재: {rel_path}",
        )
    data = json.loads(rel_path.read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    required = ("keep", "revise", "drop")
    missing = [k for k in required if k not in summary]
    if missing:
        return AcceptanceCheck(
            item_id=10, name="feature KEEP / REVISE / DROP 판정 완료",
            status="FAIL", category="AUTO",
            detail=f"reliability.summary에 누락 키: {missing}",
        )
    return AcceptanceCheck(
        item_id=10, name="feature KEEP / REVISE / DROP 판정 완료",
        status="PASS", category="AUTO",
        detail=f"keep={len(summary['keep'])} / revise={len(summary['revise'])} / drop={len(summary['drop'])}",
        evidence={
            "n_keep": len(summary["keep"]),
            "n_revise": len(summary["revise"]),
            "n_drop": len(summary["drop"]),
        },
    )


# Data Card / Pilot Report template heuristic markers (template 그대로면 fail로 추정)
_TEMPLATE_MARKERS = (
    "{{",          # Jinja-style placeholder
    "TODO",
    "TBD",
    "(fill",
    "(작성",
    "<<<",
    "[작성]",
)


def _looks_like_unfilled_template(text: str) -> bool:
    """Template이 채워지지 않은 상태인지 휴리스틱 추정."""
    if not text or len(text) < 200:
        return True
    n_markers = sum(text.count(m) for m in _TEMPLATE_MARKERS)
    # marker가 5개 이상이면 template 미작성 추정
    return n_markers >= 5


def check_11_data_card(*, data_card: Path | None) -> AcceptanceCheck:
    """§18.11 — Data Card 작성. HEURISTIC."""
    if data_card is None or not data_card.exists():
        return AcceptanceCheck(
            item_id=11, name="Data Card 작성",
            status="FAIL", category="HEURISTIC",
            detail=f"Data Card 파일 미존재: {data_card}",
        )
    text = data_card.read_text(encoding="utf-8")
    if _looks_like_unfilled_template(text):
        return AcceptanceCheck(
            item_id=11, name="Data Card 작성",
            status="FAIL", category="HEURISTIC",
            detail="template marker (TODO/TBD/{{...}}) 다수 발견 — 작성 미완료 추정",
            evidence={"size_bytes": len(text)},
        )
    return AcceptanceCheck(
        item_id=11, name="Data Card 작성",
        status="PASS", category="HEURISTIC",
        detail=f"Data Card 작성됨 (size={len(text)} bytes, marker 적음)",
        evidence={"size_bytes": len(text)},
    )


def check_12_go_no_go(*, pilot_report: Path | None) -> AcceptanceCheck:
    """§18.12 — Phase 3.1 Go / No-Go 판정. HEURISTIC."""
    if pilot_report is None or not pilot_report.exists():
        return AcceptanceCheck(
            item_id=12, name="Phase 3.1 Go / No-Go 판정 작성",
            status="FAIL", category="HEURISTIC",
            detail=f"Pilot Report 파일 미존재: {pilot_report}",
        )
    text = pilot_report.read_text(encoding="utf-8")
    if _looks_like_unfilled_template(text):
        return AcceptanceCheck(
            item_id=12, name="Phase 3.1 Go / No-Go 판정 작성",
            status="FAIL", category="HEURISTIC",
            detail="template marker 다수 발견 — 작성 미완료 추정",
            evidence={"size_bytes": len(text)},
        )
    # 판정 명시 여부 — "GO" / "NO-GO" / "CONDITIONAL_GO" 키워드 체크
    has_verdict = any(k in text for k in ("GO", "NO-GO", "CONDITIONAL"))
    if not has_verdict:
        return AcceptanceCheck(
            item_id=12, name="Phase 3.1 Go / No-Go 판정 작성",
            status="FAIL", category="HEURISTIC",
            detail="Go/No-Go/Conditional 판정 키워드 미발견",
        )
    return AcceptanceCheck(
        item_id=12, name="Phase 3.1 Go / No-Go 판정 작성",
        status="PASS", category="HEURISTIC",
        detail="Pilot Report 작성됨 + Go/No-Go 판정 키워드 발견",
        evidence={"size_bytes": len(text)},
    )


# ---------------------------------------------------------------------------
# Top-level runner
# ---------------------------------------------------------------------------

def run_all_checks(
    *,
    pilot_dir: Path,
    raw_private_dir: Path | None = None,
    data_card: Path | None = None,
    pilot_report: Path | None = None,
    approval_doc: Path | None = None,
    source_review_doc: Path | None = None,
    gitignore_path: Path | None = None,
    min_records: int = 10,
) -> list[AcceptanceCheck]:
    """12 acceptance 항목 검증."""
    if gitignore_path is None:
        gitignore_path = ROOT / ".gitignore"
    return [
        check_01_approval(approval_doc=approval_doc),
        check_02_tos_review(source_review_doc=source_review_doc, approval_doc=approval_doc),
        check_03_min_records(raw_private_dir=raw_private_dir, min_records=min_records),
        check_04_private_storage(
            raw_private_dir=raw_private_dir, gitignore_path=gitignore_path,
        ),
        check_05_annotation_inputs(pilot_dir=pilot_dir),
        check_06_annotation_outputs(pilot_dir=pilot_dir),
        check_07_schema_validation(pilot_dir=pilot_dir),
        check_08_hallucination_rate(pilot_dir=pilot_dir),
        check_09_reliability(pilot_dir=pilot_dir),
        check_10_verdict(pilot_dir=pilot_dir),
        check_11_data_card(data_card=data_card),
        check_12_go_no_go(pilot_report=pilot_report),
    ]


def summarize(checks: list[AcceptanceCheck]) -> dict:
    """검증 결과 요약. PENDING은 fail이 아니지만 pass도 아님 (사용자 승인 대기)."""
    auto = [c for c in checks if c.category == "AUTO"]
    heuristic = [c for c in checks if c.category == "HEURISTIC"]
    manual = [c for c in checks if c.category == "MANUAL"]

    auto_pass = sum(1 for c in auto if c.status == "PASS")
    auto_fail = sum(1 for c in auto if c.status == "FAIL")
    auto_pending = sum(1 for c in auto if c.status == "PENDING")
    heuristic_pass = sum(1 for c in heuristic if c.status == "PASS")
    heuristic_fail = sum(1 for c in heuristic if c.status == "FAIL")

    all_auto_pass = (auto_fail == 0 and auto_pending == 0)
    all_pass = all_auto_pass and (heuristic_fail == 0)

    return {
        "n_total": len(checks),
        "n_auto": len(auto),
        "n_heuristic": len(heuristic),
        "n_manual": len(manual),
        "auto_pass": auto_pass,
        "auto_fail": auto_fail,
        "auto_pending": auto_pending,
        "heuristic_pass": heuristic_pass,
        "heuristic_fail": heuristic_fail,
        "manual_count": len(manual),
        "all_auto_pass": all_auto_pass,
        "all_pass_including_heuristic": all_pass,
    }


def render_markdown_report(checks: list[AcceptanceCheck], summary: dict) -> str:
    """Phase 3.05 cycle 11 — markdown 보고서 (사용자 공식 문서로 활용 가능)."""
    from datetime import datetime
    lines = []
    lines.append("# Phase 3.0 §18 Acceptance Verification Report")
    lines.append("")
    lines.append(f"> Generated: {datetime.now().isoformat(timespec='seconds')}  ")
    lines.append("> Tool: `scripts/data/verify_phase3_0_acceptance.py` (Phase 3.05)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    pending = summary.get("auto_pending", 0)
    lines.append(
        f"- **AUTO** ({summary['n_auto']} 항목): "
        f"{summary['auto_pass']} PASS / {summary['auto_fail']} FAIL"
        + (f" / {pending} PENDING" if pending else "")
    )
    lines.append(
        f"- **HEURISTIC** ({summary['n_heuristic']} 항목): "
        f"{summary['heuristic_pass']} PASS / {summary['heuristic_fail']} FAIL"
    )
    lines.append(
        f"- **MANUAL** ({summary['n_manual']} 항목): 사용자 외부 확인 필요"
    )
    if summary["all_auto_pass"]:
        lines.append("")
        lines.append("✓ **모든 AUTO 검증 통과**. Phase 3.0 acceptance 자동화 부분 완료.")
    elif summary["auto_fail"] == 0 and pending > 0:
        lines.append("")
        lines.append("~ **AUTO PENDING 존재** — 사용자 승인 진행 중 (FAIL 아님).")
    else:
        lines.append("")
        lines.append("✗ **AUTO FAIL 존재** — 아래 미충족 항목 확인 필요.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 12 Acceptance 항목별 결과")
    lines.append("")
    lines.append("| § | 항목 | Category | Status | 상세 |")
    lines.append("|---|---|---|---|---|")
    for c in checks:
        status_md = {
            "PASS": "✓ PASS",
            "FAIL": "✗ FAIL",
            "N/A": "− N/A",
            "MANUAL": "? MANUAL",
            "PENDING": "~ PENDING",
        }.get(c.status, c.status)
        # escape | in detail
        detail = c.detail.replace("|", "\\|") if c.detail else "-"
        lines.append(
            f"| 18.{c.item_id} | {c.name} | `{c.category}` | **{status_md}** | {detail} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 분류 의미")
    lines.append("")
    lines.append("- **AUTO**: 코드로 자동 검증. exit code에 반영.")
    lines.append("- **HEURISTIC**: Data Card / Pilot Report 작성 추정 (template marker 검사). exit code에 영향 0.")
    lines.append("- **MANUAL**: 외부 활동 (사용자 환경에 doc 미존재 시 fallback).")
    lines.append("")
    lines.append("## Status 의미")
    lines.append("")
    lines.append("- **PASS**: 모든 조건 통과.")
    lines.append("- **FAIL**: 필수 조건 미충족 (exit 1 트리거 — AUTO인 경우만).")
    lines.append("- **PENDING**: 사용자 승인 진행 중 (FAIL 아님, exit 0).")
    lines.append("- **MANUAL**: 자동 검증 불가, 사용자 외부 확인 필요.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> Plan §18 reference: `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §18")
    return "\n".join(lines)


def render_text_report(checks: list[AcceptanceCheck], summary: dict) -> str:
    """사람이 읽기 좋은 텍스트 보고서."""
    lines = []
    lines.append("=" * 72)
    lines.append("Phase 3.0 §18 Acceptance Criteria — 자동 검증 결과")
    lines.append("=" * 72)
    lines.append("")
    for c in checks:
        status_tag = {
            "PASS": "[O]",
            "FAIL": "[X]",
            "N/A": "[-]",
            "MANUAL": "[?]",
            "PENDING": "[~]",
        }.get(c.status, "[ ]")
        lines.append(
            f"{status_tag} §18.{c.item_id} ({c.category:9s}): {c.name}"
        )
        if c.detail:
            lines.append(f"      → {c.detail}")
        lines.append("")
    lines.append("-" * 72)
    lines.append("Summary:")
    pending = summary.get("auto_pending", 0)
    pending_str = f" + {pending} PENDING" if pending else ""
    lines.append(
        f"  AUTO       : {summary['auto_pass']}/{summary['n_auto']} PASS "
        f"({summary['auto_fail']} FAIL{pending_str})"
    )
    lines.append(
        f"  HEURISTIC  : {summary['heuristic_pass']}/{summary['n_heuristic']} PASS "
        f"({summary['heuristic_fail']} FAIL)"
    )
    lines.append(
        f"  MANUAL     : {summary['n_manual']} 항목 — 사용자 외부 확인 필요"
    )
    lines.append("")
    if summary["all_auto_pass"]:
        lines.append("✓ 모든 AUTO 검증 통과.")
    elif summary["auto_fail"] == 0 and pending > 0:
        lines.append("~ AUTO PENDING 존재 — 사용자 승인 대기 (FAIL 아님, 진행 중).")
    else:
        lines.append("✗ AUTO FAIL 존재 — 위 항목 확인 필요.")
    if not summary["all_pass_including_heuristic"] and summary["all_auto_pass"]:
        lines.append("⚠ HEURISTIC FAIL 존재 — Data Card / Pilot Report 작성 권장.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pilot-dir", required=True, type=Path,
                     help="data/annotation/phase3_pilot/")
    ap.add_argument("--raw-private-dir", type=Path, default=None,
                     help="raw synopsis 디렉토리 (default: data/external_private/synopsis_raw)")
    ap.add_argument("--data-card", type=Path, default=None,
                     help="Data Card path (default: docs/plans/PHASE_3_0_DATA_CARD.md)")
    ap.add_argument("--pilot-report", type=Path, default=None,
                     help="Pilot Report path (default: docs/plans/PHASE_3_0_DATA_PILOT_REPORT.md)")
    ap.add_argument("--approval-doc", type=Path, default=None,
                     help="(default: docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md)")
    ap.add_argument("--source-review-doc", type=Path, default=None,
                     help="(default: docs/plans/DATA_SOURCE_CANDIDATE_REVIEW.md)")
    ap.add_argument("--gitignore", type=Path, default=None,
                     help="default: <ROOT>/.gitignore")
    ap.add_argument("--min-records", type=int, default=10,
                     help="§18.3 최소 episode 수 (default 10)")
    ap.add_argument("--output", type=Path, default=None,
                     help="JSON report output path (optional)")
    ap.add_argument("--md-report", type=Path, default=None,
                     help="markdown 보고서 output path (cycle 11) — 사용자가 공식 문서로 첨부 가능")
    args = ap.parse_args(argv)

    if not args.pilot_dir.exists():
        # acceptance가 *시작 전*인 정상 상태 — 모든 AUTO가 FAIL 되겠지만 exit는 1
        print(f"WARN: pilot-dir 미존재: {args.pilot_dir}", file=sys.stderr)

    # defaults
    raw_private = args.raw_private_dir or (ROOT / "data/external_private/synopsis_raw")
    data_card = args.data_card or (ROOT / "docs/plans/PHASE_3_0_DATA_CARD.md")
    pilot_report = args.pilot_report or (ROOT / "docs/plans/PHASE_3_0_DATA_PILOT_REPORT.md")
    approval_doc = args.approval_doc or (ROOT / "docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md")
    source_review = args.source_review_doc or (
        ROOT / "docs/plans/DATA_SOURCE_CANDIDATE_REVIEW.md"
    )

    checks = run_all_checks(
        pilot_dir=args.pilot_dir,
        raw_private_dir=raw_private,
        data_card=data_card,
        pilot_report=pilot_report,
        approval_doc=approval_doc,
        source_review_doc=source_review,
        gitignore_path=args.gitignore,
        min_records=args.min_records,
    )
    summary = summarize(checks)

    print(render_text_report(checks, summary))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps({
                "checks": [c.to_dict() for c in checks],
                "summary": summary,
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nJSON report → {args.output}")

    if args.md_report:
        args.md_report.parent.mkdir(parents=True, exist_ok=True)
        args.md_report.write_text(
            render_markdown_report(checks, summary), encoding="utf-8",
        )
        print(f"Markdown report → {args.md_report}")

    # exit codes
    if summary["auto_fail"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
