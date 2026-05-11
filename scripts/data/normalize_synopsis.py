"""Phase 3.0 v1.1 Pipeline — raw synopsis → normalized JSONL (Mode A 호환).

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §10.

Mode A (Manual Input Mode):
    사용자가 외부 fetch 없이 raw synopsis를 직접 입력해 둔 디렉토리를
    읽어 정규화된 JSONL로 변환.

입력: data/external_private/synopsis_raw/ 안의 *.json 또는 *.txt
      *.json: EpisodeSynopsisRecord schema (§9.1) 그대로
      *.txt: title_id_episode-NN.txt 형식, content가 synopsis_text

출력: data/annotation/phase3_pilot/normalized_synopsis.jsonl

원칙:
    - network IO 0
    - 외부 의존 0
    - record_id는 결정론적 (genre + title + episode)
    - private path는 출력에 포함하지 않음 (raw_text_storage="private")
    - schema validation은 별도 (validate_synopsis_dataset.py)
"""
from __future__ import annotations

import argparse
import io
import json
import re
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


# Filename patterns for *.txt mode
# Examples:
#   km_titleA_ep01.txt   → genre prefix infer + title_id "titleA" + ep 1
#   korean_morning_melodrama_titleA_ep01.txt → full genre id
_TXT_FILENAME_RE = re.compile(
    r"^(?P<title_id>[A-Za-z0-9_]+?)[_-]ep(?P<episode>\d+)\.txt$"
)


# ---------------------------------------------------------------------------
# Record builder (§9.1 EpisodeSynopsisRecord)
# ---------------------------------------------------------------------------

EPISODE_SYNOPSIS_RECORD_VERSION = "episode_synopsis_record_v1"


def make_record(
    *,
    genre_id: str,
    title_id: str,
    episode_number: int,
    synopsis_text: str,
    source_name: str = "manual_input",
    source_url: str = "",
    source_license_note: str = "",
    fetched_at: str = "",
    public_safe_summary: str = "",
    notes: str = "",
) -> dict:
    """EpisodeSynopsisRecord (§9.1)."""
    record_id = _make_record_id(genre_id, title_id, episode_number)
    return {
        "schema_version": EPISODE_SYNOPSIS_RECORD_VERSION,
        "record_id": record_id,
        "genre_id": genre_id,
        "title_id": title_id,
        "episode_number": int(episode_number),
        "source_name": source_name,
        "source_url": source_url,
        "source_license_note": source_license_note,
        "fetched_at": fetched_at,
        "raw_text_storage": "private",
        "synopsis_text": synopsis_text,
        "public_safe_summary": public_safe_summary,
        "notes": notes,
    }


def _make_record_id(genre_id: str, title_id: str, episode_number: int) -> str:
    """결정론적 record_id (genre + title + episode)."""
    # 짧은 genre prefix
    prefix_map = {
        "korean_morning_melodrama": "km",
        "japanese_quiet_drama": "jp",
    }
    prefix = prefix_map.get(genre_id, genre_id[:5])
    return f"{prefix}_{title_id}_ep{episode_number:03d}"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_json_record(path: Path, default_genre_id: str) -> dict:
    """*.json 파일을 EpisodeSynopsisRecord로 로드.

    파일이 schema_version을 갖고 있으면 그대로 사용 (필드 보강).
    그렇지 않으면 dict 안의 필드를 make_record로 normalize.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and raw.get("schema_version") == EPISODE_SYNOPSIS_RECORD_VERSION:
        # 이미 정규화된 record
        return raw
    # raw fields → make_record
    genre_id = raw.get("genre_id", default_genre_id)
    title_id = raw.get("title_id") or path.stem
    episode_number = int(raw.get("episode_number", 0))
    return make_record(
        genre_id=genre_id,
        title_id=title_id,
        episode_number=episode_number,
        synopsis_text=raw.get("synopsis_text", ""),
        source_name=raw.get("source_name", "manual_input"),
        source_url=raw.get("source_url", ""),
        source_license_note=raw.get("source_license_note", ""),
        fetched_at=raw.get("fetched_at", ""),
        public_safe_summary=raw.get("public_safe_summary", ""),
        notes=raw.get("notes", ""),
    )


def load_txt_record(path: Path, default_genre_id: str) -> dict | None:
    """*.txt 파일을 EpisodeSynopsisRecord로 로드. 파일명에서 메타 추론."""
    m = _TXT_FILENAME_RE.match(path.name)
    if not m:
        return None
    title_id = m.group("title_id")
    episode_number = int(m.group("episode"))
    synopsis_text = path.read_text(encoding="utf-8").strip()
    return make_record(
        genre_id=default_genre_id,
        title_id=title_id,
        episode_number=episode_number,
        synopsis_text=synopsis_text,
        source_name="manual_input_txt",
    )


def normalize_dir(input_dir: Path, default_genre_id: str) -> list[dict]:
    """입력 디렉토리 안의 모든 .json + .txt를 record list로 변환.

    record는 (record_id, episode_number) 기준 정렬.
    중복 record_id는 마지막 것만 유지.
    """
    if not input_dir.exists():
        return []
    records: dict[str, dict] = {}
    for p in sorted(input_dir.rglob("*")):
        if not p.is_file():
            continue
        record: dict | None = None
        if p.suffix.lower() == ".json":
            try:
                record = load_json_record(p, default_genre_id)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"WARNING: skip {p.name}: {e}", file=sys.stderr)
                continue
        elif p.suffix.lower() == ".txt":
            record = load_txt_record(p, default_genre_id)
            if record is None:
                print(
                    f"WARNING: skip {p.name}: filename pattern mismatch "
                    "(expected {title}_ep{NN}.txt)",
                    file=sys.stderr,
                )
                continue
        if record is None:
            continue
        records[record["record_id"]] = record
    return sorted(
        records.values(),
        key=lambda r: (r["genre_id"], r["title_id"], r["episode_number"]),
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--input", required=True, type=Path,
        help="raw private synopsis directory (Mode A — *.json or *.txt)",
    )
    ap.add_argument(
        "--output", required=True, type=Path,
        help="normalized JSONL output (e.g. data/annotation/phase3_pilot/normalized_synopsis.jsonl)",
    )
    ap.add_argument(
        "--default-genre", default="korean_morning_melodrama",
        help="genre_id to infer when input has none (default: korean_morning_melodrama)",
    )
    args = ap.parse_args(argv)

    if not args.input.exists():
        print(f"ERROR: input dir not found: {args.input}", file=sys.stderr)
        return 2

    records = normalize_dir(args.input, args.default_genre)
    if not records:
        print(f"WARNING: no records found in {args.input}", file=sys.stderr)
        # Still write empty file (so downstream sees zero records)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as fp:
        for r in records:
            fp.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"OK: normalized {len(records)} records → {args.output}")
    if records:
        first = records[0]
        print(f"  first: {first['record_id']} ({first['title_id']} ep{first['episode_number']})")
        print(f"  last:  {records[-1]['record_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
