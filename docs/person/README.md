# docs/person/ — Person Engine (v0.5–v1.2) records

Artifacts produced by the Person Engine (`engine/` code path).
Kept separate from World Engine records ([../world/](../world/)).

## Contents

- **[paper_data/](paper_data/)** — numerical & figure artifacts:
  - `paper_numbers.json` — single canonical source for paper numbers
    (Peter standalone, phased, Van Gogh, Talleyrand, cross-scenario POM,
    separability spectrum, counterfactual, hazard scaling).
  - `baseline_comparison.{json,txt}` — 4 baseline ablations + 5-level hierarchy.
  - `causal_counterfactual.{json,txt}` — V3 trigger-arrest counterfactual.
  - `hazard_scaling.{json,txt}` — hazard-rate scaling sweep.
  - `svm_comparison.{json,txt}` — LDA vs RBF-SVM on Peter + VG features.
  - `fig_*.png` — paper figures.

## Source scripts

Re-generating everything (`scripts/` at repo root):

```bash
python scripts/paper_numbers.py
python scripts/paper_figures.py
python scripts/baseline_comparison.py && python scripts/baseline_figures.py
python scripts/counterfactual_baseline.py && python scripts/hazard_scaling.py && python scripts/counterfactual_figures.py
python scripts/svm_comparison.py
```

Runtime data (trajectory datasets, ABC calibration DBs, culture/geography
content) lives in [../../data/person/](../../data/person/).
