# WITNESS Phase 3 — 수동 어노테이션 방식으로의 전환 계획

> 작성: 2026-05-11
> 배경: Phase 3.0 prep 완료 후 사용자 승인 대기 중. LLM API 사용 불가 결정 →
> 수동 chat 인터페이스 + 로컬 데이터 수집으로 방식 전환.

---

## 0. 한 줄 방향

```
LLM API 호출 없음 + Claude Code로 데이터 수집 + chat 붙여넣기로 어노테이션
→ 최소 비용으로 첫 ML 학습까지 도달
```

기존 prep이 자동 LLM API를 전제로 설계되어 있어, 본질에서 멀어진
거버넌스 5+2건이 진입 장벽이 됨. 본 계획은 그 장벽을 우회하면서
**실제 학습 1회 도달**을 목표로 한다.

---

## 1. 제약 조건의 명시

```
✅ Claude Code 사용 가능 (로컬 환경, 너의 컴퓨터에서 실행)
✅ Chat 인터페이스 사용 가능 (Claude / ChatGPT / Gemini 웹)
✅ 로컬 GPU 사용 가능 (RTX 2070 SUPER / RTX 4050)
❌ LLM API 호출 (Anthropic / OpenAI / Gemini API) — 비용 부담
❌ 자동화된 multi-AI 어노테이션 파이프라인
```

이 제약 위에서 작동하는 가장 단순한 흐름을 설계한다.

---

## 2. 작동 흐름 (단순화된 8 step)

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1. Claude Code로 데이터 수집                            │
│   - 막장 N작품 + 비교군 N작품 선정                            │
│   - 회차 줄거리를 로컬에 수집                                 │
│   - data/raw/{title_id}/{ep:02d}.json                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2. 데이터 정규화 (기존 scripts 재사용)                  │
│   - python scripts/data/normalize_synopsis.py               │
│   - data/normalized/...                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3. 어노테이션 prompt 생성                              │
│   - python scripts/data/build_annotation_inputs.py          │
│   - data/annotation_inputs/{title}/{ep}.txt                 │
│   - 각 파일은 chat에 그대로 붙여넣기 가능한 형태             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4. 수동 어노테이션 (★ 새로 도입)                       │
│   - 너가 직접 chat을 열고 prompt 붙여넣기                   │
│   - LLM 응답(JSON)을 복사                                   │
│   - data/annotated/_per_annotator/{model}/{title}/{ep}.json │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5. 검증                                                 │
│   - python scripts/annotation/validate_annotation_outputs.py│
│   - schema + hallucination + coverage                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 6. Multi-AI 합성 (선택)                                │
│   - python scripts/annotation/synthesize_annotations.py     │
│   - data/annotated/{title}/{ep}.json (최종)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 7. Feature matrix + Reliability report                 │
│   - python scripts/annotation/build_feature_matrix.py       │
│   - python scripts/annotation/build_reliability_report.py   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 8. α Classifier 학습 (Phase 3 본격 시작)               │
│   - 작은 분류기 (gradient boosting)                         │
│   - 막장 / 비교군 분류 성능 측정                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. MVP 규모 (현실적 목표)

수동 어노테이션의 시간 비용을 감안한 현실적 규모.

### 3.1 데이터 규모

```
막장 모드 작품:        2~3개
비교군 작품:           2~3개
작품당 회차:           5회차 (가능하면 7~10)
총 회차 수:            20~30회차
어노테이터 수:         2명 (Claude + ChatGPT, 또는 Claude만)
총 어노테이션 작업:    40~60건
```

### 3.2 시간 견적

```
회차당 수동 어노테이션: 2~3분 (prompt 붙여넣기 + JSON 복사 + 저장)
40~60건 × 2.5분 = 100~150분 (1.5~2.5시간 집중 작업)

→ 하루 1~2시간씩 2~3일 분산 작업 가능
```

### 3.3 학습 가능성

```
40~60건의 어노테이션 데이터
× 11 features (ANNOTATION_GUIDE v1.2)
→ 작은 분류기 학습에 충분
   (gradient boosting은 수십 건 데이터로도 작동)

→ ML 학습 자체는 가능
→ 단, 일반화 성능은 제한적 (이는 MVP의 정상적 한계)
```

---

## 4. 작품 선정 가이드

### 4.1 막장 모드 작품

```
선정 기준:
- 학술 논문 / 언론 기사에서 "막장"으로 명시 분류
- 회차별 줄거리가 공개 위키에 잘 정리되어 있음
- 종영된 작품 우선 (전개 완결성)
- 한국 작품 우선 (한국어 자료 풍부)

후보 영역:
- 한국 일일드라마 / 아침드라마
- KBS 주말드라마 중 막장 분류 작품
- 케이블 막장 시리즈
```

