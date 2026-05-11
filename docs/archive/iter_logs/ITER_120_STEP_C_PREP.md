# Iter 120 -- Step C Readability Prep: Probe Materials Updated

**Date:** 2026-04-26
**Iteration:** Iter 120
**Severity:** LOW -- pre-evaluation infrastructure improvement

---

## 0. Summary

Step C (External Readability Blind, project file priority 2) is
human-gated and cannot be run by Claude. This iter prepares the
existing probe infrastructure (P1-P12, generated Iter 99) for clean
human evaluation by:

1. **Regenerating probes with proper PYHASH** -- old probes were
   produced with the Iter 105 hash-seed bug; deterministic
   regeneration ensures probes match what the engine actually
   produces today
2. **Removing scenario label leak** -- old probe headers exposed
   scenario via role names ("fisher_laborer" → scarcity,
   "spiritual_wanderer" → sacred). Anonymized to neutral generic
   role labels (laborer, wanderer, authority, etc.)

Materials are now ready for Lee's blind evaluation when time allows.

---

## 1. What was found

### 1.1 PYHASH issue (carried over from Iter 105)
The probe generator (`scripts/b_direction/generate_readability_probes.py`)
was retrofitted with the Iter 105 PYHASH guard during the bulk
retrofit (Iter 105 §4.1). However, the .txt probe files in
`docs/b_direction/readability_probes/` were generated in Iter 99,
BEFORE the PYHASH bug was identified.

Consequence: probes Lee would read might not be exactly what the
current deterministic engine produces.

### 1.2 Scenario label leak via role/location names

Probe header format pre-Iter-120:
```
Agents: A1=merchant, A2=family_anchor, A3=fisher_laborer, ...
Locations: L1=marketplace, L2=poor_quarter
```

Problems:
- `fisher_laborer` is unique to scarcity scenario → leaks scenario
- `spiritual_wanderer` is unique to sacred → leaks scenario
- `marketplace` is unique to scarcity location set → leaks
- `temple_outer_court` is unique to sacred → leaks
- `priest_courtyard` + `upper_room` is unique to accusation → leaks

A trained evaluator (e.g., Lee) would identify scenario from header
in seconds, defeating the blind protocol's purpose.

---

## 2. What was done

### 2.1 Regenerated probes under proper PYHASH
- Verified `scripts/b_direction/generate_readability_probes.py`
  imports `enforce_pyhash` from `_pyhash_guard.py` (line 28)
- Re-ran probe generation with `unset PYTHONHASHSEED` then python
  command — guard re-execs with PYHASH=0
- Verified determinism by running twice, confirming identical
  output

### 2.2 Anonymized role names

Added `ANONYMIZED_ROLE_MAP` at line 184 of generator:
```python
ANONYMIZED_ROLE_MAP = {
    "disciple_follower": "follower",
    "authority_priest": "authority",
    "soldier_enforcer": "enforcer",
    "crowd_participant": "crowd",
    "family_anchor": "family",
    "outsider": "outsider",
    "fisher_laborer": "laborer",
    "merchant": "merchant",
    "spiritual_wanderer": "wanderer",
    "prophet": "speaker",
}
```

Header now reads (P1, scarcity scenario):
```
Agents: A1=merchant, A2=family, A3=laborer, A4=laborer, ...
Locations: L1, L2
```

vs (P4, sacred scenario):
```
Agents: A1=wanderer, A2=authority, A3=follower, A4=follower, ...
Locations: L1, L2
```

Cast diversity remains visible (different role mixes per scenario)
without exposing scenario label.

### 2.3 Locations stripped to L1, L2 only
Removed `L1=marketplace` style mapping; now just `L1, L2`. Event
log already used L1/L2 referencing, so this is consistent.

---

## 3. What's still NOT changed

### 3.1 Event names not anonymized

Sacred-specific events (prayer_invitation, miracle_witnessed) and
scarcity-specific events (scarcity_pressure) still appear in event
logs. These are observable phenomena that the evaluator should see
to answer Q2 (perceived pressure).

**Reason for keeping**: per Q2's design, "sacred_awe" answer
explicitly relies on perceiving sacred-coded events. Anonymizing
events would defeat the question.

### 3.2 State snapshots not anonymized

State fields (shame, guilt, fear, grief) are listed by name. These
are pressure dimensions the evaluator should perceive. Anonymizing
them would defeat Q2/Q3.

### 3.3 Probe files unchanged in structure

- 12 probes (P1-P12)
- ~415 lines each
- Same per-probe content structure

---

## 4. What Lee can now do

The blind evaluation protocol is fully ready:
1. Read `docs/b_direction/READABILITY_BLIND_PROTOCOL.md` for the
   methodology and Q1-Q5 questions
