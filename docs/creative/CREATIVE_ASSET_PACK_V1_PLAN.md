# Creative Asset Pack v1 Plan — Branch C Case S 분기

**Date**: 2026-04-30
**Source**: `docs/b_direction/CREATIVE_ASSET_PACK_V1_PLAN_DRAFT.md` (Lee draft) + Branch C lock decision
**Trigger**: Branch C external eval = **5/5 PASS** = Case S
**Renderer status**: Cycle 7 freeze, no Cycle 8

---

## 0. Decision

Branch C external validation strong (5/5 PASS) → 내부 structure testing에서 *curated asset packaging*으로 이동. Renderer는 Cycle 7에서 freeze 유지.

이 의미는:
- 모든 generated narrative가 public-ready라는 의미 *아님*
- *Configuration-sensitive dynamics가 readable*하다는 외부 validation 받음
- *Curated 일부*만 selection / cleanup / packaging

---

## 1. Asset pack 핵심 원칙 (Lee directive §1)

> Similar scenario pressure can diverge into recovery, saturation, partial, mixed, or low-activity outcomes depending on configuration.

이걸 *prediction*으로 frame 안 함. *Generative narrative-dynamics demo*로 frame.

---

## 2. Include first (4 candidates)

### A. P6 MIXED scarcity ⭐
- **Why**: 가장 강력한 split outcome 예시 (cohort-level divergence visible)
- **Use**: flagship narrative
- **Source**: `docs/story/generated/P6_narrative_ko.txt`

### B. P10 REC accusation
- **Why**: clean recovery after accusation, sharpness coexistence (Cycle 4 Patch G 효과)
- **Use**: recovery contrast 자료
- **Source**: `docs/story/generated/P10_narrative_ko.txt`

### C. P_CV_01 MIXED accusation
- **Why**: 같은 pressure (accusation) → divergent cohort outcome (cast variation 효과)
- **Use**: configuration-dependence explainer
- **Source**: `docs/story/generated/P_CV_01_narrative_ko.txt`

### D. Scarcity Trilogy modal (3-act)
- **Why**: nonmonotonic dynamics 가장 strong demo (1/2/3 accusations → SAT/SAT/REC)
- **Use**: explainer / blog / presentation asset
- **Source**: `outputs/creative_demo/scarcity_trilogy_modal.txt`

---

## 3. Hold or edit (internal only)

### P9 SAT scarcity
- **Problem**: saturation tone 개선됐지만 still slightly report-like (Lee v3 verdict)
- **Action**: manual edit only (no renderer patch — Cycle 7 freeze)
- **Use if edited**: SAT contrast 보조 자료

### P_PV_09 LOW_ACTIVITY
- **Problem**: bad → flat 개선됐지만 hook 약함
- **Action**: keep as internal demo of "event that fails to become event"
- **Use**: 내부 reference만, public 아님

---

## 4. Required cleanup (publication 전 필수)

### 4.1 Patch markers 제거

각 narrative 본문에 *patch annotation* 잔재 점검:
- `[Cycle X]` 또는 `[Patch Y]` 마커
- 볼드 patch explanation (`**[Cycle 3 ...]**`)
- 괄호 implementation note (`(scenario × MIXED ...)`)

→ 해당 자국 검출은 grep으로 확인. 검출 시 narrative file 직접 edit.

### 4.2 Repeated closer 감소 (Lee v2 약점 #1 + Cycle 7 motif closing 후)

다음 단어가 *연속 narrative 끝*에 반복되면 *cleanup 후보*:
- "결" (motif closing line의 핵심 단어)
- "거리" (장소 모티프)
- "흔적" (잔향 모티프)
- "다음 시각" (시간 진행 표현)

→ 1-2개 narrative만 cleanup 대상. 모든 narrative 일괄 제거 안 함 (style 통일 필요).

### 4.3 Interpretive caption 추가

각 asset 위에 짧은 captions:
- **Scenario**: "scarcity / accusation / sacred"
- **Configuration difference**: e.g., "1 accusation vs 2 vs 3 (Trilogy)"
- **Observed outcome**: "MIXED — 빈민가 vs 곡물 창고 split"
- **Why it matters**: "같은 pressure 다른 cohort routing → different outcome class"

### 4.4 Methodology caveat (BRANCH_C_LOCK_DECISION.md §6 verbatim)

각 asset 또는 README 마지막에:

> "single-seed external readability eval supports configuration-sensitive outcome divergence; magnitude requires cross-seed confirmation."

---

## 5. Pack structure (Lee directive §5)

```
WITNESS Creative Asset Pack v1 (TBD location: docs/creative/asset_pack_v1/)
├── 00_README.md                              # 전체 소개 + caveat
├── 01_flagship_mixed_scarcity.md             # P6 + caption
├── 02_recovery_accusation.md                 # P10 + caption
├── 03_mixed_accusation_configuration.md      # P_CV_01 + caption (cleanup 후)
├── 04_scarcity_trilogy_modal.md              # Trilogy 3-act + meta
├── appendix_method_caveat.md                 # single-seed limitation 상세
└── internal_hold/                            # public 아님
    ├── p9_sat_scarcity_needs_manual_edit.md
    └── p_pv_09_low_activity_reference.md
```

---

## 6. Public framing rules (Lee directive §6)

### 6.1 Use phrases

- "narrative dynamics experiment"
- "configuration-sensitive narrative dynamics"
- "generative simulator"
- "scenario pressure / outcome class divergence"

### 6.2 Avoid phrases

- "predicts human behavior"
- "proves moral causality"
- "simulates real society"
- "AI sociology engine"

→ 이는 CLAUDE.md ABSOLUTE Rule #5 (terminology 과장 금지)와 일관.

---

## 7. Immediate next steps

1. ✅ `BRANCH_C_LOCK_DECISION.md` (이미 작성)
2. ✅ 이 plan doc finalize (`docs/creative/CREATIVE_ASSET_PACK_V1_PLAN.md`)
3. **다음 LOOP**:
   - Patch marker grep 검사 (4 candidate narratives)
   - 발견 시 narrative file 직접 cleanup
   - asset_pack_v1/ 폴더 + README + 4 asset md + caveat appendix 작성
4. **그 후**:
   - Lee 검토 → 공개 여부 결정
   - 공개 시 *single-seed limitation* 명시

---

## 8. Renderer freeze 유지 명시

Lee directive §0 + Type E:

- **Renderer Cycle 8+ 진행 안 함**
- Cycle 7에서 freeze
- 자율 rollback 안 함 (별도 directive 필요)
- Asset pack 작업은 *curation*만 — renderer code 무수정

---

## 9. Versioning

| Version | Date | Note |
|---|---|---|
| Lee draft | 2026-04-30 | `docs/b_direction/CREATIVE_ASSET_PACK_V1_PLAN_DRAFT.md` |
| **v1 (this finalize)** | **2026-04-30** | **Case S 분기 trigger 후 정식화** |