### 4.2 비교군 (Control) 작품

```
선정 기준:
- 막장 작품과 같은 시기 / 같은 채널 / 같은 시간대 우선
- "잔잔한", "정통", "일상" 분류 작품
- 회차별 줄거리 공개

후보 영역:
- 잔잔한 가족 드라마
- 정통 시대극
- 한일 합작 일상극 (japanese_quiet_drama profile 활용)
```

### 4.3 작품 확정 절차

```
1. 후보 리스트 작성 (각 카테고리 5개)
2. 회차별 줄거리 접근성 확인
3. ToS / 라이선스 점검
4. 최종 2~3개씩 확정
5. data/raw/_meta/selected_works.json 기록
```

---

## 5. Claude Code 데이터 수집 가이드

### 5.1 Claude Code에게 줄 directive 예시

```
WITNESS 데이터 수집 directive:

목표: 작품 N의 1~5회차 줄거리를 data/raw/N/{ep}.json 형태로 저장.

제약:
- 위키피디아 한국어 / 나무위키 / 공식 사이트에서만 수집
- ToS 확인: 비상업 사용 (CC BY-NC-SA 등) OK
- robots.txt 준수
- 요청 간 최소 2초 간격
- 원문 시나리오 / 대본은 수집 금지

각 회차 JSON 형식:
{
  "schema_version": "raw_synopsis_v1",
  "title_id": "string",
  "title_ko": "한국어 제목",
  "episode_no": 1,
  "synopsis_text_ko": "회차 줄거리 (요약, 200~500자)",
  "source_url": "https://...",
  "source_license": "CC BY-NC-SA 2.0 KR",
  "collected_at_iso": "2026-05-11T..."
}
```

### 5.2 수집 시 주의사항

```
- 줄거리는 사실 정보(누가 무엇을 했다) 위주
- 원문 표현 그대로 복사 금지 (요약 / 재서술)
- 출처 URL과 라이선스 반드시 기록
- 수집 로그 보관 (data/raw/_log/collection_log.jsonl)
```

---

## 6. 수동 어노테이션 절차 (Step 4 상세)

### 6.1 준비

```
1. 새 chat 세션 열기 (Claude 또는 ChatGPT)
2. data/annotation_inputs/{title}/{ep}.txt 파일 열기
3. 파일 전체를 chat에 붙여넣기
4. LLM 응답 대기
```

### 6.2 LLM 응답 처리

```
1. LLM이 JSON 응답을 줌 (```json ... ``` 블록)
2. JSON 부분만 복사
3. data/annotated/_per_annotator/{model}/{title}/{ep}.json 으로 저장
   - model: "claude" 또는 "gpt" 또는 "gemini"
4. 다음 회차로 진행
```

### 6.3 한 chat에 몇 회차를 처리할지

```
권장: 한 chat 세션당 5회차 이내
이유:
- 컨텍스트가 누적되면 LLM 응답의 일관성이 변할 수 있음
- 매 5회차마다 새 chat을 열어 어노테이터를 "리셋"
- 이는 어노테이터 간 독립성과 비슷한 효과
```

### 6.4 어노테이터 다양성

```
권장 구성 (선택):
- 어노테이터 A: Claude (이 인터페이스)
- 어노테이터 B: ChatGPT (웹)
- 어노테이터 C: Gemini (웹, 선택)

최소 구성:
- Claude 한 모델, 5회차마다 새 chat
```

### 6.5 수동 어노테이션의 새 리스크와 대응

```
리스크 1: 어노테이터의 피로 → 일관성 저하
대응: 한 세션에 5회차 이내, 휴식 후 재개

리스크 2: chat context 누적 → 응답 편향
대응: 5회차마다 새 chat. 전체 instruction을 매번 다시 붙여넣기

리스크 3: JSON 응답 형식 오류 (수동 복사)
대응: validate_annotation_outputs.py로 즉시 검증.
      schema 오류 시 같은 chat에서 재시도 (LLM에게 "JSON only"로 재요청)

리스크 4: 환각 (evidence quote가 원문에 없음)
대응: hallucination report 자동 생성. 환각 비율 높은 어노테이션은 폐기.
```

---

## 7. 기존 거버넌스 재정의

### 7.1 사용자 승인 항목 재분류

```
원래 5+2 항목 중:

[유지] 데이터 수집 ToS 점검             → Claude Code directive에 포함
[유지] 작품 선정 기준 확정              → §4
[유지] 어노테이션 결과 보관 방침        → §6.2 (per-annotator 디렉토리)
[N/A]  LLM API 비용 승인                → 수동 방식이라 무관
[N/A]  LLM provider ToS 점검            → chat 인터페이스 약관 준수로 충분
[유지] Data Card 작성                    → MVP 완료 후
[유지] Pilot Report 작성                 → MVP 완료 후
```

