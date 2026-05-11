# Story Failure Modes — Baseline 12 분류

**Date**: 2026-04-28
**Source**: `STORY_SET_BASELINE_REVIEW.md` (Phase 6) + 12 baseline stories 직접 inspection
**Phase**: NEXT_STEPS Stage 1.3
**Purpose**: 실패 유형을 4 카테고리 (Extraction / IR / Renderer / Surface gap)로 분류해 다음 수정 위치 명확화.

---

## 1. 분류 체계 (NEXT_STEPS §2 Step 3)

| 유형 | 정의 | 수정 위치 |
|---|---|---|
| **A — Extraction** | annotated probe parser 오류 | `extract_story_features.py` |
| **B — Narrative IR** | 의미 atom 분류/임계값 오류 | `build_narrative_ir.py` |
| **C — Renderer** | 한국어 문장 생성/조사/문체 | `render_story_ko.py` |
| **D — Surface gap** | annotated field 자체에 정보 부족 | annotated probe spec 또는 IR 확장 |

---

## 2. 발견된 실패 유형

### 2.1 유형 A — Extraction (현재 0건)

12 baseline 모두 final_summary / primary_pressure / cohort_outcomes / event counts / world dynamics 정확히 추출됨. v4 top_blame_target 100% 추출.

**상태**: 통과. 추가 fix 불필요.

### 2.2 유형 B — Narrative IR

#### B-1. blame_strong 임계값이 약하게 잡힘 — MEDIUM

P3/P8/P10 (accusation 시나리오) 모두 `crowd_blame_peak ~ 1.0` 부근에서 `blame_strong: true` 분류. 그러나 P3의 final blame은 0.85, P10은 0.95로 실제 약함. 결과적으로 모두 같은 "비난은 빠르게 한곳으로 모였다" 문장 사용.

**진단**: `blame_strong`만으로는 강도 미세 차이를 잡지 못함. `blame_intensity_band` (low/mid/high)로 3단계 분류 필요.

**수정 위치**: `build_narrative_ir.py` `build_pressure_arc` — `blame_strong: bool` → `blame_band: str` ("absent" / "weak" / "strong" / "dominant").

#### B-2. confession_volume threshold가 시나리오별로 다른 의미 — LOW

`confessions_count`:
- scarcity probes: 60~210 (high)
- accusation probes: 80~150 (high or moderate)
- sacred probes: 30~70 (moderate or low)

같은 "100 confessions"가 sacred에서는 많고 scarcity에서는 평균. 시나리오별 정규화 없이 `≥100 → high`로 처리해 sacred RECOVERY가 "고백은 멈추지 않고 이어졌다" 출력 못 함.

**진단**: confession volume을 scenario-normalized로 처리하거나, 별도 atom으로.

**수정 위치**: `build_pressure_arc`에 `pressure_type` 받아 시나리오별 임계값.

#### B-3. world_aftereffect의 shame_residue_count가 saturation cohort 수에만 의존 — LOW

P3 (3 cohorts, 2 saturated)와 P12 (3 cohorts, 1 saturated)의 aftereffect가 동일 강도로 출력. 실제로는 saturated cohort의 *비율*이 차이를 만들어야 함.

**수정 위치**: `build_world_aftereffect`에 `shame_residue_ratio`(saturated/total) 추가.

### 2.3 유형 C — Renderer

#### C-1. 조사 오류 — FIXED Phase 7

P3: "제자을(를)" → "제자를"로 수정 완료. `josa()` 함수 도입.

#### C-2. 중복 복수 표시 — FIXED Phase 7

P3: "거리의 사람들들" → "거리의 사람들"로 수정 완료. `role_plural_ko()` 함수 도입.

#### C-3. P4 = P5 완전 동일 — MEDIUM (loop C variation 후속)

같은 시나리오 (sacred) + 같은 outcome (RECOVERY) + 같은 cohort 구성 → 100% 동일 텍스트 출력.

**진단**: 현재 renderer는 IR 결정자가 키만 보고 결과 변동 없음. cohort 수 / agent 수 / 미세한 metric 차이가 텍스트에 반영 안 됨.

**수정 위치**: `render_story_ko.py`에 IR-derived hash 또는 micro-feature 기반 문장 변주. NEXT_STEPS §3 loop C 영역.

#### C-4. SATURATION 시 중복 문장 — LOW

P3 narrative 5단:
- 4단 (turning_point): "더 이상 올라갈 수 없는 곳까지 무거움이 차올랐다."
- 4단 (outcome 이어붙임): "사람들은 자리에 머물렀다. 어떤 자리는 시간이 흘러도 풀리지 않았다."

