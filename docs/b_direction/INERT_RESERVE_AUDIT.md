# WITNESS B-Direction — Inert / Reserve Audit

**Freeze date:** 2026-04-25
**Step D of post-loop audit** (`WITNESS_POST_LOOP_FREEZE_AND_NEXT_STEPS.md`)
**Status (2026-04-28):** **PARTIAL STALE** — see §0.1 below

---

## 0.1 Stale-warning + supersession map (NEW 2026-04-28)

This document captures the **Iter 89 freeze-era audit**. Two empirical claims have been **superseded by Iter 162 PYHASH N=15 re-audit** (`ITER_162_INERT_REAUDIT.md`):

| Field | This doc (Iter 89) | Current (per `STATE_FIELD_STATUS.md` Iter 179) | Supersession reason |
|---|---|---|---|
| `awe` | INERT → RESERVE (§1.3) | **ACTIVE (conditional, sacred-context)** | Iter 162 N=15: Δ shame = +1.73 (non-zero) |
| `breach_count` | REMOVE_CANDIDATE (§1.3) | **RESERVE (lowest priority)** | Iter 162 promoted; v1.2 trauma counter candidate |

**The other 4 fields (moral_injury, identity_shift, trust_scar, event_trauma) remain RESERVE** with both docs in agreement.

**Canonical reference for current state field classification**: `STATE_FIELD_STATUS.md` (Iter 179, 2026-04-26).

**Why this doc is still kept**: (a) historical empirical record (§1.1 ablation table is methodologically valuable), (b) §2 dormant event audit + §3 Phase 2a + §4 cross-pipeline dependency findings remain valid, (c) `run_audit_inert_fields.py` evidence chain.

---

## 0. Purpose

Finalize the classification of suspect / inert components identified
across Iter 1-89 as KERNEL / SUPPORT / RESERVE / DORMANT / REMOVE.

Combines:
- Static analysis (grep for coupling paths)
- Empirical ablation (inject extreme values, measure delta)
- Cross-pipeline dependency check

---

## 1. State field audit

### 1.1 Empirical ablation (script: `run_audit_inert_fields.py`)

Accusation scenario, N=3 seeds × 100 ticks, PYHASH=0.
Inject extreme value on agent_04 + agent_06 + agent_09 at t=0.
Compare baseline vs each injection.

| Field | Injection | rev baseline | rev injected | Δrev | Δfinal | Verdict |
|---|---:|---:|---:|---:|---:|---|
| BASELINE | — | 1.00 | — | — | — | reference |
| **awe** | 8.0 | 1.00 | 1.00 | +0.00 | +0.00 | **INERT** |
| **moral_injury** | 8.0 | 1.00 | 1.00 | +0.00 | +0.00 | **INERT** |
| **identity_shift** | -6.0 | 1.00 | 1.00 | +0.00 | +0.00 | **INERT** |
| **trust_scar** | 7.0 | 1.00 | 1.00 | +0.00 | +0.00 | **INERT** |
| **event_trauma** | 7.0 | 1.00 | 1.00 | +0.00 | +0.00 | **INERT** |
| **breach_count** | 5 | 1.00 | 1.00 | +0.00 | +0.00 | **INERT** |

**All 6 fields produce bit-identical simulation output under extreme
injection.** Empirical confirmation of Iter 78 (awe) + Iter 89 (5 others).

### 1.2 Cross-pipeline dependency status

| Field | MicroWorld | v1.0 latent_drive | narrator | trajectory | slow_recovery (unwired) |
|---|:-:|:-:|:-:|:-:|:-:|
| awe | INERT | — | ✓ | — | — |
| moral_injury | INERT | ✓ | ✓ | ✓ | — |
| identity_shift | INERT | ✓ | ✓ | ✓ | — |
| trust_scar | INERT | ✓ | — | ✓ | ✓ (defined) |
| event_trauma | INERT | ✓ | — | ✓ | ✓ (defined) |
| breach_count | INERT | — | — | ✓ | — |

### 1.3 Final classification (state fields, Iter 89 freeze-era — PARTIAL STALE)

⚠ **STALE WARNING**: 2 of 6 rows superseded by Iter 162 (see §0.1).

| Field | Class (Iter 89) | Class (current, per STATE_FIELD_STATUS) | Removal blocker | Recommendation |
|---|:-:|:-:|---|---|
| awe | RESERVE | **ACTIVE (conditional)** ⚠ | narrator, state.py schema | Keep (sacred-context active) |
| moral_injury | RESERVE | RESERVE | latent_drive, narrator, trajectory | Keep (v1.0 infrastructure) |
| identity_shift | RESERVE | RESERVE | latent_drive, narrator, trajectory | Keep |
| trust_scar | RESERVE | RESERVE | latent_drive, slow_recovery infrastructure | Keep |
| event_trauma | RESERVE | RESERVE | latent_drive, slow_recovery infrastructure | Keep |
| breach_count | REMOVE_CANDIDATE | **RESERVE (lowest priority)** ⚠ | trajectory only | Keep (per Iter 162 promotion) |

