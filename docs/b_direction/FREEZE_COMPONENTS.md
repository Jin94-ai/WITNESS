# WITNESS B-Direction — Frozen Component Classification

**Freeze date:** 2026-04-25
**Git SHA:** `2ec0da125fbb0d334b159351ef1967c058acb0e0`
**Source:** Distills `COMPONENT_LEDGER.md` (as of Iter 89) into a compact
classification matrix for the freeze audit.

---

## 1. Classification levels

- **KERNEL** — removal collapses cycle existence or ≥1 major feature
- **CONDITIONAL KERNEL** — kernel only in specific scenario class
- **SUPPORT** — amplifies kernel or scenario-specific contribution
- **CONTEXTUAL** — present, observable, but low downstream effect
- **INERT (MicroWorld)** — no measurable MicroWorld effect (but may be
  load-bearing for other pipelines — see CROSS-PIPELINE column)
- **DORMANT** — defined but not wired at runtime
- **CROSS-PIPELINE** — kept for consumers outside MicroWorld

---

## 2. Engine motif layer

| Component | Class | Primary contribution | Removal cost | X-pipe? |
|---|:-:|---|---|:-:|
| `motif_tendency` (role) | KERNEL | Role identity conditional invariance | Roles indistinguishable | — |
| `activate_motifs` | KERNEL | 14-motif computation per tick | No motif selection | — |
| `select_action` + blend | KERNEL | Top-2 blended action selection | No action choice | — |
| `motif_action_priors` (role) | KERNEL | Per-role action weighting | Motif-action mapping collapses | — |
| `pressure_sensitivity` (role) | KERNEL | Motif activation scaling | No role pressure response | — |
| `affordance_pack` (role) | KERNEL | Available action gating | Actions blocked | — |
| `climate_sensitivity` (role) | SUPPORT | Crowd climate → pressure scaling | Reduced crowd responsiveness | — |

---

## 3. World layer — crowd + rumor + spatial

| Component | Class | Primary contribution | Removal cost | X-pipe? |
|---|:-:|---|---|:-:|
| `CrowdState` | KERNEL | Crowd-level shame_climate, blame, alignment | No crowd dynamics | — |
| Rumor registry + spawn | KERNEL | Propagation + decay | No rumor mechanism | — |
| Rumor amplification (crowd → agent) | KERNEL | Pressure relay | Agent pressure breaks | — |
| **Phase 2a forgiveness loop** | **KERNEL** | Universal recovery channel (3/3 scenarios) | Cycles collapse, shame ceiling saturation | — |
| ↳ Phase 2a crowd-layer sub-block | SUPPORT | Recovery-depth amp + cycle-rate dampener (scenario-dep) | Reduced depth, faster cycles | — |
| ↳ Phase 2a agent-layer sub-block | KERNEL | Cycle mechanism (shame decrement) | Cycles → 0 | — |
| ↳↳ Shame decrement channel | KERNEL | Cycle mechanism (necessary) | Cycles → 0 | — |
| ↳↳ Guilt decrement channel | SUPPORT | Amplifying; guilt-only insufficient | Reduced recovery depth | — |
| ↳↳ Fear decrement channel | SUPPORT | Amplifying; fear-only insufficient | Reduced recovery depth | — |
| Spatial registry | KERNEL | Location fields → pressure inputs | Pressure generation fails | — |

---

## 4. Agent state fields (motif-coupled)

| Field | Class | Coupling path |
|---|:-:|---|
| `shame.self`, `shame.public_group` | KERNEL | → shame_exposure pressure, Phase 2a target |
| `guilt.primary_focus`, `guilt.self` | KERNEL | → confess, seek_repair, grieve motifs |
| `fear` | KERNEL | → withdraw, conceal motifs |
| `grief` | KERNEL | → grieve, weep motifs |
| `hope` | KERNEL | → confess, seek_repair, remain_present motifs |
| `anger` | SUPPORT | → confront motif |
| `love` (per target) | SUPPORT | → remain_present motif |
| `loyalty` (per target) | SUPPORT | → assert_loyalty, remain_present |
| `awe` | **INERT (MicroWorld)** | NOT read by any motif; narrator-only | CROSS-PIPELINE |
| `confusion` | SUPPORT | Narrative + some motif coupling |
| `resolve` (slow) | CONTEXTUAL | State initial but not motif-read |
| `doubt` (slow) | CONTEXTUAL | Narrative only |

---

## 5. Agent state fields (narrative-only, INERT in MicroWorld)

| Field | Status | Downstream consumers | Removal blockers |
|---|:-:|---|---|
| `awe` | INERT (Iter 78 ablation) | narrator | state-pack loader |
| `moral_injury` | INERT (Iter 89 static) | latent_drive (v1.0), narrator, trajectory | state-pack + v1.0 pipeline |
| `identity_shift` | INERT (Iter 89 static) | latent_drive, narrator, trajectory | same |
| `trust_scar` | INERT (Iter 89 static) | latent_drive, slow_recovery (unwired), trajectory | state-pack + v1.0 |
| `event_trauma` | INERT (Iter 89 static) | latent_drive, slow_recovery (unwired), trajectory | state-pack + v1.0 |
| `breach_count` | INERT (Iter 89 static) | trajectory only | trajectory logging |

All 6 fields are CROSS-PIPELINE: removing from AgentState would break
state-pack JSON loading, `rendering/narrator.py`, `io/trajectory.py`,
and `core/latent_drive.py` (v1.0 infrastructure).

