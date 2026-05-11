"""Phase 3.0 v1.1 Pipeline — normalized JSONL → public-safe metadata only.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §9.2 + §8.3.

원본 synopsis_text는 *제거*하고 metadata만 남긴 dataset 생성. 공개 repo 또는
포트폴리오 HTML에 *원문 노출 0*을 보장.

입력: data/annotation/phase3_pilot/normalized_synopsis.jsonl
출력: data/annotation/phase3_pilot/public_safe_dataset.jsonl

Public-safe schema (§9.2):
    {
      "record_id": "...",
      "genre_id": "...",
      "title_id": "...",
      "episode_number": ...,
      "source_name": "...",
      "public_safe_summary": "redacted",
      "annotation_available": bool
    }

원칙:
    - synopsis_text 제거
    - public_safe_summary는 사용자가 직접 작성한 *짧은* (≤ 100자) 요약만 보존
    - 그 외엔 "redacted"
    - source_url은 *제거* (저작권 보호)
    - annotation_available은 별도 인덱스 파일이 있으면 True

사용:
    python scripts/data/build_public_safe_dataset.py \\
        --input data/annotation/phase3_pilot/normalized_synopsis.jsonl \\
        --output data/annotation/phase3_pilot/public_safe_dataset.jsonl \\
        --max-summary-length 100
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


PUBLIC_SAFE_SCHEMA_VERSION = "public_safe_dataset_v1"


def make_public_safe(record: dict, max_summary_len: int) -> dict:
    """원본 record → public-safe variant (synopsis_text 제거)."""
    summary = record.get("public_safe_summary", "") or ""
    if len(summary) > max_summary_len:
        summary = summary[:max_summary_len].rstrip() + "…"
    if not summary:
        summary = "redacted"
    return {
        "schema_version": PUBLIC_SAFE_SCHEMA_VERSION,
        "record_id": record["record_id"],
        "genre_id": record["genre_id"],
        "title_id": record["title_id"],
        "episode_number": record["episode_number"],
        "source_name": record.get("source_name", ""),
        # source_url은 의도적 제거
        "public_safe_summary": summary,
        "annotation_available": False,  # 외부 인덱스가 채워줌
    }


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path,
                     help="normalized_synopsis.jsonl path")
    ap.add_argument("--output", required=True, type=Path,
                     help="public_safe_dataset.jsonl output path")
    ap.add_argument("--max-summary-length", type=int, default=100,
                     help="max chars for public_safe_summary (default 100)")
    ap.add_argument("--annotation-index", type=Path, default=None,
                     help="optional dir with annotation_outputs to mark "
                          "annotation_available=True per record")
    args = ap.parse_args(argv)

    if not args.input.exists():
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        return 2

    records = load_jsonl(args.input)

    # annotation_available 인덱스
    available: set[str] = set()
    if args.annotation_index and args.annotation_index.exists():
        for path in args.annotation_index.glob("*.json"):
            try:
                d = json.loads(path.read_text(encoding="utf-8"))
                rid = d.get("record_id", "")
                if rid:
                    available.add(rid)
            except json.JSONDecodeError:
                continue

    args.output.parent.mkdir(parents=True, exist_ok=True)
    n_with_summary = 0
    n_redacted = 0
    with args.output.open("w", encoding="utf-8") as fp:
        for r in records:
            ps = make_public_safe(r, args.max_summary_length)
            if ps["record_id"] in available:
                ps["annotation_available"] = True
            if ps["public_safe_summary"] == "redacted":
                n_redacted += 1
            else:
                n_with_summary += 1
            # 안전 검증: synopsis_text 절대 없어야
            assert "synopsis_text" not in ps, (
                f"public-safe leak: synopsis_text in {ps['record_id']}"
            )
            fp.write(json.dumps(ps, ensure_ascii=False) + "\n")

    print(f"OK: {len(records)} public-safe records → {args.output}")
    print(f"  with summary: {n_with_summary}")
    print(f"  redacted:     {n_redacted}")
    print(f"  annotation_available: {len(available)} records linked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
