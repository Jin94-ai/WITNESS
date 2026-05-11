# WITNESS — 실제로 이야기를 확인하는 가이드

> 이 가이드는 [WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md](WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md)
> Stage E (Human Pick Test)를 위한 운영 매뉴얼이다. 시스템이 *Stage A-D + F를 자동으로* 실행한 후,
> *사람이 실제로 보고 판단하는 단계*를 어떻게 진행할지 설명한다.
>
> 마지막 갱신: 2026-05-08.

---

## 0. 한 줄 요약

WITNESS는 시뮬레이션에서 **이야기 후보 4개**(S01-S04)를 추출했고, 각 후보에 대해 **Scene Brief + 1-page Treatment**가 자동 생성됐다. 당신이 할 일은 **이걸 *실제로 읽어보고* 진짜 이야기로 발전시킬 수 있는지 판단**하는 것 — 자동 점수와 다를 수 있는 인간 직관 검증.

---

## 1. 어디서 무엇을 봐야 하는가

### 1.1 5초 안에 결과 확인

```bash
# 모든 산출물 한번에 빌드
python scripts/narrative/build_story_viability_report.py

# 메인 리포트 (한 화면)
cat docs/portfolio/STORY_VIABILITY_REPORT.md | head -30
# → "Summary" 표 + Strongest Candidate
```

### 1.2 깊이별 추천 읽기 순서

| 시간 | 보는 것 | 무엇을 알 수 있나 |
|---|---|---|
| 30초 | [STORY_VIABILITY_REPORT.md](portfolio/STORY_VIABILITY_REPORT.md) §1 Summary 표 | 4 후보의 점수 / 등급 / 감사 결과 한눈에 |
| 2분 | [STORY_VIABILITY_REPORT.md](portfolio/STORY_VIABILITY_REPORT.md) §2 Strongest Candidate | 가장 강한 후보 (S01 Peter) 요약 |
| 5분 | [SCENE_BRIEFS.md](portfolio/SCENE_BRIEFS.md) S01 카드 | Scene 단위로 *어떻게 쓸 수 있는지* |
| 10분 | [ONE_PAGE_TREATMENTS.md](portfolio/ONE_PAGE_TREATMENTS.md) S01 카드 | 3-act + adaptation notes (film/novel/game) |
| 30분 | 4 카드 모두 + 후보 간 비교 | *어느 게 가장 쓸 만한지* 판단 |

### 1.3 산출물 개관 (현재 상태, peter_scarcity_baseline)

```
docs/portfolio/STORY_VIABILITY_REPORT.md     ← 종합 리포트 (메인)
docs/portfolio/SCENE_BRIEFS.md               ← 4 scene briefs
docs/portfolio/ONE_PAGE_TREATMENTS.md        ← 4 treatments
docs/portfolio/STORY_CANDIDATES.md           ← 원본 candidate cards
docs/portfolio/CROSS_SEED_STORY_PATTERNS.md  ← 5 seeds robustness

data/narrative/story_viability_scores.json   ← Stage D scores
data/narrative/story_viability_audit.json    ← Stage F audit
data/narrative/story_candidates.json         ← Stage A normalized
```

**현재 결과 요약** (자동):
- 4 candidates / **1 strong_viable + 3 viable_with_gaps** / **0 audit_fail**
- 가장 강한 것: **S01 — Peter / loyalty_vs_survival** (Plan §15 Ship 조건 충족)

---

## 2. Stage E — Human Pick Test 진행 방법

자동 평가는 *시스템이 자기 자신을 채점*한 결과다. *진짜 검증*은 **사람 3명 이상**이 직접 읽어보는 것.

### 2.1 누구에게 보여줄 것인가

| 리뷰어 유형 | 묻기 좋은 질문 |
|---|---|
| 소설 / 에세이 쓰는 사람 | "Novel chapter로 발전 가능?" |
| 영상 / 영화 관심자 | "10-15분 단편으로 가능?" |
| 게임 기획 관심자 | "loyalty / silence / confess 분기 만들 만한가?" |
| 일반 독자 | "이 후보 끝까지 읽어볼 마음이 드나?" |

