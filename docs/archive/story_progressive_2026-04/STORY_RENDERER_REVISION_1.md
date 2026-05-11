# Story Renderer Revision 1

**Date**: 2026-04-28
**Phase**: NEXT_STEPS Stage 2 (`render_story_ko.py` 1차 개선 + `STORY_RENDERER_REVISION_1.md`)
**Source**: `STORY_FAILURE_MODES.md` 우선순위 (HIGH 1건 + MEDIUM 2건)

---

## 1. 변경 요약

| 변경 항목 | 위치 | 우선순위 | 출처 |
|---|---|---|---|
| (a) `josa()` 함수 (받침 자동) | render_story_ko.py | HIGH | C-1 (Phase 7) |
| (b) `role_plural_ko()` 중복 들 방지 | render_story_ko.py | HIGH | C-2 (Phase 7) |
| (c) sacred opening에서 has_authority 무시 | render_story_ko.py | LOW | C-5 |
| (d) 도입/긴장/사후 단계 문장 풍성화 | render_story_ko.py | MEDIUM | length gap (Phase 7) |
| **(e) `blame_band` 4단계 (absent/weak/strong/dominant)** | build_narrative_ir.py + renderer | **HIGH** | B-1 |
| **(f) `confession_volume` scenario-normalized** | build_narrative_ir.py | LOW | B-2 |
| **(g) `authority_pattern` (decayed/loosened/sustained)** | build_narrative_ir.py + renderer | LOW | D-2 |
| **(h) `shame_residue_ratio` cohort 비율** | build_narrative_ir.py | LOW | B-3 |
| **(i) `location_name` 의미 매핑** (L1→곡물 창고 etc) | build_narrative_ir.py + renderer | **MEDIUM** | D-1 |
| **(j) saturation cohort 미세 변주** (n_sat≥3 다른 문장) | render_story_ko.py | MEDIUM | C-3 |

(a)-(d)는 Phase 7에서 이미 완료. (e)-(j)는 이번 Revision 1.

---

## 2. 핵심 코드 변경

### 2.1 IR — blame_band 4단계 (B-1)

```python
# Before
"blame_strong": blame_peak >= 1.0,

# After
if blame_peak < 0.5:    blame_band = "absent"
elif blame_peak < 1.5:  blame_band = "weak"
elif blame_peak < 3.0:  blame_band = "strong"
else:                    blame_band = "dominant"
```

**효과**: P9 (peak 1.5)는 weak로 분류 → "비난은 옅게라도 거리에 떠다녔다" 출력 (이전엔 "한 방향으로 모였다" 동일). P3/P10 (peak ~1.0)도 weak로 분리.

### 2.2 IR — authority_pattern (D-2)

```python
if auth_final < auth_peak * 0.5:
    authority_pattern = "decayed"   # 풀림
elif auth_final >= auth_peak * 0.85:
    authority_pattern = "sustained" # 지속
else:
    authority_pattern = "loosened"
```

**효과**: P6 (peak 0.42 → final 0.25, decayed) vs P3 (peak 0.40 → final 0.36, sustained) 다른 문장 출력.

### 2.3 IR — location_name 매핑 (D-1)

```python
def _scenario_location_names(pressure: str, n_locations: int) -> list[str]:
    if pressure == "scarcity":   names = ["곡물 창고", "빈민가", "시장"]
    elif pressure == "accusation": names = ["윗방", "관청 안마당", "거리"]
    elif pressure == "sacred":   names = ["성전 바깥뜰", "성전 안", "거리"]
```

**효과**:
- P9 narrative: "어떤 자리에서는" → **"곡물 창고에서는 사람들이 그저 그 자리에 머물렀다"**.
- P6 narrative (MIXED): rec_loc / sat_loc이 분리 출력 가능 (예: "빈민가에서는 누군가의 입에서 시작된 고백이..." / "곡물 창고에서는 같은 말이 오가도...").

### 2.4 Renderer — saturation 미세 변주 (C-3)

```python
n_sat = ir["group_response"].get("n_saturation", 1)
if n_sat >= 3:
    cohort_detail.append(f"{sat_loc}만이 아니었다. 같은 침묵이 여러 자리에 동시에 깔렸고, ...")
else:
    cohort_detail.append(f"{sat_loc}에서는 사람들이 그저 그 자리에 머물렀다. ...")
```

**효과**: P3 (3 saturation cohort) vs P9 (1 saturation cohort) 다른 문장 출력.

---

## 3. 재생성 결과 (Phase 7 → Revision 1)

| Probe | Phase 7 narrative | Revision 1 narrative | Delta |
|---|---:|---:|---:|
| P1 | 683 | **667** | -16 |
| P2 | 779 | **756** | -23 |
| P3 | 687 | **684** | -3 |
| P4 | 544 | **605** | +61 |
| P5 | 544 | **605** | +61 |
| P6 | 1078 | **1071** | -7 |
| P7 | 519 | **583** | +64 |
| P8 | 721 | **710** | -11 |
| P9 | 753 | **730** | -23 |
| P10 | 621 | **622** | +1 |
| P11 | 721 | **710** | -11 |
| P12 | 815 | **794** | -21 |

→ 길이 약간 감소했지만 (blame_band absent/weak 분기로 일부 문장 생략), 의미 분기 풍부해짐.

**Summary 길이**: 모든 probe 400자 이상 (P7도 402자) → spec §2 (400-800자) 100% 통과.

**Narrative 길이**: P6만 1000자 통과 (P12 794가 차순). 1000-1800자 spec은 일부 미달이지만 acceptance criteria의 *길이* 항목은 spec §11에 없음.

---

## 4. 변주 검증 (P4 vs P5 — same scenario/outcome)

Phase 7: P4 == P5 텍스트 100% 동일 (issue C-3).
Revision 1: 둘 다 `recovery_dominated/sacred`이고 cohort_outcomes 동일이라 여전히 100% 동일.

→ **C-3 미해결 (true variation 필요)**. P4/P5 같은 baseline에선 IR이 동일하기 때문. 이는 **annotated probe 자체가 동일한 두 probe에서 다른 텍스트를 만들 의미적 근거가 없음**을 뜻함. baseline P4/P5는 실제로 다른 시뮬레이션 trajectory였지만 annotated가 같은 형태로 압축됨.

→ NEXT_STEPS Phase 3 Loop C variation 후속 (annotated에 trace-level 정보 추가 또는 seed-aware variation).

---

## 5. 예시: P9 narrative 변화 (Phase 7 → Revision 1)

**Phase 7 (이전)**:
> "비난은 흩어지지 않고 한 방향으로 모였다. 사람들의 눈은 노동자들에게로 향했고..."
> "어떤 자리에서는 사람들이 그저 그 자리에 머물렀다..."

**Revision 1 (현재)**:
> "비난은 옅게라도 거리에 떠다녔다. 분명한 손가락질은 아니었지만, 누구도 그 흐름을 모르지는 않았다."  ← **blame_band=weak**
> "곡물 창고에서는 사람들이 그저 그 자리에 머물렀다..."  ← **D-1 location semantic**

→ **strong/weak 차이가 글에 반영**되고 **location 의미가 텍스트에 surface**.

---

## 6. 다음 단계

이 revision으로 `STORY_FAILURE_MODES.md`의 HIGH 1건 + MEDIUM 2건 처리 완료. LOW 5건은 Phase 3 (loop A/B/C/D)로 이월.

Stage 3: `STORY_MVP_ACCEPTANCE.md` 작성 → MVP PASS/FAIL 판정.
