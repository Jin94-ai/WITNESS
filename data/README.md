# `data/` — Generated experimental artifacts

This folder is **gitignored** except for this README. It holds artifacts generated
by scripts — reproducible so we don't version them.

## Contents

- `person/abc_snapshots/` — pyABC calibration `.db` snapshots
- `person/pipeline_v1/` — BC training arrays (`X.npy`, `y.npy`, `meta.json`)
- `person/trajectory_*.jsonl` — Run-level trajectory datasets
- `person/fear_love_heatmap.npz` — Sensitivity analysis output
- `world/` — World engine generated outputs

## Regenerating

```bash
# Trajectory datasets
python scripts/generate_trajectories.py

# ABC calibration
python scripts/run_abc_calibration.py

# BC training data
python scripts/build_bc_training_data.py
```

See `scripts/` for the full set.
