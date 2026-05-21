"""Work-level (doc_origin_base) train/val/test split with leakage prevention.

Per docs/witness_dm_day2_directive.md §4 + cycle 86 §3.

핵심: split 단위는 *doc_origin_base*. 같은 base 작품의 다른 회차가 train/val/test에
동시에 들어가면 leakage. test로 강제.

기본 사용:
    from drama_mining.data.split import split_by_origin_base, write_split

    entries = list(preprocess_stream(stream_aihub_023(zip_path)))
    train, val, test, meta = split_by_origin_base(entries, seed=42)
    write_split(Path("data/splits/v1"), train, val, test, meta)

CLI:
    python -m drama_mining.data.split \
        --zip-path "data/023.../TL1.zip" \
        --output-dir data/splits/v1 \
        --seed 42
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from drama_mining.data.loader import stream_aihub_023
from drama_mining.data.preprocess import preprocess_stream

# 기본 비율
DEFAULT_RATIOS = (0.70, 0.15, 0.15)


def _group_by_origin_base(entries: list[dict]) -> dict[str, list[dict]]:
    """doc_origin_base 단위로 grouping (passage list)."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        groups[e["doc_origin_base"]].append(e)
    return dict(groups)


def _assign_origins_to_splits(
    origins_ordered: list[str],
    origin_to_count: dict[str, int],
    ratios: tuple[float, float, float],
) -> tuple[list[str], list[str], list[str]]:
    """Origins를 train/val/test에 *passage count 균형*으로 배분 (greedy).

    Algorithm:
      - 큰 origin부터 순회
      - 현재 split별 누적 passage count / target ratio 가장 부족한 split에 추가
    """
    total = sum(origin_to_count.values())
    targets = [total * r for r in ratios]
    split_origins: list[list[str]] = [[], [], []]
    split_counts = [0, 0, 0]
    # large origin first (greedy balance)
    for origin in sorted(origins_ordered, key=lambda x: -origin_to_count[x]):
        # pick split with greatest deficit ratio
        deficits = [
            (targets[i] - split_counts[i]) / targets[i] if targets[i] > 0 else -1.0
            for i in range(3)
        ]
        idx = max(range(3), key=deficits.__getitem__)
        split_origins[idx].append(origin)
        split_counts[idx] += origin_to_count[origin]
    return split_origins[0], split_origins[1], split_origins[2]


def split_by_origin_base(
    entries: list[dict],
    *,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
    categories: tuple[str, ...] = ("fm_drama", "fs_drama"),
) -> tuple[list[dict], list[dict], list[dict], dict]:
    """작품 단위 split. valid entries만 사용. categories 필터.

    Returns:
        (train_entries, val_entries, test_entries, metadata)
    """
    eps = 1e-9
    if abs((train_ratio + val_ratio + test_ratio) - 1.0) > 1e-3:
        raise ValueError("ratios must sum to 1.0")

    # filter
    pool = [
        e for e in entries
        if e.get("is_valid") and e.get("doc_type") in categories
    ]
    if not pool:
        raise ValueError("empty pool after filter")

    # group
    groups = _group_by_origin_base(pool)
    origin_to_count = {k: len(v) for k, v in groups.items()}
    # origin_to_doc_type: each origin has one doc_type (어떤 작품이 둘이면 안 됨)
    origin_to_doc_type: dict[str, str] = {}
    for o, items in groups.items():
        origin_to_doc_type[o] = items[0]["doc_type"]

    # shuffle origins per-class (deterministic)
    rng = random.Random(seed)
    train_origins: list[str] = []
    val_origins: list[str] = []
    test_origins: list[str] = []
    for cat in categories:
        cat_origins = sorted([o for o in groups.keys() if origin_to_doc_type[o] == cat])
        if not cat_origins:
            continue
        rng.shuffle(cat_origins)
        # 클래스별 greedy passage-count balance
        cat_to_count = {o: origin_to_count[o] for o in cat_origins}
        tr, va, te = _assign_origins_to_splits(
            cat_origins,
            cat_to_count,
            (train_ratio, val_ratio, test_ratio),
        )
        train_origins.extend(tr)
        val_origins.extend(va)
        test_origins.extend(te)

    # flatten
    train = [e for o in train_origins for e in groups[o]]
    val = [e for o in val_origins for e in groups[o]]
    test = [e for o in test_origins for e in groups[o]]

    # metadata
    metadata = build_metadata(
        train=train, val=val, test=test,
        train_origins=train_origins, val_origins=val_origins, test_origins=test_origins,
        seed=seed,
        ratios={"train": train_ratio, "val": val_ratio, "test": test_ratio},
        categories=list(categories),
    )
    return train, val, test, metadata


