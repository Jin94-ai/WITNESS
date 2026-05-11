# Annotated v4 — Top Blame Target Field Findings

**Date:** 2026-04-28
**Scope:** 12 baseline + 9 S5 + 9 S4 = 30 probes
**Status:** v4 spec implemented + validated (30/30 PASS via `validate_annotated_v4.py`)
**Driver:** GPT FILLED §6 N=12 result — Q3b interpersonal axis surfaces only "partial". v4 adds explicit field to close that gap.

---

## 1. v4 spec addition

**New field:** `Top blame target:    <role_id> (peak <X.XX>)`

**Rendering rules:**
- Peak `≥ 0.30` → `<role_id> (peak X.XX)` — strong indicator
- `0.05 ≤ peak < 0.30` → `<role_id> (peak X.XX, weak)` — weak indicator
- Peak `< 0.05` → `none (peak < 0.05)` — no concentration

**Source:** Per-tick aggregation of `c.blame_concentration[target]` across all `_crowds`. Take per-target peak across N_TICKS, surface argmax.

**Surfacing logic (generator-only, engine untouched):**
```python
target_peaks = defaultdict(float)
for tick_dict in blame_per_target_per_tick:
    for target, val in tick_dict.items():
        if val > target_peaks[target]:
            target_peaks[target] = val
top_target = max(target_peaks.items(), key=lambda kv: kv[1])
```

---

## 2. Distribution across 30 probes

### 2.1 By scenario (Q2a inferred)

| Scenario | N | Modal target | Modal share | Variants |
|---|---|---|---|---|
| accusation | 11 | crowd_participant | 9/11 (82%) | 2 alt (P_PV_02 soldier_enforcer, P_PV_03 disciple_follower) |
| scarcity   | 9  | fisher_laborer    | 9/9 (100%) | none |
| sacred     | 10 | disciple_follower | 7/10 (70%) | 3 alt (P_PV_08 crowd_participant, P_PV_09 + P_CV_09 spiritual_wanderer) |

**Key observation:** scarcity is 100% deterministic on `fisher_laborer` regardless of placement/cast. Accusation and sacred have placement/cast-driven variability.

### 2.2 By peak strength

| Range | Count | Probes |
|---|---|---|
| Strong (peak ≥ 0.3)  | 27/30 | most |
| Weak (0.05 ≤ peak < 0.3) | 3/30  | P5, P_PV_09, P_CV_09 |
| None (peak < 0.05) | 0/30 | (none) |

→ Top blame field is non-negligible in every probe. Q3b interpersonal axis can be surfaced for **every** probe, eliminating "1/5 axes" baseline gap.

---

## 3. Configuration sensitivity (vs final-summary outcome)

### 3.1 accusation: 11 probes, 4 distinct top targets surfaced via config

| Config dim | top_blame_target shifts | Final summary shifts |
|---|---|---|
| Placement (S5) | original=crowd, inverted=soldier, clustered=disciple | RECOVERY → SATURATION → RECOVERY |
| Cast (S4)     | full/no_authority/no_outsider all = crowd_participant | MIXED → RECOVERY → MIXED |

→ Placement variation drives top_blame_target shift in accusation (3 distinct targets across 3 placements). Cast variation does not (crowd_participant invariant under cast drops).

### 3.2 scarcity: 9 probes, 1 invariant target

`fisher_laborer` is dominant under all 6 config variants — placement and cast both irrelevant to **who** is blamed, but final-summary outcome still varies (PARTIAL / SATURATION / RECOVERY / MIXED). Implication: scarcity dynamics differ in **intensity** of fisher_laborer blame, not **identity** of target. (Inspect peak values: scarcity peaks consistently 0.74-1.29.)

### 3.3 sacred: 10 probes, 3 distinct top targets

| Config | target shifts |
|---|---|
| Placement | original=disciple, inverted=crowd_participant, clustered=spiritual_wanderer (weak) |
| Cast      | full=disciple, no_authority=disciple, no_outsider=spiritual_wanderer (weak) |

→ Sacred + outsider absence shifts target to spiritual_wanderer (weak) — meaning blame flattens when the prime accusation candidate (outsider role) is removed.

---

## 4. Implication for GPT-5.5 blind eval

GPT-5.5 (per blind eval package §3 / §4) will see `Top blame target:    crowd_participant (peak 1.00)` in 9-10 of 18 new probes and `fisher_laborer (peak 1.00)` in 6 of 18 — explicit handle for Q3b "interpersonal" axis. Expected lift on Q3b world-side selection: **partial → +interpersonal explicit**, addressing GPT FILLED §6 measured gap.

→ GPT-5.5 §4 aggregate question "Q3b interpersonal: N" is now answerable from headline alone, no trace inference needed.

---

## 5. What v4 did NOT change (for HARNESS H4)

- Engine code untouched (Rule #6 compliant — `engine/` is read-only at generator layer)
- Final summary labels unchanged (still 5: LOW_ACTIVITY / RECOVERY / SATURATION / MIXED / PARTIAL)
- Primary pressure logic unchanged (still 9 options per v2)
- All 12 baseline final summaries match GT (12/12)
- All 18 new probe final summaries match BLIND_PACKAGE §6 GT (18/18)

## 6. What could still be wrong (HARNESS H4 — Negative Findings)

- **Trivial explanation:** "crowd_participant peaks at 1.00 in 9/11 accusation probes" might just reflect that `disciple_follower` accusation events route blame to crowd through engine's blame_concentration coupling — i.e., the field measures engine routing, not emergent dynamics. **Falsification:** if scarcity and accusation produced different top_blame_role despite different events, that's emergent. Currently scarcity uses `merchant`-targeted public_accusation but top blame still goes to `fisher_laborer` — this is non-trivial and **rejects** the trivial routing-only hypothesis. ✓
- **What I did NOT try:** (a) run baseline 12 with other seeds (only seed=0); (b) check whether `crowd_participant` is just the role_id of crowd-state aggregator and not a "real" blamed role — would require engine-side audit; (c) compare top_blame_target peak vs total crowd blame to check if it's >50% of total or just argmax of low values.
- **Alternate interpretation:** "fisher_laborer 100% in scarcity" might mean the scarcity scene's role assignment makes fisher_laborer the demographic majority, so any uniform blame distribution would show fisher_laborer as argmax. Would need to check scarcity cast composition.

---

## 7. Files modified (LOOP 64)

- `scripts/b_direction/generate_annotated_probes_all.py` — v3 → v4
- `scripts/b_direction/generate_placement_variations.py` — v3 → v4
- `scripts/b_direction/generate_cast_variations.py` — v3 → v4
- `scripts/b_direction/validate_annotated_v4.py` — new (replaces validate_annotated_v3.py for forward use)
- 12 baseline P*_ANNOTATED.txt — regenerated v4
- 9 S5 P_PV_*.txt — regenerated v4
- 9 S4 P_CV_*.txt — regenerated v4

**Validation:** `PYTHONHASHSEED=0 python scripts/b_direction/validate_annotated_v4.py` → PASS (30/30).
