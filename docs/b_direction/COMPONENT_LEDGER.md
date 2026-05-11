# WITNESS B-Direction — Component Ledger

**Date:** 2026-04-24 (Iter 52)
**Purpose:** Single source of truth for every engine component's role.
Prevents classification drift (Iter 37 M8 revealed that Iter 27
LOW-EFFECT audit re-needed validation after D-flow kernel matured).

**Use:** When considering a change (remove/extend/refactor), check
this ledger first. If the target is KERNEL, changes require
validation probes across all 6 §15 conditions. If INERT, changes
are low-risk.

---

## Classification scheme

| Category | Meaning | Change risk |
|---|---|---|
| **KERNEL** | Removal collapses ≥1 of C_propagating / conditional invariance / D-flow | high |
| **CONDITIONAL KERNEL** | Kernel for specific scenario class (e.g., transitions) | medium-high |
| **SUPPORT** | Amplifies kernel or scenario-specific contribution | medium |
| **CONTEXTUAL** | Present and observable, limited downstream effect | low |
| **INERT** | No measurable downstream effect (lint-silent) | low |
| **DEPRECATED** | Marked for removal after validation | variable |

---

## 1. Engine Motif Layer

### motif_tendency (role field)
- **Category:** KERNEL
- **Location:** `engine/population/role_cluster.py` (10 roles)
- **Role:** Per-role baseline biases for 8 motifs (0-2 scale).
- **Keep reason:** Iter 20 confirmed motif_tendency + pressure_sensitivity
  + affordance_pack carry conditional invariance (3.83× effect).
- **Primary contribution scenarios:** all; especially cross-scenario
  role identity tests (Iter 17).
- **Removal loss:** conditional invariance collapses; agent roles become
  indistinguishable.
- **Uncertainty:** none significant.

### motif activator (`activate_motifs`)
- **Category:** KERNEL
- **Location:** `engine/persona/motif.py`
- **Role:** Computes 8 motif activations from state + pressures + events
  + profile, returns top-2.
- **Keep reason:** Foundation of action selection. Iter 34 M6 revealed
  events_recent path was 30-iter dead; Iter 51 audit locked 2 active
  contract events.
- **Primary contribution scenarios:** all.
- **Removal loss:** no agent decision possible.
- **Uncertainty:** `_confess` and `_seek_repair` still check 4 legacy v3
  events (eye_contact, forgiveness_offered, primary_figure_suffering_
  visible, restoration_moment) that MicroWorld never emits. These
  branches are dormant but harmless — see Iter 51 LOOP_ITER_51.md.

### quadratic top-2 blend (`select_action`)
- **Category:** SUPPORT
- **Location:** `engine/persona/selector.py`
- **Role:** Blends top-2 motifs quadratically (act^2 weighting) before
  action sampling. Reduces top-2 spillover dilution.
- **Keep reason:** Iter 3-era tuning improved action selection
  sharpness. Not singularly driving any finding.
- **Removal loss:** motif-to-action mapping becomes linear blend,
  likely mild divergence loss.
- **Uncertainty:** no recent validation probe on the quadratic-vs-linear
  choice.

---

## 2. Persona Profile Fields

### pressure_sensitivity
- **Category:** KERNEL
- **Location:** `engine/persona/profile.py`
- **Role:** Per-role response scaling for 8 pressure types (0-2).
- **Keep reason:** Iter 20: conditional invariance survives weak
  priors (3.78×), attributing effect to this field + motif_tendency +
  affordance.
- **Primary contribution scenarios:** all; driver of F4 cross-topology
  JS (Iter 22).
- **Removal loss:** roles respond uniformly to pressures; invariance
  fails.
- **Uncertainty:** none significant.

### motif_action_priors
- **Category:** CONDITIONAL KERNEL
- **Location:** `engine/persona/profile.py` + `engine/population/role_cluster.py`
- **Role:** Maps motif → action probability distribution.
- **Keep reason:** Iter 7: transition-triggered 21× action_JS effect
  depends on role-overridden priors. Iter 19 revealed standalone
  scenarios don't use role priors (DEFAULT_PROFILE hardcoded by build
  scripts).