**최소 3명**. 가능한 *서로 다른 매체* 관심자.

### 2.2 무엇을 보여줄 것인가

**가장 간단한 방법**: **단일 파일 [HUMAN_PICK_TEST_PACK.md](portfolio/HUMAN_PICK_TEST_PACK.md)** 를 그대로 메일/메시지로 보낸다. self-contained — 4 후보 카드 + 7 질문 + 응답 양식이 한 파일에 다 있음. 5분 안에 응답 가능.

대안 (자세히 보고 싶은 리뷰어): 후보별 3 카드도 추가:

1. STORY_CANDIDATES.md의 해당 카드 (premise + arc + turning points + creative uses)
2. SCENE_BRIEFS.md의 해당 카드 (6 progression sections)
3. ONE_PAGE_TREATMENTS.md의 해당 카드 (3 acts + adaptation notes)

### 2.3 7개 질문 (per candidate)

리뷰어에게 메일 / 메시지 / 인터뷰로 묻기:

```
[질문 — 5분 안에 응답 가능]

이 카드를 보고 답해주세요. 솔직하게.

1. 이 후보로 장면 / 에피소드 / 퀘스트를 *실제로* 만들 수 있다고 느끼나요?
   1=전혀 / 2=어렵다 / 3=어쩌면 / 4=가능 / 5=확실히

2. 4개 후보 중 가장 *쓰고 싶은* 후보는 무엇인가요? (S01-S04)

3. 왜 그 후보를 골랐나요? (한 문장)

4. 부족한 정보는 무엇인가요?
   (예: 장면 위치 / 인물 관계 / 사건의 구체성 / ...)

5. *데이터처럼* 느껴지는 문장이 있다면 어디인가요?

6. *억지로 이야기화*한 느낌이 드는 부분은 어디인가요?

7. 이 후보가 가장 적합한 매체는?
   film / novel / game / drama / none
```

### 2.4 통과 기준 (per 후보)

리뷰어 응답을 모은 뒤:

```
human_pick_score = 평균(질문 1) / 5
selection_rate = 그 후보를 고른 사람 수 / 전체 리뷰어 수
```

**Plan §9 Pass criteria**:
- `human_pick_score ≥ 0.70` (즉 평균 3.5/5 이상)
- `selection_rate ≥ 1/3` (3명 중 1명 이상 그걸 고름)
- *큰 over-inference 불만 없음* (질문 6에서 동일 부분 지적이 반복되지 않음)

### 2.5 응답 수집 → 자동 점수화

```bash
# Step 1: 템플릿 복사
cp data/narrative/human_pick_responses_template.json \
   data/narrative/human_pick_responses.json

# Step 2: 응답 입력 (3 reviewers의 답을 JSON에 채움)
# - reviewers[].id 부여 (R1, R2, R3 또는 익명)
# - 각 후보별 q1 (1-5), q4-q6 (자유), q7 (film/novel/game/drama/none)
# - q2_top_pick + q3_pick_reason

# Step 3: 자동 점수화 + Plan §9 통과 판정
python scripts/narrative/aggregate_human_pick.py
# → docs/portfolio/HUMAN_PICK_RESULT.md (사람이 읽는 결과)
# → data/narrative/human_pick_results.json (machine-readable)
```

**1명만 응답해도 baseline 분석 가능**. 단 통과 판정은 *최소 3명* 권장.

---

## 3. 평가 시 참고할 수 있는 framing

### 3.1 자동 점수 vs 인간 직관 차이가 클 때

| 자동 점수 | 인간 평가 | 의미 |
|---|---|---|
| strong_viable / 사람도 "쓸 수 있다" | ✅ Ship | Plan §15 Ship 조건 |
| strong_viable / 사람은 "데이터 시트" | ⚠️ 문제 — 점수 계산 너무 관대 | 점수 가중치 재조정 필요 |
| weak_seed / 사람은 "흥미롭다" | ⚠️ 점수가 인간 직관 못 잡음 | 새 factor 추가 검토 |
| not_viable / 사람도 "안 쓸 것" | ✅ Drop 정직 | scope 명확화 |

