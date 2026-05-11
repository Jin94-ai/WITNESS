# WITNESS Next Plan — Phase 2.9 Portfolio Finalization + Phase 3.0 Data Pilot Prep

> 기준일: 2026-05-10  
> 목표: Phase 2.8 Genre Adapter Polish를 닫고, WITNESS를 포트폴리오 메인 구조로 정리한 뒤,  
> 실제 외부 데이터를 사용하는 Phase 3.0 Data & Annotation Pilot에 들어가기 위한 승인·검토·설계 문서를 준비한다.

---

## 0. 현재 상태

WITNESS는 현재 다음 단계까지 완료되었다.

```text
Phase 0    Skeleton Cleanup              DONE
Phase 1    Data Infra                    INFRA READY
Phase 2    Annotation Prep               PREP READY
Phase 2.5  Validation Fix                DONE
Phase 2.75 Genre Adapter MVP             DONE
Phase 2.8  Genre Adapter Polish          DONE
Phase 3.0  Data & Annotation Pilot       USER APPROVAL NEEDED
Phase 3.1+ ML / Flesh Engine             BLOCKED UNTIL PHASE 3.0 PASSES
Phase 6    Portfolio integration         PARTIAL
```

현재 핵심 산출물:

```text
docs/portfolio/demo_genre_comparison/index.html
docs/portfolio/demo_genre_comparison/comparison.json
docs/portfolio/demo_genre_comparison/comparison.md
docs/plans/GENRE_ADAPTER_POLISH_AUDIT.md
content/genres/korean_morning_melodrama/rulebook.json
content/genres/japanese_quiet_drama/rulebook.json
```

핵심 결론:

```text
SkeletonOutput v1.1
→ Rulebook-driven Genre Adapter
→ Cross-genre comparison
→ Hard audit pass
→ Soft quality warnings 0
```

따라서 Phase 2.8은 닫아도 된다.

---

## 1. 이번 단계 이름

```text
Phase 2.9 — Portfolio Finalization + Phase 3.0 Data Pilot Prep
```

이번 단계는 구현 확장이 아니라 **정리와 진입 준비**다.

목표:

```text
1. demo_genre_comparison을 포트폴리오 메인으로 확정
2. README / docs index / portfolio hierarchy 정리
3. version 관계 정리
4. Phase 3.0 Data Pilot 승인 문서 준비
5. 데이터 소스 후보 검토
6. mini pilot 설계
```

하지 않을 것:

```text
- 실제 외부 데이터 fetch
- LLM API 호출
- ML 학습
- 새 장르 추가
- 원문 synopsis repo 저장
- 대사 생성
- 긴 소설 생성
```

---

## 2. 왜 Phase 2.9가 필요한가

현재 기술 구조는 많이 좋아졌지만, 외부인이 처음 볼 때 여전히 다음 질문이 생길 수 있다.

```text
1. 지금 메인 데모가 무엇인가?
2. Peter demo와 Genre Comparison demo 중 무엇이 대표인가?
3. ML Flesh Engine은 이미 된 것인가, 앞으로 할 것인가?
4. SkeletonOutput v1과 UniversalStorySeed v1.1의 관계는 무엇인가?
5. Phase 3.0으로 넘어가기 전에 외부 데이터 사용은 안전한가?
```

Phase 2.9는 이 혼란을 제거하는 단계다.

---

## 3. 현재 포트폴리오 메인 판단

이제 WITNESS의 메인 포트폴리오 asset은 다음으로 잡는다.

```text
docs/portfolio/demo_genre_comparison/index.html
```

이유:

```text
- 같은 universal skeleton을 두 장르로 변환한다.
- 한국 막장 드라마 vs 일본 정적 드라마의 차이가 바로 보인다.
- rulebook-driven adapter 구조가 드러난다.
- 하드코딩된 단일 문장이 아니라 장르 lens에 따른 변환임을 보여준다.
- audit 결과가 함께 붙어 있다.
- Phase 3 ML/Flesh Engine으로 이어질 명분이 생긴다.
```

