"""Sample annotation results for human review (Phase 2).

Per `docs/witness_narrative_mode_plan.md` §6 Phase 2 산출물 +
`docs/annotation/ANNOTATION_GUIDE.md` §3.4:
    "전체의 최소 5%를 사람이 직접 어노테이션 → LLM 결과와 비교"

이 스크립트는 *deterministic seeded sampling*으로 review 후보를 선정한다.
네트워크 호출 0. 사람 검증 비율은 기본 5%, 최소 1건 보장.

선택 우선순위 (둘 중 하나):
    1. low-confidence: synthesized confidence가 낮은 항목 (다른 의견)
    2. random-stratified: title 단위로 분층 표본 (편향 방지)

Usage:
    python scripts/annotation/sample_for_human_review.py \\
        --annotated-dir data/annotated \\
        --output data/annotated/_human_review_samples.json \\
        --pct 5 --strategy low_confidence

    python scripts/annotation/sample_for_human_review.py \\
        --annotated-dir data/annotated \\
        --output data/annotated/_human_review_samples.json \\
        --pct 5 --strategy random --seed 42
"""
from __future__ import annotations

import argparse
import io
import json
import math
import random
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


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_synthesized_annotations(annotated_dir: Path) -> list[dict]:
    """Load all synthesized_annotation_v1 records under annotated_dir.

    Layout: data/annotated/{title_id}/{episode_no:02d}.json
    """
    out: list[dict] = []
    if not annotated_dir.exists():
        return out
    for title_dir in sorted(annotated_dir.iterdir()):
        if not title_dir.is_dir():
            continue
        if title_dir.name.startswith("_"):
            # _per_annotator/, _human_review_samples.json 등 제외
            continue
        for ep_file in sorted(title_dir.glob("*.json")):
            try:
                d = json.loads(ep_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if d.get("schema_version") != "synthesized_annotation_v1":
                continue
            try:
                d["_path"] = str(ep_file.relative_to(ROOT))
            except ValueError:
                # annotated_dir가 ROOT 밖 (예: 테스트 tmp_path) — 절대 경로 보존
                d["_path"] = str(ep_file)
            out.append(d)
    return out


# ---------------------------------------------------------------------------
# Sampling strategies
# ---------------------------------------------------------------------------

def _sample_count(total: int, pct: float) -> int:
    """At least 1 if there are records; ceiling to nearest int otherwise."""
    if total <= 0:
        return 0
    return max(1, math.ceil(total * pct / 100.0))


def sample_low_confidence(records: list[dict], n: int) -> list[dict]:
    """Pick the n records with lowest synthesized confidence (most ambiguous)."""
    sorted_recs = sorted(records, key=lambda r: float(r.get("confidence", 0.0)))
    return sorted_recs[:n]


def sample_random_stratified(
    records: list[dict], n: int, seed: int,
) -> list[dict]:
    """Stratified random sample by title_id (each title gets ≥0 picks)."""
    rng = random.Random(seed)
    by_title: dict[str, list[dict]] = {}
    for r in records:
        by_title.setdefault(r.get("title_id", "_unknown"), []).append(r)
    titles = sorted(by_title.keys())
    if not titles or n <= 0:
        return []
    # 배분: 각 title에 1건 우선, 나머지를 random
    picks: list[dict] = []
    used: set[tuple[str, int]] = set()
    for t in titles:
        if len(picks) >= n:
            break
        bucket = by_title[t]
        idx = rng.randrange(len(bucket))
        picks.append(bucket[idx])
        used.add((t, idx))
    # 남은 슬롯
    flat = [
        (t, i, r)
        for t, recs in by_title.items()
        for i, r in enumerate(recs)
        if (t, i) not in used
    ]
    rng.shuffle(flat)
    for t, i, r in flat:
        if len(picks) >= n:
            break
        picks.append(r)
    return picks


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--annotated-dir", type=Path,
        default=ROOT / "data" / "annotated",
    )
    ap.add_argument(
        "--output", type=Path, required=True,
        help="Sample list JSON 저장 위치",
    )
    ap.add_argument(
        "--pct", type=float, default=5.0,
        help="샘플 비율 (default 5%%)",
    )
    ap.add_argument(
        "--strategy",
        choices=["low_confidence", "random"],
        default="low_confidence",
    )
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    records = load_synthesized_annotations(args.annotated_dir)
    if not records:
        print(
            f"WARNING: no synthesized annotations found in {args.annotated_dir}",
            file=sys.stderr,
        )
        # 빈 결과로도 schema 보존
        sample: list[dict] = []
    else:
        n = _sample_count(len(records), args.pct)
        if args.strategy == "low_confidence":
            sample = sample_low_confidence(records, n)
        else:
            sample = sample_random_stratified(records, n, seed=args.seed)

    out_dict = {
        "schema_version": "human_review_sample_v1",
        "strategy": args.strategy,
        "pct_target": args.pct,
        "total_records": len(records),
        "sampled_count": len(sample),
        "seed": args.seed if args.strategy == "random" else None,
        "items": [
            {
                "title_id": r.get("title_id"),
                "episode_no": r.get("episode_no"),
                "confidence": r.get("confidence"),
                "path": r.get("_path"),
                "contributing_annotators": r.get("contributing_annotators", []),
            }
            for r in sample
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(out_dict, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK: sampled {len(sample)} / {len(records)} records ({args.pct}% target)")
    try:
        print(f"  written: {args.output.relative_to(ROOT)}")
    except ValueError:
        print(f"  written: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(cli())
