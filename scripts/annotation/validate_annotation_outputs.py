"""Phase 3.0 v1.1 Pipeline — annotation_outputs/*.json schema + quote validation.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §13 + §16.

검사:
    1. schema (annotation_id / record_id / annotator_id / features dict / evidence_quotes / confidence / warnings)
    2. feature score: 0-5 정수 (또는 0.0-1.0 float; level/5 환산)
    3. evidence_quotes의 quote가 원본 synopsis_text에 *substring* 매칭
       (LLM hallucination 검사, §16.1)
    4. record_id가 normalized_synopsis.jsonl과 일치

출력:
    1. validation report (per-file errors)
    2. hallucination_report.json (feature별 hallucination rate)
    3. validated/ 디렉토리에 통과한 outputs 복사 (downstream용)

사용:
    python scripts/annotation/validate_annotation_outputs.py \\
        --input data/annotation/phase3_pilot/annotation_outputs \\
        --synopsis data/annotation/phase3_pilot/normalized_synopsis.jsonl \\
        --validated-dir data/annotation/phase3_pilot/validated \\
        --hallucination-report data/annotation/phase3_pilot/reports/hallucination_report.json

성공 기준 (§16.1): hallucination rate < 5%
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


# Phase 3.0 §13 episode_annotation_v1 schema
REQUIRED_FIELDS = (
    "annotation_id", "record_id", "annotator_id", "features",
    "evidence_quotes", "confidence",
)


# ---------------------------------------------------------------------------
# Synopsis index (record_id → synopsis_text)
# ---------------------------------------------------------------------------

def load_synopsis_index(jsonl_path: Path) -> dict[str, str]:
    index: dict[str, str] = {}
    if not jsonl_path.exists():
        return index
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        index[d["record_id"]] = d.get("synopsis_text", "")
    return index


# ---------------------------------------------------------------------------
# Quote validation (§16.1 — hallucination check)
# ---------------------------------------------------------------------------

_WS_RE = re.compile(r"\s+")


def _normalize_for_match(text: str) -> str:
    return _WS_RE.sub(" ", text or "").strip()


def quote_in_synopsis(quote: str, synopsis: str) -> bool:
    """공백 정규화 후 substring 매칭."""
    if not quote or not synopsis:
        return False
    return _normalize_for_match(quote) in _normalize_for_match(synopsis)


# ---------------------------------------------------------------------------
# Annotation validation
# ---------------------------------------------------------------------------

def validate_annotation(
    annotation: dict,
    synopsis_index: dict[str, str],
) -> tuple[list[str], dict]:
    """단일 annotation_output JSON 검증.

    Returns:
        (errors, hallucination_stats)
        hallucination_stats: {
            "total_quotes": N, "verified": M, "missed": [...],
            "features_with_quotes": [...],   # feature names that had ≥1 quote
            "per_feature_quote_count": {feature: count},
        }
    """
    errs: list[str] = []
    halluc = {
        "total_quotes": 0,
        "verified": 0,
        "missed": [],
        "features_with_quotes": [],
        "per_feature_quote_count": {},
    }

    if not isinstance(annotation, dict):
        errs.append("annotation is not a dict")
        return errs, halluc

    for f in REQUIRED_FIELDS:
        if f not in annotation:
            errs.append(f"missing field: {f}")

    rid = annotation.get("record_id", "")
    if rid and synopsis_index and rid not in synopsis_index:
        errs.append(
            f"record_id {rid!r} not in synopsis index "
            "(check normalized_synopsis.jsonl)"
        )
    synopsis = synopsis_index.get(rid, "")

    # Feature scores
    features = annotation.get("features", {})
    if not isinstance(features, dict):
        errs.append("features must be a dict")
    else:
        for fname, val in features.items():
            if not isinstance(val, (int, float)):
                errs.append(f"feature {fname}: must be numeric, got {type(val).__name__}")
                continue
            fv = float(val)
            # Phase 3.0 §13 example shows int 0-5; accept 0.0-1.0 float too
            if 0 <= fv <= 5:
                pass  # 0-5 level OK
            elif 0.0 <= fv <= 1.0:
                pass  # normalized 0-1 OK
            else:
                errs.append(
                    f"feature {fname}: score {fv} out of accepted range "
                    "(0-5 level or 0.0-1.0 normalized)"
                )

    # Evidence quotes
    quotes = annotation.get("evidence_quotes", {})
    feat_with_quotes: list[str] = []
    per_feature_count: dict[str, int] = {}
    if not isinstance(quotes, dict):
        errs.append("evidence_quotes must be dict[feature_name, list[str]]")
    else:
        for fname, qlist in quotes.items():
            if not isinstance(qlist, list):
                errs.append(f"evidence_quotes[{fname}] must be a list")
                continue
            count = 0
            for q in qlist:
                if not isinstance(q, str):
                    errs.append(f"evidence_quotes[{fname}]: non-str entry")
                    continue
                count += 1
                halluc["total_quotes"] += 1
                if synopsis:
                    if quote_in_synopsis(q, synopsis):
                        halluc["verified"] += 1
                    else:
                        halluc["missed"].append({
                            "feature": fname,
                            "quote": q[:80],
                        })
            if count > 0:
                feat_with_quotes.append(fname)
                per_feature_count[fname] = count
    halluc["features_with_quotes"] = feat_with_quotes
    halluc["per_feature_quote_count"] = per_feature_count
    # Phase 3.05 Step 4 — valid flag for valid_files_only_summary 분리
    halluc["valid"] = not errs

    # Confidence
    conf = annotation.get("confidence")
    if isinstance(conf, dict):
        overall = conf.get("overall")
        if overall is not None and not isinstance(overall, (int, float)):
            errs.append("confidence.overall must be numeric")
    elif conf is not None and not isinstance(conf, (int, float)):
        errs.append("confidence must be dict (with 'overall') or numeric")

    return errs, halluc


# ---------------------------------------------------------------------------
# Aggregate report
# ---------------------------------------------------------------------------

def _summarize_stats(
    stats: list[dict], *, expected_features: tuple[str, ...] = (),
) -> dict:
    """단일 file group (valid 또는 all)의 hallucination + coverage 통계."""
    total_quotes = sum(s["total_quotes"] for s in stats)
    verified = sum(s["verified"] for s in stats)
    rate = (
        (total_quotes - verified) / total_quotes
        if total_quotes > 0 else 0.0
    )
    feature_rates: dict[str, dict] = {}
    for s in stats:
        for missed in s.get("missed", []):
            f = missed["feature"]
            feature_rates.setdefault(f, {"missed": 0})
            feature_rates[f]["missed"] += 1

    per_feature_total_quote_count: dict[str, int] = {}
    per_feature_annotation_coverage: dict[str, int] = {}
    for s in stats:
        for f, c in s.get("per_feature_quote_count", {}).items():
            per_feature_total_quote_count[f] = (
                per_feature_total_quote_count.get(f, 0) + c
            )
        for f in s.get("features_with_quotes", []):
            per_feature_annotation_coverage[f] = (
                per_feature_annotation_coverage.get(f, 0) + 1
            )

    n_files = len(stats)
    summary = {
        "n_files": n_files,
        "total_quotes": total_quotes,
        "verified": verified,
        "hallucinated": total_quotes - verified,
        "hallucination_rate": round(rate, 4),
        "per_feature_missed": feature_rates,
        "phase3_threshold_pass": rate < 0.05,  # §16.1
        "phase3_threshold_no_go": rate >= 0.10,
        "per_feature_quote_count": per_feature_total_quote_count,
        "per_feature_annotation_coverage": per_feature_annotation_coverage,
    }

    if expected_features:
        coverage_ratio = {}
        for f in expected_features:
            cov = per_feature_annotation_coverage.get(f, 0)
            coverage_ratio[f] = (
                round(cov / n_files, 4) if n_files > 0 else 0.0
            )
        summary["expected_features"] = list(expected_features)
        summary["expected_features_coverage_ratio"] = coverage_ratio
        summary["expected_features_with_zero_coverage"] = sorted(
            f for f in expected_features if per_feature_annotation_coverage.get(f, 0) == 0
        )
        if coverage_ratio:
            min_feat = min(coverage_ratio.items(), key=lambda x: x[1])
            summary["min_coverage_feature"] = min_feat[0]
            summary["min_coverage_ratio"] = min_feat[1]

    return summary


def aggregate_hallucination_rate(
    per_file_stats: list[dict],
    *,
    expected_features: tuple[str, ...] = (),
    invalid_files: list[dict] | None = None,
) -> dict:
    """Phase 3.05 Step 4 — valid_files_only / all_files / invalid_files 3 layer 분리.

    threshold (phase3_threshold_pass / phase3_threshold_no_go)는 *valid_files_only*
    기준으로 산출 — schema invalid 파일이 통계를 오염시키지 않도록 한다.

    Top-level 키는 valid_files_only_summary를 그대로 노출 (backwards compat).

    Args:
        per_file_stats: 각 항목에 'valid' bool 필드 가져야 함 (없으면 valid 처리).
        invalid_files: 추가 invalid file 목록 (json parse fail 등 — per_file_stats에 없는 경우).
    """
    valid_stats = [s for s in per_file_stats if s.get("valid", True)]
    invalid_stats = [s for s in per_file_stats if not s.get("valid", True)]

    valid_summary = _summarize_stats(valid_stats, expected_features=expected_features)
    all_summary = _summarize_stats(per_file_stats, expected_features=expected_features)

    # invalid_files: per_file_stats에 못 들어간 (json parse fail 등) + per_file_stats invalid
    invalid_list = list(invalid_files or [])
    # backwards compat: top-level은 valid_files_only summary와 동일
    summary = dict(valid_summary)
    summary["n_annotations"] = valid_summary["n_files"]  # cycle 12 backwards compat
    summary["all_files_summary"] = all_summary
    summary["valid_files_only_summary"] = valid_summary
    summary["invalid_files"] = invalid_list
    summary["n_invalid_files"] = len(invalid_list) + len(invalid_stats)

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path,
                     help="annotation_outputs/ dir")
    ap.add_argument("--synopsis", type=Path,
                     help="normalized_synopsis.jsonl (for quote validation)")
    ap.add_argument("--validated-dir", type=Path, default=None,
                     help="copy validated outputs here (optional)")
    ap.add_argument("--hallucination-report", type=Path, default=None,
                     help="hallucination_report.json output path")
    ap.add_argument("--strict", action="store_true",
                     help="exit 1 if any annotation has errors")
    ap.add_argument(
        "--expected-features", nargs="+", default=None,
        help="feature 이름 목록 — 각 feature가 quote를 받았는지 coverage 추적 "
             "(default: Phase 3.0 §11 7 features)",
    )
    ap.add_argument(
        "--quote-coverage-min", type=float, default=None,
        help="expected feature 중 *annotation_coverage_ratio* (quote를 받은 annotation 비율) "
             "가 이 값보다 낮은 게 있으면 경고. --strict와 함께 쓰면 exit 1.",
    )
    args = ap.parse_args(argv)

    # default expected features (Phase 3.0 §11 7)
    if args.expected_features is None:
        expected_features = (
            "conflict_intensity_peak",
            "dangling_thread_generation",
            "cliffhanger_strength",
            "relationship_pressure",
            "hidden_information_pressure",
            "silence_or_avoidance",
            "emotional_suppression",
        )
    else:
        expected_features = tuple(args.expected_features)

    if not args.input.exists():
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        return 2

    # Phase 3.05 Step 3 — strict mode에서 quote validation 강제
    if args.strict and args.synopsis is None:
        print(
            "ERROR: --strict requires --synopsis "
            "(quote hallucination check needs original synopsis text)",
            file=sys.stderr,
        )
        return 2

    synopsis_index = (
        load_synopsis_index(args.synopsis) if args.synopsis else {}
    )

    per_file_stats: list[dict] = []
    invalid_files: list[tuple[Path, list[str]]] = []
    valid_files: list[Path] = []
    # Phase 3.05 Step 4 — JSON parse fail은 per_file_stats에 들어가지 못함;
    # 별도 reporting을 위해 dict 목록 유지
    parse_failed: list[dict] = []

    for path in sorted(args.input.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            err = f"invalid JSON: {e}"
            invalid_files.append((path, [err]))
            parse_failed.append({"path": path.name, "errors": [err]})
            continue
        errs, halluc = validate_annotation(data, synopsis_index)
        per_file_stats.append(halluc)
        if errs:
            invalid_files.append((path, errs))
        else:
            valid_files.append(path)
            if args.validated_dir:
                args.validated_dir.mkdir(parents=True, exist_ok=True)
                (args.validated_dir / path.name).write_text(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

    # Phase 3.05 Step 4 — invalid_files (schema fail + parse fail) 모두 report에 포함
    schema_invalid = []
    for p, errs in invalid_files:
        # parse_failed 이미 있는 path는 중복 추가 안 함
        if any(p.name == pf["path"] for pf in parse_failed):
            continue
        schema_invalid.append({"path": p.name, "errors": list(errs)})

    summary = aggregate_hallucination_rate(
        per_file_stats,
        expected_features=expected_features,
        invalid_files=parse_failed + schema_invalid,
    )

    print(f"validated: {len(valid_files)} / total: {len(valid_files) + len(invalid_files)}")
    print(
        f"  hallucination: {summary['hallucinated']}/{summary['total_quotes']} "
        f"= {summary['hallucination_rate']:.4f} "
        f"({'PASS' if summary['phase3_threshold_pass'] else 'WARN' if not summary['phase3_threshold_no_go'] else 'NO-GO'} vs §16.1 < 0.05)"
    )

    # Expected feature coverage
    coverage_warning = False
    if expected_features:
        zero = summary.get("expected_features_with_zero_coverage", [])
        if zero:
            print(f"  WARN: {len(zero)} expected features have 0 quotes: {', '.join(zero)}")
            coverage_warning = True
        if args.quote_coverage_min is not None:
            min_ratio = summary.get("min_coverage_ratio", 0.0)
            min_feat = summary.get("min_coverage_feature", "")
            if min_ratio < args.quote_coverage_min:
                print(
                    f"  WARN: min coverage ratio {min_ratio:.3f} < threshold "
                    f"{args.quote_coverage_min:.3f} (feature: {min_feat})"
                )
                coverage_warning = True

    if invalid_files:
        print(f"\nFAIL — {len(invalid_files)} files with issues:")
        for p, errs in invalid_files:
            print(f"  - {p.name}:")
            for e in errs:
                print(f"      {e}")

    if args.hallucination_report:
        args.hallucination_report.parent.mkdir(parents=True, exist_ok=True)
        args.hallucination_report.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8",
        )
        print(f"\nhallucination report → {args.hallucination_report}")

    if args.strict:
        if invalid_files:
            return 1
        if coverage_warning:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