기존 데모 위치 조정:

```text
Main:
- demo_genre_comparison

Appendix:
- Peter portfolio demo
- Life Arc demo
- Story Seed Cards
- SkeletonOutput
- Genre Adapter audit reports
- Earlier visual prototypes / frozen tracks
```

---

## 4. 수정 필요 사항

---

# Issue 1 — README 첫 문장 정정

## 문제

현재 README 상단은 다음 뉘앙스를 가질 수 있다.

```text
결정론적 서사 시뮬레이션 엔진 + ML로 학습된 Narrative Mode 변환기
```

하지만 현재 ML Flesh Engine은 아직 완료되지 않았다.  
현재 완료된 것은 rule-based Genre Adapter다.

## 수정 방향

README 첫 설명은 다음처럼 수정한다.

```text
WITNESS는 결정론적 서사 시뮬레이션 엔진(뼈대)과 장르 변환기(살)를 분리한 포트폴리오 프로젝트입니다.

현재 버전은 SkeletonOutput v1.1을 기반으로, rule-based Genre Adapter를 통해 같은 이야기 뼈대를 서로 다른 장르 문법으로 변환합니다.

ML 기반 Flesh Engine은 Phase 3.0 Data & Annotation Pilot 이후 진행할 예정입니다.
```

영어 보조 문장:

```text
WITNESS currently demonstrates a rule-based genre adaptation layer.
The ML-based Flesh Engine is planned after the Phase 3.0 data and annotation pilot.
```

## Acceptance

```text
[ ] README가 ML Flesh Engine을 완료된 것으로 표현하지 않는다.
[ ] 현재 완료된 것은 rule-based Genre Adapter라고 명시한다.
[ ] demo_genre_comparison을 portfolio main으로 명시한다.
```

---

# Issue 2 — Schema version 관계 명시

## 문제

현재 산출물에는 다음 버전들이 같이 등장한다.

```text
SkeletonOutput container: skeleton_output_v1
UniversalStorySeed: universal_story_seed_v1_1
GenreAdaptedOutput: genre_adapted_output_v1_1
GenreComparisonOutput: genre_comparison_output_v1
```

이 자체는 문제는 아니지만, 문서화하지 않으면 헷갈릴 수 있다.

## 수정 방향

문서에 명시한다.

```text
SkeletonOutput container는 v1 family를 유지한다.
내부 UniversalStorySeed contract는 RFC-0001에 따라 v1.1로 확장되었다.
GenreAdaptedOutput은 Phase 2.8에서 v1.1로 확장되었다.
GenreComparisonOutput은 cross-genre wrapper이므로 v1으로 시작한다.
```

권장 신규 파일:

```text
docs/specs/NARRATIVE_SCHEMA_VERSION_MAP.md
```

## Acceptance

```text
[ ] schema version 관계 문서 존재
[ ] README 또는 docs/INDEX에서 링크
[ ] Phase 3 consumer가 어떤 필드를 읽어야 하는지 명시
```

---

# Issue 3 — comparison output 존재 반영

## 현재 상태

`docs/portfolio/demo_genre_comparison/comparison.json`은 존재한다.

따라서 이전 보완 항목:

```text
genre_comparison_output.json 생성 필요
```

은 완료 처리한다.

## 추가 정리

단, 파일명이 `comparison.json`이므로 문서에서 이름을 명확히 쓴다.

```text
docs/portfolio/demo_genre_comparison/comparison.json
```

선택적으로 machine-readable canonical copy를 추가할 수 있다.

```text
data/narrative/genre_comparison_output.json
```

권장:

```text
- docs/portfolio/demo_genre_comparison/comparison.json 유지
- data/narrative/genre_comparison_output.json mirror 생성
```

이 mirror는 필수는 아니지만, 데이터 산출물 위치를 일관화하려면 좋다.

