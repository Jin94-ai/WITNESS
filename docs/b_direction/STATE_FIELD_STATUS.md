# WITNESS State Field Status -- Reserve / Active / Cross-Pipeline

**Date:** 2026-04-26
**Iteration:** Iter 179 (Step B1 of new directive)
**Source basis:** Iter 89 grep audit + Iter 162 PYHASH N=15 re-audit + Iter 123 awe finding
**Sibling doc:** `INERT_RESERVE_AUDIT.md` (Iter 89 audit, freeze era)
**Sibling doc:** `ITER_162_INERT_REAUDIT.md` (PYHASH-corrected re-audit)

---

## 0. Purpose

Single per-field reference table for every `AgentState.slow_state` field
and related state-dict fields. Replaces scattered references in
INERT_RESERVE_AUDIT.md, ITER_162_INERT_REAUDIT.md, and COMPONENT_LEDGER.md
with one canonical status per field.

This is **B1 directive output**:
> "5 reserve 항목 확정 표기 / 각 항목의 현재 상태, 제거 여부 아님, future
> reactivation 조건 한 줄씩 기록 / unwired / doc-only / decorative 여부 표시"

---

## 1. Status legend

| Status | Meaning |
|---|---|
| **ACTIVE** | Read by MicroWorld runtime; affects dynamics |
| **ACTIVE (conditional)** | Active only in specific scenarios/contexts |
| **RESERVE** | Schema/storage retained; MicroWorld INERT but cross-pipeline load-bearing |
| **REMOVE_CANDIDATE** | RESERVE with weakest cross-pipeline dependency; could be removed |

| Tag | Meaning |
|---|---|
| `unwired` | Schema exists, no rule reads it for state updates |
| `doc-only` | Defined for narrative/render or trajectory log only |
| `decorative` | Set by content/builders but no consumer (cosmetic) |
| `latent-infra` | Reserved for v1.0 PredictiveLatentDrive future activation |
| `slow-recovery-infra` | Reserved for v1.2 SlowStateFieldRecoveryRule future activation |

### 1.2 Cross-doc terminology alignment (NEW 2026-04-28; audit completed LOOP 19 2026-04-28)

**Audit결과 (LOOP 19 cross-doc consistency check)**:
- ✓ COMPONENT_LEDGER §11 ↔ STATE_FIELD §2: 5 fields 명단 + tags + status + reactivation 모두 일치
- ✓ KERNEL_GAPS §8 ↔ §2-§7: 6 gaps cost/risk/Lee gate 모두 일치
- ✓ ANNOTATED_PROBE_FORMAT §1.2.0 5 labels ↔ RESULTS_V2 §1.1.5 vocabulary: 5 labels 일치
- ✓ INERT_RESERVE_AUDIT §0.1 supersession map ↔ STATE_FIELD §2: 2 supersession (awe, breach_count) 명시 일치 (LOOP 16에서 추가)

State-field 용어와 SACRED_STATUS_NOTE의 mechanism status 분류는 **다른 차원**이지만 자주 혼용되어 정리:

| 차원 | 용어 | 사용 doc | 의미 |
|---|---|---|---|
| **State field schema** | ACTIVE / RESERVE / REMOVE_CANDIDATE | this doc, COMPONENT_LEDGER §11 | 필드 자체가 dynamics에 영향을 주는가 |
| **State field tag (sub)** | unwired / doc-only / decorative / latent-infra / slow-recovery-infra | this doc | RESERVE 상태의 *이유* |
| **Mechanism wiring** | WIRED / CAUSALLY ACTIVE / DECORATIVE | SACRED_STATUS_NOTE.md | 메커니즘(예: prayer/miracle handler)이 코드에 연결되어 인과 영향을 주는가 |

**왜 두 축이 분리되는가**: 한 mechanism이 WIRED여도 그것이 읽는 *field*가 RESERVE일 수 있음 (반대도 가능). 예:
- `awe` field = ACTIVE (conditional) — 메커니즘이 읽음
- `prayer_invitation` handler = WIRED + CAUSALLY ACTIVE — handler가 awe를 set
- `aux awe→shame_decay` = DECORATIVE — wired but fires <1% (Iter 108)
- `moral_injury` field = RESERVE (unwired) — 어떤 active mechanism도 안 읽음