### 3.2 카드를 평가할 때 본인 스스로 체크리스트

읽으면서 *체크 표시*:

```
[ ] Main character가 누구인지 5초 안에 알겠다
[ ] 무엇을 원하고 무엇이 위협하는지 보인다
[ ] 시작과 끝이 다르다 (변화가 있다)
[ ] 적어도 한 *전환*이 보인다 (turning point)
[ ] 다음 장면을 부르는 *질문*이 남는다
[ ] 영화 / 소설 / 게임 중 어디로 가져갈지 떠오른다
[ ] *근거 없는 사건*이 추가된 흔적이 없다
[ ] 텔레메트리 (수치 / agent_03)가 메인 surface에 노출 안 됐다
```

5개 이상 체크 = strong 후보.

---

## 4. 후보를 *진짜 이야기*로 발전시키는 방법 (창작 단계)

### 4.1 Stage E 통과한 후 — 다음 단계

WITNESS는 *이야기 본문 생성을 의도적으로 안 한다* (plan §10.2). 통과한 후보를 받으면 **창작자가 직접** 다음 중 하나로:

| 매체 | 출발점 | 추가 결정해야 할 것 |
|---|---|---|
| **단편 소설 (5,000-10,000자)** | Scene Brief의 4 progression | 시점 (1인칭 / 3인칭) / 시간 / 장소 / 관계 구체화 |
| **단편 영화 (10-15분)** | 1-page Treatment의 3 acts | 대사 / 배우 / 촬영 장소 / 분위기 |
| **게임 퀘스트 분기** | unresolved_question + adaptation hook (game) | 플레이어 선택 (3-5 갈래) / 결과 / NPC 반응 |
| **방송 에피소드** | Treatment + relationship_dynamics | 인물 등장 순서 / B-plot / 결말 |

**핵심**: Scene Brief / Treatment는 *seed*다. 나머지는 작가의 영역.

### 4.2 추가 데이터가 필요할 때

후보를 발전시키다가 *시뮬레이션의 더 깊은 맥락*이 필요하면:

```bash
# 특정 candidate의 evidence 전체 읽기
python -c "
import json
d = json.load(open('data/narrative/story_candidates.json',encoding='utf-8'))
c = next(x for x in d['candidates'] if x['story_candidate_id']=='S01')
print('Turning points:')
for tp in c['key_turning_points']:
    print(f\"  t{tp['tick']}: {tp['summary']}\")
print('\\nProvenance:')
print(c['provenance_summary'])
"

# 원본 thread + 모든 linked moments
python -c "
import json
threads = json.load(open('data/narrative/story_threads.json',encoding='utf-8'))
moments = json.load(open('data/narrative/moments.json',encoding='utf-8'))
t = next(x for x in threads['threads'] if x['thread_id']=='T01')
print(f'Thread {t[\"thread_id\"]} — {len(t[\"moment_ids\"])} moments:')
m_by_id = {m['moment_id']:m for m in moments['moments']}
for mid in t['moment_ids']:
    m = m_by_id.get(mid)
    if m: print(f\"  t{m['tick']:>3}: {m['summary']}\")
"
```

### 4.3 다른 시뮬레이션 결과를 보고 싶을 때

다른 seed로 새 candidate set 생성:

```bash
# seed 7로 시뮬레이션 → 새 후보 set
python scripts/visual/export_dot_observer_data.py --seed 7 --output data/visual/dot_observer_data_seed7.json
python scripts/narrative/build_moments.py --input data/visual/dot_observer_data_seed7.json --output data/narrative/moments_s7.json
python scripts/narrative/build_story_threads.py --moments data/narrative/moments_s7.json --threads data/narrative/threads_s7.json --run-label peter_scarcity_baseline_s7
python scripts/narrative/export_narrative_opportunities.py --threads data/narrative/threads_s7.json --moments data/narrative/moments_s7.json --out-md /tmp/ops_s7.md --out-json /tmp/ops_s7.json
# 후속 build_story_candidates / build_story_viability_report 적용
```