→ 의미 중복. turning_point + outcome이 같은 4단에 결합되며 redundant.

**수정 위치**: `render_narrative` 4단에서 turning과 outcome 합칠 때 변주 또는 turning 생략.

#### C-5. 문단 길이 편차 큼 — LOW

P4/P5 (sacred RECOVERY, 354자/544자) vs P6 (MIXED scarcity, 644자/1078자).

sacred 시나리오에서 has_authority 무시 정책 때문에 짧음. sacred 자체 묘사 단락 추가가 필요.

**수정 위치**: `_opening` sacred branch에 추가 문장.

### 2.4 유형 D — Surface gap

#### D-1. cohort 위치 (L1/L2/L3)의 의미가 텍스트에 안 옮겨짐 — MEDIUM

P6 (MIXED scarcity): L1=granary, L2=poor_quarter, L3=marketplace. 각 cohort에서 L1 saturation, L2 recovery, L3 saturation. 이야기에서는 단순히 "한쪽에서는 회복… 다른 자리는 굳었다"로 위치 의미 미사용.

**진단**: extraction에서 location ID는 추출하지만 location → semantic mapping 없음. annotated probe도 location ID만 노출.

**수정 후보**:
- annotated probe v5에 location semantic (granary/marketplace 등) 추가
- 또는 IR에서 location ID + scenario type → semantic location name 추론

**위치**: annotated probe spec 확장 또는 `build_narrative_ir.py` location semantic 매핑 추가.

#### D-2. authority vigilance peak vs final 차이가 안 보임 — LOW

P6: authority_vigilance peak 0.42 → final 0.25 (감소). P3: peak 0.40 → final 0.36 (지속). 둘 다 IR에서 `authority_residue: true` 동일 처리.

**진단**: peak vs final 차이가 의미 atom에 반영 안 됨. 감소 = 시간 흐름이 권위 시선을 풀었다. 지속 = 풀리지 않았다. 텍스트 차이 가능.

**수정 위치**: `build_world_aftereffect`에 `authority_decay`(peak - final 비교) 추가.

#### D-3. event timing은 추출되지만 미사용 — LOW

key_events_sample (첫 30개 events)이 extraction에 들어있지만 IR에서 사용 안 됨. timing rhythm (early burst / sustained / late)이 텍스트 차이 만들 수 있음.

**수정 위치**: `build_pressure_arc`에 `event_timing_pattern` atom 추가 후 renderer에 매핑.

---

## 3. 우선순위 (Stage 2 renderer 1차 개선 후속)

| Priority | 유형 | 항목 | 수정 위치 |
|---|---|---|---|
| HIGH | B-1 | blame_band (3단계) | build_narrative_ir.py |
| MEDIUM | C-3 | P4=P5 variation | render_story_ko.py |
| MEDIUM | D-1 | location semantic | annotated probe v5 또는 IR |
| LOW | B-2 | scenario-normalized confession volume | build_narrative_ir.py |
| LOW | B-3 | shame_residue_ratio | build_narrative_ir.py |
| LOW | C-4 | turning + outcome 중복 | render_story_ko.py |
| LOW | C-5 | sacred 문단 길이 | render_story_ko.py |
| LOW | D-2 | authority decay 차이 | build_narrative_ir.py |
| LOW | D-3 | event timing rhythm | build_narrative_ir.py |

---

## 4. 분류 결과 요약

| 유형 | 발견 건수 | Status |
|---|---:|---|
| A — Extraction | 0 | 통과 |
| B — Narrative IR | 3 (B-1 medium / B-2 low / B-3 low) | 1차 개선 후속 |
| C — Renderer | 5 (C-1, C-2 fixed; C-3 medium; C-4, C-5 low) | 2 fixed, 3 후속 |
| D — Surface gap | 3 (D-1 medium / D-2, D-3 low) | annotated 확장 후보 |

→ **HIGH priority 1건 (B-1 blame_band)** 은 다음 renderer revision에서 처리. MEDIUM 2건 (C-3, D-1) 도 함께. LOW 5건은 후속 loop.

---

## 5. 후속 cycle 권장

NEXT_STEPS §2 Stage 2.4에서 "renderer 1차 개선" 명시. 이미 Phase 7에서 일부 (조사/복수/길이) 완료. 추가 1차 개선:

**Renderer Revision 1 (지금)**:
- B-1: blame_band 3단계 도입
- C-3: P4/P5 같은 동일-IR 케이스에 micro-variation
- D-1: scenario type → semantic location name

→ `STORY_RENDERER_REVISION_1.md`에 변경 기록.
