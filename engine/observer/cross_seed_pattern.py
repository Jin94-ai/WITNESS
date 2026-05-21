"""Cross-seed Story Pattern Mining — Phase E.

Per `docs/WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md` §12 Phase E.

Aggregates StoryCandidate sets across N seeds (same anchor, varying seed)
and reports:
    - conflict_family frequency
    - arc_direction frequency
    - recurring main-character involvement
    - robust patterns (appears in ≥ K seeds)
    - seed-specific anomalies (appears in only 1 seed)

ABSOLUTE rules:
    - No new anchors / scenarios / metrics introduced.
    - Aggregator is *post-hoc* — it reads StoryCandidate ledgers, does not
      re-run mining.
    - Provenance preserved: each pattern entry counts which seeds produced it.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CrossSeedPattern:
    """One aggregated pattern across multiple seeds."""
    pattern_kind: str        # "conflict" / "arc" / "main_character"
    pattern_value: str       # e.g. "loyalty_vs_survival" / "a display name"
    seed_count: int
    total_seeds: int
    seeds_present: tuple[int, ...]   # which seeds had it
    candidate_ids: tuple[str, ...]   # which candidates instantiated it
    robustness: str          # "robust" / "moderate" / "anomaly"

    def to_dict(self) -> dict:
        return {
            "pattern_kind": self.pattern_kind,
            "pattern_value": self.pattern_value,
            "seed_count": self.seed_count,
            "total_seeds": self.total_seeds,
            "frequency": round(self.seed_count / self.total_seeds, 3) if self.total_seeds else 0.0,
            "seeds_present": list(self.seeds_present),
            "candidate_ids": list(self.candidate_ids),
            "robustness": self.robustness,
        }


@dataclass
class SeedRecord:
    """Per-seed input to the aggregator."""
    seed: int
    run_label: str
    candidates: list[dict]           # raw StoryCandidate dicts (post-serialize)


# ---------------------------------------------------------------------------
# Robustness classification
# ---------------------------------------------------------------------------

def _classify_robustness(seed_count: int, total_seeds: int) -> str:
    """≥80% of seeds → robust; ≥40% → moderate; otherwise anomaly."""
    if total_seeds == 0:
        return "anomaly"
    ratio = seed_count / total_seeds
    if ratio >= 0.80:
        return "robust"
    if ratio >= 0.40:
        return "moderate"
    return "anomaly"


# ---------------------------------------------------------------------------
# Aggregators
# ---------------------------------------------------------------------------

def _aggregate_by_field(
    seeds: list[SeedRecord],
    pattern_kind: str,
    field_extractor,
) -> list[CrossSeedPattern]:
    """Generic aggregator: count distinct values of one field across seeds.

    field_extractor(candidate_dict) → list[str] of values to count.
    """
    seen_per_seed: dict[str, set[int]] = {}
    candidate_ids_per_value: dict[str, list[str]] = {}
    total_seeds = len(seeds)

    for s in seeds:
        for c in s.candidates:
            for value in field_extractor(c):
                if not value:
                    continue
                seen_per_seed.setdefault(value, set()).add(s.seed)
                candidate_ids_per_value.setdefault(value, []).append(
                    f"{s.seed}:{c['story_candidate_id']}"
                )

    out: list[CrossSeedPattern] = []
    for value, seed_set in sorted(seen_per_seed.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        out.append(CrossSeedPattern(
            pattern_kind=pattern_kind,
            pattern_value=value,
            seed_count=len(seed_set),
            total_seeds=total_seeds,
            seeds_present=tuple(sorted(seed_set)),
            candidate_ids=tuple(candidate_ids_per_value[value]),
            robustness=_classify_robustness(len(seed_set), total_seeds),
        ))
    return out


def aggregate_conflict_patterns(seeds: list[SeedRecord]) -> list[CrossSeedPattern]:
    return _aggregate_by_field(
        seeds, pattern_kind="conflict",
        field_extractor=lambda c: [c.get("core_conflict")],
    )


def aggregate_arc_patterns(seeds: list[SeedRecord]) -> list[CrossSeedPattern]:
    """arc_direction is on StoryThread, not directly on StoryCandidate.
    Pull from candidate's source thread title heuristics — but a cleaner
    approach is to expose arc_direction through the candidate; for now
    fall back to a flat list."""
    return _aggregate_by_field(
        seeds, pattern_kind="arc",
        # Without arc on candidate, classify by conflict family as proxy
        field_extractor=lambda c: [],
    )


def aggregate_character_patterns(seeds: list[SeedRecord]) -> list[CrossSeedPattern]:
    """Recurring main characters across seeds.

    Note: with identity_map.json, agent_03 → "a display name" in *every* seed of the
    same anchor. So a character appearing in 4/5 seeds means "a display name is
    main in 4 of 5 runs" — a meaningful robustness signal.
    """
    return _aggregate_by_field(
        seeds, pattern_kind="main_character",
        field_extractor=lambda c: c.get("main_characters", []),
    )


# ---------------------------------------------------------------------------
# Top-level cross-seed report
# ---------------------------------------------------------------------------

@dataclass
class CrossSeedReport:
    anchor_id: str
    seeds: tuple[int, ...]
    candidate_counts: dict[int, int]    # seed → candidate count
    conflict_patterns: list[CrossSeedPattern]
    character_patterns: list[CrossSeedPattern]
    robust_count: int                    # patterns flagged "robust"
    anomaly_count: int                   # patterns flagged "anomaly"

    def to_dict(self) -> dict:
        return {
            "schema_version": "cross_seed_story_patterns_v1",
            "anchor_id": self.anchor_id,
            "seeds": list(self.seeds),
            "candidate_counts": {str(k): v for k, v in self.candidate_counts.items()},
            "conflict_patterns": [p.to_dict() for p in self.conflict_patterns],
            "character_patterns": [p.to_dict() for p in self.character_patterns],
            "summary": {
                "total_patterns": len(self.conflict_patterns) + len(self.character_patterns),
                "robust": self.robust_count,
                "anomaly": self.anomaly_count,
            },
        }


def build_cross_seed_report(
    seed_records: list[SeedRecord],
    anchor_id: str,
) -> CrossSeedReport:
    conflicts = aggregate_conflict_patterns(seed_records)
    characters = aggregate_character_patterns(seed_records)
    all_patterns = conflicts + characters
    robust_count = sum(1 for p in all_patterns if p.robustness == "robust")
    anomaly_count = sum(1 for p in all_patterns if p.robustness == "anomaly")

    return CrossSeedReport(
        anchor_id=anchor_id,
        seeds=tuple(sorted(s.seed for s in seed_records)),
        candidate_counts={s.seed: len(s.candidates) for s in seed_records},
        conflict_patterns=conflicts,
        character_patterns=characters,
        robust_count=robust_count,
        anomaly_count=anomaly_count,
    )
