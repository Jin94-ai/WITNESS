# WITNESS — Creative IP 트랙 전환 + J-Alpha 실행 계획

**Date**: 2026-04-28
**Source directive**: `docs/WITNESS_CREATIVE_IP_TRACK_IMPROVED_DIRECTIVE.md` (Lee)
**Status**: J-Alpha 진행 시작 (8 Steps), J-Beta는 J-Alpha 성공 시에만

---

## 1. 트랙 전환 개요

### 1.1 정체성 변경
- **이전**: 연구 트랙 중심 (paper, validation framework, Branch C cross-seed methodology)
- **이후**: **Creative IP 트랙 우선** — 산출물 중심 (한국어 이야기 텍스트, 1차 타겟 = 소설/웹소설)

### 1.2 핵심 가설
> **같은 세계 조건에서 출발한 5개의 seed가, 사람이 읽었을 때 서로 다른 운명/아크를 가진 한국어 이야기 5편으로 읽힌다.**

이 가설이 **참**이면:
- cross-seed variation = 운명 변주 자산 (statistical weakness 아님)
- selector의 존재 이유 명확
- renderer 개선 방향 분명

이 가설이 **거짓**이면:
- Creative IP 전환 보류
- Research 트랙으로 복귀

### 1.3 1차 타겟
- 첫 IP 형태: **소설/웹소설**
- 드라마/웹툰/게임은 J-Beta 이후

---

## 2. 4-Layer 구조 (유지)

| Layer | 역할 | J-Alpha 구현 수준 |
|---|---|---|
| 1 World Simulation | 엔진 + Branch C cross-seed | 기존 그대로 (변경 없음) |
| 2 Story Unit Taxonomy | Person/Event/World arc 분류 | **Minimal 3개만** (Step 3) |
| 3 Story Selector / Framer | anchor variation bundling | **anchor 5-seed 묶기만** (Step 5) |
| 4 Style-aware Renderer | 한국어 prose 출력 | **3 우선 개선만** (Step 6) |

각 layer는 J-Alpha에서 *최소 동작* 수준으로만 구현. J-Beta에서 일반화.

---

## 3. J-Alpha vs J-Beta 분리

### J-Alpha (now)
- 작은 curated set (10-15 trajectories)
- Peter anchor 1 × 5 seeds + Van Gogh anchor 1 × 5 seeds
- 핵심 가설 1차 증명

### J-Beta (J-Alpha 성공 시에만)
- Full taxonomy (`STORY_UNIT_TAXONOMY.md`)
- 70+ trajectory 라벨링
- selector query API 확장
- cross-seed anchor library
- IP mode 확장 (drama/webtoon/game)

순서: **작은 데모 → 일반화** (반대 아님)

---

## 4. 기존 Phase J 매핑

| 기존 J# | J-Alpha 처리 |
|---|---|
| J1 트랙 전환 공식화 | 유지 (이 문서) |
| J2 renderer 진단 | **앞으로 당김 → Step A1** |
| J3 taxonomy 문서화 | **minimal만** (Step A2) |
| J4 70+ 라벨링 | **J-Beta로 연기** |
| J5 selector 1차 구현 | **minimal만** (Step A4) |
| J6 renderer 개선 | **축소 3 항목** (Step A5) |
| J7 통합 데모 | **5-variation demo로 축소** (Step A6) |
| J8 Lee 검토 | 유지 (Gate 2) |

---

## 5. Lee Gates (J-Alpha 2회만)

### Gate 1 — Renderer 진단 (Step A1 결과)
- 샘플 5개 출력 보고 좋다/애매하다/나쁘다 판정
- creative output으로 어떤 점이 약한지 기록
- → `docs/creative/RENDERER_DIAGNOSIS_ALPHA.md`

### Gate 2 — Variation Demo 판정 (Step A6 결과)
- Peter / Van Gogh 5-variation demo 읽고:
  - 정말 변주처럼 보이는가
  - IP 자산으로 갈 만한가
- → `docs/creative/VARIATION_READING_REVIEW.md`

---

## 6. 성공 / 실패 기준

### 성공 (4/6 만족)
1. 같은 anchor의 5 seed가 최소 3개 이상 명확히 다르게 읽힘
2. 차이가 단순 문체가 아니라 **구조 차이**
3. person / event / world 중 최소 2개 층위가 읽힘
4. renderer가 trajectory 차이를 죽이지 않음
5. Lee가 "IP 변주로 쓸 수 있겠다"고 판단
6. 반복 템플릿 냄새가 치명적이지 않음

### 실패 (2/5 만족 시 J-Beta로 가지 않음)
1. 5개가 거의 같은 이야기로 읽힘
2. 차이가 seed가 아니라 renderer 랜덤성처럼 느껴짐
3. world-side cause가 안 보임
4. 문장이 너무 보고서 같아서 creative output으로 어려움
5. selector보다 manual curation이 더 낫게 느껴짐

---

## 7. J-Alpha 8 Steps 실행 plan

| Step | 작업 | 산출물 |
|---|---|---|
| 1 | 트랙 전환 공식화 | `docs/CREATIVE_TRACK_TRANSITION.md` (this) |
| 2 | Renderer 진단 틀 | `docs/creative/RENDERER_DIAGNOSIS_ALPHA.md` (Lee 기입용) |
| 3 | Minimal taxonomy | `docs/specs/STORY_UNIT_TAXONOMY_MINIMAL.md` |
| 4 | Curated anchor set | `docs/creative/CURATED_ANCHOR_SET_ALPHA.md` |
| 5 | Minimal selector | `engine/story/selector.py` + `tests/test_story/test_selector_alpha.py` |
| 6 | Renderer 1차 개선 | renderer patch + `docs/creative/NOVEL_TONE_GUIDE_ALPHA.md` |
| 7 | 5-variation demo | `outputs/creative_demo/{peter,vangogh}_anchor_5_variations_ko.txt` |
| 8 | Reading review | `docs/creative/VARIATION_READING_REVIEW.md` (성공/실패 판정) |

---

## 8. 지금 하지 말 것 (forbidden_now)

- 70+ trajectory 전체 라벨링
- selector 점수 체계 과도 정교화
- IP 형태 추가 확장 (drama/game/webtoon)
- research 트랙 재개
- paper 통합 작업
- Branch C 추가 slice 실행
- engine touch (authority autonomy 등)
- `world/` legacy 재검토

---

## 9. 트랙 위치 (project roadmap)

| 단계 | 상태 |
|---|---|
| v0.7 trace pipeline | 완료 |
| v1.2 phase-linked | 완료 |
| Branch C 1차 evidence | 완료 (paper §6.9, Appendix G) |
| Story Output MVP Phase 2 | 완료 (paper §6.10, Appendix H, 6/6 PASS) |
| **J-Alpha (Creative 1차 증명)** | **진행 중** |
| J-Beta (Creative 일반화) | J-Alpha 성공 후 |
| v1.0 Stage 2 PyTorch | 보류 (Creative 트랙 우선) |
| v2.0 Narrative Witness Layer | J-Alpha 성공 + selector 일반화 후 |

→ **Creative 트랙이 v2.0의 entry point**. J-Alpha 성공 시 v2.0 visible.

---

## 10. 한 줄 요약

**Phase J를 그대로 크게 시작하지 말고, J-Alpha에서 먼저 "같은 anchor의 5 seed가 실제로 서로 다른 한국어 이야기로 읽히는가"를 증명한다. 그 다음 J-Beta에서 taxonomy / selector / labeling을 일반화한다.**
