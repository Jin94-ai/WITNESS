# WITNESS — 다음 단계 작업 지시서  
## Observer → Story Candidate Pipeline 구축 및 결과물 확인

## 0. 문서 목적

이 문서는 현재 WITNESS 프로젝트가  
- Story Output MVP 구축 완료
- Branch C external validation PASS
- Observer Layer MVP + Real-run validation 완료

상태에 도달한 뒤, **Observer Layer를 실제 결과물 파이프라인에 연결하는 다음 단계**를 정의한다.

이번 단계의 핵심 목표는 단 하나다.

> **Observer가 포착한 salient moment / split / event ripple / world shift를  
> 실제 story candidate로 연결하고,  
> 그 결과를 사람이 확인 가능한 형태로 출력하는 것.**

즉, 이번 단계가 끝나면 단순히
- observer가 있다
- story renderer가 있다

수준이 아니라,

**observer를 통해 “어떤 이야기를 뽑아낼 것인가”가 실제로 보이는 결과물**
을 확인할 수 있어야 한다.

---

## 1. 이번 단계의 최종 목표

### 목표 문장
**실제 simulation run 하나를 observer layer로 관찰하고,  
그 안에서 story-worthy candidate를 3~5개 추출해,  
각 candidate를 person / event / world 관점에서 짧게 보여주고,  
그중 일부를 실제 한국어 story output으로 연결한다.**

즉 이번 단계의 결과물은:
1. **observer가 잡은 후보**
2. **그 후보가 왜 후보인지**
3. **그 후보를 어떤 렌즈로 볼 수 있는지**
4. **그 후보가 실제 story로 어떻게 이어지는지**
를 한 번에 확인하는 것이다.

---

## 2. 왜 이 단계가 필요한가

지금까지는 크게 세 층이 따로 존재했다.

### A. Simulation / World Engine
세계가 흐른다.

### B. Observer Layer
그 흐름을 여러 시점으로 관찰할 수 있다.

### C. Story Renderer
선택된 trajectory/probe를 이야기로 바꾼다.

하지만 아직 빠진 것이 있다.

> **“관찰된 세계 중 무엇을 이야기로 볼 것인가”**

즉 지금 필요한 건:
- observer가 세계를 본다
- 그중 salient한 흐름을 후보로 뽑는다
- 그 후보를 story renderer로 보낸다

이 연결 계층이다.

---

## 3. 이번 단계의 핵심 산출물

반드시 나와야 하는 핵심 결과물은 아래 4개다.

### 3.1 Candidate List
observer가 잡은 story-worthy candidate 목록

예:
- Candidate 1 — accusation ripple with split
- Candidate 2 — scarcity saturation lock
- Candidate 3 — low-activity but high-tension person arc
- Candidate 4 — world-view blame concentration shift

### 3.2 Candidate Packet
각 candidate를 사람이 빠르게 볼 수 있게 정리한 packet

포함:
- candidate id
- 왜 뽑혔는지
- person/event/world lens 요약
- 어떤 종류 이야기로 이어질 수 있는지

### 3.3 Story Render Link
candidate 중 일부를 실제 story output으로 연결

즉 observer → candidate → story가 한 번 이어져야 한다.

### 3.4 Demo Entry
한 run에서 observer 기반으로 이야기 후보를 뽑고 확인하는 demo command

---

## 4. 이번 단계의 구현 범위

이번 단계는 **새로운 engine 확장**이 아니라  
**기존 observer와 story를 연결하는 최소 파이프라인**이다.

### 포함
- salient candidate extraction
- candidate packet 생성
- multi-lens 요약
- 일부 candidate의 renderer 연결
- demo command

### 제외
- public UI
- polished browser
- quality verdict 자동화
- asset pack 자동 생성
- Branch C 추가 실험
- 새 scenario 추가
- learned model / encoder
- observer 기능 대확장

즉 이번 단계는 **Observer-to-Story Pipeline MVP**다.

---

## 5. 이야기 후보(candidate)란 무엇인가

이 단계에서는 candidate를 지나치게 복잡하게 정의하지 않는다.

### 기본 정의
다음 중 하나 이상을 만족하면 candidate로 본다.

1. **salience spike**
   - pressure spike
   - blame target shift
   - public suspicion jump
   - authority vigilance spike