- **Primary contribution scenarios:** transition scenarios only
  (fisher → elite_strategist etc.).
- **Removal loss:** transition-visible role shift drops from 21× to
  2.26× (Iter 20 measured).
- **Uncertainty:** role-specific priors populated for 10/10 roles
  (Iter 11), but build scripts still use DEFAULT priors for
  non-transitioned agents. True impact on standalone scenarios
  minimal.

### recovery_bias
- **Category:** **INERT** (was CONTEXTUAL, reclassified Iter 62)
- **Location:** `engine/persona/profile.py`
- **Role:** Per-role emotion recovery rate modifiers (fear_recovery_
  rate, guilt_decay_rate, grief_tail_strength, confusion_decay_rate,
  trust_restoration_bias).
- **Iter 62 ablation:** values varied 0.1 / 1.0 / 5.0 → **bit-identical
  dynamics** (rise_fall 20/30, peak 9.657, final 3.548, confess=11
  across all 3 conditions). Zero runtime coupling.
- **Status:** dataclass exists, fields are stored + blended +
  validated. NO code reads them for state updates or motif
  activation.
- **Ledger drift note:** Classification CONTEXTUAL → INERT. Previous
  HIGH uncertainty resolved with definitive ablation evidence.
- **Keep reason:** v3 PersonV3Loop content files still populate
  these fields in peter/judas/vangogh JSONs. Removing dataclass
  would break v3 content loading. Retained for cross-pipeline
  compat (similar to orphan consumer branches).

### relation_bias
- **Category:** **INERT** (was SUPPORT, reclassified Iter 63 M18)
- **Location:** `engine/persona/profile.py`
- **Role (intended):** per-role weighting for 4 relational pressures
  (primary_focus_attachment_strength, peer_dependence, authority_
  reactivity, public_exposure_sensitivity).
- **Iter 63 ablation:** varied 0.1 / 1.0 / 2.0 (20× range), also
  compared to archetype values set by scenario builders → **bit-
  identical dynamics** (rise_fall 15/30, peak 9.369, final 4.488,
  confess 9.6 across all 4 conditions).
- **Status:** dataclass exists, stored + blended + validated + MUTATED
  BY SCENARIO BUILDERS per archetype. But NO engine runtime file
  reads the values.
- **Secondary finding:** archetype tuning in accusation / sacred /
  scarcity builder scripts (e.g., "devoted" archetype +0.4 on
  primary_focus_attachment_strength) is COSMETIC.
- **Ledger drift note:** Classification SUPPORT → INERT. Iter 52's
  SUPPORT was speculative; Iter 63 ablation resolves definitively.
- **Implication for Iter 20 Layer 1 claim:** Iter 20 listed
  relation_bias among conditional invariance drivers (with
  pressure_sensitivity + motif_tendency + affordance_pack). Iter 63
  shows relation_bias is NOT part of the mechanism. Layer 1 driver
  set is narrower: pressure_sensitivity + motif_tendency +
  affordance_pack (3 components).
- **Keep reason:** v3 PersonV3Loop content files populate these
  fields; tests reference them for profile comparison. Deletion
  would break cross-pipeline compat and 3 tests.

### affordance_pack (role field)
- **Category:** SUPPORT
- **Location:** `engine/population/role_cluster.py`
- **Role:** Role-specific allowed action set; gates motif → action
  selection.
- **Keep reason:** Contributes to role differentiation alongside
  motif_tendency + pressure_sensitivity (Iter 20 breakdown).
- **Primary contribution scenarios:** scenarios with role-specific
  affordance-gated actions (e.g., draw_sword for soldier).
- **Removal loss:** roles can select any action regardless of type.
- **Uncertainty:** haven't isolated affordance's independent
  contribution.

### climate_sensitivity (role field)
- **Category:** SUPPORT (was LOW-EFFECT, retracted M8 Iter 37)
- **Location:** `engine/population/role_cluster.py`
- **Role:** Per-role scaling coefficient on shame_climate +
  authority_vigilance → agent pressures.
