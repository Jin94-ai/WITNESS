"""Phase D -- 3-종 separability test + consistency test.

Spec §5.2 verbatim:
    - Linear separability (LogReg 5-fold CV): target >= 0.6
    - Consistency test (k-means cluster 내 동일 action 비율): target mean > 0.7
    - Feature importance (RandomForest): per-action top-3 feature 뚜렷

출력: docs/person/diagnostics/separability_v2.md (spec §5.4).
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sklearn.cluster import KMeans  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.model_selection import cross_val_score  # noqa: E402


def run_separability_tests(X, y, vocab, feature_names):
    # 1. Linear separability (5-fold CV on LogReg)
    lr = LogisticRegression(max_iter=3000)
    lr_scores = cross_val_score(lr, X, y, cv=5)
    lr_mean = float(lr_scores.mean())
    lr_std = float(lr_scores.std())

    # 2. Consistency test (k-means k=30, in-cluster action homogeneity)
    k = min(30, len(np.unique(y)) * 2)
    km = KMeans(n_clusters=k, random_state=0, n_init=5)
    cluster_labels = km.fit_predict(X)
    consistencies = []
    for c in range(k):
        mask = cluster_labels == c
        if mask.sum() < 2:
            continue
        in_cluster_y = y[mask]
        most_common_count = Counter(in_cluster_y.tolist()).most_common(1)[0][1]
        consistency = most_common_count / mask.sum()
        consistencies.append(consistency)
    consistency_mean = float(np.mean(consistencies))
    consistency_min = float(np.min(consistencies))
    consistency_max = float(np.max(consistencies))

    # 3. Feature importance per action (RF + per-class shift)
    rf = RandomForestClassifier(n_estimators=150, random_state=0)
    rf.fit(X, y)
    global_imp = rf.feature_importances_.tolist()

    # Per-action importance: feature value shift from global mean
    global_mean = X.mean(axis=0)
    per_action_top: dict[str, list[tuple[str, float]]] = {}
    for idx, a in enumerate(vocab):
        mask = y == idx
        if mask.sum() < 2:
            continue
        class_mean = X[mask].mean(axis=0)
        shift = np.abs(class_mean - global_mean) / (X.std(axis=0) + 1e-8)
        top3 = sorted(enumerate(shift), key=lambda kv: -kv[1])[:3]
        per_action_top[a] = [
            (feature_names[i], float(shift[i])) for i, _ in top3
        ]

    return {
        "linear_cv_mean": lr_mean,
        "linear_cv_std": lr_std,
        "linear_cv_pass": lr_mean >= 0.6,
        "consistency_mean": consistency_mean,
        "consistency_min": consistency_min,
        "consistency_max": consistency_max,
        "consistency_pass": consistency_mean > 0.7,
        "global_feature_importance": dict(zip(feature_names, global_imp)),
        "per_action_top3_features": per_action_top,
    }


def render_markdown(report: dict, dataset_info: dict) -> str:
    lines = [
        "# Phase D -- Separability Test Report",
        "",
        "**생성**: `scripts/data_pipeline/separability_check.py`",
        f"**Dataset**: balanced_for_training (n={dataset_info['n_samples']}, "
        f"classes={dataset_info['n_classes']}, feature_dim={dataset_info['feature_dim']})",
        "",
        "## Spec §5.2.1 -- Linear Separability Test",
        "",
        "| Metric | Value | Target | Pass |",
        "|---|---:|---:|:---:|",
        f"| 5-fold CV acc (LogReg) | {report['linear_cv_mean']:.3f} ± {report['linear_cv_std']:.3f} | >= 0.6 | {'✓' if report['linear_cv_pass'] else '✗'} |",
        "",
        "## Spec §5.2.2 -- Consistency Test",
        "",
        "KMeans(k=30) 클러스터 내 동일 action 비율.",
        "",
        "| Metric | Value | Target | Pass |",
        "|---|---:|---:|:---:|",
        f"| Mean in-cluster consistency | {report['consistency_mean']:.3f} | > 0.7 | {'✓' if report['consistency_pass'] else '✗'} |",
        f"| Min | {report['consistency_min']:.3f} | - | - |",
        f"| Max | {report['consistency_max']:.3f} | - | - |",
        "",
        "## Spec §5.2.3 -- Feature Importance",
        "",
        "### Global feature importance (RandomForest)",
        "",
        "| Feature | Importance |",
        "|---|---:|",
    ]
    for f, imp in sorted(report["global_feature_importance"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| {f} | {imp:.3f} |")
    lines += [
        "",
        "### Per-action top-3 distinguishing features",
        "",
        "(action별 state 평균과 전체 state 평균의 차이. 큰 값일수록 해당 action을 구분짓는 feature.)",
        "",
        "| action | top 1 | top 2 | top 3 |",
        "|---|---|---|---|",
    ]
    for a, top3 in sorted(report["per_action_top3_features"].items()):
        cells = " | ".join(f"{f} ({s:.2f})" for f, s in top3)
        lines.append(f"| {a} | {cells} |")

    # Overall pass
    overall_pass = report["linear_cv_pass"] and report["consistency_pass"]
    lines += [
        "",
        "## Overall Phase D Result",
        "",
        f"- Linear separability: {'PASS' if report['linear_cv_pass'] else 'FAIL'}",
        f"- Consistency: {'PASS' if report['consistency_pass'] else 'FAIL'}",
        f"- **Phase D {'PASS' if overall_pass else 'FAIL'}**",
        "",
    ]
    if not overall_pass:
        lines += [
            "## Spec §5.3 -- 실패 처방",
            "",
        ]
        if not report["linear_cv_pass"]:
            lines.append("- Linear acc < 0.6 → Phase A 재실행, target state 재설계")
        if not report["consistency_pass"]:
            lines.append("- Consistency < 0.7 → Phase B (event context feature) 강화")
    return "\n".join(lines)


def main() -> int:
    PIPELINE = ROOT / "data" / "person" / "pipeline_v2"

    # Load balanced_for_training
    ds_path = PIPELINE / "balanced_for_training" / "dataset.npz"
    meta = json.loads((PIPELINE / "balanced_for_training" / "meta.json").read_text(encoding="utf-8"))
    data = np.load(ds_path)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int64)
    vocab = meta["action_vocab"]

    # 15 feature names (12 base + 3 extended)
    feature_names = [
        "fear", "hope", "grief", "confusion", "love",
        "fatigue", "hunger", "health",
        "moral_injury", "identity_shift", "event_trauma", "trust_scar",
        "recent_event_id", "time_since_event", "hazard_proximity",
    ]

    print(f"[Phase D] dataset X={X.shape}, {len(vocab)} classes")

    report = run_separability_tests(X, y, vocab, feature_names)
    print(f"\n  linear CV acc:     {report['linear_cv_mean']:.3f} ± {report['linear_cv_std']:.3f}")
    print(f"  consistency mean:  {report['consistency_mean']:.3f}")
    print(f"  consistency range: [{report['consistency_min']:.3f}, {report['consistency_max']:.3f}]")

    md = render_markdown(report, {
        "n_samples": X.shape[0], "n_classes": len(vocab),
        "feature_dim": X.shape[1],
    })
    out_dir = ROOT / "docs" / "person" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "separability_v2.md").write_text(md, encoding="utf-8")

    (out_dir / "separability_v2.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    print(f"\n  saved: {out_dir}/separability_v2.md")
    print(f"         {out_dir}/separability_v2.json")

    # Exit code indicates pass/fail
    overall_pass = report["linear_cv_pass"] and report["consistency_pass"]
    print(f"\n  OVERALL: {'PASS' if overall_pass else 'FAIL'}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
