# WITNESS · Phase 3.1 Flesh Baseline Demo

> Phase 3.1 prep (No-ML weighted score) — 2026-05-11

universal skeleton의 각 seed가 어떤 장르 flesh와 잘 맞는지 *설명 가능한 weighted
rule score*로 점수화한다. **ML / fine-tuning 0**.

---

## 1. 무엇을 보여주는가

### 1.1 핵심 흐름

```
SkeletonOutput v1.1
  → Genre Profile (rulebook + KEEP feature 기반)
  → weighted rule score
  → recommendation (genre_id, fit_label, reason_features)
```

### 1.2 5초 인상

```
- 4개 universal seed 각각에 *어떤 장르가 가장 잘 맞는지* 점수
- 점수가 *왜* 그렇게 나왔는지 reason_features 표시
  (e.g. "axis:loyalty_vs_survival" / "pressure:authority_vigilance")
- raw text / 대사 / 본문 생성 0 — audit 자동 검증
- 각 score는 코드 + JSON으로 추적 가능 → ML 진입 시 ablation baseline으로 그대로 사용
```

---

## 2. 보는 법

### 2.1 self-contained HTML 데모

```
docs/portfolio/demo_flesh_baseline/index.html
```

브라우저에서 바로 연다. 외부 CDN / asset 의존 0. CSS grid + per-seed 카드 + 전체
matrix 표.

### 2.2 텍스트 산출물

```
docs/portfolio/demo_flesh_baseline/baseline.md
docs/portfolio/demo_flesh_baseline/flesh_baseline_output.json (machine-readable)
```

### 2.3 재생성

```bash
# 1. genre profiles (Phase 3.0 통과 전이면 rulebook-only)
python scripts/narrative/build_genre_profiles.py \
    --genres korean_morning_melodrama japanese_quiet_drama \
    --output data/narrative/phase3_1_demo/genre_profiles.json \
    --allow-rulebook-only

# 2. flesh baseline
python scripts/narrative/run_flesh_baseline.py \
    --skeleton docs/portfolio/demo/skeleton_output.json \
    --profiles data/narrative/phase3_1_demo/genre_profiles.json \
    --output data/narrative/phase3_1_demo/flesh_baseline_output.json

# 3. demo HTML / MD
python scripts/narrative/build_flesh_baseline_demo.py \
    --skeleton docs/portfolio/demo/skeleton_output.json \
    --baseline data/narrative/phase3_1_demo/flesh_baseline_output.json \
    --output docs/portfolio/demo_flesh_baseline
```

---

## 3. Score 공식 (설명 가능)

```
final_score = 0.5 × compatibility_score + 0.5 × annotation_score
```

- **compatibility_score** (rulebook 기반):
  - axis match: skeleton.conflict_axis_id ∈ profile.compatible_conflict_axes → +0.5
  - pressure overlap: |seed_pressures ∩ profile_pressures| / |seed_pressures| × 0.5
- **annotation_score** (Phase 3.0 KEEP feature 기반):
  - Σ(feature_score normalized × profile.feature_weight)
  - normalized: 0-5 level → 0.0-1.0 (level/5)
- **annotation_score**가 없으면 compatibility-only fallback (Phase 3.0 통과 전 상태)

### fit_label 매핑

| score | fit_label |
|---|---|
| ≥ 0.70 | strong_fit |
| ≥ 0.50 | moderate_fit |
| ≥ 0.25 | weak_fit |
| < 0.25 | no_fit |

---

## 4. 신뢰성

### 4.1 Audit 자동 검증

모든 baseline 생성마다 다음 audit 필드가 체크된다:

```text
audit.raw_text_used:       false  (synopsis 본문 사용 0)
audit.evidence_preserved:  true   (source_seed_id / conflict / pressure 보존)
model.trained:             false  (학습 안 함, weighted rule만)
model.type:                "weighted_rule_score"
```

→ 모든 score가 *코드 + JSON*으로 설명 가능. neural / fine-tuning 영역 진입 시
이 baseline을 *ablation 비교군*으로 사용.

### 4.2 Test 커버리지

```text
tests/test_skeleton/test_phase3_1_baseline.py   20 tests
  - GenreProfile (4): roundtrip / normalize / build_from_rulebook / KEEP filter
  - Scoring (5): compatibility / annotation linear / fit_label / blended
  - run_flesh_baseline (2): multi × multi / serializable
  - build_genre_profiles CLI (5): help / rulebook-only / require-flag /
    with-reliability / low-keep fail
  - run_flesh_baseline CLI (3): help / e2e / exit 2
  - + build_flesh_baseline_demo CLI (Phase 3.1 cycle 4): help / deployed e2e /
    HTML self-contained / no synopsis_text
```

---

## 5. Phase 3.0 → Phase 3.1 데이터 흐름

```text
Phase 3.0 mini pilot (사용자 승인 후)
  → reliability.json
  → KEEP features
  → build_genre_profiles.py
    → genre_profiles.json (KEEP 기반 weights)

Phase 3.1 baseline
  → run_flesh_baseline.py
    → flesh_baseline_output.json (recommendations + audit)
  → build_flesh_baseline_demo.py
    → demo HTML + MD + JSON mirror
```

---

## 5.1. 3 Targets — Plan §22 (A / B / C)

위 §1-4는 Plan **§22.1 Target A** 만 다룬다. 전체 Phase 3.1 baseline은 *세 layer*:

