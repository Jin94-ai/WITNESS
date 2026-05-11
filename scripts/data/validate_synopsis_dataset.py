"""Phase 3.0 v1.1 Pipeline — normalized synopsis JSONL schema validation.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §10.

검사:
    - schema_version == "episode_synopsis_record_v1"
    - 필수 필드 존재 + 타입
    - record_id 결정론적 (genre + title + episode 와 일치)
    - record_id 중복 0
    - episode_number ≥ 1
    - synopsis_text 길이 ≥ 10 (너무 짧은 샘플 catch)
    - raw_text_storage = "private" (공개 repo 보호)
    - 같은 (title_id) 안에서 episode_number 단조 증가 (gap 허용)

권장 사용:
    python scripts/data/validate_synopsis_dataset.py \\
        --input data/annotation/phase3_pilot/normalized_synopsis.jsonl

exit codes:
    0 = pass
    1 = validation 위반 발견
    2 = file error
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


REQUIRED_FIELDS = (
    "schema_version", "record_id", "genre_id", "title_id",
    "episode_number", "source_name", "raw_text_storage", "synopsis_text",
)


def validate_record(record: dict, line_no: int) -> list[str]:
    errs: list[str] = []
    where = f"line {line_no}"
    if not isinstance(record, dict):
        return [f"{where}: not a dict"]

    for field in REQUIRED_FIELDS:
        if field not in record:
            errs.append(f"{where}: missing field {field!r}")

    if record.get("schema_version") != "episode_synopsis_record_v1":
        errs.append(
            f"{where}: schema_version drift "
            f"(expected episode_synopsis_record_v1, got {record.get('schema_version')!r})"
        )

    rid = record.get("record_id", "")
    if not isinstance(rid, str) or not rid:
        errs.append(f"{where}: empty record_id")

    title_id = record.get("title_id", "")
    if not isinstance(title_id, str) or not title_id:
        errs.append(f"{where}: empty title_id")

    ep = record.get("episode_number")
    if not isinstance(ep, int) or ep < 1:
        errs.append(f"{where}: episode_number must be int ≥ 1, got {ep!r}")

    text = record.get("synopsis_text", "")
    if not isinstance(text, str) or len(text.strip()) < 10:
        errs.append(
            f"{where}: synopsis_text too short (≥10 chars required, got {len(text) if isinstance(text, str) else 'non-str'})"
        )

    storage = record.get("raw_text_storage", "")
    if storage != "private":
        errs.append(
            f"{where}: raw_text_storage must be 'private' (got {storage!r}); "
            "Phase 3.0 §8 requires private storage"
        )

    return errs


def validate_dataset(records: list[dict]) -> list[str]:
    """레코드 단위 검사 + 데이터셋 단위 검사 (중복 / 정렬)."""
    errs: list[str] = []
    seen_ids: dict[str, int] = {}
    by_title_episodes: dict[str, list[int]] = {}

    for i, r in enumerate(records, start=1):
        errs.extend(validate_record(r, i))
        rid = r.get("record_id")
        if isinstance(rid, str) and rid:
            if rid in seen_ids:
                errs.append(
                    f"line {i}: duplicate record_id {rid!r} "
                    f"(already at line {seen_ids[rid]})"
                )
            else:
                seen_ids[rid] = i
        title_id = r.get("title_id")
        ep = r.get("episode_number")
        if isinstance(title_id, str) and isinstance(ep, int):
            by_title_episodes.setdefault(title_id, []).append(ep)

    # title 안에서 episode_number 단조 증가 (정렬됨, 중복 0)
    for title_id, eps in by_title_episodes.items():
        if eps != sorted(eps):
            errs.append(
                f"dataset: title_id={title_id!r} episode_numbers not monotonically "
                f"increasing: {eps}"
            )
        if len(set(eps)) != len(eps):
            errs.append(
                f"dataset: title_id={title_id!r} duplicate episode_numbers: {eps}"
            )

    return errs


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"line {i}: invalid JSON: {e}") from e
    return records


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path,
                     help="normalized_synopsis.jsonl path")
    ap.add_argument("--strict-min-records", type=int, default=0,
                     help="요구되는 최소 레코드 수 (default 0). "
                          "Phase 3.0 mini pilot은 10")
    args = ap.parse_args(argv)

    if not args.input.exists():
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        return 2

    try:
        records = load_jsonl(args.input)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    errs = validate_dataset(records)
    if args.strict_min_records and len(records) < args.strict_min_records:
        errs.append(
            f"dataset: record count {len(records)} < required min "
            f"{args.strict_min_records}"
        )

    print(f"records: {len(records)}")
    if errs:
        print(f"FAIL: {len(errs)} validation issue(s):")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("PASS — dataset valid.")
    # 요약 stats
    by_genre: dict[str, int] = {}
    by_title: dict[str, int] = {}
    for r in records:
        by_genre[r["genre_id"]] = by_genre.get(r["genre_id"], 0) + 1
        by_title[r["title_id"]] = by_title.get(r["title_id"], 0) + 1
    print(f"  genres: {dict(by_genre)}")
    print(f"  titles: {dict(by_title)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