**Cross-link**:
- SACRED_STATUS_NOTE §1 mechanism inventory ↔ this doc §3 awe section
- COMPONENT_LEDGER §11 RESERVE state fields ↔ this doc §2 (1:1 매핑)

---

## 2. The 5 RESERVE state fields

These 5 fields are the directive B1 target. All confirmed RESERVE by
Iter 162 PYHASH N=15 ablation (Δ shame = 0.00 under extreme injection).

### 2.1 moral_injury
- **Status:** RESERVE
- **Tags:** `unwired` `latent-infra` `doc-only`
- **MicroWorld empirical:** Δ shame = 0.00 (injection 8.0, N=15)
- **Cross-pipeline reads:** v1.0 LatentDrive read; narrator render; trajectory log
- **Future reactivation condition:** v1.2 SlowStateFieldRecoveryRule wiring OR v1.0 LatentDrive activation
- **Removal blocker:** Pydantic schema in `engine/core/state.py`, narrator depends on field, v3 content JSONs populate it
- **Recommendation:** RETAIN. Do not remove.

### 2.2 identity_shift
- **Status:** RESERVE
- **Tags:** `unwired` `latent-infra` `doc-only`
- **MicroWorld empirical:** Δ shame = 0.00 (injection -6.0, N=15)
- **Cross-pipeline reads:** v1.0 LatentDrive read; narrator render; trajectory log
- **Future reactivation condition:** Same as moral_injury (v1.2 recovery rule OR v1.0 LatentDrive)
- **Removal blocker:** Pydantic schema, narrator dependency, v3 content
- **Recommendation:** RETAIN.

### 2.3 trust_scar
- **Status:** RESERVE
- **Tags:** `unwired` `latent-infra` `slow-recovery-infra`
- **MicroWorld empirical:** Δ shame = 0.00 (injection 7.0, N=15)
- **Cross-pipeline reads:** v1.0 LatentDrive read; trajectory log
- **Future reactivation condition:** v1.2 SlowStateFieldRecoveryRule (already defined for this field but unwired)
- **Removal blocker:** Pydantic schema, slow_recovery infra, v3 content
- **Recommendation:** RETAIN. Closest to v1.2 reactivation candidate.

### 2.4 event_trauma
- **Status:** RESERVE
- **Tags:** `unwired` `latent-infra` `slow-recovery-infra`
- **MicroWorld empirical:** Δ shame = 0.00 (injection 7.0, N=15)
- **Cross-pipeline reads:** v1.0 LatentDrive read; trajectory log
- **Future reactivation condition:** v1.2 SlowStateFieldRecoveryRule (already defined but unwired)
- **Removal blocker:** Pydantic schema, slow_recovery infra, v3 content
- **Recommendation:** RETAIN. Closest to v1.2 reactivation candidate.

### 2.5 breach_count
- **Status:** RESERVE (was REMOVE_CANDIDATE in Iter 89; promoted to RESERVE Iter 162)
- **Tags:** `unwired` `doc-only`
- **MicroWorld empirical:** Δ shame = 0.00 (injection 5, N=15)
- **Cross-pipeline reads:** trajectory log only (lowest dependency among 5)
- **Future reactivation condition:** Currently no candidate rule defined for breach_count update. Potential future use for "trauma counter" in v1.2.
- **Removal blocker:** Pydantic schema, trajectory format, ~5 tests reference it
- **Recommendation:** RETAIN with note. Lowest-priority RESERVE; could move back to REMOVE_CANDIDATE if v1.2 work doesn't claim it.

---

## 3. Awe -- conditionally ACTIVE (NOT in RESERVE list)

awe was originally classified RESERVE (Iter 89) but Iter 162 PYHASH N=15
ablation found **Δ shame = +1.73** when injected. Iter 123 had previously
identified awe as load-bearing in sacred contexts via aux pathway.