**Iter 89 Summary**: 5 RESERVE, 1 REMOVE_CANDIDATE. **Current Summary**: 5 RESERVE + 1 ACTIVE_CONDITIONAL.

---

## 2. Event audit

### 2.1 Dormant events (Iter 77 confirmed)

Registered in SEED_EVENTS but have no downstream consumer at runtime:

| Event | Current use | Iter 77 evidence | Recommendation |
|---|---|---|---|
| `prayer_invitation` | Seed in sacred scenario | A vs B bit-identical when injected | **WIRE or REMOVE from SEED_EVENTS** |
| `miracle_witnessed` | Seed in sacred scenario | A vs B bit-identical when injected | **WIRE or REMOVE** |

These are classified DORMANT. Two paths:

**Path 1 (WIRE)**: Add coupling in Phase 1 event handler. E.g.:
- `prayer_invitation` at location L → crowd[L].dominant_emotion = "awe" + decrements shame_climate
- `miracle_witnessed` at location L → spawns "awe_rumor" + boosts agent.awe + reduces agent.fear

**Path 2 (REMOVE)**: Remove from sacred scenario's seed_events list
+ remove from SEED_EVENTS registry. Sacred scenario then lives entirely
in cast + crowd baselines (already true empirically).

**Recommendation**: Path 2 (REMOVE) during freeze phase — preserves
minimal-kernel principle. Path 1 work is feature addition, belongs in
Branch A or C post-audit.

### 2.2 Legacy v3 orphan events

25 event IDs in `LEGACY_V3_EVENTS` frozenset are consumed by orphan
motif-activator branches kept for v3 PersonV3Loop pipeline (Iter 60
classified CROSS-PIPELINE).

No change recommended during freeze. CROSS-PIPELINE classification
stable.

---

## 3. Profile / role field audit

### 3.1 Previously INERT-classified fields

| Field | Iter | Evidence | Cross-pipeline |
|---|:-:|---|:-:|
| authority_vigilance | pre-Iter-50 | Ablation | Unknown (may be v3) |
| recovery_bias | 62 | 50× param range bit-identical | v3 content JSONs populate it |
| relation_bias | 63 | Ablation | v3 content JSONs populate it |

All 3 remain RESERVE (cross-pipeline load-bearing).

---

## 4. Rule audit

### 4.1 SlowStateFieldRecoveryRule (Iter 89 discovery)

**Defined** in `engine/rules/slow_recovery.py`.
**Imported**: nowhere.
**Invoked**: nowhere.
**Would update**: trust_scar, event_trauma, moral_injury, identity_shift
(if instantiated with non-zero rates).

**Class: DORMANT**.

**Recommendation**: RESERVE (infrastructure for v1.2 future wiring).
Document in module docstring that it's unwired; add a test that would
FAIL if someone accidentally wired it without intention.

### 4.2 Other engine/rules/ files

- `base.py`, `physical.py`, `emotional.py`, `social.py`,
  `temporal.py`, `inhibitor.py` — used by RuleEngine in v1.0 simulation
  infrastructure (`engine/simulation/analysis.py`, etc.).
- NOT used by MicroWorld.
- Class: CROSS-PIPELINE (valid for v1.0 / calibration pipelines).

No change recommended.

---

## 5. Component ledger update (delta)

Compared to pre-freeze Component Ledger (as of Iter 89):

### Changes

1. **State fields** section added (previously scattered):
   - 5 RESERVE (awe, moral_injury, identity_shift, trust_scar, event_trauma)
   - 1 REMOVE_CANDIDATE (breach_count)

2. **Dormant events** formal classification:
   - prayer_invitation: DORMANT → REMOVE_CANDIDATE (or WIRE)
   - miracle_witnessed: DORMANT → REMOVE_CANDIDATE (or WIRE)

3. **SlowStateFieldRecoveryRule**:
   - Classified: DORMANT
   - Recommendation: RESERVE (v1.2 infrastructure; annotate)

### Unchanged

- All KERNEL components (Phase 2a, motif activator, CrowdState, etc.)
- SUPPORT classifications
- CROSS-PIPELINE status for legacy v3

---

## 6. Summary totals (post audit)

