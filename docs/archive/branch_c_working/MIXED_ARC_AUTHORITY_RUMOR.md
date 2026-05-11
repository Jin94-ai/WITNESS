# Mixed-Arc Reinforcement — authority + rumor probe

**Iter 90 / Priority 6 of WORLD_BUILDING**
**Date:** 2026-04-25

---

## 1. Hypothesis

Layering 2 known-coupled pressure families (authority via guard_approaches
+ rumor via multiple seeds) — does it produce richer dynamics than
single-pressure baseline, or single-loop collapse?

---

## 2. Setup

4 conditions × 5 seeds × 200 ticks (PYHASH=0):
- **A baseline**: standard accusation (Iter 66)
- **B heavy authority**: A + 3 guard_approaches at varied locations/times
- **C heavy rumor**: A + 2 extra seed rumors (misdeed against outsider, secret about priest)
- **D mixed**: B + C combined

---

## 3. Result — single-loop collapse confirmed

### 3.1 Cycle metrics (essentially identical)

| Condition | rev/agent | final shame | confess/s | top motif (remain_present) |
|---|---:|---:|---:|---:|
| A baseline | 3.73 | 5.36 | 33.4 | 0.528 |
| B heavy authority | 3.80 | 4.56 | 37.0 | 0.524 |
| C heavy rumor | 3.90 | 4.29 | 36.2 | 0.518 |
| **D mixed** | **3.70** | **5.15** | **33.4** | **0.527** |

All within noise floor (Iter 70: 0.388 rev/agent stdev). Final shame
varies 4.29-5.36 but no clear pattern — D is between B and C, not
beyond either.

### 3.2 Motif distribution (nearly identical across conditions)

| Motif | A | B | C | D |
|---|---:|---:|---:|---:|
| remain_present | 0.528 | 0.524 | 0.518 | 0.527 |
| conceal | 0.192 | 0.183 | 0.203 | 0.196 |
| observe_wait | 0.086 | 0.088 | 0.084 | 0.080 |
| withdraw | 0.081 | 0.083 | 0.078 | 0.081 |
| confess | 0.072 | 0.079 | 0.071 | 0.068 |

**Motif drift D vs A (threshold > 1%): NONE.**

Top-motif entropy: A=1.270, B=1.284, C=1.273, D=1.259. Differences
within noise.

### 3.3 public_suspicion saturated everywhere

`public_suspicion_peak_mean` = **1.0 in ALL conditions**.

Even baseline A reaches the public_suspicion ceiling. Adding heavy
authority/rumor cannot differentiate because already saturated.
This is a tuning issue — the +0.2/+0.3 generation rates per event
are too high relative to 0.02/tick decay. Single accusation event
saturates the field.

---

## 4. Verdict

**Scale-8 Mixed-Arc Richness Score: 0-1**

Per WORLD_BUILDING §3.8 scale:
- 0: 하나만 강함
- 1: mixed probe 일부 가능
- 2: 혼합 조건에서 새로운 arc family
- 3: mixed arc readable + general

This probe scores **0-1** — heavy authority + heavy rumor mixing
collapses to baseline dynamics. No new arc family emerges.

### 4.1 Compared to Step E findings

Step E covered:
- accusation+sacred (null per Iter 77 — sacred decoupled)
- scarcity+grief (real mixed dynamics — guilt+grief injection IS coupled)

Iter 90 authority+rumor: **also null at cycle level**, but for a
different reason than acc+sacred. Both authority and rumor channels
already feed into the same Phase 2a recovery loop via shame_climate
+ blame_concentration. They don't add orthogonal pressure.

### 4.2 Mechanism: which mixings work?

Pattern emerging from Step E + Iter 90 probes:

| Mixing | Result | Why |
|---|---|---|
| acc + sacred | null | sacred state architecturally decoupled (Iter 77/78) |
| scar + grief | RICH | guilt+grief injection bypasses motif gates, drives grieve motif distinct from accusation cycle |
| authority + rumor | null (Iter 90) | both feed same shame_climate/blame channels, Phase 2a unifies |

**Working mixing requires**: orthogonal motif activation (e.g., grief
→ grieve motif) NOT a different upstream pressure that converges to
same downstream loop.

---

## 5. public_suspicion saturation issue (H4 finding)

The new Iter 90 channel saturates at 1.0 for all conditions
including baseline. Generation magnitudes (+0.2 per accusation, +0.3
per authority_suppression) overwhelm decay (0.02/tick).

**Options**:
- Lower generation: +0.05 per accusation, +0.1 per authority. HL of
  decay 35t means single event would reach 0.5 transient vs current 1.0.
- Higher decay: 0.05/tick (HL 14t) — faster forgetting.
- Don't tune (current saturation is observable phenomenon, not bug).

Per freeze discipline (no parameter tuning), recommend:
- Annotate as "high-saturation channel; effective range 0.0-0.5"
  rather than re-tune now.

This is a Branch B (simplification) decision point: if public_suspicion
is to be retained as RESERVE+wired, may need re-tuning. If readability
fails, this channel's value is unclear.

---

## 6. Scale-8 progression

Pre-Iter-90: Scale-8 = 1 (Iter 57 + Step E partial)
Post-Iter-90: Scale-8 = 1 (no improvement)

**To reach Score 2** would require either:
- A new motif activator that responds to a non-shame-driven pressure
  (e.g., authority_vigilance re-wiring as hyper-pressure → distinct motif)
- An auxiliary recovery channel (Branch B candidate)
- Reduced public_suspicion generation rate so it doesn't saturate

---

## 7. Implications for branch decision

This finding **strengthens Branch B (kernel simplification +
auxiliary recovery path)**:

- Kernel exhibits single-loop collapse for non-grief pressure mixing
- public_suspicion was added as new variable but saturates immediately
  → low actionable dynamic range
- WORLD_PROCESSES + WORLD_MEMORY + WORLD_MESO_SCALE docs reveal
  many existing channels that all converge to Phase 2a → same recovery

**Branch A (readability)** still possible but readability blind needs
to find the kernel's outputs interesting despite single-loop bias.

**Branch C (broader world)** definitely premature — meso-scale
addition (public_suspicion) didn't produce expected mixing richness;
broader world expansion would produce more variables converging to
same loop.

---

## 8. What could still be wrong (H4)

- 5 seeds × 200 ticks per condition. Larger N might reveal subtle
  drift.
- public_suspicion saturation could mask a partial effect that would
  emerge at lower generation rates.
- Top-motif fractions are aggregated across all agents; per-cohort
  differences (e.g., disciple_follower vs authority_priest) might
  show divergence.
- Heavy authority used 3 guard events but didn't directly target
  authority_vigilance (which is INERT anyway). Could try
  heavy-authority via direct rumor attacks on authority role.

---

## 9. What I did NOT try (H2)

- Public_shame + low_belonging (4th §5.6 candidate; would require
  defining "low belonging" first)
- Re-tuning public_suspicion to non-saturating range
- Per-cohort motif analysis
- Longer horizon (500 tk)

---

## 10. Summary

**Authority + rumor mixing produces no measurable richness over
baseline accusation.** Single-loop collapse confirmed at Scale-8 = 1.

This is the expected outcome given Iter 84's M24 (confess-feedback
unifies recovery): adding upstream pressures that all converge on
shame_climate/blame_concentration cannot escape single-loop dynamics.

**Working mixings require orthogonal motif activation paths** — grief
injection (via direct state write to grief field) is the only clean
example so far.

Branch B preference reinforced.
