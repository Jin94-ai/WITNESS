# Branch C - Cross-Seed Ensemble Results (S2/S3/S4/S5)

**Date:** 2026-04-28
**Source:** LOOP 75-76 cross-seed re-tests of all 4 within-scenario slices.
**Scope:** 4 slices x 9 cells x 5 seeds = 180 runs (S5 already done LOOP 75).

## 1. Per-slice cross-seed sensitivity

| Slice | Cells | Cross-seed flips | Cross-seed ratio | Seed=0 ratio | Delta |
|---|---:|---:|---:|---:|---:|
| S5 placement | 9 | 4 | 44.4% | 67% | -22.6pp |
| S4 cast | 9 | 5 | 55.6% | 67% | -11.4pp |
| S3 event_density | 9 | 4 | 44.4% | 22% | +22.4pp |
| S2 scarcity_depth | 9 | 1 | 11.1% | 44% | -32.9pp |

**Mean cross-seed sensitivity**: 38.9% (vs seed=0-only mean: 50.0%, delta -11.1pp).

## 2. Within-cell variance

S5: 2/9 cells unanimous (LOOP 75)
S4: 0/9 cells unanimous
S3: 4/9 cells unanimous
S2: 0/9 cells unanimous

## 3. Implication

Branch C 1차 evidence v3-v4.2 sensitivity claims overstated by ~20pp due to seed=0
conditioning. Cross-seed ensemble is the true measure. Configuration sensitivity
**is real but weaker** than original claim.

The qualitative finding (cast/placement > event_density) survives — relative ranking
of slices is preserved — but absolute magnitudes need ~20pp reduction.

## 4. Per-cell modal outcomes

### S4

| Cell | s0 | s1 | s2 | s3 | s4 | Modal |
|---|---|---|---|---|---|---|
| ('accusation', 'full') | MIXED | MIXED | SATURA | RECOVE | RECOVE | MIXED (2/5) |
| ('accusation', 'no_authority') | RECOVE | PARTIA | SATURA | SATURA | SATURA | SATURATION_DOMINATED (3/5) |
| ('accusation', 'no_outsider') | MIXED | MIXED | MIXED | SATURA | SATURA | MIXED (3/5) |
| ('scarcity', 'full') | SATURA | SATURA | SATURA | RECOVE | SATURA | SATURATION_DOMINATED (4/5) |
| ('scarcity', 'no_authority') | RECOVE | SATURA | SATURA | RECOVE | RECOVE | RECOVERY_DOMINATED (3/5) |
| ('scarcity', 'no_outsider') | RECOVE | SATURA | RECOVE | SATURA | PARTIA | RECOVERY_DOMINATED (2/5) |
| ('sacred', 'full') | PARTIA | PARTIA | PARTIA | RECOVE | RECOVE | PARTIAL (3/5) |
| ('sacred', 'no_authority') | RECOVE | RECOVE | PARTIA | MIXED | RECOVE | RECOVERY_DOMINATED (3/5) |
| ('sacred', 'no_outsider') | RECOVE | RECOVE | RECOVE | PARTIA | PARTIA | RECOVERY_DOMINATED (3/5) |

### S3

| Cell | s0 | s1 | s2 | s3 | s4 | Modal |
|---|---|---|---|---|---|---|
| ('low', 'early') | RECOVE | RECOVE | RECOVE | SATURA | RECOVE | RECOVERY_DOMINATED (4/5) |
| ('low', 'even') | PARTIA | PARTIA | RECOVE | RECOVE | PARTIA | PARTIAL (3/5) |
| ('low', 'late') | RECOVE | RECOVE | RECOVE | RECOVE | SATURA | RECOVERY_DOMINATED (4/5) |
| ('med', 'early') | RECOVE | RECOVE | RECOVE | RECOVE | PARTIA | RECOVERY_DOMINATED (4/5) |
| ('med', 'even') | PARTIA | PARTIA | PARTIA | PARTIA | PARTIA | PARTIAL (5/5) |
| ('med', 'late') | RECOVE | RECOVE | RECOVE | RECOVE | RECOVE | RECOVERY_DOMINATED (5/5) |
| ('high', 'early') | PARTIA | PARTIA | PARTIA | PARTIA | PARTIA | PARTIAL (5/5) |
| ('high', 'even') | PARTIA | PARTIA | PARTIA | RECOVE | PARTIA | PARTIAL (4/5) |
| ('high', 'late') | PARTIA | PARTIA | PARTIA | PARTIA | PARTIA | PARTIAL (5/5) |

### S2

| Cell | s0 | s1 | s2 | s3 | s4 | Modal |
|---|---|---|---|---|---|---|
| ('single', 'low') | RECOVE | RECOVE | SATURA | RECOVE | RECOVE | RECOVERY_DOMINATED (4/5) |
| ('single', 'baseline') | SATURA | RECOVE | SATURA | PARTIA | RECOVE | SATURATION_DOMINATED (2/5) |
| ('single', 'high') | SATURA | RECOVE | SATURA | PARTIA | RECOVE | SATURATION_DOMINATED (2/5) |
| ('double', 'low') | SATURA | RECOVE | SATURA | PARTIA | RECOVE | SATURATION_DOMINATED (2/5) |
| ('double', 'baseline') | SATURA | RECOVE | SATURA | SATURA | RECOVE | SATURATION_DOMINATED (3/5) |
| ('double', 'high') | SATURA | RECOVE | SATURA | SATURA | RECOVE | SATURATION_DOMINATED (3/5) |
| ('triple', 'low') | RECOVE | RECOVE | SATURA | RECOVE | RECOVE | RECOVERY_DOMINATED (4/5) |
| ('triple', 'baseline') | RECOVE | RECOVE | SATURA | SATURA | RECOVE | RECOVERY_DOMINATED (3/5) |
| ('triple', 'high') | RECOVE | RECOVE | SATURA | SATURA | RECOVE | RECOVERY_DOMINATED (3/5) |
