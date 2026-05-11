# WITNESS — Candidate 품질 정리 방법 및 다음 진행 지시서

## 0. 문서 목적

이 문서는 현재 Observer-to-Story Pipeline이
- candidate를 실제로 뽑아낼 수는 있으나
- 아직 “좋은 이야기 후보를 잘 고른다”기보다
- “관찰 가능한 후보를 잘 뽑는다”에 가까운 상태

라는 점을 전제로,  
**candidate 품질을 어떻게 정리할지**와  
그 다음 단계에서 무엇을 할지를 함께 정리한 실행 지시서다.

핵심 목표는 다음과 같다.

> **candidate를 더 많이 뽑는 것이 아니라,  
> 이야기로 이어질 가능성이 있는 후보를 더 잘 남기고  
> 비슷한 후보·약한 후보·탐색용 후보를 분리하는 것.**

즉 이번 단계의 목적은:
- observer를 더 키우는 것 아님
- story quality를 자동 평가하는 것 아님
- **candidate browsing 품질을 높이는 것**
이다.

---

## 1. 현재 상태 진단

현재 observer-to-story pipeline은 구조적으로는 성공이다.

### 이미 확보된 것
- candidate extractor 존재
- packet builder 존재
- 3-lens(person/event/world) 비교 가능
- render link 존재
- quality verdict 자동화 없음
- demo CLI로 browse / packet / render 가능

즉 시스템은 이미:
**“이 세계에서 후보를 발견하고, 다양한 렌즈로 살펴보고, 일부를 story render로 연결한다”**
까지는 가능하다.

하지만 현재 약점도 선명하다.

### 현재 약점
1. **candidate가 관찰 후보에 가깝다**
   - salience는 잡지만 story-worthiness는 약함

2. **late-run cluster**
   - top salient가 특정 구간에 과도하게 몰림
   - temporal diversity 부족

3. **약한 person arc**
   - 짧은 window에서 변화량이 작으면
     “안정적 / 큰 변화 없음” 반복

4. **low_activity가 다른 후보와 섞임**
   - 탐색 가치와 직접 render 가치가 다른데
     같은 후보 집합에서 경쟁 중

따라서 다음 단계는:
**기능 추가가 아니라 candidate 정리 단계**
로 가는 것이 맞다.

---

## 2. 이번 단계의 핵심 원칙

## 원칙 1 — 새 scoring system을 크게 만들지 않는다
지금 필요한 건 또 하나의 rubric가 아니다.

- massive weighted ranking 금지
- “best story” 자동 판정 금지
- creative value score 금지

대신:
- **얇은 2차 필터**
- **중복/군집 정리**
- **탐색 bucket 분리**
정도만 추가한다.

---

## 원칙 2 — 관찰 후보와 이야기 후보를 분리한다
지금까지는 둘이 섞여 있다.

앞으로는 candidate를 최소 3종으로 나눈다.

### A. Story-ready candidate
바로 render로 넘겨볼 만한 후보

### B. Observation-only candidate
읽을 가치는 있지만 바로 story로 가면 약한 후보

### C. Low-activity / latent candidate
지금은 약하지만 tension seed가 있는 후보

즉 후보를 버리는 게 아니라,
**무엇으로 쓸지 먼저 나누는 방식**으로 간다.

---

## 원칙 3 — temporal diversity를 우선 보정한다
현재 가장 선명한 UX 문제는 late-run cluster다.

따라서 다음 작업 중 1순위는
**비슷한 시점/비슷한 신호의 후보가 한꺼번에 몰리는 문제를 줄이는 것**
이다.

---

## 3. Candidate 품질 정리 방법

## 3.1 단계 1 — Temporal diversity rule 추가
### 문제
top 5 salient 후보가 거의 같은 구간에서 반복적으로 올라온다.

### 해결 방법
다음 중 최소 하나를 적용한다.

1. **min tick gap**
   - top candidate 선정 시 최소 tick 간격 규칙 추가

