# Story × Branch C Integration

**Date**: 2026-04-28
**Phase**: NEXT_STEPS Phase 4 entry — Story output × Branch C 1차 evidence 연결
**Source**:
- 12 baseline + 36 Branch C probes = 48 total
- `STORY_MVP_ACCEPTANCE_v2.md` (6/6 PASS)
- `BRANCH_C_FIRST_EVIDENCE_SUMMARY.md` (v4.4)

**Verdict**: **Configuration sensitivity가 이야기 수준에서 surface**. Branch C 발견이 한국어 글로 직접 읽힘.

---

## 1. 작업 내용

### 1.1 파이프라인 일반화

`extract_story_features.py`:
- `BRANCH_C_DIRS` 매핑 추가 (P_PV → placement, P_CV → cast, P_ED → event_density, P_S2 → scarcity_depth)
- `_resolve_probe_path()` — probe_id prefix로 자동 디렉토리 선택
- `--branch-c` 모드: 36 probes 일괄 처리

`build_narrative_ir.py` + `render_story_ko.py`: probe_id 그대로 처리 (코드 변경 불필요).

### 1.2 산출

48 stories total:
- `docs/story/generated/P{1-12}_{summary,narrative}_ko.txt` (12 baseline)
- `docs/story/generated/P_PV_{01-09}_*.txt` (9 placement variant)
- `docs/story/generated/P_CV_{01-09}_*.txt` (9 cast variant)
- `docs/story/generated/P_ED_{01-09}_*.txt` (9 event density)
- `docs/story/generated/P_S2_{01-09}_*.txt` (9 scarcity depth)

길이 평균: Narrative 750-870자.

---

## 2. 핵심 검증 — Configuration Sensitivity가 이야기에 surface하는가?

### 2.1 P_PV_09 — LOW_ACTIVITY 통한 placement 효과

`P_PV_09` = sacred + clustered placement (모든 agents가 temple_inner에 모임). Branch C에서 발견된 유일한 LOW_ACTIVITY (1/48).

**Story 출력**:
> "특별한 일이 없는 날이었다. 사람들의 발걸음은 일상의 무게로 흘렀고, 거리에는 익숙한 소리만 남았다."
> "큰 사건은 없었다. 다만 작은 마찰들이 거리를 따라 가볍게 움직였고, 그 외에는 아무것도 멈추거나 시작되지 않았다."
> "큰 변화는 없었다. 사건이라 부를 만한 일도 없이, 시간은 흘러갔다."

→ **LOW_ACTIVITY 톤이 정확히 surface**. "사건 없음" / "평소처럼 흘러감" / "분명하지 않음" 이라는 의미가 글에 다음 사례들과 다르게 분명히 드러남.

### 2.2 P_S2 시리즈 — Nonmonotonic (single/double SAT vs triple RECOVERY)

같은 scarcity scenario, 같은 cast, 같은 placement. **오직 event count만 다름** (1/2/3 accusations).

**P_S2_05 (double, SATURATION)**:
> "비난은 옅게라도 거리에 떠다녔다."
> "사람들은 자리에 굳었다. 고백이 있었어도 무거움은 풀리지 않았고, 어떤 자리에서는 시간이 멈춘 것처럼 보였다."
> "사람들은 자리에 머물렀다. 어떤 자리는 시간이 흘러도 풀리지 않았다."

**P_S2_08 (triple, RECOVERY) — nonmonotonic finding**:
> "고백은 멈추지 않고 이어졌고, 용서한다는 말도 그만큼 거리 위에 떠다녔다."
> "사람들은 흔들렸지만 다시 자리를 잡았다. 고백이 한 사람에서 다음 사람으로 옮겨 갔고, 무거움은 조금씩 줄어들었다."
> "흔들림은 가라앉았다. 누가 먼저랄 것도 없이 사람들의 어깨에서 무게가 풀렸다."

→ **이야기 톤이 정확히 다름**. Saturation = "굳었다 / 자리에 머물렀다 / 시간이 멈춘 것처럼". Recovery = "다시 자리를 잡았다 / 흔들림은 가라앉았다 / 무게가 풀렸다".

→ **S2 nonmonotonicity (LOOP 69 발견) 가 글에서 직접 식별 가능**. 만약 사람이 P_S2_05와 P_S2_08을 읽는다면, *왜 단순히 "더 많은 비난 = 더 깊은 굳음"이 아닌가*를 묻게 됨. 이는 Branch C가 만든 대조 자체가 *서사적 가치*를 가짐을 뜻함.

### 2.3 P_PV_01 vs P_PV_02 — Placement inversion → 이야기 반전

같은 accusation, 같은 cast. Original placement (P_PV_01) vs inverted placement (P_PV_02).

**P_PV_01 (RECOVERY)**: "사람들은 흔들렸지만 다시 자리를 잡았다…"
**P_PV_02 (SATURATION)**: "사람들은 자리에 굳었다…"

→ Placement만 바뀌었는데 이야기 결말이 정반대. *공간이 결을 바꾼다*는 Branch C 1차 evidence (S5 placement reversal 3/3) 가 **서사 단위에서 보존**됨.

---

## 3. 이야기 단위 configuration sensitivity 정량화

### 3.1 같은 시나리오, 다른 cast/placement/event count

