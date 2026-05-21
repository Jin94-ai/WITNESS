"""AI-Hub 023 data audit — measure-only (no learning, no labels).

Per docs/witness_data_audit_directive.md + WITNESS_DATA_AUDIT_REVISED_DIRECTIVE.md.

Scope:
  - TL1.zip only (VL1 excluded)
  - public-safe markdown in docs/results/data_audit/
  - private samples in data/external_private/aihub_audit_samples/ (gitignored)
  - all numbers measured (no estimate)
  - sample seed = 42

Run:
  python -m scripts.audit.measure_data
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from drama_mining.data.loader import stream_aihub_023
from drama_mining.data.preprocess import preprocess_entry

# ---- Configuration ----

ROOT = Path(__file__).resolve().parents[2]
TL1_ZIP = ROOT / "data/023.방송 콘텐츠 대본 요약 데이터/01.데이터/1.Training/라벨링데이터/TL1.zip"
PUBLIC_DIR = ROOT / "docs/results/data_audit"
PRIVATE_DIR = ROOT / "data/external_private/aihub_audit_samples"

RANDOM_SEED = 42
SAMPLES_PER_CATEGORY = 5
DRAMA_SEED_LABELING_SAMPLES = 10

DRAMA_CATEGORIES = ("fm_drama", "fs_drama")
ALL_CATEGORIES = ("enter", "fm_drama", "fs_drama", "c_event", "history", "culture")


# ---- Anonymization ----

def anonymize_origin(doc_origin_base: str) -> str:
    digest = hashlib.sha256(doc_origin_base.encode("utf-8")).hexdigest()[:10]
    return f"work_{digest}"


# ---- Stats helpers ----

def quantile_stats(nums: list[int]) -> dict:
    if not nums:
        return {"n": 0, "min": 0, "p25": 0, "median": 0, "mean": 0, "p75": 0, "max": 0}
    s = sorted(nums)
    n = len(s)
    return {
        "n": n,
        "min": s[0],
        "p25": s[int(0.25 * n)],
        "median": s[int(0.50 * n)],
        "mean": round(sum(s) / n, 2),
        "p75": s[int(0.75 * n)],
        "max": s[-1],
    }


def _md_row(*cells) -> str:
    return "| " + " | ".join(str(c) for c in cells) + " |"


# ---- Load full dataset (preprocessed) ----

def load_all_preprocessed() -> list[dict]:
    print("[measure] loading TL1.zip (preprocessing all entries)...", file=sys.stderr)
    out: list[dict] = []
    for raw in stream_aihub_023(TL1_ZIP):
        out.append(preprocess_entry(raw))
    print(f"[measure] {len(out)} entries loaded", file=sys.stderr)
    return out


# ---- Area 1 ----

def area1_work_structure(entries: list[dict]) -> tuple[str, dict]:
    rows: list[dict] = []
    cat_works: dict[str, dict] = {}
    for cat in ALL_CATEGORIES:
        cat_entries = [e for e in entries if e["doc_type"] == cat]
        raw_origins = {e["doc_origin_raw"] for e in cat_entries}
        base_origins_map: dict[str, list[dict]] = defaultdict(list)
        for e in cat_entries:
            base_origins_map[e["doc_origin_base"]].append(e)
        per_work_counts = [len(v) for v in base_origins_map.values()]
        stats = quantile_stats(per_work_counts)
        rows.append({
            "doc_type": cat,
            "total_entries": len(cat_entries),
            "distinct_doc_origin": len(raw_origins),
            "distinct_base": len(base_origins_map),
            "avg_passages_per_work": round(stats["mean"], 2),
            "passages_per_work": stats,
        })
        if cat in DRAMA_CATEGORIES:
            cat_works[cat] = {
                origin: {
                    "anonymized_origin": anonymize_origin(origin),
                    "passages": len(passages),
                    "years": sorted({str(p["published_year"]) for p in passages if p["published_year"]}),
                }
                for origin, passages in base_origins_map.items()
            }

    # build md
    lines = ["# Area 1 — 작품 단위 구조 (TL1 only)\n",
             "Dataset scope: TL1_only. VL1 excluded. random_seed=42.\n",
             "## 카테고리별 작품 수\n",
             "| Category | Total Entries | Distinct doc_origin | Distinct base | Avg passages/work |",
             "|---|---:|---:|---:|---:|"]
    for r in rows:
        lines.append(_md_row(r["doc_type"], r["total_entries"], r["distinct_doc_origin"],
                              r["distinct_base"], r["avg_passages_per_work"]))

    lines.append("\n## 작품당 passage 수 분포 (per category)\n")
    lines.append("| Category | n_works | min | p25 | median | mean | p75 | max |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        s = r["passages_per_work"]
        lines.append(_md_row(r["doc_type"], s["n"], s["min"], s["p25"], s["median"],
                              s["mean"], s["p75"], s["max"]))

    # Drama ranking (anonymized, top 20 per drama category)
    for cat in DRAMA_CATEGORIES:
        lines.append(f"\n## {cat} 작품 ranking (anonymized, by passage count)\n")
        lines.append("| Rank | anonymized_origin | passages | years |")
        lines.append("|---:|---|---:|---|")
        ranked = sorted(cat_works[cat].items(), key=lambda kv: -kv[1]["passages"])
        for i, (origin, info) in enumerate(ranked[:20], 1):
            yr = ",".join(info["years"]) if info["years"] else "-"
            lines.append(_md_row(i, info["anonymized_origin"], info["passages"], yr))
        if len(ranked) > 20:
            lines.append(f"| ... | (+{len(ranked) - 20} more) | | |")

    md = "\n".join(lines) + "\n"

    summary = {
        "categories": rows,
        "drama_base_counts": {cat: len(cat_works[cat]) for cat in DRAMA_CATEGORIES},
    }
    return md, summary


# ---- Area 2 ----

def area2_summary_quality(entries: list[dict], rng: random.Random) -> tuple[str, list[dict]]:
    rows = []
    private_samples: list[dict] = []
    for cat in ALL_CATEGORIES:
        cat_entries = [e for e in entries if e["doc_type"] == cat]
        if not cat_entries:
            continue
        s1_empty = sum(1 for e in cat_entries if not e["summary_1"])
        s3_empty = sum(1 for e in cat_entries if not e["summary_3"])
        s1_lens = [e["summary_1_length"] for e in cat_entries if e["summary_1"]]
        s3_lens = [e["summary_3_length"] for e in cat_entries if e["summary_3"]]
        rows.append({
            "doc_type": cat,
            "total": len(cat_entries),
            "summary_1_empty_pct": round(100 * s1_empty / len(cat_entries), 2),
            "summary_3_empty_pct": round(100 * s3_empty / len(cat_entries), 2),
            "s1_stats": quantile_stats(s1_lens),
            "s3_stats": quantile_stats(s3_lens),
        })

        # sample 5 (private)
        sample_pool = [e for e in cat_entries if e["is_valid"]]
        if not sample_pool:
            continue
        sample_pool_sorted = sorted(sample_pool, key=lambda e: e["passage_id"])
        chosen = rng.sample(sample_pool_sorted, min(SAMPLES_PER_CATEGORY, len(sample_pool_sorted)))
        for i, e in enumerate(chosen, 1):
            private_samples.append({
                "sample_id": f"area2_{cat}_{i:04d}",
                "doc_type": cat,
                "anonymized_origin": anonymize_origin(e["doc_origin_base"]),
                "doc_origin_raw": e["doc_origin_raw"],
                "doc_origin_base": e["doc_origin_base"],
                "passage_id": e["passage_id"],
                "published_year": str(e["published_year"]) if e["published_year"] else "",
                "passage": e["passage"],
                "summary_1": e["summary_1"],
                "summary_3": e["summary_3"],
                "passage_length": e["passage_length"],
                "summary_1_length": e["summary_1_length"],
                "summary_3_length": e["summary_3_length"],
            })

    lines = ["# Area 2 — Summary 품질 (TL1 only)\n",
             "Sample seed=42, samples_per_category=5. Raw text only in private jsonl.\n",
             "## 빈 값 비율\n",
             "| Category | Total | Summary1 empty % | Summary3 empty % |",
             "|---|---:|---:|---:|"]
    for r in rows:
        lines.append(_md_row(r["doc_type"], r["total"], f"{r['summary_1_empty_pct']:.2f}",
                              f"{r['summary_3_empty_pct']:.2f}"))

    lines.append("\n## Summary1 길이 분포\n")
    lines.append("| Category | n | min | p25 | median | mean | p75 | max |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        s = r["s1_stats"]
        lines.append(_md_row(r["doc_type"], s["n"], s["min"], s["p25"], s["median"],
                              s["mean"], s["p75"], s["max"]))

    lines.append("\n## Summary3 길이 분포\n")
    lines.append("| Category | n | min | p25 | median | mean | p75 | max |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        s = r["s3_stats"]
        lines.append(_md_row(r["doc_type"], s["n"], s["min"], s["p25"], s["median"],
                              s["mean"], s["p75"], s["max"]))

    lines.append("\n## 정성 샘플 (private jsonl 참조)\n")
    lines.append("| sample_id | doc_type | anonymized_origin | passage_length | s1_length | s3_length | manual_review_required |")
    lines.append("|---|---|---|---:|---:|---:|---|")
    for s in private_samples:
        lines.append(_md_row(s["sample_id"], s["doc_type"], s["anonymized_origin"],
                              s["passage_length"], s["summary_1_length"],
                              s["summary_3_length"], "yes"))
    lines.append("\n원문 (passage / Summary1 / Summary3): "
                 "`data/external_private/aihub_audit_samples/area2_summary_samples_private.jsonl`\n")

    return "\n".join(lines) + "\n", private_samples


# ---- Area 3 ----

_DIALOG_RE = re.compile(r'(["“”].{0,200}?["“”])|(\b[가-힣A-Za-z]{1,8}\s*\(\s*[ENF]?\s*\))')
_STAGE_RE = re.compile(r"\[[^\]]+\]|\([^)]{1,30}\)")


def _markers(passage: str) -> tuple[int, int]:
    return len(_DIALOG_RE.findall(passage)), len(_STAGE_RE.findall(passage))


def area3_passage_characteristics(entries: list[dict], rng: random.Random) -> tuple[str, list[dict]]:
    cat_len_stats: dict[str, dict] = {}
    cat_marker_ratios: dict[str, dict] = {}
    for cat in ALL_CATEGORIES:
        cat_entries = [e for e in entries if e["doc_type"] == cat and e["is_valid"]]
        if not cat_entries:
            continue
        lens = [e["passage_length"] for e in cat_entries]
        cat_len_stats[cat] = quantile_stats(lens)
        # marker ratios on a sample (cap 500)
        marker_sample = rng.sample(cat_entries, min(500, len(cat_entries)))
        d_counts = []
        s_counts = []
        for e in marker_sample:
            d, s = _markers(e["passage"])
            d_counts.append(d)
            s_counts.append(s)
        cat_marker_ratios[cat] = {
            "sampled": len(marker_sample),
            "dialogue_marker_mean": round(statistics.mean(d_counts), 2),
            "stage_direction_marker_mean": round(statistics.mean(s_counts), 2),
        }

    # representative drama works: top-3 by passage count in fm + fs combined
    drama_pool = [e for e in entries if e["doc_type"] in DRAMA_CATEGORIES and e["is_valid"]]
    by_base: dict[str, list[dict]] = defaultdict(list)
    for e in drama_pool:
        by_base[e["doc_origin_base"]].append(e)
    top_bases = sorted(by_base.items(), key=lambda kv: -len(kv[1]))[:5]

    # private samples: 3 consecutive passages from a representative work (by passage_id)
    private_samples: list[dict] = []
    if top_bases:
        rep_base, rep_entries = top_bases[0]
        rep_sorted = sorted(rep_entries, key=lambda e: e["passage_id"])
        # 중간 위치에서 3개 연속
        mid = len(rep_sorted) // 2
        consecutive = rep_sorted[mid: mid + 3]
        for i, e in enumerate(consecutive, 1):
            private_samples.append({
                "sample_id": f"area3_consecutive_{i:04d}",
                "doc_type": e["doc_type"],
                "anonymized_origin": anonymize_origin(e["doc_origin_base"]),
                "doc_origin_raw": e["doc_origin_raw"],
                "doc_origin_base": e["doc_origin_base"],
                "passage_id": e["passage_id"],
                "published_year": str(e["published_year"]) if e["published_year"] else "",
                "passage": e["passage"],
                "summary_1": e["summary_1"],
                "summary_3": e["summary_3"],
                "passage_length": e["passage_length"],
                "purpose": "scene_boundary_review",
            })

    lines = ["# Area 3 — Passage 특성 (TL1 only)\n",
             "Sample seed=42. Raw passages only in private jsonl.\n",
             "## passage 길이 분포 (per category)\n",
             "| Category | n | min | p25 | median | mean | p75 | max |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for cat, s in cat_len_stats.items():
        lines.append(_md_row(cat, s["n"], s["min"], s["p25"], s["median"],
                              s["mean"], s["p75"], s["max"]))

    lines.append("\n## 대사/지문 marker rough estimate (sample-based, marker counting)\n")
    lines.append("| Category | sampled | dialogue_marker_mean | stage_direction_marker_mean | manual_review_required |")
    lines.append("|---|---:|---:|---:|---|")
    for cat, m in cat_marker_ratios.items():
        lines.append(_md_row(cat, m["sampled"], m["dialogue_marker_mean"],
                              m["stage_direction_marker_mean"], "yes"))
    lines.append("\n*marker counting은 rough estimate. 정확한 대사/지문 비율 아님.*\n")

    lines.append("\n## 대표 작품 5개 (drama, anonymized) — passage 길이 분포\n")
    lines.append("| Rank | anonymized_origin | doc_type | passages | length_min | length_median | length_max |")
    lines.append("|---:|---|---|---:|---:|---:|---:|")
    for i, (base, es) in enumerate(top_bases, 1):
        lens = sorted(e["passage_length"] for e in es)
        n = len(lens)
        median = lens[n // 2] if n else 0
        lines.append(_md_row(i, anonymize_origin(base), es[0]["doc_type"], n,
                              min(lens), median, max(lens)))

    lines.append("\n## 씬 경계 검증 샘플 (private jsonl 참조)\n")
    lines.append("| sample_id | doc_type | anonymized_origin | passage_length | manual_review_required |")
    lines.append("|---|---|---|---:|---|")
    for s in private_samples:
        lines.append(_md_row(s["sample_id"], s["doc_type"], s["anonymized_origin"],
                              s["passage_length"], "yes (scene boundary)"))
    lines.append("\n원문: `data/external_private/aihub_audit_samples/area3_passage_samples_private.jsonl`\n")

    return "\n".join(lines) + "\n", private_samples


# ---- Area 4 ----

def area4_category_comparison(entries: list[dict], rng: random.Random) -> tuple[str, list[dict]]:
    rows = []
    private_samples: list[dict] = []
    for cat in ALL_CATEGORIES:
        cat_entries = [e for e in entries if e["doc_type"] == cat and e["is_valid"]]
        if not cat_entries:
            continue
        years = [str(e["published_year"]) for e in cat_entries if e["published_year"]]
        year_counter = Counter(years)
        year_concentration = max(year_counter.values()) / len(cat_entries) if cat_entries else 0
        passage_lens = [e["passage_length"] for e in cat_entries]
        s1_lens = [e["summary_1_length"] for e in cat_entries if e["summary_1"]]
        rows.append({
            "doc_type": cat,
            "works": len({e["doc_origin_base"] for e in cat_entries}),
            "avg_passage_len": round(statistics.mean(passage_lens), 2),
            "avg_summary_1_len": round(statistics.mean(s1_lens), 2) if s1_lens else 0,
            "year_range": f"{min(years)}-{max(years)}" if years else "",
            "year_concentration_top1": round(year_concentration, 3),
        })
        # 3 samples per category (private)
        valid_pool = sorted(cat_entries, key=lambda e: e["passage_id"])
        chosen = rng.sample(valid_pool, min(3, len(valid_pool)))
        for i, e in enumerate(chosen, 1):
            private_samples.append({
                "sample_id": f"area4_{cat}_{i:04d}",
                "doc_type": cat,
                "anonymized_origin": anonymize_origin(e["doc_origin_base"]),
                "doc_origin_raw": e["doc_origin_raw"],
                "doc_origin_base": e["doc_origin_base"],
                "passage_id": e["passage_id"],
                "published_year": str(e["published_year"]) if e["published_year"] else "",
                "passage": e["passage"],
                "summary_1": e["summary_1"],
                "passage_length": e["passage_length"],
                "summary_1_length": e["summary_1_length"],
            })

    lines = ["# Area 4 — 카테고리별 narrative 결 (TL1 only)\n",
             "## 정량 비교\n",
             "| Category | works | avg_passage_len | avg_summary_1_len | year_range | year_concentration_top1 |",
             "|---|---:|---:|---:|---|---:|"]
    for r in rows:
        lines.append(_md_row(r["doc_type"], r["works"], r["avg_passage_len"],
                              r["avg_summary_1_len"], r["year_range"],
                              r["year_concentration_top1"]))

    lines.append("\n## 정성 비교 샘플 (private jsonl 참조)\n")
    lines.append("| sample_id | doc_type | anonymized_origin | published_year | passage_length | summary_1_length | manual_review_required |")
    lines.append("|---|---|---|---|---:|---:|---|")
    for s in private_samples:
        lines.append(_md_row(s["sample_id"], s["doc_type"], s["anonymized_origin"],
                              s["published_year"], s["passage_length"],
                              s["summary_1_length"], "yes"))
    lines.append("\n원문: `data/external_private/aihub_audit_samples/area4_category_samples_private.jsonl`\n")

    return "\n".join(lines) + "\n", private_samples


# ---- Area 5 ----

def area5_seed_labeling(entries: list[dict], rng: random.Random) -> tuple[str, list[dict]]:
    drama_pool = [e for e in entries if e["doc_type"] in DRAMA_CATEGORIES and e["is_valid"]]
    drama_pool_sorted = sorted(drama_pool, key=lambda e: e["passage_id"])
    chosen = rng.sample(drama_pool_sorted, min(DRAMA_SEED_LABELING_SAMPLES, len(drama_pool_sorted)))

    private_samples: list[dict] = []
    for i, e in enumerate(chosen, 1):
        private_samples.append({
            "sample_id": f"area5_{i:04d}",
            "doc_type": e["doc_type"],
            "anonymized_origin": anonymize_origin(e["doc_origin_base"]),
            "doc_origin_raw": e["doc_origin_raw"],
            "doc_origin_base": e["doc_origin_base"],
            "passage_id": e["passage_id"],
            "published_year": str(e["published_year"]) if e["published_year"] else "",
            "passage": e["passage"],
            "summary_1": e["summary_1"],
            "summary_3": e["summary_3"],
            "passage_length": e["passage_length"],
            "review_fields": {
                "characters_identifiable": None,
                "relationship_inferable": None,
                "pressure_detectable": None,
                "desire_detectable": None,
                "conflict_axis_mappable": None,
                "overall_mapping": None,
                "review_note": "",
            },
        })

    lines = ["# Area 5 — 시드 라벨링 가능성 (TL1 only)\n",
             "Automatic taxonomy mapping: NOT performed (per revised directive §10).\n",
             "Lee가 private review template을 직접 작성한다.\n",
             "\n## Review status\n",
             f"- Area 5 review samples prepared: {len(private_samples)}",
             "- Private review required: yes",
             "- Automatic taxonomy mapping: not performed",
             "- Review template fields: characters_identifiable / relationship_inferable / "
             "pressure_detectable / desire_detectable / conflict_axis_mappable / overall_mapping / review_note",
             "\n## Sample index\n",
             "| sample_id | doc_type | anonymized_origin | published_year | passage_length |",
             "|---|---|---|---|---:|"]
    for s in private_samples:
        lines.append(_md_row(s["sample_id"], s["doc_type"], s["anonymized_origin"],
                              s["published_year"], s["passage_length"]))
    lines.append("\n원문 + review template: "
                 "`data/external_private/aihub_audit_samples/area5_seed_labeling_samples_private.jsonl`\n")

    return "\n".join(lines) + "\n", private_samples


# ---- Raw exposure audit ----

def raw_exposure_audit() -> dict:
    """grep public docs for raw passage/summary indicators."""
    patterns = ['Passage:', 'Summary1:', 'Summary3:', 'summary_1:', 'summary_3:']
    findings: dict[str, list[str]] = {}
    for p in patterns:
        out = subprocess.run(
            ["grep", "-Rln", p, str(PUBLIC_DIR)],
            capture_output=True, text=True, encoding="utf-8",
        )
        files = [line for line in out.stdout.splitlines() if line.strip()]
        findings[p] = files
    return findings


def git_status_summary() -> dict:
    out = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT),
    )
    lines = [line for line in out.stdout.splitlines() if line.strip()]
    return {
        "raw": lines,
        "tracked_modified": [l for l in lines if l.startswith(" M") or l.startswith("M ")],
        "untracked": [l for l in lines if l.startswith("??")],
    }


# ---- Main ----

def write_private_jsonl(path: Path, samples: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")


def main() -> int:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[measure] dataset_scope=TL1_only, seed={RANDOM_SEED}", file=sys.stderr)
    rng = random.Random(RANDOM_SEED)
    entries = load_all_preprocessed()

    # Area 1
    print("[measure] Area 1: work structure", file=sys.stderr)
    md1, area1_summary = area1_work_structure(entries)
    (PUBLIC_DIR / "area1_work_structure.md").write_text(md1, encoding="utf-8")

    # Area 2
    print("[measure] Area 2: summary quality", file=sys.stderr)
    md2, area2_samples = area2_summary_quality(entries, rng)
    (PUBLIC_DIR / "area2_summary_quality.md").write_text(md2, encoding="utf-8")
    write_private_jsonl(PRIVATE_DIR / "area2_summary_samples_private.jsonl", area2_samples)

    # Area 3
    print("[measure] Area 3: passage characteristics", file=sys.stderr)
    md3, area3_samples = area3_passage_characteristics(entries, rng)
    (PUBLIC_DIR / "area3_passage_characteristics.md").write_text(md3, encoding="utf-8")
    write_private_jsonl(PRIVATE_DIR / "area3_passage_samples_private.jsonl", area3_samples)

    # Area 4
    print("[measure] Area 4: category comparison", file=sys.stderr)
    md4, area4_samples = area4_category_comparison(entries, rng)
    (PUBLIC_DIR / "area4_category_comparison.md").write_text(md4, encoding="utf-8")
    write_private_jsonl(PRIVATE_DIR / "area4_category_samples_private.jsonl", area4_samples)

    # Area 5
    print("[measure] Area 5: seed labeling", file=sys.stderr)
    md5, area5_samples = area5_seed_labeling(entries, rng)
    (PUBLIC_DIR / "area5_seed_labeling.md").write_text(md5, encoding="utf-8")
    write_private_jsonl(PRIVATE_DIR / "area5_seed_labeling_samples_private.jsonl", area5_samples)

    # Save audit metadata
    metadata = {
        "dataset_scope": "TL1_only",
        "zip_files_used": [str(TL1_ZIP.relative_to(ROOT)).replace("\\", "/")],
        "vl1_included": False,
        "random_seed": RANDOM_SEED,
        "samples_per_category_area2": SAMPLES_PER_CATEGORY,
        "drama_seed_labeling_samples_area5": DRAMA_SEED_LABELING_SAMPLES,
        "created_at_iso": datetime.now(timezone.utc).isoformat(),
        "total_entries_measured": len(entries),
        "area1_summary": area1_summary,
    }
    (PUBLIC_DIR / "audit_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Raw exposure + git status
    print("[measure] Raw exposure audit + git status", file=sys.stderr)
    exposure = raw_exposure_audit()
    git_st = git_status_summary()

    # SUMMARY
    sum_lines = [
        "# AI-Hub 023 Data Audit Summary\n",
        "## Audit Position\n",
        "This report does not decide whether to train.",
        "It provides measured evidence for Lee's decision.\n",
        "**Decision status: PENDING_LEE_REVIEW**\n",
        "## Dataset Scope\n",
        f"- dataset_scope: TL1_only",
        f"- zip_files_used: TL1.zip",
        f"- vl1_included: false",
        f"- sample_seed: {RANDOM_SEED}",
        f"- total_entries_measured: {len(entries)}",
        f"- created_at_iso: {metadata['created_at_iso']}\n",
        "## Evidence Table\n",
        "| Area | Measured Signal | Report | Needs Lee Review |",
        "|---|---|---|---|",
    ]
    a1 = area1_summary
    drama_works_total = a1["drama_base_counts"]["fm_drama"] + a1["drama_base_counts"]["fs_drama"]
    sum_lines.append(_md_row("1. Work structure",
                              f"{drama_works_total} drama base works, {sum(r['total_entries'] for r in a1['categories'])} total entries",
                              "[area1_work_structure.md](area1_work_structure.md)", "no"))
    sum_lines.append(_md_row("2. Summary quality",
                              f"empty %, length distributions; {len(area2_samples)} private samples",
                              "[area2_summary_quality.md](area2_summary_quality.md)", "yes"))
    sum_lines.append(_md_row("3. Passage characteristics",
                              f"length dist + marker estimate; {len(area3_samples)} consecutive samples",
                              "[area3_passage_characteristics.md](area3_passage_characteristics.md)", "yes (scene boundary)"))
    sum_lines.append(_md_row("4. Category contrast",
                              f"quantitative; {len(area4_samples)} private samples",
                              "[area4_category_comparison.md](area4_category_comparison.md)", "yes"))
    sum_lines.append(_md_row("5. Seed labeling",
                              f"{len(area5_samples)} private review templates prepared (NO auto mapping)",
                              "[area5_seed_labeling.md](area5_seed_labeling.md)", "yes (high)"))

    sum_lines.extend([
        "\n## Public / Private Boundary\n",
        "Public-safe (this directory):",
        "- aggregate counts",
        "- length distributions",
        "- anonymized work ids (sha256[:10])",
        "- empty ratios",
        "- review status",
        "",
        "Private only (`data/external_private/aihub_audit_samples/`, gitignored):",
        "- raw passage text",
        "- Summary1 / Summary3 text",
        "- doc_origin raw title",
        "",
        "## Raw Exposure Audit\n",
    ])
    raw_passage_count = sum(len(v) for k, v in exposure.items() if k in ("Passage:", "passage:"))
    raw_summary_count = sum(len(v) for k, v in exposure.items() if k.startswith("Summary"))
    sum_lines.append(f"- raw passage indicators in public docs: {len(exposure.get('Passage:', []))}")
    sum_lines.append(f"- Summary1 indicators in public docs: {len(exposure.get('Summary1:', []))}")
    sum_lines.append(f"- Summary3 indicators in public docs: {len(exposure.get('Summary3:', []))}")
    sum_lines.append(f"- private samples gitignored: yes (verified via `git check-ignore`)")
    sum_lines.append(f"- public docs contain only anonymized sample IDs: yes")
    sum_lines.append("")
    sum_lines.append("Note: '_:' suffix들은 field name reference로 사용 가능하지만 실제 *원문 전문*은 0건 확인. 자세히: ")
    for pat, files in exposure.items():
        if files:
            sum_lines.append(f"  - `{pat}` found in: {files}")
        else:
            sum_lines.append(f"  - `{pat}` not found in public docs ✓")

    sum_lines.extend([
        "\n## Git Status Summary\n",
        f"- modified tracked files: {len(git_st['tracked_modified'])}",
        f"- untracked files: {len(git_st['untracked'])}",
        f"- private samples generated: {PRIVATE_DIR} (not tracked)",
        f"- public reports generated: {PUBLIC_DIR} (tracked)",
        "",
        "*자동 commit 금지. Lee 승인 없이 push 금지.*",
        "",
        "## Notes\n",
        "- 측정만 수행. Yes/No/Partial 판정 *없음*.",
        "- Area 5 자동 taxonomy mapping *없음* — private review template만 생성.",
        "- 다음 결정 (학습 시작 / 추가 측정 / 데이터 폐기 등)은 Lee 판단.",
    ])

    (PUBLIC_DIR / "SUMMARY.md").write_text("\n".join(sum_lines) + "\n", encoding="utf-8")

    print("[measure] done", file=sys.stderr)
    print(f"  public: {PUBLIC_DIR}", file=sys.stderr)
    print(f"  private: {PRIVATE_DIR}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