2. **split / divergence**
   - group outcome divergence
   - same anchor seed 간 차이
   - person vs world arc tension

3. **turning point**
   - recovery turn
   - saturation lock
   - mixed bifurcation
   - event ripple turning point

4. **world-heavy moment**
   - 개인보다 세계 흐름이 더 강하게 보이는 순간
   - crowd / authority / suspicion / blame가 서사를 끄는 순간

5. **low-activity but meaningful**
   - 사건은 작지만 tension이 살아 있는 순간
   - hook이 약하나 내부적으로는 유의미한 변화가 있는 구간

### 중요한 원칙
이건 story quality 평가가 아니다.  
그저 **“이건 이야기로 볼 만하다”는 후보 추출**이다.

---

## 6. Candidate 추출 방식

이번 단계에서는 과한 scoring system을 만들지 않는다.

### 6.1 Minimal scoring
각 candidate에 대해 아래 항목만 본다.

- salience score
- world signal strength
- split signal
- event ripple strength
- person arc movement
- closure potential

### 6.2 출력 방식
후보는 정렬만 하고, 자동 판정하지 않는다.

예:
- Top 5 salient candidates
- Top 3 world-heavy candidates
- Top 3 person-arc candidates
- Top 3 event-ripple candidates

### 6.3 금지
- “best story” 자동 결정
- “good / bad asset” 자동 분류
- creative value 점수화

---

## 7. Multi-lens Candidate Packet 설계

각 candidate는 아래 최소 포맷으로 출력한다.

## Candidate Packet
### A. Basic
- candidate_id
- source run
- tick range
- dominant pressure
- dominant mode
- candidate type (person / event / world / mixed)

### B. Why surfaced
- 어떤 salience rule로 올라왔는가
- split / spike / ripple / residue 등

### C. Lens summaries
- Person lens: 2~3줄
- Event lens: 2~3줄
- World lens: 2~3줄

### D. Story potential
- person arc로 읽을 수 있음
- event arc로 읽을 수 있음
- world arc로 읽을 수 있음
- 아직 hook 약함 / demo용 / strong candidate 등

### E. Render link
- 이 candidate를 실제 story render로 넘길지 여부
- 넘긴다면 어떤 렌즈로 넘길지

### F. Human check
- keep
- interesting
- revise later
- skip

### 원칙
여기서도 시스템은 추천만 하고 판정은 사람에게 남긴다.

---

## 8. 이번 단계에서 꼭 확인해야 하는 결과물

이번 단계가 성공하면, 아래 3가지를 직접 볼 수 있어야 한다.

### 8.1 Observer가 story candidate를 잡아낸다
즉 observer output이 단순 정보 열람이 아니라  
“어, 이건 이야기로 볼 수 있겠네” 수준까지는 가야 한다.

### 8.2 같은 candidate를 여러 렌즈로 볼 수 있다
예:
- person lens로 보면 두려움의 흔들림
- world lens로 보면 blame 집중
- event lens로 보면 accusation ripple

즉 같은 세계 흐름이 관점에 따라 다르게 읽히는 것이 보이면 성공이다.

### 8.3 일부 candidate는 실제 story output으로 이어진다
즉 observer가 그냥 관찰로 끝나지 않고,
**story renderer와 실제로 연결되는 것**
이 확인되어야 한다.

---

## 9. 구현 순서

## Phase P1 — Candidate Extractor
### 산출물
- `engine/observer/candidate.py`

### 기능
- snapshot stream / observer outputs에서 candidate 추출
- salience / split / world-heavy / event-ripple 기준으로 정렬

### 최소 API 예시
```python
extract_story_candidates(run_id, top_k=5)
extract_world_candidates(run_id, top_k=3)
extract_person_candidates(run_id, top_k=3)
extract_event_candidates(run_id, top_k=3)
```

---

## Phase P2 — Candidate Packet Builder
### 산출물
- `scripts/observer/candidate_packet.py`

### 기능
- candidate를 사람이 읽기 쉬운 packet으로 변환
- person/event/world lens를 함께 요약
- tick range와 핵심 변화 정리

### 출력
- text packet
- markdown packet
- compact packet

---

## Phase P3 — Candidate-to-Story Link
### 산출물
- `scripts/observer/render_candidate_story.py`

### 기능
- 선택된 candidate를 story renderer로 연결
- 동일 candidate를 person/event/world 프레임 중 하나로 렌더링
- 최소 2~3개 샘플 생성