### 7.2 정직성 4-layer 재적용

```
JSON layer:
- 어노테이션 JSON에 annotator_id 명시 (Claude/GPT/Gemini)
- annotated_at_iso 명시
- chat session id (선택, 너가 임의 부여)

Demo layer:
- 결과 demo에 "manual annotation" 배지 표시
- 자동 API 호출이 아님을 명시

Validator layer:
- hallucination report 그대로 유지
- coverage check 그대로 유지

운영 layer:
- Operating Guide를 수동 step으로 재작성
- Deploy Status Matrix 단순화: deployed / pending_manual_work
```

### 7.3 버리는 것

```
- 자동 LLM API 호출 prep
- API 비용 견적 / 한도 관리
- API 키 보안 절차
- API rate limit 처리
- 자동 multi-AI orchestrator (수동 방식이 대체)
```

---

## 8. Step 8 — α Classifier 첫 학습

### 8.1 목표 단순화

```
야심찬 목표 X: "막장 모드를 변별하는 일반화된 분류기"
현실적 목표 O: "수집한 데이터에서 막장 / 비교군이 분리되는지 확인"

이게 분리되면:
- 7~11 features의 변별력이 검증됨
- Phase 4 (Evaluator γ)로 진행 가능

분리되지 않으면:
- features 재설계 필요
- 또는 데이터 양 부족 (더 수집)
- 또는 어노테이션 품질 부족 (재어노테이션)

어느 결과든 다음 행동이 명확해진다.
```

### 8.2 모델 선택

```
권장: gradient boosting (LightGBM 또는 XGBoost)
이유:
- 작은 데이터셋에서 작동
- 11 features를 입력으로 받기 쉬움
- 변별력 분석 (feature importance) 자동 제공
- RTX GPU 불필요 (CPU 학습)
- 너의 (b) Mid ML 규모에 적합

대안: 작은 transformer
- 데이터 양이 너무 적어 비추천
- 회차 줄거리 텍스트를 직접 입력하려면 의미 있음
```

### 8.3 학습 코드 위치

```
scripts/learning/train_alpha_classifier.py (신규)
notebooks/alpha_classifier_v1.ipynb (탐색용)

models/mode_classifier_alpha_v1/
├── model.pkl
├── feature_importance.json
├── eval_metrics.json
└── model_card.md
```

### 8.4 학습 결과 분석 항목

```
필수:
- 정확도 / F1 / AUC
- 혼동 행렬
- Feature importance (어떤 feature가 가장 분리력 있나)
- Confidence calibration

추가 분석:
- features 중 분리력 없는 것 식별 → 제거 후보
- 작품 단위 분할 시 성능 (data leakage 점검)
```

---

## 9. 단계별 실행 계획

### 9.1 Week 1: 데이터 수집

```
Day 1: 작품 선정 + ToS 점검
  - 막장 후보 5개, 비교군 후보 5개 리스트업
  - 위키 / 공식 사이트에서 줄거리 접근성 확인
  - 최종 각 2~3개씩 확정

Day 2-3: Claude Code로 수집
  - 작품당 5회차 × 4~6작품 = 20~30회차
  - data/raw/ 구축
  - 수집 로그 작성

Day 4: 정규화 + annotation_inputs 생성
  - normalize_synopsis.py 실행
  - build_annotation_inputs.py 실행
  - 검토 후 다음 단계 준비
```

### 9.2 Week 2: 수동 어노테이션

```
Day 5-6: 어노테이터 A (Claude)
  - 20~30회차 × 2.5분 = 50~75분
  - 5회차씩 분산, 컨텍스트 리셋
  - data/annotated/_per_annotator/claude/ 구축

Day 7 (선택): 어노테이터 B (ChatGPT)
  - 같은 작업 반복
  - 두 어노테이터 결과 비교 가능해짐

Day 8: 검증 + 합성
  - validate_annotation_outputs.py
  - synthesize_annotations.py
  - hallucination report 확인
```

### 9.3 Week 3: ML 학습 첫 시도

```
Day 9: Feature matrix + Reliability
  - build_feature_matrix.py
  - build_reliability_report.py
  - Pearson r 측정 (어노테이터 2명일 때)

Day 10: α Classifier 학습
  - train_alpha_classifier.py
  - 학습 결과 분석
  - feature importance 검토

Day 11: 결과 정리
  - Model card 작성
  - 다음 phase 결정 (Phase 4 진행 또는 데이터 재수집)
```