- **Keep reason:** Iter 37 found removal drops sacred D-flow by 13pp.
  M8 retraction: previously LOW-EFFECT classification was wrong post
  D-flow emergence.
- **Primary contribution scenarios:** sacred (largest effect), less
  crisis scenarios.
- **Removal loss:** sacred rise_then_fall 91% → 78% (−13pp).
- **Uncertainty:** may be Sacred-specific; not re-tested post Iter 37.

---

## 3. World Layer (MicroWorld)

### CrowdState (density, alignment, blame, phase)
- **Category:** KERNEL
- **Location:** `engine/world/crowd_dynamics/state.py`
- **Role:** Meso-layer state that carries crisis dynamics (conceal-
  deny cascade via blame concentration).
- **Keep reason:** Iter 17-18 SAME/DIFF bucket classification depends
  on blame state; crisis cascade requires crowd alignment dynamics.
- **Removal loss:** no crisis dynamics possible.
- **Uncertainty:** none.

### shame_climate (memory field)
- **Category:** SUPPORT
- **Location:** `engine/world/crowd_dynamics/state.py`
- **Role:** Slow-decay climate field tracking post-shame world memory.
- **Keep reason:** Iter 31 recovery cascade modulates shame_climate via
  forgiveness rumor. Iter 26 confirmed shame_climate feeds into
  downstream shame_exposure pressure.
- **Primary contribution scenarios:** all crisis scenarios.
- **Removal loss:** recovery dynamics lose their primary handle.
- **Uncertainty:** Iter 43 confirmed decay removal safe; natural
  decay wasn't needed since forgiveness rumor drives reduction.

### authority_vigilance (memory field)
- **Category:** INERT (was LOW-EFFECT, Iter 38 confirmed inert after
  coupling removal)
- **Location:** `engine/world/crowd_dynamics/state.py`
- **Role:** Post-authority-action memory tracking. Raised by
  `authority_suppression` event.
- **Keep reason:** Observability only. No downstream coupling (Iter 38
  removed coupling to physical_threat).
- **Primary contribution scenarios:** none (coupling removed).
- **Removal loss:** none expected.
- **Uncertainty:** candidate for deprecation. Iter 53+ could delete
  field entirely.

### Rumor layer + action→rumor amplification
- **Category:** KERNEL
- **Location:** `engine/world/information/rumor_registry.py`,
  `engine/world/micro_world/world.py` (Iter 3 additions)
- **Role:** Information propagation + 6-action spawn paths (deny,
  confess, weep, withdraw_in_fear, pray, assert_loyalty) feeding
  crowd and agent pressures.
- **Keep reason:** Iter 3 breakthrough: B_reactive → C_propagating
  required this.
- **Primary contribution scenarios:** all crisis + devotion.
- **Removal loss:** flow type collapses to B_reactive.
- **Uncertainty:** low.

### Forgiveness rumor Phase 2a counter-pressure loop
- **Category:** KERNEL (promoted from SUPPORT at Iter 31-32;
  cross-scenario universality confirmed Iter 66)
- **Location:** `engine/world/micro_world/world.py` (Phase 2a in step)
- **Role:** Active forgiveness rumors reduce crowd blame + alignment
  + shame_climate per tick, AND reduce agent shame/guilt for
  target_role.
- **Keep reason:** Enables autonomous D-flow cascade (60-96% rise_
  then_fall rates Iter 36). Iter 66 further revealed this is the
  **sole recovery channel** across 3/3 tested scenarios
  (accusation, scarcity, sacred); ablation produces identical
  saturation collapse (final shame = 10.0 ceiling) in all three.
- **Primary contribution scenarios:** all crisis scenarios producing
  Arc C. Cross-scenario verified (Iter 66).
- **Removal loss:** Arc C disappears AND recovery itself dies across
  all 3 scenarios. Cycles collapse to 0 reversals/agent, shame locks
  at ceiling 10.0, confess events explode 3-5x without reducing
  accumulated shame. Structurally load-bearing.
