# Iter 122 -- Multi-Layer Memory Verified Empirically

**Date:** 2026-04-26
**Iteration:** Iter 122
**Severity:** LOW -- empirical confirmation of Iter 121 audit

---

## 0. Summary

Probed weak-accusation scenario (single seed × 500t) tracking 5
memory layers per tick. **Three layers (shame_climate, blame_concentration,
forgiveness_rumors) are simultaneously active and load-bearing** with
distinct trajectories. **Score-3 (World Memory) = 3 empirically
verified**.

---

## 1. Per-layer dynamics

| Layer | Peak value | Peak tick | Nonzero ticks | Activity |
|---|---:|---:|---:|---|
| shame_climate | 2.00 | 96 | 444/500 (89%) | LOAD-BEARING |
| blame_concentration (sum) | 1.44 | 308 | 410/500 (82%) | LOAD-BEARING |
| forgiveness_rumors | 16 | 122 | 197/500 (39%) | LOAD-BEARING (episodic) |
| public_suspicion | 0.16 | 492 | 67/500 (13%) | weak |
| threat_rumors | 1 | 0 | 6/500 (1%) | mostly inactive |

### Distinct trajectories
- shame_climate: smooth oscillation throughout horizon
- blame_concentration: episodic, peaks during accusation/recovery cycles
- forgiveness_rumors: bursty, peak 16 simultaneously active rumors at t=122
- public_suspicion: low and slow, late-rising
- threat_rumors: only the seeded rumor; decayed by t≈10

### Inter-layer correlation check
- 320 ticks with shame_climate > 0.5
- 0 ticks with public_suspicion > 0.5
- Overlap: 0
- Layers track different aspects of world state

---

## 2. What this confirms

### Score-3 World Memory = 3
Lee's criterion: "여러 memory channel이 동시에 작동". Three channels
demonstrably active simultaneously across most of horizon (89%, 82%, 39%
respectively for top three layers). Verdict: ✓.

### Iter 121 audit was correct
The audit estimated Score-3 = 3 based on layer count + interaction
existence. Iter 122 verifies empirically: layers DO have distinct
trajectories, not synchronized noise.

### Recovery model layer connectivity
Per Iter 117-118 conjunctive model:
- accusation → shame_climate ↑ (memory layer 1)
- accusation → blame_concentration[role] ↑ (memory layer 2)
- confess action → forgiveness_rumor spawn (memory layer 3)
- forgiveness_rumor → blame ↓, shame_climate ↓
- All three active simultaneously creates the recovery cascade

This is the mechanistic foundation of the predictive recovery model.

---

## 3. What was unexpected

### public_suspicion is weak in this scenario
Max 0.16 across 500 ticks (well below threshold for many gating
checks). Only 67 nonzero ticks. Despite being "active memory" per
Iter 90 wiring, it doesn't dominate dynamics in single-accusation
scenario.

This may matter for project file's stated purpose: public_suspicion
was meant as "general/role-independent" complement to blame_concentration.
In practice it provides weak signal.

**Possible explanations**:
- Generation rate too low (per Iter 91 tuning: 0.05 acc, 0.1 auth)
- Decay rate too high (0.02/tick, HL ~35)
- Net effect: barely accumulates above floor

This is a tuning parameter question, not a structural failure.

### threat_rumors are mostly absent after seed
Only the initially seeded `threat_to_authority` rumor exists; it
decays in ~12 ticks. No new threat rumors get spawned by accusation
events.

This means accusation events generate blame_concentration but NOT
new threat rumors. The "rumor topology" Score-6 (Information
Topology) might be weaker than Iter 121 estimated:
- Forgiveness rumors fire reliably (39% of horizon)
- Threat rumors are seed-only
- Rumor topology is half-active

Score-6 estimate from Iter 121: 2 (rumor exists). Iter 122 evidence
suggests this is right -- existence yes, but only one direction
(forgiveness) is regularly populated.

---

## 4. Implications

### 4.1 Score-tier confirmations
- Scale-3 World Memory = 3 ✓ (verified)
- Scale-6 Information Topology = 2 ✓ (consistent with audit; only
  forgiveness rumors propagate regularly post-seed)

### 4.2 No code changes needed
The current memory layers are sufficient. public_suspicion has weak
effect but is not a phantom -- it does fire at limited intensity.
Tuning could amplify it if Lee wants stronger signal, but per Iter
105-119 lessons, only with empirical motivation.

### 4.3 Project direction reading
Multi-layer memory + their interactions = Lee's "world flow"
desideratum. Empirically, the kernel produces distinct dynamics
across 3+ memory layers. This is the structural foundation for
narrative readability claims.

---

## 5. What could still be wrong (H4)

- Single seed × single scenario probe. Different seeds might show
  different layer activity patterns; couldn't generalize from N=1.
- Weak accusation chosen specifically because it produces 53%
  recovery (Iter 116 V0). Different scenarios might show different
  layer balance (e.g., scarcity might activate public_suspicion
  more if it has direct generation pathway).
- "Distinct trajectories" doesn't prove "distinct effects on agent
  behavior". Could be that 2 of 3 layers are redundant (one drives
  the other; both correlate with cause).
- The "0 overlap" between high shame_climate and high public_susp
  could mean public_susp simply never fires high, not that they
  track different things. Stricter test would compare two layers
  that BOTH fire significantly.
- Forgive_rumors max=16 simultaneously is striking -- not sure all
  16 are doing distinct work; they might overlap in target_role.
- Score-3=3 is qualitative criterion ("multiple channels operating");
  3 active layers is one interpretation; stricter interpretation
  might require crossover effects (e.g., shame_climate causally
  modulates forgiveness_rumor effectiveness).

---

## 6. What I did NOT try (H2)

- Scarcity scenario probe (might show different layer balance,
  including stronger public_suspicion if generation pathway exists)
- Sacred scenario probe (might show stronger awe-related memory)
- Per-layer ablation (zero out each layer; measure dynamic change)
- N=15 verification (single-seed point estimate has noise)
- Layer-correlation analysis with formal cross-correlation
- Rumor target_role distribution (if 16 active forgiveness rumors,
  do they target different roles or duplicate)

---

## 7. Conclusion

**Score-3 (World Memory) = 3 empirically verified**. Three load-
bearing layers (shame_climate, blame_concentration, forgiveness_rumors)
operate simultaneously with distinct trajectories. Plus 2 weaker
layers (public_suspicion, threat_rumors) that exist but don't
dominate.

**No code changes**, no architectural retractions, no controversial
findings. Pure empirical verification of Iter 121 audit.

**Project's "world that flows" thesis is now supported at the
memory-layer level**: world has multiple persistent state channels
that all contribute to evolving possibility landscape, exactly as
Lee's project file specifies.

---

## 8. Recommendations for Iter 123+

### (A) Score-tier consolidation document
Update Iter 119/120 scale-tier estimates to reflect Iter 121-122
verification. Single canonical scale tier table.

### (B) Cross-scenario layer activity comparison
Run scarcity + sacred probes through same memory-layer trace.
Compare which layers dominate where. Tests generalization.

### (C) Continue with priority 6 (Mixed-Arc) audit
Iter 113-119 work covers this; could write standalone doc.

### (D) Continue with priority 7 (Population Grammar) audit
Already strong at score 3 per Iter 119. Standalone doc possible.

I lean toward **(A) score-tier consolidation** -- the empirical
work has produced enough material that a clean tier table is timely.
Then (B) for generalization in next iter.