## Acceptance

```text
[ ] audit 문서와 README가 comparison.json 존재를 반영
[ ] 선택 시 data/narrative mirror 생성
```

---

# Issue 4 — 작은 표현 polish

## 문제

일부 문장이 여전히 약간 기계적이다.

예:

```text
망설이는 사람의 망설임은 주변의 의심을 키운다.
```

## 수정 방향

rulebook template을 다듬는다.

추천:

```text
망설이는 시간이 길어질수록 주변의 의심은 커진다.
```

또는:

```text
결정을 미루는 시간이 길어질수록 주변의 의심은 커진다.
```

한국 장르 S03:

```text
알아차리지만 말하지 않는 사람은 변화를 알아차리지만 아직 말하지 않는다.
```

추천:

```text
알아차린 사람은 변화를 눈치채지만 아직 말하지 않는다.
```

일본 장르는 현재 상대적으로 자연스럽다.  
다만 다음 표현은 조금 다듬을 수 있다.

```text
곁에서 숨을 고르는 사람의 망설임이 공기 속 거리를 조금씩 더한다.
```

추천:

```text
곁에서 숨을 고르는 사람의 망설임은 두 사람 사이의 거리를 조금씩 넓힌다.
```

## Acceptance

```text
[ ] 중복 명사 표현 제거
[ ] 한국/일본 outline 모두 자연스럽게 읽힘
[ ] quality_warnings 0 유지
[ ] audit pass 유지
```

---

# Issue 5 — Portfolio hierarchy 정리

## 문제

README와 docs index에 과거 데모가 많이 남아 있어 현재 메인 흐름이 흐려질 수 있다.

## 수정 방향

포트폴리오 hierarchy를 다음처럼 재정렬한다.

```text
Main Portfolio Demo
1. Genre Comparison Demo
   - 같은 universal skeleton → 두 장르 변환
   - 현재 대표 산출물

Core Evidence
2. SkeletonOutput sample
3. GenreComparisonOutput sample
4. Genre Adapter Polish Audit
5. UniversalStorySeed RFC

Appendix
6. Peter Story Demo
7. Life Arc Demo
8. Story Candidate Cards
9. Visual prototypes / frozen tracks
```

수정 대상:

```text
README.md
docs/INDEX.md
docs/portfolio/README.md
```

## Acceptance

```text
[ ] 메인 포트폴리오 asset이 demo_genre_comparison으로 보인다.
[ ] Peter / Life Arc는 appendix로 내려간다.
[ ] audit / schema / RFC 문서가 evidence로 연결된다.
```

---

## 5. Phase 2.9 산출물

이번 단계에서 만들어야 할 파일:

```text
docs/plans/PHASE_2_9_PORTFOLIO_FINALIZATION_PLAN.md
docs/specs/NARRATIVE_SCHEMA_VERSION_MAP.md
docs/plans/PHASE_3_0_DATA_PILOT_PREP.md
docs/plans/DATA_SOURCE_CANDIDATE_REVIEW.md
docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md
```

수정할 파일:

```text
README.md
docs/INDEX.md
docs/portfolio/README.md
content/genres/korean_morning_melodrama/rulebook.json
content/genres/japanese_quiet_drama/rulebook.json
```

선택적 생성:

```text
data/narrative/genre_comparison_output.json
```

---

## 6. Phase 3.0 Data & Annotation Pilot 준비

Phase 3.0은 외부 데이터를 처음 도입하는 단계다.  
따라서 바로 fetch하지 말고, 먼저 후보 검토와 승인 문서를 만든다.

---

# 6.1 승인 5건

Phase 3.0을 실제로 시작하려면 사용자 승인이 필요하다.

```text
1. 실제 줄거리 데이터 fetch 승인
2. 출처별 ToS / robots.txt 검토 승인
3. LLM API 사용 승인
4. 비용 상한 승인
5. 저장 위치 / 공개 가능성 결정
```

