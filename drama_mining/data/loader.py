"""AI-Hub 023 ZIP loader — streaming JSON parsing.

Per docs/witness_dm_day2_directive.md §2.

기본 사용:
    from drama_mining.data.loader import stream_aihub_023, count_by_category
    for entry in stream_aihub_023(zip_path, categories=["fm_drama", "fs_drama"]):
        ...

CLI (실제 TL1.zip 검증용):
    python -m drama_mining.data.loader \
        --zip-path "data/023.방송 콘텐츠 대본 요약 데이터/01.데이터/1.Training/라벨링데이터/TL1.zip" \
        --count
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Iterator

# 가능한 AI-Hub 023 데이터 root (Day 1 AIHUB_023_PATH.md 참조)
AIHUB_023_ROOT_CANDIDATES = [
    Path("data/aihub_023/01.데이터"),
    Path("data/023.방송 콘텐츠 대본 요약 데이터/01.데이터"),
]

# 6 doc_type 카테고리
KNOWN_CATEGORIES = ("enter", "fm_drama", "fs_drama", "c_event", "history", "culture")
# 2 summary modes (디렉토리/파일명에서 추출)
KNOWN_SUMMARY_MODES = ("20per", "3sent")


def find_aihub_023_root() -> Path | None:
    """plan §5 / Day 1 AIHUB_023_PATH.md 의 두 후보 중 존재하는 것 반환."""
    for candidate in AIHUB_023_ROOT_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def _extract_summary_mode(zip_internal_path: str) -> str:
    """ZIP 내부 경로에서 '20per' 또는 '3sent' 추출. 없으면 빈 문자열."""
    for mode in KNOWN_SUMMARY_MODES:
        if f"/{mode}/" in zip_internal_path:
            return mode
    return ""


def _flatten_entry(raw: dict, summary_mode: str) -> dict:
    """AI-Hub 023 nested JSON을 평탄화."""
    meta = raw.get("Meta", {}) or {}
    annotation = raw.get("Annotation", {}) or {}
    return {
        "doc_id": meta.get("doc_id", ""),
        "doc_type": meta.get("doc_type", ""),
        "doc_origin": meta.get("doc_origin", ""),
        "passage_id": meta.get("passage_id", ""),
        "passage": meta.get("passage", ""),
        "summary_1": annotation.get("Summary1", "") or "",
        "summary_3": annotation.get("Summary3", "") or "",
        "published_year": meta.get("published_year", "") or "",
        "summary_mode": summary_mode,
    }


def stream_aihub_023(
    zip_path: Path,
    categories: list[str] | None = None,
    *,
    skip_logger=None,
) -> Iterator[dict]:
    """AI-Hub 023 ZIP에서 라벨 JSON을 한 건씩 yield.

    Args:
        zip_path: TL1.zip 또는 VL1.zip 경로.
        categories: 필터링할 doc_type 리스트 (예: ["fm_drama", "fs_drama"]).
            None이면 전체.
        skip_logger: optional callable(reason: str, path: str) — 손상된 entry 보고.

    Yields:
        평탄화된 dict (doc_id, doc_type, doc_origin, passage_id, passage,
        summary_1, summary_3, published_year, summary_mode).

    Raises:
        FileNotFoundError: zip_path 부재.
        zipfile.BadZipFile: 손상된 ZIP.

    Note:
        손상된 JSON 1건은 skip + warning. 전체 중단하지 않음.
    """
    zip_path = Path(zip_path)
    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP not found: {zip_path}")

    cat_filter = set(categories) if categories else None

    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir() or not info.filename.endswith(".json"):
                continue

            # quick category filter (디렉토리 prefix가 카테고리)
            internal = info.filename
            parts = internal.split("/")
            if cat_filter is not None:
                if not parts or parts[0] not in cat_filter:
                    continue

            summary_mode = _extract_summary_mode(internal)
            try:
                with zf.open(info) as f:
                    payload = json.loads(f.read().decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                if skip_logger is not None:
                    skip_logger(f"parse_error: {e}", internal)
                continue

            yield _flatten_entry(payload, summary_mode)


def count_by_category(zip_path: Path) -> dict[str, int]:
    """각 doc_type별 entry 수 카운트. 빠른 검증용 (전체 stream)."""
    counts: Counter[str] = Counter()
    for entry in stream_aihub_023(zip_path):
        dtype = entry.get("doc_type", "") or "_unknown"
        counts[dtype] += 1
    return dict(counts)


def count_by_category_and_mode(zip_path: Path) -> dict[tuple[str, str], int]:
    """(doc_type, summary_mode) 쌍별 카운트."""
    counts: Counter[tuple[str, str]] = Counter()
    for entry in stream_aihub_023(zip_path):
        key = (entry.get("doc_type", "") or "_unknown", entry.get("summary_mode", "") or "_none")
        counts[key] += 1
    return dict(counts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--zip-path", required=True, type=Path, help="TL1.zip / VL1.zip 경로")
    parser.add_argument("--count", action="store_true", help="doc_type별 카운트만 출력")
    parser.add_argument("--count-by-mode", action="store_true",
                        help="(doc_type, summary_mode) 쌍별 카운트 출력")
    parser.add_argument("--categories", nargs="*", default=None,
                        help="필터링할 카테고리 (예: fm_drama fs_drama)")
    parser.add_argument("--limit", type=int, default=0,
                        help="앞에서 N개만 stream (0=전체)")
    args = parser.parse_args(argv)

    if args.count:
        counts = count_by_category(args.zip_path)
        for k in sorted(counts, key=counts.get, reverse=True):
            print(f"  {k}: {counts[k]}")
        print(f"  TOTAL: {sum(counts.values())}")
        return 0

    if args.count_by_mode:
        counts = count_by_category_and_mode(args.zip_path)
        for k in sorted(counts, key=lambda x: counts[x], reverse=True):
            print(f"  {k[0]}/{k[1]}: {counts[k]}")
        print(f"  TOTAL: {sum(counts.values())}")
        return 0

    # stream + show first few
    n = 0
    for entry in stream_aihub_023(args.zip_path, categories=args.categories):
        if args.limit and n >= args.limit:
            break
        print(json.dumps(entry, ensure_ascii=False)[:200])
        n += 1
    print(f"\nstreamed {n} entries", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
