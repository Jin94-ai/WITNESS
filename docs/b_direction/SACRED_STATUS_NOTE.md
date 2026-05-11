# Sacred Status Note -- Where the Evidence Actually Points

**Date:** 2026-04-26
**Iteration:** Iter 181 (Step B3 of new directive)
**Status:** Mixed -- partly active, partly decorative
**Directive:** `WITNESS_INTERNAL_BRANCH_DECISION_AND_NEXT_STEPS.md` Step B3

---

## 0. Lee의 원래 지시 (verbatim, H5)

> "B3. sacred decorative suspicion 문서화
> sacred가 지금 genuinely active world process가 아니라 decorative suspect
> 라는 점을 공식적으로 기록한다.
> 이유: 나중에 sacred를 다시 손댈 때 '왜 지금은 보류인지'를 잊지 않도록 하기 위함
> 산출물: docs/b_direction/SACRED_STATUS_NOTE.md"

---

## 1. Honest framing (H4 negative findings discipline)

The directive frames sacred as "decorative suspect, not genuinely active".
**Evidence partially supports, partially contradicts this framing.** Honest
account:

| Sacred component | Evidence | Status |
|---|---|---|
| `prayer_invitation` event handler | Wired Iter 95 (agents +awe +2, crowd dominant=awe) | **WIRED** |
| `miracle_witnessed` event handler | Wired Iter 95 (agents +awe +4, crowd dominant=awe strong) | **WIRED** |
| Late miracle (t=250) recovery effect | Iter 113 ablation: -26.7% recovery if removed | **CAUSALLY ACTIVE** |
| Early miracle (t=10) recovery effect | Iter 113 ablation: +6.7% if removed (≈ noise) | partially redundant |
| Awe-driven aux (shame decay mechanism) | Iter 108: aux fires <1% of horizon ticks | **DECORATIVE** |
| Awe direction-of-effect | Iter 162: injection produces shame INCREASE (+1.73), not DECREASE as designed | **MECHANISM PUZZLE** |
| `awe` field as state | Iter 162: non-zero MicroWorld effect | ACTIVE (conditional) |

**Sacred is mixed**: some components wired and causally active, others
decorative. The directive's "decorative suspect" framing is half-right.

### 1.1 Terminology cross-doc note (NEW 2026-04-28)

Sacred uses a **mechanism-wiring** axis (WIRED / CAUSALLY ACTIVE / DECORATIVE) which is **orthogonal** to the **state-field schema axis** (ACTIVE / RESERVE) used in `STATE_FIELD_STATUS.md` §1 and `COMPONENT_LEDGER.md` §11.

- A mechanism can be WIRED but read a RESERVE field (no effect).
- A mechanism can be CAUSALLY ACTIVE while reading an ACTIVE field.
- A field can be ACTIVE (set by something) but only consumed by DECORATIVE mechanisms.

For full alignment matrix see `STATE_FIELD_STATUS.md` §1.2.

---

## 2. What IS active (with evidence)

### 2.1 Sacred event handlers (Iter 95 wiring)

`engine/world/micro_world/world.py` event handler block:

```python
elif event_id == "prayer_invitation":
    for aid in self._spatial.agents_at(location_id):
        agent.state["awe"] = min(10.0, current_awe + 2.0)
    set_dominant_emotion(crowd, "awe", strength_boost=0.15)

elif event_id == "miracle_witnessed":
    for aid in self._spatial.agents_at(location_id):
        agent.state["awe"] = min(10.0, current_awe + 4.0)
    set_dominant_emotion(crowd, "awe", strength_boost=0.3)
```

These ARE wired. Iter 89 INERT_RESERVE_AUDIT listed them DORMANT but that
audit predates the Iter 95 wiring. **The audit is stale on this point.**

### 2.2 Late miracle causal effect (Iter 113)

Ablation V1 (remove t=250 miracle):
- Recovery rate: 60% → 33% (-26.7% absolute)
- Mean final shame: 3.98 → 4.99

This is the **largest single causal lever** identified in sacred ablation.
Sacred is NOT removable from the recovery dynamics without significant
behavioral change.

### 2.3 awe field non-inert (Iter 162)

PYHASH N=15 injection of awe=8.0 produces Δ shame = +1.73 (vs baseline 5.37).
Direction is unexpected (shame INCREASE not DECREASE) but magnitude is real.

---

## 3. What IS decorative (with evidence)

### 3.1 The aux mechanism (Iter 108)

The originally-designed sacred mechanism was: awe ≥ threshold → aux block
fires → shame decay.

Iter 108 measurement: **aux fires <1% of horizon ticks.**

Comparison (mixed-B 500t):
| Mechanism | Active ticks | Recovery seeds |
|---|---:|---:|
| Aux block | 0-1 | 0-4 |
| Confess actions (Phase 2a trigger) | 153-160 | 1.5x baseline |
| Forgiveness rumor active | 247 | 1.5x baseline |

**Aux is decorative.** The recovery mechanism is Phase 2a forgiveness rumor
(Iter 31 design), which fires regardless of sacred context.

