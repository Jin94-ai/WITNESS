# WITNESS · 장르 어댑터 데모

> Phase 2.75 MVP → Phase 2.8 Polish (2026-05-10)

세계 시뮬레이션에서 나온 *보편 이야기 뼈대*를 한국 아침 막장 드라마 / 일본 정적
드라마의 *구조 문법*으로 변환합니다. 외부 LLM / 학습 모델 / 데이터 fetch 0.

**Phase 2.8 Polish 추가**:
- 장르 렌즈 (genre_lens_ko) — 5초 안에 장르 차이 이해
- structured outline (rhythm × phase template) — 회차 흐름이 mapping 나열이 아닌 자연스러운 한 줄
- quality_warnings — soft audit (placeholder 조사 / duplicate / repeated function / empty lens)
- comparison_summary — 장르 간 보존된 갈등 축 + 장르별 다른 premise 표면화
- HTML 정보 위계 — 일반인용 한국어 label 우선, 내부 ID는 small 태그 보조

---

## 1. 무엇을 보여주는가

### 1.1 핵심 흐름

```text
WITNESS engine
  → SkeletonOutput v1.1  (universal — anchor-clean)
  → GenreRulebook         (korean_morning_melodrama)
  → GenreAdaptedOutput v1 (장르 변환 결과 + audit)
```

### 1.2 5초 인상

```text
- 같은 universal seed 4개가 *한국 아침 막장 드라마*의 회차 흐름으로 펼쳐진다
- 인물은 "버티는 사람", "알아차리지만 말하지 않는 사람", "뒤늦게 반응하는 사람" 등
  장르 역할로 매핑된다
- "권위자의 압박" 같은 universal pressure는 "가족/권위자의 시선"으로 변환된다
- 마지막 질문(cliffhanger)는 rulebook 우선순위로 자동 선택
- 변환 결과에 *대사 / 출생의 비밀 / 살인 / 작품 이름* 0건 — audit 자동 검증
```

---

## 2. 보는 법

### 2.1 self-contained HTML 데모

```text
docs/portfolio/demo_genre/index.html
```

브라우저에서 바로 열어 본다. 외부 CDN / asset 의존 0.

### 2.2 텍스트 산출물

```text
docs/portfolio/demo_genre/genre_adapted_output.md     (전체 변환 결과)
docs/portfolio/demo_genre/evidence_audit.md            (audit 상세)
docs/portfolio/demo_genre/genre_adapted_output.json    (machine-readable)
```

### 2.3 재생성

```bash
python scripts/narrative/run_genre_demo.py \
  --skeleton docs/portfolio/demo/skeleton_output.json \
  --genre korean_morning_melodrama \
  --output docs/portfolio/demo_genre
```

---

## 3. 변환 원칙

### 3.1 한다

- 원본 `conflict_axis` / `dominant_pressures` / `dominant_desires` / `seed_id`
  / `flow_role` 보존 (audit가 강제)
- universal role → 장르 역할 라벨 (rulebook.role_mappings)
- universal pressure → 장르 표현 (rulebook.pressure_mappings)
- universal flow → episode_rhythm (평온한 표면 → 작은 균열 → 의심의 확산 →
  침묵 또는 회피 → 관계 충돌 → 마지막 질문)
- 우선순위 기반 cliffhanger 선택

### 3.2 하지 않는다

- 출생의 비밀 / 불륜 / 살인 같은 막장 사건 *추가* (audit blocklist가 차단)
- 대사 / 큰따옴표 / "라고 말했다" *생성* (audit가 차단)
- 특정 드라마 (아내의 유혹 / 오로라 공주 등) 모방 (audit가 차단)
- 인물 관계 임의 추가
- 폭로 *확정* (가능성으로만 변환)

`transformation_level == "structure_only"` — 구조 변환만, 사건 *추가* 0.

---

## 4. 신뢰성

### 4.1 audit 자동 검증

모든 demo 생성마다 `engine/observer/genre_audit.py`가 4개 영역 검사:

```text
1. forbidden_event_violations    — 출생의 비밀 / 불륜 / 살인 / 납치 등
2. dialogue_violations            — 큰따옴표 / "라고 말했다" / "라고 외쳤다"
3. source_imitation_violations    — 특정 드라마명 / 등장인물명
4. evidence_violations            — source_seed_id / conflict_axis 보존 여부
```

→ overall == "pass"여야 acceptance 충족. CLI `--strict-audit`로 fail 시 exit 1.

### 4.2 입력 게이트

GenreAdapter는 SkeletonOutput v1.1의 다음을 강제:

```text
- flow != null
- audit_trail.unknown_axis_count == 0
- audit_trail.forbidden_event_additions == 0
- audit_trail.forbidden_dialogue_generation == 0
```

→ 위반 시 ValueError. 즉 *오염된 skeleton*은 장르 변환 자체에 진입 못 함.

### 4.3 Soft Quality Audit (Phase 2.8)

Hard audit과 별도로, 표현 품질을 검사:

```text
- awkward_josa_patterns ('이(가)' / '을(를)' / '은(는)') 본문 등장
- duplicate outline lines
- repeated adapted_function in outline
- empty genre_lens_ko
```

→ overall = pass / fail은 *hard audit*만 결정. quality_warnings는 별도 노출
   (portfolio polish 게이트 신호).

### 4.4 Test 커버리지

```text
tests/test_genre/test_genre_rulebook.py        13 tests
tests/test_genre/test_genre_adapter.py         15 tests
tests/test_genre/test_genre_audit.py           12 tests
tests/test_genre/test_genre_demo.py            11 tests
tests/test_genre/test_genre_comparison.py       8 tests
tests/test_genre/test_rulebook_drift_guard.py  21 tests (포함 abstraction)
tests/test_genre/test_phase2_8_polish.py       14 tests (Phase 2.8 신규)
                                       total:  94 (모두 fast suite)
```

---

## 5. 포트폴리오 활용

이 데모는 다음 흐름을 5초 안에 보여준다:

```text
세계 시뮬레이션 → universal seeds → 장르 변환 → 회차 흐름 + 클리프행어
```

면접 / cover letter에서:
- "ML 학습 없이 rule-based로 *장르 어댑터*를 분리 가능하다"
- "*structure-only* 변환으로 막장 요소 자동 추가 0"
- "*audit*이 출력 본문을 자동 검증하므로 LLM 환각 같은 위험이 0"
- "Phase 3 (ML / Flesh Engine) 진입 시 같은 출력을 supervised target으로 사용 가능"

---

## 6. 한 줄 요약

```text
ML 학습 없이도 *뼈대 → 장르* 변환 가능함을 증명하는 외부 의존 0 데모.
```
