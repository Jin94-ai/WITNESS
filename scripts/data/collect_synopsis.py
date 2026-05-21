"""Synopsis collection orchestrator skeleton (Phase 1).

Per `docs/witness_narrative_mode_plan.md` §5 and `docs/data/SELECTION_CRITERIA.md`:

This script *does not perform network IO yet*. It establishes the CLI surface,
the validation pipeline, and the on-disk layout. Actual fetchers will be
added per-source after ToS / robots.txt review.

Why a skeleton first?
    Plan §5.5 — "사용 전 출처별 ToS 확인. 가능하면 공식 API/덤프 사용."
    수집 도구가 *먼저* 라이선스 / ToS 검증 stage를 통과하지 않은 채로
    네트워크 호출을 만들면, 사용자도 모르게 ToS 위반이 발생할 수 있다.
    이 스크립트는 manual ToS-cleared input → 검증된 EpisodeSynopsis 작성만 한다.

Usage:
    # 수동으로 작성한 synopsis JSON 파일을 검증하고 정규 위치에 저장
    python scripts/data/collect_synopsis.py validate <path.json>

    # _selection_log.json에서 후보 목록 보기
    python scripts/data/collect_synopsis.py list-candidates --category melodrama
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

from scripts.data.synopsis_schema import (  # noqa: E402
    EpisodeSynopsis,
    now_iso_utc,
    validate_episode_dict,
    write_episode,
)

# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_validate(args) -> int:
    """Validate a manually-prepared synopsis JSON and write to canonical path.

    Input file must already follow the schema. This command checks structure
    and writes to data/raw/{category}/{title_id}/episodes/.
    """
    p = Path(args.path)
    if not p.exists():
        print(f"ERROR: file not found: {p}", file=sys.stderr)
        return 1
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON: {e}", file=sys.stderr)
        return 1
    errs = validate_episode_dict(d)
    if errs:
        print("Validation errors:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    # Re-write in canonical location
    syn = EpisodeSynopsis(
        title_id=d["title_id"],
        title_ko=d["title_ko"],
        title_en=d["title_en"],
        category=d["category"],
        episode_no=int(d["episode_no"]),
        synopsis_text_ko=d["synopsis_text_ko"],
        source_url=d["source_url"],
        source_license=d["source_license"],
        fetched_at_iso=d.get("fetched_at_iso") or now_iso_utc(),
        fetcher_version=d.get("fetcher_version", "manual_v1"),
        notes=list(d.get("notes", [])),
    )
    out = write_episode(syn)
    print(f"OK: written {out.relative_to(ROOT)}")
    return 0


def cmd_list_candidates(args) -> int:
    log_path = (
        ROOT / "data" / "raw" / args.category / "_selection_log.json"
    )
    if not log_path.exists():
        print(f"ERROR: selection log missing: {log_path}", file=sys.stderr)
        return 1
    log = json.loads(log_path.read_text(encoding="utf-8"))
    candidates = log.get("candidates", [])
    if not candidates:
        print(f"No candidates yet in {args.category}.")
        return 0
    for c in candidates:
        marker = "✓" if c.get("selected", False) else "x"
        print(
            f"  [{marker}] {c.get('title_id', '?'):<30s} "
            f"{c.get('title_ko', '?'):<25s} "
            f"({c.get('year_start', '?')})"
        )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser(
        "validate",
        help="Validate a synopsis JSON file and store it in canonical location.",
    )
    v.add_argument("path", help="Path to manually-prepared synopsis JSON.")
    v.set_defaults(func=cmd_validate)

    lc = sub.add_parser(
        "list-candidates",
        help="List candidates from a selection log.",
    )
    lc.add_argument("--category", choices=["melodrama", "control"], required=True)
    lc.set_defaults(func=cmd_list_candidates)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(cli())
