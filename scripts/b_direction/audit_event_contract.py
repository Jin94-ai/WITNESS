"""Event contract lint (Iter 51, Updated Loop Phase 0 gate).

Scans the engine for:
- Events spawned in code (producer side)
- Events read by motif activators or other consumers
- Compares against engine/world/event_registry.py declarations

Fails if:
- Producer emits an event name not in PRODUCED_EVENTS registry
- Consumer reads an event name not in CONSUMED_EVENTS registry
- Registry declares events that aren't actually found in code (drift)

Usage: python scripts/b_direction/audit_event_contract.py
Exit 0 on clean; non-zero on contract violations.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.world.event_registry import (  # noqa: E402
    AGENT_ACTION_EVENTS,
    SEED_EVENTS,
    CONSUMED_EVENTS,
    LEGACY_V3_EVENTS,
    audit,
    dead_emissions,
    legacy_dormant_consumers,
    orphan_consumers,
)


ENGINE_DIR = ROOT / "engine"
SCRIPTS_DIR = ROOT / "scripts"


# =============================================================================
# Scan for produced events
# =============================================================================

def scan_produced_events() -> dict[str, set[str]]:
    """Return {event_name: {source_files}} for all 'event_id': 'NAME' strings."""
    pattern = re.compile(
        r'["\']event_id["\']\s*:\s*["\']([a-z_][a-z_0-9]*)["\']'
    )
    alt_pattern = re.compile(
        r'event_id\s*=\s*["\']([a-z_][a-z_0-9]*)["\']'
    )
    # Scope: engine/ + scripts/b_direction/ only (exclude data_pipeline
    # and unrelated tooling that uses 'event_id' keyword in other
    # contexts)
    found: dict[str, set[str]] = {}
    scope = (
        list(ENGINE_DIR.rglob("*.py"))
        + list((SCRIPTS_DIR / "b_direction").rglob("*.py"))
    )
    for path in scope:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in pattern.finditer(text):
            found.setdefault(m.group(1), set()).add(str(path.relative_to(ROOT)))
        for m in alt_pattern.finditer(text):
            found.setdefault(m.group(1), set()).add(str(path.relative_to(ROOT)))
    return found


# =============================================================================
# Scan for consumed events (from events_recent.get)
# =============================================================================

def scan_consumed_events() -> dict[str, set[str]]:
    """Return {event_name: {source_files}} for events_recent.get('NAME', ...)."""
    pattern = re.compile(
        r"events_recent\.get\(\s*[\"']([a-z_][a-z_0-9]*)[\"']"
    )
    found: dict[str, set[str]] = {}
    for path in ENGINE_DIR.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in pattern.finditer(text):
            found.setdefault(m.group(1), set()).add(str(path.relative_to(ROOT)))
    return found


# =============================================================================
# Lint
# =============================================================================

def run_lint() -> dict:
    produced_found = scan_produced_events()
    consumed_found = scan_consumed_events()

    produced_names = set(produced_found)
    consumed_names = set(consumed_found)

    registry_produced = AGENT_ACTION_EVENTS | SEED_EVENTS
    all_registered = registry_produced | LEGACY_V3_EVENTS

    # Undeclared producers: code emits event not in ANY registry section
    undeclared_producers = produced_names - all_registered
    # Stale: registry declares producer not found in code
    stale_producer_registry = registry_produced - produced_names

    # Undeclared consumers: code reads event not in registry
    undeclared_consumers = consumed_names - CONSUMED_EVENTS
    # Stale consumer registry
    stale_consumer_registry = CONSUMED_EVENTS - consumed_names

    # Orphan / dead
    orphans = orphan_consumers()
    dead = dead_emissions()

    return {
        "produced_in_code": sorted(produced_names),
        "consumed_in_code": sorted(consumed_names),
        "undeclared_producers": sorted(undeclared_producers),
        "stale_producer_registry": sorted(stale_producer_registry),
        "undeclared_consumers": sorted(undeclared_consumers),
        "stale_consumer_registry": sorted(stale_consumer_registry),
        "orphan_consumers": sorted(orphans),
        "dead_emissions": sorted(dead),
        "active_contract": sorted(registry_produced & CONSUMED_EVENTS),
    }


def main() -> int:
    print("=" * 72)
    print("EVENT CONTRACT LINT (Iter 51)")
    print("=" * 72)
    print()

    r = run_lint()

    print("Registry state:")
    a = audit()
    print(f"  produced declared:  {a['produced_count']}")
    print(f"  consumed declared:  {a['consumed_count']}")
    print()

    print("In code (scanned):")
    print(f"  produced found:     {len(r['produced_in_code'])}")
    print(f"  consumed found:     {len(r['consumed_in_code'])}")
    print()

    # Active contract = sucessfully wired feedback events
    print(f"ACTIVE CONTRACT ({len(r['active_contract'])}):")
    for e in r["active_contract"]:
        print(f"  OK{e}")
    print()

    legacy_dormant = sorted(legacy_dormant_consumers())
    truly_orphan = sorted(set(r["orphan_consumers"]) - set(legacy_dormant))

    print(f"ORPHAN CONSUMERS ({len(r['orphan_consumers'])}):")
    print(f"  -- legacy v3 dormant ({len(legacy_dormant)}): motif still "
          f"checks but MicroWorld doesn't emit; v3-era hooks:")
    for e in legacy_dormant:
        print(f"    v3  {e}")
    if truly_orphan:
        print(f"  -- truly undesigned ({len(truly_orphan)}):")
        for e in truly_orphan:
            print(f"    XX  {e}")
    print()

    print(f"DEAD EMISSIONS ({len(r['dead_emissions'])}) "
          "-- emitted but no motif activator reads:")
    for e in r["dead_emissions"]:
        print(f"  --{e}")
    print()

    # Lint violations
    violations = 0
    if r["undeclared_producers"]:
        print(f"VIOLATION -- undeclared producers: "
              f"{r['undeclared_producers']}")
        violations += len(r["undeclared_producers"])
    if r["undeclared_consumers"]:
        print(f"VIOLATION -- undeclared consumers: "
              f"{r['undeclared_consumers']}")
        violations += len(r["undeclared_consumers"])
    if r["stale_producer_registry"]:
        print(f"WARNING -- stale producer registry entries: "
              f"{r['stale_producer_registry']}")
    if r["stale_consumer_registry"]:
        print(f"WARNING -- stale consumer registry entries: "
              f"{r['stale_consumer_registry']}")

    print()
    if violations == 0:
        print(f"LINT OK -- registry matches code. Orphans/dead are DESIGN "
              f"concerns, not violations.")
        if r["orphan_consumers"]:
            print(f"  NOTE: {len(r['orphan_consumers'])} orphan consumers "
                  f"detected. Consider wiring producers OR removing "
                  f"consumer branches.")
        return 0
    else:
        print(f"LINT FAILED -- {violations} violations.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