### 3.2 Branch B aux tuning work (Iter 92-103, retracted Iter 107)

Iter 92-103 spent ~12 iterations tuning aux magnitude / threshold / dual-layer.
Iter 107 retraction: those measurement effects were **sampling artifacts of
Phase 2a bimodal distribution**, not aux contributions.

The aux tuning work was real engineering effort spent on a decorative
mechanism. This is the "decorative suspect" framing's strongest evidence.

### 3.3 Awe direction-of-effect puzzle (Iter 162)

Designed pathway (Iter 92-95): high awe → aux → shame decreases.
Measured (Iter 162): high awe injection → shame INCREASES (+1.73).

Possible explanations (untested):
- awe_decay (0.05/tick) brings awe below threshold quickly; aux fires only briefly
- Indirect: high awe → crowd dominant_emotion="awe" → different blame_concentration cascade → more confess events → ... → final shame state
- Test injection (a.state["awe"] = 8.0) doesn't reach the Pydantic field; signal is noise

**This is unresolved.** The mechanism that connects sacred events to recovery
rate is unknown. Iter 113 confirmed the connection is causal (-26.7% effect),
but the pathway is not validated.

---

## 4. Why "decorative suspect" framing is half-right

The directive says sacred is "not genuinely active world process".

**Half-right reading**: aux mechanism is decorative (Iter 108 evidence), so the
**designed** sacred recovery pathway is decorative.

**Half-wrong reading**: sacred event handlers ARE wired (Iter 95) and DO have
measurable causal effect on recovery rate (Iter 113). Sacred is not entirely
decorative; it just doesn't work the way it was designed to.

Better framing: **"sacred is wired and causally active, but the mechanism
connecting events → recovery is unknown / not validated."**

---

## 5. Why pause sacred work now (per directive intent)

Even with the half-right caveat, the directive's reason to pause is sound:

### 5.1 Mechanism validation gap
- Iter 113 ablation shows late miracle = -26.7% effect
- But Iter 108 shows aux is decorative
- So sacred events affect recovery through some OTHER pathway, not the
  designed one
- Working on sacred without knowing the actual pathway = working blind

### 5.2 Branch B closure (Iter 108)
Iter 108 explicitly closed Branch B aux work as decorative. Reopening sacred
work means revisiting that closure, which requires either:
- New evidence the aux pathway is NOT decorative (would need to find why
  Iter 108 measurement was wrong)
- Or new pathway hypothesis (what does sacred event → recovery actually look like?)

### 5.3 awe direction-of-effect puzzle unresolved
Iter 162 found awe injection INCREASES shame. Designed mechanism predicts
DECREASE. Until this is resolved, any sacred mechanism work risks chasing
ghosts.

### 5.4 Phase 2a is sole load-bearing recovery channel (Iter 66)
Phase 2a forgiveness rumor accounts for recovery in all 3 scenarios. If
sacred events affect recovery, they do so by interacting with Phase 2a
(probably indirect: events → awe → ??? → confess actions → forgiveness rumor).
The actual mechanism is several layers removed from "sacred events".

---

## 6. What "reactivating sacred" would look like (when revisited)

Per directive: "나중에 sacred를 다시 손댈 때 '왜 지금은 보류인지'를 잊지 않도록".

When revisiting, the open questions to resolve first:

1. **What pathway connects sacred events to recovery rate?**
   - Hypothesis 1: events → awe → ??? → confess → forgiveness rumor
   - Hypothesis 2: events → crowd dominant_emotion → blame distribution → ?
   - Hypothesis 3: events → social_threat reduction → fear reduction → action mix
   - Probe: trace per-tick awe + confess + forgiveness intensity in V0 vs V1 ablations

2. **Why does awe injection INCREASE shame (Iter 162)?**
   - Hypothesis 1: awe_decay too fast (0.05/tick); aux fires only briefly
   - Hypothesis 2: indirect cascade through crowd state
   - Hypothesis 3: injection method (a.state dict) doesn't reach Pydantic field
   - Probe: instrument awe trajectory + aux trigger count under injection

3. **Is aux truly decorative or only in current parameter regime?**
   - Iter 108 measured aux fires <1% under default rates
   - With different magnitude / threshold, would aux become non-decorative?
   - Probe: parameter sweep on aux_threshold (currently 5.0) and aux_magnitude

4. **Should aux be removed entirely?**
   - If decorative AND no plausible regime makes it non-decorative, remove
   - If decorative BUT plausible regime exists, retain with documented gap
   - Branch B aux retention (Iter 108 closure) is current default

---

## 7. Recovery family options (sacred re-extension)

If a future iter wants to make sacred a "real" recovery family (not via
unknown indirect pathway), the candidates per Iter 161 directive priority 4:

| Recovery family | Status | Gate to enable |
|---|---|---|
| Phase 2a (existing) | ACTIVE | already on |
| Aux awe→shame_decay | DECORATIVE | needs threshold lowering OR awe sustainment |
| Spatial disengagement | BLOCKED (Iter 161) | needs shame_decay rule (kernel gap) |
| Sacred-specific recovery channel | not implemented | would need new event handler + decay rule |