### 9.4 일정의 유연성

```
이 일정은 권장이지 강제가 아니다. 너의 페이스에 맞춰 조정.
중요한 건 "끊김 없이 진행"이 아니라 "각 step의 결과를 보면서 다음 결정".
```

---

## 10. 실패 시나리오와 대응

### 10.1 시나리오 A: 작품 수집이 안 됨

```
원인: ToS 제약 / 회차별 줄거리 부족
대응:
- 비교군을 한국 작품 외로 확장 (일본 잔잔극 등)
- 회차 수를 줄이고 작품 수를 늘림 (3회차 × 8작품)
- 공식 EPG / 학술 정리 자료 활용
```

### 10.2 시나리오 B: 수동 어노테이션이 너무 힘듦

```
원인: 회차당 3분 이상 소요 / 피로 누적
대응:
- 어노테이터 1명으로 축소 (Claude만)
- 회차 수 축소 (10~15회차 MVP)
- prompt를 더 간결하게 (features 11 → 7로 축소)
```

### 10.3 시나리오 C: α 학습이 분리 안 됨

```
원인:
- 데이터 부족
- features 변별력 부족
- 어노테이션 품질 문제

대응 (우선순위 순):
1. Inter-annotator r 확인 → 낮으면 어노테이션 가이드 개선
2. Feature importance 확인 → 분리력 0인 feature 제거
3. 데이터 추가 수집
4. Features 재설계 (10번 미만 분리력이면 정의 자체 의심)
```

### 10.4 시나리오 D: 환각이 너무 많음

```
원인: LLM이 줄거리에 없는 quote를 만들어냄
대응:
- prompt에 "원문에 없으면 evidence_quotes를 빈 리스트로" 명시
- 환각 비율 30% 이상 어노테이션은 폐기 후 재시도
- 같은 chat에서 "JSON 다시, 원문 인용만"으로 재요청
```

---

## 11. Phase 3 이후 가능한 확장

이번 MVP 이후 자연스럽게 이어질 수 있는 방향들. 지금은 결정하지 않음.

```
- Evaluator γ 구축 (α 활용)
- Transformer β 구축 (γ로 평가)
- 두 번째 Narrative Mode 학습 (잔잔극, 웹소설 등)
- 어노테이션 양 확장
- (먼 미래) 작은 LM fine-tuning으로 문체 학습
```

---

## 12. 본 directive와 기존 거버넌스의 관계

```
기존 directive들의 위치:

docs/WITNESS_PHASE_3_05_PREP_INTEGRITY_AND_VALIDATOR_HARDENING_PLAN.md
  → 자동 LLM API 전제. 본 directive에서 대부분 N/A.

docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md
  → 자동 LLM Labeler 부분 비활성화. 데이터 파이프라인은 유지.

docs/plans/PHASE_3_0_OPERATING_GUIDE.md
  → 본 §2의 8-step으로 대체.

docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md
  → §7.1 재분류 적용.

조치:
- 위 문서들에 본 directive 참조 추가 (대체 / 보완 관계 명시)
- 본 directive를 docs/WITNESS_PHASE_3_MANUAL_ANNOTATION_PIVOT.md로 저장
```

---

## 13. 핵심 의사결정 한 줄

```
prep 인프라는 더 만들지 않는다.
수동으로 첫 학습까지 도달하는 것이 모든 것보다 우선이다.
```

---

## 14. 즉시 시작 directive

```text
WITNESS Phase 3 Manual Pivot — Immediate Start directive:

본 계획 §9.1 Week 1 Day 1부터 시작.

Day 1 작업:
1. 막장 모드 후보 작품 5개 리스트업
   - 한국 일일/주말 드라마, 학술 / 언론 분류 "막장" 작품
2. 비교군 작품 5개 리스트업
   - 같은 시기 / 채널의 잔잔극, 정통극
3. 각 후보에 대해 위키 / 공식 사이트 회차 줄거리 접근성 확인
4. ToS / 라이선스 점검
5. 최종 각 2~3개씩 확정
6. data/raw/_meta/selected_works.json 작성

제약:
- 자동 API 호출 0
- 기존 거버넌스 거치지 않음 (수동 방식 적용)
- prep 인프라 추가 0

Acceptance:
- selected_works.json에 막장 2~3, 비교군 2~3 명시
- 각 작품에 source_urls + license + 5회차 줄거리 접근 가능성 확인 완료
- 이 작업 완료 후 Day 2 (Claude Code 수집)로 자동 진행 가능

Day 1 완료 후 사용자에게 보고하고, Day 2 directive를 받는다.
```

---

*End of plan.*
*수동 어노테이션 방식 — 비용 0, 첫 학습 도달 목표.*