- **Uncertainty:** low; bootstrap-validated + cross-scenario
  ablation-validated. Remaining: whether a 4th scenario with
  fundamentally different action topology (no confess) would
  decouple.
- **Sub-component decomposition (Iter 67):**
  - **Agent-layer sub-block** (`world.py:192-220`):
    KERNEL. Per-agent shame/guilt/fear decrements. Necessary and
    sufficient for cycle existence (C_agent_only rev=3.10 vs
    baseline rev=3.67). Ablation → 0 reversals in accusation.
    **Field decomposition (Iter 71 + 72 refinement):**
    - shame decrement channel: **structurally necessary**.
      Shame-only rev=1.80; guilt-only rev=0; fear-only rev=0.
    - guilt + fear decrement channels: amplifying but not
      sufficient alone.
    - **Magnitude regime (Iter 72 + 73 refined)**:
      Shame-multiplier dose-response is sigmoid + secondary rise.
      - mul < 0.05: rev=0 (suppressed, final stuck at ceiling).
      - mul 0.05-0.15: emergence zone (rev 0.2 → 2.63).
      - mul 0.20-0.40: **local plateau** (rev=3.17; Iter 72
        "saturated regime" confirmed here).
      - mul 0.80: secondary rise (rev=5.17, final=3.61).
      Production value 0.4 sits at plateau edge, conservative
      choice. "Channel presence necessary" confirmed (Iter 71 C
      and Iter 73 mul=0 both give rev=0). M20 retraction holds:
      within 0.2-0.4 magnitude has no effect, but beyond that,
      magnitude matters again.
  - **Crowd-layer sub-block** (`world.py:173-191`):
    SUPPORT. Crowd-level blame/alignment/shame_climate decrements.
    Alone produces 0 reversals (B_crowd_only matches full ablation).
    **Dual-role modulator (Iter 68):**
    (i) Recovery-depth amplifier: +2.33 / +7.97 / +4.29 units final
    shame reduction in accusation / scarcity / sacred.
    (ii) Cycle-rate dampener: removing crowd-layer raises rev/agent
    by **~0 (accusation, within hash-noise floor)** / +2.85 / +1.24
    in the 3 scenarios (larger in higher-pressure scenarios). Iter
    69 amp-threshold + PYHASH=0 re-run refined Iter 68 accusation
    finding from "-0.13 dampening" to "A ~ C within noise." In
    scarcity C without crowd-layer, cycles persist at ceiling
    (rev=5.70, final=10.0).

### Spatial registry (visibility / authority_reach / concealment)
- **Category:** KERNEL
- **Location:** `engine/world/spatial/`
- **Role:** Location fields generate pressure inputs (physical_threat,
  shame_exposure via visibility).
- **Keep reason:** Without spatial pressures, crowd dynamics lose
  location-based modulation.
- **Removal loss:** pressure generation collapses.
- **Uncertainty:** none.

---

## 4. Agent State Transitions

### `_update_agent_state_from_world` (pressure → state)
- **Category:** KERNEL
- **Location:** `engine/world/micro_world/world.py`
- **Role:** Per-tick agent state update from world pressures.
- **Keep reason:** Without this, state never accumulates from events;
  motif activation thresholds not reached.
- **Removal loss:** agents stuck in initial state; no dynamics.

### `_apply_action_consequences_to_self`
- **Category:** SUPPORT
- **Location:** `engine/world/micro_world/world.py`
- **Role:** Per-action self-state effects (deny → guilt up, confess →
  resolve up, etc.).
- **Keep reason:** Agent feedback loop primary path.
- **Removal loss:** actions become externally-visible-only, agents
  don't react to their own history.

---

## 5. Role Transition Mechanism (Iter 1)

### `apply_role_transition` + `blend_profile_toward_role`
- **Category:** SUPPORT (CONDITIONAL KERNEL for calling scene)
- **Location:** `engine/population/transitions.py`
- **Role:** Mid-simulation role change with profile blend, state
  preserved.
- **Keep reason:** Enables calling scene's role_transition events +
  fisher→elite transition experiments (Iter 7's 21× action_JS
  finding).
- **Primary contribution scenarios:** calling, Iter 2 distant
  transition.