이 승인 전까지는 다음을 하면 안 된다.

```text
- 외부 사이트 scrape / fetch
- LLM API 호출
- 원문 synopsis 저장
- 모델 학습
```

---

# 6.2 Mini Pilot 범위

처음부터 40개를 수집하지 않는다.

권장 1차:

```text
1 genre
2 titles
5 episodes each
총 10 episode synopses
```

성공 시 확장:

```text
2 genres
2 titles each
10 episodes each
총 40 episode synopses
```

---

# 6.3 Data Source Candidate Review

작성 문서:

```text
docs/plans/DATA_SOURCE_CANDIDATE_REVIEW.md
```

포함할 표:

```text
source_name
genre
official_or_unofficial
url
robots_txt_status
tos_status
copyright_risk
fetch_difficulty
public_repo_allowed
notes
recommendation
```

우선순위:

```text
1. 공식 방송사 회차 소개
2. 공식 스트리밍 플랫폼 공개 synopsis
3. 위키/팬덤 요약은 보조 참고
4. 개인 블로그/리뷰는 비추천
```

---

# 6.4 저장 정책

권장 저장 구조:

```text
data/external_private/synopsis_raw/
data/annotation/phase3_pilot/
data/annotation/phase3_pilot/features/
data/annotation/phase3_pilot/reports/
```

공개 repo 정책:

```text
원문 synopsis: 비공개 / local-only 권장
annotation feature vector: 공개 가능
derived metrics: 공개 가능
short evidence quote: 내부 audit용 우선
portfolio HTML: 원문 본문 노출 금지
```

---

# 6.5 Annotation Pilot

기존 Phase 2 annotation infra를 사용한다.

입력:

```text
episode synopsis
genre label
title metadata
episode number
```

출력:

```text
annotation feature vector
evidence quotes
hallucination check result
inter-annotator correlation
```

LLM 구성:

```text
2-model pilot first
3-model pilot if cost allows
```

측정:

```text
hallucination quote rate
inter-annotator Pearson r
feature reliability grade
manual spot-check
```

성공 기준:

```text
hallucination quote rate < 5%
inter-annotator r >= 0.7 for at least 4-5 features
manual spot-check pass
data card complete
```

실패 시:

```text
feature definition 수정
prompt template 수정
low reliability feature 제거
data source 교체
LLM model 조합 변경
```

---

## 7. Phase 3.0 문서 설계

---

# 7.1 PHASE_3_0_DATA_PILOT_PREP.md

내용:

```text
- 목적
- 범위
- 승인 필요 항목
- 데이터 소스 후보
- pilot size
- 저장 정책
- annotation 계획
- reliability 기준
- 중단 조건
```

---

# 7.2 DATA_SOURCE_CANDIDATE_REVIEW.md

내용:

```text
- 후보 source list
- ToS / robots.txt 상태
- 저작권 위험
- fetch 가능성
- 공개 repo 가능 여부
- 추천 / 보류 / 제외 판정
```

---

# 7.3 PHASE_3_0_APPROVAL_CHECKLIST.md

내용:

```text
[ ] fetch 승인
[ ] ToS 검토 승인
[ ] LLM API 승인
[ ] 비용 상한 승인
[ ] 저장 위치 승인
[ ] 공개 repo 정책 승인
[ ] 10-episode mini pilot 승인
```

---

## 8. Phase 2.9 Acceptance Criteria

```text
[ ] README 첫 문장이 현재 상태와 일치한다.
[ ] ML Flesh Engine이 완료된 것으로 표현되지 않는다.
[ ] demo_genre_comparison이 portfolio main으로 지정된다.
[ ] Peter / Life Arc는 appendix로 내려간다.
[ ] schema version map 문서가 생긴다.
[ ] comparison.json 존재가 docs에 반영된다.
[ ] 작은 표현 polish가 적용된다.
[ ] quality_warnings 0 유지.
[ ] Phase 3.0 준비 문서 3개가 생성된다.
[ ] 실제 fetch / LLM / ML 실행 0건.
[ ] fast suite 회귀 0.
```

