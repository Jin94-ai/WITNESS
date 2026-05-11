"""Phase 3.0 v1.1 Pipeline — annotation_outputs → feature_matrix.csv.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §10 + §11.

각 annotation_output JSON에서 features dict를 추출하고, *long-form CSV*로
저장한다. ML / reliability 분석 입력으로 사용.

CSV 형식 (long form):
    record_id, annotator_id, feature, score
    km_titleA_ep001, modelA, conflict_intensity_peak, 4
    km_titleA_ep001, modelA, dangling_thread_generation, 5
    ...

장점:
    - feature set 변경에도 schema 안 깨짐
    - per-feature reliability 계산이 직관적
    - pandas pivot으로 wide form 쉽게 변환 가능

사용:
    python scripts/annotation/build_feature_matrix.py \\
        --input data/annotation/phase3_pilot/validated \\
        --output data/annotation/phase3_pilot/features/feature_matrix.csv
"""
from __future__ import annotations

import argparse
import csv
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


def extract_rows(annotation: dict) -> list[dict]:
    """annotation_output → long-form rows."""
    record_id = annotation.get("record_id", "")
    annotator_id = annotation.get("annotator_id", "")
    genre_id = annotation.get("genre_id", "")
    features = annotation.get("features", {})
    rows: list[dict] = []
    if not isinstance(features, dict):
        return rows
    for fname, score in features.items():
        if not isinstance(score, (int, float)):
            continue
        rows.append({
            "record_id": record_id,
            "genre_id": genre_id,
            "annotator_id": annotator_id,
            "feature": fname,
            "score": float(score),
        })
    return rows


def build_matrix(input_dir: Path) -> list[dict]:
    """annotation_outputs 디렉토리 → long-form rows."""
    rows: list[dict] = []
    for path in sorted(input_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"WARNING: skip {path.name}: {e}", file=sys.stderr)
            continue
        rows.extend(extract_rows(data))
    # 정렬
    rows.sort(key=lambda r: (r["record_id"], r["annotator_id"], r["feature"]))
    return rows


def write_csv(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(
            fp, fieldnames=["record_id", "genre_id", "annotator_id", "feature", "score"],
        )
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path,
                     help="annotation_outputs/ or validated/ dir")
    ap.add_argument("--output", required=True, type=Path,
                     help="feature_matrix.csv output path")
    args = ap.parse_args(argv)

    if not args.input.exists():
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        return 2

    rows = build_matrix(args.input)
    write_csv(rows, args.output)

    # summary stats
    n_records = len({r["record_id"] for r in rows})
    n_annotators = len({r["annotator_id"] for r in rows})
    n_features = len({r["feature"] for r in rows})
    print(f"OK: {len(rows)} rows → {args.output}")
    print(f"  records:    {n_records}")
    print(f"  annotators: {n_annotators}")
    print(f"  features:   {n_features}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