- **Removal loss:** calling-scene role evolution arc disappears.
- **Uncertainty:** standalone-scenario impact is minimal (priors don't
  apply in build scripts).

---

## 6. Event System (Iter 51 audit)

### ACTIVE CONTRACT events (2)
- `forgiveness_emitted` — confess action → motif activator _confess
- `public_confession` — confess action → motif activator _confess
- **Category:** KERNEL (established by Iter 34 M6 fix)
- **Removal loss:** autonomous D-flow cascade breaks.

### DEAD EMISSIONS (12)
- public_denial, visible_grief, visible_withdrawal, discussion_emitted,
  public_devotion, public_loyalty (from actions)
- public_accusation, guard_approaches, role_transition, shame_repair,
  prayer_invitation, miracle_witnessed (seed events)
- **Category:** CONTEXTUAL (observability only, no motif feedback)
- **Removal loss:** trace/debug visibility; no functional effect.

### ORPHAN CONSUMERS from B-direction view (4, cross-pipeline)
- forgiveness_offered, restoration_moment, eye_contact,
  primary_figure_suffering_visible
- **Category:** **CROSS-PIPELINE** (revised Iter 60; was DEPRECATED)
- **Reason for revision:** Iter 60 investigation revealed these
  events ARE consumed by legacy `engine/person/loop.py`
  (PersonV3Loop pipeline) + rubric critics + 4 tests + v3 content
  files. Motif activator is SHARED between B-direction MicroWorld
  and PersonV3Loop. B-direction never emits them, but v3 scenarios
  do. Removing the consumer branches would break legacy tests.
- **Action:** DO NOT DELETE. Branches remain as legacy v3 hooks.
  Event registry `LEGACY_V3_EVENTS` set continues to document them.
- **Drift history:** Iter 51 flagged as DEPRECATED assuming v3 was
  abandoned. Iter 60 discovered cross-pipeline share. Reclassified.

---

## 7. LOW-EFFECT audit final (Iter 37-43)

| Component | Class | Last validated |
|---|---|---|
| authority_vigilance → pressure coupling | Removed | Iter 38 |
| deny alignment gate | Removed | Iter 42 |
| shame_climate_decay | Removed | Iter 43 |
| authority_vigilance_decay | Removed | Iter 43 |
| climate_sensitivity | Retained (SUPPORT) | Iter 37 M8 |
| authority_vigilance field | INERT (retained for observability) | Iter 38 |

---

## 8. Drift prevention rules

1. **No silent reclassification.** Any component's category change
   must be recorded in this ledger with iter reference.
2. **Test new KERNEL additions** before promoting. Ablation probe
   required.
3. **DEPRECATED components** are candidates for Iter N+1 removal.
4. **INERT components** must have matching tests confirming inertness
   (fail loud if downstream coupling re-enabled without reclassification).
5. **New events** go through event_registry.py (Iter 51 lint gate).

---

## 9. Uncertain items pending validation

High uncertainty — ablation not performed:
- `recovery_bias` (persona profile field)
- `relation_bias` (persona profile field) — isolated contribution
- Quadratic top-2 blend coefficient

Medium uncertainty:
- Whether legacy v3 consumer branches in motif activator cause any
  noise (currently benign; could become bugs if v3 events re-added).

---

## 10. Summary counts (post-Iter 52)

| Category | Count |
|---|---:|
| KERNEL | 9 (motif_tendency, motif activator, pressure_sensitivity, CrowdState, rumor + amplification, Phase 2a forgiveness loop, spatial, state transitions, active contract events) |
| CONDITIONAL KERNEL | 1 (motif_action_priors) |
| SUPPORT | 5 (quadratic blend, affordance_pack, climate_sensitivity, shame_climate, action consequences, role transition) |
| CONTEXTUAL | 1 (dead emissions) |
| INERT | 3 (authority_vigilance field, recovery_bias, **relation_bias**) |
| **CROSS-PIPELINE** | **1 (4 legacy v3 consumer branches shared with PersonV3Loop; was DEPRECATED, reclassified Iter 60)** |

