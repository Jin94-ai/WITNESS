"""Episode synopsis schema (Phase 1).

Per `docs/data/SELECTION_CRITERIA.md` §3, each episode synopsis is stored
as a single JSON file at:
    data/raw/{category}/{title_id}/episodes/{episode_no:02d}.json

This module defines the schema, a writer that enforces it, and validators
that the test suite can use to keep raw data well-formed.

NOTE: This module never *fetches* data from the internet. Network IO lives
in `scripts/data/collect_synopsis.py` only.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "synopsis_v1"
ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Selection log
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SelectionEntry:
    """One candidate work in `data/raw/{cat}/_selection_log.json#candidates`.

    Per SELECTION_CRITERIA §2.3.
    """
    title_id: str                 # stable id: snake_case, ascii only
    title_ko: str                 # 한국어 작품명
    title_en: str                 # romanized
    year_start: int
    year_end: int
    channel: str
    episodes_total: int
    category: str                 # "melodrama" | "control"
    category_evidence: list[dict] = field(default_factory=list)
    synopsis_source: str = ""     # "wiki_link" | "official_site" | "epg"
    synopsis_license: str = ""    # SPDX-style or text
    selected: bool = True
    rejection_reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Episode synopsis
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EpisodeSynopsis:
    """One episode of a serialized work."""
    title_id: str
    title_ko: str
    title_en: str
    category: str                 # "melodrama" | "control"
    episode_no: int
    synopsis_text_ko: str         # 회차 줄거리 — 사실 정보만
    source_url: str
    source_license: str
    fetched_at_iso: str           # ISO-8601 UTC
    fetcher_version: str = "synopsis_v1_placeholder"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            **asdict(self),
        }


def now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------

def episode_path(title_id: str, category: str, episode_no: int) -> Path:
    """Resolve the on-disk path for a given episode."""
    return (
        ROOT / "data" / "raw" / category / title_id /
        "episodes" / f"{episode_no:02d}.json"
    )


def write_episode(synopsis: EpisodeSynopsis) -> Path:
    """Write a synopsis to disk in the canonical layout. Returns the path."""
    p = episode_path(synopsis.title_id, synopsis.category, synopsis.episode_no)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(synopsis.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return p


def load_episode(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Validators (used by tests)
# ---------------------------------------------------------------------------

REQUIRED_EPISODE_FIELDS = (
    "schema_version", "title_id", "title_ko", "title_en", "category",
    "episode_no", "synopsis_text_ko", "source_url", "source_license",
    "fetched_at_iso",
)


def validate_episode_dict(d: dict) -> list[str]:
    """Return a list of error messages (empty list == valid)."""
    errs: list[str] = []
    for f in REQUIRED_EPISODE_FIELDS:
        if f not in d:
            errs.append(f"missing field: {f}")
    if d.get("schema_version") and d["schema_version"] != SCHEMA_VERSION:
        errs.append(
            f"schema_version mismatch: got {d['schema_version']!r}, expected {SCHEMA_VERSION!r}"
        )
    if d.get("category") not in ("melodrama", "control"):
        errs.append(
            f"category must be 'melodrama' or 'control', got: {d.get('category')!r}"
        )
    return errs