- **Status:** ACTIVE (conditional, sacred-context)
- **Tags:** none (active load-bearing)
- **MicroWorld empirical:** Δ shame = +1.73 (injection 8.0, N=15) — non-zero, direction unexpected (shame INCREASE not DECREASE)
- **Cross-pipeline reads:** narrator (sacred render); v3 content
- **Active mechanism:** Iter 92-95 awe-driven shame decay (aux pathway, conditional)
- **Direction puzzle:** Iter 162 found INCREASE, but Iter 92-95 expected DECREASE. Untested whether interaction with crowd state initialization explains direction.
- **Recommendation:** RETAIN. Treat as ACTIVE, not RESERVE.

---

## 4. Profile fields with INERT history (cross-pipeline RESERVE)

These are NOT state fields but persona profile fields. Listed here for
completeness because they share RESERVE classification.

### 4.1 recovery_bias
- **Status:** RESERVE (per `COMPONENT_LEDGER.md` §2)
- **Tags:** `unwired` (for MicroWorld) `latent-infra` `decorative`
- **Iter 62 ablation:** 50× param range → bit-identical dynamics
- **Cross-pipeline reads:** v3 PersonV3Loop content files populate it; legacy v3 hooks
- **Future reactivation condition:** v3 PersonV3Loop reactivation OR v1.0 LatentDrive integration
- **Removal blocker:** v3 content compatibility, 3 tests
- **Recommendation:** RETAIN.

### 4.2 relation_bias
- **Status:** RESERVE (per `COMPONENT_LEDGER.md` §2)
- **Tags:** `unwired` (for MicroWorld) `decorative` (archetype tuning)
- **Iter 63 ablation:** 20× param range → bit-identical dynamics
- **Cross-pipeline reads:** v3 PersonV3Loop content files populate; archetype scenario builders mutate (cosmetic)
- **Future reactivation condition:** v3 PersonV3Loop reactivation OR new MicroWorld coupling
- **Removal blocker:** v3 content, 3 tests
- **Recommendation:** RETAIN.

### 4.3 authority_vigilance (memory field)
- **Status:** INERT (retained for observability per `COMPONENT_LEDGER.md` §3)
- **Tags:** `unwired` `doc-only`
- **Iter 38 ablation:** Coupling to physical_threat removed; field retained for trace visibility
- **Recommendation:** RETAIN as INERT, observability only.

---

## 5. Unwired rule -- SlowStateFieldRecoveryRule

- **Defined:** `engine/rules/slow_recovery.py`
- **Imported:** nowhere
- **Invoked:** nowhere
- **Would update:** trust_scar, event_trauma, moral_injury, identity_shift
- **Status:** RESERVE (slow-recovery-infra)
- **Future reactivation condition:** v1.2 phase work (post-branch decision)
- **Recommendation:** RETAIN. Annotate docstring that it's unwired; add a regression test that fails if it's accidentally wired without intention.

---

## 6. Dormant events -- 2 REMOVE_CANDIDATE

Per `INERT_RESERVE_AUDIT.md` §2.1:

| Event | Status | Recommendation |
|---|---|---|
| `prayer_invitation` | DORMANT (seed in sacred, no consumer) | REMOVE or WIRE; freeze-discipline favors REMOVE |
| `miracle_witnessed` | DORMANT (seed in sacred, no consumer) | REMOVE or WIRE; freeze-discipline favors REMOVE |

These are NOT state fields. Listed for completeness because they share
the "decorative-suspect" character that Step B3 will document for the
sacred scenario.

---

## 7. Summary table (all RESERVE / DORMANT items)

