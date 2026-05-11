# Genre Adapter Polish Audit (Phase 2.8)

> Per `docs/WITNESS_PHASE_2_8_GENRE_ADAPTER_POLISH_AND_PHASE_3_PILOT_PLAN.md` §6 (Acceptance) + §7 (No-Go).

이 문서는 Phase 2.8 polish가 Phase 2.75 산출물의 표현 품질 결함을 어떻게
해소했는지 정리한다.

---

## 1. 6 Issue 대응표

| Issue | 결함 | 대응 | 코드/콘텐츠 위치 | 테스트 |
|---|------|------|-----------------|--------|
| 1 | 회차 흐름 문장이 기계적 반복 ("사람이(가)") | structured outline (rulebook outline_templates × phase) | `engine/observer/genre_adapter.py::_build_structured_outline` | `test_structured_outline_has_no_awkward_josa`, `test_structured_outline_step_distinct_lines` |
| 2 | Skeleton summary가 내부 ID 중심 (loyalty_vs_survival 등) | plain Korean 우선 + small 태그로 ID 병기 | `scripts/narrative/run_genre_comparison.py::_render_html` (skeleton table) + `genre_rulebook.archetype_plain_ko / flow_role_plain_ko` | `test_comparison_html_has_genre_lens_section` (header check) |
| 3 | "왜 다르게 나왔는지" 설명 부족 | rulebook `genre_lens_ko` + HTML "장르 렌즈" 섹션 + "왜 다르게 나오는가" 섹션 | `content/genres/*/rulebook.json::genre_lens_ko` + HTML lens-card / why-section | `test_korean_rulebook_has_genre_lens_and_outline_templates`, `test_japanese_rulebook_has_distinct_genre_lens` |
| 4 | comparison output JSON이 단일 장르 | `genre_comparison_output_v1` schema + comparison_summary | `scripts/narrative/run_genre_comparison.py::main` | `test_comparison_json_has_comparison_summary`, `test_comparison_premise_differs_between_genres` |
| 5 | Audit가 표현 품질 미검증 | `quality_warnings` (soft, hard와 별도) | `engine/observer/genre_audit.py::_check_quality_warnings` | `test_audit_quality_warnings_field_present`, `test_quality_warning_catches_awkward_josa`, `test_quality_warning_catches_duplicate_outline_lines` |
| 6 | "회차 흐름"보다 "역할 함수 나열" | `GenreAdaptedOutlineStep` (step + source_seed_id + flow_role + line_ko) | `engine/observer/genre_adapter.py::GenreAdaptedOutlineStep` + `adapted_outline_steps` | `test_structured_outline_steps_present`, `test_structured_outline_step_uses_phase_template` |

---

## 2. Acceptance Criteria 검증 (§6)

| # | 조건 | 상태 |
|---|------|------|
| 1 | genre_lens_ko가 두 rulebook에 존재 | ✅ |
| 2 | outline_templates가 두 rulebook에 존재 | ✅ |
| 3 | adapted_outline_steps가 source_seed_id 보존 | ✅ |
| 4 | HTML "One Skeleton, Two Genre Lenses" 섹션 | ✅ (lens-preview 섹션) |
| 5 | 한국/일본 장르 차이 5초 안에 이해 | ✅ (lens-card preview + why-differ section) |
| 6 | "사람이(가)" placeholder 없음 | ✅ (audit + 테스트 강제) |
| 7 | outline line 중복 없음 | ✅ |
| 8 | quality_warnings가 audit에 포함 | ✅ (`audit.quality_warnings` 필드) |
| 9 | hard audit overall == pass | ✅ |
| 10 | soft quality warning == 0 또는 documented | ✅ (deployed 0건) |
| 11 | comparison output JSON 생성 | ✅ (`genre_comparison_output_v1`) |
| 12 | fast suite 회귀 0 | ✅ |

---

## 3. No-Go Criteria 검증 (§7)

| 조건 | 발생? |
|------|-------|
| adapted output이 원본 conflict_axis 잃음 | ❌ |
| source_seed_id 연결 끊김 | ❌ (adapted_outline_steps도 보존) |
| forbidden event가 출력 본문 등장 | ❌ |
| 대사 생성 | ❌ |
| 특정 작품/대사 모방 | ❌ |
| hard audit fail | ❌ |
| side-by-side 결과가 거의 동일 | ❌ (outline lines + premises + cliffhangers 모두 다름) |
| HTML 첫 화면에서 무엇을 비교하는지 불명확 | ❌ (lead "같은 이야기 뼈대가 장르 문법에 따라 다르게 살아나는 과정" + lens-preview) |

→ **No-Go 0건. Phase 2.8 GO.**

---

## 4. 산출물 변경 요약

### 4.1 코드

