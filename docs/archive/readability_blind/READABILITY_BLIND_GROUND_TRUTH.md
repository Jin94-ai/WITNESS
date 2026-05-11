# Readability Blind — GROUND TRUTH (internal)

**Do not share with evaluator until post-eval.**

| probe_id | scenario | seed | variant | config |
|---|---|---|---|---|
| P1 | scarcity | 0 | sham_mul_0.8 | p2a=True sham_mul=0.8 |
| P2 | scarcity | 2 | baseline | p2a=True sham_mul=None |
| P3 | accusation | 0 | p2a_off | p2a=False sham_mul=None |
| P4 | sacred | 0 | baseline | p2a=True sham_mul=None |
| P5 | sacred | 1 | baseline | p2a=True sham_mul=None |
| P6 | scarcity | 0 | p2a_off | p2a=False sham_mul=None |
| P7 | sacred | 0 | sham_mul_0.05 | p2a=True sham_mul=0.05 |
| P8 | accusation | 0 | sham_mul_0.8 | p2a=True sham_mul=0.8 |
| P9 | scarcity | 0 | baseline | p2a=True sham_mul=None |
| P10 | accusation | 0 | baseline | p2a=True sham_mul=None |
| P11 | accusation | 3 | baseline | p2a=True sham_mul=None |
| P12 | sacred | 0 | p2a_off | p2a=False sham_mul=None |

---

## v2.1/v3 detection accuracy (2026-04-28 autonomous LOOP 32-34)

| probe_id | GT scenario | v2.1 Primary pressure | Match | v2 Failure mode | v3 Public susp. peak | v3 Authority vig. peak |
|---|---|---|---|---|---:|---:|
| P1 | scarcity | scarcity | ✓ | — | 0.24 | 0.25 |
| P2 | scarcity | scarcity | ✓ | shame_cap | 0.24 | 0.25 |
| P3 | accusation | accusation | ✓ | shame_cap | 0.22 | negligible |
| P4 | sacred | sacred | ✓ | — | 0.06 | negligible |
| P5 | sacred | sacred | ✓ | — | 0.06 | negligible |
| P6 | scarcity | scarcity | ✓ | — | 0.43 | 0.25 |
| P7 | sacred | sacred | ✓ | — | 0.08 | negligible |
| P8 | accusation | accusation | ✓ | — | 0.22 | negligible |
| P9 | scarcity | scarcity | ✓ | shame_cap | 0.24 | 0.25 |
| P10 | accusation | accusation | ✓ | — | 0.22 | negligible |
| P11 | accusation | accusation | ✓ | — | 0.18 | negligible |
| P12 | sacred | sacred | ✓ | shame_cap | 0.39 | negligible |

**Aggregate**: Primary pressure 12/12 = 100%. Authority vigilance non-zero ONLY in scarcity scenarios (4/4) — `guard_approaches` accumulates. Public suspicion correlates with cohort saturation severity.