**9 KERNEL components identified. Any of these removed → finding
regression expected.**

---

## 11. State field RESERVE formalization (Iter 179, Step B1 directive)

Per `WITNESS_INTERNAL_BRANCH_DECISION_AND_NEXT_STEPS.md` Step B1, the 5
RESERVE state fields below are **formally classified RESERVE** based on
Iter 89 grep audit + Iter 162 PYHASH N=15 ablation.

**Canonical reference:** `STATE_FIELD_STATUS.md` (per-field details).
**Terminology cross-doc**: state-field schema axis (ACTIVE/RESERVE) is **orthogonal** to mechanism-wiring axis (WIRED/CAUSALLY ACTIVE/DECORATIVE) used in `SACRED_STATUS_NOTE.md`. See `STATE_FIELD_STATUS.md` §1.2 for alignment matrix (added 2026-04-28).

| Field | Status | Tags | Future reactivation |
|---|---|---|---|
| moral_injury | RESERVE | unwired, latent-infra, doc-only | v1.2 SlowStateFieldRecoveryRule OR v1.0 LatentDrive |
| identity_shift | RESERVE | unwired, latent-infra, doc-only | same as moral_injury |
| trust_scar | RESERVE | unwired, latent-infra, slow-recovery-infra | v1.2 SlowStateFieldRecoveryRule (rule already defined for this field) |
| event_trauma | RESERVE | unwired, latent-infra, slow-recovery-infra | v1.2 SlowStateFieldRecoveryRule (rule already defined) |
| breach_count | RESERVE (lowest priority) | unwired, doc-only | v1.2 trauma counter (no candidate rule yet) |

### 11.1 Awe reclassification (Iter 162 finding)
**awe** was previously listed RESERVE in Iter 89 audit but Iter 162 PYHASH
N=15 ablation found Δ shame = +1.73 (non-zero). Iter 123 had identified awe
as load-bearing in sacred contexts via aux pathway.

**Reclassification:** awe → **ACTIVE (conditional, sacred-context)**.
NOT in RESERVE list.

### 11.2 SlowStateFieldRecoveryRule
- **Defined:** `engine/rules/slow_recovery.py`
- **Imported:** nowhere
- **Invoked:** nowhere
- **Status:** RESERVE (slow-recovery-infra)
- **Future reactivation condition:** v1.2 phase work post-branch decision

### 11.3 Removal policy
**DO NOT REMOVE** any RESERVE item. Removal would break:
- Pydantic schema (state fields)
- Narrator render dependencies
- Trajectory log format
- v3 PersonV3Loop test compatibility (~5-10 tests)

REMOVE_CANDIDATE items (prayer_invitation, miracle_witnessed dormant
events) require Lee decision per `INERT_RESERVE_AUDIT.md` §2.1.

### 11.4 Profile fields (recovery_bias, relation_bias)
Already classified INERT in §2 above. Cross-pipeline RESERVE for v3
content loading. No change in this iter.

### 11.5 Updated summary count
| Category | Count |
|---|---:|
| KERNEL | 9 (unchanged) |
| CONDITIONAL KERNEL | 1 (unchanged) |
| ACTIVE (conditional) | +1 (awe, formerly listed INERT) |
| SUPPORT | 5 (unchanged) |
| CONTEXTUAL | 1 (unchanged) |
| INERT (observability) | 3 (unchanged: authority_vigilance, recovery_bias, relation_bias) |
| **RESERVE state fields** | **5 (NEW formalized: moral_injury, identity_shift, trust_scar, event_trauma, breach_count)** |
| RESERVE rule | 1 (SlowStateFieldRecoveryRule) |
| REMOVE_CANDIDATE events | 2 (prayer_invitation, miracle_witnessed; Lee gate) |
| CROSS-PIPELINE | 1 (4 legacy v3 consumer branches) |

---

**End of ledger v1.1 (Iter 179 Step B1 update; v1 was Iter 52).**

Update history:
- v1 (Iter 52): initial ledger
- v1.1 (Iter 179): §11 state field RESERVE formalization per directive Step B1