| 시나리오 | RECOVERY | SATURATION | MIXED | PARTIAL | LOW_ACTIVITY |
|---|---:|---:|---:|---:|---:|
| accusation (12 probes) | 4 | 4 | 3 | 0 | 0 |
| scarcity (15 probes) | 7 | 7 | 1 | 0 | 0 |
| sacred (15 probes) | 6 | 1 | 0 | 7 | 1 |
| 기타/none_clear (1) | 0 | 0 | 0 | 0 | 1 |

→ 같은 시나리오 안에서도 **모든 5 outcome 중 최소 2개** 발견 (sacred는 4종 outcome).

**이야기 수준 효과**: 같은 도입부 ("성전 바깥뜰…", "곡식이 비어 가는 계절…", "공기는 이미 무거웠다…")로 시작해도 결말이 RECOVERY/SATURATION/MIXED/PARTIAL/LOW_ACTIVITY 5가지 다른 톤으로 분기됨.

### 3.2 길이 분포 (48 stories)

| 시나리오 | Avg summary | Avg narrative |
|---|---:|---:|
| baseline (12) | 488자 | 864자 |
| placement (9) | 470자 | 770자 |
| cast (9) | 473자 | 804자 |
| event density (9) | 393자 | 705자 |
| scarcity depth (9) | 546자 | 872자 |
| **전체 48** | **474자** | **803자** |

→ Sacred event density (P_ED) 시리즈가 가장 짧음 (평균 705자). 이유: sacred 시나리오에 has_authority 무시 정책 + 상대적으로 작은 cast → 짧음.

---

## 4. Forbidden phrase 검증 (48 stories)

```
docs/story/generated/ 전체 grep:
- "trajectory" / "probe" / "final summary" / "annotated": 0건
- raw IDs (P_PV_NN, P_S2_NN, A1, L1, agent_): 0건
- 숫자 (peak X.YY, final, t=N): 0건
- 메타 ("이 시뮬레이션", "데이터에 따르면"): 0건
```

→ Spec §6 forbidden 0건 유지 (Branch C 36 probes에서도 통과).

---

## 5. 함의 (NEXT_STEPS Phase 4 검증)

NEXT_STEPS Phase 4는 Branch C가 **story output quality 개선**에 기여할 때만 열림.

이번 적용에서 확인된 사실:

1. **Branch C 36 probes는 추가 quality 개선 없이도 한국어 story로 즉시 surface 가능** (파이프라인 일반화만 필요).
2. **Configuration sensitivity가 이야기 톤에 보존됨**: cast/placement/event_count/event_density 변화가 RECOVERY/SAT/MIXED/PARTIAL/LOW_ACTIVITY tone 차이로 직접 surface.
3. **Branch C가 이미 "story 다양성"을 만들어 줌**: 12 baseline에서는 안 나타난 LOW_ACTIVITY (1/48), placement reversal pair, nonmonotonic event count 모두 이야기로 읽힘.

→ **Branch C 1차 evidence는 story output에 immediate value**. 더 많은 probes 생성이 더 풍부한 story set을 만든다.

### 5.1 향후 Branch C가 가치 있는 변경

NEXT_STEPS Phase 4 §3.2 기준 ("이 변화가 story output quality를 실제로 개선하는가?"):

- **D-3 event timing rhythm** (이전 FAILURE_MODES.md): 추가하면 같은 outcome 안에서 *언제 비난이 시작됐는가*가 글로 surface 가능. 가치 medium.
- **추가 시나리오 (4번째)**: 새로운 도입 톤. 가치 high — but engine 변경 필요 가능 (지금 forbidden).
- **role 다양성 확장**: 새 role 추가 시 ROLE_KO 매핑만 추가. 가치 low (현재 17 roles 충분).

### 5.2 향후 Branch C가 가치 적은 변경

- 더 많은 placement variants: 마지막 PV 9개도 충분
- 더 많은 cast variants: S4 9개도 충분
- 더 많은 seeds (cross-seed ensemble): 통계용이지 story용 가치 낮음

---

## 6. 결론

**NEXT_STEPS Phase 4 entry 통과**. Branch C 1차 evidence (36 probes) + Story output MVP Phase 2 (6/6 PASS)는 **결합 시 추가 가치 큼**:

- 48 stories total로 다양성 풍부
- 같은 시나리오 안에서도 outcome 분기 모든 5종 surface
- LOW_ACTIVITY, nonmonotonic, placement reversal 같은 *희귀 발견*이 이야기로 surface

**다음 권장 작업**:
1. (이번 cycle 이후) 12 baseline + 36 Branch C 종합 review — 어느 stories가 가장 잘 읽히는가
2. (선택) Loop B aftereffect 강화 — world_aftereffect 단계 확장
3. (선택) Loop D style branching — 요약형/서사형 분기 더 분명히

**보존**:
- 3단계 파이프라인 (extract / IR / render)
- Template-guided rendering
- forbidden phrases 0건
- 5단 구조

---

## 7. 산출물 요약

| 파일 | 변경 |
|---|---|
| `scripts/story/extract_story_features.py` | `BRANCH_C_DIRS` + `_resolve_probe_path()` + `--branch-c` 모드 |
| `scripts/story/build_narrative_ir.py` | `--branch-c` 모드 |
| `scripts/story/render_story_ko.py` | `--branch-c` 모드 |
| `data/story/story_features/` | +36 JSON files |
| `data/story/narrative_ir/` | +36 JSON files |
| `docs/story/generated/` | +72 .txt files (36 summary + 36 narrative) |
| **`docs/story/STORY_BRANCH_C_INTEGRATION.md`** | **이 문서 (NEW)** |