| Target | Plan § | 질문 | 모듈 | 데모 |
|---|---|---|---|---|
| **A** Genre Mode Classification | §22.1 | seed가 어떤 장르 flesh와 잘 맞는가? (flat) | [engine/observer/flesh_baseline.py](../../engine/observer/flesh_baseline.py) | `demo_flesh_baseline/index.html` |
| **B** Genre Intensity Score | §22.2 | *각 episode*가 장르 시그니처에 얼마나 부합하는가? | [engine/observer/episode_intensity.py](../../engine/observer/episode_intensity.py) | `demo_episode_intensity/index.html` (cycle 40, **fixture-only**) |
| **C** Adaptation Recommendation | §22.3 | seed별 *top-K* 장르 ranked 추천 (grouped) | [engine/observer/adaptation_recommendation.py](../../engine/observer/adaptation_recommendation.py) | `demo_adaptation_recommendation/index.html` |

### Target C — Adaptation Recommendation (cycle 17-19)

Target A의 (seed × profile) flat list를 *seed별 grouped + score 내림차순 + top_k*로 재구성. schema_version `adaptation_recommendation_v1`.

```bash
# 1. Target C 산출
python scripts/narrative/run_adaptation_recommendation.py \
    --skeleton docs/portfolio/demo/skeleton_output.json \
    --profiles data/narrative/phase3_1_demo/genre_profiles.json \
    --output data/narrative/phase3_1_demo/adaptation_recommendation.json \
    --top-k 3

# 2. Target C 데모 HTML/MD
python scripts/narrative/build_adaptation_recommendation_demo.py \
    --recommendation data/narrative/phase3_1_demo/adaptation_recommendation.json \
    --output docs/portfolio/demo_adaptation_recommendation
```

→ 데모: [docs/portfolio/demo_adaptation_recommendation/index.html](demo_adaptation_recommendation/index.html). Non-Claims + Prep-mode (rulebook-only) + Calibration banner + 1순위 분포 + seed별 ranked card.

**Cross-target invariant** (cycle 21): Target A의 seed별 top-1 = Target C의 1순위. 두 Target은 동일한 `recommend_seed()` 호출 — `tests/test_skeleton/test_phase3_1_baseline.py::test_target_a_and_c_*` 강제.

---

## 5.2. Plan §24 Step 2 Bridge — Recommendation → Adapter (cycle 25)

`adaptation_recommendation.json`의 *modal 1순위 genre*를 자동 선택해 `apply_genre_adapter.py`에 delegate. SkeletonOutput → Target C → modal_genre → GenreAdaptedOutput chain 완결.

```bash
python scripts/narrative/apply_top_recommendation.py \
    --skeleton docs/portfolio/demo/skeleton_output.json \
    --recommendation data/narrative/phase3_1_demo/adaptation_recommendation.json \
    --output data/narrative/phase3_1_demo/top_recommendation_adapted.json
```

산출:
- stdout — 선택 근거 (modal_genre / count / tie_break / `calibration_status` / `mode` rulebook_only/annotation_blended) 노출.
- output JSON — GenreAdaptedOutput (apply_genre_adapter와 동일 schema).
- `--genre` flag로 modal 자동 선택을 override 가능.

---

## 5.3. Phase 3.1 §29 Acceptance 자동 검증 (cycle 29-31)

`verify_phase3_1_acceptance.py`로 Plan §29 9 항목을 한 명령으로 점검 (Phase 3.0 verifier 대칭):

```bash
python scripts/data/verify_phase3_1_acceptance.py \
    --baseline-output data/narrative/phase3_1_demo/flesh_baseline_output.json \
    --profiles data/narrative/phase3_1_demo/genre_profiles.json \
    --demo-dir docs/portfolio/demo_flesh_baseline \
    --baseline-cover-doc docs/portfolio/FLESH_BASELINE_DEMO.md \
    --output data/narrative/phase3_1_demo/acceptance_check.json \
    --md-report data/narrative/phase3_1_demo/acceptance_check.md
```

- exit 0 (모든 AUTO PASS 또는 PENDING) / 1 (AUTO FAIL ≥ 1) / 2 (입력 오류)
- Phase 3.0 reliability 의존 항목 활성화: `--reliability-report data/annotation/phase3_pilot/reports/reliability.json`
- 운영 절차 상세: [PHASE_3_0_PIPELINE_OPERATING_GUIDE §4.6](../plans/PHASE_3_0_PIPELINE_OPERATING_GUIDE.md#46-phase-31-acceptance-자동-검증-cycle-29-31)

---

## 6. Phase 3.1 §29 Acceptance 매핑

| 조건 | 상태 |
|---|---|
| Phase 3.0 reliability report 통과 | ⏳ 사용자 승인 후 |
| GenreProfile v1 생성 | ✅ |
| weighted score baseline | ✅ |
| Skeleton seed별 genre fit score | ✅ |
| reason_features 설명 가능 | ✅ |
| raw synopsis 출력 노출 0 | ✅ (audit + serialization 검증) |
| rule-based adapter 연결 | ✅ (`recommended_adapter="rulebook_v2_8"`) |
| baseline report | ⏳ Phase 3.0 pilot 후 |
| demo_flesh_baseline/index.html | ✅ |

---

## 7. 한 줄 요약

```text
ML 학습 0으로도 *설명 가능한 weighted rule score*가 가능함을 증명하는 데모.
Phase 3.0 데이터가 들어오면 점수가 더 정교해지지만, 구조는 그대로 유지.
```