### 목표
observer → story 연결이 실제로 된다는 증명

---

## Phase P4 — Demo Command
### 산출물
- `examples/demo_observer_story.py`

### 지원 모드
- `--list-candidates`
- `--packet <candidate_id>`
- `--render-story <candidate_id>`
- `--compare-lenses <candidate_id>`

### 목표
한 번의 run으로 observer 기반 story selection을 시연 가능하게 만들기

---

## Phase P5 — Validation / Review
### 산출물
- `docs/observer/OBSERVER_TO_STORY_VALIDATION.md`
- `docs/observer/OBSERVER_TO_STORY_REVIEW.md`

### 검증 질문
1. candidate가 실제로 이야기 후보처럼 보이는가
2. multi-lens가 의미 있게 다르게 읽히는가
3. observer가 story selection에 실제 도움을 주는가
4. 단순 renderer보다 더 좋은 진입점을 제공하는가

---

## 10. 추천 입력 run

### 1순위
**Peter scarcity baseline canonical run**

이유:
- 기존 story/creative 자산과 연결됨
- world-side pressure가 선명함
- split / saturation / mixed를 보기 좋음

### 2순위
accusation canonical run

첫 단계는 1개만으로 충분하다.

---

## 11. 성공 기준

다음 중 4개 이상 만족하면 이번 단계는 성공으로 본다.

1. observer가 뽑은 candidate 3~5개가 실제로 story-worthy하게 보인다
2. 같은 candidate를 person/event/world lens로 볼 때 차이가 느껴진다
3. candidate packet만 읽어도 “왜 이게 후보인지” 이해된다
4. 최소 2개 candidate가 실제 story output으로 자연스럽게 이어진다
5. observer가 story selection의 앞단으로서 유용하다는 느낌이 든다
6. 시스템이 quality verdict를 하지 않으면서도 탐색 효율은 올라간다

---

## 12. 실패 기준

다음 중 2개 이상이면 재설계가 필요하다.

1. candidate가 그냥 salience log처럼만 보인다
2. multi-lens 차이가 거의 없다
3. packet이 story 후보를 설명하기보다 또 다른 보고서처럼 느껴진다
4. observer를 거쳐도 renderer로 가는 연결 이점이 약하다
5. candidate scoring이 또 다른 rubric처럼 비대해진다

---

## 13. 다음 단계 이후 분기

## 경우 A — 성공
- Observer-to-Story Pipeline freeze 검토
- Story Explorer / Browser 방향 검토
- curated observation pack or internal browsing tool로 확장

## 경우 B — 일부 약함
- candidate extractor 또는 packet만 국소 수정
- real run 한 번 더 검증

## 경우 C — 전반적으로 약함
- observer narrative summary 축소
- candidate logic 단순화
- story link를 person/event/world 중 한 축만 남겨 재검증

---

## 14. 지금 하지 말아야 할 것

- public browser UI
- story quality 자동 판정
- 더 많은 렌즈 추가
- candidate 점수 체계 비대화
- Branch C 추가 실험
- Talleyrand scenario
- PyTorch encoder
- renderer 재시작
- polished asset pack 자동화

즉 지금은 **연결 MVP**가 목표다.

---

## 15. Claude Code용 작업 순서

### Step 1
`docs/observer/OBSERVER_TO_STORY_PIPELINE.md` 작성  
(이 문서를 canonical plan으로 옮기기)

### Step 2
candidate extractor 최소 구현

### Step 3
candidate packet builder 구현

### Step 4
2~3개 candidate의 실제 story render 연결

### Step 5
`examples/demo_observer_story.py` 구현

### Step 6
`OBSERVER_TO_STORY_VALIDATION.md`와 `REVIEW.md` 작성

---

## 16. 최종 한 줄 요약

**다음 단계가 끝나면, Observer Layer가 단순한 세계 관찰 도구를 넘어  
실제로 “이 세계에서 어떤 이야기를 뽑아낼 것인가”를 도와주는 파이프라인으로 작동하는 결과물을 확인할 수 있어야 한다.  
즉 이번 단계의 목표는 Observer를 더 만드는 것이 아니라,  
Observer가 story candidate를 잡아내고 그것이 실제 한글 이야기로 이어지는 걸 보여주는 것이다.**