### 4.4 다른 anchor (peter / vangogh / talleyrand)에서 보고 싶을 때

```bash
# vangogh anchor (8 agents, 조용한 시나리오)
python scripts/visual/export_dot_observer_data.py --anchor vangogh_sacred_baseline --seed 0 --output data/visual/dot_observer_data_vangogh.json
# 같은 narrative pipeline 적용
# 단, content/anchors/vangogh_sacred_baseline/identity_map.json은 *없음*
# → 익명 archetype fallback이 작동 (agent_03 → "agent_03 (loyal_presence)")
# → 카드는 익명이지만 mining은 동일하게 작동 (정직한 generalization 검증)
```

---

## 5. *경고 사인* — 검증이 실패했을 때

### 5.1 audit_fail 발생

**의미**: 시스템이 *forbidden token*을 출력했다 (대사 / 시나리오 슬러그 / 플롯 prescription). Plan §15는 audit_fail 0개를 *Ship 조건*으로 명시.

**대응**:
1. `data/narrative/story_viability_audit.json` 열어 violations 위치 확인
2. 어느 builder가 그걸 출력했는지 (`scene_brief` / `treatment`)
3. 해당 builder의 template 수정 (`engine/observer/scene_brief.py` 또는 `treatment.py`)
4. 또는 anchor blocklist에 새 패턴 추가 (`content/anchors/{anchor_id}/audit_blocklist.json`)
5. 재실행 + 재검증

### 5.2 모든 후보 not_viable

**의미**: 시뮬레이션이 *narrative 가치 있는 패턴*을 못 만듦. Plan §15는 이 경우 **Drop / Reframe** 권고:

> *"Narrative Mining Engine" → "Simulation Pattern Mining Tool"*

scope 낮추기 — 이야기 후보 채굴 claim 포기.

### 5.3 Human Pick Test 통과 후보 0개

**의미**: 자동 점수는 strong_viable인데 *사람은 안 고른다*. 자동 평가 calibration 문제.

**대응**:
1. 질문 6 응답 분석 → 어디가 *억지로 이야기화*인지
2. story_candidate_builder의 *premise template* 또는 *adaptation hooks*가 너무 generic하지 않은지
3. relationship_dynamics가 너무 hedged ("co-occurring within thread, not directional") → 흥미 떨어뜨릴 수 있음
4. 점수 가중치 (`engine/observer/story_viability.py`) 재조정 — character_clarity 낮추고 turning_point_strength 높이기 등

---

## 6. *그래서 결국 — 이게 "이야기"인가?* (정직한 답)

### 6.1 현재 시스템이 보여주는 것

> "Peter tries to stay present as fear and public pressure slowly turn loyalty into silence."

이건 **이야기의 씨앗 (premise)**. *완성된 이야기*는 아님.

### 6.2 이게 "이야기 수준"으로 가려면 더 필요한 것

| 추가 layer | 비용 | Plan 위배 여부 |
|---|---|---|
| 장면 위치 / 시간 구체화 | 작가의 영역 | OK (위배 X) |
| 대사 작성 | 작가의 영역 | OK (위배 X) |
| 인물 행동 묘사 | 작가의 영역 | OK (위배 X) |
| 시스템이 *위 모두* 자동 생성 | LLM 통합 / 큰 작업 | ⚠️ Plan §10.2 위배 — 새 directive 필요 |

### 6.3 권장 사용 흐름

```
WITNESS 시뮬레이션
   ↓
StoryCandidate × 4 (자동)
   ↓
Scene Brief + Treatment (자동, 검증됨)
   ↓
[*당신이 여기 들어옴*]
   ↓
당신이 직접 작가 / 감독 / 게임기획자가 되어
씨앗에서 실제 이야기를 작성
```