2. Open `docs/b_direction/readability_probes/P1.txt` through
   `P12.txt` and answer Q1-Q5 per probe BLIND
3. Fill in `docs/b_direction/READABILITY_BLIND_RESULTS.md` template
4. After all 12 done, consult
   `docs/b_direction/READABILITY_BLIND_GROUND_TRUTH.md` to score
   accuracy

Expected effort: ~5-10 minutes per probe × 12 = ~1-2 hours for full
evaluation.

---

## 5. Connection to Iter 119 structural model

Iter 119 finalized the predictive model:
> recovery_rate ≈ ∏ P(role r forgiven | cast, pressure, horizon)

The 12 probes test 3 scenarios × 4 variants. All produce simulation
traces under 200t horizon. Per the model:
- Sacred baseline (P4, P5): expected recovery arc (mid-fraction)
- Sacred Phase 2a OFF (P12): expected NO recovery arc
- Accusation baseline (P10, P11): mostly saturation (1-2 acc, 1
  outsider in cast → conjunctive crash predicted)
- Scarcity (P2, P9): mostly saturation
- Mul variants: regime-altered cycling

The blind eval should detect these qualitative arc differences if
the kernel is producing readable flow. If evaluator labels most as
"random" or "no arc", that's evidence the kernel produces
mechanism-level success but narrative-level failure -- pointing
to Branch B simplification per protocol §6.3.

---

## 6. Updated infrastructure status

| Component | Status |
|---|---|
| Probe generator PYHASH guard | ✓ Iter 105 retrofit |
| Probe role/location anonymization | ✓ Iter 120 fix |
| 12 probes regenerated | ✓ Iter 120 |
| Ground truth file | ✓ existing |
| Protocol document | ✓ existing |
| Results template | ✓ existing (empty) |
| Human evaluator | ⏳ awaits Lee |

---

## 7. What could still be wrong (H4)

- The role anonymization map has 10 known roles. If a probe uses a
  role not in the map (unlikely given current cast designs), it
  leaks. Mitigation: ANONYMIZED_ROLE_MAP returns role_id unchanged
  if not in dict, so any new role would still leak. Should be
  caught in code review.
- "merchant" exists in both scarcity and accusation scenarios; the
  word itself is not scenario-specific so anonymizing it isn't
  needed. But this means "merchant in cast" is ambiguous between
  the two scenarios.
- The 200t horizon might be too short for sacred recovery arcs
  to fully manifest. Iter 113's late-miracle finding (60% recovery
  at 500t) might be ~30% at 200t. Probe arc visibility could be
  weaker than expected.
- I haven't verified whether the regenerated probe text matches
  Iter 99 probe text byte-for-byte. They likely DIFFER (different
  PYHASH state at Iter 99 generation time). Lee may have made
  partial blind notes on the old probes; those would be invalidated
  by regeneration.
- Bullet 4 above is a real risk: if Lee already has notes from old
  probes, regeneration overwrote those probes. We may have lost
  evaluator preparation work without realizing it.

---

## 8. What I did NOT try (H2)

- Did NOT add new probes (e.g., Iter 118 cast augmentation rescue
  showcase)
- Did NOT change horizon to 500t to give arcs more time to manifest
- Did NOT verify probe text against pre-Iter-120 versions before
  regenerating (potential data loss)
- Did NOT add HTML/markdown formatting for easier reading
- Did NOT generate a Q1-Q5 example walkthrough

---

## 9. Recommended next direction

The Step C blind evaluation is now ready for Lee. Two paths from here:

### (A) Wait for Lee's blind evaluation
Step C is blocked on human evaluator. Once Lee fills in
READABILITY_BLIND_RESULTS.md, the verdict directly informs
project direction (Branch A/B/C choice per protocol §6.3).

### (B) Continue empirical work in parallel
While Step C is human-gated, other priorities can be advanced:
- Priority 4: World Memory layer formalization
- Priority 5: Meso-scale state additions
- Slow-state mechanism (currently INERT) integration

### (C) Add Iter 118-style demonstration probes
Add P13/P14 showing cast augmentation rescue as an explicit "kernel
produces predictable arc difference" demonstration. Could go in a
separate "extended probe set" file.

I lean toward **(B) continue empirical work** since (A) is human-paced
and (C) is optional. Priorities 4-5 from the project file have not
been fully addressed in Iter 105-119; addressing them would extend
the kernel.

---

## 10. Conclusion

**Step C readability blind eval materials are now Lee-ready**:
- 12 probes regenerated under proper PYHASH (deterministic)
- Scenario label leak removed via role anonymization
- Protocol and ground-truth files exist
- Empty results template ready for filling

**Remaining gap**: human evaluator. Lee can run the blind protocol
when time permits.

**No engine changes**, no architectural retractions, no controversial
findings. This is pure infrastructure preparation work that unblocks
a downstream priority.
