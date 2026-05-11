# Narrative Mode Corpus — 작품 선정 기준 (Phase 1)

> Per `docs/witness_narrative_mode_plan.md` §5.4 + §5.5.
>
> 이 문서는 막장 / 비교군 코퍼스 *후보 작품*을 어떤 기준으로 고르고, 어떤
> 데이터를 수집하며, 어떤 출처를 ToS / 라이선스 안전선 안에서 사용할지
> 정의한다. **데이터 수집은 이 기준이 확정된 후에만 시작한다.**

---

## 1. 막장 / 비교군 정의

### 1.1 막장 드라마 (target mode)

이 프로젝트에서 *막장 모드*는 다음을 만족하는 회차 흐름으로 정의한다.

```
- 갈등 증폭률이 매우 높음 (회차 시작 대비 끝의 갈등이 급격히 강화)
- 폭로 밀도가 높음 (회차당 새 비밀/사실 1+개)
- 우연 빈도가 결정타 (출생의 비밀, 우연한 마주침 등)
- 관계 극단화 (중간 지대 거의 없음)
- 회수보다 새 갈등 도입이 빠름
- 클리프행어 강도가 회차 말미에 일관되게 강함
```

이 정의는 §2.3의 정량 특성 벡터와 연결된다. 어떤 작품을 막장으로 분류할 때
*학술 논문 / 언론 기사*에서 명시적으로 "막장"으로 분류된 작품만 사용한다.
모호하면 제외.

### 1.2 비교군 (control mode)

같은 시기, 같은 채널, 같은 시간대의 *막장이 아닌* 작품. 예:
- 잔잔한 가족극
- 정통 사극
- 슬라이스-오브-라이프

비교군은 막장 모드를 학습하기 위한 *negative class*로 작동한다. 비교군 없이는
"막장스러움"이 무엇인지 학습 신호가 약해진다.

---

## 2. 작품 선정 기준

### 2.1 막장 작품 — 다음 조건 모두 충족

```
[A] 학술/언론 1차 분류
    - KCI 등록 논문, 주류 언론 기사, 또는 위키 분류 카테고리에서
      "막장"으로 명시 분류된 작품
    - 단순 시청자 의견 (블로그, 댓글)은 1차 근거로 사용하지 않음
[B] 회차 줄거리 공개
    - 위키 / 공식 사이트 / EPG에 회차별 줄거리가 *전체 회차*의 60% 이상
      확보 가능한 작품만 선정
[C] 라이선스 / ToS 안전
    - 줄거리 출처가 robots.txt 허용 + ToS 준수 가능
    - 공식 API / 위키 덤프가 있으면 우선 사용
[D] 시간 분포
    - 2000년대 이후 한국 드라마 우선 (한국어 어노테이션 일관성)
    - 5년 이상 분포 — 시대 편향 최소화
[E] 최소 회차 수
    - 16회 이상 (단막은 제외)
```

### 2.2 비교군 작품

```
[A] 같은 학술/언론 출처에서 "막장 아님"으로 명시 또는 묵시적 분류
[B-D] 위와 동일
[E] 막장과 채널 / 시간대 / 시기 매칭 (1:1 가능하면 매칭)
```

### 2.3 선정 결과 기록 형식

각 후보 작품마다 다음을 기록한다 (`data/raw/{melodrama|control}/_selection_log.json`).

```json
{
  "title": "작품명",
  "title_en": "Romanized Title",
  "year_start": 2010,
  "year_end": 2010,
  "channel": "지상파 채널명",
  "episodes_total": 24,
  "category": "melodrama|control",
  "category_evidence": [
    {"type": "academic", "source_ko": "KCI 논문 제목", "url": ""},
    {"type": "news", "source_ko": "기사 제목", "url": ""}
  ],
  "synopsis_source": "wiki_link|official_site|epg",
  "synopsis_license": "CC-BY-SA-4.0|public_domain|other",
  "selected": true,
  "rejection_reason": ""
}
```

`selected=false` + `rejection_reason`이 채워진 항목도 *기록 보존* — 선정
과정의 투명성.

---

## 3. 수집 데이터 형식

각 회차에 대해 다음 형식으로 저장한다.

```
data/raw/{category}/{title_id}/episodes/{episode_no:02d}.json
```

```json
{
  "schema_version": "synopsis_v1",
  "title_id": "string",
  "title_ko": "string",
  "title_en": "string",
  "category": "melodrama|control",
  "episode_no": 5,
  "synopsis_text_ko": "회차 줄거리 텍스트 (raw 그대로 X — 사실 정보만 구조화 발췌)",
  "source_url": "string",
  "source_license": "string",
  "fetched_at_iso": "2026-05-09T...",
  "fetcher_version": "string",
  "notes": []
}
```

**원문 시나리오 / 대본은 절대 수집하지 않는다.** 회차 줄거리만.

---

## 4. ToS / robots.txt 안전선

```
- 위키피디아: 공식 덤프 (XML/JSON) 사용. 라이브 스크래핑 X.
- 나무위키: ToS 확인 필요. 라이선스가 명시된 부분만 fair-use 범위에서 인용.
- EPG / 공식 사이트: robots.txt 확인. 요청 간격 ≥ 2초.
- 모든 fetch에 User-Agent에 "WITNESS-research-bot (contact: ...)" 명시.
- 수집 로그를 `data/raw/_fetch_log.jsonl`에 추가 (누가, 언제, 어디서, 무엇을).
- 의심스러우면 제외.
```

수집 도중 ToS 변경 / 사이트 차단 발생 시 즉시 정지 + 이미 수집한 데이터의
사용 가능성 재검토.

---

## 5. 첫 시드 리스트 (작성 단계)

이 항목은 *후속 iteration*에서 채워진다. 본 문서가 commit된 시점에는
선정 기준만 정의된 상태. 실제 작품 리스트는:
- `data/raw/melodrama/_selection_log.json` (멜로드라마 후보)
- `data/raw/control/_selection_log.json` (비교군 후보)

위 두 파일이 채워지면 Phase 1 acceptance 충족.

---

## 6. 검증 항목 (Phase 1 acceptance 매핑)

| Plan §5.5 / §6 항목 | 충족 방법 |
|---|---|
| 막장 작품 10개 이상 회차 줄거리 수집 | `data/raw/melodrama/{title}/episodes/*.json` 10 작품 × 평균 16+ 회차 |
| 비교군 작품 10개 이상 회차 줄거리 수집 | 동일 형식으로 control 폴더 |
| 수집 출처와 라이선스 명확 기록 | 각 episode JSON의 `source_url` + `source_license` 필드 |
| robots.txt와 ToS 준수 | `data/raw/_fetch_log.jsonl`에 모든 fetch 로그 + 본 문서 §4 준수 |

---

*이 문서는 Phase 1 시작 전 동결된 기준이다. 변경 시 RFC.*
