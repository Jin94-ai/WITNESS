# Data Card — WITNESS Drama Mining

> 작성: 2026-05-12 (Track A pivot Day 1)
> 데이터: AI-Hub 023 "방송 콘텐츠 대본 요약 데이터"

---

## 1. Dataset Identity

| 항목 | 값 |
|---|---|
| **Dataset name** | 방송 콘텐츠 대본 요약 데이터 |
| **AI-Hub 번호** | 023 |
| **출처** | aihub.or.kr (한국지능정보사회진흥원 NIA) |
| **공식 지원** | 과학기술정보통신부 |
| **언어** | 한국어 |
| **도메인** | 방송 대본 (드라마 / 예능 / 시사 / 역사 / 문화) |
| **본 프로젝트 로컬 경로** | `data/023.방송 콘텐츠 대본 요약 데이터/` (gitignored) |

---

## 2. 라이선스 + 사용 정책

### 2.1 공식 라이선스

AI-Hub 데이터는 *비상업 학술/연구 목적 한정 무료*. 사용 신청 + 회원 약관 동의 후 다운로드. **Raw 데이터 재배포 금지**.

### 2.2 본 프로젝트의 사용 정책

```
✅ 허용 (Track A 진행 가능):
  - 학습 데이터로 활용
  - 학습된 모델 코드 공개
  - 학습 결과 메트릭 공개 (accuracy / F1 / ROUGE 등)
  - 모델 카드에 *집계 통계*만 명시
  - 비원문 (paraphrased / synthetic) 예시 인용

❌ 금지 (강제):
  - Raw passage public repo commit
  - Raw passage README / model card / docs / portfolio 노출
  - 학습 데이터 그대로 외부 공유
  - 상업적 활용 (비상업 한정)
  - Annotation Summary 원문 그대로 인용 + 공개

✅ 학습 산출 공개 시 의무:
  - 인용 문구 포함:
    "이 연구는 과학기술정보통신부의 재원으로
     한국지능정보사회진흥원의 지원을 받아 구축된
     '방송 콘텐츠 대본 요약 데이터'를 활용하여 수행된 연구입니다."
  - AI-Hub 023 출처 명시
```

---

## 3. 규모 + 구조

### 3.1 전체 분포 (TL1 = Training 라벨 기준)

| 카테고리 | 20per (20% 분량 요약) | 3sent (3문장 요약) | 합계 |
|---|---:|---:|---:|
| `enter` (예능) | 7,568 | 8,878 | 16,448 |
| `fs_drama` (KBS 일일/주말) | 7,502 | 8,500 | 16,004 |
| `fm_drama` (KBS 일일/아침) | 8,214 | 7,786 | 16,002 |
| `c_event` (시사) | 6,791 | 7,092 | 13,885 |
| `history` (역사) | 5,250 | 6,233 | 11,485 |
| `culture` (문화) | 4,875 | 5,675 | 10,552 |
| **합계** | **40,200** | **44,164** | **84,382** |

| Split | passages |
|---|---:|
| Training (TL1) | 84,382 |
| Validation (VL1) | 10,018 |

### 3.2 드라마 데이터 (본 프로젝트 핵심)

```
fm_drama + fs_drama (20per만) = 16,716 passages
fm_drama + fs_drama 전체 (20per + 3sent) = 32,006 passages
fm_drama 1064 distinct doc_origin / fs_drama 566 distinct
약 800 base works (회차 통합 시)
overlap fm vs fs = 0
```

### 3.3 방송사 분포

```
모든 데이터: KBS (author = "KBS", publisher = "KBS")
연도: 2002~2017+
```

**한계**: SBS / JTBC / MBC / OTT 작품 미포함. Lee 원래 의도 (펜트하우스 / 부부의 세계 / 아내의 유혹 등 막장 6작품)와는 *다른 데이터*. KBS 가족극에 한정된 일반화.

### 3.4 Schema

```json
{
  "Meta": {
    "doc_id": "SCRIPT-fm_drama-11001",
    "doc_category": "SCRIPT",
    "doc_type": "fm_drama",
    "doc_name": "11001_NC_당신옆이좋아_20020701.txt",
    "author": "KBS",
    "publisher": "KBS",
    "published_year": "2002",
    "doc_origin": "당신옆이좋아",
    "passage_id": "SCRIPT-fm_drama-11001-00002",
    "passage": "씬 단위 대본 텍스트 (해설 + 상황 묘사 + 일부 대사)"
  },
  "Annotation": {
    "Summary1": "1문장 요약",
    "Summary2": "",
    "Summary3": "2-3문장 요약"
  },
  "filename": "..."
}
```

`Summary2`는 일관적으로 비어있음 (사용 안 함).

### 3.5 doc_origin 패턴

```
회차 통합형: "당신옆이좋아" (단일 doc_origin, 다수 passage)
회차 분리형: "장밋빛인생024", "결혼해주세요31", "복희누나004"
             (회차마다 별도 doc_origin, 끝 숫자 = 회차 번호)
```

**Data leakage 주의**: split 시 회차 단위가 아닌 *base 작품 단위* 분할 필요 (cycle 86 §3).

---

## 4. 본 프로젝트 사용 범위 (Track A)

| 학습 과제 | 데이터 사용 |
|---|---|
| 과제 B (Week 1, fm vs fs 분류기) | 드라마 카테고리 (20per + 3sent) — 32,006 passages |
| 과제 A (Week 2, 씬 요약) | fm + fs (20per만) — 16,716 (passage, Summary1) 쌍 |
| 비교용 6-way (fallback) | 전체 84,382 |

---

## 5. 알려진 한계

### 5.1 도메인 한계
- KBS 가족극 / 일일극 / 주말 특집 위주
- SBS 막장 (펜트하우스 / 아내의 유혹 등) 미포함
- JTBC 현대극 (부부의 세계) 미포함
- OTT (넷플릭스 / 디즈니+) 미포함
- 영화 / 웹드라마 미포함

### 5.2 텍스트 한계
- passage = 씬 단위. 전체 회차 narrative arc 정보 미보존 (분리됨)
- 대사 비중 낮음 (해설 + 상황 묘사 위주)
- 작가/연출 메타 정보 부족

### 5.3 라벨 한계
- Summary1/3은 *인간 작성* 요약 — 일관성 변동 가능
- Summary 품질 검토 gate (cycle 86 §7) Week 2 학습 전 필수

### 5.4 Leakage 위험
- 회차 분리형 doc_origin이 *같은 base 작품의 다른 회차*에 split될 수 있음
- 검증 테스트 필수 (tests/test_drama_mining_split.py)

---

## 6. 정직성 정책 (WITNESS 정신 계승)

```
모든 학습 결과 (model card / report)에 다음 명시:
  - 사용된 데이터 출처 (AI-Hub 023)
  - 학습 데이터 양 / 분할 비율 / leakage 검증 결과
  - 하이퍼파라미터
  - 학습 시간 / GPU
  - *알려진 한계* (§5 참조)
  - 일반화 가능 영역 (KBS 가족극)
  - 일반화 어려운 영역 (SBS 막장 / OTT / 영화)
```

---

## 7. 한 줄 요약

```
AI-Hub 023 = KBS 드라마 32,006 씬 + Summary 라벨. 비상업 학술 OK.
Raw 절대 commit 금지 / portfolio 노출 금지 / 인용 의무.
Track A 학습 ground truth로 사용.
```