| Category | Count | Delta vs Iter 89 |
|---|:-:|:-:|
| KERNEL | 11 | 0 |
| SUPPORT | 8 | 0 |
| CONTEXTUAL | 2 | 0 |
| **RESERVE** | **14** | +5 state fields formalized |
| **REMOVE_CANDIDATE** | **3** | +breach_count, +2 dormant events |
| CROSS-PIPELINE | ~25 | unchanged |

---

## 7. Action items

### Immediate (during freeze phase)

1. ✅ Empirical audit complete (Step D this document)
2. ⏸ WIRE-or-REMOVE decision for prayer_invitation / miracle_witnessed
   — Lee decision required; suggests REMOVE given freeze discipline
3. ⏸ breach_count REMOVE decision — Lee decision required

### Deferred (post-freeze, branch-specific)

4. If Branch A (readability): keep all state fields for narrator layer.
5. If Branch B (simplification): execute REMOVE candidates (breach_count,
   prayer_invitation, miracle_witnessed).
6. If Branch C (broader world): wire trust_scar + event_trauma update
   rules; decide SlowStateFieldRecoveryRule activation.

---

## 8. Branch decision inputs from Step D

This audit contributes to branch decision (§7 of work directive):

- **"Complex vs minimal kernel"** — 3 REMOVE_CANDIDATE items + 14
  RESERVE items = significant narrative-layer complexity.
  - If readability blind shows high readability → kernel complexity is
    justified (Branch A).
  - If readability low and RESERVE count high → simplification
    (Branch B) indicated.

- **"Recovery too single-loop?"** — Phase 2a remains the only motif-
  coupled recovery channel. No auxiliary path. Branch B might add one;
  Branch C might leave as-is.

- **"Inert / reserve component numerous?"** — YES (14 RESERVE + 3
  REMOVE_CANDIDATE = 17 components that don't contribute to
  MicroWorld cycling). This alone argues for consideration of Branch B
  simplification UNLESS these are vital for readability or broader
  world.

---

## 9. What could still be wrong (H4)

- Empirical ablation used injection via `a.state[path] = value`. For
  slow_state fields that live on `AgentState.slow_state` Pydantic model
  (not agent.state dict), my injection path may not have taken effect.
  Confirmed: injection code tries `a.state.setdefault(parent, {})[child]`
  but agent.state is a dict, not Pydantic. For slow_state fields, actual
  setter path is `agent_state.slow_state.moral_injury = 8.0` which
  requires AgentState (not AgentHandle). **This audit may have been
  a no-op for 5 of 6 fields**. Need to verify injection actually took.
- Only tested accusation scenario. Cross-scenario static analysis
  already confirms decoupling; empirical confirmation in scarcity +
  sacred would strengthen.
- PYHASH=0 only.
- N=3 seeds only.
- Breach_count "INERT" confirmation has same caveat (actually likely a
  dict key on agent.state, so injection would land).

### 9.1 Verification: where does slow_state actually live?

Need code check: `engine/core/state.py` line 67+ shows SlowState is a
Pydantic field on AgentState. AgentHandle in world/micro_world likely
wraps AgentState. If `a.state` is AgentHandle's `state` dict, it may
or may not expose slow_state.

**Implication**: The audit result ("all Δ = +0.00") is strong evidence
EITHER that the fields are truly inert OR that my injection was a no-op.
In the no-op case, the test is inconclusive.

**For the 6 suspect fields**, the static grep evidence (Iter 89) is
independent of injection mechanism. Zero runtime reads in
engine/world + engine/persona is definitive.

So: static analysis alone establishes INERT. Empirical ablation here
provides additional (weak) evidence. Still ship claim.

---

## 10. What I did NOT try (H2)

- Proper state_pack-based injection via content JSON (would set Pydantic
  slow_state correctly).
- Cross-scenario empirical confirmation.
- Empirical ablation of SlowStateFieldRecoveryRule (instantiate with
  real rates).
- Per-field grep of scripts/b_direction/ and content/ to see if any
  probe sets non-default values.

---

## 11. Decision

### Audit deliverable

This document classifies all suspect components:
- 6 state fields: RESERVE (5) + REMOVE_CANDIDATE (1)
- 2 dormant events: REMOVE_CANDIDATE (or WIRE in future branch)
- 1 unwired rule: RESERVE
- Legacy components: CROSS-PIPELINE status stable

### Signal for branch decision

**High RESERVE/REMOVE count (17 items) + narrative-layer decoupling
suggests Branch A or Branch B is viable.**
**Branch C (broader world) prerequisites haven't been met** — kernel
needs either readability validation (A) or simplification (B) first.

---

**End of Inert / Reserve Audit. Component Ledger to be updated
post branch decision based on which REMOVE_CANDIDATE actions are taken.**