def build_metadata(
    *,
    train: list[dict],
    val: list[dict],
    test: list[dict],
    train_origins: list[str],
    val_origins: list[str],
    test_origins: list[str],
    seed: int,
    ratios: dict[str, float],
    categories: list[str],
) -> dict:
    """split_metadata.json schema (directive §4.5)."""

    def class_dist(entries: list[dict]) -> dict[str, int]:
        return dict(Counter(e["doc_type"] for e in entries))

    def year_dist(entries: list[dict]) -> dict[str, int]:
        return dict(Counter(str(e.get("published_year", "")) for e in entries))

    train_set = set(train_origins)
    val_set = set(val_origins)
    test_set = set(test_origins)
    return {
        "schema_version": "split_metadata_v1",
        "created_at_iso": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "ratios": ratios,
        "categories": categories,
        "totals": {
            "train_passages": len(train),
            "val_passages": len(val),
            "test_passages": len(test),
            "train_origins": len(train_origins),
            "val_origins": len(val_origins),
            "test_origins": len(test_origins),
        },
        "class_distribution": {
            "train": class_dist(train),
            "val": class_dist(val),
            "test": class_dist(test),
        },
        "year_distribution": {
            "train": year_dist(train),
            "val": year_dist(val),
            "test": year_dist(test),
        },
        "leakage_check": {
            "origin_overlap_train_val": len(train_set & val_set),
            "origin_overlap_train_test": len(train_set & test_set),
            "origin_overlap_val_test": len(val_set & test_set),
        },
        "passage_length_avg": {
            "train": _avg([e["passage_length"] for e in train]),
            "val": _avg([e["passage_length"] for e in val]),
            "test": _avg([e["passage_length"] for e in test]),
        },
    }


def _avg(nums: list[int]) -> float:
    return round(sum(nums) / max(1, len(nums)), 2)


def write_split(
    output_dir: Path,
    train: list[dict],
    val: list[dict],
    test: list[dict],
    metadata: dict,
) -> None:
    """passage_id 리스트 + metadata 저장.

    raw passage는 *저장하지 않음* (재배포 금지). passage_id로 reproducible.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    def _ids(entries: list[dict]) -> list[str]:
        return [e["passage_id"] for e in entries]

    (output_dir / "train_ids.json").write_text(
        json.dumps(_ids(train), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "val_ids.json").write_text(
        json.dumps(_ids(val), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "test_ids.json").write_text(
        json.dumps(_ids(test), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "split_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--zip-path", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-ratio", type=float, default=0.70)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--test-ratio", type=float, default=0.15)
    parser.add_argument("--categories", nargs="*", default=["fm_drama", "fs_drama"])
    args = parser.parse_args(argv)

    print(f"[split] loading {args.zip_path}", file=sys.stderr)
    raw_iter = stream_aihub_023(args.zip_path, categories=args.categories)
    entries = list(preprocess_stream(raw_iter))
    print(f"[split] preprocessed {len(entries)} entries", file=sys.stderr)

    train, val, test, meta = split_by_origin_base(
        entries,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
        categories=tuple(args.categories),
    )
    write_split(args.output_dir, train, val, test, meta)
    print(f"[split] wrote {args.output_dir}", file=sys.stderr)
    print(json.dumps(meta["totals"], ensure_ascii=False, indent=2))
    print(json.dumps(meta["leakage_check"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