2. **signal family dedup**
   - 같은 signal family(예: cohort_split + saturation_lock cluster)가 연속되면
     대표 후보 1개만 상위 유지

3. **cluster summary**
   - 비슷한 후보 여러 개를 개별 candidate로 모두 올리지 않고
     하나의 cluster candidate로 요약

### 기대 효과
- browse 품질 상승
- “지금 뭘 보면 되는가”가 더 선명해짐
- 사람 검토 피로 감소

---

## 3.2 단계 2 — Render recommendation rule 보강
### 문제
render 추천은 yes인데 실제로는 story로 가면 약한 후보가 있다.
예: person lens가 “큰 변화 없음” 수준인 경우

### 해결 방법
story quality 평가가 아니라,
**render로 넘길 최소 조건**만 얇게 둔다.

예:
- person candidate는 변화량 거의 0이면 추천 해제
- event candidate는 single blip + low ripple이면 observation-only
- world candidate는 shift/residue가 약하면 direct render 비추천

### 출력 변경
기존:
- Recommended: yes / no

변경:
- `story_ready`
- `observation_only`
- `low_activity_hold`

즉 render 가능성과 candidate 가치를 분리한다.

---

## 3.3 단계 3 — Low-activity bucket 분리
### 문제
low_activity candidate가 일반 candidate와 같은 랭킹에서 경쟁한다.

### 해결 방법
low-activity 후보를 별도 bucket으로 분리한다.

예:
- Top story-ready candidates
- Top observation-only candidates
- Top low-activity / latent candidates

### 이유
low_activity는 약점이 아니라 “다른 종류의 탐색 대상”일 수 있다.  
하지만 일반 후보와 섞이면 상위 브라우징 품질을 망친다.

---

## 3.4 단계 4 — Packet wording 정리
### 문제
현재 packet은 정보는 충분하지만, 여전히 observer report 냄새가 난다.

### 해결 방법
quality verdict를 넣지 않고,
story browsing에 필요한 최소 문구만 다듬는다.

#### 추천 필드
- **Why surfaced**
- **Strongest lens**
- **Use mode**
  - story_ready
  - observation_only
  - low_activity_hold
- **Story potential**
  - person_arc
  - event_arc
  - world_arc
  - mixed_arc

즉 packet은 판정문이 아니라
**“이 후보를 어떻게 봐야 하나”를 빠르게 알려주는 카드**가 되어야 한다.

---

## 3.5 단계 5 — Near-duplicate candidate 정리
### 문제
같은 tick range / 같은 signal / 같은 world state를 거의 반복하는 후보가 생길 수 있다.

### 해결 방법
다음 중복 축을 본다.

- 같은 tick 중심
- 같은 signal family
- 같은 dominant pressure
- 같은 strongest lens
- 같은 render recommendation

중복성이 높으면:
- 대표 후보만 남기고
- 나머지는 related candidates로 접는다

---

## 4. 이번 단계 구현 범위

### 포함
- temporal diversity rule
- render recommendation 보강
- low-activity bucket 분리
- packet wording 정리
- near-duplicate candidate 정리
- validation 문서 갱신

### 제외
- story quality scoring
- public browser UI
- 새 lens 추가
- observer summary 대확장
- renderer 재시작
- anchor 대규모 확장
- Branch C 추가 실험

---

## 5. 추천 구현 순서

## Phase Q1 — Candidate curation rules
### 산출물
- `engine/observer/candidate_curation.py`

### 기능
- temporal diversity
- signal family dedup
- near-duplicate reduction
- bucket assignment

---

## Phase Q2 — Recommendation refinement
### 대상
- `engine/observer/candidate.py`
- 또는 packet builder 쪽 로직

### 목표
기존 yes/no 추천을
- story_ready
- observation_only
- low_activity_hold
로 변경

---

## Phase Q3 — Packet schema v2
### 산출물
- `scripts/observer/candidate_packet.py` 업데이트

