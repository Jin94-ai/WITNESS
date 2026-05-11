# V3 Reference Distribution Report (Phase G Step G3)

**Generated:** 2026-04-23

**Source:** `data/reference/evaluation_results.json` (45 trajectories)


**Current evaluator thresholds:**
- `reproduction_threshold` = 3.0
- `noise_threshold` = 20.0
- `copy_threshold` = 2.0
- `character_min_composite` = 0.4

---

## 1. Score distribution by category


### character_composite

| category | n | min | q1 | median | q3 | max | mean ± stdev |
|---|---:|---:|---:|---:|---:|---:|---|
| canonical_like | 15 | 0.67 | 0.67 | 0.67 | 0.72 | 0.81 | 0.69 ± 0.05 |
| plausible_alternative | 15 | 0.70 | 0.84 | 0.88 | 0.91 | 0.99 | 0.88 ± 0.07 |
| obvious_noise | 15 | 0.67 | 0.71 | 0.81 | 0.94 | 0.94 | 0.81 ± 0.11 |
| noise_level_1 | 5 | 0.67 | 0.71 | 0.71 | 0.71 | 0.89 | 0.74 ± 0.09 |
| noise_level_2 | 5 | 0.94 | 0.94 | 0.94 | 0.94 | 0.94 | 0.94 ± 0.00 |
| noise_level_3 | 5 | 0.67 | 0.74 | 0.74 | 0.81 | 0.81 | 0.75 ± 0.06 |

### canon_soft_drift

| category | n | min | q1 | median | q3 | max | mean ± stdev |
|---|---:|---:|---:|---:|---:|---:|---|
| canonical_like | 15 | 22.50 | 24.00 | 25.00 | 27.75 | 28.50 | 25.57 ± 2.07 |
| plausible_alternative | 15 | 27.00 | 28.50 | 29.50 | 32.25 | 35.50 | 30.57 ± 2.72 |
| obvious_noise | 15 | 29.00 | 29.00 | 29.00 | 30.00 | 30.00 | 29.33 ± 0.49 |
| noise_level_1 | 5 | 29.00 | 29.00 | 29.00 | 29.00 | 29.00 | 29.00 ± 0.00 |
| noise_level_2 | 5 | 30.00 | 30.00 | 30.00 | 30.00 | 30.00 | 30.00 ± 0.00 |
| noise_level_3 | 5 | 29.00 | 29.00 | 29.00 | 29.00 | 29.00 | 29.00 ± 0.00 |

### causal_smoothness

| category | n | min | q1 | median | q3 | max | mean ± stdev |
|---|---:|---:|---:|---:|---:|---:|---|
| canonical_like | 15 | 0.84 | 0.84 | 0.85 | 0.85 | 0.86 | 0.85 ± 0.01 |
| plausible_alternative | 15 | 0.85 | 0.86 | 0.87 | 0.87 | 0.88 | 0.87 ± 0.01 |
| obvious_noise | 15 | 0.84 | 0.87 | 0.87 | 0.87 | 0.88 | 0.87 ± 0.01 |
| noise_level_1 | 5 | 0.87 | 0.87 | 0.87 | 0.88 | 0.88 | 0.88 ± 0.00 |
| noise_level_2 | 5 | 0.87 | 0.87 | 0.87 | 0.87 | 0.87 | 0.87 ± 0.00 |
| noise_level_3 | 5 | 0.84 | 0.85 | 0.85 | 0.87 | 0.87 | 0.86 ± 0.01 |

### novelty_drift

| category | n | min | q1 | median | q3 | max | mean ± stdev |
|---|---:|---:|---:|---:|---:|---:|---|
| canonical_like | 15 | 22.50 | 24.00 | 25.00 | 27.75 | 28.50 | 25.57 ± 2.07 |
| plausible_alternative | 15 | 27.00 | 28.50 | 29.50 | 32.25 | 35.50 | 30.57 ± 2.72 |
| obvious_noise | 15 | 29.00 | 29.00 | 29.00 | 30.00 | 30.00 | 29.33 ± 0.49 |
| noise_level_1 | 5 | 29.00 | 29.00 | 29.00 | 29.00 | 29.00 | 29.00 ± 0.00 |
| noise_level_2 | 5 | 30.00 | 30.00 | 30.00 | 30.00 | 30.00 | 30.00 ± 0.00 |
| noise_level_3 | 5 | 29.00 | 29.00 | 29.00 | 29.00 | 29.00 | 29.00 ± 0.00 |

## 2. Canon valid + novelty band

| category | n | canon_valid_rate | novelty_band counts |
|---|---:|---:|---|
| canonical_like | 15 | 100% | {'noise': 15} |
| plausible_alternative | 15 | 100% | {'noise': 15} |
| obvious_noise | 15 | 100% | {'noise': 15} |
| noise_level_1 | 5 | 100% | {'noise': 5} |
| noise_level_2 | 5 | 100% | {'noise': 5} |
| noise_level_3 | 5 | 100% | {'noise': 5} |

## 3. Current DiscoveryClass classification (before calibration)


**canonical_like** (n=15): {'not_discovery_noise': 15}

**plausible_alternative** (n=15): {'not_discovery_noise': 15}

**obvious_noise** (n=15): {'not_discovery_noise': 15}

## 4. Category separation analysis


### drift (canon_soft_drift)
- canonical vs alternative: 12% overlap of combined range
- alternative vs noise:     12% overlap of combined range
- canonical vs noise:       NO OVERLAP

### character_composite
- canonical vs alternative: 34% overlap of combined range
- alternative vs noise:     76% overlap of combined range
- canonical vs noise:       51% overlap of combined range

## 5. Current threshold diagnosis

- canonical_like under reproduction_threshold=3.0: 0/15 (0%)
- obvious_noise over noise_threshold=20.0: 15/15 (100%)
- plausible_alternative in [rep_t, noise_t]: 0/15 (0%)

## 6. Calibration targets (G4 input)

Per Phase G spec §4.2:
- `reproduction_threshold = canonical.drift P90`
- `noise_threshold        = obvious_noise.drift P10`
- `character_min_composite = plausible_alternative.character P25`
- `copy_threshold          = canonical.novelty_drift P10`

**Computed targets (preview):**
- reproduction_threshold ← canonical.drift P90 = **28.30**
- noise_threshold        ← obvious_noise.drift P10 = **29.00**
- character_min_composite ← alt.character P25 = **0.843**