**WITNESS의 역할**: *씨앗 채굴기*. 작가의 *대체*가 아닌 *입력 도구*.

---

## 7. 빠른 reference — 한눈에 보는 명령어

```bash
# Step 1: 모든 산출물 한번에 빌드
python scripts/narrative/build_story_viability_report.py

# Step 2: 메인 리포트 읽기
# → docs/portfolio/STORY_VIABILITY_REPORT.md

# Step 3: 각 후보 상세
# → docs/portfolio/SCENE_BRIEFS.md
# → docs/portfolio/ONE_PAGE_TREATMENTS.md

# Step 4: Human Pick Test (수동, 3명 이상)
# → 7개 질문, §2.3

# Step 5: 통과한 후보를 받아 작가가 직접 작성
# → 매체별 출발점, §4.1
```

---

## 8. 자주 묻는 질문

**Q: agent_03이 왜 Peter인가? 시뮬레이션이 그렇게 결정한 건가?**

A: 아니요. `content/anchors/peter_scarcity_baseline/identity_map.json` 매핑 파일이 그렇게 *명명*한 것. 시뮬레이션은 익명 agent_01-12를 만들고, identity_map은 *결과를 보고 사람이 가장 active한 agent들에 이름을 붙임*. 매핑을 다른 이름으로 바꿔도 시뮬레이션 결과 자체는 같음 (L57 lesson).

**Q: 4 후보가 모두 "loyalty / uncertainty" 비슷한데 왜 그런가?**

A: 같은 anchor (peter_scarcity_baseline) 위에서 같은 압력 구성 (scarcity + authority pressure)이 작용하기 때문. 다른 conflict family를 보고 싶으면:
- vangogh_sacred_baseline (frustration / loneliness 중심)
- 또는 새 anchor / scenario 도입 (단, plan §10 새 anchor 도입 금지 — 사용자 directive 필요)

**Q: cross-seed에서 6/6 robust인데 그 의미는?**

A: 5 seeds 모두에서 같은 4명 + 같은 2 conflict family가 등장 → *narrative structure가 seed-stable*. 즉 시뮬레이션이 *우연이 아닌 세계 구조*로 narrative를 produce. portfolio claim 강화.

**Q: 시간이 없을 때 *최소* 무엇만 봐야 하나?**

A: 메인 리포트 §1 Summary 표 (30초) + S01 Scene Brief (2분) = **2분 30초**. Stage E는 별도로 24-48시간 분 회신 받기.

**Q: 만약 모든 후보가 weak_seed로 나오면?**

A: §5.2 참조 — Drop / Reframe 권고. 또는 새 anchor / 다른 압력 설정 / 다른 seed 시도. *현재 peter_scarcity_baseline은 1 strong + 3 viable이므로 이 경고는 해당 안 됨*.

---

## 9. 관련 문서

- Plan: [WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md](WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md)
- 메인 산출물: [docs/portfolio/STORY_VIABILITY_REPORT.md](portfolio/STORY_VIABILITY_REPORT.md)
- Scene Briefs: [docs/portfolio/SCENE_BRIEFS.md](portfolio/SCENE_BRIEFS.md)
- Treatments: [docs/portfolio/ONE_PAGE_TREATMENTS.md](portfolio/ONE_PAGE_TREATMENTS.md)
- 입력 layer (Story Candidates): [docs/portfolio/STORY_CANDIDATES.md](portfolio/STORY_CANDIDATES.md)
- Cross-seed robustness: [docs/portfolio/CROSS_SEED_STORY_PATTERNS.md](portfolio/CROSS_SEED_STORY_PATTERNS.md)
- 외부 AI 검토용 brief: [EXTERNAL_REVIEW_BRIEF.md](EXTERNAL_REVIEW_BRIEF.md)

---

*이 가이드는 Stage E (Human Pick Test) 운영용. Stage A-D + F는 자동 — `python scripts/narrative/build_story_viability_report.py` 한 줄로 모두 실행.*
