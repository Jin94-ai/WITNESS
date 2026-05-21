"""Stage 2.1 — TL1.zip → train/val/test.jsonl with Summary2 filter.

Per docs/witness_train_directive_2.md §1.

Run (Python 3.11):
    "C:/Program Files/Python311/python.exe" -m scripts.witness_train.stage2_1_parse
"""

from __future__ import annotations

import json
import random
import statistics
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from drama_mining.data.preprocess import extract_origin_base

ROOT = Path(__file__).resolve().parents[2]
TL1_ZIP = ROOT / "data" / "023.방송 콘텐츠 대본 요약 데이터" / "01.데이터" / "1.Training" / "라벨링데이터" / "TL1.zip"
OUT_DIR = ROOT / "data" / "processed" / "witness_v2"

SEED = 42
DOC_TYPES = ("fm_drama", "fs_drama")
SPLIT_RATIOS = (0.90, 0.05, 0.05)


def stream_pairs() -> list[dict]:
    """TL1.zip → list of (summary2, passage) pair dicts (drama + S2 non-empty only)."""
    pairs: list[dict] = []
    skipped = {"not_drama": 0, "empty_summary2": 0, "empty_passage": 0}
    with zipfile.ZipFile(TL1_ZIP) as z:
        names = [n for n in z.namelist() if n.endswith(".json")]
        for i, name in enumerate(names):
            if i % 10000 == 0:
                print(f"[parse] {i}/{len(names)}", file=sys.stderr, flush=True)
            try:
                data = json.loads(z.read(name).decode("utf-8"))
            except Exception:
                continue
            meta = data.get("Meta") or {}
            ann = data.get("Annotation") or {}
            doc_type = meta.get("doc_type", "")
            if doc_type not in DOC_TYPES:
                skipped["not_drama"] += 1
                continue
            summary2 = (ann.get("Summary2") or "").strip()
            passage = (meta.get("passage") or "").strip()
            if not summary2:
                skipped["empty_summary2"] += 1
                continue
            if not passage:
                skipped["empty_passage"] += 1
                continue
            pairs.append({
                "passage_id": meta.get("passage_id", ""),
                "doc_id": meta.get("doc_id", ""),
                "doc_type": doc_type,
                "doc_origin": meta.get("doc_origin", ""),
                "published_year": meta.get("published_year", ""),
                "summary2": summary2,
                "passage": passage,
            })
    print(f"[parse] kept {len(pairs)}, skipped {skipped}", file=sys.stderr, flush=True)
    return pairs


def _origin_base(doc_origin: str) -> str:
    return extract_origin_base(doc_origin.strip())


def split_by_origin(pairs: list[dict], rng: random.Random) -> tuple[list[dict], list[dict], list[dict]]:
    """작품 단위 90/5/5 split — Stage 1과 동일 알고리즘 (class-stratified greedy)."""
    by_origin: dict[str, list[dict]] = defaultdict(list)
    origin_doc_type: dict[str, str] = {}
    for p in pairs:
        key = _origin_base(p["doc_origin"]) or p["doc_id"][:6]
        by_origin[key].append(p)
        origin_doc_type[key] = p["doc_type"]

    split_origins: list[list[str]] = [[], [], []]
    for cat in DOC_TYPES:
        cat_origins = sorted([o for o in by_origin.keys() if origin_doc_type[o] == cat])
        if not cat_origins:
            continue
        rng.shuffle(cat_origins)
        cat_total = sum(len(by_origin[o]) for o in cat_origins)
        targets = [cat_total * r for r in SPLIT_RATIOS]
        cat_split: list[list[str]] = [[], [], []]
        cat_counts = [0, 0, 0]
        for o in sorted(cat_origins, key=lambda k: -len(by_origin[k])):
            deficits = [(targets[i] - cat_counts[i]) / targets[i] if targets[i] > 0 else -1 for i in range(3)]
            idx = max(range(3), key=deficits.__getitem__)
            cat_split[idx].append(o)
            cat_counts[idx] += len(by_origin[o])
        for i in range(3):
            split_origins[i].extend(cat_split[i])

    return (
        [p for o in split_origins[0] for p in by_origin[o]],
        [p for o in split_origins[1] for p in by_origin[o]],
        [p for o in split_origins[2] for p in by_origin[o]],
    )


def _len_stats(values: list[int]) -> dict:
    if not values:
        return {"n": 0, "min": 0, "mean": 0, "median": 0, "max": 0, "p95": None}
    return {
        "n": len(values),
        "min": min(values),
        "mean": round(statistics.mean(values), 1),
        "median": int(statistics.median(values)),
        "max": max(values),
        "p95": int(sorted(values)[int(0.95 * len(values))]) if len(values) >= 20 else None,
    }


def write_split(split: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in split:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> int:
    rng = random.Random(SEED)
    print(f"[stage2.1] reading {TL1_ZIP}", file=sys.stderr, flush=True)
    pairs = stream_pairs()
    train, val, test = split_by_origin(pairs, rng)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_split(train, OUT_DIR / "train.jsonl")
    write_split(val, OUT_DIR / "val.jsonl")
    write_split(test, OUT_DIR / "test.jsonl")

    def doc_type_dist(s: list[dict]) -> dict:
        return dict(Counter(r["doc_type"] for r in s))

    summary_lens = [len(r["summary2"]) for r in pairs]
    passage_lens = [len(r["passage"]) for r in pairs]

    train_origins = {_origin_base(r["doc_origin"]) for r in train}
    val_origins = {_origin_base(r["doc_origin"]) for r in val}
    test_origins = {_origin_base(r["doc_origin"]) for r in test}

    stats = {
        "schema_version": "parse_stats_v2",
        "seed": SEED,
        "source_zip": str(TL1_ZIP.relative_to(ROOT)).replace("\\", "/"),
        "filter": "doc_type in {fm_drama, fs_drama} AND Annotation.Summary2 non-empty",
        "split_ratios": list(SPLIT_RATIOS),
        "totals": {
            "pairs_total": len(pairs),
            "train": len(train),
            "val": len(val),
            "test": len(test),
            "origins_train": len(train_origins),
            "origins_val": len(val_origins),
            "origins_test": len(test_origins),
        },
        "doc_type_distribution_overall": dict(Counter(r["doc_type"] for r in pairs)),
        "doc_type_distribution_per_split": {
            "train": doc_type_dist(train),
            "val": doc_type_dist(val),
            "test": doc_type_dist(test),
        },
        "summary2_length_chars": _len_stats(summary_lens),
        "passage_length_chars": _len_stats(passage_lens),
        "leakage_check": {
            "train_val_overlap": len(train_origins & val_origins),
            "train_test_overlap": len(train_origins & test_origins),
            "val_test_overlap": len(val_origins & test_origins),
        },
    }
    (OUT_DIR / "parse_stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(stats["totals"], ensure_ascii=False, indent=2))
    print(json.dumps(stats["doc_type_distribution_per_split"], ensure_ascii=False, indent=2))
    print(json.dumps(stats["summary2_length_chars"], ensure_ascii=False, indent=2))
    print(json.dumps(stats["leakage_check"], ensure_ascii=False, indent=2))
    print(f"[stage2.1] wrote {OUT_DIR}", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
