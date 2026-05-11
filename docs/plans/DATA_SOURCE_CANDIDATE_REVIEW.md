# Data Source Candidate Review (Phase 3.0)

> Per `docs/WITNESS_PHASE_2_9_PORTFOLIO_FINALIZATION_AND_PHASE_3_PREP_PLAN.md` §6.3.

이 문서는 Phase 3.0 Pilot에서 사용할 *후보 데이터 소스*를 검토한다.
ToS / robots.txt / 저작권 / fetch 가능성 / 공개 repo 정책 측면에서 평가하고,
사용자 승인 전까지는 후보를 *기록*만 한다 — 실제 fetch는 승인 후.

---

## 0. 검토 원칙

```text
1. robots.txt를 *우선* 확인. disallow면 즉시 제외.
2. ToS에서 scrape / automated download 금지 명시 시 제외.
3. 공식 방송사 / 공식 스트리밍 플랫폼 우선.
4. 위키 / 팬덤은 보조 참고만.
5. 개인 블로그 / 리뷰는 저작권/품질 위험으로 비추천.
6. 공개 repo에 원문 synopsis는 commit하지 않음 (data/external_private/).
7. evidence_quote는 짧게 사용 (≤ 30자), 길게 인용 금지.
```

---

## 1. 한국 아침 막장 드라마 후보

| source | url | robots.txt | ToS | 저작권 | fetch | 공개 repo | 추천 |
|---|---|---|---|---|---|---|---|
| KBS 공식 회차 소개 | (확인 필요) | TBD | TBD | 본문 인용 위험 | high | partial (요약만) | TBD — 1순위 후보 |
| MBC 공식 회차 소개 | (확인 필요) | TBD | TBD | 동상 | high | partial | TBD |
| SBS 공식 회차 소개 | (확인 필요) | TBD | TBD | 동상 | high | partial | TBD |
| 네이버 TV 공식 페이지 | (확인 필요) | TBD | TBD | 본문 인용 위험 | medium | low | 보류 |
| 위키백과 (한국 드라마) | (확인 필요) | OK 가능 | CC-BY-SA | 출처 표기로 가능 | medium | partial | 보조 참고 |
| 나무위키 | (확인 필요) | TBD | CC-BY-NC-SA | 비상업 OK | medium | partial | 비상업 portfolio면 OK |
| 개인 블로그 / 리뷰 | 다양 | 사이트별 | 사이트별 | 위험 | low | 비공개 | 비추천 |

→ **사용자 승인 전 모든 status TBD**. 실제 fetch 전 robots.txt + ToS 직접 확인 필수.

## 2. 일본 정적 드라마 후보

| source | url | robots.txt | ToS | 저작권 | fetch | 공개 repo | 추천 |
|---|---|---|---|---|---|---|---|
| NHK 공식 회차 소개 | (확인 필요) | TBD | TBD | 본문 인용 위험 | high | partial | TBD |
| 일본 위키백과 | (확인 필요) | OK 가능 | CC-BY-SA | 출처 표기로 가능 | medium | partial | 보조 참고 |
| 일본 공식 스트리밍 (TVer 등) | (확인 필요) | TBD | TBD | 본문 인용 위험 | medium | low | 보류 |

→ **일본 소스는 1차 pilot 범위에서 제외 권장**. Phase 3.0 1차는 1 genre만 + 한국 우선.

## 3. 비교군 (control / 잔잔한 가족극)

| source | url | robots.txt | ToS | 저작권 | fetch | 공개 repo | 추천 |
|---|---|---|---|---|---|---|---|
| (Phase 3.0 1차에선 비교군 미수집 권장) | — | — | — | — | — | — | 보류 |

---

## 4. 권장 1차 시작점

```text
권장: 한국 아침 막장 드라마 1 genre × 2 titles × 5 episodes
sources: KBS / MBC / SBS 공식 회차 소개 중 robots.txt + ToS 통과한 것 1-2개
fallback: 위키백과 한국 드라마 article (출처 표기, CC-BY-SA)
```

선택 기준:
- robots.txt가 명시적으로 allow 또는 silent
- ToS에 scrape 금지 문구 없음
- 회차별 synopsis가 공식적으로 공개됨 (방송 후 영구 공개)
- 인용 길이를 짧게 유지할 수 있음 (각 회차 < 500자)

## 5. 제외 기준

다음은 1차 pilot에서 제외:

```text
- robots.txt에서 user-agent 없이 disallow
- ToS에 scrape / automated download 금지 명시
- 출처 명시 불가능
- 본문 인용 분량이 너무 큰 sites (전문 + 저작권 위험)
- 광고 / paywall 뒤 공개 안 되는 회차
- 개인 블로그 / 팬 리뷰 / 자막 사이트
```

## 6. 수집 시 필수 메타

각 episode synopsis JSON에 다음 메타를 기록:

```json
{
  "schema_version": "synopsis_v1",
  "title_id": "...",
  "title_ko": "...",
  "title_en": "...",
  "category": "melodrama",
  "episode_no": 1,
  "synopsis_text_ko": "...",
  "source_url": "https://...",
  "source_license": "CC-BY-SA-4.0 | proprietary | unknown",
  "source_robots_txt_status": "allow | disallow | silent",
  "source_tos_status": "allows_research_use | restricted | unknown",
  "fetched_at_iso": "2026-05-XX...",
  "fetcher_user_agent": "WITNESS-Phase3.0-Pilot/0.1 (research)",
  "rate_limit_respected": true,
  "public_repo_allowed": false,
  "notes": ["짧은 메모"]
}
```

---

## 7. 위험 매트릭스

| 위험 | 영향 | 완화 |
|---|---|---|
| 저작권 위반 | high | 짧은 인용 (≤ 30자) + 출처 표기 + 비공개 repo |
| ToS 위반 | high | 사전 검토 + 사용자 승인 + 즉시 중단 |
| 본문 노출 | medium | portfolio HTML에 본문 0건, feature vector만 |
| LLM 비용 폭증 | medium | 비용 상한 + 1차 10 episodes로 제한 |
| 어노테이션 신뢰도 낮음 | medium | 2-3 LLM 모델 + 사람 spot-check 5% |
| 데이터 다양성 부족 | low | 1차 통과 후 2차 확장 |

---

## 8. 승인 후 첫 작업 순서

```text
1. user-agent 정의 (WITNESS-Phase3.0-Pilot/0.1 (research))
2. fetch_helpers.py 작성 — robots.txt 자동 확인 + rate limit
3. 첫 source 1개에서 1 episode 샘플 수집
4. synopsis_v1 스키마 검증
5. 사용자 검토
6. OK면 나머지 9 episodes 수집
```

---

## 9. 한 줄 결론

```text
어떤 소스도 fetch하기 *전*에 robots.txt + ToS를 직접 확인해야 한다.
이 문서는 후보 *기록*일 뿐, 승인 전 실제 fetch는 0건.
```
