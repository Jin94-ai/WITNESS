"""LLM annotation orchestrator skeleton (Phase 2).

Per `docs/witness_narrative_mode_plan.md` §6 Phase 2 산출물:
    scripts/annotation/annotate_with_llm.py

이 스크립트는 *네트워크 호출 0*. 두 가지 모드를 지원한다:

1. **dry-run mode**: 회차 줄거리를 읽어 LLM에 보낼 *prompt만 빌드*하고 디스크에
   저장한다. 실제 호출은 사용자가 수동으로 (또는 별도 LLM client 스크립트로)
   수행한 뒤 응답 JSON을 받아온다.

2. **fixture mode**: 미리 준비된 dummy 응답 JSON을 읽어 검증 + 정규 위치에
   저장한다. CI / 통합 테스트에서 LLM 호출 없이 파이프라인 무결성 확인용.

실제 LLM 호출 모드 (`--mode live`)는 *plan §5.5 "사용 전 출처별 ToS 확인"*과
LLM provider key 관리가 마무리된 뒤 별도 turn에서 추가한다.

Usage:
    # dry-run: 줄거리 + 어노테이터 id → prompt 파일 생성
    python scripts/annotation/annotate_with_llm.py dry-run \\
        --episode data/raw/melodrama/{title}/episodes/05.json \\
        --annotator-id claude-3.5-sonnet \\
        --output prompts/{title}/05_claude.txt

    # fixture: 미리 준비된 LLM 응답을 정규 위치에 검증 후 저장
    python scripts/annotation/annotate_with_llm.py fixture \\
        --response path/to/llm_response.json \\
        --output data/annotated/_per_annotator/{annotator_id}/{title}/05.json
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _ensure_utf8_stdout() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace",
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace",
            )
        except Exception:
            pass


_ensure_utf8_stdout()

from scripts.annotation.prompt_templates import (  # noqa: E402
    SYSTEM_PROMPT_KO,
    build_user_prompt_ko,
    hallucination_rate,
    validate_annotation_dict,
    validate_evidence_quotes,
    ANNOTATION_SCHEMA_VERSION,
)
from scripts.data.synopsis_schema import (  # noqa: E402
    REQUIRED_EPISODE_FIELDS,
    SCHEMA_VERSION as SYNOPSIS_SCHEMA_VERSION,
)


# ---------------------------------------------------------------------------
# Prompt builder (used by dry-run mode + future live mode)
# ---------------------------------------------------------------------------

def build_prompt_pair(synopsis: dict) -> tuple[str, str]:
    """Episode synopsis dict → (system_prompt, user_prompt). LLM-agnostic."""
    title_ko = synopsis.get("title_ko") or synopsis.get("title_id", "(제목 미상)")
    episode_no = int(synopsis.get("episode_no", 0))
    synopsis_text = synopsis.get("synopsis_text_ko", "")
    user_prompt = build_user_prompt_ko(synopsis_text, episode_no, title_ko)
    return SYSTEM_PROMPT_KO, user_prompt


def _validate_synopsis(d: dict) -> list[str]:
    errs: list[str] = []
    for f in REQUIRED_EPISODE_FIELDS:
        if f not in d:
            errs.append(f"missing field: {f}")
    if d.get("schema_version") and d["schema_version"] != SYNOPSIS_SCHEMA_VERSION:
        errs.append(
            f"schema_version mismatch: got {d['schema_version']!r}, "
            f"expected {SYNOPSIS_SCHEMA_VERSION!r}"
        )
    return errs


# ---------------------------------------------------------------------------
# dry-run mode — build prompt, write to file
# ---------------------------------------------------------------------------

def cmd_dry_run(args) -> int:
    p = Path(args.episode)
    if not p.exists():
        print(f"ERROR: episode synopsis not found: {p}", file=sys.stderr)
        return 1
    syn = json.loads(p.read_text(encoding="utf-8"))
    errs = _validate_synopsis(syn)
    if errs:
        print("ERROR: episode synopsis invalid:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    system, user = build_prompt_pair(syn)

    # Header annotation so downstream LLM caller can wire up easily.
    header = (
        f"# WITNESS Narrative Mode annotation prompt\n"
        f"# title_id: {syn.get('title_id')}\n"
        f"# episode_no: {syn.get('episode_no')}\n"
        f"# annotator_id: {args.annotator_id}\n"
        f"# schema_target: {ANNOTATION_SCHEMA_VERSION}\n"
        f"# notes: send the following {{system, user}} pair to the LLM.\n"
        f"#   parse the JSON response, then run\n"
        f"#   `python scripts/annotation/annotate_with_llm.py fixture "
        f"--response <response.json> --output <path>`\n"
        f"\n"
    )
    body = (
        f"=== SYSTEM PROMPT ===\n{system}\n\n"
        f"=== USER PROMPT ===\n{user}\n"
    )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(header + body, encoding="utf-8")
    print(f"OK: prompt written → {out}")
    return 0


# ---------------------------------------------------------------------------
# fixture mode — validate + save LLM response (real or dummy)
# ---------------------------------------------------------------------------

def cmd_fixture(args) -> int:
    p = Path(args.response)
    if not p.exists():
        print(f"ERROR: response not found: {p}", file=sys.stderr)
        return 1
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON: {e}", file=sys.stderr)
        return 1

    # Phase 2.5 cycle 7: optional v1 → v1.1 auto-migration
    if getattr(args, "migrate_deprecated", False):
        from scripts.annotation.prompt_templates import migrate_deprecated_annotation
        d = migrate_deprecated_annotation(d)

    errs = validate_annotation_dict(d)
    if errs:
        print("ERROR: response not a valid annotation:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        if any("missing feature" in e for e in errs) and not getattr(
            args, "migrate_deprecated", False
        ):
            print(
                "  HINT: --migrate-deprecated 로 v1 → v1.1 자동 변환 시도 "
                "(conflict_amplification_rate / resolution_to_dangling_ratio 매핑)",
                file=sys.stderr,
            )
        return 1

    # Optional evidence-quote validation against original synopsis (LLM
    # hallucination check). Per ANNOTATION_GUIDE §3.2.
    halluc_rate: float | None = None
    if args.synopsis:
        syn_path = Path(args.synopsis)
        if not syn_path.exists():
            print(f"ERROR: synopsis not found: {syn_path}", file=sys.stderr)
            return 1
        syn = json.loads(syn_path.read_text(encoding="utf-8"))
        synopsis_text = syn.get("synopsis_text_ko", "")
        quote_errs = validate_evidence_quotes(d, synopsis_text)
        if quote_errs:
            print(
                "WARNING: evidence_quote validation issues "
                f"({len(quote_errs)}):", file=sys.stderr,
            )
            for e in quote_errs:
                print(f"  - {e}", file=sys.stderr)
            if args.strict_quotes:
                print(
                    "ERROR: --strict-quotes set; refusing to save.",
                    file=sys.stderr,
                )
                return 1
        halluc_rate = hallucination_rate(d, synopsis_text)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(d, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK: annotation saved → {out}")
    info = (
        f"  title_id: {d.get('title_id')} · episode_no: {d.get('episode_no')} · "
        f"annotator: {d.get('annotator_id')} · confidence: {d.get('confidence')}"
    )
    if halluc_rate is not None:
        info += f" · hallucination_rate: {halluc_rate:.2f}"
    print(info)
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    dr = sub.add_parser("dry-run",
                          help="Build LLM prompt from an episode synopsis (no network call)")
    dr.add_argument("--episode", required=True,
                     help="Path to episode synopsis JSON (synopsis_v1)")
    dr.add_argument("--annotator-id", required=True,
                     help="Annotator label (e.g. 'claude-3.5-sonnet')")
    dr.add_argument("--output", required=True,
                     help="Where to write the {system, user} prompt text")
    dr.set_defaults(func=cmd_dry_run)

    fx = sub.add_parser("fixture",
                          help="Validate an LLM response and save to canonical location")
    fx.add_argument("--response", required=True,
                     help="Path to LLM response JSON (annotation_v1)")
    fx.add_argument("--output", required=True,
                     help="Where to save the validated annotation")
    fx.add_argument(
        "--synopsis", default=None,
        help="(Optional) original episode synopsis JSON. If provided, each "
             "evidence_quote is checked against the synopsis text "
             "(LLM hallucination guard).",
    )
    fx.add_argument(
        "--strict-quotes", action="store_true",
        help="With --synopsis: refuse to save if any evidence_quote is "
             "not found in the synopsis (default: warn only).",
    )
    fx.add_argument(
        "--migrate-deprecated", action="store_true",
        help=(
            "Phase 2.5: v1 어노테이션 응답의 conflict_amplification_rate / "
            "resolution_to_dangling_ratio 필드를 v1.1 이름으로 자동 변환 후 "
            "검증/저장 (재 어노테이션 없이 backward-compat)."
        ),
    )
    fx.set_defaults(func=cmd_fixture)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(cli())