The kernel gap (no shame_decay rule) blocks 5/6 recovery family candidates,
including most sacred-related options. See `KERNEL_GAPS.md` (Step B4 next iter).

---

## 8. Decision: keep sacred wired, do not extend

### Per directive principles

1. **No new mechanism drilling** (§6 forbidden)
2. **Sacred events stay wired** — removing prayer_invitation / miracle_witnessed
   handlers would break Iter 113-validated -26.7% causal effect
3. **Aux mechanism stays decorative** — Iter 108 closure not reopened
4. **awe field stays ACTIVE conditional** — Iter 162 non-inert finding stands
5. **Future revisit gated on**: pathway validation + awe direction-of-effect
   resolution

### What this note formalizes

- prayer_invitation + miracle_witnessed: **WIRED, retain**
- Aux mechanism: **DECORATIVE, retain (decorative-but-harmless)**
- awe field: **ACTIVE (conditional), retain**
- Sacred recovery pathway: **UNKNOWN, do not extend without validation**

---

## 9. What could still be wrong (H4)

### 9.1 Iter 113 ablation noise
Iter 113 used N=15 seeds. -26.7% effect might be inflated by sampling.
Effect could be -15% to -30% with wider CI.

### 9.2 Iter 108 aux measurement scope
Iter 108 measured aux firing rate under default parameters. With different
parameters, aux might not be decorative. The decorative classification is
parameter-conditional.

### 9.3 awe injection caveat (per Iter 162)
If injection didn't reach Pydantic field, the Δ +1.73 finding may be sampling
artifact. Static grep evidence is independent and shows aux pathway exists,
but firing rate is the issue.

### 9.4 Sacred scenario empirical scope
Sacred ablation focused on standalone sacred (Iter 113). Mixed-B (sacred 300t
combined with accusation 200t) may show different dynamics. Iter 108 used
mixed-B for aux measurement; Iter 113 used standalone sacred. Cross-validation
not done.

### 9.5 "Decorative suspect" might still be right after pathway resolution
If pathway investigation reveals sacred → recovery is purely indirect via
Phase 2a (i.e., sacred events trigger more confess actions which trigger
forgiveness rumors which drive recovery), then sacred IS in some sense
decorative — Phase 2a is doing the actual work, sacred is a trigger
amplifier. The Iter 113 "-26.7% effect" would still be real but the
mechanism would be "Phase 2a indirect", not "sacred-specific".

---

## 10. What I did NOT try (H2)

- **Pathway tracing probe**: instrument per-tick awe + confess + forgiveness
  to identify the actual sacred → recovery pathway
- **awe injection via Pydantic AgentState** (Iter 162 caveat resolution)
- **Aux parameter sweep** (test if aux becomes non-decorative under different
  thresholds)
- **Cross-mode sacred ablation** (standalone vs mixed-B)
- **Iter 113 N expansion** (N=30 or N=50 to tighten CI on -26.7%)
- **Engine code changes** (sacred handler removal or aux mechanism deletion)

이유:
- Step B3은 "기록"이지 새 ablation이 아님
- 디렉티브 §6: 새 메커니즘 drilling 금지
- 디렉티브 §6 forbidden: "Phase 2a 추가 drilling, shame multiplier 미세 스윕,
  새 변수 대량 추가" (sacred drilling은 명시 안 됐지만 동일 정신)

---

## 11. Alternate interpretations (H4)

- **"Decorative suspect"가 entire sacred system 의미**: 그러면 evidence와
  대치. Iter 113은 명시적으로 -26.7% effect 확인.
- **"Decorative suspect"가 aux mechanism only**: 그러면 evidence 일치.
  내 해석은 이쪽 (§4 framing 참조).
- **"Decorative suspect"가 Iter 89 audit 기준**: Iter 89 audit는 Iter 95
  wiring 이전. Stale evidence.

내 해석 (§4 framing): aux decorative + sacred events wired-but-unclear-pathway.
Lee 재확인 필요.

---

## 12. References

- `engine/world/micro_world/world.py` — Iter 95 wiring of prayer_invitation,
  miracle_witnessed
- `archive/b_direction_legacy/iter_91_to_119/ITER_95_SACRED_WIRING.md` — wiring spec (archived 2026-04-27)
- `archive/b_direction_legacy/iter_91_to_119/ITER_108_BRANCH_B_CLOSURE.md` — aux decorative finding (archived 2026-04-27)
- `archive/b_direction_legacy/iter_91_to_119/ITER_113_SACRED_ABLATION.md` — late miracle -26.7% effect (archived 2026-04-27)
- `docs/b_direction/INERT_RESERVE_AUDIT.md` §2.1 — Iter 89 stale "DORMANT"
  classification (predates Iter 95)
- `docs/b_direction/ITER_162_INERT_REAUDIT.md` — awe non-inert + direction puzzle
- `docs/b_direction/STATE_FIELD_STATUS.md` §3 — awe ACTIVE (conditional)
- `engine/world/event_registry.py` — event metadata (Iter 95 annotation)