```text
engine/observer/genre_rulebook.py
  + outline_templates / outline_step_mapping / outline_role_assignment_priority /
    outline_final_step_uses_cliffhanger / genre_lens_ko 5 신규 필드
  + archetype_plain_ko / flow_role_plain_ko helper

engine/observer/genre_adapter.py
  + GenreAdaptedOutlineStep dataclass (Issue 6)
  + adapted_outline_steps + genre_lens_ko on GenreAdaptedFlow
  + _build_structured_outline (rhythm × role × phase template)
  - _interleave_outline 제거 (legacy free-form은 outline_steps에서 자동 생성)
  + GENRE_ADAPTED_OUTPUT_VERSION = "genre_adapted_output_v1_1"

engine/observer/genre_audit.py
  + quality_warnings 필드 (soft, overall에 영향 0)
  + _check_quality_warnings (awkward josa / duplicate / repeated function / empty lens)
  + adapted_outline_steps도 _collect_output_text에서 검사
  + GENRE_AUDIT_VERSION = "genre_audit_result_v1_1"
```

### 4.2 콘텐츠 (rulebook)

```text
content/genres/korean_morning_melodrama/rulebook.json
  + genre_lens_ko: "침묵은 갈등을 줄이지 않는다. 오히려 주변의 의심과 오해를 키운다."
  + outline_templates (4 roles × 3 phases = 12 templates)
  + outline_step_mapping (6 rhythm steps → early/middle/late)
  + outline_role_assignment_priority (6 entries)
  + outline_final_step_uses_cliffhanger: true

content/genres/japanese_quiet_drama/rulebook.json
  + genre_lens_ko: "침묵은 폭발하지 않는다. 정적으로 남아 인물 사이의 거리를 조금씩 바꾼다."
  + outline_templates / step_mapping / priority / final_step_uses_cliffhanger (모두 자체 톤)
```

### 4.3 CLI / 산출물

```text
scripts/narrative/run_genre_comparison.py
  + comparison_summary section in JSON (shared_axes / differences_by_seed /
    audit_overall / total_quality_warnings)
  + new HTML hierarchy: Hero → Lens Preview → Skeleton Summary (plain labels)
    → Side-by-side → Why-Differ → Evidence (collapsed) → Technical Appendix (collapsed)
  + schema_version = "genre_comparison_output_v1"

docs/portfolio/demo_genre_comparison/
  - index.html 재생성 (Phase 2.8 hierarchy)
  - comparison.json schema bumped to v1
  - comparison.md 갱신
```

### 4.4 테스트

```text
tests/test_genre/test_phase2_8_polish.py  (14 신규)
  - rulebook v2.8 fields (genre_lens_ko / outline_templates / step_mapping)
  - structured outline (no josa / steps preserve source_seed_id / distinct lines / phase templates)
  - quality_warnings (field present / catches josa / catches duplicates)
  - comparison summary (schema / shared_axes / differences_by_seed / 두 장르 premise 다름)
  - HTML genre_lens 섹션 / no awkward josa
```

---

## 5. 5초 인상 시연 (deployed)

```text
docs/portfolio/demo_genre_comparison/index.html
```

첫 화면 위계:
1. 제목: "WITNESS · 같은 뼈대, 두 장르 렌즈"
2. Lead: "같은 이야기 뼈대가 장르 문법에 따라 다르게 살아나는 과정을 보여줍니다."
3. **Lens preview** (2 카드 side-by-side):
   - 한국 아침 막장 드라마: "침묵은 갈등을 줄이지 않는다. 오히려 주변의 의심과 오해를 키운다."
   - 일본 정적 드라마: "침묵은 폭발하지 않는다. 정적으로 남아 인물 사이의 거리를 조금씩 바꾼다."
4. 입력 Universal Skeleton (plain Korean 표 + 작은 ID)
5. Side-by-side 회차 흐름 (structured outline)
6. **왜 다르게 나오는가** (rulebook conflict_amplifier 인용)
7. Evidence Preservation (펼침)
8. Technical Appendix (펼침, 내부 ID + schema)

---

## 6. Phase 3.0 Pilot 진입 조건 (§8)

Phase 2.8 완료 후 Phase 3.0 Data & Annotation Pilot 진입 가능. **사용자 승인 5건 필요**:

```text
1. 실제 줄거리 데이터 fetch 승인
2. 출처별 ToS / robots.txt 검토 승인
3. LLM API 사용 승인
4. 비용 상한 승인
5. 저장 위치 / 공개 가능성 결정
```

자체 사이클로 Phase 3.0 진입 불가 — 사용자 directive 필요.

---

## 7. 한 줄 결론

```text
Phase 2.75는 작동을 증명했다.
Phase 2.8은 그 작동을 *포트폴리오 메인으로 보일 만큼* polish했다.
표현 품질 / 비교 명확성 / soft quality audit 모두 갖췄다.

다음은 ML이 아니라 사용자 승인 후 Phase 3.0 Data & Annotation Pilot.
```