Cannot be deleted in freeze; classified as RESERVE (kept for future
v1.0 activation or narrator-layer wiring).

---

## 6. Events registry (engine/world/event_registry.py)

### 6.1 Active contract (both produced and consumed)
- `forgiveness_emitted` — spawned by confess action, read by confess motif
- `public_confession` — spawned by confess action, read by confess motif

**Active contract size: 2** (post-Iter-51 audit).

### 6.2 Produced seed + action events (no motif consumers in current pipeline)
- `public_accusation` — seed event with Phase 1 handler (raises blame)
- `guard_approaches` — seed event with Phase 1 handler (authority)
- `shame_repair` — seed event (spawn forgiveness rumor)
- `role_transition` — seed event (role blend)
- `public_denial` — deny action
- `visible_grief` — weep action
- `visible_withdrawal` — withdraw action
- `discussion_emitted` — discuss action
- `public_devotion` — pray action
- `public_loyalty` — assert_loyalty action

### 6.3 DORMANT seed events (registered but not consumed)
- `prayer_invitation` — Iter 77 confirmed
- `miracle_witnessed` — Iter 77 confirmed

### 6.4 LEGACY V3 events (kept for cross-pipeline compat)
25 event IDs in `LEGACY_V3_EVENTS` frozenset, consumed by orphan
motif branches retained for v3 PersonV3Loop. Not spawned by
MicroWorld.

---

## 7. Rules (engine/rules/)

| Module | Class | Status |
|---|:-:|---|
| `base.py` (RuleEngine) | SUPPORT | v1.0 infrastructure; not used in MicroWorld |
| `physical.py` | SUPPORT | RuleEngine-gated |
| `emotional.py` | SUPPORT | RuleEngine-gated |
| `social.py` | SUPPORT | RuleEngine-gated |
| `temporal.py` | SUPPORT | RuleEngine-gated |
| `inhibitor.py` | SUPPORT | RuleEngine-gated |
| `slow_recovery.py` | **DORMANT** | Defined but not imported; would update trust_scar/event_trauma |

MicroWorld does NOT use RuleEngine. Rules files exist for v1.0 /
simulation infrastructure but aren't part of current B-direction
MicroWorld loop.

---

## 8. Previously reclassified INERT fields

| Field | Ledger class | Ablation evidence |
|---|:-:|---|
| `authority_vigilance` (field) | INERT | Pre-Iter-50 audit |
| `recovery_bias` (persona profile) | INERT | Iter 62: bit-identical 50× param range |
| `relation_bias` (persona profile) | INERT | Iter 63 |

---

## 9. Component classification totals (post Iter 89)

| Category | Count | Examples |
|---|:-:|---|
| KERNEL | 11 | motif_tendency, activate_motifs, Phase 2a agent-layer, CrowdState, rumor, shame decrement, spatial, etc. |
| CONDITIONAL KERNEL | 0 | (Phase 2a was here; elevated to KERNEL at Iter 66) |
| SUPPORT | 8 | Phase 2a crowd-layer, guilt/fear decrements, climate_sensitivity, etc. |
| CONTEXTUAL | 2 | resolve, doubt |
| INERT (MicroWorld) | 9 | authority_vigilance, recovery_bias, relation_bias + 6 narrative state fields |
| DORMANT | 3 | prayer_invitation, miracle_witnessed events + SlowStateFieldRecoveryRule |
| CROSS-PIPELINE | 25+ | LEGACY_V3_EVENTS + 6 narrative state fields + rules modules |

---

## 10. Freeze component audit checklist (for Step D)

For Step D (Inert / Reserve Audit), the following are candidate
targets for formal empirical re-audit:

### Category 1: Confirmed INERT via static analysis (Iter 89)
Status: ready for RESERVE classification.
- `moral_injury`, `identity_shift`, `trust_scar`, `event_trauma`, `breach_count`
- Recommendation: empirical ablation confirmation (inject extreme values,
  measure zero delta) to complete catalog.

### Category 2: Confirmed INERT via ablation (Iter 62, 63)
Status: ready for RESERVE or REMOVE classification.
- `authority_vigilance`, `recovery_bias`, `relation_bias`
- Recommendation: check cross-pipeline compat; if v1.0 dormant, consider REMOVE.

### Category 3: DORMANT events (Iter 77)
Status: ready for REMOVE or RESERVE.
- `prayer_invitation`, `miracle_witnessed`
- Recommendation: either wire coupling (lifts status) or REMOVE from
  SEED_EVENTS + sacred scenario (explicit narrative-only annotation).

### Category 4: DORMANT rule (Iter 89 discovery)
Status: RESERVE or REMOVE.
- `SlowStateFieldRecoveryRule`
- Recommendation: if v1.2 plans to wire, keep as RESERVE. Otherwise REMOVE
  or annotate as "v1.2 future infrastructure."

### Category 5: Other candidates
- `climate_sensitivity` — was INERT, reclassified SUPPORT. Re-audit?
- `blend_power` — SUPPORT, is 2.0 optimal?
- Legacy v3 orphan motif branches — retained CROSS-PIPELINE, could be
  partitioned (keep for v3, remove from MicroWorld motif activator).

---

**End of Freeze Component Classification. Referenced by
INERT_RESERVE_AUDIT.md (Step D) for empirical confirmation.**