### 변경점
- strongest lens
- use mode
- refined story potential
- related candidates (optional)

---

## Phase Q4 — Validation rerun
### 산출물
- `docs/observer/CANDIDATE_CURATION_VALIDATION.md`

### 검증 질문
1. candidate 상위 목록의 temporal diversity가 좋아졌는가
2. story-ready 후보가 실제로 더 그럴듯해졌는가
3. observation-only 후보가 분리되어 browsing이 쉬워졌는가
4. low-activity 후보가 일반 리스트를 덜 오염시키는가
5. packet만 읽어도 “어떻게 볼지” 더 빠르게 이해되는가

---

## 6. 이 단계 이후 다음 진행사항

이번 단계가 끝나면 다음은 아래 순서로 간다.

---

## Step 1 — Anchor 2개째 확장
지금은 `peter_scarcity_baseline` 하나로만 증명했다.

candidate 품질 정리가 끝나면,
그때 2번째 anchor를 붙인다.

추천:
- accusation canonical run

### 목적
- observer-to-story pipeline이 한 anchor 전용인지 확인
- 같은 규칙이 다른 pressure에서도 먹히는지 확인

---

## Step 2 — Observer-based browsing pack
이건 public UI가 아니라,
**네가 쉽게 훑어볼 수 있는 curated text pack**이다.

예:
- top 3 story-ready
- top 3 observation-only
- top 3 low-activity hold
- same candidate 3-lens compare 2세트

즉 해석기를 넣는 대신,
**쉽게 보는 패키지**를 만든다.

---

## Step 3 — Story Explorer 방향 검토
이 단계는 Q1-Q4와 Anchor 2 확장까지 끝났을 때만.

목표:
- 결과물을 더 쉽게 보는 방법
- 인물 중심 / 세계 중심 / 사건 중심 전환
- 비교/정렬/필터 강화

즉 Story Explorer는 지금이 아니라,
**candidate 품질이 정리된 뒤**에 가는 게 맞다.

---

## 7. 성공 기준

다음 중 4개 이상 만족하면 이번 단계는 성공으로 본다.

1. top candidate 목록의 시간적 다양성이 눈에 띄게 좋아진다
2. story-ready 후보가 실제로 더 이야기 후보처럼 보인다
3. observation-only 후보가 별도 구획으로 분리되어 읽기 쉬워진다
4. low-activity 후보가 메인 후보 목록을 덜 오염시킨다
5. packet만 읽어도 strongest lens와 use mode가 이해된다
6. near-duplicate 후보가 줄어든다

---

## 8. 실패 기준

다음 중 2개 이상이면 재조정 필요.

1. temporal diversity rule 넣었는데도 cluster가 그대로다
2. story-ready 후보가 여전히 약한 person arc 중심이다
3. packet wording이 여전히 보고서 같다
4. bucket 분리했는데 실제 browsing 경험이 별 차이 없다
5. candidate curation이 또 다른 rubric처럼 비대해진다

---

## 9. Claude Code용 작업 순서

### Step 1
`docs/observer/CANDIDATE_CURATION_PLAN.md` 작성

### Step 2
candidate curation rules 최소 구현
- temporal diversity
- dedup
- low-activity bucket

### Step 3
packet schema v2 업데이트

### Step 4
validation rerun

### Step 5
`CANDIDATE_CURATION_VALIDATION.md` 작성

### Step 6
성공 시 2번째 anchor 확장 계획 문서 작성
- `docs/observer/ANCHOR_2_EXPANSION_PLAN.md`

---

## 10. 한 줄 요약

**다음 단계는 observer를 더 만드는 것이 아니라,  
현재 뽑히는 candidate를 정리해서  
“관찰 후보”와 “이야기 후보”를 분리하고,  
top candidate가 실제로 더 볼 만하게 보이도록 browsing 품질을 높이는 단계다.  
그 다음에야 2번째 anchor로 확장하고,  
나중에 Story Explorer 방향으로 갈 수 있다.**
