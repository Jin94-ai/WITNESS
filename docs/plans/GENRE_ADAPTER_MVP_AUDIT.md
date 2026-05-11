# Genre Adapter MVP Audit (Phase 2.75)

> Per `docs/WITNESS_PHASE_2_75_GENRE_ADAPTER_MVP_PLAN.md` §12 (Acceptance) + §11 (Audit rules).

이 문서는 Phase 2.75 Rule-based Genre Adapter MVP의 acceptance 충족 여부 +
audit 결과 정리.

---

## 1. Acceptance Criteria 대응표

Plan §12 11개 항목 모두 met:

| # | 조건 | 상태 | 증거 |
|---|------|------|------|
| 1 | genre rulebook JSON이 존재한다 | ✅ | [content/genres/korean_morning_melodrama/rulebook.json](../../content/genres/korean_morning_melodrama/rulebook.json) |
| 2 | audit blocklist JSON이 존재한다 | ✅ | [content/genres/korean_morning_melodrama/audit_blocklist.json](../../content/genres/korean_morning_melodrama/audit_blocklist.json) |
| 3 | SkeletonOutput v1.1을 읽을 수 있다 | ✅ | `apply_genre_adapter.py` + `_load_skeleton_output` 재사용 |
| 4 | GenreAdaptedOutput JSON을 생성한다 | ✅ | [data/narrative/genre_adapted_output.json](../../data/narrative/genre_adapted_output.json) |
| 5 | Original seed와 adapted seed가 source_seed_id로 연결된다 | ✅ | `test_adapted_seeds_preserve_source_seed_ids` |
| 6 | conflict_axis / desires / pressures가 보존된다 | ✅ | `test_adapted_seeds_preserve_conflict_axis` + `test_adapted_seeds_preserve_pressures_and_desires` |
| 7 | transformation_level == "structure_only"로 표시된다 | ✅ | `test_adapted_seeds_have_structure_only_transformation_level` |
| 8 | forbidden event 추가 0건 | ✅ | audit pass — `forbidden_event_violations: []` |
| 9 | dialogue 생성 0건 | ✅ | audit pass — `dialogue_violations: []` + `test_demo_html_has_no_dialogue_markers` |
| 10 | demo_genre/index.html이 self-contained로 생성된다 | ✅ | `test_demo_html_self_contained` (외부 CDN/asset 0건) |
| 11 | 기존 fast suite 회귀 0 | ✅ | 2,413 passed (이전 2,373 + 40 신규 genre tests) |

---

## 2. No-Go Criteria 검증

Plan §13 — 어느 하나라도 발생하면 Phase 2.75 실패.

| 조건 | 발생? |
|------|-------|
| adapted output이 원본 conflict_axis를 잃음 | ❌ 모든 adapted seed가 `source_conflict_axis_id` 보존 |
| adapted output이 source_seed_id를 잃음 | ❌ 모든 adapted seed가 `source_seed_id` 보존 |
| forbidden event가 출력 본문에 등장 | ❌ audit `forbidden_event_violations: []` |
| 대사 생성 | ❌ `dialogue_violations: []`, `라고 말했다` / `“ ”` 0건 |
| 특정 드라마/작품명/실제 대사 모방 | ❌ `source_imitation_violations: []` |
| skeleton_output 없이 genre output 생성 | ❌ CLI는 `--input` 강제, 로더는 schema 검증 |
| audit 결과를 숨김 | ❌ JSON / Markdown / HTML 모두 audit 섹션 노출 |

→ **No-Go 조건 0건. Phase 2.75 GO.**

---

## 3. 산출물 위치

### 3.1 코드

```text
engine/observer/genre_rulebook.py    — Rulebook / Blocklist loader + dataclass
engine/observer/genre_adapter.py     — SkeletonOutput → GenreAdaptedOutput 변환
engine/observer/genre_audit.py       — GenreAdaptedOutput audit
```

### 3.2 콘텐츠

```text
content/genres/korean_morning_melodrama/rulebook.json
content/genres/korean_morning_melodrama/audit_blocklist.json
```

### 3.3 CLI

```text
scripts/narrative/apply_genre_adapter.py
scripts/narrative/run_genre_demo.py
```

### 3.4 산출

```text
data/narrative/genre_adapted_output.json     (machine-readable)
docs/portfolio/demo_genre/index.html          (self-contained HTML demo)
docs/portfolio/demo_genre/genre_adapted_output.md
docs/portfolio/demo_genre/evidence_audit.md
docs/portfolio/demo_genre/genre_adapted_output.json
```

### 3.5 테스트

```text
tests/test_genre/test_genre_rulebook.py   (13 tests)
tests/test_genre/test_genre_adapter.py    (15 tests)
tests/test_genre/test_genre_audit.py      (12 tests)
tests/test_genre/test_genre_demo.py       (11 tests)
                                  total: 51 신규 tests
```

---

## 4. 변환 결과 샘플 (Peter scarcity baseline)

### 4.1 입력 SkeletonOutput v1.1

- `seeds_count: 4` (S01-S04)
- `flow.ordered_seed_ids: [S01, S03, S02, S04]`
- `audit_trail: unknown_axis_count=0, forbidden_event_additions=0`

### 4.2 출력 GenreAdaptedOutput v1

```json
{
  "schema_version": "genre_adapted_output_v1",
  "genre_id": "korean_morning_melodrama",
  "source_skeleton_version": "skeleton_output_v1",
  "source_seed_ids": ["S01", "S02", "S03", "S04"],
  "adapted_seeds": [
    {
      "source_seed_id": "S01",
      "source_conflict_axis_id": "loyalty_vs_survival",
      "source_pressures": ["authority_vigilance"],
      "source_desires": ["loyalty", "survival"],
      "genre_role": "버티는 사람",
      "genre_pressure": ["가족/권위자의 시선"],
      "genre_conflict_amplifier": "silence_to_misunderstanding",
      "transformation_level": "structure_only",
      "evidence_preserved": true,
      "forbidden_added": false
    }
  ],
  "adapted_flow": {
    "title_ko": "한국 아침 막장 드라마: 버티는 사람 이야기",
    "episode_rhythm": ["평온한 표면", "작은 균열", "의심의 확산", "침묵 또는 회피", "관계 충돌", "마지막 질문"],
    "cliffhanger_ko": "누군가 침묵을 배신으로 해석하기 시작한다."
  },
  "audit": {
    "overall": "pass"
  }
}
```

---

## 5. 다음 단계 분기

Plan §14에 따라 두 갈래:

### 5.1 Phase 3 ML/Flesh Engine

Rule-based adapter의 feature와 출력 구조를 supervised target으로 사용 가능:

```text
ML 입력:    SkeletonOutput v1.1 + annotation features + genre rulebook features
ML 출력:    mode classification / genre intensity / adaptation recommendation
ML 게이트:  외부 의존성 (LLM API / 데이터 fetch / GPU) 사용자 승인 필요
```

### 5.2 Product / Portfolio 메인 흐름

```text
Universal Skeleton → Genre Adapter → Genre Treatment
```

이 데모 (docs/portfolio/demo_genre/index.html)가 포트폴리오에서
"활용 가능성"을 5초 안에 보여주는 메인 후보.

---

## 6. 한 줄 결론

```text
SkeletonOutput v1.1이 외부 학습 없이 rule-based로 장르 변환에 쓸 수 있다.
원본 conflict / desire / pressure / seed_id가 모두 보존되며,
forbidden event / 대사 / 작품 모방 0건.
Phase 3 ML 진입 전 *뼈대-살* 분리의 첫 증명 완료.
```
