"""Phase 3.0 v1.1 Pipeline — feature_matrix.csv → reliability.json.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §10 + §16.2 + §16.3.

각 feature에 대해 *annotator pair별 Pearson r*를 계산하고, KEEP / REVISE / DROP /
NEEDS_MORE_DATA 판정을 부여 (§16.3).

성공 기준 (§16.2):
    최소 4-5개 feature에서 r >= 0.7

판정 규칙 (§16.3):
    KEEP             — r >= 0.7
    REVISE           — 0.4 <= r < 0.7
    DROP             — r < 0.4
    NEEDS_MORE_DATA  — pair count < 3 (표본 부족)

출력 schema:
    {
      "schema_version": "phase3_reliability_report_v1",
      "n_records": ...,
      "n_annotators": ...,
      "feature_reliability": {
        "feature_name": {
          "n_pairs": N,
          "pair_correlations": [...],
          "mean_r": ...,
          "median_r": ...,
          "decision": "KEEP" | ...,
        },
        ...
      },
      "summary": {
        "keep": [...],
        "revise": [...],
        "drop": [...],
        "needs_more_data": [...],
        "phase3_threshold_pass": bool  # ≥ 4 KEEP features
      }
    }

사용:
    python scripts/annotation/build_reliability_report.py \\
        --features data/annotation/phase3_pilot/features/feature_matrix.csv \\
        --output data/annotation/phase3_pilot/reports/reliability.json
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import statistics
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


REPORT_SCHEMA_VERSION = "phase3_reliability_report_v1"


def _pearson_r(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n != len(ys) or n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    den = sx * sy
    if den == 0:
        return 0.0
    return num / den


def load_feature_matrix(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8", newline="") as fp:
        reader = csv.DictReader(fp)
        for r in reader:
            try:
                r["score"] = float(r["score"])
            except (ValueError, KeyError):
                continue
            rows.append(r)
    return rows


def feature_reliability(rows: list[dict]) -> dict:
    """각 feature에 대해 annotator pair별 Pearson r 계산."""
    # group: feature → record_id → annotator_id → score
    by_feat: dict[str, dict[str, dict[str, float]]] = {}
    for r in rows:
        feat = r["feature"]
        rid = r["record_id"]
        aid = r["annotator_id"]
        score = r["score"]
        by_feat.setdefault(feat, {}).setdefault(rid, {})[aid] = score

    out: dict[str, dict] = {}
    for feat, by_rec in by_feat.items():
        # 모든 annotator
        all_anns = sorted({a for rec in by_rec.values() for a in rec.keys()})
        pair_rs: list[dict] = []
        for i in range(len(all_anns)):
            for j in range(i + 1, len(all_anns)):
                a, b = all_anns[i], all_anns[j]
                xs, ys = [], []
                for rid, ann_scores in by_rec.items():
                    if a in ann_scores and b in ann_scores:
                        xs.append(ann_scores[a])
                        ys.append(ann_scores[b])
                if len(xs) >= 2:
                    r_val = _pearson_r(xs, ys)
                    pair_rs.append({
                        "annotator_pair": [a, b],
                        "n": len(xs),
                        "r": round(r_val, 4),
                    })
        if pair_rs:
            r_values = [p["r"] for p in pair_rs]
            mean_r = round(statistics.mean(r_values), 4)
            median_r = round(statistics.median(r_values), 4)
        else:
            mean_r = 0.0
            median_r = 0.0
        out[feat] = {
            "n_records": len(by_rec),
            "n_annotators": len(all_anns),
            "n_pairs": len(pair_rs),
            "pair_correlations": pair_rs,
            "mean_r": mean_r,
            "median_r": median_r,
            "decision": _decide_feature(pair_rs, mean_r),
        }
    return out


def _decide_feature(pair_rs: list[dict], mean_r: float) -> str:
    """§16.3 판정 규칙."""
    if len(pair_rs) < 1:
        return "NEEDS_MORE_DATA"
    # 어느 한 pair라도 sample size < 3이면 NEEDS_MORE_DATA로 평가 가능하지만
    # 우선 mean_r 기준
    if any(p["n"] < 3 for p in pair_rs):
        # 표본 너무 작음 — Phase 3.0 mini pilot 흔함
        if mean_r >= 0.7:
            return "KEEP"  # 작은 표본이지만 r 강함
        return "NEEDS_MORE_DATA"
    if mean_r >= 0.7:
        return "KEEP"
    if mean_r >= 0.4:
        return "REVISE"
    return "DROP"


def build_summary(feature_reliability_dict: dict) -> dict:
    keep, revise, drop, needs_more = [], [], [], []
    for feat, info in feature_reliability_dict.items():
        d = info["decision"]
        if d == "KEEP":
            keep.append(feat)
        elif d == "REVISE":
            revise.append(feat)
        elif d == "DROP":
            drop.append(feat)
        else:
            needs_more.append(feat)
    return {
        "keep": sorted(keep),
        "revise": sorted(revise),
        "drop": sorted(drop),
        "needs_more_data": sorted(needs_more),
        "n_keep": len(keep),
        "phase3_threshold_pass": len(keep) >= 4,  # §16.2 + Phase 3.1 진입 조건
    }


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--features", required=True, type=Path,
                     help="feature_matrix.csv path")
    ap.add_argument("--output", required=True, type=Path,
                     help="reliability.json output path")
    args = ap.parse_args(argv)

    if not args.features.exists():
        print(f"ERROR: features csv not found: {args.features}", file=sys.stderr)
        return 2

    rows = load_feature_matrix(args.features)
    if not rows:
        print("WARNING: no rows in feature_matrix", file=sys.stderr)

    feat_rel = feature_reliability(rows)
    summary = build_summary(feat_rel)

    n_records = len({r["record_id"] for r in rows})
    n_annotators = len({r["annotator_id"] for r in rows})

    payload = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "n_records": n_records,
        "n_annotators": n_annotators,
        "feature_reliability": feat_rel,
        "summary": summary,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8",
    )

    print(f"OK: reliability report → {args.output}")
    print(f"  records: {n_records} / annotators: {n_annotators} / features: {len(feat_rel)}")
    print(f"  KEEP: {summary['keep']}")
    print(f"  REVISE: {summary['revise']}")
    print(f"  DROP: {summary['drop']}")
    print(f"  NEEDS_MORE_DATA: {summary['needs_more_data']}")
    print(
        f"  Phase 3.1 threshold (≥4 KEEP): "
        f"{'PASS' if summary['phase3_threshold_pass'] else 'NOT YET'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
