"""Phase 3.1 §22.2 — feature_matrix + profiles → episode_intensity_v1 JSON.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §22.2.

목표:
    Annotation feature vector (per episode) → genre_intensity_score per genre.
    예: korean_melodrama_intensity = 0.78.

용법:
    python scripts/annotation/run_episode_intensity.py \\
        --feature-matrix data/annotation/phase3_pilot/features/feature_matrix.csv \\
        --profiles data/annotation/phase3_pilot/genre_profiles.json \\
        --output data/annotation/phase3_pilot/episode_intensity.json \\
        [--reliability data/annotation/phase3_pilot/reliability.json]

옵션:
    --reliability: KEEP feature만 사용. 미지정 시 profile.feature_weights union.
    --strict-min-records N: 결과 record 수 < N이면 exit 1.

원칙:
    - 학습 0 / fine-tuning 0 / raw text 0
    - feature_weights는 GenreProfile 그대로
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

from engine.observer.episode_intensity import run_episode_intensity  # noqa: E402
from engine.observer.genre_profile import load_profiles  # noqa: E402


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


def load_feature_matrix(path: Path) -> list[dict]:
    """feature_matrix.csv → list of {record_id, annotator_id, feature, score}."""
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8", newline="") as fp:
        reader = csv.DictReader(fp)
        for r in reader:
            rows.append({
                "record_id": r.get("record_id", ""),
                "genre_id": r.get("genre_id", ""),
                "annotator_id": r.get("annotator_id", ""),
                "feature": r.get("feature", ""),
                "score": r.get("score", ""),
            })
    return rows


def load_kept_features(reliability_path: Path) -> list[str] | None:
    """reliability.json → KEEP feature 리스트. 없으면 None."""
    if not reliability_path.exists():
        return None
    raw = json.loads(reliability_path.read_text(encoding="utf-8"))
    summary = raw.get("summary", {})
    keep = summary.get("keep")
    if isinstance(keep, list) and keep:
        return list(keep)
    return None


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--feature-matrix", required=True, type=Path,
                     help="feature_matrix.csv (long-form)")
    ap.add_argument("--profiles", required=True, type=Path,
                     help="genre_profiles.json")
    ap.add_argument("--output", required=True, type=Path,
                     help="episode_intensity.json output path")
    ap.add_argument("--reliability", type=Path, default=None,
                     help="reliability.json — KEEP feature 필터 (옵션)")
    ap.add_argument("--strict-min-records", type=int, default=0,
                     help="결과 record 수 < N이면 exit 1")
    args = ap.parse_args(argv)

    if not args.feature_matrix.exists():
        print(f"ERROR: feature matrix not found: {args.feature_matrix}", file=sys.stderr)
        return 2
    if not args.profiles.exists():
        print(f"ERROR: profiles not found: {args.profiles}", file=sys.stderr)
        return 2

    rows = load_feature_matrix(args.feature_matrix)
    if not rows:
        print("ERROR: feature matrix is empty", file=sys.stderr)
        return 1

    profiles = load_profiles(args.profiles)
    if not profiles:
        print("ERROR: no profiles loaded", file=sys.stderr)
        return 1

    kept = None
    if args.reliability is not None:
        kept = load_kept_features(args.reliability)
        if kept is None:
            print(
                "WARNING: reliability provided but no KEEP features found; "
                "falling back to profile.feature_weights union",
                file=sys.stderr,
            )

    output = run_episode_intensity(rows, profiles, kept_features=kept)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    n = output.n_records
    print(f"OK: {n} records × {output.n_genres} genres → {args.output}")
    print(f"  kept_features_used: {len(output.kept_features_used)}")
    if output.intensity_records:
        scores = [r.intensity_score for r in output.intensity_records]
        print(f"  score range: {min(scores):.3f} - {max(scores):.3f}")

    if args.strict_min_records and n < args.strict_min_records:
        print(
            f"ERROR: n_records {n} < strict-min-records {args.strict_min_records}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