---

## 9. No-Go Criteria

아래 중 하나라도 발생하면 Phase 2.9 실패다.

```text
- README가 ML Flesh Engine을 이미 완료된 것으로 표현
- demo_genre_comparison이 메인으로 보이지 않음
- comparison.json과 docs 내용 불일치
- 외부 데이터 fetch 발생
- LLM API 호출 발생
- 원문 synopsis repo 저장
- Phase 3.0 승인 체크리스트 없음
```

---

## 10. 다음 에이전트 Directive

```text
WITNESS Phase 2.9 — Portfolio Finalization + Phase 3.0 Prep directive

목표:
Phase 2.8 Genre Adapter Polish는 GO로 확정한다.
다음은 포트폴리오 메인 정리와 Phase 3.0 Data & Annotation Pilot 준비다.

제약:
- 실제 fetch 금지
- LLM API 호출 금지
- ML 학습 금지
- 새 장르 추가 금지
- 원문 synopsis repo 저장 금지
- engine simulation core 수정 금지
- visual track 수정 금지

작업:
1. README 첫 문장을 현재 상태와 맞게 수정한다.
   - 완료된 것은 rule-based Genre Adapter.
   - ML Flesh Engine은 Phase 3 이후 예정.
   - demo_genre_comparison을 portfolio main으로 지정.

2. schema version map 문서를 작성한다.
   - docs/specs/NARRATIVE_SCHEMA_VERSION_MAP.md
   - SkeletonOutput container v1
   - UniversalStorySeed v1.1
   - GenreAdaptedOutput v1.1
   - GenreComparisonOutput v1

3. comparison.json 존재를 docs에 반영한다.
   - docs/portfolio/demo_genre_comparison/comparison.json
   - 필요하면 data/narrative/genre_comparison_output.json mirror 생성.

4. 작은 표현 polish를 적용한다.
   - “망설이는 사람의 망설임” 제거.
   - “알아차리지만 말하지 않는 사람은 변화를 알아차리지만” 제거.
   - quality_warnings 0 유지.

5. portfolio hierarchy를 정리한다.
   - Main: demo_genre_comparison
   - Evidence: skeleton_output / comparison.json / audit reports / RFC
   - Appendix: Peter demo / Life Arc / old visual prototypes

6. Phase 3.0 준비 문서 작성.
   - docs/plans/PHASE_3_0_DATA_PILOT_PREP.md
   - docs/plans/DATA_SOURCE_CANDIDATE_REVIEW.md
   - docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md

7. Mini pilot을 작게 설계한다.
   - 1 genre
   - 2 titles
   - 5 episodes each
   - total 10 synopses

Acceptance:
- README가 현재 상태와 모순되지 않는다.
- comparison output 존재가 반영된다.
- schema version 관계가 명확하다.
- Phase 3.0 승인 체크리스트가 존재한다.
- 실제 외부 작업 0건.
- fast suite 회귀 0.
```

---

## 11. Phase 2.9 이후 진행 순서

```text
1. 사용자에게 Phase 3.0 승인 항목 제시
2. 승인된 범위 안에서 source 후보 조사
3. ToS / robots.txt 검토
4. 10-episode mini pilot dataset 수집
5. 2-model annotation pilot
6. quote hallucination 검사
7. inter-annotator reliability 계산
8. reliability report 작성
9. Phase 3.1 ML/Flesh Engine 진입 여부 결정
```

---

## 12. 한 줄 결론

Phase 2.8까지의 기술 증명은 완료됐다.  
이제 중요한 것은 “더 구현”이 아니라, **포트폴리오 메인 정리와 외부 데이터 사용 전 안전한 준비**다.

> 다음 단계는 Phase 2.9 Portfolio Finalization + Phase 3.0 Data Pilot Prep이다.

---

*End of plan.*