| Item | Type | Status | Tags | Future activation |
|---|---|---|---|---|
| moral_injury | state field | RESERVE | unwired, latent-infra, doc-only | v1.2 recovery OR v1.0 latent |
| identity_shift | state field | RESERVE | unwired, latent-infra, doc-only | v1.2 recovery OR v1.0 latent |
| trust_scar | state field | RESERVE | unwired, latent-infra, slow-recovery-infra | v1.2 SlowStateFieldRecoveryRule |
| event_trauma | state field | RESERVE | unwired, latent-infra, slow-recovery-infra | v1.2 SlowStateFieldRecoveryRule |
| breach_count | state field | RESERVE (lowest) | unwired, doc-only | v1.2 trauma counter (no candidate rule yet) |
| awe | state field | **ACTIVE (conditional)** | (active in sacred) | already active; needs direction-of-effect investigation |
| recovery_bias | profile field | RESERVE | unwired, latent-infra, decorative | v3 PersonV3Loop reactivation |
| relation_bias | profile field | RESERVE | unwired, decorative | v3 PersonV3Loop reactivation |
| authority_vigilance | memory field | INERT (observability) | unwired, doc-only | none planned |
| SlowStateFieldRecoveryRule | rule | RESERVE | unwired, slow-recovery-infra | v1.2 wiring |
| prayer_invitation | event | REMOVE_CANDIDATE | (seed-only, no consumer) | freeze-discipline: REMOVE |
| miracle_witnessed | event | REMOVE_CANDIDATE | (seed-only, no consumer) | freeze-discipline: REMOVE |

**5 state fields RESERVE** (per directive B1) + 2 profile fields RESERVE
+ 1 INERT-observability + 1 unwired rule + 2 REMOVE_CANDIDATE events.

---

## 8. Removal policy (per Iter 162 + this iter)

**DO NOT REMOVE** any RESERVE item. Removal would:
- Break Pydantic schema (state fields)
- Break narrator render (moral_injury, identity_shift, awe)
- Break v3 content loading (recovery_bias, relation_bias)
- Break trajectory log readers (all state fields)
- Break v3 PersonV3Loop tests (~5-10 tests)

**Mark, don't remove.** This document IS the marking.

REMOVE_CANDIDATE items (prayer_invitation, miracle_witnessed) require
Lee decision — not removed automatically.

---

## 9. What could still be wrong (H4)

### 9.1 Empirical injection caveat (from INERT_RESERVE_AUDIT.md §9.1)
The Iter 89 + Iter 162 ablation injects via `agent.state[path]`. For
slow_state fields living on Pydantic `AgentState.slow_state`, the actual
setter path is different. **Result Δ=0.00 may indicate true INERT OR
no-op injection.** Static grep evidence (zero runtime reads) is
independent and stronger.

### 9.2 Cross-scenario coverage
Both audits used accusation scenario primarily. Scarcity / sacred
empirical confirmation is partial. Static analysis covers all scenarios,
but empirical signal is accusation-weighted.

### 9.3 awe direction-of-effect puzzle
Iter 162 found awe injection INCREASES shame (Δ +1.73). Iter 92-95
mechanism predicts DECREASE. Untested explanations:
- awe_decay (0.05/tick) brings awe below threshold quickly
- crowd state initialization interaction
- aux pathway conditional fires only briefly

awe is classified ACTIVE conditional but mechanism is not fully validated.

### 9.4 breach_count promotion
Iter 89 audit listed breach_count as REMOVE_CANDIDATE (lowest dependency).
Iter 162 promoted to RESERVE. The promotion was based on "no harm in
keeping" rather than positive evidence of need. If v1.2 doesn't claim it,
it could revert to REMOVE_CANDIDATE.

---

## 10. What I did NOT try (H2)

- Proper state_pack-based injection via Pydantic AgentState (would set
  slow_state correctly, ruling out no-op caveat)
- Cross-scenario empirical confirmation (scarcity + sacred)
- Direct probe of awe direction-of-effect mechanism (decay interaction
  vs crowd state interaction)
- Removal proposal for prayer_invitation / miracle_witnessed (Lee gate)
- v1.2 SlowStateFieldRecoveryRule prototype wiring

Reasons:
- Step B1 is documentation, not new ablation
- Directive §6: 새 메커니즘 drilling 금지
- Removal decisions are Lee gate

---

## 11. Versioning

| Version | Date | Source |
|---|---|---|
| Iter 89 INERT_RESERVE_AUDIT (pre-PYHASH) | 2026-04-25 | grep + injection (N=3) |
| Iter 162 INERT_REAUDIT (PYHASH N=15) | 2026-04-26 | confirmed 5/6 INERT, awe non-inert |
| **Iter 179 STATE_FIELD_STATUS.md (this doc)** | **2026-04-26** | **Per-field canonical reference** |
