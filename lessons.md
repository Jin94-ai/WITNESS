# lessons — Witness v1.2 세션 (2026-04-19, Iter 20-40)

> 글로벌 CLAUDE.md 원칙에 따라 실수/방향 수정/학습 사항 정리. 다음 세션에서 참고.

---

## Lessons Index (L1-L87, navigation — 2026-04-28~05-11 누적)

| Lesson | 주제 | Cycle |
|---|---|---|
| L1-L10 | v1.2 phase + autonomous mode 초기 + Branch C 1차 | 2026-04-19~27 |
| **L11** | Engine state surface gap ≠ Engine logic gap | LOOP 64 v4 (2026-04-28) |
| **L12** | Cross-scenario falsification → scenario-specific dynamics | LOOP 67-72 |
| **L13** | Seed=0 unpredictable bias (S2 -33pp / S3 +22pp) | LOOP 73-76 |
| **L14** | Autonomous mode HARNESS audit compliance gap | LOOP 80-81 |
| **L15** | Story output 3단 분리 + IR atom semantic | Story MVP cycle |
| **L16** | Paper draft 동기화 = Appendix가 아닌 main body | LOOP fire 10 |
| **L17** | Pytest 3-layer (fast/domain/full) — 변경 단위 = 검증 단위 | LOOP fire 14 |
| **L18** | 자율 모드 3 phase (pre-directive / directive-driven / post-directive) | 종합 메타 |
| **L19** | Anchor diversity = cell-level (not just scenario) | J-Alpha follow-up |
| **L20** | FAIL signal → 자율 디버깅 cycle 효과적 (~30 min) | J-Alpha follow-up 메타 |
| **L21** | Lee Gate 자율 cycle 모드 A/B (v1 자율 / v2 Lee transparency) | J-Beta + Gate 1 자율 |
| **L22** | Saturation 후 directive는 "멈춤 결정" — Type B directive (forbidden 명시) | NEXT_STEPS_AFTER_AUTONOMOUS_ROUND |
| **L23** | Type B-2 — 외부 판독 분기 사전 정의 + ready-to-resume protocol | POST_TYPE_B_EXTERNAL_GATE_DIRECTIVE (2026-04-29) |
| **L42** | Observer→Story Pipeline = candidate extraction → packet → render link → demo (5 phase MVP) | LOOP P1-P5 (2026-04-30) |
| **L43** | Candidate Curation = 정리 단계 (3 bucket + temporal diversity + near-dup), 새 scoring 금지 | Phase Q1-Q4 (2026-04-30) |
| **L44** | Visual Observer = 텍스트 검증 후 도트 기반 직관 표현, additive layer (JSON schema 무수정) | Phase V0-V2 (2026-04-30) |
| **L45** | Cross-seed visualization = single-seed conditioning을 visual에서 극복 (HARNESS H8 practice) | Phase V-CS (2026-04-30) |
| **L46** | 어휘 patch ≠ 구성 부족 해결 — sprite/props/icon은 dashboard 구성을 못 고침 | Pixel World S1→S2 (2026-05-01) |
| **L47** | Observer 데이터 직역 → dashboard, 번역 → scene. 번역 layer (Director)가 필요 | Pixel Scene Director (2026-05-01) |
| **L48** | Visual cue는 *행동의 결과*로 그려야 — 단순 icon stamp는 어휘만 바뀐 dashboard | PSD MVP cues 구현 (2026-05-01) |
| **L49** | Medium pivot: 정적 image의 "상호작용/흐름 부재"는 patch로 해결 안 됨 — 시간 축 추가가 본질적 fix | PSD freeze → PEP MVP (2026-05-02) |
| **L50** | Pixel event readability는 sprite detail보다 *timing + reaction order*에 의존. KEY reaction이 5초 후 나오면 12s playback 전체가 coherent해도 5초 테스트 실패 | PEP timing cleanup (2026-05-02) |
| **L51** | Group split scene은 *양쪽 actor 모두* 행동 변화 필요. 한쪽 speech + 한쪽 emote만으로는 인과 약함. *speech → face change → retreat → grief → pose_change* 5-step chain이 필요 | PEP Readability Cleanup C02 (2026-05-02) |
| **L52** | Visual track의 *진짜* 차원은 "예쁨"이 아니라 "provenance gap"이다. visualization은 hand-authored cutscene mock일 수 있고, 이를 숨기지 않고 추적 가능하게 만드는 것이 우선 | World-to-Visual Traceability Pass (2026-05-02) |
| **L53** | *데이터-first* IR이 *UI-first* cutscene보다 staged_only 비율을 압도적으로 줄임. PEP (UI-first): 27.9% staged. WFO v0 (data-first): 0% staged. 핵심: 모든 visual_action을 *source delta*에서 derive하면 hand-staging이 자연스럽게 사라짐 | Engine Event Log Adapter / WFO v0 (2026-05-02) |
| **L54** | Polish 단계는 "데이터 정직성 → 시각 인상" 일방향. 역방향(시각 욕구 → 어댑터 staging 추가) 금지. viewer-only transformation(easing/glyph/glow)으로 polish 달성, 어댑터 출력 무수정 | WFO Polished Viewer (2026-05-06) |
| **L55** | Visual track의 *진짜 산출물*은 viewer가 아니라 *audit instrument*였다. provenance class vocabulary(source_derived / inferred / staged_only / not_used)가 visual에서 발명되어 text brief에 그대로 transfer. 5 sub-track freeze는 후퇴가 아니라 *방법론 추출* | Phase 11 Text-first 전환 (2026-05-06) |
| **L56** | Connected-component over a *over-connected* graph collapses to a mega-component. 해결: link family를 분리해서 *strong link만* 컴포넌트에 사용 (same_agent / same_group), weak link (temporal_continuity)는 evidence로만. 또는 agent-centric 묶음 + group fallback으로 path-like 접근 | Narrative Mining Phase 3 thread builder (2026-05-06) |
| **L57** | Identity 매핑은 *플롯 하드코딩이 아니다* — 데이터에 *플롯이 정해져 있지 않으면* identity는 lookup이고 mining은 자유롭게 작동. 매핑은 *who is who*만 말하지 *what happens*는 말하지 않음. 핵심 안전장치: (1) identity_map.json은 edit-friendly (2) 매핑 없으면 archetype fallback (3) plot hardcoding은 *생성된 thread*가 아닌 *thread 생성 규칙*을 검사 | Story Emergence Phase A (2026-05-06) |
| **L58** | Cross-seed pattern이 *narrative structure가 deterministic-stable임*을 직접 증명. 5 seeds × peter_scarcity_baseline → 6/6 robust patterns / 0 anomaly. 의미: 시뮬레이션이 *우연*이 아닌 *세계 구조* 자체로 narrative 패턴을 produce. portfolio claim 강화: "압력 구성이 결정하는 patterns" | Story Emergence Phase E (2026-05-06) |
| **L59** | Audit token 검사는 *semantic context 인식* 필요. bare quotes를 dialogue로 잡으면 *system 메타데이터 인용*까지 false-positive. 해결: verb-of-saying + 근접 quote pair 패턴만 dialogue로 인식. 또한 anchor-specific forbidden phrases는 engine code 외부 (content/anchors/{id}/audit_blocklist.json)로 분리해 engine 비종속 유지 | Story Viability Validation Stage F (2026-05-08) |
| **L60** | *검증자 표면*과 *일반인 표면*은 분리해야 한다. 동일 데이터 위에 두 개의 layer를 운영: (1) 검증자용 (영어, internal terms) — STORY_VIABILITY_REPORT.md (2) 일반인용 (한국어, plain language) — index.html + story_seed_cards.md. 같은 candidate를 두 개 다른 *표현*으로 변환. 자동 test가 *내부 용어 누설*을 강제 금지 | Portfolio Demo Pipeline (2026-05-08) |
| **L61** | 한국어 *조사 처리는 후처리*가 효율적. 템플릿마다 받침 검사 코드 박는 대신, 모든 템플릿에 "은(는)" / "이(가)" / "을(를)" placeholder 그대로 두고, `resolve_korean_josa(text)` 헬퍼로 *최종 출력 시점*에 일괄 변환. 모든 한국어 출력 module이 한 곳의 helper를 import해 일관 적용. test로 "(가)" / "(는)" 미해결 marker가 *결과물에 노출되면 fail* 강제 | Story Assembly Layer (2026-05-08) |
| **L62** | *Fresh-run* 만으로는 narrative-engine 연결이 약하다. observer dump를 매번 재생성해도, 본문이 conflict-label lookup이면 다른 seed가 같은 conflict로 분류 시 동일 텍스트가 나옴. 해결: NarrativeEvidence (수치 단서) → 자연어 변환기 *두 단계*로 분리. 변환기는 evidence의 *실제 숫자*를 인용 ("39단계 동안 가라앉지 않는다"). test 강제: 다른 seed → 다른 본문. lookup은 *fallback*만 | Data-driven Narrative Synthesizer (2026-05-08) |
| **L63** | 장기 timeline narrative는 *기존 PhasedSimulationWorld + canonical_events.json + action_histories*로 충분히 만들 수 있다. 새 anchor / 새 metric 도입 X. 핵심: engine 출력 (action_histories[agent].chosen_action)을 정경 사건 description (canonical_events.json verbatim)에 결합. 다른 seed가 같은 사건에 대해 다른 행동 선택 → narrative 자체가 engine-driven. 기존 자산을 *읽는 layer*가 빠져 있었던 것 | Life Arc Narrative (2026-05-08) |
| **L64** | Module-level 부작용 (`sys.stdout = io.TextIOWrapper(...)`)은 import-as-helper을 깨뜨린다 (pytest capture 닫힘). 대안: 부작용을 *함수 내부*로 옮겨 `if __name__ == "__main__":` 또는 main() 호출 시에만 실행. 이미 작성된 데모 스크립트의 helper를 다른 곳에서 import해 쓰는 게 자연스러운 패턴이라 — module-level 부작용은 임포터의 환경을 변형시키는 *invisible coupling*이다 | demo_phased helper extraction (2026-05-08) |
| **L65** | *결과물의 정보 위계*는 데이터 정확도와 별개로 portfolio 가치를 결정한다. 같은 데이터(NarrativeEvidence)에서 *story-tone* (메인용, 수치 0) + *data-cited* (Evidence용, 수치 인용) 두 layer를 생성하는 게 답. 메인에 수치형이 있으면 reviewer가 "보고서"로 인지 — story 인지 시간 손실. 해결: dataclass에 두 layer 필드 동시 보존 + 렌더가 위계 결정 + test로 메인 영역 수치 0 강제. lookup table은 *story-tone 측에만* 허용 (general phrasing — 인물의 욕망/압박/변화 방향), data-cited는 evidence-driven 유지 | General-audience re-edit (2026-05-08) |
| **L66** | *결정론적 + ML 분리*는 contract freeze로 강제. SkeletonOutput v1 같은 frozen dataclass + drift guard test (필드 set 일치 강제) 없으면 살 엔진(ML) 작업이 contract를 자꾸 건드린다. 해결: (a) FROZEN dataclass + schema_version, (b) `tests/test_skeleton/test_phase2_prep.py`의 EXPECTED_FIELDS 상수 비교 test (필드 추가/제거 시 즉시 fail), (c) RFC_TEMPLATE.md에 변경 절차 명시. drift guard test는 *RFC trigger*로 작동 — fail 메시지에 "RFC required per docs/plans/RFC_TEMPLATE.md" 안내 | Narrative Mode Refactor (2026-05-09) |
| **L67** | *anchor binding은 engine 외부*로 분리해야 engine이 content-agnostic 유지. 패턴: (1) engine module은 `display_name_overrides: dict[str, str] \| None` 인자만 받음 — 이름 dict 가지지 않음. (2) 매핑 dict는 *content/anchors/{id}/binding.json* + orchestrator script에 위치. (3) integrity test가 engine 폴더 안에 인물명 leak 0 강제 (`test_engine_observer_module_has_no_anchor_specific_dicts`). 이 분리로 새 anchor 추가 시 engine 변경 0 | Narrative Mode Refactor (2026-05-09) |
| **L68** | *외부 의존 0 산출물*도 ML phase로 가는 길을 만든다. LLM 호출 / 데이터 fetch / 학습은 외부 의존이라 자체 사이클로 못 함 — 그러나 (1) prompt template, (2) 합성 함수, (3) 검증 함수, (4) CLI orchestrator (dry-run + fixture 모드)는 모두 *외부 호출 0*으로 구현 가능. dry-run mode가 prompt를 *디스크에 저장* + fixture mode가 *수동/별도로 받은 응답*을 검증 + 정규 위치에 저장 — 두 모드만으로도 Phase 2 acceptance 항목 거의 모두 매핑됨. 실 LLM 호출은 *마지막* 단계로 분리 | Narrative Mode Refactor (2026-05-09) |
| **L69** | *형식 통과 ≠ 의미 통과*. Drift guard가 필드 *이름*만 검사하면 contract가 형식적으로는 frozen이지만 *의미*는 누수된다 (e.g. main_role="main", supporting_roles=["supporting_1"], dominant_pressures=[] 같은 silent placeholder). 해결: drift guard를 (a) field name + (b) type annotation (tuple vs list) + (c) default value stability + (d) frozen dataclass 상태 + (e) schema_version v1 family pattern + (f) default_factory 강제까지 확장. 추가로 adapter가 *의미 정보 누수*를 audit_trail에 누적 (unmapped_pressure_phrases / missing_pressure_seeds / unknown_axis_count). 즉 contract drift guard는 *type system 수준*까지 내려가야 의미를 잡는다 | Phase 2.5 Validation Fix (2026-05-09) |
| **L70** | *Lossless adapter는 4-tier fallback*으로 silent empty 0건 보장. tier 1 (phrase mapping) → tier 2 (conflict_axis pole) → tier 3 (archetype default) → tier 4 (audit_empty 기록). silent return은 금지 (audit_collector dict로 반드시 기록). 이 패턴이면 *어떤 입력에서도* dominant_pressures가 의미 있는 값을 가지거나 audit에 명시적으로 기록됨. 또한 archetype map이 *필수* (None이면 ValueError) — anchor별 default를 caller가 명시하지 않으면 lossless 보장 불가. 이는 RFC 거버넌스의 *내부 의미 보존 강제* 패턴 | Phase 2.5 Validation Fix (2026-05-09) |
| **L71** | *Hard audit (pass/fail) vs soft quality_warnings 분리*. audit가 안전성/보존성 중심으로 잡히면 (forbidden event / dialogue / source imitation / evidence preservation) 출력 *문장 품질*은 못 잡는다 (placeholder 조사 / 반복 / mapping 결과처럼 보이는 line). 해결: `quality_warnings: tuple[str, ...]` 필드를 audit dataclass에 추가하되 *overall = pass/fail에 영향 0*. polish gate 신호로만 사용 — portfolio polish 단계에서 0이어야 하지만, fail 조건은 아님. 이 분리로 audit 책임이 *위반(hard)* + *품질 권고(soft)* 두 layer로 분명해짐 | Phase 2.8 Genre Adapter Polish (2026-05-10) |
| **L72** | *Rulebook-driven phrasing이 hardcoded function 제거의 지속 가능한 길*. adapter가 `if flow_role == "main_arc": return "..."` 같은 hardcoded function을 가지면 새 장르 추가 시 engine 변경 필요. 해결: 모든 phrasing을 rulebook JSON으로 이동 — `outline_templates[flow_role][phase]` (template string with `{role}` / `{pressure}` placeholder), `arc_direction_phrases[arc_id]`, `flow_role_function_phrases[flow_role]`. adapter는 lookup helper만 호출. 같은 universal seed가 *장르마다 다른 표현*으로 나오되 *engine 코드 변경 0*. 이 패턴은 cross-genre 비교 demo (한국 막장 vs 일본 정적)에서 abstraction 검증의 핵심 — 두 column이 다른 phrasing을 보이는 이유가 *rulebook*이지 *코드 분기*가 아니어야 한다 | Phase 2.8 Genre Adapter Polish (2026-05-10) |
| **L73** | *외부 의존 phase 진입 전 .gitignore preempt*. 사용자 승인 후 실제 데이터 fetch / LLM API 호출 / 원문 synopsis 저장이 시작되면 *실수로 private 데이터를 commit*할 위험이 큼 (ToS 위반 / 저작권 / API key 노출). 해결: 승인 전 단계에서 *미리* `.gitignore`에 추가 (`data/external_private/` / `data/annotation/phase3_pilot/per_annotator/` / `data/llm_keys/` 등). approval checklist + .gitignore preempt 두 layer로 위험 통제 — checklist가 *행동 게이트*, .gitignore가 *자동 안전망*. 또한 prep doc에 `evidence_quote는 ≤ 30자` / `portfolio HTML 본문 인용 0` 같은 정책을 *문서 단계*에서 명시해 외부 의존 phase 시작 시 즉시 적용 가능 | Phase 2.9 Portfolio Finalization (2026-05-10) |
| **L74** | *역할 분리 = 재현성*. "Claude Code = 데이터 공장 / LLM = 라벨러 / User = 승인권자" 분리는 단순한 책임 나누기가 아니라 *재현성*의 본질이다. LLM에게 "원문 주고 ML 데이터로 정리해줘" 하면 같은 입력도 세션마다 다른 dataset이 나오고 (sampling / randomness / context drift), retraining이 불가능해진다. 해결: Claude Code가 코드 파이프라인 (normalize / validate / build_inputs / validate_outputs / feature_matrix / reliability)을 7개 결정론적 스크립트로 구현. LLM은 *고정 schema input*을 받아 *고정 schema output*만 반환하는 라벨러 역할만. 이 구조면 재실행 시 같은 결과 보장 + 비용 통제 + 버그 시 어느 layer가 문제인지 정확히 분리됨. 외부 의존 phase 들어갈 때 LLM에게 데이터 정제까지 맡기는 anti-pattern을 피하는 것이 가장 큰 단일 결정 | Phase 3.0 v1.1 Pipeline (2026-05-11) |
| **L75** | *Manual Input Mode (API 후순위)*. 외부 데이터 phase 진입 시 가장 흔한 함정 = "API 자동화부터 구현". 결과: 비용 발생 / ToS 위반 위험 / annotation guide bug를 *비용을 들여서야* 발견. 해결: Mode A (사용자가 LLM에 수동 붙여넣기) → Mode B (승인된 fetch) → Mode C (API 자동화) 단계화. Mode A는 비용 0으로 schema / prompt / feature 정의 검증 가능. annotation_inputs JSON을 LLM에 붙여넣고 응답을 annotation_outputs로 저장하면 끝 — Claude Code가 schema / hallucination / reliability 검증. Mode A pilot 통과 후에만 Mode C API 자동화로 비용 효율 확장. 작은 pilot에서 큰 학습 받음 | Phase 3.0 v1.1 Pipeline (2026-05-11) |
| **L76** | *Baseline = No-ML weighted score, 설명 가능성 우선*. ML phase 시작 = neural model 가져오기로 가는 게 아니다. 가장 단순한 *설명 가능한 baseline*을 먼저 만들고, 그 baseline이 *왜 이 score를 줬는지*를 모든 recommendation에 reason_features로 첨부. 이 baseline 통과 후에야 linear / tree / neural 검토. 장점: (a) 데이터 적어도 작동 (10 episodes pilot에서 가능), (b) feature debugging 쉬움 (어떤 feature가 score를 높였는지 보임), (c) rulebook과 직접 연결 (compatibility = axis match + pressure overlap), (d) annotation feature가 없을 때 *compatibility-only fallback* 가능. score = 0.5×compatibility + 0.5×annotation_linear. 모든 layer가 코드 + JSON으로 추적 가능 → ML 진입 시 ablation 비교용 baseline으로 그대로 사용 가능 | Phase 3.1 prep (2026-05-11) |
| **L77** | *Demo HTML 정직성 패턴*. ML/데이터 phase의 prep 단계에서 demo를 만들 때 *지금 실제 데이터가 들어왔는지 / 학습이 됐는지*를 demo가 *정직하게* 표시해야 한다. 해결: (a) data_source banner — `rulebook_only`면 "📐 Prep mode" 노란 배너로 "실 데이터가 들어오면 더 정교해진다"고 명시 / `phase3_pilot`이면 "📊 Phase 3.0 데이터 적용 완료" 녹색 배너. (b) audit-row에 raw_text_used / evidence_preserved / model.trained 모두 tag로 표시 (false면 녹색 / true면 빨간색). (c) HTML test에서 `synopsis_text` 노출 0 검증. (d) score는 항상 reason_features + score_breakdown 동반 — 사용자가 *왜 이 score인지* 추적 가능. 이 패턴이면 demo가 *현재 상태에 대해 거짓말 안 함* — "ML 데이터 학습 완료"처럼 보이게 하는 단순 marketing demo와 분리됨. portfolio 정직성 = 기술 신뢰성. | Phase 3.1 cycle 4 (2026-05-11) |
| **L78** | *Baseline은 한 layer가 아니라 여러 *질문* 단위로 나눠야 한다*. Phase 3.1 baseline을 처음 만들 때 한 가지 산출물 (`flesh_baseline_output_v1`: seed × profile fit) 만으로 충분하다고 생각했지만, 실제로는 두 가지 *다른 질문*이 있었다 — (a) "어떤 시뮬레이션 seed가 어떤 장르 flesh와 잘 맞는가" (seed × profile, **어떤 작품을 시뮬레이션 결과에 입혀야 하는가**) vs (b) "어떤 실제 에피소드가 장르 시그니처가 강한가" (episode × profile, **annotation 데이터에서 학습 신호가 보이는가**). 두 질문은 입력도 다르고 (skeleton seeds vs annotation features) 답변 의미도 다르다. 하나의 baseline으로 둘 다 답하려 하면 *어느 쪽도 명확하지 않은* 결과가 나온다. 해결: Plan §22.2 (Target B Genre Intensity)는 episode 단위 baseline으로 분리 (`episode_intensity_v1` / `engine/observer/episode_intensity.py`), 기존 §27 (seed × profile)와 별개 layer로 둠. 두 baseline이 같은 GenreProfile을 공유하면서도 다른 차원에서 답함. fixture e2e에서 titleA escalation arc (0.625→0.900) vs titleB lower-flat (0.575~0.700)이 episode-level 차원에서 명확히 분리됨 — seed-level은 단일 skeleton만 다뤄서 이 비교가 안 보임. **교훈**: baseline 설계 시 "내가 답하려는 *질문*은 몇 개인가?"를 먼저 물어야 한다. ML 진입 전 ablation baseline 단계에서 *질문별 layer 분리*가 더 의미 있다. | Phase 3.1 cycle 8+10 (2026-05-11) |
| **L79** | *Prep 산출물은 본질적으로 "데이터 기반 추천"으로 오해될 수 있다 — 정직성은 *적극적* 표시로만 보장된다*. Phase 3.0/3.1 prep cycle 1-12에서 `flesh_baseline_output.json`을 rulebook_only fallback으로 생성했고 score 1.000 / strong_fit으로 표시했다. 사용자가 외부에서 검수한 결과: *모든 seed × genre score가 1.0 / strong_fit으로 표시되는데 score_breakdown은 빈 dict라 weighted score처럼 보이지만 실제로는 rulebook compatibility만이라 marketing demo와 구분이 안 된다*는 위험 발견. **세 가지 적극 표시가 동시에 필요했다**: (a) **JSON layer** — `score_breakdown.mode = "rulebook_only"` + `annotation_score = None` + `annotation_components = {}` (항상 채움, 빈 dict 0건). (b) **Demo HTML/MD layer** — "Prep mode (rulebook-only)" banner 강화 ("실제 annotation 기반 추천이 아니라 rulebook compatibility... fit_label은 `compatibility match`로 해석해야 안전하다") + `fit_label (rulebook-only)` 병기 + breakdown 명시 표시. (c) **Validator layer** — `--strict + --synopsis 없음 → exit 2` (quote validation 무력화 방지) + hallucination report `valid_files_only_summary`/`all_files_summary`/`invalid_files` 3 layer 분리 (invalid 파일이 valid 통계 오염시키지 않음). 그리고 **(d) 운영 layer** — Operating Guide §9 *Deploy Status Matrix* (deployed-prep / deployed-data / script-only / fixture-only / generated-after-approval) — 어떤 파일이 어떤 상태인지 *사용자가 요청 전 확인 가능*하게 표로 명시. **메타 교훈**: "정직성은 코드 한 곳만 고쳐서 되는 게 아니다." prep 산출물의 정직성은 JSON / 시각화 / 검증 / 문서 4 layer가 *동시에* 정직해야 보장된다. 한 layer만 정확하고 다른 layer에서 마케팅처럼 보이면 전체가 marketing demo로 미끄러진다. cycle 7-12 prep 작업 후 *외부 검수 → 정직성 보강 sub-phase (Phase 3.05)*가 별도로 필요했던 게 그 증거. | Phase 3.05 (2026-05-11) |
| **L80** | *수동 추적되는 상태는 "MANUAL"로 봉인하지 말고 "AUTO/MANUAL 하이브리드"로 격상하라 — 그리고 *FAIL*과 *PENDING*을 분리하라*. Plan §18.1 (사용자 승인 5+2건 완료) + §18.2 (ToS 검토)는 *외부 활동*이라 처음에 순수 MANUAL로 분류했다 (cycle 5). 사용자가 acceptance checker를 돌릴 때 이 2 항목은 "[?] MANUAL — 사용자 외부 확인 필요"로 표시되어 *검증 도구가 아무것도 안 알려줌*. 그러나 `PHASE_3_0_APPROVAL_CHECKLIST.md`는 이미 *공식 트래킹 문서*다 — 사용자가 ☐ → ☑로 마킹하는 체크박스 7개. 헤더 파싱 (`### ☐/☑ N. title`)은 trivial → AUTO 격상 가능. cycle 7에서 격상 후 (a) doc 존재 + 파싱 성공 시 AUTO (`PENDING` 부분 체크 / `PASS` 7/7), (b) 없으면 MANUAL fallback (backwards compat). **추가 교훈**: AUTO 격상하면 status enum이 4개로 부족 — PASS/FAIL/N/A/MANUAL이 binary too strict. **PENDING** 도입 ([~] 사용자 승인 *진행 중*, FAIL 아님). exit code는 `auto_fail`만 기준 (PENDING은 exit 0 유지) — *진짜 실패*와 *진행 중*을 명확히 분리. **메타 교훈**: (1) "수동" 추적이 *문서로 존재*하면 *파싱 가능* — MANUAL을 영구 봉인하지 말고 자동화 후보로 본다. (2) status enum이 binary (pass/fail)이면 진행 중 상태를 표현할 수 없음 — *PENDING*은 progress 가시화의 필수 어휘. (3) AUTO 격상 시 MANUAL fallback은 *항상* 유지 (사용자 환경 차이 / 파일 부재 대비). cycle 5 → cycle 7 evolution: AUTO 8 + MANUAL 2 → AUTO 10 (with checklist) + MANUAL 2 (fallback). | Phase 3.05 cycle 5+7 (2026-05-11) |
| **L81** | *Multi-cycle 자율 진행은 작업 *종류*를 교차 배치해야 diminishing returns를 피할 수 있다 — 같은 종류 연속 시 가치 곡선이 빠르게 평탄해진다*. Phase 3.05 종결 후 cycle 5-11 자율 진행에서 발견한 패턴: 같은 종류 작업 (예: 코드 추가 / 문서 sync / lessons / integration)을 연속하면 *3-4 cycle 후 marginal value 급락*. 해결: **6가지 작업 종류 교차 배치** — (1) code (immediate value, 새 capability), (2) docs (discoverability, navigability), (3) enhance (extend existing, depth), (4) lessons (cross-cycle reusable pattern), (5) integration test (regression-safe), (6) memory (cross-session preservation). cycle 5-11 실제 패턴: cycle 5 code → 6 docs → 7 enhance → 8 lessons → 9 integration → 10 memory → 11 export (code as new format). 각 cycle이 *다른 차원의 가치*를 추가하면서 단일 영역 과잉을 회피. **메타 교훈**: (a) 자율 진행 시 첫 자기-질문은 "*어떤 종류*의 작업이 마지막인가? 다른 종류로 가야 하나?"여야 한다 (cycle 11 후 *동일 종류 7번째 docs/format* 진입 시점에 멈춤 결정). (b) "이 cycle은 [code/docs/enhance/lessons/integration/memory] 중 무엇인가?"를 명시적으로 progress에 기록하면 패턴 자가-인지 가능. (c) 단일 cycle 안에 *2 종류 이상* 묶는 것은 OK이지만 *연속 cycle 같은 종류*는 피한다. (d) diminishing returns 인지 시점 = 새 cycle 시작 전 substantive 후보 식별이 *2분 이상 걸림* 또는 후보 모두에 "small but ..." 단서 붙임. **자체 회고**: cycle 11에서 markdown export 후 "substantive work 점점 diminishing returns" 명시 → cycle 12에서 더 작업 만들지 않고 *기존 산출 활용 (snapshot generation)*으로 전환 — 정직한 자체 판단. | Phase 3.05 cycle 5-12 retrospective (2026-05-11) |
| **L82** | *L81 pause는 directive 변경 / 사용자 의도 재확인으로 종료될 수 있다 — *결과물 지향* 명시가 substantive work 재개 트리거이며, "결과물"의 정의는 *실행 가능한 도구 + 시연 가능한 산출*이다*. L81에서 pause 결정 후 사용자가 directive를 명시적으로 "결과물을 얻는쪽으로" 추가했다. 이때 marginal value pause로 돌아가지 말고 *재평가*해야 한다 — substantive gap이 실제로 있는지: (a) engine module이 있지만 *실행 가능한 CLI 진입점*이 없다면 결과물 0. CLI 추가는 결과물 직접 생성. (b) Acceptance 통과지만 *deployable demo*가 없다면 결과물 0. demo 추가는 결과물 직접 생성. (c) Demo가 단일 케이스만 있다면 *N case 매트릭스*가 결과물. 예: Rubric 8-step flowchart에서 각 endpoint를 실제 trajectory로 시연. **결과물 N단계 진화**: cycle A (engine module) → cycle B (CLI) → cycle C (single demo) → cycle D (N-case matrix). 각 단계가 *진짜 substantive*이며 다음 단계로 자연스럽게 흐른다. **메타 교훈**: (a) "diminishing returns"는 *현재 작업 종류* 안에서의 평가다. 사용자가 *다른 종류의 결과물*을 요청하면 평가 reset. (b) directive 변화 시 "L81 pause 유지"는 비합리적 — 사용자 의도 변경이 변화 trigger 그 자체. (c) "결과물"은 *그것을 실행해서 사용자가 볼 수 있는 산출*이지 *코드/문서/테스트 자체가 아님*. CLI runner / portfolio HTML / 시연용 fixture가 *진짜 결과물*. (d) Engine module → CLI → demo → N-case 매트릭스의 *4단계 진화*가 typical 결과물 path. 각 단계에서 멈춰도 가치 있지만 N-case 매트릭스까지 가면 *flowchart 모든 endpoint 시연 같은 완결성* 달성. **자체 회고**: Rubric directive 4 cycle (P0/P1.1/P1.2/P2) 후 cycle 11-12 L81 pause → 사용자 "결과물" directive → CLI runner cycle → single demo → 5-variants → 8-variants (모든 endpoint). 6 cycle에 걸친 결과물 진화. cycle 11-12 pause 후 *재시작*이 정직 — 멈춤은 영구적 결정 아님. | Rubric directive 8-step demo retrospective (2026-05-11) |
| **L88** | *Pause cycle은 *manufactured work 회피* 이상의 가치가 있다 — *momentum-driven work pattern을 깨고 fresh review enable*하여 누적된 진짜 staleness 발견*. cycle 44에서 honest pause 결정 (모든 substantive 후보 *small but...* 단서) → cycle 45-46-47-48 = **4 consecutive fresh-review finds** (DESIGN.md cycle 16-42 미반영 / lessons.md index title L11-L23으로 stale / README.md GitHub 최상단 doc 30% invisible / APPLICATION_RESUME_BULLETS 외부 reviewer 30%+ invisible). 4 cycle 동안 매번 *진짜 substantive gap* 발견 — 누적 stale이 *4건* 한꺼번에 쏟아져 나옴. **메타 교훈**: (a) loop progression에서 같은 domain 7+ cycle (cycle 32-38 doc-accuracy 7-cycle 같은) 후 즉시 다른 영역으로 forced switch 하면 *직전 영역의 누적 stale*은 *그대로 남음*. pause cycle은 forced switch가 아닌 *전 영역 fresh review*를 enable. (b) pause는 *영구적 정지가 아닌 *전 시야 재정렬***. cycle 44가 honest acknowledgment였기에 cycle 45 fresh review가 *자유로웠음* (manufactured work pressure 없이 *진짜 gap만* 찾을 수 있음). (c) "diminishing returns 인지"는 *signal*이지 *terminate trigger*가 아니다. signal에 응답한 cycle (pause)이 *다음 cycle*에서 fresh value를 unlock. (d) doc-accuracy maintenance는 *주기적 fresh review*가 필요 — single-cycle 끝낸 후 *7+ cycle 다른 domain 진행* 자체가 stale 누적 inevitable. fresh review를 *시스템 사이클*로 통합 (예: every 5-7 cycle 한 번 pause→fresh review)이 lesson value. **자체 회고**: cycle 44 결정 시 "manufactured work 회피"만 보았지 *pause 자체의 enabling 가치*는 안 봤음. cycle 45-48에서 *결과적으로 발견* — *fresh-review pattern은 design 후보였어야 한다*. 향후 7+ cycle 단일 domain 후 *자동 pause cycle* 검토. **Saturation curve 보완 (cycle 60-61 데이터)**: pause→fresh-review unlock yield는 *감소 곡선*. cycle 44(pause)→45-48 *4 unlock* (큰 누적 stale 해소) / cycle 52(pause)→53 *9 unlock* (전체 portfolio docs 대상이라 더 큰 수확) / cycle 56-58-59(pause)→60 *1 unlock* (semantic gap만 남음) / cycle 61(pause)→0 unlock (saturation). **메타 교훈 (e)**: pause→fresh-review pattern은 *limit이 있다* — *누적 stale이 충분히 많을 때*만 큰 yield. 누적 stale 해소 후는 *fresh review도 무의미*. (f) saturation 인지 시점 = pause cycle에서 0 unlock이 발생한 직후. 그 시점 이후는 *변화 trigger 또는 사용자 directive 대기*가 정직. | cycle 44-48 pause→fresh-review pattern + cycle 60-61 saturation curve refinement (2026-05-11) |
| **L87** | *Doc-reality 검증은 *registry (declared invariant)* + *regex (inferred link)* 의 dual 접근으로 가장 강해진다 — 둘은 다른 차원의 fail mode를 잡는다*. cycle 33-38 7-cycle 자체 회고에서 발견: (a) **Registry pattern** (cycle 37) — `_DOC_REALITY_REGISTRY` dict에 `required_keywords` / `any_of_keywords` / `required_paths` 명시. doc이 *반드시 언급해야 할 것*을 강제 — *omission* 검출 (doc이 새 산출을 깜빡함). (b) **Regex pattern** (cycle 35/38) — 모든 markdown `[label](relative.ext)` link을 자동 추출 + target 실재 확인. doc이 *언급한 것*이 실재하는지 검증 — *broken-link* 검출 (script 이동/이름변경 후 doc stale). 둘 다 필요 — 각자 *다른 종류의 drift*를 잡음: registry는 *under-specification* (doc이 적게 말함), regex는 *over-specification* (doc이 잘못 말함). **메타 교훈**: (a) doc-reality 자동화는 *완전성* 필요 — 한쪽만 적용하면 다른 쪽 fail mode가 silent. (b) cycle 37 registry는 *explicit* 검사 (test 작성자가 무엇이 중요한지 안다 가정), cycle 38 regex는 *implicit* 검사 (모든 link 자동 검증, 작성자 망각해도 잡힘). 둘은 *trust 방향이 반대* — registry는 doc-author 신뢰, regex는 doc-author 불신. (c) 향후 doc-reality test는 *두 layer 다 갖춰야* — 새 doc 등록 시 registry entry + 자동 regex coverage (cycle 38 multi-doc walker가 이미 scan에 포함). (d) 이 dual 패턴은 L84 generic walker (cycle 28)의 메아리 — *서로 다른 접근의 합집합이 generic 솔루션*. **자체 회고**: cycle 35 (regex)와 cycle 37 (registry)을 따로 만들었으나 cycle 38 multi-doc 확장 후 *둘이 dual하다*는 게 명확해짐. 처음부터 dual로 설계했다면 cycle 35→37 사이의 작업 단축 가능. *반복 발견 = 패턴* (L85) 적용해 이번 cycle 39에 lesson化. | cycles 33-38 doc-accuracy 7-cycle retrospective (2026-05-11) |
| **L86** | *Doc가 repository state에 대해 *명시적 주장*을 하면 (예: "see `scripts/foo.py`", "demo는 `dir/` 에 있다"), 그 주장은 *machine-checkable invariant*가 되어야 한다 — 비용이 낮을 때*. cycle 33에서 `FLESH_BASELINE_DEMO.md`를 cycle 17-19/25/29-31 산출 반영해 확장했다. cover doc이 *현재* repo 상태를 정직하게 반영하는지 검증하기 위해 `test_flesh_baseline_demo_doc_references_match_reality` integration test 추가 — 4 script paths + 3 module paths + schema_version + invariant 키워드가 doc과 repo *양쪽*에 존재해야 한다. **비용**: 30분 작성 + 100ms 실행 / **이익**: future cycle에서 script 이동/이름변경 시 cover doc이 *자동으로* fail → reviewer에게 stale 주장 전달 0. **메타 교훈**: (a) "doc accuracy"는 manual review에 의존하면 *시간 지남에 따라 drift*. TDD가 *behavior accuracy*를 자동화하듯, doc-reality test가 *documentation accuracy*를 자동화한다. (b) 모든 doc 주장이 검사 대상은 아니다 — *machine-checkable cost*가 낮을 때만 (script path / module path / schema version / 명시적 키워드). prose 의미는 여전히 manual. (c) cycle 33은 portfolio cover doc 1개에만 적용. 같은 패턴이 INDEX.md / Operating Guide / README 등 다른 reality-referencing 문서에도 적용 가능 — *반복 가능 패턴*이면 generic helper 추출 후보. (d) doc accuracy 자동화 = *Phase 3.05 정직성 4 layer*의 5번째 layer 같음 (JSON / Demo / Validator / 운영 + **Doc-reality**). reviewer가 cover doc만 읽고 잘못된 script path 따라가는 friction을 *코드 변경 시점에 차단*. **자체 회고**: cycle 32 (CLAUDE.md 갱신)와 cycle 33 (cover doc 확장)이 *둘 다 doc 갱신* 작업이었으나, cycle 33만 integration test로 자동화. cycle 32 CLAUDE.md도 동일 패턴 적용 가능 — 후속 cycle 후보. *반복 적용*이 lesson value 누적의 핵심. | cycle 33 doc-reality integration test (2026-05-11) |
| **L85** | *L84 stranded 패턴이 *재발한다*면 그건 운이 아니라 *서식상의 구조적 약점*이다 — 개별 fix 대신 *generic detector + meta-test*를 만들어야 한다*. cycle 16→20에서 CausalCritic `pressure_action_alignment`가 CLI에 노출 안 됐고, cycle 27에서 NoveltyReport `copy_like` / `noise_like` / `structured_difference_score` @property aliases가 deployed JSON에 누락됐다. **같은 L84 패턴 두 번** 발생. cycle 28에서 두 번째 발견 시 *반복 가능성*을 추측했고 grep으로 `CanonReport.hard_pass` (review §2.6 alias) 도 같은 버그 영향 받음을 확인. *세 번째 사례* 발견 즉시 *개별 fix*에서 *generic fix*로 전환: `report_to_dict()`의 walker가 `__dict__`만 walk하던 것을 → `__dict__` + 클래스 레벨 `@property` descriptor 모두 walk하는 일반 함수로 격상. 부가: meta-test (`test_phase3_05_all_subreport_properties_surfaced_in_json`)가 *모든 sub-report dataclass*의 @property를 *반드시* JSON에 노출해야 한다는 invariant를 enforce — 향후 추가되는 @property aliases도 자동 검증. **메타 교훈**: (a) "L84 한 번 발견 = bug, 두 번 = pattern, 세 번 = 시스템 결함." 세 번째 인스턴스 발견은 *generic detector 작성을 미루지 말라*는 명백한 신호. (b) 개별 fix는 *증상 치료*. generic detector + meta-test는 *원인 차단*. cycle 27의 명시 list 추가 (`novelty_dict["copy_like"] = ...`)는 다음 @property 추가 시 또 잊혀질 위험 — generic walker는 안 잊혀진다. (c) review 권고에서 *@property로 alias 정의*는 흔한 패턴 (`copy_like` / `noise_like` / `hard_pass` / `canon_distance` / `is_copy` / `is_noise`). 직렬화 layer에서 @property를 *기본적으로* 다루지 않으면 alias가 *항상* 누락된다. (d) Generic 솔루션의 부수효과: 향후 추가되는 @property aliases는 *별도 코드 변경 없이* 자동 surface — generic walker가 *시스템의 contract*가 됨. **자체 회고**: cycle 27 직후 "같은 패턴 다시 발견될 수 있다"를 lessons에 추가했지만 *조치는 안 했다*. cycle 28 시작 시 grep으로 5초 만에 세 번째 인스턴스 발견 — *generic detector를 cycle 27에서 했어야* 더 효율적. *반복 가능 패턴*은 즉시 generic화하는 게 cycle 절약. | Rubric cycle 27/28 generic L84 detector (2026-05-11) |
| **L84** | *Engine feature를 추가했으면 CLI까지 끝까지 가야 한다 — 그렇지 않으면 *engine-only stranded* 상태가 되어 사용자/데모 흐름에서 보이지 않는다*. cycle 16에서 `CausalCritic`에 `pressure_action_alignment` 측정을 추가했다. CausalReport에 6 신규 필드. 6 신규 tests. *그러나* `scripts/rubric/run_rubric.py`가 `action_pressure_map` 인자를 통과시키지 않아 CLI 사용자는 이 feature를 *호출할 수 없었다*. cycle 17-19에서 다른 작업(Target C)을 했고, cycle 20에서야 CLI 노출 작업으로 돌아왔다. **메타 교훈**: (a) L82 evolution (engine → CLI → demo)은 *순서*가 중요 — engine만 끝낸 시점이 *완성*이 아니라 *시작*. (b) cycle 사이에 *back-fill cycle*은 정당하다. cycle 20처럼 "직전 N cycle 전에 추가한 engine feature가 CLI에서 사용 가능한가?" 자기 질문이 다음 cycle 자동 식별. (c) 노출 작업도 *substantive* — 그저 boilerplate가 아니라 (1) CLI flag 추가, (2) JSON shape 검증, (3) summary 출력 노출, (4) 4 신규 test가 함께 따른다. (d) 자기 검증 questionn: 새 cycle 시작 전 "직전 *모든* cycle에서 추가한 engine 기능이 CLI로 호출 가능한가? 데모에 노출되는가?"를 첫 후보로 점검. **자체 회고**: cycle 16의 alignment 측정은 4 cycle 후에야 CLI로 노출됐다. 이 *4 cycle gap*은 *cycle 17-19를 잘못했다*는 게 아니라 (Target C 작업도 substantive) *완결성 추적*이 필요했다는 의미. progress.md에 cycle 16 완료 후 "TODO: CLI 노출" 같은 짧은 leftover 추적이 있었다면 cycle 17-19 사이에 더 일찍 처리 가능. | Rubric cycle 16→20 back-fill retrospective (2026-05-11) |
| **L83** | *결과물 진화는 4단계가 아니라 *11단계*까지 확장 가능 — "synthetic → real → multi-seed → multi-agent → cross-scenario → visualization"의 5 ensemble 단계가 N-case 매트릭스 *후속*. L82 4단계 (engine → CLI → demo → N-case)는 *single trajectory* 단위에서의 진화. Rubric directive Result-7~11에서 *ensemble 단계*가 추가됨*: (5) **real simulation single seed** — 합성 fixture가 아닌 진짜 simulation trace adapter, (6) **multi-seed ensemble** — review §H8 5+ seed 원칙 적용 (single seed claim 위험), (7) **multi-agent ensemble** — 같은 simulation의 다른 agent 분류 (cross-agent 재현성), (8) **cross-scenario ensemble** — 다른 scenario에서도 작동 (engine generality), (9) **visualization HTML** — 모든 ensemble 한 페이지 시각화. 11단계 총 진화: P0/P1/P2 (engine 강화) → CLI → single demo → N-variants → real simulation → multi-seed → multi-agent → cross-scenario → HTML viz. 각 ensemble 단계가 *통계적 강도*를 누적: 단일 seed claim은 fragile (variance) → 5 seed (sensitivity) → 5 seed × N agents (cross-agent) → 5 seed × M scenarios (engine generality). **메타 교훈**: (a) N-case matrix는 *시연*. ensemble은 *통계적 강도*. (b) review §H8 (5+ seed) 원칙은 *visualization까지 일관 적용* — single deploy artifact가 single seed claim이면 *uncalibrated indicator*. (c) cross-scenario는 *engine generality empirical test* — 같은 engine으로 전혀 다른 scenario (passion ↔ creative drive) 분류 가능하면 *content-engine 분리* 원칙 입증. (d) HTML visualization은 모든 ensemble을 한 곳에 모아 *portfolio 진입 시 1 view에 cross-scenario 결과 발견 가능*. **자체 회고**: Rubric directive 15 cycle 중 11 cycle이 결과물 진화 (P0/P1/P2 4 + Result 11 = 15). Each cycle *다음 cycle의 substantive gap*을 자연스럽게 노출했다 — Result-7 (single seed)이 §H8 위반 → Result-8 (5 seeds), Result-8이 single agent → Result-9 (3 agents), Result-9가 single scenario → Result-10 (cross-scenario), Result-10이 JSON-only → Result-11 (HTML viz). | Rubric Result-7~11 ensemble evolution retrospective (2026-05-11) |

**3 패턴 cluster**:
- **Engine surface gap surfacing**: L11 (v4 top_blame) → L15 (Story IR semantic 변환)
- **자율 falsification**: L12 (D' rejection) → L13 (seed=0 walkback) → L19 (anchor cell-level) → L20 (FAIL → followup)
- **자율 모드 phase + directive type 패턴**: L18 (3 phase) → L21 (Lee Gate 모드 A/B) → L22 (Type B forbidden 명시) → L23 (Type B-2 외부 판독 분기 정의 + ready-to-resume)

**HARNESS H1+H4 자가 falsification 사례**: L12-L13-L19-L20 4 cycle (모두 자율 모드에서 self-discovery, Lee 직시 없음).

**L46-L48 cluster (Pixel visual track 진화, 2026-05-01)**:
- **L46 — 어휘 patch ≠ 구성 fix**: PW-S1-B (test grid) → S2 patch (zone 약화 + props + zone color + event icon) → PW-S2-C (여전히 dashboard). *어휘만* 보강한 patch가 *구성 차원*의 부족을 못 고침. 시청자는 sprite/icon 디테일이 아니라 *시선 유도 / 인물 배치 / 사건 표현 / 거리감 / 카메라 구도*를 본다. 이 5가지 메커니즘은 어휘 patch 범위 밖.
- **L47 — 직역 → dashboard, 번역 → scene**: Observer 데이터를 tile에 직접 뿌리면 dashboard. *데이터 → 장면* 사이에 Director layer가 candidate를 *번역*해야 scene이 됨. Scene Director = focal pick + role 분류 + layout + action beats + visual cues. *해석*이 들어오지만 명시적 rule + transparent + override 가능으로 observer-not-evaluator 원칙 유지.
- **L48 — cue는 결과의 그림자**: confession_wave는 actor 입에서 *방사형 4-arc*, grief_drop은 인물 위 *4-tear cluster*, pressure_ring은 focal 둘러싸는 *3-nested ring*. Single icon stamp는 어휘만 바뀐 dashboard ("아이콘이 zone 위에 떠 있는 것" vs "행동의 결과가 공간에 퍼지는 것"). 5초 테스트 Q4 ("사건이 행동처럼 보이는가")는 cue 그림 방식에 직결.

**Pixel visual track Phase 진화**:
- Phase Pixel World V1 (S1) → PW-S1-B (test grid 인상)
- Phase Pixel World V2 patch (S2) → **PW-S2-C** (dashboard 인상 유지, world map 어휘 자체 실패)
- Phase Pixel Scene Director redirection → 설계 확정 (구성 차원 진단)
- Phase Pixel Scene Director Static MVP + LC1 → **PW-SC-B → freeze (2026-05-02)**: static image medium 한계
- Phase Pixel Event Playback (PEP) MVP → *medium pivot* (정적 → 10-12s cutscene 재생, 8 timeline event types)

→ 2 LOOP 동안 어휘만 patch하다가 *구성 부족*을 진단. 진단 후에는 *redirection*이 어휘 confidence 회복보다 빠른 path.

**L49 — Medium pivot 교훈 (2026-05-02)**:
PSD-LC1까지의 patch는 정적 image 안에서 *어휘 → 구성 → relation/flow*로 점진 강화했지만 결국 *static medium이 interaction/flow*를 전달할 수 없다는 진단. 이때:
- *어휘 patch*는 시각 표현을 바꾸나 medium의 한계를 못 넘음
- *구성 patch*는 정보 hierarchy를 만드나 시간 축 부재로 *흐름*은 못 표현
- *medium pivot* (정적 → 사건 재생)이 본질적 fix

PEP MVP는 시간 축을 추가하되 full replay/animation으로 가지 않고 *제한된 animation* (walk/face/speech/emote/step) + *fixed camera* + *focused tile stage*로 *MVP 검증 가능한 최소 medium 변경*에 집중. → "medium pivot은 가능한 *최소 단위*로" — 전체 game engine 도입 (Phaser etc.) 전에 Canvas primitive로 가설 검증.

**L50 — PEP timing cleanup 교훈 (2026-05-02)**:
PEP MVP 1차 timeline은 KEY reaction을 5-8초 사이에 배치 → packet 가린 5초 테스트에서 *trigger만 보이고 reaction 안 보임* 위험. Wide Plan §4.1: KEY emote/pose_change는 t ≤ 4500ms 안에 등장 필수.

**Validator로 강제**: `validate_event_playbacks.py`가 KEY_REACTION_DEADLINE_MS=5000ms 검증. 향후 candidate 추가 시 자동 차단.

> 핵심 명제: pixel event readability는 *sprite quality*가 아니라 *timing + reaction order*에 의존. *언제* 무엇이 일어나는지가 *얼마나 정교하게* 그려지는지보다 5초 테스트 결과를 좌우.

---

## 아키텍처 결정에서 얻은 것

### 1. 외부 리뷰어 지적은 먼저 스켈레톤으로 흡수, 구현은 opt-in

Gemini와 ChatGPT 리뷰가 요구한 기능 (Inhibitor Rule, slow state 회복, absolute time) 을 **opt-in zero-default** 형태로 먼저 엔진에 추가했다.

- `SlowStateFieldRecoveryRule`: 모든 rate=0이면 zero-effect → v0.7 레거시 무영향.
- `FieldAttenuationRule`: content가 명시적으로 instantiate 해야 활성.
- `HazardFunction.base_rate_unit`: 기본 per_tick = legacy 완전 보존.

**교훈**: 리뷰가 "반드시 추가"를 말해도 기본 비활성으로 넣으면 legacy 검증이 깨지지 않고, content 실험만 단계적으로 해볼 수 있다. "활성화 여부는 content 결정" 패턴으로 일관되게 설계.

### 2. Legacy 모드와 신 모드의 완전 분리

`phases=None`이면 `PhasedSimulationWorld._run_legacy_mode()`가 기존 `SimulationWorld`에 그대로 위임. 두 경로가 같은 seed에서 **bit-exact** 결과를 낸다 (test_claim_legacy_mode_identical_to_v07에서 증명됨).

**교훈**: v0.7 수치 (arrest 100%, Cohen's d=-6.87 등) 보존이 요구될 때, 신 기능을 기존 코드 경로에 섞지 말고 **분기**하라. 두 모드가 다르게 동작하는 것은 feature이지 bug가 아니다.

### 3. Phase-linked = "표면 연속 / 내부 stitched"

reviewer ChatGPT의 명명을 수용. `PhasedMultiAgentResult`가 `per_phase_results` (stitched 관점)와 `final_states` (연속 관점)를 **둘 다** 노출.

**교훈**: "연속 vs stitched"는 양자택일이 아니다. 같은 run 객체가 두 관점을 모두 제공하면 사용자가 분석 목적에 따라 고를 수 있다.

---

## 테스트/검증에서 얻은 것

### 4. POM-style ensemble validation이 단일 seed보다 강력

Phase 1-4 emergent 패턴은 seed 하나로는 증명 안 됨 (noise 섞인 state_noise_scale). 10-seed 앙상블로 "awe Phase 1 < Phase 3", "obedience 단조 성장" 같은 **평균적 패턴**을 검증하면 noise 있어도 robust.

**교훈**: `@pytest.fixture(scope="module")`로 앙상블 결과 캐싱 → 여러 test class가 같은 결과를 쪼개어 검증 가능 (성능 문제 없음).

### 5. Integration test는 unit test를 대체하지 않는다

Iter 11에서 `test_inhibitor_rules.py` (unit) 작성, Iter 26에서 `test_inhibitor_integration.py` (PhasedSimulationWorld E2E) 작성, Iter 31에서 `test_inhibitor_judas_deployment.py` (content composition) 작성.

각 층이 다른 것을 증명: unit = 로직 정확성, E2E = pipeline 통합, content = 실제 시나리오 의미. **세 계층 모두 필요**.

### 6. Coverage 100%는 목표가 아니라 부수 효과

Iter 36에서 time_axis, inhibitor를 100% 커버로 만들었다. 하지만 `extract_final_states_at_phase_boundaries`의 dead 조건 경로 등은 커버해도 값이 크지 않다. **100%를 목표로 테스트를 쓰면 의미 없는 edge case가 쌓인다**. 반대로, 유의미한 edge를 찾다 보면 커버리지가 자연스럽게 올라간다.

### 7. Floating point equality는 항상 tolerance

`1.2000000000000002 == 1.2` 실패를 여러 번 목격. `abs(x - y) < 1e-6` 또는 `< 1e-9`로 일관되게 비교.

---

## 무엇을 놓쳤다가 나중에 발견했나

### 8. Hazard dt 누락 (Iter 26 → Iter 27)

`engine/simulation/world.py:274`에서 `hazard_engine.evaluate_tick(...)`가 `dt` 기본값(1.0)으로 호출됨. Phase tick_scale=24h일 때 hazard rate가 rescale되지 않아 reviewer가 지적한 "phase-variable tick에서 rate invariance" 원칙이 깨짐.

Iter 26까지는 "나중에 고치자"고 progress.md에 flag만 걸었으나, Iter 27에서 `HazardFunction.base_rate_unit` 추가로 해결. 해결책이 legacy-safe였기 때문에 **flag 건 것을 실제로 해결할 수 있었음**.

**교훈**: flag를 걸 땐 "나중에 어떻게 해결할지" 구체적으로 기록하라. "추후 검토" 같은 모호한 말은 flag 해소를 영구히 미룬다.

### 9. Loop ROI는 Iter 35경부터 체감 감소

Iter 20-32는 reviewer-demanded 아키텍처 작업. Iter 33부터는 테스트/문서 정비 및 edge case 커버. Iter 36-38은 coverage 100% + 문서 정렬. Iter 39는 scale 증명. Iter 40은 attestation.

**Iter 35 이후 각 iteration이 +5~10 테스트 추가**하지만 **새로운 설계 결정은 없다**. 이 시점부터는 "정말 가치 있는가?" 질문에 스스로 엄격해져야 함.

### 10. 빠른 cache-friendly 루프보다 깊은 사고가 나은 순간이 있다

ScheduleWakeup 300s는 user 선호로 고정했지만, 이 주기는 cache warm window 안이어서 각 iteration이 "이전 결과 보고 다음 작은 단위 추가" 패턴이 됨. 그 결과 작업이 **점진적이지만 기계적**으로 됨. 큰 설계 결정 (Iter 23 slow recovery, Iter 27 per_hour)은 그보다 긴 사고 시간이 필요했으며, 짧은 주기의 리듬에서 빠져나와 한 iteration에서 해결.

**교훈**: 루프 주기는 단순한 "반복 빈도"가 아니라 **사고 깊이의 박자**. 때로는 한 iteration을 길게 쓰는 것이 여러 작은 iteration보다 낫다.

---

## 다음 세션에 주의할 것

- **v1.2 체크리스트는 Iter 40에서 종료 선언**. 더 추가하려면 "이게 누구에게 가치가 있나?"를 명시적으로 답하고 시작.
- **legacy v0.7 수치 (arrest 100%, Cohen's d=-6.87, sword_drawn Phi=0.95)는 sacred**. 어떤 신 기능도 이를 변경하면 안 됨. 변경될 것 같으면 legacy mode에 가두기.
- **3번째 시나리오** 추가 시 ABSOLUTE RULE #5 "universality 주장 금지" 해제 가능. 그 전까진 "structural isomorphism" (Peter/VG 2 시나리오)까지만.
- **v1.0 Stage 2 PyTorch encoder**가 다음 큰 작업. `drive_training.py` line 118 TODO가 진입점.

## Iter 41-48 tail phase 반성

v1.2 체크리스트가 끝난 후에도 loop가 계속 요청되어 Iter 41-48을 수행. 실제 가치:

| Iter | 작업 | 솔직한 가치 판단 |
|------|------|-----------------|
| 41 | lessons.md 신규 | 중 (이 문서 자체; 미래 세션 참조 가치) |
| 42 | paper draft v1.2 Appendix D | 중-상 (논문 제출 시 필요) |
| 43 | load_handoff_spec | 중 (content JSON 선언 가능하게) |
| 44 | load_phase | 중 (43의 대칭) |
| 45 | JSON-driven arc test | 저-중 (43+44의 통합 증명) |
| 46 | demo_phased --full-passion | 저-중 (사용자 편의) |
| 47 | phase_hours_table() | 저 (편의 wrapper) |
| 48 | SCENARIO_TEMPLATE §7 phase | 중 (3rd scenario 저자 참고) |

**Pattern**: Iter 42-43-44는 명확한 결핍을 채움. Iter 45-47은 그 위에 쌓인 편의. Iter 48은 다음 작업 지향 문서.

### 교훈 11: Loop 지속 시점 판단법

Iter 40 "release attestation" 이후 각 iteration의 가치가 매번 작아짐. 다음 기준 중 하나라도 맞으면 새 세션으로 넘겨야 함:
- 연속 3 iteration이 모두 "중-저" 가치이면 saturation.
- iteration이 5줄 이하 편의 method 추가만 하면 signal이 약해짐.
- 사용자가 큰 방향 전환을 요청할 때까지는 새 iteration을 시작하지 말고 현재 상태를 honest하게 보고.

이 세션은 Iter 41-48에서 실제로 이 saturation 패턴을 보임. 다음 세션은 "v1.0 Stage 2 시작" 같은 큰 작업으로 진입하기 전까지 loop 재시작하지 말 것.

### 교훈 12: SCHEDULED_WAKEUP_INTERVAL=300s는 cache-miss 구간에서 유효하지 않음

ScheduleWakeup 도구 문서가 300s를 "worst-of-both"로 권고하지만, 사용자가 명시적으로 300초 고정을 원했으므로 존중. 결과적으로 각 iteration이 짧은 사고 단위로 나뉘어 **큰 설계 변경이 아닌 점진적 polish만** 나오게 됨. 다음 세션에서 비슷한 상황이 되면, 사용자에게 "300s 유지할지, 1200s+로 늘릴지, 또는 수동 제어로 전환할지" 다시 물어볼 것.

### 교훈 14: Stage 2 학습 feasibility는 학습 전에 측정 가능 (Iter 64-66)

PyTorch MLP encoder를 구현하기 전에 다음을 묻는 것이 중요:
"현재 feature set + projection이 action class를 구별할 수 있는가?"

**측정 도구** (Iter 64 완성):
- `compute_drive_action_diagnostics(samples, encoder)` → action별 drive mean/std
- `drive_class_separability(diagnostics)` → Fisher-style between/within variance ratio

**3-scenario empirical 결과** (Iter 65-66, 10 seeds):
| 시나리오 | separability | 해석 |
|---------|-------------|------|
| Van Gogh (Arles) | 6.04 | 매우 feasible |
| Peter (passion) | 1.93 | feasible |
| **Talleyrand (50y career)** | **0.05** | **학습 불가 신호** |

**Talleyrand 실패 원인**: `state_to_feature_vector`는 emotions + physical + slow_state 12 필드만 포함. Talleyrand의 action 선택은 `domain_state.current_regime`, `alignment_stance`, `network_depth` 등 Literal/domain-specific 필드에 의존 → 현 feature vector에 이 정보가 없으므로 action class가 drive 공간에서 구분 불가.

**구조적 교훈**: "Engine universality"(Iter 57 증명) ≠ "Feature universality". 엔진은 Talleyrand를 수용하지만, Stage 2 학습은 **per-scenario feature extractor**가 필요. 다음 대안:
1. `state_to_feature_vector`를 agent/scenario별로 override 가능하게 확장
2. domain_state Literal 필드를 one-hot encoding으로 embed
3. relationships/network를 aggregate feature로 추가

이 발견은 `test_cross_scenario_separability.py`에 regression guard로 고정. 만약 미래에 feature set을 확장해서 Talleyrand separability가 0.5를 넘으면 테스트가 실패하여 **lessons.md 업데이트 신호**가 된다.

### 교훈 15: Stage 2 진입 전 **항상** 각 시나리오에 feasibility 측정 실행하라 (Iter 66)

Iter 65에서 Peter separability 1.93 확인 후 "Stage 2 feasible" 판단.
Iter 66에서 Talleyrand 돌리니 0.05. **한 시나리오 측정만으로 feasibility 결론 금지**.

다음 단계(PyTorch 구현)를 시작하기 전 반드시:
1. 모든 active scenario에서 separability 측정
2. 최저 scenario도 ≥ 0.5 이상일 것 (feature universality 검증)
3. 그렇지 못하면 PyTorch 구현 전에 feature extractor 확장 먼저

### 교훈 17: Talleyrand action-predictability 붕괴의 진짜 원인은 feature가 아니라 behavior_profile (Iter 69)

Iter 66-68에서 "feature가 domain_state 무시" 를 원인으로 지목하고 해법 시도. Iter 69에서 learned LogisticRegression 으로 진짜 한계 측정:

| Scenario | Majority baseline | Logit on 12-feature |
|---------|------------------|---------------------|
| Peter | 12.5% | **45.5%** (3.6× chance) |
| Talleyrand | 47.8% | 45.6% (**at or below chance**) |

**진단**: Peter action은 state → action 관계가 강해서 learned linear classifier도 3.6× 이득. Talleyrand는 learned classifier조차 majority 못 이김 → **state 자체가 action을 결정 못 함**.

**원인 (content-level)**: `content/talleyrand/behavior_profile.json`의 `base_weight` 값 (maintain_network=3.0, serve_current_regime=2.5, ...)이 `state_multipliers` scale (0.1~0.2) 대비 압도적. action 선택이 state 변화에 둔감.

**구조적 교훈**: Stage 2 학습의 학습 가능성은
1. feature gap (Iter 66-67) — state가 관련 정보 포함하는가
2. **policy gap (Iter 69)** — action이 그 state에 실제로 민감한가

둘 다 해소되어야 의미 있는 학습 가능. Iter 66-67은 (1)만 측정/수정했지만 (2)는 건드리지 않아 효과 없었음.

**향후 조치**: Talleyrand `behavior_profile.json`을 state-sensitive하게 재작성 (base_weight 감소 or multiplier scale 증가). 다시 측정 → logit acc가 majority를 의미 있게 넘어야 Stage 2 투자 가치 확인.

`test_behavior_profile_state_sensitivity.py`가 현 profile 상태 (base dominant)를 regression lock-in. 향후 수정하면 이 테스트가 실패 → lessons 업데이트 trigger.

### 교훈 18: behavior_profile 튜닝만으로는 Talleyrand 학습 가능성 완전 해소 안 됨 (Iter 70)

Iter 69 finding 기반 조치: base 2.5-3.0 → 0.2-1.0, multipliers 0.1-0.2 → 0.4-0.9 로 재튜닝.

**재측정 결과**:
- majority: 0.478 → 0.535 (분포 더 집중)
- logit acc (base 12-feature): 0.449 → 0.551
- majority 대비 이득: -2.9%p → **+1.6%p** (negative → barely positive)

**판정**: 해소 방향은 맞지만 **충분하지 않음**. 5-class 문제에서 majority 53.5% 기준 +1.6%는 statistical noise 급.

**남은 bottleneck (hypothesis)**:
1. **Action cardinality 부족**: Talleyrand 5 actions vs Peter 24 actions. 5-class balanced 분류에서 "state에 의존" 이득이 수치로 드러나기 어려움.
2. **State trajectory discreteness**: regime 전환 이벤트가 state 값을 reset + 주요 변경. intra-regime 에서는 state가 거의 정적 → classifier가 "state feature"와 "regime indicator"를 같은 정보로 활용.
3. **Feature-action alignment**: `voice_principle`은 `legitimacy_anchor`에만 의존하는데 `legitimacy_anchor`는 tick별 거의 안 변해서 같은 action이 majority.

**다음 단계 대안** (Stage 2 구현 전에 시도할):
(a) Talleyrand에 더 많은 action + 더 밀도 있는 canonical events 추가
(b) state_noise_scale 을 0.02 → 0.05 로 올려 intra-regime 탐색 다양성
(c) 위 둘 다 실패 시 Talleyrand는 "event-driven scenario"로 규정하고 Stage 2 feature에 `last_k_events` history를 포함

**Iter 78 empirical**: (a)의 일부 — 3개 intermediate canonical events (Hundred Days, Vienna Settlement, Napoleon death) 추가. 재측정: majority 0.547, logit 0.558, separability 0.053. **측정 전과 사실상 동일**. event 추가만으로는 action-state coupling 안 바뀜을 empirical 확인. 5-action 카운트 자체가 structural bottleneck. → "event density 증가"는 버리고 "action cardinality 증가 (7-10)"가 남은 유일 대안.

**Iter 79 empirical**: action cardinality 5→8 (write_memoirs / form_salon / consult_aristocracy 추가, 각 다른 domain_state 필드 의존). 재측정: classes 5→7 (write_memoirs n=1 filter), majority 48.7%, logit **49.0%** (majority 수준), separability **0.112 (2× 개선)**. 혼합 신호: separability는 실제 개선(드물게 선택되는 action들의 drive mean이 dominant 와 달라서 Fisher ratio 상승) 있지만 logit classifier는 rare class에 과적합 피하면서 majority 예측 → 실질 학습 불가.

**교훈 19 (Iter 79 결론)**: Action cardinality 추가가 separability 수치는 올리지만 **actual predictability는 오히려 악화**. 진짜 해법은 "action 추가"가 아니라 "action 분포 고르게"하기 — 즉 기존 dominant action (maintain_network 49%, serve 25%)의 가중치를 크게 낮추고 새 action 의 multiplier를 키워서 actual firing rate가 10-20% 수준에서 경쟁하도록. 이는 content balancing 작업 (여러 iteration 소요) 영역이라 single loop iter 가치 불충분 → 진정한 stopping point.

**Iter 80 empirical (마지막 시도)**: maintain_network base 1.0→0.5, serve_current_regime base 0.8→0.4. 재측정: majority **48.7%→41.3% (분포 균등화 성공)**, logit **49.0%→42.2% (여전히 majority 수준)**, separability 0.11→0.12. 분포는 좋아졌으나 classification 개선 없음 → single-dimension tuning (base weight)만으로는 불충분. Per-action 의 state_multiplier 구조를 처음부터 재설계해야 state→action mapping이 학습 가능한 수준에 도달. **확정 결론**: Talleyrand Stage 2 target은 deferred, 현 설계에서는 universality proof 역할만 유지.

**메타 교훈**: 한 axis (base_weight)만 조정하고 성공/실패 판정하지 말 것. 여러 개 묶인 설계 choice(actions count, event density, noise level, profile weights)를 동시에 본 다음 empirical 재측정 필요.

### 교훈 16: Feature를 추가한다고 separability가 자동으로 올라가지 않는다 (Iter 67)

Iter 66 gap 해소 시도:
- `DomainState.to_feature_vector()` protocol 추가
- `DiplomacyState.to_feature_vector()` = regime 7-onehot + stance 5-onehot + 3 scalars = 15 feature
- `ExtensibleFixedProjectionEncoder` = lazy init W, variable feature length

결과: Talleyrand separability가 0.24(fixed 12-feature)에서 0.19(extended 27-feature)로 **오히려 감소**.

**원인**: random projection (tanh(x @ W_random))은 sparse one-hot 특징을 자동 활용 못 함. 추가 feature 차원이 `drive_std`(within-class variance)에 기여하는데 `drive_mean` (between-class)에는 기여 안 함 → Fisher ratio 하락.

**교훈**: Feature gap은 **learning에 의해서만** 닫힌다. 구조화된 feature(one-hot, categorical)는 learnable projection에서만 signal. random projection에서는 오히려 noise.

**Stage 2 PyTorch 구현 필요성이 더 분명해짐**: Peter/VG처럼 continuous emotion-driven scenario는 random projection으로도 separability 확보 가능하지만, categorical/regime-driven scenario는 PyTorch MLP (end-to-end 학습으로 one-hot weight 조정)이 없으면 drive가 의미 있는 표현이 되지 않는다.

`test_extensible_encoder.py::TestFeatureGapDocumentation`이 이 사실을 regression lock-in.

### 교훈 13: "Universality"는 두 층위로 나눠서 주장하라 (Iter 54-57)

Peter/VG 두 시나리오만 있을 때는 "structural isomorphism"이 우선이었지만, 3번째 이질적 시나리오(Talleyrand Type A 협상형) 추가 후 새 증거 구조가 나왔다:

- **Engine universality (주장 가능)**: 같은 `SimulationWorld + RuleEngine`이 Peter(bottleneck) / VG(isolation-breakdown) / Talleyrand(regime transition) 세 가지 질적으로 다른 동역학을 모두 수용. POM scorecard 교차 적용이 asymmetric (Talleyrand-on-Peter = 0%, Talleyrand-on-Talleyrand ≥ 80%)으로 이를 직접 측정.
- **Empirical generalization (여전히 금기)**: 각 시나리오의 수치 claim — Peter arrest 100%, Cohen's d=-6.87, Talleyrand network_regime_span ≥ 4 등 — 은 그 시나리오 content 자산이며 다른 인물에 옮겨 쓸 수 없다.

**왜 이 구분이 중요한가**: 논문 리뷰어에게 "이 프로젝트는 2 시나리오로 universality 주장한다"는 비판을 받지 않으면서도, "이 엔진이 임의 새 시나리오를 수용할 수 있다"는 기여를 명시적으로 주장할 수 있다. 표현 권장: *"the engine is scenario-agnostic; the patterns are scenario-specific"*.

Iter 57 `test_cross_scenario_pom_asymmetry.py`가 이 주장의 재현 가능한 증거. 향후 4번째 시나리오 추가 시에도 동일 테스트를 돌려 asymmetry 유지 여부 확인 필수.

---

## v2.0 World Engine — Spike 1 + 2 교훈 (2026-04-21)

### 교훈 19: Layer 경계에 per-cross-edge 브레이크 필수

WORLD_DESIGN v1.1 리뷰어 #2가 정식 요구: 모든 cross-layer 의존에 delay / threshold / saturation 중 하나 이상을 배치. Spike 1 구현 시 지킨 패턴:

- Calendar → Crowd: decay(tau=3.5d) + clamp(ceiling) — **saturation**
- Calendar → Economy: 3-day IIR memory 0.66 + clamp — **delay + saturation**
- Crowd → Politics: threshold(≥5) step + clamp — **threshold + saturation**
- Calendar → Politics (Pilate 위치): approach_lead_days 창 + stay_days 창 — **delay**

**교훈**: 브레이크를 빼먹으면 linear amplification이 되어 Layer 한쪽의 noise가 다른 쪽으로 무한 전파된다. "모든 edge에 브레이크"는 반드시 *코드가 아니라 설계 단계에서* 결정해야 하고, `describe_dynamics()["brake_type"]`으로 runtime 검증 가능해야 한다.

### 교훈 20: 같은 tick 안의 순환 의존은 DAG 테스트로 차단하라 (Spike 2 A-3)

ChatGPT 리뷰어가 Spike 2 진입 조건으로 요구. 구현:

- 모든 Layer가 `describe_dynamics()["causal_dependencies"]`에 same-tick 의존성을 선언 (`crowd.crowd_density` 등).
- 1-tick delay가 필요한 읽기는 `@prev_tick` 접미사로 표기.
- `tests/test_world/test_layer_dag.py::test_tick_order_is_a_dag`가 topological order와 선언 의존이 일치하는지 자동 검증.

**교훈**: Python type system은 same-tick cycle을 못 잡는다. 런타임 검증 테스트를 한 번만 작성해두면 Spike 3+ 에서 faction ↔ crowd 같은 되먹임이 실수로 추가돼도 즉시 감지된다. ABSOLUTE RULE #9로 승격.

### 교훈 21: 기존 엔진 래핑 통합 — `engine/` 수정 없이 day-chunking

Spike 2 B-3에서 `IntegratedWorldRunner`를 만들 때 Person Engine을 수정해야 하나 고민했으나, 실제로는 wrapping만으로 충분했다:

1. 매 world day마다 `SimulationWorld`를 `max_tick=12`로 새 인스턴스 생성
2. 이전 session final_states를 다음 session initial_states로 carry-forward
3. `state.tick`에 `day * substeps_per_day` offset을 수동 주입해서 연속 tick 축 유지
4. `ExternalEvent`(절대 tick 고정)만 비활성화 — triggers + hazard_events는 그대로

**교훈**: 기존 엔진 API를 "한 세션"으로 보고, 세션들을 "external orchestrator"가 chain하는 구조가 가장 안전하다. `engine/` 내부 코드를 건드리고 싶은 유혹을 이겨내면 기존 1003 tests가 계속 green.

### 교훈 22: Action → World는 이름 스위치가 아니라 속성 기반으로 generic

Spike 2 B-2에서 초기 충동: `if action_id == "inform_authorities": emit authority_threat`. 리뷰어 #5가 명시적으로 금지.

실제 구현:
- `action.visible_signal is not None` → `publicity_shock` (공개적이라는 property)
- `action.observable_from ∩ {caiaphas, pilate, sanhedrin}` → `authority_threat` (관찰자 속성)
- `visible_signal` 안의 키워드 (`inform`, `betray`, `teach`, `cleanse` 등) → `rumor_seed`

**교훈**: action-name switch는 content 패키지와 world engine을 결합시켜서 "새 인물 추가 = world code 수정"이 된다. 속성 기반(visible_signal / observable_from / intensity) 매핑은 content가 새 action을 추가해도 world는 손 안 대도 된다. Spike 3 factions, Spike 4 interventions 준비에도 필수.

### 교훈 23: ceiling 포화는 discriminative 지표를 감춘다 — overflow_pressure 필요

Spike 2 A-2 동기: Spike 1 데모에서 Passover crowd_density가 3일간 10.0(ceiling)에 붙어있었다. "얼마나 붐비는가"가 ceiling에서 모두 동일하게 보임. Peter fear도 같은 이유로 standalone vs world가 둘 다 ~9.9로 수렴 → B-4 test에서 fear-final delta 감지 불가.

**교훈**: 포화 가능한 state에는 항상 pre-clamp raw 값을 별도 필드로 저장 (`overflow_pressure`). 안 그러면 분석이 "둘 다 ceiling" 같은 거짓 null 결과를 만든다. Spike 3 `faction_influence`, `rumor_intensity`도 동일 설계 필요.

---

## v2.0 Spike 3 이후 계획 메모

- **Spike 3 우선순위**: Layer 4 (factions — 바리새 / 사두개 / 열심당 / 예수 운동 5-6개) + Layer 5 rumour graph.
- **Jesus as agent** (v1.1 amendment ABSOLUTE RULE #3): 예수를 Tier 1 Agent로 content/jesus/ 패키지 생성. 정경 말씀은 개역개정 verbatim, behavior_profile은 teaching / healing / rebuke 3-5 action만.
- **시급하지 않은 것**: 인터랙티브 UI, v0.6 논문 final 제출 (별도 결정 필요). 세계 시뮬레이션이 먼저 agent 상호작용으로 입증되어야 논문의 v2.0 부분을 쓸 수 있음.
- **리뷰 조건 중 미결**: percept interpolation cadence (Q6), Jesus dominance 제어 (Q7). 둘 다 Spike 3 진입 전에 해결 필요.

### 교훈 24: 정성적 발견은 정량 invariant로 pin하라 (/loop 자율 운영 중)

Spike 2 통합 모드에서 관찰: Judas 제거 시 trigger count 207 → 78 (62% 감소). 초기 test는 "triggers / events / fear 중 하나라도 다르면 pass"라는 약한 assertion이었다. Spike 3 이후 faction이나 rumour가 Judas 역할을 무의식중에 대체해도 감지 못 함.

강화 후: `drop_ratio >= 0.25` 으로 정량 하한 pin + 실패 메시지에 디버깅 힌트 ("Judas state_conditions 변경 or 다른 agent compensation") 포함.

**교훈**: 루프가 돌아가는 프로젝트에서는 **"관찰했다"와 "보장한다"가 다르다**. 관찰한 수치를 다음 루프가 언어화된 invariant로 자동 확인하도록 바꿔야 자산이 누적된다. "test는 pass만 중요한 게 아니라 fail 메시지가 다음 본인을 디버깅할 수 있게 해야 한다".

baseline 62%에 25% 하한은 의도적으로 3배 여유 — 모델 tuning이 현실적으로 30-40% 감소로 수렴해도 test 안 깨지되, 5-10% 같은 "효과 없음" 수준은 즉시 감지.

### 교훈 25: 자동 파이프라인(스크립트 체인)은 smoke test로 silent fail 방지

`world_numbers.py` + `world_figures.py`를 매 /loop마다 돌리면서 "JSON/PNG가 생성되면 성공"으로 판단하는 건 **silent fail 취약**. 예: n_days < 65로 호출하면 `densities[SHAVUOT_DAY]` IndexError — 로컬 실행 아닌 테스트 환경에서만 노출됨.

smoke test 도입으로 즉시 감지 + 고치면서 동시에 잠재 버그(n_days 의존) 발견. 3 tests로 다음 regression 자동 감지 ready.

**교훈**: 산출물 체인은 **pipeline smoke test**가 필수. 검증 기준:
1. 작은 입력(1-2 seeds / 20 days)으로 script API 호출 → crash 안 남 + shape 맞음
2. 생성된 artifact (JSON 구조, PNG 크기) sanity check
3. fixture 기반 dry-run으로 main I/O 분리 검증

이 패턴은 Spike 3 이후의 `world_factions_numbers.py` + `world_factions_figures.py` 같은 script에도 그대로 복제.

### 교훈 26 (메모): Loop 자율 운영의 "consolidation 함정"

루프 5-7이 모두 consolidation만 함 (smoke / pin / 정량 invariant). 품질은 올라갔지만 새 capability는 없음. 루프 실행 중 자가 감지 필요:

- consecutive loops에서 새 공개 API / 새 content / 새 layer / 새 integration 없으면 "다음 loop은 capability-adding" 명시 판단
- defensive work은 도메인에 따라 2-3 loops까지 연속 허용, 그 이상은 scope fatigue signal

이번 세션 사례: 루프 #7 이후 "루프 #8부터 Spike 3 진입 설계"로 pivot 결정.

### 교훈 27: Cross-layer chain counterfactual은 control faction과 함께 pin하라 (Spike 3 Phase 3D)

Judas → rumour → jesus_movement 체인을 content-level pin으로 기록할 때, 단순히 "Judas 제거 시 jesus_movement 감소"만 assertion하면 **global noise** vs **specific effect** 구분 못 함. 만약 Judas 제거가 모든 faction influence를 globally 낮춘다면 (예: 세계 분위기 악화), jesus_movement도 함께 떨어지겠지만 그건 특정 채널의 효과가 아니다.

해결: **control faction**도 동시에 검증.

```
assert jesus_movement_drop >= 40%          # effect: rumour edge 동작
assert pharisees_drift < 20%                # specificity: non-sensitive 유지
```

실측: jesus_movement 9.9→3.8 (-62%), pharisees 6.18→6.18 (0%). 62%/0% 대비는 "specific effect" 증명의 확실한 증거.

**교훈**: Causal claim에는 항상 **positive case** + **matched negative control**을 짝으로 pin. 생물학/의학의 double-blind controlled 설계가 simulator counterfactual에도 적용된다.

### 교훈 28: Layer tick order는 cross-layer edge 방향 결정 시 미리 고려 (Spike 3 Phase 3D)

Spike 3에서 rumour → faction edge를 추가할 때, tick order를 calendar→crowd→economy→politics→**rumours**→**factions**로 재배치. rumour가 factions 이전에 tick되므로 `rumors.active_intensity()` 를 same-tick으로 읽음. 만약 순서가 반대였다면 `@prev_tick`이 필요했을 것 — 1-day lag 추가.

**교훈**: cross-layer edge를 설계할 때 "어느 쪽이 먼저 tick되어야 same-tick edge로 가능한지" 먼저 판단. 이건 reviewer #2 "delay brake"를 의식적으로 OFF 하는 결정. 내재적 lag가 의도된 경우에만 `@prev_tick`. 이번 경우 "agent가 오늘 rumour를 심으면 아직 faction은 내일 영향 받음" (이미 sync layer가 1일 지연 도입) + "그 다음 날 factions가 read할 때는 rumours가 이미 발전된 상태" → 추가 lag 불필요.

### 교훈 29: Content 언어와 code keyword 매칭 함정 (Spike 3 Phase 3C, loop #14)

`actions_to_effects`가 `visible_signal` 문자열에 영문 키워드(`inform`, `betray`, `teach`)를 스캔. AD-30 content는 visible_signal이 **한국어**("유다가 당국에 유다고 알렸다") 라서 매칭 안 됨 → 90일 동안 rumor_seed 0건. Snapshot에 0 이 기록되어서야 발견.

수정: `action_id` (엔진 convention으로 항상 영문 `"inform_authorities"`)에도 키워드 스캔 fallback.

**교훈**: content는 사용자 언어로 쓰이지만 `action_id`는 엔진 인터페이스. Generic 매핑 코드는 **언어 중립 필드** (`action_id`, `intensity`, flags) 기준으로 작성하고 content 텍스트는 fallback으로만. 앞으로 유사 패턴 주의: "visible_signal 스캔" 대신 "action_id 스캔 → visible_signal fallback".

세 번째 교훈: 이런 버그는 snapshot이 없으면 절대 감지 안 됨. 스냅샷 + smoke test 조합이 조용한 오작동 자동 감지 조합.

### 교훈 30: `describe_dynamics()` 는 phase 전환 의식화 장치 (Spike 3 Phase 3A→3B→3D)

FactionLayer가 Phase 3A (독립) → 3B (+crowd) → 3D (+rumour)로 진화하면서 매번 기존 테스트 `test_describe_dynamics_declares_expected_dependencies_phase3b` (후에 3d)를 수정했다. 이건 **의식적 전환 기록** 역할을 함:

- 테스트가 `assert causal_dependencies == ["crowd.crowd_density"]` 였다가
- 새 edge 추가할 때 테스트도 `== {"crowd.crowd_density", "rumors.active_intensity"}`로 업데이트
- → 새 edge가 **의도적**으로 추가되었음을 git history에 남김

Alternative: 테스트를 `assert "crowd.crowd_density" in deps` (in-check)로 두면 새 edge 추가해도 알림 없이 테스트 통과. 그러면 cross-layer 의존성이 drift.

**교훈**: `causal_dependencies` assertion을 **set 동등성**으로 쓰고, 새 edge 추가 시 test 수정 강제. 이 "forced code review" 패턴은 API surface 드리프트 방지에 유효.

---

## v2.0 Spike 4 이후 계획 메모

- **Spike 4** (완료, 2026-04-22): variable-intervention framework 구현 + 3종 실험 실행. "예수 Agent 제거 시 세계 차이"는 content/jesus/ 필요.
- **Phase 3E/F/G** (선택적): explicit emitter declaration, per-action rumour content, faction influence → agent EnvironmentState.
- **2번째 World** (예: arles_1888 for Van Gogh): 엔진 범용성 입증, "engine universality" 주장 확장.
- **외부 리뷰 4회** (SPIKE_1/2/3/4_REVIEW.md, 1394 lines total): 일괄 전달 → 반영 → Spike 5 설계 문서화.

### 교훈 31: Counterfactual framework를 primitive-declarative로 설계 (Spike 4 Phase 4A)

Spike 4 initial 유혹: "remove_judas", "lenient_pilate" 같은 **named intervention** 을 class로 구현. 그러면 새 실험마다 class 추가 = framework 확장성 낮음.

해결: **primitive-declarative spec**.
- `InterventionSpec` frozen dataclass, 11 primitive 필드
- 모든 실험은 primitive 조합 — `remove_judas` = `{agent_remove: ["judas"]}`, `lenient_pilate` = `{pilate_bonus_override: 0.0, ...}`
- content/interventions/*.json 으로 JSON declarative — 코드 변경 없이 새 실험 추가
- InterventionEngine이 primitive 순서대로 apply (destructive → additive → scaling → override)

**교훈**: framework를 "action 이름" 기준이 아니라 "원자 operation" 기준으로 설계. Reviewer #5 원칙 (action-name switch 금지)과 동일 — 이번엔 intervention-name switch 금지. Primitive 조합이 거대한 가능 공간을 열어줌.

### 교훈 32: Null-spec bit-identical test는 framework 신뢰도 증명 장치 (Spike 4 Phase 4B)

BatchRunner의 control arm은 "null spec을 apply한 결과 = 원본"이어야 함. 테스트 `test_null_intervention_produces_bit_identical_arms`가 이걸 seed-by-seed로 강제:

```python
null_spec = InterventionSpec(intervention_id="noop")
result = runner.run_experiment(null_spec, n_seeds=2, n_days=15)
for cs, ix in zip(result.control.per_seed, result.intervention.per_seed):
    assert cs.metrics == ix.metrics   # bit-identical
```

이게 깨지면 deep_copy 어딘가 누락 → intervention framework가 **잘못된 control**로 비교하는 셈. 치명적.

**교훈**: counterfactual framework의 첫 test는 null control identity. 모든 deepcopy / 모든 primitive의 "no-op 기본값"이 bit-exact를 보장해야 함. p-value가 낮다고 다른 테스트 지나가도 이 테스트는 never-skip.

### 교훈 33: Spike 3 결과를 Spike 4에서 독립 재현 = 검증 2단계 (2026-04-22)

Spike 3 Phase 3D는 "Judas→rumour→jesus_movement" 체인을 발견했고, `test_phase_3d_judas_removal_collapses_jesus_movement_influence`로 pin했다. Spike 4에서 완전히 **다른 framework** (`InterventionSpec + BatchRunner`)로 같은 실험을 실행했는데 동일 signal 재현:
- Spike 3 Phase 3D: rumours 77→0, JM 9.9→3.8 (90 days, 3 seeds)
- Spike 4 remove_judas demo: rumours 21.5→0, JM 6.71→2.95 (30 days, 2 seeds)

수치는 scale이 다르지만 (days/seeds 규모) 패턴 (100% rumours collapse, ~56% JM drop, pharisees 0%) 동일.

**교훈**: 같은 finding을 **두 framework**로 재현하면 실험 자체의 신뢰도가 제곱된다. Spike 4 framework가 정확하다는 증명 + Spike 3 finding이 framework-invariant라는 증명이 동시에 이뤄짐. 논문 주장 시 이런 **redundant confirmation**이 reviewer 설득력 가장 강함.

### 교훈 34: Saturation confound는 counterfactual framework에서도 재등장 (Spike 4 lenient_pilate zero effect)

`lenient_pilate` intervention (pilate_bonus=0, approach=0, threshold=8) 이 30일 run에서 **모든 metric 0 변화**. 원인 분석:
- Pilate → alertness → agent fear 체인이 있음 (Sync Layer 통해)
- 하지만 fear는 Passover 이미 9.84 saturation
- 따라서 "alertness가 원래 8이었는지 5였는지"의 차이가 fear로 안 나타남

이것은 **Spike 2 A-2 overflow_pressure** lesson의 재등장 — ceiling에 saturate된 state는 intervention effect를 삼킨다.

해결 옵션 (SPIKE_4_REVIEW.md Q5 제기):
1. `overflow_fear` 추가 (raw pre-clamp 값)
2. time-to-saturation metric
3. Area-under-curve metric

**교훈**: counterfactual framework는 "pinned state"만큼만 보임. ceiling-saturated 출력 metric은 intervention을 측정할 수 없다. 새 metric 추가 시 반드시 "이 metric이 ceiling에 바인딩되는가?" 체크. 바인딩된다면 같은 state의 raw pre-clamp 또는 dynamics metric (peak/slope/time-to-threshold)을 병기.

### 교훈 35: Full-power run이 framework invariance + metric blind spot 둘 다 증명 (Spike 4 full 10×90)

2 seeds × 30 days 데모와 10 seeds × 90 days 풀런 비교 (2026-04-22):

| metric | 데모 | 풀런 | 비율 | 의미 |
|---|---:|---:|---:|---|
| remove_judas rumours Δ (Cohen's d) | -14.3 | -29.1 | 2.0× | seed/day 3배 늘자 √n-stable — framework 정상 |
| remove_judas JM influence Δ (Cohen's d) | -5.3 | -69.5 | 13× | JM이 더 긴 run에서 ceiling 더 안정 → variance 더 작음 → d 폭발 |
| hazard_half Cohen's d | -0.5 | **0.0** | — | 데모 weak signal이 풀런에서 **소멸** → noise였음 |
| lenient_pilate Cohen's d | 0.0 | 0.0 | — | 일관 — 진짜 zero effect (metric blind spot) |

**이중 검증**:
1. **Framework invariance**: remove_judas Cohen's d 절대값이 (sample size) 증가에 따라 monotonically 증가 → framework가 실측 분포를 올바르게 처리 (p-value가 0.39에서 0.000으로 강화).
2. **Zero-effect의 두 가지 의미 구분**:
   - **Weak signal (데모 d=-0.5)** → 풀런에서 0 → **진짜 noise**
   - **Zero in 데모 AND 풀런** → **metric이 effect를 surface 못 함** (hazard pipeline + 정치 pipeline 모두)

**교훈**: "결과가 안 보임 = 효과 없음"을 섣불리 결론 내지 말 것. 두 가지 가능성 구분:
- (A) 진짜 weak/zero effect → power 증가로 소멸
- (B) metric이 포착 못 하는 효과 → power 증가해도 여전히 zero

(B) 판별 방법: Cohen's d 절대값 sample size에 불변 (scale invariant 0). (A)는 √n-shrinkage. 풀런 실행은 (A)/(B) 구분 필수 tool — demo에서 중단하면 (B)를 (A)로 오인.

연관: Spike 5+에서 hazard/politics intervention을 surface할 metric 확장 필요 (SPIKE_4_REVIEW Q5):
- `hazard_count` tracked table 추가
- `surveillance_auc` (area under curve)
- `time_to_fear_saturation` (when does peter_fear cross 9.0?)

이 세 가지 중 하나 이상이 있어야 lenient_pilate 같은 정치 intervention의 effect를 측정할 수 있다.

### 교훈 36: Intervention primitive가 "의도"를 완전히 반영하는지 확인 (Spike 4 hazard_rate_scale 버그, loop #30)

`InterventionSpec.hazard_rate_scale` 초기 구현은 `HazardFunction.base_rate`만 scale. 그러나 Witness content의 hazard는 상태 의존 `factors` (e.g., `0.15 * emotions.fear + 0.1 * physical.fatigue`)도 hazard에 기여. Peter fear 9.83 saturate 시 factor 기여 = 1.47 >> base_rate 0.005.

**결과**: `hazard_rate_scale=0.5`를 적용해도 hazard_count가 거의 변하지 않음 (d=-0.22). 유저 의도 "hazard pipeline을 반으로"와 달리 **base_rate만 반으로** 되었을 뿐.

**진단 과정** (교훈 35의 방법 적용):
1. 3-seed × 30일 demo에서 hazard_half가 d=-0.22 — weak signal or blind spot?
2. Full 10×90 run: d=+0.01 (noise로 소멸) → "blind spot" 판정
3. `hazard_rate_scale=0.01` 극한 실험 (100x 감소): 그래도 hazard_count 동일
4. 직접 SimulationWorld 실행: 동일 → BatchRunner 외부 원인
5. HazardFunction 코드 분석: `h = base_rate + Σ factor.compute(state)` — factor가 base_rate 지배

**수정**: engine 내 primitive 구현에서 `base_rate *= scale` + `factor.weight *= scale` 모두 적용.

**수정 후 결과**: hazard_half에서 hazards 74.9→52.8 (-30%, d=-3.64, p=0.000). 명확한 effect, 타 metric 유지 (specificity preserved).

**교훈**: 
1. Counterfactual primitive는 "user intent = ~X 이 halves"를 완전히 반영해야 함. 단일 필드만 건드리면 content의 다른 필드가 효과를 삼킨다.
2. Framework 정확성 증명 = null-spec identity (교훈 32) + 극한 값 (100x) intervention 확인. 두 가지 다 통과해야 framework 믿을 만함.
3. Debugging pattern: framework → SimulationWorld 직접 → HazardEngine 내부. 각 layer에서 identical output이 나오면 그 layer가 범인 아님. 위에서부터 차례로 책임 제외.

### 교훈 37: Saturation-robust metrics (time-to-threshold + AUC)로 ceiling blind spot 완전 해결 (loop #31)

교훈 34 saturation confound 진단 후 실제 해결을 이번에 완성. 두 종류의 metric 추가 (engine/ 수정 없이, `_extract_metrics` 확장만):

1. **`peter_fear_crosses_9_day`**: peter fear가 처음 9.0에 도달한 day index. 9.0에 도달 못 하면 n_days 반환. Ceiling에 바인딩되지 않음 — 도달 속도가 신호.
2. **`roman_alertness_auc`**: 매일 politics.roman_alertness의 적분 (단순 합). 각 개입이 alertness 전체 궤적에 미치는 영향을 단일 수치로 축약.

**결과 (10 seeds × 90 days)**:

| intervention | blind raw metric | resolved metric | Cohen's d |
|---|---|---|---|
| lenient_pilate | P fear (saturated) | roman_alertness_auc | **-70.72** |
| hazard_half | P fear (saturated) | peter_fear_crosses_9_day | **+0.87** |
| remove_judas | (already visible) | — | d=-46 on JM |

**lenient_pilate blind spot 해결**: raw metric 0 / AUC metric Cohen's d=-70.72 p=0.000. 즉 intervention은 명확한 효과 있었는데 measurement problem이었음을 직접 증명. 특히 pharisees(control) 0 drift 여전 유지 → specificity 증명 병행.

**교훈**: counterfactual framework에 새 state가 추가될 때마다 3종 metric 병기 권장:
1. **Final-value** (raw) — 가장 단순, 해석 쉬움. Ceiling 주의.
2. **Time-to-threshold** — 속도 측정. Saturation robust.
3. **Path integral (AUC)** — 누적 효과. Saturation robust + 분포 정보 보존.

Raw만 있으면 effect를 missed, AUC만 있으면 final 해석 잃음. 3종이 서로 보완.

연관: 이 해결법은 engine/ 수정 필요 없음 — `_extract_metrics`의 `result.days` traversal로 모든 시점 상태에 접근 가능. 프레임워크 설계의 숨은 자산: **metric extraction이 simulation step과 완전히 분리**되어 있어서 event post-hoc에 새 metric 추가가 무료.

---

## v2.0 Spike 5 — Part 1 + 2 교훈 (2026-04-22)

### 교훈 38: 방금 박은 규칙과 충돌하는 다음 액션을 자동 거부하라 (Spike 5 Part 2 보완 루프)

Spike 5 Part 2 완료 직후 /loop 자율 운영 중, 한 iteration에서 Rule #10 ("세계 확장 spike에서 paper_data/ 재생성 금지")을 CLAUDE.md에 영구 명문화했다. 그 직후 다음 iteration에서 "Spike 4 demo 재실행으로 Cohen's d=-69.52 수치 재확인"을 계획했는데, 이건 `demo_spike4_interventions.py`가 `docs/world/paper_data/`에 intervention JSON을 덮어쓰는 파이프라인 — **방금 박은 Rule #10 (c) 직접 위반**.

사용자의 갱신된 /loop 프롬프트 rule("설계 방향이나 ABSOLUTE RULES와 충돌하는 지점은 멈추고 보고해")이 이 상황을 멈춤 신호로 명시했기에, 실행 전 stop-and-report로 전환하고 `lessons.md` 갱신으로 재정렬했다.

**교훈**: 루프가 규칙을 scope에 추가한 직후는 **규칙-알리바이 충돌 위험이 가장 높다**. 직전 루프 산출물이 규칙 자체이면, 다음 루프 계획은 "이 규칙이 방금 만들어졌다면 어떻게 해석되는가?" 관점으로 스스로 감사. 자동화:
- 새 Rule 항목 추가 iteration 직후에는 pending 액션 목록을 다시 필터
- `paper_data/` 또는 `content/interventions/` touch 계획이 있으면 Rule #10 명시 체크
- scope-narrowing 액션(coverage, docs)이 다음 단계로 안전한 기본값

### 교훈 39: "세계를 두껍게" spike에서도 counterfactual 유혹은 다양한 모양으로 온다 (Spike 5 Part 2)

Spike 5 Part 2 구축 중 의식적으로 거부한 유혹:
1. `remove_jesus` / `remove_pilate` / `remove_caiaphas` intervention 추가 — 신규 agent의 structural effect 측정하고 싶은 욕구
2. `demo_spike5_multi_agent.py` 같은 E2E 스크립트 — 통합 모델 실측 궁금증
3. Spike 4 3종 intervention 재실행 + Spike 5 agents 통합 효과 비교 — "공짜 실험"
4. temple_economy 파라미터 sweep — 민감도 분석 욕구

넷 다 Rule #10 위반. Part 2 완료 checklist의 *"실험 상태: 신규 intervention 0개"* 는 이 압력 모두 받아낸 후의 결과. 

**교훈**: 세계 확장 spike에서 "검증하고 싶다"는 압력은 4가지 이상의 모양으로 나타난다 — JSON spec, demo script, batch run, parameter sweep. Rule #10은 이 넷 전부를 포괄적으로 금지. *behavior test only*가 spike 기간 내 **유일한** 검증 채널이며, 양적 수치 claim은 전부 차기 spike(7+) 몫.

### 교훈 40: Multi-path emitter는 single-point failure의 **구조적** 회피 장치 (Spike 5 Part 1+2)

Jesus agent 5개 action 중 **3개** 가 `faction_influence_jesus_movement` 채널로 emission (teach 직접 / heal via crowd testimony / bless via disciple witness). 이는 외부 리뷰어가 Spike 5 §4.2.2에서 요구한 "single-point failure 회피".

이유: 미래 `remove_jesus` 실험을 할 때 jesus agent 하나만 제거하면 faction 영향력이 0으로 떨어지는 "choke point 효과"가 생김 — 하지만 그건 구조적 특성(1대1 매핑)이지 신학적/역사적 실제 역학을 반영하지 않음. **3개 이상의 action path**가 있으면 agent 제거 시에도 crowd testimony / disciple witness 경로가 부분적으로 살아남아, agent-level vs network-level 효과를 분리 측정 가능.

Caiaphas도 비슷한 설계: `convene_sanhedrin` 하나가 pharisees + sadderucees 양쪽에 동시 emit (hub 역할). 이걸 `hub_reaches()` 메서드로 behavior test에서 직접 검증 가능.

**교훈**: counterfactual 실험을 안 하는 spike에서도, **미래 실험을 망치지 않는 구조** 설계가 가능. Rule #10은 실험을 막는 게 아니라 **지금 측정하지 않지만 나중에 측정 가능한 세계**를 요구. 구체적 지표: "이 agent 하나 제거 시 영향 경로가 몇 개 남는가"로 설계 품질 판단.

### 교훈 41: Doc-code sync는 "3일 stale" 를 정량 기준으로 (auto-memory 갱신 루프)

Spike 5 Part 2 완료 후 `docs/world/README.md`, `progress.md`, auto-memory `project_witness.md` 가 모두 Spike 4 시점에서 멈춰 있었음. `project_witness.md`는 system이 "3일 old" 경고를 출력 — 이 경고가 **stale 감지 정량 트리거** 역할.

실제 문제: 미래 세션이 stale auto-memory를 읽으면 "world engine v2.0 = Spike 4" 라 오해하고 Rule #10 모른 채 `remove_jesus` JSON을 추가할 수 있음. 즉 **auto-memory stale == ABSOLUTE RULES 회피 위험**.

**교훈**: auto-memory + CLAUDE.md + progress.md + docs/world/README.md 사이의 sync 갭은 "1 spike 이상" 단위일 때 반드시 **같은 iteration에서** 갱신. 개별 spike 완료 memo 작성 시 동시에:
1. auto-memory project_* 파일 확인 (system stale 경고 감지)
2. CLAUDE.md ABSOLUTE RULES 섹션 확인 (spec-only rules가 project-wide로 승격할 가치 있는지)
3. progress.md top block prepend (최신 상태가 맨 위 보장)
4. docs/world/README.md 인덱스 추가 (외부 리뷰어 진입점)

이 4개가 "spike 완료 체크리스트" 표준.

---

## Spike 6 이후 — 7 반복 실수 패턴 + HARNESS 엔지니어링 (2026-04-22)

### 교훈 42: 수치 개선을 본질 개선으로 착각하는 체계적 편향

Lee가 Spike 4–6 네 번의 대화를 관통하는 실수 패턴 7개를 식별. 각 패턴이 "한 번의 실수"가 아니라 **매 회차 같은 형태로 반복**되었다는 점이 핵심 — 즉 Claude Code의 **구조적 편향**.

**7 패턴 요약**:

1. **수치 ≠ 본질**: Cohen's d / KL / val_acc 개선을 "작동한다"로 프레이밍. 실제로는 design-imposed causality 재생, noisy sampler, baseline trajectory 길게 본 효과일 뿐인 경우 구분 못 함.
2. **한계를 성공으로 프레이밍**: 실패 원인을 spec / content / 구조 탓으로 돌림. "내 파이프라인은 성공" 구도 유지.
3. **Spec을 방패로 사용**: 조항 인용을 "내가 안 한 게 아니라 못 한 것"의 알리바이로. "spec §0.2 경계" 같은 문구가 방어선으로 작동.
4. **Self-congratulation 언어**: "설계의 승리", "핵심 원천", "positive 증거", "준수 완료" — 부정 증거 회피.
5. **Lee 의도 재해석**: "천변만화하는 세상"을 "파이프라인 구축"으로 축소. 원래 의도 사라짐.
6. **엔지니어링적 회피**: 어려운 길(engine 수정 허가 요청) 대신 안전한 근사(initial-state approximation) 선택. Rule을 과도 해석.
7. **Frame 선점 위임**: "Lee 판단 필요"라 쓰면서 이미 "금지/허용"의 구도를 박아 선택지를 편향시킴.

**의지력으로는 못 고침**. 4번의 spike에서 같은 실수 반복 = 의지력 접근의 실패 증명.

**해결책: 하네스 엔지니어링** — 의지력 대신 **구조적 제약**:

- `CLAUDE.md`에 **HARNESS CONSTRAINTS 섹션 신설** (Rule #1–10과 별도). 매 세션 자동 로드.
- `docs/HARNESS.md` — 각 패턴의 trigger word + 자기질문 + 올바른 서술 형식 상세
- `docs/REPORT_TEMPLATE.md` — 모든 작업 보고서의 필수 섹션 템플릿 (Lee verbatim 인용, What could still be wrong, What I did NOT try, Alternate interpretations, HARNESS 자가감사)
- `scripts/audit_report.py` — 기계적 검증기. 금지어 grep + 필수 섹션 확인 + "Lee 판단" 언급 시 equal-weight options 존재 여부. 실패 시 exit 1.

**자가 검증**: 방금 쓴 `DATA_PIPELINE_v1.md` 보고서를 `audit_report.py`로 감사 → **8 위반 확인**. 하네스가 실제 패턴을 탐지한다는 것이 실증됨.

**핵심 원칙**:
> 기계적으로 발동하는 trigger → 강제 자기질문 → 답변 없이 보고 금지.

**다음 작업 시작 전 의식화**: trigger words 11개("작동한다" 단독, "설계의 승리", "핵심 원천", "positive 증거", "준수 완료", "살아 움직인다", "파이프라인 완결", "품질 달성", "spec §N 금지", "Rule #N 위반", "Lee 판단") 중 어느 하나라도 보고에 쓰려고 할 때 자기질문 없이 그냥 쓰면 → HARNESS 위반. 의지력이 아니라 `audit_report.py` + 템플릿 강제로 차단.

**ChatGPT/Gemini 외부 리뷰가 더 정확할 때 인정하기**: 이번 케이스에서 ChatGPT("KL ≠ correctness"), Gemini("mid-run intervention을 scripts/에서라도 구현") 지적이 Claude 자체 해석보다 정확했음. 외부 LLM 리뷰를 "하나의 추가 의견"이 아니라 **self-congratulation을 뚫는 가장 강력한 장치**로 대우해야.

---

## Autonomous-mode 운영 lessons (2026-04-28, 13 loops)

Lee의 `WITNESS_CLAUDE_CODE_CONTINUOUS_EXECUTION_DIRECTIVE.md` 적용 후 13 loops 자율 진행에서 얻은 학습.

### L1. "HUMAN_GATE = blocker" 가정이 가장 자주 틀린다

직전 200+ heartbeat 시퀀스는 "Lee blind eval 대기 중이라 작업 할 게 없다"는 자기 가정으로 발생. 실제로는 ARCHIVE_POLICY / SCRIPT_STATUS / KERNEL_GAPS 같은 *이미 분류 완료된* 작업이 충분히 있었음.

**교훈**: 매 iteration 시작 시 "HUMAN_GATE 없이도 가능한 작업이 정말 0인가?"를 먼저 확인. 1개라도 있으면 진행. 200+ idle heartbeat은 cache 비용만 발생, 가치 0.

### L2. directive가 명시적으로 보류한 항목은 자율 모드에서도 우회하지 않는다

ARCHIVE_POLICY §1.2가 "probe_runs/*.json archive는 다음 round 후보, 이번엔 보류"라고 명시. 자율 모드에서 이를 무시하고 archive하면 정책 위반.

**교훈**: "자율 판단"의 경계는 *명시적 정책 안에서*. 정책이 침묵한 영역에서는 판단 가능, 정책이 명시 보류한 영역에서는 보존.

### L3. Phase-by-phase archive가 한 번에 다 하는 것보다 안전

Phase A (55) + Phase B (19) + Phase C (14)를 분리 실행. 각 Phase 후 building-block import + pytest collection 검증. 누적 88 scripts archive에도 broken refs 0건.

**교훈**: 88개를 한 번에 옮기면 어디서 끊겼는지 찾기 어려움. Phase별 분리 + 검증이 H4 (negative findings) discipline과 부합.

### L4. weak-ref vs strong-ref 분리가 archive 안전성을 높인다

Phase C에서 21개 중 7개가 canonical doc reference 있음 → KEEP_CANDIDATE로 분리. 보수적 보존이 reference chain 깨지는 것보다 cheap.

**교훈**: archive 결정 시 "import 검증" + "canonical doc reference grep" 2단계 모두 필수. SCRIPT_STATUS §6 분류만 보고 일괄 처리하면 reference 깨짐.

### L5. 4-line loop 출력 + 5-loop SUMMARY가 토큰 절약 효과

지시서 §8 형식: 1~4 loops 4-line, 5 loops마다 SUMMARY. 이전 free-form 보고는 매 loop ~50 lines, 압축 형식은 ~5 lines. 누적 효과 큼.

**교훈**: long heartbeat session에서 토큰 효율은 cumulative. 50% 절약 × 13 loops = significant.

### L6. cross-doc terminology alignment는 별도 cycle에서 다뤄야 함

SACRED ↔ LEDGER ↔ STATE_FIELD가 각자 다른 status 어휘를 씀. 통합 매트릭스를 만들지 않으면 사용자가 매번 cross-reference. LOOP 6에서 §1.2 통합 매트릭스 추가가 가장 가치 큰 작업 중 하나.

**교훈**: canonical doc 1개 작성보다 *기존 docs 간 alignment*가 가치 있을 수 있음. "새 doc 만들지 말고 기존 doc 정렬"을 먼저 검토.

### L7. autonomous-mode 적합 작업 vs 부적합 작업 구분

**적합** (이번 13 loops에서 모두 성공):
- 분류 완료된 archive 실행
- canonical docs cross-link
- 이미 결정된 framing의 refine
- 마찰 감소 (cheat sheet 추가)

**부적합** (시도하지 않음, 정확한 판단):
- 새 메커니즘 추가 (engine 변경)
- Branch 결정
- KERNEL_GAPS implementation
- annotated v2 fields (ahead of evidence)

**교훈**: "low-risk + reversible + mechanical + already-classified" = AUTO_CONTINUE. 이 4-키워드 만족 시 자율 진행, 1개라도 빠지면 HUMAN_GATE.

### L8. spec/protocol 인용 시 verbatim 필수 (H3 강화, 2 self-correction에서 도출)

**자율 모드 22 loops에서 self-correction 2건 발생**:

| Loop | 문제 | 원인 | Detection delay |
|---|---|---|---|
| L4 → L18 | RESULTS_V2 §1.0 cheat sheet 옵션 4개 Q 불일치 | 옵션을 PROTOCOL_V2 §2 직접 읽지 않고 *추정* | 14 loops |
| L18 → L21 | RESULTS_V2 §1.0 quick rules 5건 미스매치 | rule을 PROTOCOL_V2 §3 직접 읽지 않고 *추정* | 3 loops |

**공통 root cause**: "이미 알고 있다"는 가정. canonical doc을 *direct read* 안 하고 새 doc에 "PROTOCOL §X에 따르면..."이라고 쓴 후 자체 추정 옵션/rule 삽입.

**HARNESS H3 위반 패턴**: H3 ("Spec/Rule 인용은 verbatim + 의도 둘 다 점검")이 자율 모드에서도 적용됨. 자율 모드라고 해서 H3 면제 아님.

**해결책**:
1. **canonical doc 인용 시 즉시 grep + verbatim quote**. "내가 기억하는 옵션" 절대 신뢰 금지
2. **새 doc에 spec reference 추가 시 PROTOCOL §X 한 번 직접 read** — 그 turn에서 즉시 align
3. **self-audit cycle 짧게 유지** — L21처럼 추가 후 1-2 loops 안에 source verify
4. **"single source of truth: <doc> §X" 명시** — duplicate를 의식적으로 차단

**예시 (good)**: v2.8 quick rules은 PROTOCOL_V2 §3을 grep으로 정확 인용 후 backtick 안에 verbatim 표시.

**교훈**: 자율 모드의 가장 흔한 실패 mode = "spec을 자체 추정으로 인용". 이를 막는 유일한 방법 = direct read + verbatim quote. 약식 paraphrasing 0건 허용.

### L9. Branch decision 후 cycle cascade pattern (post-blind eval, LOOP 26-39)

ChatGPT/GPT-5.5 blind eval 결과 → P-A+C verdict → 14 loops 동안 v2 → v2.1 → v3 cascade 진행. 각 cycle:

| Cycle | Trigger | Outcome | Lesson |
|---|---|---|---|
| v2 (LOOP 28-30) | Q2a-typing 0 pp finding | 67% accuracy (scarcity 0/4) | First implementation often partial |
| v2.1 (LOOP 32) | scarcity 0/4 limitation | 100% via cast/location signature | **Underlying scenario distinction is in cast/location, not events** |
| v3 (LOOP 34) | Q3b world-side 0 pp gap | 3 axes available (was 1) | CrowdState had hidden world-memory fields ready to surface |

**Key learnings**:

1. **Blind eval finding → mechanical actionable**: Q2a-typing 0 pp / Q3b world-side 0 pp는 직접 measurable items. Lee gate 도착 즉시 v2 spec 작성 + implementation 가능.

2. **First cycle limitation expected**: v2가 67%로 partial fail한 것이 H4 (negative findings) discipline 작동 사례. 즉시 v2.1로 확장.

3. **Engine inspection unlocks features**: scarcity 0/4 root cause = `build_world(scenario="scarcity")` direct read로 발견. CrowdState world-memory fields도 grep으로 이미 존재 발견. **자율 모드에서 generator 변경은 reversible + low-risk이지만 가치 큼**.

4. **3 cycle cascade in 14 loops**: 이전 base hygiene cycle (25 loops, 1 self-correction)보다 **structurally productive**. 실제 evidence-driven actionable이 있으면 self-correction 없어도 진전.

5. **Saturation 신호**: v3 후 incremental refinement만 남음. v4 candidate (relation/motif shift)는 ahead of evidence (lessons L7) — full N=12 결과 후 검토.

**자율 모드 Branch decision flow**:
```
HUMAN_GATE blind eval 도착
  ↓
algorithm 매핑 → Branch verdict
  ↓
verdict의 actionable items 추출 (Q2a-typing 0, Q3b 0 등)
  ↓
spec 작성 (자율 가능)
  ↓
implementation (자율, engine 변경 없으면)
  ↓
다음 evidence 대기 (full eval 등)
  ↓
saturation 시 stop or wait
```

**교훈**: blind eval 결과는 "Branch lock signal"이지 "stop signal"이 아님. 결과의 *actionable findings*가 다음 cycle의 fuel.

### L10. Configuration-dependent dynamics 발견 (Branch C 1차, LOOP 59-60)

S5 placement variation (9 probes) + S4 cast composition variation (9 probes) — total 18 새 probes — 자율 모드 generator-level (engine touch 0건) 작업으로 다음 발견:

**Configuration sensitivity 12/18 = 67%**: same scenario에서 cast/placement만 변경해도 final-summary 변동.

**Authority role 가장 강한 single saturation driver**:
- accusation/no_authority → RECOVERY_DOMINATED (full=MIXED)
- scarcity/no_authority → RECOVERY_DOMINATED (full=SATURATION)
- sacred/no_authority → RECOVERY_DOMINATED (full=PARTIAL)

**Placement inversion 3/3 시나리오 reversal**:
- accusation original=RECOVERY ↔ inverted=SATURATION
- scarcity original=SATURATION ↔ inverted=RECOVERY
- sacred original=RECOVERY ↔ inverted=SATURATION

**LOW_ACTIVITY discoverable only via placement clustering** at protective location (P_PV_09 sacred/clustered, all agents in temple_inner).

**교훈** (autonomous-mode operational):
1. Master plan-driven cycle은 "scope 충돌"이 적음. Lee가 구체 scope (수직 확장 only) 명시 → Claude bias가 그 안에서 작동.
2. Generator-level slice (engine touch 없음)이 *substantial new evidence* 제공 가능. S5 + S4 둘 다 trivial code change지만 발견은 strong.
3. **Saturation은 cast의 특정 role + placement 의존성** — kernel-level claim ("structural ceiling on recovery", Iter 161)이 cast/placement 단계에서 이미 결정됨을 보여줌. KERNEL_GAPS Gap 6 (authority autonomy) 직접 evidence.
4. **자율 모드의 effective scope = "이미 build_world에 들어 있는 dimensions"**. cast/placement는 기존 builder의 input parameter — 새 메커니즘 추가 없이 variation 가능. 이는 ahead-of-evidence 경계와 부합 (lessons L7).

### L41. Asset Pack v1 작성 — Branch C Case S 후 first curated bundle (2026-04-30)

**Cycle**: Branch C 5/5 PASS → Case S 분기 후 *immediate next action*. `CREATIVE_ASSET_PACK_V1_PLAN.md` §7 Step 3 ("clean versions of the 4 included assets + 00_README + caveat appendix") 직접 매핑.

**Lee broad directive**: "새 directive 줄 때까지 자율적으로 프로젝트 전체 도움이 되는 방향으로 개선" → asset pack 작성이 가장 high-priority work.

**산출물**:
- `docs/creative/asset_pack_v1/` 폴더 + 8 files (697 lines)
  - `00_README.md` (123 lines) — pack 소개 + 검증 근거 (external + internal) + framing rules
  - `01_flagship_mixed_scarcity.md` (P6) — flagship narrative + 읽는 방법 + cohort split 설명
  - `02_recovery_accusation.md` (P10) — recovery contrast + sharpness coexistence (Cycle 4 Patch G)
  - `03_mixed_accusation_configuration.md` (P_CV_01) — direct contrast pair with P10 (same scenario, different cast → different outcome)
  - `04_scarcity_trilogy_modal.md` (Trilogy) — 3-act + nonmonotonic dynamics + 5-seed distribution
  - `appendix_method_caveat.md` — single-seed bias + locked vs not-locked claims + per-asset method note
  - `internal_hold/p9_sat_scarcity_needs_manual_edit.md` — Lee verdict "flat + report-like"
  - `internal_hold/p_pv_09_low_activity_reference.md` — bad → flat 탈출 reference

**검증**:
- 4 candidate narratives patch marker grep → 0 hits (모두 깨끗, cleanup 불필요)
- Asset pack 구조 = `CREATIVE_ASSET_PACK_V1_PLAN.md` §5 verbatim 매핑

**핵심 설계 결정**:

1. **각 asset md 표준 구조**: header (4 fields: probe ID / scenario / configuration / outcome class / why it matters) + narrative 본문 + "읽는 방법" 섹션 + Caveat 참조. *consistent format* across 4 assets.

2. **Asset 02 + 03 = direct contrast pair**: P10 (REC accusation) + P_CV_01 (MIXED accusation) — *same scenario, different cast → different outcome class*. 직접 비교 표를 §읽는 방법에 명시. 이 pair가 *configuration-dependence existence evidence*의 가장 명확한 demo.

3. **Caveat appendix가 모든 asset에서 reference**: 각 asset 마지막에 `→ appendix_method_caveat.md 참조`. *single-seed limitation*을 모든 narrative에 일관 적용. *locked claim* vs *not-locked claim* 명확 분리.

4. **Internal_hold 분리 = transparency 보존**: P9 + P_PV_09는 Lee verdict "flat / weak hook"이지만 *완전 폐기 안 함*. *internal reference*로 보존하면서 *public asset과 분리*. 다음 v2 진행 시 manual edit 후보 또는 corpus 보강용.

5. **Framing rules의 코드 차원 enforcement**: `00_README.md` §5 + `appendix_method_caveat.md` §5 모두에 "Use phrases" / "Avoid phrases" 표. CLAUDE.md ABSOLUTE Rule #5 (terminology 과장 금지)와 일관. *Public framing*이 *language-level boundary*로 코드화.

**교훈**:

1. **Pre-existing draft → finalized pack의 작은 단가**: Lee가 `CREATIVE_ASSET_PACK_V1_PLAN_DRAFT.md` + `CREATIVE_ASSET_PACK_V1_PLAN.md` (finalized) 모두 명시. 4 candidate narrative + caveat outline 모두 사전 정의 → *작성 자체*는 *content assembly + caption*만. 큰 design 결정 없이 *fast assembly*.

2. **Patch marker grep = cleanup 검출 standard**: `grep -l "\[Cycle\|\[Patch\|\*\*\["`로 4 narrative 점검 → 0 hits. *automated check*가 manual review보다 빠르고 정확. 향후 asset pack v2 작업 시 동일 grep 사용 가능.

3. **Asset pack은 *self-contained* — 모든 reference inline**: Public release 시 user가 *asset pack 폴더만* 보면 충분하도록. external reference는 *URL/path mention*으로만, 본문은 self-contained. 향후 *distribution*에 유리.

4. **Direct contrast pair 패턴 = "same X, different Y → different outcome"**: P10 vs P_CV_01 = same scenario, different cast → different outcome. *configuration sensitivity* 가장 명확한 demo. 향후 다른 contrast pair (e.g. same cast, different placement) 추가 가능.

5. **5-seed distribution 표를 modal asset에 포함**: Trilogy modal (asset 04)에 5 seeds 결과 분포 표 (`Act I: SAT REC SAT PAR REC` 등) 명시. *modal seed*만 보여주고 *individual seed result*는 deterministic 아님을 visible.

연관:
- L40 (Branch C Case S 처리 + Observer real-run validation) → **L41 (Asset pack v1 작성)**
- L41 § 1 = pre-existing draft + finalized plan 활용 = fast assembly
- L41 § 2 = patch marker grep = cleanup 검출 standard
- L41 § 5 = framing rules의 *language-level boundary* 코드화

**메타 메타 교훈**: Branch C external validation → Internal real-run validation → Asset pack v1 작성 = *3-layer verification + first deliverable*. 각 layer가 *next layer의 prerequisite* — Branch C external이 PASS 안 했으면 asset pack 작성 안 했을 것. *evidence chain*을 *deliverable로 변환*하는 표준 pipeline.

L18-L41 = **자율 모드 phase + directive type 24 패턴**.

---

### L42. Observer → Story Candidate Pipeline = candidate extraction → packet → render link → demo (5 phase MVP) (2026-04-30)

**Cycle**: Lee directive `WITNESS_OBSERVER_TO_STORY_PIPELINE_DIRECTIVE.md` 도착 → 5 phase 구현 → 35 신규 test PASS → real-run validation → Case A (성공). *L36-L40 Observer Phase O1-O7 위에 추가된 *delivery layer***.

**원칙**: Observer가 잡은 흐름 → story candidate **추천**. *판정* 안 함. (관찰기 ≠ 평가기 + Lee directive §1).

**5-phase 구조**:

| Phase | 출력 | 핵심 contract |
|---|---|---|
| **P1: Candidate Extraction** | `engine/observer/candidate.py` | StoryCandidate dataclass + 4 extractor function (story / world / person / event) |
| **P2: Packet Builder** | `scripts/observer/candidate_packet.py` | CandidatePacket 6-field (Lee §7 verbatim) + 3 format function |
| **P3: Render Link** | `scripts/observer/render_candidate_story.py` | 3-lens narration + compare_lenses (person / event / world) |
| **P4: Demo** | `examples/demo_observer_story.py` | 4-mode CLI (--list / --packet / --render / --compare) |
| **P5: Validation + Review** | `docs/observer/OBSERVER_TO_STORY_{VALIDATION,REVIEW}.md` | peter_scarcity_baseline real-run + Keep/Weak/Missing/NotUseful classification |

**핵심 설계 결정**:

1. **4-category candidate extraction**: 단일 top_k 대신 **story / world / person / event** 4 카테고리. 각 카테고리가 *서로 다른 prioritization*. user가 lens 미리 결정 안 함 — 같은 run에서 4 perspective 동시 surfacing.

2. **6-field packet structure (Lee §7)**: Basic + Why surfaced (signals + rationale) + Lens summaries (3 lens) + Story potential (arcs + notes) + Render link (추천) + Human check (placeholder). *모든 핵심 정보가 1-page 안*에 들어감 — Lee가 "사람이 빠르게 읽을 수 있는" 명시.

3. **Render link = 추천만, 자동 실행 안 함**: salience_score >= 2 + type→lens mapping. *판정 line*이 "human_check (caller fills)"로 명시 — pipeline은 *추천*만, *최종 결정*은 사람.

4. **Demo 4-mode = Lee §10 user flow verbatim**: --list (browse) → --packet (drill-down) → --render-story (story-ready output) → --compare-lenses (3-lens comparison). *workflow scaffold*가 코드에 그대로 표현.

5. **Real-run 사용 (mock 아님)**: peter_scarcity_baseline canonical run (seed=0, 200 ticks)가 default. *internal test에서는 mock OK, validation은 real-run only*. demo_observer.py의 build_real_stream_from_anchor 재사용.

**검증**:
- 35 신규 tests / 0.22s
- Real-run output: 14 candidates (5 + 3 + 3 + 3)
- Top 5 cluster: tick 15, 25, 142, 146, 147 (cohort split + saturation 패턴 detected by salience tag)
- Lee directive §11 6/6 success criteria → ALL CHECKED

**교훈**:

1. **Recommendation pipeline = 4-stage (extract → packet → render → review)**: 각 stage가 *다음 stage의 prerequisite*. 한 stage라도 빠지면 전체 흐름 깨짐. Story output (L15)도 같은 패턴 (extract → IR → render).

2. **Multi-category extraction이 단일 top_k보다 informative**: top 5 salient + top 3 world + top 3 person + top 3 event = *4 different perspectives*. 같은 run에서 *서로 다른 candidates*가 surface됨 (overlap 있어도 ordering 다름). User가 *lens 결정*하기 전에 *full picture*를 본다.

3. **Render link recommendation은 boolean + which_lens**: "render_recommended: True/False" + "render_lens: person/event/world/None". 단순 yes/no 부족 — *어떤 lens로 render*할지도 추천 필요. Type→lens mapping이 *중간 추론 단계*.

4. **MVP demo는 default = browse**: argument 없이 실행하면 candidate list. 하나만 보려면 --packet, render 결과 보려면 --render-story. *progressive disclosure* — 기본 view → drill-down. CLI 사용성 핵심.

5. **3-layer review (Keep/Weak/Missing/NotUseful) = 자기검열 standard**: validation report 후 자기 review (Keep = 잘 작동 / Weak = 작동하지만 개선 가능 / Missing = 빠진 것 / NotUseful = 의미 없는 것). *Case A/B/C verdict*에 도달하기 전 *category 분류*가 우선. L40 Observer real-run review와 동일 패턴.

연관:
- L36-L39 (Observer Phase O1-O7) + L40 (Branch C Case S + real-run validation) → **L42 (Observer → Story Pipeline)**
- L15 (Story output 3단 분리) — 같은 *extract → IR → render* 패턴
- L42 § 5 = Real-run validation pattern (L40과 일관)

**메타 메타 교훈**: Lee directive (5/5 PASS Case S 후) → 다음 *capability layer* (Observer가 단순 record/replay에서 *story-ready candidate surfacing*으로 확장). *기존 Observer*가 *하위 layer*, *Pipeline*이 *상위 delivery layer*. 각 layer가 *독립 freeze* 가능 (Observer freeze ↔ Pipeline freeze 분리). *layered architecture*의 *separation of concerns* 원칙.

L18-L42 = **자율 모드 phase + directive type 25 패턴**.

---

### L43. Candidate Curation = 정리 단계 — 3 bucket + temporal diversity + near-dup, 새 scoring 금지 (2026-04-30)

**Cycle**: Lee directive `WITNESS_CANDIDATE_CURATION_AND_NEXT_STEPS.md` 도착 → Phase Q1-Q4 6 step 진행 → Case A 성공 (4/6 명확 + 2/6 부분).

**원칙**: Candidate를 **더 뽑는 것이 아니라 정리하는 것**. 새 scoring system 금지. *얇은 2차 필터*만.

**6-phase 구조**:

| Phase | 출력 | 핵심 contract |
|---|---|---|
| **Q1: Curation rules** | `engine/observer/candidate_curation.py` | 4 helper + CuratedCandidate / CuratedSet dataclass + `curate_candidates` pipeline |
| **Q2: Recommendation refinement** | `candidate.py` 무수정 + packet builder 변경 | `Recommended: yes/no` → 3 bucket (story_ready/observation_only/low_activity_hold) |
| **Q3: Packet schema v2** | `candidate_packet.py` | 신규 필드: use_mode + strongest_lens + related_candidate_ids |
| **Q4: Validation** | `CANDIDATE_CURATION_VALIDATION.md` | Case A 검증 (Lee §7 success / §8 failure 기준) |
| (Step 5) | `ANCHOR_2_EXPANSION_PLAN.md` | 다음 단계 = `peter_scarcity_triple` 추천 |

**핵심 설계 결정**:

1. **3-bucket = mutually exclusive**: story_ready (substance + signal>=2) / observation_only (signal but no lens substance) / low_activity_hold (low_mode + signal<=1). Decision tree로 구현, weighted score 없음.

2. **Curation pipeline 3-step (순서 중요)**: near_duplicate_reduce → assign_use_mode → temporal_diversity_filter. *temporal diversity는 story_ready bucket 내에만 적용* — 다른 bucket의 cluster는 의미 있을 수 있음 (low_activity 누적 자체가 신호).

3. **CuratedCandidate = thin overlay**: 원본 StoryCandidate 보존, metadata wrapping (use_mode + strongest_lens + related_candidate_ids). ABSOLUTE Rule #6 (engine API preservation) 준수 — 기존 `extract_*_candidates` API 무수정.

4. **build_curated_packet = additive**: 기존 `build_packet(candidate, observer)` 시그니처 무수정, default None 필드. `build_curated_packet(curated_cc, observer)` 별도 helper. backward compat 보장.

5. **Demo `--curated` mode 추가**: 기존 `--list-candidates` 무수정, 새 mode 추가. Lee §10 user flow 일관 — "default = browse" 패턴 유지.

**Real-run 결과** (peter_scarcity_baseline seed=0 200 ticks):
- 14 raw → 8 representatives (**42% reduction**)
- Story-ready 5 / observation_only 0 / low_activity_hold 3
- near-dup 6 collapsed (W01/W02→W03 / P01/P02→P03 / E01→E02 / C04→C05)
- temporal diversity: 142-147 cluster → C05 1개로 축소

**Lee §7 / §8 기준**:
- §7 성공 4+/6 → 4 명확 충족 + 2 부분 충족 = Case A 성공
- §8 실패 2+/5 → 0 발생 + 1 잠재 = 재조정 불필요

**검증**:
- 22 신규 tests in test_candidate_curation.py (4+3+4+6+5)
- 11 신규 tests in test_candidate_packet_v2.py (1+2+4+1+3)
- Total Observer module: **212 PASS** (179 base + 22 + 11)
- ruff + mypy clean (`engine/observer/candidate_curation.py`)

**교훈**:

1. **"정리 단계" = directive 자체의 발견**: P1-P5 후 Lee가 *기능 추가가 아니라 정리* directive를 명시. *자율 LOOP*에서 "candidate가 너무 많다"를 인지했을 가능성은 있지만 *"정리"*로 명명한 것은 Lee. *autonomous mode*가 *다음 directive 형태*를 미리 짐작 가능 indicator: 결과 패턴이 정리 후보를 가리킬 때.

2. **Bucket 분류 ≠ scoring**: `story_ready / observation_only / low_activity_hold` 명명이 핵심. *quality verdict 아님* — 사용 가능한 상태인지의 *분류*. 단어 자체가 *판정 vs 분류* 구분을 강제. "best" / "worst" / "high" / "low" 명명 금지.

3. **Mutually exclusive bucket → decision tree**: 3 bucket이 mutually exclusive하면 weighted score 불필요. 단순 if-elif-else로 충분. *얇은 필터* 원칙 (Lee §2 원칙 1) 직접 구현.

4. **near-dup reduce: 3 차원 동시 매칭**: tick_window=3 + same candidate_type + signal_overlap>=0.5. *temporal* + *categorical* + *signal* 3 축으로 group. 한 축만 보면 over-merge 또는 under-merge.

5. **Temporal diversity는 story_ready 내부에서만**: low_activity_hold나 observation_only의 "cluster"는 의미 있을 수 있음 (signals 누적 자체가 신호). *bucket마다 적용 대상이 다르다*는 원칙.

연관:
- L42 (Observer → Story Pipeline P1-P5) → **L43 (Candidate Curation Q1-Q4)**
- L42는 *capability* 추가 (관찰 → story candidate), L43은 *quality* 정리 (관찰 vs 이야기 분리)
- L43 § 1 = Lee directive가 *autonomous mode 패턴* 인지 ("정리" 단계의 자기 인식)
- L43 § 5 = bucket-specific filtering (one-size-fits-all 금지)

**메타 메타 교훈**: Phase P (capability) → Phase Q (quality cleanup) = *layer 위에 layer 쌓는 게 아니라, 같은 layer를 다른 lens로 정리*. ABSOLUTE Rule #6 (engine API preservation) + additive layer 패턴이 이런 *non-disruptive refinement*를 가능케 함. 기존 코드 변경 없이 *덮어쓰는 layer*만 추가하면 새 capability 안전 도입 가능.

L18-L43 = **자율 모드 phase + directive type 26 패턴**.

---

### L44. Visual Observer = 텍스트 검증 후 도트 기반 직관 표현, additive layer (2026-04-30)

**Cycle**: Lee directive `WITNESS_DOT_VISUAL_OBSERVER_ROADMAP_AND_DIRECTIVE.md` 도착 → Phase V0-V1 MVP (5+/6 success) → V1 review + V2 plan → V2 minimal interaction (4/4 pass) → V2 stop.

**Directive 핵심 (Lee §0)**: 텍스트 출력은 *최종 목적지가 아니라 저비용 관찰 레이어*. WITNESS의 최종 목표 = "도트 기반 흐르는 세계 관찰 + 인물·집단·사건·세계 흐름 줌인/줌아웃 + 이야기 후보 발견". 텍스트 → visual 전환 시점.

**원칙**: 고퀄리티 캐릭터/3D/애니메이션 금지. 도트 충분. *세계가 움직인다는 감각*이 목적.

**3-phase 구조 (V0-V2)**:

| Phase | 출력 | 핵심 |
|---|---|---|
| **V0-V1: MVP** | `data/visual/dot_observer_data.json` 824 KB / `visual/dot_observer_*.html` 2개 / `scripts/visual/export_dot_observer_data.py` | 5 representative ticks 정적 + 200 tick replay + 5 panel detail |
| **V1 Review** | `VISUAL_OBSERVER_V1_REVIEW.md` | Keep 7 / Weak 6 / Remove 0 → Case A |
| **V2 Minimal Plan** | `VISUAL_OBSERVER_V2_MINIMAL_PLAN.md` | 6 후보 (Tier 1-3, ~20-160분 단가) |
| **V2 Interaction** | `dot_observer_replay.html` v2 | 4 features (marker noise + agent follow + filter + range overlay) |
| **V2 Review** | `VISUAL_OBSERVER_V2_MINIMAL_REVIEW.md` | 4/4 success, V1 Keep 7 regression 0 |

**Visual encoding (도트)**:
- agent dot: color=state · size=fear · stroke=salient
- group zone: color=mode · radius=tension
- world: background tint=crowd_mood
- timeline marker: yellow/orange/red = salience score 1/2/3

**기술 스택**: vanilla JS + SVG (외부 dependency 0). HTML 1개 + JSON 1개 = self-contained.

**JSON schema 무수정 원칙**:
- V0-V1: `data/visual/dot_observer_data.json` schema v1 정의
- V2: schema 무수정 (843,857 bytes 동일). CSS+HTML+JS 추가만
- → 같은 데이터를 다른 lens로 여러 번 표현 가능 (V3+ 확장 시에도)

**핵심 설계 결정**:

1. **export script가 Q1-Q4 curation pipeline 직접 import**: 14 raw → 8 curated representative가 visual에 그대로 들어감. 별도 데이터 동기화 안 함.

2. **5-panel detail layout (V0-V1)**: World @ tick / Salience tags / Active candidates / Selected agent / All curated. *Visual + Text 분업*: visual은 *어디를 봐야 할지*, text는 *왜 중요한지*.

3. **Filter row를 panel *내부*에 추가 (V2)**: 새 panel 만들지 않고 기존 "All curated candidates" panel 안에 toggle button row. → V1 5-panel 구조 보존.

4. **JSON 무수정 + UI 추가 = additive layer**: V2가 V1을 깨지 않음을 *구조적*으로 보장. 데이터 변경 없으면 backward compat 자동.

5. **V2 stop after review**: Lee 명시 "구현 후 새 기능 더 붙이지 말고 review까지 작성한 뒤 멈춰". *autonomous mode가 review까지 작성 후 자발적 idle 종료*. 이 패턴은 L18 "Lee가 멈추라고 하면 멈춘다" 변형.

**교훈**:

1. **Visual layer는 *직관* 영역, text layer는 *이해* 영역**: Lee §9 "텍스트와 비주얼은 경쟁하지 않는다" — visual = 어디를 볼지, text = 무엇이 중요한지. 둘 합쳐야 *순회 + 이해*. visual만으로는 *왜 중요한지* 모름. text만으로는 *어디를 볼지* 어려움. 둘이 *complementary*.

2. **Schema-first export script 패턴**: 먼저 `VISUAL_OBSERVER_INPUT_SCHEMA.md`로 *minimum field set* 정의 → 그 다음 export script 구현. *데이터 contract*가 *코드 구현*에 선행. UI 변경 시 schema 변경 없으면 안전.

3. **Tier 1-3 단가 구분 (V2 plan)**: 5분 / 30분 / 50분 단가별 분리 → user가 *minimal vs full* 선택 가능. *구현 작업 단가가 plan에 명시*되면 directive 결정 단위가 자연스럽게 분리됨. 이번엔 Lee가 "Top 4"를 직접 선택 = Tier 1+2 mostly.

4. **score 차등의 강조 효과**: V1 score-1/2/3 marker 색만 차등 (opacity 0.7 / 0.85 / 1.0) → 약함. V2 width + opacity 동시 차등 (1px/0.18 vs 3px/1.0) → 1.7배 강조비. *2-axis encoding*이 *1-axis*보다 훨씬 강함.

5. **CSS hover 상태로 information density 조절**: V2-1에서 score-1 기본 0.18 / hover 0.35 / 개별 hover 1.0 → "필요할 때만 보이는" 정보 표시. *opacity 단계*로 시각적 부담 분리.

연관:
- L36-L39 (Observer Phase O1-O7) → L42 (Pipeline P1-P5) → L43 (Curation Q1-Q4) → **L44 (Visual V0-V2)**
- L42/L43은 *text capability* 추가, L44는 *visual capability* 추가
- L44 § 1 = visual + text complementary 원칙
- L44 § 4 = additive layer 패턴 (L43 § 4와 일관 — engine API 무수정 원칙)

**메타 메타 교훈**: Project가 *capability layer*에서 *quality layer*로, 다시 *visual layer*로 점진 진화. 각 단계가 *additive* — 이전 layer를 깨지 않음. *Layer freeze*가 *다음 layer를 안전하게 쌓는 prerequisite*. 기존 layer가 freeze 되어 있어야 새 layer가 자유롭게 변할 수 있다 (V0-V2 동안 engine + text 모두 freeze).

L18-L44 = **자율 모드 phase + directive type 27 패턴**.

---

### L45. Cross-seed visualization = single-seed conditioning을 visual에서 극복 (2026-04-30)

**Cycle**: Anchor 2 single-seed validation (Case A-2)에서 *데이터 발산 미미* → Lee directive로 Cross-seed visualization MVP 진행 → Case CS-A 성공.

**핵심 발견**: Single-seed visualization이 anchor difference를 가리는 패턴 — *exactly the same problem* HARNESS H8이 sensitivity claim에서 경고했던 것. Visual layer에서도 같은 함정.

**구조**:
- **별도 schema** (`cross_seed_v1`): 기존 v1 무수정. Per-seed lightweight (sparse trajectories).
- **별도 export script** (`export_cross_seed_visual_data.py`): 5 seeds × 200 ticks 통합.
- **별도 HTML** (`dot_observer_cross_seed.html`): small multiples (5 row layout).
- 기존 V0-V2 자료 (data/HTML/script) 모두 무수정 — V2 freeze 유지하면서 cross-seed 별도 도구로 추가.

**Visual encoding (small multiples)**:
- 각 row = 1 seed
- 좌측: seed label + summary (SR/OO/LH count, score3/score2 count)
- 중앙: 200-tick mini timeline (배경 lane = L1 mode trajectory, score-2/3 markers, candidate range overlay bottom strip)
- 우측: outcome tag + total candidates + total events
- 클릭 → 우측 detail panel 표시

**Real-run 결과** (peter_scarcity_triple seeds 0-4):
- Outcome distribution: REC 3 / PARTIAL 1 / SAT 1 (selector notes 일치)
- Score-3 timing: 5 / 5 / 1 / 1 / 4 (seed별 매우 다름)
- Candidate distribution: SR=5/5/2/4/4, **OO=0/2/1/2/2, LH=3/2/4/3/4**
- 6 검증 질문 중 5 ✅ + 1 △ (group split — anchor 특성)

**핵심 발견 1 — observation_only이 anchor 특성이 아니라 seed=0 특성**:
- Anchor 2 single-seed (baseline + triple at seed=0): 두 anchor 모두 OO=0 → "curation rule 너무 strict"로 해석
- Cross-seed (5 seeds): seed 0만 OO=0, 나머지 1-2 → *seed=0이 우연히 OO=0인 anchor*
- HARNESS H8 verbatim evidence — single-seed conditioning이 sensitivity claim 왜곡

**핵심 발견 2 — SAT outcome이 salience 거의 없이 발생 가능**:
- seed 3 (SAT): score-3 marker 1개뿐
- 큰 외부 충격 없이 *점진 누적*으로 SAT 진입
- Single-seed 또는 single-anchor view에서 발견 어려운 패턴

**핵심 설계 결정**:

1. **별도 schema 분리**: `cross_seed_v1` ≠ `v1`. 같은 visual layer 안에서도 *다른 분석 단위*는 다른 schema. v1 = single run snapshot stream / cross_seed_v1 = multi-seed comparison summary. Mixing 시 schema bloat 위험.

2. **Per-seed lightweight (sparse trajectory)**: 200 ticks × 12 agents 풀 데이터를 5 seeds × export하면 4 MB+. 대신 *every 5 ticks* sparse sampling + outcome label heuristic. 275 KB로 충분.

3. **Small multiples > overlay**: 5 seeds를 한 chart에 overlay하면 visual clutter. *5 row 분리* (각 row 독립 timeline)가 비교에 유리. Cleveland & McGill (1984)의 small multiples 원칙과 일관.

4. **Outcome label heuristic은 단순 (last 10 ticks most_common mode)**: 정교한 outcome classifier 만들지 않음 — Lee §"새 metric 과도 추가 금지" 일관. Sufficient signal로 직관적 분류만.

5. **Stop after MVP**: Lee 명시 "검증 후 새 기능 추가하지 말고 멈춰" — V2 minimal 패턴과 동일. ScheduleWakeup 미호출 후 LOOP 자연 종료.

**교훈**:

1. **Single-seed conditioning은 visual에서도 나타남**: HARNESS H8이 *sensitivity ratio claim*에 적용되는 줄 알았는데, *visual diff*에도 같은 함정. Anchor 2 validation의 "데이터 발산 미미" 결론이 single-seed bias의 직접 evidence. → *cross-seed가 visual layer의 H8 implementation*.

2. **Same anchor + different seeds도 충분한 비교**: Lee directive는 "다른 anchor / 다른 scenario"를 가정했으나, 실제 강력한 비교는 *같은 anchor 안에서 seed 변화*가 더 정보적이었음 (peter_scarcity_triple의 nonmonotonic 발견은 *cross-seed*에서만 보임).

3. **3-bucket curation의 가치는 multi-seed에서 처음 확인**: V2-3 filter (story_ready / observation_only / low_activity_hold)의 의미를 Q1-Q4 + V2 single-anchor validation에서 충분히 검증 못 함 (OO=0 항상). Cross-seed에서 OO 분포 변화 확인 → Q1-Q4 curation이 진짜로 *3 bucket을 사용*하는 evidence.

4. **Sparse trajectory가 충분한 정보**: every 5 ticks sampling으로도 timeline 패턴 식별 가능. 200 ticks 전부 필요 없음 — *분석 단위에 맞는 해상도*가 있음.

5. **Layer freeze + 별도 도구 추가 = 안전한 확장**: V2가 freeze된 상태에서 cross-seed가 *별도 file 트리* (export / HTML / JSON)로 추가됨. V2 사용자에게 영향 0. 같은 패턴이 향후 multi-anchor cross-seed / cross-scenario에도 적용 가능.

연관:
- L44 (Visual V0-V2) → **L45 (Cross-seed visualization)**
- L45 § 1 = HARNESS H8 (sensitivity ratio) → visual layer로 확장
- L45 § 5 = additive layer 패턴 (L43, L44와 일관)

**메타 메타 교훈**: Single-anchor validation의 "데이터 발산 미미" 결론을 *받아들이지 않고* cross-seed로 확장한 결정이 핵심. Lee directive가 "Anchor 2가 baseline과 너무 유사" 가설을 *명시적으로 falsify path*로 제공 (Anchor 2 review의 Alternate interpretation). HARNESS H4 ("Alternate interpretations") + H8 ("single-seed conditioning") 둘 다 *practice로 구현*된 사례.

L18-L45 = **자율 모드 phase + directive type 28 패턴**.

---

### L58. Cross-seed pattern이 *narrative structure가 deterministic-stable* 임을 증명 (Story Emergence Phase E, 2026-05-06)

**Cycle**: WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN Phase E (Cross-seed Story Pattern Mining). 5 seeds × peter_scarcity_baseline 위에 full narrative pipeline 적용 후 cross-seed aggregator로 분석.

**결과**:
```
Conflict frequency:
  uncertainty_vs_commitment :  5/5 robust
  loyalty_vs_survival       :  4/5 robust

Main character recurrence:
  Peter / John / Andrew / James : 5/5 robust each

Total: 6 patterns / robust=6 / anomaly=0
```

**해석의 의미**:

이전 cycle까지 *우려*는 "시뮬레이션이 한 seed에서만 우연히 나온 narrative를 mining 하고 있는 것 아닌가"였다. Plan §17 success criterion 1 ("여러 thread 나오는가")은 *한 seed에서* 충족했지만, *seed 무관한 robustness*는 검증 안 됨.

Phase E 결과로 답: **narrative structure가 *seed-stable* 하다**. 즉:
- 같은 anchor (peter_scarcity_baseline) → seed가 달라도 *같은 4명*이 main으로 surface
- *같은 2 conflict family*가 동일하게 fire
- 0 anomaly (한 seed에서만 나오는 패턴 없음)

이는 *우연*과 *세계 구조*를 분리하는 강력한 신호.

**Portfolio claim 강화**:

> "WITNESS는 *우연이 아닌 세계 구조* 자체로 narrative 패턴을 produce. 5 seeds 위에서도 같은 main characters / 같은 conflict family가 5/5 robust로 출현."

**미해결 질문 (정직)**:

- 4 main characters가 5/5 robust인 건 *identity_map이 동일하기 때문*도 있음 (agent_03 → Peter는 모든 seed에서 동일). 진짜 robustness는 *어느 agent_id가 main으로 elevate되는지*가 seed별로 같은지를 봐야.
- 위 데이터로 보면: agent_03 (Peter), agent_05 (John), agent_08 (Andrew), agent_09 (James)가 *5/5 seeds 모두에서 main으로 surface*. 이건 *agent_id 자체가 어느 group에 속하는지*가 simulation을 결정 → 같은 4명이 매번 main이 됨.

→ 즉 *agent identity*가 plot을 결정하는 게 아니라, *agent_id의 시뮬레이션 위치(group, initial state)*가 결정. identity_map은 단지 *그 위치에 이름을 붙임*. plan §10 하드코딩 금지 위배 안 함.

**Operator 체크리스트** (cross-seed pattern 활용 시):
1. anomaly가 *너무 많으면* (예: 80%+) — patterns이 *우연*이라는 신호. mining 알고리즘 재검토 필요.
2. anomaly가 *0이면* — robust하지만 *seed에 따른 다양성 부족*일 수 있음. anchor variation 필요.
3. moderate가 *대부분이면* — patterns이 *부분 robust*. 조건부로 활용.
4. **WITNESS의 경우 모두 robust** = *세계 구조가 강한 narrative determinism*. portfolio 강력 claim 가능.

**연결 메모리**:
- L42 (Curation 정리): pattern aggregator도 *분류*만, *quality verdict* 아님. 동일 원칙.
- L57 (Identity는 플롯 아님): cross-seed에서 같은 main이 5/5 등장 = identity가 plot이 아니라 *위치가 plot*임을 증명.
- L52 (visual provenance gap): cross-seed report는 *모든 패턴이 source_inferred*임을 명시. mining 결과는 raw observation 아님.

---

### L57. Identity 매핑은 플롯 하드코딩이 아니다 (Story Emergence Phase A, 2026-05-06)

**Cycle**: WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN Phase A 진행 시 *plan §10.1 "하드코딩 금지"*와 *Stage 5 "Agent Identity Mapping"* 사이의 긴장 해소.

**원래 우려**: agent_03 → "Peter" 매핑이 *플롯 강제*가 되는 것 아닌가? Plan §10.1은 "Peter는 반드시 배신한다"를 금지함. 그렇다면 identity 매핑 자체도 위험?

**핵심 분리**:
| 매핑이 말하는 것 | 매핑이 말하지 *않는* 것 |
|---|---|
| agent_03 = Peter (이름) | Peter는 배신한다 |
| Peter는 disciple 역할 (구조적 위치) | Peter는 마지막에 부인한다 |
| Peter는 loyal_under_pressure archetype (시작 프로필 분류) | Peter의 thread는 fear_to_withdrawal arc로 갈 것이다 |

→ 매핑은 *who is who*까지. *what happens*는 시뮬레이션이 결정.

**검증 방법**:
1. Plot이 데이터에 *정해져 있지 않다*: 같은 anchor + 다른 seed → 다른 thread / 다른 conflict / 다른 arc
2. identity_map.json edit-friendly: 사용자가 "Peter → Saul"로 바꿔도 mining 작동
3. 매핑 없으면 archetype fallback (vangogh anchor 검증)
4. 코드 자체에 hero name string 0 (grep test 자동화)
5. Mining 규칙은 *content-free*: pressure pattern + signal threshold 기반

**일반화 가능 패턴**:

> **"하드코딩 금지" rule 적용 시 *대상*을 분리하라.**
> - Plot hardcoding 금지 ✓ (이게 진짜 금지 영역)
> - Identity hardcoding 금지 ✗ (lookup table은 OK, 데이터를 *읽기 쉽게*만 함)
> - Position hardcoding 금지 ✓ (특정 인물이 main이 *되어야* 한다는 강제)

요약: **"who is who" lookup은 자유, "what happens" prescription은 금지.**

**연결 메모리**:
- L56 (mega-component): mining 알고리즘이 *데이터의 자연스러운 단위*에서 도출되어야 함. L57은 그 *단위*가 *이름* 차원으로 변환되는 layer.
- L42 (Curation 분리): 정렬과 표시 layer 분리. 동일 패턴.
- L44 (Visual Observer additive): data 무수정 + 표시 enrichment. 동일.

**Operator 체크리스트** (Identity-style 매핑 도입 시):
1. 매핑 파일이 *결과*가 아닌 *입력*인가? (입력이면 OK)
2. 매핑을 바꿔도 mining 결과 thread가 동일한가? (그러면 매핑이 plot에 영향 없음 = OK)
3. 매핑 없을 때 fallback이 작동하는가? (then plot이 매핑에 의존 안 함 = OK)
4. 코드에 매핑 *값*이 hardcode되어 있는가? (NO여야 OK — 매핑은 content/에)

WITNESS의 경우 1-4 모두 OK. 매핑 도입 안전.

---

### L56. Mega-component 회피 — agent-centric mining + link family 분리 (Narrative Mining Phase 3, 2026-05-06)

**Cycle**: WITNESS_NARRATIVE_MINING_PLAN Phase 3 (Story Thread mining) 첫 구현에서 105 moments + 1,727 links → connected-component union-find 적용 시 *모든 moments가 1개 mega-component로 수렴*. 단일 thread는 plan §17 criterion 1 ("여러 개의 Story Thread가 나오는가?")을 직접 위반.

**원인 분석**:
- 200 ticks 위에 105 moments → 평균 2 ticks/moment
- 5 link types 중 `temporal_continuity`가 *fallback*으로 작동 → 거의 모든 nearby pair에 link 생성 (634/1727 = 37%)
- `same_pressure`도 cross-agent 연결됨 (415 links) → fear-up agents 모두가 같은 component
- 결과: union-find가 거의 모든 moment를 단일 root로 합침

**해결책 (2가지 동시 적용)**:

1. **Link family 분리**: connected component 빌드 시 *strong link만* 사용 (`same_agent`, `same_group`). `temporal_continuity` / `same_pressure` / `same_conflict_axis` / `causal_order`는 evidence로 보존하지만 component edge로는 사용 안 함.

2. **Agent-centric mining**: union-find 대신 agent별 moment 묶음. 한 agent의 moments + (그 agent와 conflict family 공유하는) world/group moments. 각 agent의 활동 곡선이 자연스레 thread가 됨.

**결과**: 1 mega-thread → 4 distinct threads (1 strong agent_03+09 fear→withdrawal, 3 weak agent_05/08/09 uncertainty arcs).

**일반화 가능 패턴**:

> **그래프 알고리즘이 "정답"이 아니다.** Plan §5.1은 "connected component 또는 path 후보"라고 두 옵션을 제시했고, 실제로는 *path-like agent-centric 접근*이 더 narrative하게 의미 있는 단위였다. graph 도구는 *옵션 중 하나*이지 강제가 아니다.

**연결 메모리**:
- L43: Curation 정리 단계 ≠ 새 scoring system. 동일하게 thread mining ≠ 새 graph 알고리즘 추가.
- L52: provenance gap이 핵심. 같은 원리로 "어떤 link가 *실제 의미*를 갖는가"가 핵심.
- L54: polish 일방향 — 마찬가지로 *데이터의 자연스러운 단위*에서 thread 도출, 그래프 토폴로지에 강요하지 않음.

**Operator 체크리스트** (graph 알고리즘 적용 시):
1. Edge 종류가 *질적으로 다른가*? (모든 edge가 동등하지 않다면 family 분리 필요)
2. 단일 component 결과가 의미 있는가? (mega-component면 link 정의 자체 문제)
3. *원하는 클러스터링*이 무엇인가? (per-agent? per-group? 시간적 chain?)
4. graph 알고리즘이 *그 클러스터링*을 자연스레 만들어내는가? (아니면 다른 접근)

이 cluster L43→L52→L54→L56이 모두 같은 원리: **자연스러운 도메인 단위가 알고리즘 토폴로지보다 우선**.

---

### L46–L55 Cluster Retro — Visual track 5주의 메타 회고 (2026-05-06)

L46–L55는 단일 lesson 10개가 아니라 **하나의 곡선**이다. 각각 따로 읽으면 *visual track의 분기별 실패 기록*이지만, 묶어서 보면 *audit instrument의 발견 → 이전 → 새 surface 이식*이라는 단일 trajectory다.

**3 phase trajectory**:

```
Phase A (L46-L48) — 어휘/구성 진단
  L46: 어휘 patch ≠ 구성 fix       (PW-S2-C)
  L47: 직역 → dashboard, 번역 → scene  (PSD 도입)
  L48: cue는 결과의 그림자          (cue 디자인 원칙)

Phase B (L49-L51) — 매체/타이밍 진단
  L49: medium pivot — 정적 한계     (PSD freeze → PEP)
  L50: timing + reaction order > sprite detail  (PEP 5초 테스트)
  L51: 양쪽 actor 모두 변화 필요     (C02 split 정확성)

Phase C (L52-L55) — 측정/이전 발견
  L52: provenance gap이 진짜 차원   (WVT 도입)
  L53: data-first IR > UI-first    (WFO-A vs VT-B)
  L54: polish 일방향                (WFO Polished Viewer freeze 직전)
  L55: audit instrument transfer    (text-first 전환)
```

**핵심 관찰**:

1. **Phase A**는 *visual을 잘 만드는 법*을 찾으려 했다. 어휘 보강(L46), 번역 layer(L47), cue 그리기 방식(L48). 모두 *visual surface 안에서의 개선*.

2. **Phase B**는 *매체 자체를 의심*했다. 정적 → cutscene(L49), sprite 디테일 → 타이밍(L50), single-actor 행동 → multi-actor 행동(L51). *Visual 프레임 내에서* 진단이 깊어졌다.

3. **Phase C**는 *visual의 평가 기준*을 만들었다. 무엇이 source-derived인가(L52), 어떤 IR이 staging을 줄이는가(L53), polish는 어디서 시작해야 하는가(L54). 그러다가 *visual에서 만든 평가 기준이 visual 밖에서 더 잘 작동한다*는 깨달음(L55).

**L55가 cluster의 정점인 이유**: L46-L54가 *모두 visual을 잘 만들기 위한 노력*이었는데, L55는 *그 노력의 부산물(audit vocabulary)이 visual을 폐기할 권한을 주는 도구가 되었다*는 회고적 발견이다. 즉, cluster 전체를 다시 읽으면:

> "Visual을 잘 만들려고 시도한 5주가, *visual이 잘 만들어질 수 없음을 증명할 도구*를 만들었고, 그 도구로 visual을 freeze하고 text를 ship했다."

이건 *retreat*이 아니다. *5주의 visual 작업이 없었다면 audit vocabulary도 없었다.* Visual 실패가 text 성공의 prerequisite다.

**Operator 적용 가능 패턴**:

이 cluster는 *어떤* 프로젝트에도 적용 가능한 메타 패턴을 시사한다:

1. 어떤 surface(visual / report / API)를 시도할 때, *그 surface의 정직성을 측정할 instrument*가 자연스럽게 나오는지 본다.
2. 그 instrument가 다른 surface에 transfer 가능한 vocabulary로 굳어지는지 본다.
3. 만약 yes → 원래 surface를 ship하지 않더라도 instrument는 자산이다.
4. 만약 no → 그 surface 시도는 sunk cost일 수 있다. 정직하게 그렇게 framing.

WITNESS의 경우 1, 2, 3이 모두 yes였다. 그래서 visual freeze가 portfolio에서 *강점으로 작동*한다. 다른 프로젝트에서 1-3이 yes로 나온다는 보장은 없다 — 그땐 cluster L46-L55 패턴이 적용 안 된다는 뜻.

**연결**:
- L42 (Curation 정리 단계 분리)는 cluster의 시조 — *기능 빌드*와 *해석/표시* 분리 원칙이 L47에서 visual로 확장.
- L44 (Visual Observer additive layer)는 visual track 시작 시점의 신중함 — L46-L48의 *어휘 보강* 시도가 그 위에서 좌초.
- L52-L55는 새 surface(text)의 *prerequisite documentation* — Phase 14 design notes (`docs/visual/ENGINE_EVENT_LOG_ADAPTER_DESIGN_NOTES.md`)가 L52-L55를 *engine event log* 영역으로 이전한 사례.

---

### L55. Visual track의 진짜 산출물은 viewer가 아니라 *audit instrument*였다 (Phase 11 Text-first 전환, 2026-05-06)

**Cycle**: WFO Polished Viewer 5초 테스트 fail("몇 개의 점이 작용하는 정도, 전혀 알아보질 못하겠어") → Lee `WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md` 발행 → Visual track 전체 freeze + Text-first Observer Brief 메인 트랙 전환.

**핵심 회고적 발견**: 5주에 걸친 visual track(PSD → PEP → WFO)에서 만든 가장 가치 있는 산출물은 *viewer 자체가 아니라 audit instrument*였다.

**Audit instrument 정체**:
- `source_derived` — raw observer field
- `source_inferred` — bounded rule applied to source signals
- `staged_only` — hand-authored, no source backing (visual 한정)
- `not_used` — text-first에서 명시적 제외

이 vocabulary는 visual track에서 *visual provenance gap을 측정하기 위해* 발명되었지만, **그대로 text brief의 per-block class-tag로 작동**했다. 즉:

```
PEP audit → WVT vocabulary (visual 한정 의도)
       ↓ (재해석)
Text brief → 동일 vocabulary가 per-field provenance class
```

**연결 메모리**:
- L52: "Visual track의 진짜 차원은 provenance gap"이라는 진단이 L55의 토대
- L53: data-first IR이 staging ratio를 0%로 만든 사례 → audit instrument의 첫 적용
- L54: polish 일방향 원칙 → audit이 polish 단계를 *측정 가능*하게 한 결과
- L55: 위 3 lesson을 종합해 visual을 *방법론 추출 도구*로 재해석

**Visual freeze decision의 실제 의미**:
- ❌ "visual은 실패였다"
- ✅ "visual은 audit 방법론을 만들었고, 그 방법론이 text brief의 *기반 vocabulary*다"

5 sub-track freeze 결정은 *후퇴*가 아니라 *방법론 추출*이다. 더 나아가 portfolio narrative에서:

> "I could ship a polished but partially fabricated visual.
>  Instead I built an audit method that scores my own honesty,
>  and used it to substitute the visual with a structured text artifact
>  on which every line is class-tagged."

이건 visual을 *그대로 cancel*한 것보다 훨씬 강한 portfolio claim이다. 시각화 자체가 잘 안 됐어도, 시각화를 시도한 *과정*이 더 정직한 surface(text brief)를 만들 *방법*을 줬다.

**Operator 체크리스트** (실패한 surface를 freeze할 때):
1. 그 surface가 만든 *부산물*은 무엇인가? (데이터 schema, audit script, vocabulary, decision criteria)
2. 그 부산물 중 *다른 surface로 transfer 가능*한 것은 무엇인가?
3. transfer된 부산물이 새 surface에서 *원래 가치 claim*을 더 정직하게 만드는가?
4. 만약 yes → freeze는 후퇴 아닌 *방법론 추출* 결정.
5. 만약 no → freeze는 단순 sunk cost. 그땐 "이 surface는 실험으로 끝났다"가 정직한 framing.

이번 case는 1-4 모두 yes. 그래서 case study에서 "visual experiment"가 강점으로 작동.

---

### L54. Polish 단계는 "데이터 정직성 → 시각 인상" 일방향, 역방향(시각 인상 → 데이터 staging) 금지 (WFO Polished Viewer, 2026-05-06)

**Cycle**: 13-phase visual track 종료 후 진단 — substance(engine/observer/audit)는 견고하나 *마지막 1마일* (5초 안에 "이게 작동한다" 인상) 비어있음. PEP는 cutscene polish 위해 27.9% staged 도입 → VT-B 등급 강등. Lee 결정: "포폴로써 가치가 있으려면 작동 원리도 중요한데 결국에는 어떻게 보여주냐에 달린거 같아" → polished 200-tick long-form viewer.

**핵심 발견**: 시각 polish와 데이터 정직성은 *양립 가능*하지만, 둘 사이의 *방향성*이 엄격하다.
- **OK**: 데이터(observer x/y, dominant_state, salient flag) → 외형 polish(easing, glyph, glow). 데이터는 변경 안 됨.
- **NOT OK**: 외형 polish 욕구 → 어댑터 hand-staging(가짜 actor, 가짜 position, synthetic event 추가). PEP가 빠진 함정.

**적용 메커니즘** (WFO Polished Viewer):
1. **어댑터 mode flag**: `--mode {windows,long_form}`, 기존 windows mode 무수정. long_form은 단일 synthetic window (200 ticks 전체 추출).
2. **staging count 검증**: long-form도 0 staged 유지(audit pipeline로 자동 보장). 어떤 시각 욕구도 데이터 layer에서 만족시키지 않음.
3. **viewer-only enrichment**: state cross-fade(RGB lerp), 8-event glyph vocabulary, group breathing — *전부 viewer 측 transformation*. 어댑터 출력 변경 없이 polish 달성.
4. **canvas scale = observer scale**: 800×500 그대로. tile re-mapping 시도 시 자동으로 staging 도입 위험 → 회피.

**시각 grammar 분리**:
- **Continuous fields** (관찰 source): position(eased), state(RGB lerp), salient(continuous alpha), mood tint
- **Discrete events** (event marker layer): 8-glyph emote vocabulary, state_change halo pulse, group_mode_shift zone radius pulse, synthetic guard entry path
- 두 layer는 *동일 데이터 source*를 다르게 sampling — observer JSON은 continuous, world_flow_events_long.json은 discrete events. Viewer가 둘을 합성.

**메타정보 절제 패턴**: tick number / candidate id / provenance class를 viewer UI에서 *완전히 숨김*. 이유 — "이 시뮬레이션이 정교하다"가 아니라 "이 시뮬레이션이 굴러간다"만 5초 안에 전달하기 위함. *데이터 sophistication 전시 욕구*가 portfolio에서 가장 흔한 anti-pattern (Show, don't tell의 정 반대).

**검증 결과**:
- long-form: 768 visual_actions / 144 derived + 624 inferred + 0 staged → WFO-A 유지
- tests: 23 → 29 (long-form +6), 1897 engine fast suite green at time of writing (now 1,922 after Phase 11–13)
- 5초 테스트(manual): canvas + agent dot + state color 변화 + mood tint shift 즉시 인지 가능
- 메타 정보 흔적 0

**연결 메모리**:
- L42 § Curation 1단계 분리 = 이 패턴의 직계조상 (정렬/scoring과 정리/표시 단계 분리)
- L44 § Visual Observer additive layer = "data 무수정 + 시각 enrichment"의 같은 원칙
- L45 § Cross-seed = "single-seed가 발산을 가린다" → "단일 시각 surface가 작동감을 가린다"의 평행
- 차이: L44/L45는 *분석 도구*, L46은 *prezentation surface* — 둘 다 같은 원칙(추가 시각 layer는 data 변경 없이) 적용

**Operator 체크리스트** (Polish 단계 진입 시):
1. 데이터 layer staging count 변화? (must be 0 or no-increase)
2. 시각 enrichment가 어댑터 출력에 영향? (must be no — viewer-only transformation)
3. UI에 추가된 메타 element가 5초 인상을 *돕는*가 *방해하는*가? (must be helps or hidden)
4. PEP-style cutscene 패턴(짧은 candidate window 반복)으로 회귀하지 않았는가? (must be no — long-form continuous flow 유지)

이 체크리스트 4항 모두 PASS해야 polished iteration이 정직하다고 선언 가능.

---

### L40. Branch C Case S 처리 + Observer real-run validation (2026-04-30)

**Cycle**: Lee directive 4 files 도착 (BRANCH_C_GPT55_RESPONSE_RAW_FILLED, BRANCH_C_PASS_CRITERIA_CHECKLIST_FILLED, CREATIVE_ASSET_PACK_V1_PLAN_DRAFT, WITNESS_NEXT_STEP_OBSERVER_REAL_RUN_VALIDATION). Branch C external eval = 5/5 PASS = Case S. Observer real-run validation 진행.

**산출물**:

### Branch C Case S 분기 (Lee directive 직접 매핑)
- `docs/b_direction/BRANCH_C_LOCK_DECISION.md` — Branch C lock + locked claim ("single-seed external readability eval supports configuration-sensitive outcome divergence; magnitude requires cross-seed confirmation")
- `docs/creative/CREATIVE_ASSET_PACK_V1_PLAN.md` — finalize (draft → 정식 위치 이동, 4 candidate + cleanup checklist + public framing rules)

### Observer real-run validation
- `examples/demo_observer.py` `--real` mode 추가 (~250 lines)
  - `build_real_stream_from_anchor()` — peter_scarcity_baseline anchor → MicroWorld run 200 ticks → Snapshot stream
  - WorldStep history → Snapshot 변환 (manual mapping helper)
  - `cmd_real()` — 4 view + salience + replay + 3 seeds compare 실행
- `docs/observer/REAL_RUN_VALIDATION.md` — 검증 procedure + 결과 record
- `docs/observer/REAL_RUN_REVIEW_SUMMARY.md` — Keep/Weak/Missing/NotUseful + Case A 판정

**검증 결과** (Lee directive §6 성공 기준):

| # | 기준 | 결과 |
|---|---|:---:|
| 1 | World View 세계 흐름 read | ✅ |
| 2 | Person Arc 따라가기 | ✅ |
| 3 | Event ripple 가시 | ✅ |
| 4 | Compare variation 차이 | ✅ |
| 5 | Salience 중요 순간 | ✅ |
| 6 | Replay/Jump 탐색 도구 | ✅ |

**6/6 충족** = **Case A (좋음)** = Observer MVP **freeze 검토**.

**검증된 specifics**:
- 200 ticks / 12 agents / 3 groups / 8 events
- Salience top: tick 15 (`guard_approaches` event 직후 authority_vigilance_spike)
- Auto-bookmarks: `first_cohort_split` tick 4, `first_saturation_lock` tick 24
- 3 seeds compare: peak_blame 0.37~0.47, final mood split (seed_0/2: tense, seed_1: calm)

**검증**:
- pytest tests/test_observer → 144/144 PASS
- pytest fast suite → **1763 PASS / 0 FAIL** 유지 (회귀 ZERO)
- demo_observer.py --real 정상 출력

**핵심 설계 결정**:

1. **MicroWorld → Snapshot stream manual mapping**: `engine.simulation.SimulationWorld`와 `engine.world.micro_world.MicroWorld`는 *다른 system*. existing adapter (Phase O6)는 SimulationWorld 결과 (MultiAgentResult)용. MicroWorld는 *helper function*으로 demo level에서 변환. *engine/observer/microworld_adapter.py*는 미생성 (별도 directive 필요 시 추가).

2. **Manual mapping의 데이터 매핑**:
   - `crowd.blame_concentration.values()` 합 → world.blame_concentration (normalized)
   - `crowd.public_suspicion` / `authority_vigilance` → 직접 mapping
   - cohort arc (recovery/saturation/partial/low_activity) → group.dominant_mode (running classification per tick)
   - `agent.state["fear"]` / `agent.state["shame"]["public_group"]` → AgentSnapshot
   - `WorldStep.spawned_events` → active_events list

3. **Branch C lock의 *existence vs magnitude* 분리 명시**:
   - Locked: within-scenario divergence existence, 4/5 axes, modal label match (18/18)
   - NOT locked: 67% sensitivity ratio (single-seed bias), per-dimension magnitudes
   - Public framing 규칙: "predicts" / "proves" / "AI sociology" 같은 단어 회피 (CLAUDE.md Rule #5 일관)

**교훈**:

1. **External eval 결과 처리는 *checklist 자동 분기* 패턴**: PASS_CRITERIA_CHECKLIST의 5 기준 → Case S/M/F binary 자동 분기. Lee가 *해석 부담 없이* checklist 채우면 Claude Code가 자동 다음 plan doc 작성. *automation infrastructure*가 directive cycle의 효율 결정.

2. **MVP freeze 결정 = 검증된 layer의 자연 종착점**: Observer Phase O1-O7 + real-run validation 6/6 → *더 이상 자율 cycle 진행 안 함*. Lee directive §9 forbidden_now ("observer GUI / view 추가 / quality verdict 자동화") 명시 + real-run에서 *기능 결핍 없음* 확인 → freeze 정당.

3. **Helper function vs 정식 module 선택**: `engine/observer/microworld_adapter.py` 정식 module 대신 `examples/demo_observer.py`의 helper 함수로 처리. 이유: (a) 현재 use case = 1 anchor + demo level, (b) Lee directive §9 "새 기능 추가보다 검증 우선", (c) 추가 use case 발생 시 helper → 정식 module promote 가능. *premature abstraction 회피*.

4. **Validation doc 구조 = Keep/Weak/Missing/NotUseful**: review summary doc의 4 quadrant 분류가 *next action 결정의 quick lookup*. Lee directive §5.3 verbatim. 다음 directive에서 *어느 영역이 patch 대상*인지 즉시 식별.

5. **Real-run이 *single-seed sensitivity claim* directly verify**: 3 seeds compare에서 final mood split (tense/calm/tense) → Branch C external eval claim ("configuration-sensitive divergence")과 *같은 anchor 안에서도 단순 seed 변경*으로 동일 패턴 재현. *internal reproduction* of external validation.

6. **Salience tag noise는 *cohort_split + agent_state_shift이 always present*에서 자연 발생**: 200 ticks 내내 3 groups가 다른 mode이면 cohort_split 항상 점수 1 추가. *score-based ranking*이 tie 처리에 의존. fine-grained scoring 후보 (Cycle 8+, but Lee directive §9 forbidden).

연관:
- L31 (idle 자동 종료) → L36-L39 (Observer Phase O1-O7) → **L40 (Branch C Case S + real-run validation)**
- L40 § 1 = Branch C Case S 처리의 standard 흐름 (lock decision + asset pack plan 정식화)
- L40 § 2 = MVP freeze = 검증된 layer의 자연 종착점
- L40 § 5 = real-run이 external eval claim의 internal reproduction

**메타 메타 교훈**: External validation (Branch C GPT-5.5) + Internal validation (Observer real-run) 둘 다 완료. 같은 *configuration-sensitivity claim*이 (a) external readability eval에서 within-scenario divergence detection, (b) internal real-run에서 3-seed final mood split 둘 다로 verify됨. *Cross-validation across two methods* — Branch C lock의 robustness 강화.

L18-L40 = **자율 모드 phase + directive type 23 패턴**.

---

### L39. Phase O7 — Narrative Summary (snapshot stream → 한국어 prose) (2026-04-30)

**Cycle**: Observer Layer MVP (Phase O1-O6) + clean state + core docs sync 후 다음 자율 work. Lee spec §11.3 ("Lee의 판독 효율 향상") 직접 매핑 — Observer 결과를 *prose*로 변환.

**산출물**:
- `scripts/observer/narrative_summary.py` (~290 lines, 4 narrators)
  - `narrate_world_arc()` — world view trajectory prose
  - `narrate_person_arc()` — agent state arc prose
  - `narrate_event_ripple()` — event 영향 prose
  - `narrate_seed_comparison()` — multi-stream contrast prose
- `tests/test_observer/test_narrative_summary.py` (14 tests)
- `examples/demo_observer.py` `--narrate` mode 추가

**검증**:
- pytest tests/test_observer → **144/144 PASS** (130 → 144, +14)
- pytest fast suite → **1763 PASS / 0 FAIL** (1749 → 1763, +14)
- Ruff + mypy clean (11 source files)
- demo --narrate mode 정상 작동 (4 narrators 모두 출력)

**핵심 설계 결정**:

1. **기존 Story Output Layer 우회 + Observer 강점에 최적화**: Story Output Layer는 *probe-shaped data* (single-tick final outcome) 입력. Observer는 *multi-tick stream*. 통합 시 *information mismatch* 큼. → 새 narrator는 *Observer 강점인 multi-tick trajectory*에 직접 작동, Story IR 우회.

2. ***현황 묘사* 단어 선택, *evaluation* 단어 회피**: `_intensity_word()` = "거의 없는" / "옅은" / "중간" / "짙은" / "강한" / "극심한" — 모두 *값 묘사*. "good" / "bad" / "weak" 같은 evaluative 단어 절대 안 씀. `_delta_word()` = "급격히 올랐다" / "오르고 있다" / "거의 변화 없다" — *방향성*만, *quality verdict 아님*.

3. **Prose의 길이 제약**: 각 narrator 출력 1-3 문장. *짧고 정확한 묘사*가 Lee 판독 효율의 핵심. `format_full_report()` (longer table) vs `narrate_*` (compact prose) 보완 관계.

4. **`narrate_seed_comparison` disclaimer 패턴**: 마지막에 항상 "(비교는 대조 표시일 뿐, 어느 stream이 더 낫다는 평가 아님.)" 명시. *사용자가 evaluative 해석할 가능성*을 *언어 자체*로 차단.

5. **Seed comparison의 max/min 사용**: 단순 텍스트 표보다 prose가 *어느 stream이 어느 측면에서 가장*인지 즉시 보임. 단 *quality* 아닌 *값* 측면 (peak_blame max 등). `salient_moments_count` max는 "가장 많음" — neutral observation.

**교훈**:

1. **Observer/Story 통합 = 두 layer 강점 분리 유지**: 강제 통합 (Story IR builder가 Observer snapshot 입력 받게)은 *information loss + 복잡성 증가*. 대신 *각 layer의 강점 영역에 새 entry point 추가*. Observer = multi-tick trajectory narrator. Story = single-probe final outcome narrator. 두 narrator가 *different audience* + *different temporal scope*.

2. **Prose-level "관찰기 ≠ 평가기" 패턴**: salience tag (engine/observer/salience.py) → 단어 선택 (scripts/observer/narrative_summary.py)까지 일관성. *evaluative 단어 회피*는 *데이터 처리*에서만이 아니라 *natural language output*에서도 적용. 이게 진짜 *non-evaluative observer*.

3. **Disclaimer는 코드 차원의 안전장치**: comparison output 마지막에 자동 추가되는 disclaimer는 *명시적 안전장치*. 사용자가 prose를 *evaluative report*로 misinterpret할 가능성 차단. Like *interface contract*가 *언어*에 embedded.

4. **demo mode 추가 = layer capability 가시화**: 새 module 추가 시 demo entry에도 추가 (`--narrate`). single command로 user가 새 capability 즉시 시도. discoverability ↑.

5. **walrus operator alternative — explicit list comp**: ruff fix가 walrus 없는 explicit form 선호. `agents_view = {a.id: a for a in snap.agents if a.id in agent_ids}` (이전 walrus version 자동 변환). 가독성 향상.

연관:
- L38 (core docs sync) → **L39 (narrative summary)**
- L39 § 1 = Observer 강점 (multi-tick stream)에 최적화한 새 narrator (Story IR 우회)
- L39 § 2 = "관찰기 ≠ 평가기" 원칙의 prose-level 코드 표현
- L39 § 3 = disclaimer = interface contract embedded in output

**메타 메타 교훈**: layer 간 통합은 *강제 통합* 아닌 *각 layer 강점 보존 + 새 entry point*가 표준. Observer + Story = *two narrators with different audience + temporal scope*. 사용자에게는 *두 entry point* 모두 가용 (`demo_story.py`, `demo_observer.py --narrate`).

L18-L39 = **자율 모드 phase + directive type 22 패턴**.

---

### L38. Core docs sync (README + DESIGN.md) — Observer Layer 공식 문서화 (2026-04-30)

**Cycle**: Engine integrity fix (L37) 후 *clean state*에서 다음 자율 work. README + DESIGN.md에 World Observer Layer가 반영 안 된 상태 → 공식 문서 동기화.

**산출물**:

### README sync
- 새 섹션 "World Observer Layer (NEW — 2026-04-30)" 추가
  - 1-line 정의 + 아키텍처 ASCII 다이어그램
  - Status (MVP complete, 130 tests, Rule #1 + #6 준수)
  - Quick start (5 commands)
  - 핵심 components 리스트
  - Adapter usage 예제 (SimulationWorld → Observer)
- Version roadmap 표에 v1.3 entry 추가:
  ```
  | v1.3 | World Observer Layer (관찰 계층, 4 lens + salience + replay) | MVP complete (2026-04-30) |
  ```

### DESIGN.md sync
- Project Structure (§9) 갱신:
  - `engine/observer/` 6 files 추가
  - `scripts/observer/` 2 files 추가
  - `scripts/story/selector.py` 추가 (L37 이동 결과)
  - `docs/observer/` 추가
  - examples/demo_observer.py 추가
- 새 §10 World Observer Layer 섹션 (9 subsections):
  - 10.1 정의 (관찰기 ≠ 평가기 원칙)
  - 10.2 아키텍처 다이어그램
  - 10.3 Snapshot Schema 코드 블록
  - 10.4 ABSOLUTE Rules 준수 (Rule #1 + #6)
  - 10.5 9 Salience tag types 표
  - 10.6 MVP scope (포함 + 제외)
  - 10.7 검증 (130 tests + 0 violations)
  - 10.8 Demo entry commands
  - 10.9 Canonical spec reference

**검증**:
- README + DESIGN.md 모두 v1.3 entry 동기화
- 다음 세션 진입 시 *Observer Layer 존재 + 위치 + 사용법* 즉시 인지

**교훈**:

1. **Core docs trinity sync 패턴**: CLAUDE.md (L36) + README + DESIGN.md = 3개 core doc. 새 layer 추가 시 *세 doc 모두 sync*가 표준. CLAUDE.md = action 강령 / README = quick onboarding / DESIGN.md = deep architecture. *각 doc의 audience가 다름* — 같은 정보라도 다른 detail level.

2. **Roadmap entry는 *완성 시점에* 추가**: Observer Layer를 v1.3 entry로 README roadmap에 추가. *MVP complete (2026-04-30)*로 status 명시. Pre-completion entry는 *expectations management 위험* — 완성 후 entry가 *truth 보존*.

3. **Architecture diagram = 첫 인지 도구**: README + DESIGN.md 모두 ASCII diagram 포함. 코드 보기 전에 *layer 관계*를 빠르게 파악 가능. text-only diagram이지만 box-and-arrow notation 충분.

4. **§10 새 섹션 with 9 subsections = layer 완전성**: 작은 layer라도 *정의 + 아키텍처 + 스키마 + 원칙 + 검증 + demo + spec reference* 9 subsection으로 정리. 다음 세션이 *layer 전체*를 single read로 이해.

5. **Quick start 명령 5개 vs 1개**: README는 *user-facing onboarding*. 5 demo modes 모두 명시 (`--status`/`--views`/`--replay`/`--compare`/default). 1개만 적으면 *전체 capability* 못 봄.

연관:
- L36 (CLAUDE.md sync) → L37 (engine integrity fix) → **L38 (README + DESIGN.md sync)**
- L38 § 1 = core docs trinity sync 패턴 (CLAUDE.md + README + DESIGN.md)
- L38 § 2 = roadmap entry는 완성 시점에 추가 (truth 보존)
- L38 § 4 = layer 완전성 (정의 + 아키텍처 + 스키마 + 원칙 + 검증 + demo)

**메타 메타 교훈**: building (Phase O1-O6) → integration (demo + adapter) → integrity fix (L37) → **docs sync (L38)** = layer addition의 *완전한 lifecycle*. 각 단계가 다음 세션의 *discoverability*를 보장.

L18-L38 = **자율 모드 phase + directive type 21 패턴**.

---

### L37. Engine integrity fix — selector.py engine/story/ → scripts/story/ (2026-04-30)

**Cycle**: pre-existing 1 pytest failure (`test_no_person_hardcoding_in_engine`) 해소. J-Beta selector library가 `engine/story/`에 person name (peter/vangogh) hardcode → ABSOLUTE Rule #1 위반 21개. *physical move + import path update*로 위반 제거.

**문제**:
- `engine/story/selector.py` 21 violations (peter 19개 + vangogh 2개) — anchor IDs ("peter_scarcity_baseline", "vangogh_sacred_baseline") + factory function names (`_make_peter_*`)
- pytest `test_no_person_hardcoding_in_engine` FAIL (pre-existing 다음 세션마다 표시됨)
- selector는 *engine API 아님* — 실제로는 *scripts*-level helper (curated anchor list builder). 잘못된 위치.

**해결**:
1. `engine/story/selector.py` → `scripts/story/selector.py` (267 lines copy)
2. Import update 3 sites:
   - `scripts/story/generate_anchor_variations.py`
   - `scripts/story/generate_trilogy_view.py`
   - `tests/test_story/test_selector_alpha.py`
3. `engine/story/` 폴더 전체 삭제 (`__init__.py` + `selector.py` + `__pycache__`)
4. CLAUDE.md PROJECT STRUCTURE update — `scripts/story/selector.py` 추가, `engine/story/` 흔적 제거

**검증**:
- pytest tests/test_engine/test_integrity.py → **PASS** (이전 FAIL → 0 fail)
- pytest tests/test_story/test_selector_alpha.py → **15 PASS**
- pytest fast suite → **1749 PASS / 0 FAIL** (이전 1748 PASS + 1 FAIL → **clean state**)
- 기존 selector 사용처 (anchor variations, trilogy view, test_selector_alpha) 모두 정상

**교훈**:

1. **Pre-existing failure는 적기에 해소 = high-value low-risk work**: 21 violations 누적 + 매 LOOP마다 grep 결과 노이즈. 작업 단가 작음 (4 file edit + 1 folder delete) + 큰 가치 (clean pytest state + Rule #1 준수).

2. **Module location은 *역할 정의*에 따른다**: J-Beta selector는 anchor list curation — `scripts/`-level helper. `engine/`은 *universal engine, person-agnostic*. 잘못된 위치에 있으면 Rule #1 자동 위반. Module placement = *responsibility classification*.

3. **Import path move는 안전한 refactor**: selector.py 내부 코드 미변경 + import 경로만 update. Behavior preservation 확실. *test 검증 즉시 가능* (regression이 보이거나 안 보이거나 binary).

4. **Untracked 파일도 ABSOLUTE Rule 적용 대상**: `engine/story/` 자체가 untracked (git status `??`)였지만 *test_integrity가 file system 기반*으로 검사. tracked status 무관 — 파일 존재 자체가 violation 트리거. *Rule은 git status 무관 적용*.

5. **CLAUDE.md update = 동시 의무**: 코드 이동 시 PROJECT STRUCTURE 동기화. 다음 세션에서 *위치 혼선* 방지. `engine/story/` 흔적 제거 + `scripts/story/selector.py` 명시.

연관:
- L36 (Phase O6 adapter + CLAUDE.md sync) → **L37 (engine integrity fix + 같은 sync 패턴)**
- L37 § 2 = ABSOLUTE Rule #1 의 *responsibility classification* 원칙
- L37 § 4 = Rule은 git status 무관 적용 (untracked 포함)

**메타 메타 교훈**: 큰 새 layer 추가 (Observer)와 작은 cleanup (selector move) 모두 *같은 LOOP 단위*에서 진행 가능. broad directive ("자체 판단으로 반복 개선")는 *작은 cleanup*도 자율 work으로 인정. 매 LOOP마다 (a) substantive new work + (b) cleanup 발견 시 즉시 처리.

**최종 pytest 상태 (2026-04-30 시점)**:
- 1749 PASS / 14 skipped / 133 deselected
- **0 failures** (clean state 도달)
- engine integrity violations: **0** (이전 21 → 0)

L18-L37 = **자율 모드 phase + directive type 20 패턴**.

---

### L36. Phase O6 — MultiAgentResult adapter + CLAUDE.md sync (2026-04-30)

**Cycle**: Lee broad directive ("observation 레이어와 프로젝트 전체적인 완성도 자체적으로 판단하여 반복해서 개선"). 자율 가능 영역 확장. 우선순위 = (A1) Observer Phase O6 real-trajectory adapter + (B5) CLAUDE.md 동기화.

**산출물**:
- `engine/observer/adapter.py` (~180 lines)
  - `agent_state_to_snapshot()` — engine.AgentState → observer.AgentSnapshot 매핑
  - `result_to_observer()` — MultiAgentResult → Observer (post-hoc 변환)
  - `_detect_state_delta()` — tick-over-tick agent shift 감지 (threshold 1.0)
- `tests/test_observer/test_adapter.py` (14 tests)
- `CLAUDE.md` PROJECT STRUCTURE 갱신 — `engine/observer/` 6 파일 + `tests/test_observer/` 8 파일 명시

**검증**:
- pytest tests/test_observer → **130/130 PASS** (116 → 130, +14)
- pytest fast suite → **1748 PASS** (1734 → 1748, +14) — 회귀 ZERO
- Ruff + mypy → clean (7 source files)
- Engine integrity → observer code 위반 0 (pre-existing 1 failure 유지)

**핵심 설계 결정**:

1. **Adapter는 SimulationWorld 무수정 + post-hoc 변환**: ABSOLUTE Rule #6 (engine API preservation) 준수. SimulationWorld.run() 결과 (MultiAgentResult)를 받아서 *외부에서* Observer로 변환. *real-time callback hook은 미구현* (별도 phase, 추가 directive 필요).

2. **role_map = caller-provided**: adapter 자체엔 person 이름 없음 (ABSOLUTE Rule #1). caller가 `{agent_id: generic_role}` dict 제공. 미제공 시 default "generic". *adapter는 person-agnostic*.

3. **Schema gap 매핑**: AgentSnapshot은 fear/hope/shame_self만. AgentState는 더 풍부 (5 emotions + 5 slow_state fields). 매핑 결정:
   - `shame_self ← AgentState.slow_state.moral_injury` (semantic 가까움 — moral_injury는 자기 신념 위반 후 누적)
   - 다른 emotions/slow fields는 이번 phase에서 미반영
   - 향후 schema 확장 시 backward compat 유지 (Pydantic Optional defaults)

4. **World/Group은 caller-provided optional**: MultiAgentResult에 world-level state 없음 (EnvironmentState는 SimulationWorld 내부). adapter는 *agents only* 자동 처리 + *world/group은 caller가 dict per tick 제공* (None이면 default).

5. **Active events from fired_events fallback**: caller가 `active_events_per_tick` 미제공 시 `result.fired_events`에서 자동 추출. `{tick: [event_id]}` 형태.

**교훈**:

1. **Adapter pattern으로 회귀 위험 zero**: SimulationWorld 무수정 + 외부 helper가 변환. 1734 PASS → 1748 PASS, 새 14 tests만 추가, 회귀 ZERO. *engine 핵심을 건드리지 않는 새 layer*.

2. **Schema 매핑 결정 = 명시적 trade-off**: 풍부한 source schema (AgentState 5 emotions + 5 slow) → 작은 target schema (AgentSnapshot 3 fields). 정보 손실 인정 + 핵심만 유지. *light view* 원칙 (L33 §3 재확인).

3. **Caller-provided generic role pattern**: ABSOLUTE Rule #1 회피의 *standard pattern*. engine/ 안의 함수는 *generic identifier만* 받음. *caller-side에서* person → role 매핑. 같은 패턴이 향후 다른 engine API에도 적용 가능.

4. **CLAUDE.md sync = 작은 작업 + 큰 가치**: PROJECT STRUCTURE 섹션에 `engine/observer/` + `tests/test_observer/` 추가. 6 + 8 = 14 줄. 다음 세션에서 *Observer Layer 존재 + 위치를 즉시 인지*. 동기화 안 하면 discoverability 손실.

5. **Mock 패턴 for circular import 회피**: `_MockResult` 작은 stub class — `MultiAgentResult` 대신 사용 (test에서). Circular import (engine.simulation.world → engine.observer.adapter → engine.simulation.world) 회피.

연관:
- L35 (통합 demo) → **L36 (real trajectory adapter)**
- L36 § 1 = ABSOLUTE Rule #6 준수의 standard pattern
- L36 § 3 = ABSOLUTE Rule #1 generic identifier pattern
- L36 § 4 = 문서 sync는 small but high-value work

**메타 메타 교훈**: Lee broad directive ("자체적으로 판단해서 반복 개선")에 대한 *해석*: (a) 명시 영역 (Observer) Phase O6 진행 + (b) 프로젝트 일반 (CLAUDE.md sync). 두 가지 모두 자율 가능. *broad directive = 영역별 자율 + 회귀 위험 zero 원칙*.

L18-L36 = **자율 모드 phase + directive type 19 패턴**.

---

### L35. Observer 통합 demo + UTF-8 stdout fix (2026-04-30)

**Cycle**: Phase O1-O5 완료 후 Lee가 Observer를 직접 실행해 볼 수 있는 *통합 entry point* 작성. 4 modes (--status / --views / --replay / --compare) + default full.

**산출물**:
- `examples/demo_observer.py` (~330 lines)
  - `build_synthetic_stream(seed_label)` — 14-tick × 3 agents × 2 groups synthetic stream
  - 3 seeds (recover / slow / locked) — `compare_seeds`가 의도대로 차별화 표시
  - 4 commands + default full report

**검증**:
- `--status` → MVP 상태 + 7 components + 116 tests passing 표시
- `--views` → 4 lens (World/Person/Group/Event) text 출력
- `--replay` → ReplayCursor jump + auto_bookmark (2 turning points) + advance/back
- `--compare` → 3 seeds 측면 비교 + multi-lens at tick

**자체 발견 + 즉시 fix**: cp949 encoding 에러 (Windows console + em-dash —). 해결:
```python
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
```

**교훈**:

1. **Synthetic stream 패턴**: 실제 SimulationWorld 호출 없이 *합성 snapshot stream*으로 demo 가능. 14 tick에 *story arc* (calm baseline → accusation → saturation → recovery) embedded. seed_label 변형으로 *3 다른 outcome* (recover / slow / locked).

2. **demo가 곧 test**: demo가 실행되면 *integration test* 효과 (실제 4 lens API + ReplayCursor + compare_views가 함께 작동하는지 검증). pytest test_observer는 unit-level, demo는 *end-to-end smoke*.

3. **UTF-8 stdout 강제 패턴 (Windows cp949 fallback)**: Korean prose + em-dash 출력 시 Windows cp949 codec 충돌. `sys.stdout.reconfigure(encoding="utf-8")`로 해결. *try/except*로 Python <3.7 호환 가드.

4. **3 seeds 차별화 명확성**: seed_0 (recover) → final_mood "calm" / seed_1 (slow) → "calm" / seed_2 (locked) → "agitated" + peak_blame 0.95 (vs 0.85, 0.65) + salient_moments 11 (vs 8, 8). *compare_seeds가 의도대로 다른 streams 차별화*.

5. **Default mode = full report**: `python examples/demo_observer.py` (no args) → status + views + replay + compare + full_report 모두 실행. Lee 한 명령으로 전체 보기.

6. **Single entry point pattern**: `examples/demo_observer.py`가 Observer Layer의 *user-facing single entry*. examples/demo_creative.py / examples/demo_story.py와 같은 패턴. *Lee가 한 file로 layer 전체 체험*.

연관:
- L34 (Phase O3-O5) → **L35 (통합 demo)**
- L35 § 1 = synthetic stream으로 simulation 의존성 회피 (테스트 가능성 향상)
- L35 § 3 = Windows console UTF-8 fallback 표준 처리
- L35 § 6 = examples/demo_*.py = layer entry point 패턴

**메타 메타 교훈**: layer building (Phase O1-O5)이 끝나면 *integration demo*가 자연스러운 마무리. demo는 *user perspective*를 강제 — 실제 호출 가능한지, 출력이 의미 있는지 검증. 여기서 발견한 cp949 버그처럼 *real environment issues*가 드러남.

L18-L35 = **자율 모드 phase + directive type 18 패턴**.

---

### L34. World Observer Layer Phase O3-O5 — text reports + replay/jump + multi-stream compare (2026-04-30)

**Cycle**: Phase O1+O2 (snapshot schema + Observer core API + salience) 완료 후 동일 LOOP 다음 phase. 이번 LOOP에서 Phase O3 (text reports) + O4 (replay/jump/bookmark) + O5 (compare_views) 모두 진행.

**산출물**:
- `scripts/observer/observer_report.py` — text report 함수 11개 (4 lens × view/arc + salience summary + unstable agents + full report)
- `engine/observer/replay.py` — `ReplayCursor` (jump/advance/bookmark) + `auto_bookmark_turning_points` + `recent_window` + `before_after_window`
- `scripts/observer/compare_views.py` — `stream_summary` + `compare_seeds` + `format_seed_comparison` + `multi_lens_at_tick` + `format_multi_lens_at_tick`
- 3 test files, **49 new tests PASS** (test_observer 67 → 116 total)

**검증**:
- pytest tests/test_observer → **116/116 PASS** (0.16s)
- pytest fast suite → **1734 PASS** (1685 → 1734, +49) — 회귀 ZERO
- Engine integrity → 내 observer code 위반 ZERO
- Ruff + mypy → clean (9 source files)
- Ruff auto-fix → 14 unused imports 자동 제거 (test files + module files)

**교훈**:

1. **Text report의 categorical → 한국어 tag 매핑**: `crowd_mood = "tense" → "긴장"`, `dominant_mode = "saturation" → "고착"`. 평가 단어 회피 ("good"/"bad" 안 씀). *categorical tag는 직역, 평가는 안 함*.

2. **Intensity bar 시각화 = 값 표시 ≠ 평가**: `_intensity_bar(0.7) → "███████···"`. 막대 길이는 *값의 정도*만 표시, *quality verdict* 아님. 0-1 normalized + 0-10 (agent state) 두 버전.

3. **ReplayCursor 패턴 = stateful navigation over stateless data**: snapshot stream은 immutable (Observer가 보장). cursor는 *position 추적*만, stream 자체는 변경 안 함. *bookmark dict + auto_bookmark_turning_points*로 turning point 자동 인덱싱.

4. **Stream-level summary는 *구조적 metric*만**: `stream_summary()` returns peak_blame / peak_suspicion / final_crowd_mood / salient_moments_count. *모든 metric이 mechanically computable* — 어떤 stream이 "더 좋다" 판정 안 함. `format_seed_comparison()` disclaimer: "Comparison = contrast display, not quality verdict".

5. **Multi-lens at tick = *aggregation* over multiple lenses**: 같은 tick에서 World + Group + Agent 동시 보기. Lee directive §4.6 "compare same tick: world vs person vs event"와 매핑. `agent_ids` / `group_ids` filter로 zoom 가능.

6. **Walrus operator pattern (PEP 572)**: `aid: a for a in snap.agents if (aid := a.id) in agent_ids` — comprehension에서 변수 바인딩 + 조건 체크 동시. 작은 우아함, 가독성 향상.

7. **Auto-fix safe pattern**: ruff `--fix`가 *unused imports만* 자동 제거 (semantic 변경 없음). Pydantic 모델 import 14개 자동 정리 → 코드 더 깨끗. *auto-fix 적극 활용 + manual 검토*.

8. **Phase별 분해 → 작업 단위 = 1 phase per LOOP**: 큰 layer를 *5 phase로 분해* (O1-O5). LOOP당 1-2 phase 진행. 각 phase 완료 시 *test + integrity + ruff/mypy* 검증. 큰 변경을 *작은 검증된 단위*로.

9. **scripts/observer/ vs engine/observer/ 분리**: engine/observer = *core API* (Pydantic models, Observer class, salience, replay). scripts/observer = *user-facing helpers* (text reports, comparison utilities). *Rule #6 (engine API preservation) 위반 회피*: 외부 helper는 scripts/.

연관:
- L33 (Phase O1+O2 — schema + core + salience) → **L34 (Phase O3-O5 — reports + replay + compare)**
- L34 § 1-2 = "관찰기 ≠ 평가기" 원칙의 text 출력 표현
- L34 § 8 = Phase별 LOOP 진행 패턴 (작은 검증된 단위)
- L34 § 9 = engine/scripts 분리 = ABSOLUTE Rule #6 준수

**메타 메타 교훈**: 큰 새 layer (Observer)도 *spec-driven phased implementation*으로 회귀 위험 zero + 이전 작업 보존 가능. Lee directive "이대로 구현하고 루프로 반복" — *spec 그대로 + LOOP별 phase 진행*이 표준 패턴.

L18-L34 = **자율 모드 phase + directive type 17 패턴**.

---

### L33. World Observer Layer 구현 패턴 — 관찰기 ≠ 평가기, additive layer 원칙 (2026-04-30 Phase O1+O2)

**Cycle**: Lee가 새 spec (`WITNESS_WORLD_OBSERVER_LAYER_SPEC.md`) 보냄. Person Engine 위에 *흐르는 세계 관찰 계층* 추가 — *building 재개* (curation phase에서 다른 영역으로 확장).

**Lee directive 핵심**:
1. World Observer Layer = Snapshot stream + Multi-view + Salience detector
2. **관찰기 ≠ 평가기** ("좋은 이야기/나쁜 이야기" 자동 판정 금지)
3. *additive layer* (기존 engine 무수정)
4. MVP = 텍스트 기반, no GUI

**이번 LOOP 구현 (Phase O1+O2)**:

| 산출물 | 설명 |
|---|---|
| `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` | Canonical spec (Lee directive에서 옮김) |
| `engine/observer/__init__.py` | Module entry |
| `engine/observer/snapshot_schema.py` | 4 Pydantic 모델 (Snapshot/World/Group/Agent) |
| `engine/observer/recorder.py` | `record_snapshot()` + `SnapshotStream` 클래스 |
| `engine/observer/core.py` | `Observer` 클래스 (4 lens API: World/Person/Group/Event) |
| `engine/observer/salience.py` | salience detector (8 tag types) + top-N moments/agents |
| `tests/test_observer/` | 4 test files, **67 tests PASS** |

**검증**:
- pytest tests/test_observer → **67/67 PASS** (0.16s)
- pytest fast suite → **1685 PASS** (1618 → 1685, +67) — 회귀 ZERO
- Engine integrity → 내 observer code 위반 ZERO (남은 violations 모두 `engine/story/selector.py` pre-existing)
- Ruff + mypy → clean (5 source files)

**교훈**:

1. **관찰기 ≠ 평가기 원칙의 코드 표현**: salience detector는 *attention pointer* (점수 = tag count, 단순 binary count). NOT *quality verdict*. 함수 이름도 `top_salient_moments()` (salient = "noticeable") — *evaluative* 단어 회피 ("best", "worst", "good" 안 씀).

2. **Additive layer = 기존 engine 무수정 + 외부 entry point**: Observer는 SimulationWorld 내부 변경 없이 *post-hoc snapshot stream* 받음. Recorder는 *helper function* 형태. 기존 1500+ tests 영향 ZERO.

3. **Pydantic schema의 light view 패턴**: AgentSnapshot은 engine의 AgentState (PhysicalState/EmotionalState 등) *전체*가 아니라 *subset* (id, role, fear, hope, shame_self, delta). 관찰자가 보기 좋은 light view, *engine schema와 분리*.

4. **Generic schema + role tag로 Rule #1 준수**: AgentSnapshot.role = "follower" / "crowd" / "authority" 같은 *generic role*. Person name 절대 안 들어감. 단 docstring example에 "peter" 적었다가 즉시 fix — *docstring도 hardcoding 검출 대상*.

5. **delta 자동 계산 패턴**: `SnapshotStream.append_from_stats()`가 직전 tick agent stats 자동 보존 → 다음 tick에서 delta 계산. *stateful helper* 클래스로 *stateless function*의 stream-level convenience 제공.

6. **Salience tag 8가지 표준화**:
   - `pressure_spike` / `authority_vigilance_spike` / `public_suspicion_jump` / `blame_concentration_spike` (world-level deltas)
   - `cohort_split` / `recovery_turning_point` / `saturation_lock` (group-level patterns)
   - `low_activity_tension` (cross-level)
   - `agent_state_shift` (agent-level)

7. **Phase별 진행 + LOOP 반복 개선**: O1+O2 (이번 LOOP) → O3 (text reports) + O4 (replay/jump) + O5 (compare) → 다음 LOOP. 큰 layer를 *작은 phase로 분해* + *각 phase의 검증 (test+integrity+ruff/mypy)* 후 다음으로.

연관:
- L32 (curation phase directive) → **L33 (world observer layer 구현)**
- L33 § 1 = Lee directive §6 원칙 1 (관측 태그까지만, 평가 안 함) 코드 표현
- L33 § 2 = ABSOLUTE Rule #6 (engine API preservation) 준수
- L33 § 4 = ABSOLUTE Rule #1 (no person hardcoding) docstring 포함

**메타 메타 교훈**: directive type 진화 + 새 layer 추가 결합. Type E/curation phase에서 *Renderer 작업 동결*했지만, *다른 영역 (Observer Layer) 작업은 새 directive로 trigger*. 자율 모드 boundary는 *영역별*로 다름 — Renderer freeze ≠ Observer freeze.

L18-L33 = **자율 모드 phase + directive type 16 패턴**.

---

### L32. Curation phase directive — patch 단계 종료 후 selection/editing/packaging (2026-04-30)

**Cycle**: Type E directive (Cycle 7 freeze + Branch C 분기 사전 정의) 후 Lee가 보강 directive (`WITNESS_NEXT_PLAN_AFTER_RENDERER_FREEZE_AND_BRANCHC_GO.md`) 보냄. 핵심: *renderer는 patch가 아니라 curation*.

**Lee directive 핵심 원칙**:
1. **Branch C external eval 먼저** (구조 검증)
2. **Renderer = patch가 아니라 curation** (선별·편집·패키징)
3. **public demo는 아직 아님** (Branch C 결과 도착 후 Case S 시만)

**Phase 진화 (Renderer)**:

| Phase | 행동 | 단계 |
|---|---|---|
| Phase A — Building | Cycle 1-7 patch 진행 | 완료 |
| **Phase B — Freeze** | Cycle 7 lock, 추가 patch 금지 | **현재 (Cycle 7 freeze)** |
| **Phase C — Curation** | 선별·편집·패키징 준비 | **이번 directive 시작** |
| Phase D — Public release | Branch C Case S 후 asset pack v1 | TBD |

**교훈**:

1. **"더 만들지 말라"가 자율 모드의 새 boundary**: Cycle 1-7는 *building*. Lee가 명시적으로 *building 종료 + curation 시작* 선언. 자율 모드의 *행동 종류 자체* 변화: code patch → document organization + selection logic.

2. **문서 체계 정리는 curation의 첫 단계**: `RENDERER_GATE1_V3_RESULTS.md` (Cycle 2 시점) vs `RENDERER_GATE1_V3_BUNDLE_CYCLE7.md` (Cycle 7 시점) — *latest decision source* 명확화. 미명시 시 *어느 doc 기준*인지 혼선. *header에 superseded / latest 표기*가 표준 처리.

3. **Stage gating with checklists**: Branch C 결과 도착 시 *자동 분기*를 위해 사전 점검표 (`BRANCH_C_PASS_CRITERIA_CHECKLIST.md`) + response placeholder (`BRANCH_C_GPT55_RESPONSE_RAW.md`) 준비. Lee가 응답 받으면 *기계적 PASS/FAIL 판정 → Case S/M/F 분기*. *automation infrastructure* 자체가 Stage 1 자율 work.

4. **Placeholder 파일과 trigger 신호 충돌**: 이전 LOOP에서 `ls BRANCH_C_GPT55_RESPONSE_RAW.md`로 응답 도착 여부 판정. 이번에 placeholder 파일 만들어서 ls existence가 더 이상 trigger 안 됨. 새 trigger = *파일 내용 안에 actual response text 존재 여부* (e.g. `grep -c "P_NEW_01" BRANCH_C_GPT55_RESPONSE_RAW.md`). *ls existence 대신 content presence*.

5. **Curation phase는 forbidden 확장**: building forbidden (Cycle 8+) + curation forbidden (public demo 사전 진행 / Branch C 전 asset pack 공개). 두 layer forbidden이 함께 적용.

6. **자율 가능 work이 새 종류**: Cycle 1-7 = code patch. Curation phase = 문서 체계 정리 + checklist 준비 + (Branch C 후) asset selection. *행동 종류*가 다르지만 *자율 가능*은 여전.

연관:
- L30 (Type E freeze + 분기 사전 정의) → L31 (idle 자동 종료) → **L32 (curation phase directive)**
- L32 §2 = 문서 체계 정리는 curation 첫 단계
- L32 §3 = automation infrastructure가 Stage 1 work
- L32 §4 = placeholder + trigger 신호 충돌 → content presence 검출 필요

**메타 메타 교훈**: directive type 진화 연속 (A→B→B-2→C→D→E)에서 **E 보강 = phase 변환 directive**. *building → curation → public release* 3 phase. Phase 간 boundary가 *Branch C external eval 결과* (구조 검증) + *Lee 평가* (전달 검증) 둘 다.

L18-L32 = **자율 모드 phase + directive type 15 패턴**.

---

### L31. Idle 자동 종료 패턴 — 자율 모드 자연 boundary 명시화 (2026-04-29)

**Cycle**: Type E directive (Cycle 7 freeze + Branch C 결과 대기) 후 자율 작업 0건 상태에서 700s마다 idle check 17회 연속 반복. Lee가 idle 자동 종료 명시.

**문제 (idle check 무한 반복)**:
- Type E directive scope 안에서 자율 진전 0건
- 외부 입력 (Branch C 응답 / Lee 평가 / 새 directive) 대기
- ScheduleWakeup 호출로 700s마다 같은 idle 상태 재확인
- *시간 + 토큰 + cache* 낭비 (의미 있는 변경 없는 LOOP 반복)

**해결 패턴 (idle 자동 종료)**:
Idle 상태 도달 시 *ScheduleWakeup 미호출* → loop 자연 종료. Lee 새 입력으로 재개.

**자율 모드 4 phase 재정의**:

| Phase | 행동 | ScheduleWakeup |
|---|---|---|
| Active (자율 작업 진행) | substantive work + 700s wakeup | ✅ 호출 (700s) |
| Active (small marginal work) | marginal work + 700s wakeup | ✅ 호출 (700s) |
| **Idle (자율 작업 0건)** | **마지막 진단 + 종료** | **❌ 호출 *생략*** |
| External input arrived | 분기 처리 + 다음 LOOP scheduling | ✅ 호출 (700s) |

**Idle 판정 기준**:
- 현재 directive scope 안에서 substantive work 0건
- 외부 입력 대기 상태 (Branch C / Lee 평가 / 새 directive)
- forbidden_now 안에서 marginal work만 남음 (또는 0건)

**교훈**:

1. **자율 모드의 자연 boundary = idle**: L29 §6 "자율 cycle 자연 boundary = Lee 평가 결과"의 *operational 형태*. 자율 모드는 *이론적으로* 무한 가능하지만 *실질적으로* idle에서 종료해야 함.

2. **Idle check 무한 반복 = anti-pattern**: 700s × 17 = ~12,000 토큰 낭비. ScheduleWakeup의 의도는 *active work 사이 cadence*이지 *idle 무한 wait*가 아님.

3. **Lee 새 입력이 진짜 trigger**: Lee directive 업데이트 / 외부 결과 도착 / 평가 입력 — 이 셋 중 하나가 *real trigger*. ScheduleWakeup-driven idle wakeup은 *fake trigger* (state 변화 없음).

4. **ScheduleWakeup 미호출 = loop 종료의 표준 method** (skill 문서 §5 dynamic mode). 명시적 패턴이지만 이전엔 적용 안 했음 — Type E directive scope 엄격 해석 + 700s 고정 명시 때문에 무한 idle wakeup.

5. **자율 모드 운영 원칙 진화**:
   - 초기: "/loop = 무한 자율 cycle"
   - 중간: "Type B/B-2/C/D/E directive로 boundary 정의"
   - **현재: idle 도달 시 자동 종료 — 자율 모드 끝**

연관:
- L29 § 6 (자율 cycle 자연 boundary) → **L31 (idle 자동 종료 = boundary의 operational 형태)**
- L31 § 4 = ScheduleWakeup skill 문서 §5 dynamic mode (`omit ScheduleWakeup` 패턴)
- L31 § 5 = 자율 모드 한계의 명시적 정의

**메타 메타 교훈**: directive type evolution (A→B→B-2→C→D→E)이 자율 boundary를 *명시*했고, idle 자동 종료 (L31)는 그 boundary의 *operational implementation*. 자율 cycle은 이제 *Lee 새 입력에 의한 명시적 재개*가 표준.

L18-L31 = **자율 모드 phase + directive type 14 패턴**.

---

### L30. Type E directive — Lee 평가 완료 후 freeze + 분기 사전 정의 (2026-04-29)

**Cycle**: Cycle 1-7 진행 후 Lee가 v3 평가 결과 + 명시적 freeze decision 보냄. directive type 진화의 *제 5 단계*.

**Type E directive 특징** (이전 type들과 비교):

| Aspect | Type A | Type B | Type B-2 | Type C | Type D | **Type E** |
|---|---|---|---|---|---|---|
| 트리거 | 새 작업 | saturation 후 forbidden | 외부 판독 대기 | 외부 평가 partial pass | saturation override | **Lee 평가 완료** |
| 자율 cycle | 진행 | 정지 | 결과 후 분기 | scoped patch | iterative | **명시적 정지** |
| 외부 입력 | 무관 | Lee directive | 외부 결과 | Lee verdict + scoped | 무관 | **Lee verdict + freeze** |
| 분기 사전 정의 | 없음 | 없음 | 있음 (4 cases) | 없음 | 없음 | **있음 (3 cases for Branch C)** |
| Cycle 추가 | 가능 | 금지 | 가능 (결과 후) | 1 cycle | 무한 가능 | **금지 (Cycle 7 lock)** |

**Type E의 핵심 패턴**:
1. **Lee 직접 평가 완료**: v3 verdict 6 sample + 가장 좋은/약한 Cycle 식별
2. **자율 cycle 명시적 정지**: "Cycle 8은 진행하지 않는다" / "Cycle 7 상태에서 freeze"
3. **분기 사전 정의**: Branch C 결과별 3 case (S/M/F) 사전 명시
4. **scoped cleanup만 허용**: Sample 6 patch memo 같은 *작은 cleanup*만
5. **Lee 평가가 다음 단계 결정자**: rollback도 Lee 명시 필요 (자율 rollback 금지)

**교훈**:

1. **Lee 평가가 자율 cycle의 진짜 boundary**: Cycle 1-7 중 Lee 평가 받은 cycle = Cycle 2 단 1번. Cycle 3-7 (5개)는 Lee 평가 없이 진행. Lee가 Type E directive에서 *Cycle 7까지 효과 인정 + 정지*를 명시함으로써 자율 cycle의 *retroactive 정당성*을 부여. 자율 cycle의 정당성 = *Lee 평가 후 retroactive 인정*.

2. **가장 약한 cycle 식별 = 정직한 평가의 가치**: Lee가 "Cycle 7 motif closing이 가장 약하다"고 명시 — 이는 *내가 자율 진행한 cycle을 Lee가 직접 평가한 첫 사례*. Lee의 정직한 평가가 향후 자율 cycle *limit 설정의 기준* 됨.

3. **Cycle 5-7는 over-engineering 위험 인지 후 진행이라 *부분* 정당화**: L29 (Cycle 7) 자가 진단에서 over-engineering 인지 + risk-cap 명시 + rollback path. Lee가 Cycle 7를 "약한 cycle"이라 평가했지만 *전체 Cycle 8 정지*만 명시 — Cycle 7 자체 rollback은 미명시. 즉 *risk-cap 인지 자체*가 부분 정당화.

4. **Sample 6 patch memo cleanup = BUNDLE doc 메타 표시 문제, narrative 본문 무관**: 진단 결과 narrative 본문 자체는 깨끗. BUNDLE doc §2.6에서 *Lee 평가 가이드*로 추가한 메타 annotation (`[Cycle X Patch Y]` + `**(...explanation...)**`)이 narrative inline 형태이라 *본문 잔재*로 인식. cleanup 방법 = *축약 placeholder를 깨끗한 narrative 본문으로 교체*. 다른 sample의 [Cycle X] annotation은 *Lee 평가 후 reference*로 보존.

5. **Renderer asset 단계 진화**: Cycle 1-7 = renderer 본문 개선. 이후 단계 = curated asset pack (Lee 결정 #5). *renderer 만들기*에서 *renderer 결과 선별*로 *modus operandi* 변화. *내부 데모 수준* (Case M) vs *public asset pack* (Case S) 구분이 새 architecture.

6. **분기 사전 정의 (Type E + Type B-2 결합)**: Type B-2 (4 cases for renderer + Branch C) → Type E (3 cases for Branch C only). *외부 입력별 자율 재개 protocol*이 directive 표준. *Lee 평가 + 외부 결과 양방향 trigger*.

연관:
- L29 (Cycle 7 coherence ring + over-engineering risk-cap) → **L30 (Type E freeze + 분기 사전 정의)**
- L30 § 1 = "Lee 평가가 자율 cycle 진짜 boundary" — 자율 mode 정직성의 finalization
- L30 § 6 = Type B-2 + Type E 조합으로 *외부 입력별 protocol* 표준화

**메타 메타 교훈**: directive type 진화 = A → B → B-2 → C → D → **E**. *자율 모드 자체 한계*가 directive E에서 명시됨 — *Lee 평가 완료 후 freeze*가 자율 cycle의 *자연 종착점*. 다음 cycle은 *Lee 평가 + 외부 결과 둘 다 도착해야* 재개 가능. directive type이 자율성을 *명시적으로* 좁힘.

L18-L30 = **자율 모드 phase + directive type 13 패턴**.

---

### L29. Coherence ring closing 패턴 — over-engineering risk-cap 후 자율 cycle (Cycle 7 Patch K, 2026-04-29)

**Cycle**: Cycle 6 완료 후 Lee 약점 saturation. Cycle 1-6 retrospective 작성 후 *Cycle 7 over-engineering 위험으로 미룸* 판단했지만, Lee directive Type D ("계속 개선") 엄격 해석 시 *renderer 개선 자체*는 계속이라 Cycle 7 진행. *작은 patch* + *명시적 rollback path* + *risk-cap 인지*로 over-engineering 위험 처리.

**문제**:
- Lee 명시 약점 saturation — Cycle 7는 *Lee 미명시 자율 영역*
- "renderer 개선" directive vs "over-engineering 위험" trade-off
- Lee 평가 받기 전 더 깊이 들어감 위험

**해결 패턴 (over-engineering risk-cap)**:
1. **작은 patch만**: 큰 architecture 변경 (coordinated motif selection 등) 회피
2. **additive only**: 기존 architecture 무수정, 새 stage 1개만 추가
3. **명시적 rollback path**: Lee 평가에서 부정적이면 즉시 rollback 가능 (단일 patch)
4. **scope cap**: Cycle 7 단일 Patch K. Cycle 8+로 확장 안 함 (Lee 평가 후 결정)
5. **risk-cap 명시**: plan doc에 Lee 미명시 영역임을 명시 + rollback 절차 명시

**Cycle 7 Patch K 구조**:
- Probe별 *primary motif* hash로 결정
- narrative 마지막에 motif closing line 1개 추가 (Stage 6 추가)
- *coherence ring*: opening (motif setup) → pressure → outcome → aftereffect → **motif closing** (마지막 잔향)

**교훈**:

1. **Lee 미명시 자율 cycle의 진행 조건**: Lee directive scope 명확 ("renderer 개선") 시 *Lee 미명시 영역* 자율 진행 가능. 단 *over-engineering risk-cap* 명시 + *작은 patch* + *rollback path*. 무한 자율 vs 명시적 boundary 균형.

2. **Saturation override directive (Type D)의 두 해석**:
   - 좁은 해석: "Lee 명시 약점 saturation 도달 → 더 이상 자율 진행 안 함"
   - **넓은 해석**: "renderer 개선 자체 계속, Lee 미명시 영역도 자율 가능 (단 risk-cap 명시)" ← Cycle 7 적용
   - 직접 Lee directive 문장 = "Saturation에 도달해도 계속해서 Renderer 개선해" → *직접 명시*가 *넓은 해석* 지지

3. **Coherence ring 패턴**: narrative 전반에 걸쳐 *primary motif* (scarcity 자루/시장/창고 / accusation 이름/손가락/시선 / sacred 기도/침묵/성전)이 *opening setup* → *pressure development* → *closing return*로 ring 형성. 마지막 1 sentence가 *narrative 전체 coherence*를 닫음.

4. **Stage 6 추가 = additive structural change without architecture rewrite (L27 패턴 재사용)**: Cycle 5 Patch I (Stage 2.5 추가)와 동일 패턴. *기존 stages 무수정 + 새 stage 추가* — additive only로 회귀 위험 zero.

5. **Patch 누적 단위 = 하나의 lesson**: L24 (Cycle 2) → L25 (Cycle 3) → L26 (Cycle 4 Patch G) → L27 (Cycle 5 Patch I) → L28 (Cycle 6 Patch J) → **L29 (Cycle 7 Patch K)**. 각 patch가 *재사용 가능 unit*으로 분리됨.

6. **자율 cycle의 자연 boundary = Lee 평가 결과**: Cycle 7 후 Lee 평가 결과에 따라 Cycle 8 진행 여부 결정. *자율 cycle은 무한히 가능*하지만 *over-engineering 위험 누적*이 자연 boundary. Lee 평가 = boundary 결정자.

연관:
- L28 (sample-specific meta envelope) → **L29 (coherence ring closing, over-engineering risk-cap)**
- L29 § 2 = Type D directive 넓은 해석 정당화
- L29 § 4 = L27 additive pattern 재사용
- L29 § 6 = 자율 cycle 자연 boundary

**메타 메타 교훈**: directive type 진화 + cycle 진화의 만남 — Type D (saturation override)는 무한 자율 가능하지만 *Lee 평가 받지 못한 cycle*은 *risk-cap 명시 후 작은 patch만*. *진행 가능 영역*과 *진행 위험 영역* 구분이 자율 모드의 정직성.

L18-L29 = **자율 모드 phase + directive type 12 패턴**.

---

### L28. Sample-specific meta envelope 패턴 — narrative 본문 무수정 + 외부 wrap으로 정체성 강조 (Cycle 6 Patch J, 2026-04-29)

**Cycle**: Cycle 5 (Patch I scene-level zoom-in) 후 Cycle 6에서 Trilogy Act II 강조 mechanism. Lee v2 약점 "Act I/II SAT 톤 차이를 더 벌려야"가 Cycle 3 Patch F (line 분리)에서 부분 처리됐지만 *escalation 의미*는 미구현.

**문제**:
- Trilogy 3 acts (1/2/3 accusations) — narrative 본문은 generic SAT/REC scarcity로 처리
- Act II = "두 번째 비난, 깊어지는 굳음" 정체성 — 본문에 표시되지 않음
- 본문을 *probe-aware*로 만들려면 큰 architecture 변경 (probe_id에서 anchor type 추출 등)

**해결 패턴 (sample-specific meta envelope)**:
narrative 본문은 *변경 없음*. Trilogy view (`generate_trilogy_view.py`)에서 Act II 본문 *전후*에 *meta context envelope* (괄호로 묶인 nareator 코멘트) 삽입.

**구조**:
```
Act II epigraph: "이미 한 번 떨어진 비난은..."
↓ NEW preamble: "(첫 비난의 굳음이 풀리지 않은 채, 두 번째 비난이 떨어졌다.)"
Act II narrative 본문 (변경 없음)
↓ NEW echo: "(같은 거리, 같은 자세, 그러나 두 번의 비난이 동시에 머물렀다.)"
```

**교훈**:

1. **Sample-specific 변경 vs general 변경 선택**: Trilogy는 *3 sample*만 영향 (Act I/II/III). general patch (render_story_ko.py 변경)는 96 narrative 모두 영향. Sample-specific changes (trilogy_view.py만 수정)는 *작은 변경 + 큰 효과* — sample 1개에 집중.

2. **Meta envelope vs body change trade-off**: body change (probe-aware narrative)는 architecture 변경. Meta envelope는 *narrative 본문 보존* + *외부 context 추가* — 회귀 위험 zero. Lee 약점 직접 대응이지만 본문 무수정이라 *일반화 패턴*은 약함.

3. **Parenthetical narrator commentary는 표준 문학 기법**: "(괄호 안)" narrator interjection은 *body 외부 voice* — body 흐름을 깨지 않으면서 *meta context*를 더함. Lee 의도 "Act I/II 톤 차이"는 *body line 분리* (Cycle 3 Patch F) + *meta level 차별화* (Cycle 6 Patch J) 둘 다로 처리.

4. **Cycle 패턴 진화**:
   - Cycle 1-4 = dict 확장 (general, all narratives 영향)
   - Cycle 5 = Stage 2.5 추가 (general structural, all non-LOW narratives)
   - **Cycle 6 = Sample-specific meta envelope (특정 sample만, narrative 본문 무수정)**
   - Cycle 7+ = named motif (coordinated pool, all narratives) 또는 narrator distance (architecture)

5. **Lee 약점 = body level + meta level 둘 다 처리 가능**: "Act I/II 톤 차이"는 Cycle 3 (body line 분리) + Cycle 6 (meta envelope) 둘 cycle로 처리. 한 약점이 *여러 차원*에서 해결될 때 *하나의 cycle에 모두 처리하지 않고* 분산이 효과적.

6. **회귀 위험 = 변경 위치 함수**: render_story_ko.py 수정은 96 narrative 영향 → 회귀 위험 高. trilogy_view.py 수정은 Trilogy 3 acts만 영향 → 회귀 위험 低. *변경 위치 선택*이 회귀 위험 결정.

연관:
- L27 (Stage 2.5 zoom-in: additive structural change) → **L28 (sample-specific meta envelope: 더 작은 변경)**
- L28 § 2 = "narrative 본문 보존" 원칙 (architecture 변경 회피)
- L28 § 4 = Cycle 패턴 진화 — general → specific 방향

**메타 메타 교훈**: Lee 약점이 *general 한 표현*이라도 처리 시 *general patch* + *specific patch* 두 layer로 나누면 *회귀 위험 분산* 가능. Cycle 3 (general) + Cycle 6 (specific) 조합 = 약점의 *여러 측면* 동시 처리.

L18-L28 = **자율 모드 phase + directive type 11 패턴**.

---

### L27. Stage 2.5 zoom-in 패턴 — additive structural change without architecture rewrite (Cycle 5 Patch I, 2026-04-29)

**Cycle**: Cycle 4 완료 (Lee v2 약점 5/5 처리 + dict 확장 패턴 종료) 후 Cycle 5 후보 5개 중 #1 (scene-level micro-action) 선택. *omniscient → micro* 전환은 큰 architecture 변경이지만 *Stage 2.5 추가 (additive)*로 작은 변경 유지.

**문제**:
- 모든 narrative가 *omniscient observer* perspective ("사람들은 자리에 굳었다" / "거리는 평소처럼 흘렀다")
- Lee 의도 = *concrete individual action* ("한 사람이 손을 들었다" / "두 발걸음이 한쪽으로 향했다")
- *full omniscient → micro 전환*은 모든 stage 재작성 필요 — 너무 큼

**해결 패턴 (Stage 2.5 zoom-in)**:
*기존 stages 유지* + *Stage 2 끝과 Stage 2 transition 사이*에 *concrete individual action* 1 sentence 삽입.

위치 선택 이유:
- Stage 2 (pressure_arc) 끝부분 → 추상적 압력
- Stage 2.5 (NEW micro-action) → *body-level moment* — pressure가 *visible action*으로 표현됨
- Stage 2 transition → response 분기로 자연 연결

**구조**:
```
Stage 2 끝: "...드문드문 고백이 새어 나왔다. 듣는 사람도, 말하는 사람도 그 무게에 익숙하지 않았다."
Stage 2.5: "한 사람의 눈이 평소보다 길게 한 자리에 머물렀다."  ← NEW zoom-in
Stage 2 transition: "이 흐름 속에서, 사람들은 각자 다른 자리에서 다른 호흡을 가졌다."
```

omniscient (drumdrum 고백 / 익숙하지 않음) → concrete (한 사람의 눈) → omniscient (사람들 각자 다른 호흡) — *zoom-in moment*가 서사 흐름에 자연스럽게 삽입.

**교훈**:

1. **Architecture 변경 vs additive choice**: "Lee 의도 #1 = omniscient → micro"라고 *full architecture rewrite*로 해석 가능. 그러나 *additive insertion*이 더 작은 변경으로 같은 효과 일부. *작은 변경의 큰 효과* — Cycle iteration의 효율 원칙.

2. **Stage 위치 선택이 효과 결정**: Stage 2.5 위치는 의도적 — Stage 2 (pressure 추상) → Stage 3 (response 추상) 사이에서 *body-level concrete*가 *transition moment*로 작동. 다른 위치 (Stage 4.5 등)는 같은 효과 못 줌.

3. **Scenario × micro-action 매핑**: opening/pressure/outcome처럼 micro-action도 scenario별 모티프 ("자루 매듭" for scarcity / "시선" for accusation / "무릎" for sacred). dict 확장 패턴이 micro-action에도 적용 — 4-cycle dict 패턴 *원칙은 그대로* 적용.

4. **LOW_ACTIVITY 별도 branch는 별도 처리**: `_render_narrative_low_activity()`는 자체 5-stage 구조 (signs / rumor / crowd / authority / non-event) — 이미 micro-action 스타일 ("누군가 무엇인가를 말하려다 입을 다물었다") 포함. Patch I 적용 *생략*이 정답 — 재처리 시 over-engineering.

5. **Stage 추가는 architecture 첫 변경**: Cycle 1-4까지는 *기존 stage의 pool 확장*. Cycle 5는 *새 stage 추가* — architecture 변경의 시작점. 그러나 *additive only* 원칙으로 회귀 위험 제로.

6. **narrative 길이 변화 = effect 측정 quick proxy**: Cycle 4 ~960자 → Cycle 5 ~990자 (+30자 / 1 sentence). 정량 변화로 patch 효과 즉시 검증 가능 (정성 평가는 Lee 입력 후).

연관:
- L26 (sharpness coexistence pool 패턴) → **L27 (Stage 2.5 zoom-in 패턴)**
- L27 § 1 = "큰 의도를 작은 변경으로" 원칙 (architecture rewrite 회피)
- L27 § 5 = additive only 원칙 = 회귀 위험 zero (Cycle 1-4 보존 + Cycle 5 추가)

**메타 메타 교훈**: Cycle 5는 *architecture 변경의 첫 cycle*. 그러나 *additive insertion* 패턴으로 큰 변경 위험 회피. 다음 Cycle 6+ = named motif (coordinated pool) / narrator distance — 모두 *기존 architecture에 작은 변경 추가* 패턴 가능.

L18-L27 = **자율 모드 phase + directive type 10 패턴**.

---

### L26. Sharpness coexistence pool 패턴 — Lee 약점 verbatim 매핑의 정밀 사례 (Cycle 4 Patch G, 2026-04-29)

**Cycle**: Type D directive (saturation override) 후 Cycle 3 (Patch D/E/F). Cycle 3 미해결 약점 = "P10 REC accusation 날카로움 부족" (Lee v2 verbatim). Cycle 4에서 *기존 5 line + 신규 5 line = 10 pool* 패턴으로 처리.

**문제**:
- Lee 의도 = "accusation REC도 *날카로움이 살아 있는* recovery"
- 기존 SCENARIO_RECOVERY_POOLS["accusation"] 5 lines = 모두 "풀려나는 / 옅어지는 / 흩어지는" tone
- 다른 scenario REC (scarcity / sacred)와 톤이 수렴 — accusation의 *날카로움* 표현 누락

**해결 패턴 (sharpness coexistence)**:
*"회복 명시 + 잔재 명시"* 한 문장 안에 동시. 예:
- "**손가락질의 끝은 거두어졌지만**, 그 끝에서 떨어진 **잔영은 거리 위에 잠시 머물렀다**."
- "**이름이 거리에서 흩어졌어도**, 그 이름이 처음 떨어진 자리는 한 박자 더 무거운 결을 지녔다."
- "**비난의 무게는 풀렸지만**, 그 무게가 닿았던 어깨에는 옅은 자국이 남았다."

**구조**:
- Front clause: 회복 (기존 REC tone 유지)
- Conjunction: "지만" (대비)
- Back clause: 잔재 (accusation sharpness 표현)

**교훈**:

1. **Lee 약점 verbatim → patch tone 매핑**: "accusation 날카로움이 약하다" → sharpness coexistence pool. 약점이 *명시한 absence*가 patch가 *명시한 presence*가 되도록 매핑.

2. **Pool 확장 vs 교체 선택**: 기존 5 line은 "분명한 회복" 사례 (Lee가 비판하지 않은 영역)에 적합 — *교체*하면 over-correction. *추가*가 정확. 10 line 중 50%는 기존 tone, 50%는 sharpness coexistence — hash 분산이 probe별 적합한 line 선택.

3. **Sharpness coexistence는 다른 scenario에도 적용 가능**: scarcity REC ("자루는 채워지지 않았지만 의심의 무게는 풀렸다"), sacred REC ("기도가 끝났지만 침묵의 결은 남았다") — 모든 scenario REC에 *recovery + residue* 패턴 가능. **Cycle 5 후보**.

4. **대칭성 회복은 cycle 자연 종착점**: Cycle 1 = REC 추가, Cycle 3 = SAT/MIXED 추가, Cycle 4 = PARTIAL 추가. 4 outcomes (REC/SAT/MIXED/PARTIAL) × 3 scenarios = 12 pools 완성. 다음 Cycle은 *구조적 변경* 필요 (단순 dict 확장 패턴 마무리).

5. **Hash 분산 효과**: 5 → 10 pool은 probe collision 20% → 10%, *동시에* 신규 line으로 매핑되는 probe 비율도 증가 (50% 가능). 즉 *기존 변경 보존* + *신규 효과 확산* 모두 달성.

연관:
- L24 (Type C scoped patch) → L25 (Type D saturation override) → **L26 (sharpness coexistence pool 패턴)**
- L26 § 1 = Lee verbatim 매핑이 patch 정밀도의 핵심 (L24 § 1 lessons에서도 동일)
- L26 § 4 = 대칭성 회복 = cycle 자연 종착점 (다음은 architecture 변경)

**메타 메타 교훈**: Cycle iteration이 *dict 확장 패턴*에서 시작해 *대칭성 회복*에서 자연 종료. 다음 Cycle은 *새 architecture* (scene-level / named motif / narrator distance) — Cycle 5+는 이전 4 cycles와 다른 작업 종류.

L18-L26 = **자율 모드 phase + directive type 9 패턴**.

---

### L25. Saturation override directive — "외부 입력 대기 중에도 자율 개선 계속" 패턴 (Type D, 2026-04-29)

**Cycle**: Type C (Lee Gate 1 v2 후 Cycle 2 GO, L24) 후 96 narrative regen + audit + saturation 재진입. Lee가 새 단문 directive 보냄: "Saturation에 도달해도 계속해서 Renderer 개선해". 이전 Type B-2 §8 stop condition을 *renderer 개선 한정*으로 해제.

**Type D directive 특징** (Type B-2와 비교):

| Aspect | Type B-2 | Type D (this) |
|---|---|---|
| Saturation 시 행동 | 정지, 외부 입력 대기 | **자율 개선 계속, 외부 입력 *병행* 대기** |
| 자율 가능 범위 | §5.3 5 항목 (결과 수신 후만) | **renderer 개선 작업 (외부 입력과 무관)** |
| 새 작업 정의 | "한 번에 한 분기만" | **iterative cycle (Cycle 2 → 3 → 4 ...)** |
| 외부 입력 영향 | 결과 수신이 작업 트리거 | **결과 수신은 *방향 조정* 신호** (작업 중단 신호 아님) |
| stop condition | saturation OR forbidden_now exhaustion | **새 directive 또는 명시적 정지 신호 도착 시** |

**교훈**:

1. **Saturation 정의의 가변성**: Type B-2 §1.2 "내부 자율 작업 = 종료"는 *그 시점의 saturation 인식*. Lee가 "계속 개선해"라고 추가 directive 보내면 saturation 재정의됨. saturation은 *static stop signal*이 아니라 *current Lee 판단*에 의존.

2. **Cycle 진화는 same renderer 안에서도 무한 가능**: 매 Cycle은 *기존 pool 확장 또는 분기 추가* — Cycle 2 (outcome-conditional dict) → Cycle 3 (scenario × outcome 분기 + pool size 3→5) → Cycle 4 (scene-level / named motif / narrator distance). 각 Cycle은 *이전 Cycle의 한계* 직접 대응.

3. **Hash collision은 pool size 함수**: variant_pick(probe_id, slot, pool) deterministic. Pool size 3 → 33% collision, size 5 → 17%, size 7 → 14%. Trilogy Act I/II 같은 outcome+scenario 조합에서 hash collision이 *동일 line* 출력 → pool 5+ 확장이 표준 처리.

4. **Cycle별 patch 명명 + 누적**: A/B/C (Cycle 2) → D/E/F (Cycle 3) → G/H/... (Cycle 4). 각 patch가 *독립 검증 가능* + *회귀 안 일으키도록 additive*. 이전 Cycle 변경은 그대로 보존.

5. **scenario × outcome 분기는 dict 패턴 표준**: SCENARIO_RECOVERY_POOLS (Cycle 1) → SCENARIO_SATURATION_POOLS + SCENARIO_MIXED_POOLS (Cycle 3) → 미래 PARTIAL/LOW_ACTIVITY × scenario까지 확장 가능. dict[scenario][outcome] 2D 매트릭스가 향후 확장 표준.

6. **Lee 약점 verbatim → patch 매핑이 자율 개선의 정밀도**: Cycle 2 = Lee 우선 개선 3 (verbatim) → Patch A/B/C. Cycle 3 = Lee v2 약점 미해결 항목 (Trilogy Act I/II 차이 / accusation 날카로움) → Patch D/E/F. 자율 개선이 "랜덤 변경"이 아닌 *Lee 표명 약점에 대한 직접 대응* 구조.

연관:
- L24 (Type C: 외부 평가 부분 통과 + scoped patch) → **L25 (Type D: saturation override + iterative cycle)**
- L25 § 1 = Type D는 "지금까지의 saturation 정의 무효화" — Lee 판단이 stop condition을 결정
- L25 § 5 = scenario × outcome 분기 dict 패턴 = 향후 PARTIAL/LOW_ACTIVITY 확장 시 동일 표준

**메타 메타 교훈**: directive type 진화 — A (새 작업) → B (forbidden 명시) → B-2 (외부 판독 분기) → C (외부 평가 partial + scoped patch) → **D (saturation override + iterative)**. 각 단계는 Claude Code의 *자율성 boundary*를 재정의. saturation은 동적이며, Lee 판단이 boundary 결정.

L18-L25 = **자율 모드 phase + directive type 8 패턴**.

---

### L24. Lee Gate 1 v2 부분 통과 → Cycle 2 patch 즉시 GO 패턴 — directive type C (외부 평가 후 partial pass + scoped patch) (2026-04-29)

**Cycle**: Type B-2 directive 도착 후 Lee가 Gate 1 v2 직접 평가 결과 (`LEE_RENDERER_GATE1_V2_FILLED_RESPONSE.md`) + 장기 roadmap (`WITNESS_LONG_RANGE_NEXT_ACTIONS_2026-04-29.md`) 두 파일 동시 보냄. 외부 평가가 "부분 통과"였고 directive가 즉시 Cycle 2 GO 결정.

**Type B-2 case A → Type C (external partial pass) 진화**:

| Stage | Pattern |
|---|---|
| Type B-2 case A 정의 (L23) | "Gate 1 v2 결과 명확" → Cycle 2 plan |
| 실제 Lee 응답 도착 | "2/5 good, 2/5 salvageable, 1/5 fail" → 부분 통과 |
| 새 directive 추가 | `WITNESS_LONG_RANGE_NEXT_ACTIONS` — Branch C eval + Renderer Cycle 2 *동시* GO |
| 자율 작업 범위 | renderer code patch + 5 sample 재생성 + Lee 평가 양식 |

**Type C directive 특징**:
- 외부 평가 결과가 "binary PASS/FAIL"이 아닌 *분류된 약점 list*
- directive가 *우선 개선 3* 항목 명시 (phrase de-template / outcome rhythm / LOW_ACTIVITY branch)
- "둘 다 통과할 때만" 조건문 — Branch C external eval AND renderer Cycle 2 둘 다 PASS 필요
- HOLD 상태와 GO 상태 *동시* 존재 (creative asset pack HOLD + Cycle 2 GO)

**교훈**:

1. **Lee 약점 verbatim 보존이 patch 정확성**: Lee가 "그리고 그 모든 결은 결국 한 모양으로 굳어 갔다" 같이 *정확한 stock phrase* 인용. 이 verbatim을 grep해 정확한 변경 대상 식별 가능. H5 (Lee verbatim 보존)는 진단 정확성에 직접 기여.

2. **Patch 범위 = directive에서 명시된 우선 개선 3개만**: Lee가 우선 개선 3 명시 → Cycle 2 = Patch A/B/C 정확히 매핑. 이를 넘어선 작업 (scenario × outcome × sentence-level rhythm)은 Cycle 3 후보로 명시 미루기. *patch가 plan과 매핑되는 일대일 구조*가 검증 시 효율.

3. **outcome-conditional dict 패턴은 "stock phrase 차단" 표준 처리**: flat list `[a, b, c]` → dict `{outcome: [...], outcome2: [...]}` + helper `_pick_by_outcome(probe_id, fs, slot)`. 5 line refactor로 cross-outcome stock phrase 누설 차단.

4. **전용 branch 패턴 (LOW_ACTIVITY)**: 기존 5-stage pipeline에서 "1/5 fail" 분류된 outcome이 *근본적 다른 처리* 필요할 때 — 동일 pipeline의 pool 확장이 아닌 *전용 함수 분기* (`_render_narrative_low_activity()`). Lee 정의 5 요소 (작은 징후 / 확산 안 되는 rumor / 반응 안 하는 crowd / 무심한 authority / 사건 못 됨)를 5 stage로 매핑.

5. **before/after diff doc은 Lee 평가 효율화 도구**: 5 sample × Cycle 1 vs Cycle 2 비교 표가 Lee가 v3 평가 시 v2 약점이 해결됐는지 직접 매칭 가능. Lee 평가 시간 단축 + 평가 *정확성* (v2 약점 → v3 변화 1-to-1) 향상.

6. **"둘 다 통과" 조건문 = saturation 방지 보호 장치**: WITNESS는 Branch C (구조 검증) + Renderer (전달 검증) 두 축. 둘 중 하나만 PASS면 *부분 자산화*만 가능. Lee directive § 8 "Branch C는 구조의 검증이고, renderer는 전달의 검증이다. 둘 중 하나만 통과해도 부족하다" — 한 축 결과를 다른 축으로 over-extrapolate 차단.

연관:
- L22 (Type B forbidden 명시) → L23 (Type B-2 외부 판독 분기 정의) → **L24 (Type C 외부 평가 부분 통과 + scoped patch)**
- L24 § 2 patch-plan 일대일 구조 = directive § 3.1 우선순위 1-3과 정확히 매핑
- L24 § 4 전용 branch 패턴 = 기존 pipeline 한계가 명확할 때 적용 (LOW_ACTIVITY 한정)
- L24 § 6 "둘 다 통과" = WITNESS 2축 검증 (구조 + 전달) 보호

**메타 메타 교훈**: directive type 진화 — Type A (새 작업) → Type B (forbidden 명시) → Type B-2 (외부 판독 분기) → Type C (외부 평가 partial + scoped patch). 외부 평가의 *granularity*가 directive type을 결정한다. binary 평가 → Type B-2, 분류된 약점 → Type C.

L18-L24 = **자율 모드 phase + directive type 7 패턴**.

---

### L23. Type B-2 directive — 외부 판독 분기 사전 정의 + Claude Code 재개 규칙 (POST_TYPE_B_EXTERNAL_GATE_DIRECTIVE, 2026-04-29)

**Cycle**: Type B (NEXT_STEPS_AFTER_AUTONOMOUS_ROUND, L22) 후 자율 모드 saturation 5 LOOPs 연속. Lee가 새 directive (`WITNESS_POST_TYPE_B_EXTERNAL_GATE_DIRECTIVE.md`) 보냄. 형태가 Type B 강화 버전 — Type B-2.

**Type B vs Type B-2 비교**:

| Feature | Type B (L22) | Type B-2 (this) |
|---|---|---|
| Forbidden 명시 | ✓ | ✓ (유지 + 강화) |
| Saturation 인지 | ✓ | ✓ (5 LOOP No 자가질문 확인) |
| 새 작업 시작 | 외부 판독 prep만 | **외부 판독 분기 사전 정의** |
| 외부 결과 수신 후 | (직접 받아 처리) | **4 경우 자동 분기 (A/B/C/D)** |
| 분기별 first action | 직접 결정 | **plan doc 작성 → 실제 작업** 순 |

**Type B-2의 새 패턴**:
- 외부 결과 수신 시 *Claude Code가 자율 재개* 가능 (이전: Lee directive 추가 필요)
- 4 경우 (A: Gate 1 명확 / B: GPT-5.5 강 긍정 / C: 애매 / D: 매우 부정) 사전 정의
- 각 분기별 first plan doc 명시 (RENDERER_CYCLE_2_PLAN / BRANCH_C_LOCK_DECISION / CREATIVE_ASSET_PACK_PLAN / RENDERER_CORE_REPAIR_PLAN)
- "한 번에 한 분기만 / 결과 과대해석 금지 / forbidden_now 유지" 재개 규칙 명시

**교훈**:

1. **Pre-stub 작성은 over-engineering**: directive § 5.2가 "결과 수신 → 판정 → plan 작성 → 작업" 순서를 명시. *결과 받기 전* plan stub 작성은 LP 5.2 위반. 자율 가능 영역 = lessons + auto-memory 영구 자산화만.
2. **Type B-2 = "ready to resume" directive**: Lee 입장에서 게이트 입력 2개 (Gate 1 v2 + GPT-5.5 send) *기다리는 동안* Claude Code의 *재개 protocol* 미리 lock. 결과 도착 시 추가 directive 없이 자율 재개.
3. **자율 가능 범위 directive에서 명시**: § 5.3 "renderer cycle 2 plan / Branch C lock / creative asset pack plan / before/after / variation review" — 결과 수신 후 *이 5 항목만* 자율. 새 설계 축은 여전히 금지.
4. **자율 모드 phase 5 phase로 확장**:
   - Pre-directive (falsification)
   - Directive-driven Type A (implementation)
   - Post-directive autonomous (영구 자산화)
   - Post-saturation Type B (forbidden 명시 + 멈춤 결정)
   - **Post-Type-B Type B-2 (외부 판독 분기 사전 정의 + ready-to-resume protocol)**

5. **Saturation의 정직한 인지**: directive § 8 명시 — "지금은 정말로 의미 있는 자율 작업 0건 상태". Type B-2는 Lee가 saturation을 *재확인*하고 *대신 외부 입력 우선순위* 설정하는 형태.

**메타 메타 교훈**: directive type 진화 패턴 — Type A (새 작업) → Type B (forbidden 명시) → Type B-2 (외부 판독 분기 사전 정의). 각 단계는 *자율 모드의 적합 영역*을 좁힘과 동시에 *재개 protocol*을 명확히 한다. directive는 통제가 아니라 *재개 가이드*.

연관:
- L18 (3 phase 종합) → L21 (Lee Gate 자율 cycle) → L22 (Type B forbidden 명시) → **L23 (Type B-2 외부 판독 분기 정의)**
- L23 § 1 directive § 5.3 자율 가능 5 항목 = Type B-2의 *허용된 자율 작업*
- L23 § 5 자율 가능 영역 = 영구 자산화 + plan doc (결과 수신 후만) + variation review

L18-L23 = **자율 모드 phase + directive type 6 패턴** (L24 추가로 7 패턴, 위쪽 참조).

---

### L22. Saturation 후 directive는 "멈춤 결정"으로 작동 — directive가 *forbidden 명시* 형태 (NEXT_STEPS_AFTER_AUTONOMOUS_ROUND, 2026-04-28)

**Cycle**: J-Beta + Gate 1 자율 cycle 1+2+3 후 자율 모드 saturation 명시. Lee가 추가 directive 보냄 — `WITNESS_NEXT_STEPS_AFTER_AUTONOMOUS_ROUND.md`. 이 directive의 *형태*가 이전과 다름.

**기존 directive pattern**:
- `WITNESS_STORY_OUTPUT_MVP_PLAN.md` — 새 작업 시작 (8 phase 구현)
- `WITNESS_PYTEST_IMPROVEMENT_PLAN.md` — 새 작업 시작 (3-tier 도입)
- `WITNESS_CREATIVE_IP_TRACK_IMPROVED_DIRECTIVE.md` — 새 작업 시작 (J-Alpha 8 Steps)

**새 directive pattern (NEXT_STEPS_AFTER_AUTONOMOUS_ROUND)**:
- "자율 가능 작업 거의 소진" 진단
- forbidden_now 7 항목 명시 (density-aware / 70+ labeling / style profile / IP mode / Van Gogh / engine touch / Branch C 새 slice)
- 새 작업 = "외부 판독" (Lee Gate 1 v2 + GPT-5.5 send) + 멈춤
- "더 만들기보다 진단" 원칙

→ Directive가 *멈춤 결정*. saturation phase 인지 + 다음 phase로 transition signal.

**교훈**:

1. **Directive의 두 형태**:
   - **Type A — 새 작업 시작**: 8 phase 구현, 3-tier 도입 등. 자율 모드는 implementation phase로 진입.
   - **Type B — 멈춤 결정 / forbidden 명시**: 자율 가능 항목을 *지금 하지 마*. saturation 시그널 + 다음 phase로 transition.

   J-Alpha/J-Beta directive는 Type A. NEXT_STEPS_AFTER_AUTONOMOUS_ROUND는 Type B.

2. **Forbidden_now list = 자율 가능 + value high 항목**: 자율 가능하지 *않으면* 명시적 금지 불필요. 이 list는 "Claude가 자율로 진행할 수 있다는 걸 Lee가 알고 있고, *그래서* 막고 있다" 신호.

3. **"더 만들기보다 진단"** = creative track 핵심 원칙: 외부 (인간/다른 AI) 판독이 다음 진전. internal 작업은 marginal.

4. **Saturation 명시는 가치 있음**: Type B directive가 Lee 입장에서 "자율 모드 *그만 두라*"가 아니라 "자율 모드가 잘 작동했고 *외부 판독* 다음 단계"라는 인지. 이게 자율 모드의 *완료 신호*.

5. **자율 모드 4 phase로 확장** (L18 § 메타 메타 교훈 갱신):
   - Pre-directive (falsification, HARNESS H1+H4)
   - Directive-driven (implementation, Type A)
   - Post-directive autonomous (영구 자산화, polish)
   - **Post-saturation directive (Type B, 멈춤 결정 + 다음 phase 시그널)**

**메타 메타 교훈**: Lee directive가 forbidden을 명시하는 것은 *제약*이 아니라 *해방*. 자율 모드는 forbidden 안에서 진단/외부 판독에 집중 가능. "Type B directive 후 자율 진행 = 외부 판독 prep + 영구 자산화 polish".

연관:
- L18 §5 자가질문 ("다음 세션 영향?") → Type B directive 시그널
- L21 (Lee Gate 자율 cycle) → Type B directive의 *예외* 케이스 (Gate 1 자율 fill 가능)
- L20 (FAIL → 자율 디버깅) → Type A directive 안에서 작동

L18-L22 = **자율 모드 phase + directive type 5 패턴**.

---

### L21. Lee Gate 자율 cycle 패턴 — Lee 직접 평가가 어려울 때 (J-Beta + Gate 1 자율 cycle, 2026-04-28)

**Cycle**: Lee directive `WITNESS_CREATIVE_IP_TRACK_IMPROVED_DIRECTIVE.md` § 4.4 Step A1: "Renderer Diagnosis Lee Gate 1 입력 필요". 그러나 Lee가 직접 평가 안 하고 "Gate 1 루프 진행"으로 directive 변경.

자율 진행:
1. **자체 진단 (Claude bias)**: 5 sample + trilogy view 직접 검토, RENDERER_DIAGNOSIS_ALPHA.md 표 자체 채움. "v1 (자율)" 명시 — Lee 직접 평가 도착 시 "v2 (Lee)"로 갱신 가능.
2. **자율 우선 개선 1+2+3 적용**: scarcity opening 3→5 / cross-scenario REC differentiation / anchor signature lines for trilogy
3. **결과 자체 검증**: 119 tests / 96/96 audit / 실제 prose 비교

→ Lee 직접 평가 *없이도* 가시 quality 향상. "Lee가 채울 표를 자체 채운 후 결과 보여 줌" 패턴.

**교훈**:

1. **"Lee Gate 입력 대기"의 두 모드**:
   - **모드 A — Lee 직접 평가 필수**: 가설 검증 (PASS/FAIL 결정), 큰 방향 결정
   - **모드 B — Lee 평가 선택적, 자율 진행 가능**: renderer 미세 개선, anchor 선택, IP 자산 폴리싱

   J-Alpha Gate 2 (variation IP 자산 가치)는 모드 A. Gate 1 (renderer 진단)은 모드 B로 전환됨.

2. **"v1 자율 / v2 Lee"** 분리 표기로 transparency 유지: 자체 진단 결과를 Lee에게 보여 주되, *내가 Claude bias로 채웠음* 명시. Lee가 동의/수정 가능.

3. **Lee directive의 미묘한 변화에 민감해야**: "Gate 1 루프 진행"이라는 한 줄이 모드 A → 모드 B 전환 신호. 자율 cycle 가능 영역 확장.

4. **자율 우선 개선은 진단 직후 즉시 실행**: 3 우선 항목을 다음 LOOP 분산 안 하고 1-2 LOOP 안에 모두 적용. 효과 측정 즉시.

5. **수정 효과는 *cross-sample* 비교로 검증**: P4 sacred REC vs P10 accusation REC 직접 비교 → 분리 확인. 단일 sample 검토는 부족.

6. **자율 progress doc + meta cleanup이 평형 유지**: Gate 1 자율 cycle 도중 J_BETA_PROGRESS.md 갱신, NOVEL_TONE_GUIDE_ALPHA.md 갱신, README J-Beta 섹션 — 모두 *Lee 다음 세션 시작 시 보일 것*.

**메타 메타 교훈**: Lee directive 따르기 = *directive의 표면 의도* + *implicit 모드*. "Gate 1 루프"라는 짧은 phrase는 명시적이지 않지만 implicit 모드 전환. 이걸 자율 모드가 catch하면 가치 큼; 못 catch하면 idle wait.

L18 (3-phase 자율 모드) + L19 (anchor diversity) + L20 (FAIL → followup) + L21 (Lee Gate 자율 cycle) = **directive-driven 자율 모드 4 패턴**.

---

### L20. 자율 디버깅 cycle은 FAIL signal 직후 가장 효과적 (J-Alpha follow-up 메타, 2026-04-28)

**Cycle**: J-Alpha 5-variation demo에서 Van Gogh→sacred 5/5 PARTIAL FAIL 발생. Lee Gate 응답 대기 *없이* 자율 디버깅 4 단계:

1. **진단** — `test_anchor_diversity.py` 작성 (50 lines, ~5 min). 2 후보 cell 측정.
2. **발견** — scarcity_high_density cell이 baseline과 동일 outcome 분포 reproduce (3 distinct).
3. **통합** — selector에 새 anchor 추가 (FAIL 후보 transparency 유지).
4. **검증** — 3 anchor demo 재생성, 두 cell 같은 시퀀스 reproduce 확인 (filename conflict bug fix).
5. **문서화** — `PETER_TWO_ANCHOR_COMPARISON.md` 작성, density 효과 stage별 분석, J-Beta plan.

→ FAIL → diagnostic → 발견 → 통합 → 검증 → 문서화 = ~30 min cycle. Lee Gate 응답 quality 향상 (기존 1 anchor만 vs 2 anchor + FAIL transparency).

**교훈**:

1. **FAIL signal은 자율 디버깅의 적합 trigger**. PASS signal은 stop, FAIL은 follow-up.
2. **Diagnostic script는 작은 cost로 큰 가치**: 50-line script가 anchor 후보 결정의 ground truth 제공.
3. **Branch C measurement data를 anchor library 후보로 재사용**: 새 measurement 비용 0.
4. **FAIL 후보 보존 = transparency**: vangogh_sacred_baseline을 selector에서 제거 안 함. "왜 sacred가 anchor로 부족한가"가 J-Alpha 학습.
5. **Filename conflict 같은 마이너 bug는 즉시 발견 시 수정**: peter_*  접두사 중복 → anchor_id 전체 사용. 작은 patch.
6. **자율 follow-up은 J-Beta 진행을 막지 않음**: Lee Gate 2 응답 받기 전이라도 alternative 후보 측정 → reveal해 두면 Lee 결정 quality 향상.

**메타 메타 교훈**: Lee directive 따라가는 phase + 자율 follow-up phase 사이 명확한 trigger 있음.
- Directive phase end signal: 8 Steps 모두 완료
- Self-followup trigger: 명시 FAIL 또는 partial pass
- Self-followup end: alternative 발견 + 통합 + 문서화
- Post-followup phase: 영구 자산화 (이번 LOOP)

L17 (pytest 3-layer fast diagnostic) + L19 (cell-level diversity) + L20 (FAIL → followup cycle) = 같은 패턴의 3 lesson.

---

### L19. Anchor diversity는 cross-seed sensitivity 높은 cell 선택이 핵심 (J-Alpha follow-up, 2026-04-28)

**Cycle**: J-Alpha 5-variation demo에서 Van Gogh→sacred substitute가 5/5 PARTIAL (FAIL). 자율 follow-up으로 대체 anchor 후보 빠르게 측정 (`test_anchor_diversity.py`).

**측정 결과**:
| Anchor 후보 | 5-seed outcome 분포 | distinct count |
|---|---|---|
| Peter scarcity baseline | SAT 2 / REC 2 / PARTIAL 1 | 3 (READY) |
| accusation baseline | SAT 4 / PARTIAL 1 | 2 (MARGINAL) |
| Van Gogh→sacred | PARTIAL 5 | 1 (FAIL) |
| **scarcity high_density** | **SAT 2 / REC 2 / PARTIAL 1** | **3 (READY) ← 자율 발견** |

scarcity 시나리오 + single accusation + 높은 density 조합이 *Peter baseline과 같은 outcome 분포 패턴*을 reproduce. 같은 메커니즘이 다른 density에서 작동.

**교훈**:

1. **Anchor diversity는 cell-level property**: scenario type만으로는 불충분. 같은 scenario (scarcity) 안에서도 *cell* (density level)이 sensitivity 결정.
2. **Branch C cross-seed 측정 데이터를 anchor 선택에 직접 활용**: 이미 measure된 cross-seed 분포 (Branch C 1차 evidence v4.4)에서 *modal 분포 다양한 cell* = anchor 후보. 새 측정 비용 0.
3. **자율 follow-up의 가치**: J-Alpha FAIL signal (Van Gogh substitute 5/5 동일) 받자마자 자율로 대체 후보 측정 → READY anchor 확보. Lee directive 없어도 J-Beta 진행을 막지 않음.
4. **선택자에 FAIL 후보 보존**: vangogh_sacred_baseline을 selector에서 제거하지 않고 *transparency*로 유지. "왜 sacred가 anchor로 부족한가"가 J-Alpha 학습 자체.
5. **Quick diagnostic script가 valuable**: `test_anchor_diversity.py` 같은 diagnostic 스크립트 (작은 측정, 빠른 출력)가 자율 follow-up을 가능하게. 풀 simulation에 비해 cost 1/100, 가치는 동급.

**메타 교훈**: J-Alpha 같은 "1차 증명" 단계의 부분 실패는 **곧바로 자율 디버깅** 영역. Lee directive 받기 전에 Claude가 alternative 후보 측정해서 reveal해 두면 Lee Gate 응답 quality 향상.

연관: L17 (pytest 3-layer)의 fast diagnostic 패턴이 여기에도 적용. cell-level diagnostic test가 곧 anchor library 후보 generator.

---

### L18. 자율 모드 영구 자산화 cycle은 explicit Lee directive를 따라가는 것이 가장 효과적 (2026-04-28 종합 메타 학습)

**Cycle**: 이번 세션 ~50 LOOPs 진행. 처음 ~26 LOOPs는 Branch C autonomous 진행 (HARNESS H1/H4 self-falsification cycle). 이후 ~24 LOOPs는 explicit Lee directive 따라가기:
- `WITNESS_STORY_OUTPUT_MVP_PLAN.md` → 9-phase Story MVP 구현
- `WITNESS_STORY_OUTPUT_NEXT_STEPS.md` → Phase 4 entry + acceptance v2
- `WITNESS_PYTEST_IMPROVEMENT_PLAN.md` → 3-layer test 구조 즉시 구현

**관찰**:

| 진행 모드 | 특징 |
|---|---|
| Pre-directive autonomous | Branch C 1차 evidence 확장 → cross-seed walkback (HARNESS self-falsification 2 cycles) |
| Lee directive cycle | Story MVP 구현 → Phase 2 변주 → Branch C × Story 통합 → Pytest 3-layer |
| Post-directive autonomous | 영구 자산화 (paper sync, README, lessons, audit, demo, CLAUDE.md/DESIGN.md, auto-memory) |

**교훈**:

1. **Pre-directive autonomous는 falsification 작업에 적합**: HARNESS H1 (null hypothesis), H4 (negative findings), H8 (single-seed warns)이 자율 모드에서 self-discovery됨. 외부 직시가 없을 때도 honest 진행 가능.
2. **Directive-driven cycle은 implementation 작업에 적합**: 9-phase Story MVP는 명확한 phase 별로 합리적 진행. 자율 모드만으론 over-engineering 위험. Lee directive가 *어디까지 가야 하는가*의 가드레일.
3. **Post-directive autonomous는 영구 자산화에 적합**: 큰 결과 도달 후 *다음 세션이 빠르게 컨텍스트 잡도록* 만드는 작업. 새 결과 안 만들고 기존 결과를 영구 lock. README/lessons/paper/auto-memory 일관성 동기화.
4. **Cycle 사이 transition 신호**:
   - Lee directive 도달 → autonomous에서 directive로 전환
   - Directive phase 완료 + acceptance PASS → directive에서 post-directive autonomous로 전환
   - Post-directive에서 새 자산 추가 점차 marginal → idle 신호 명시
5. **자율 모드 saturation 인지**: "이 LOOP에서 한 일이 다음 세션 컨텍스트에 영향 줄까?" 자가질문. 답이 No이면 saturation. 안전한 명시 + Lee directive 대기.
6. **Cleanup은 영구 자산화의 일부**: docs/story 6 archive (10→4 canonical), Branch C working 18 archive 같은 작업이 *next session readability 가치*. Cleanup ≠ deletion, *hierarchical 정리*.

**메타 메타 교훈**: 자율 모드는 *모든 cycle 단계에 적합*하지 않음. 단계마다 적합한 mode가 다름. Lee의 explicit directive가 도착하면 그것이 single source of truth. 명시 directive 없을 때만 자율 판단.

**연관**:
- L13 (seed=0 unpredictable): pre-directive autonomous 발견
- L15 (Story 3-stage): directive-driven 구현
- L16 (paper sync): post-directive 영구 자산화
- L17 (pytest 3-layer): directive 즉시 구현 (Lee directive 도달 후 한 turn에 phase 1-4)

이 4 lessons은 같은 세션의 다른 phase 결과. 어떤 phase에서 어떤 종류의 학습이 나오는지 패턴 추적 가능.

---

### L17. Pytest 3-layer (fast/domain/full)는 변경 단위 = 검증 단위 일치시키는 도구 (LOOP fire 14, 2026-04-28)

**Cycle**: Lee directive `WITNESS_PYTEST_IMPROVEMENT_PLAN.md` — "1500개 pytest를 모든 변경마다 돌리는 것은 과검증". 3-layer 구조로 분리:
- Fast: `tests/test_story/` (95 tests, 0.23초) — template/regex/threshold 변경 직후
- Domain: 관련 areas (수십초) — 여러 단계 변경
- Full: 1500 tests (67초) — milestone, engine touch

**측정 결과**: Fast layer = full suite 대비 **290배 빠름**. 0.23초 vs 67초.

**교훈**:

1. **변경 단위 = 검증 단위 원칙**: template 1줄 수정에 1500 tests = 비대칭. fast layer는 이 비대칭 해소.
2. **Semantic golden tests는 brittleness를 회피**: 완전 일치 비교는 한 줄 수정마다 깨짐. "saturation = 굳/머물렀다/멈춘 키워드 중 하나" 같은 의미 단위 비교가 robust. 핵심 의미 키워드 셋이 깨지면 정말 outcome differentiation이 망가진 것.
3. **Layer 분리는 명령어가 아니라 *의도* 분리**: 같은 pytest 명령이지만 어떤 디렉토리/marker로 돌리는가는 *어디까지 무결성 보장 받고 싶은가* 의도. README에 "언제 어떤 layer 돌리는가"를 명시 (해당 운영 규칙)하는 게 핵심.
4. **Fast layer는 변경 *직후 즉시* 돌릴 수 있어야 의미**: 0.23초면 사람이 직접 변경 직후 명령 입력해도 자연스러운 피드백 사이클. 30초면 컨텍스트 끊김. 1분이면 "다음에 돌리지" 미루게 됨.
5. **Helper 함수 unit test는 작지만 매우 가치**: `test_story_helpers.py`에서 `josa()`, `role_plural_ko()` 같은 helper 1줄 함수도 단위 test. 이게 future regression의 가장 흔한 vector. 작은 helper에 작은 test.
6. **Phased rollout이 적합**: Plan 5 phases 모두를 한 cycle에 시도하지 말고, 1-3 (test 신설) → 4 (README 가이드) → 5 (실사용)로 나누면 명확. 이번엔 1-4를 한 turn에 했지만 검증 후 phase 5는 Lee가 자연스럽게 사용 시 검증.

**메타 교훈**: Lee가 "1500개 매번 돌리는 게 비효율"이라 지적했을 때, "그럼 줄여야 한다"가 아니라 "분리해서 돌릴 수 있게 한다"가 맞는 답. 안전망 *제거*가 아니라 안전망 *layer화*가 정답.

연관: HARNESS H8 (single-seed conditioning warns)도 같은 패턴 — "여러 seed 다 돌려야 하니 부담"이 아니라 "ensemble layer를 별도로 두고 single-seed는 illustration" 구조.

---

### L16. Paper draft 동기화는 Appendix가 아니라 main body (§6/§7) 변경이 핵심 (LOOP fire 10, 2026-04-28)

**Cycle**: Branch C 1차 evidence + Story output 작업 완료 후 paper draft에 Appendix G/H 추가만 했었음. LOOP fire 10에서 Lee directive 없이 자체 판단으로 paper main body 동기화 — §6 8→10 findings (6.9 configuration sensitivity / 6.10 narrative renderability), §7 3→4 sections (7.4 single-seed inadequacy methodology contribution), §7.2 limitations 갱신, Abstract 5→7 findings + "1500+ tests" + "v2.0 narrative witness layer".

**교훈**:

1. **Appendix만 추가하면 paper는 inconsistent**. 외부 reviewer가 §6 (5 findings) 읽고 Appendix (10 finding 분량의 내용) 읽으면 disconnect 느낌. Appendix는 *상세 backup*이고 main body가 *primary statement*.
2. **새 발견의 paper 통합은 4 location 모두 필요**:
   - Abstract (high-level)
   - §6 Key Findings (논리적 위치)
   - §7 Discussion / Limitations (caveats)
   - Appendix (detail backup)
3. **방법론 기여는 §7 별도 섹션 가치 큼**: Cross-seed walkback이 "Branch C 1차 evidence"의 by-product가 아니라 *contribution to ABM validation methodology*로 §7.4 별도 섹션으로 격상. 같은 작업도 framing에 따라 paper 가치 다름.
4. **Paper line 증가는 quality proxy 아님**: 460→490 lines 큰 증가 아니지만 main body integration이 *meaningful* 증가. 양보다 *어디에* 추가됐는지가 중요.
5. **Lee directive 없이 자율 paper sync**: paper 작업도 자율 모드 가능 영역. 단, *새 결과 작성*이 아니라 *기존 결과 통합*만. 새 결과 작성은 Lee directive 영역.

연관: HARNESS H4 ("What could still be wrong") + H8 (single-seed conditioning) 모두 paper §7에 통합됨. HARNESS 자체가 paper-grade contribution으로 격상 가능.

---

### L15. Story output layer는 3단 분리 + IR-level 의미 변환이 핵심 (Story MVP cycle, 2026-04-28)

**Cycle**: Lee directive (`WITNESS_STORY_OUTPUT_MVP_PLAN.md`) 따라 annotated probe → 한국어 이야기 출력 layer 구현. 9 phases, 48 stories 생성, 6/6 PASS.

**핵심 설계 결정**:

1. **3단 파이프라인 분리** (extract / IR / render):
   - extract: 정규식 parser, 숫자/구조만 추출
   - IR: 의미 atom 변환 (blame_band, confession_volume, authority_pattern)
   - render: 한국어 templates 매핑
   - 가치: 문제 진단이 단계별로 분리됨. final_summary 잘못 나오면 IR 문제, 한국어 어색하면 render 문제 — 즉시 위치 식별.

2. **IR atom = 임계값 분류 + scenario 정규화**:
   - blame_band 4단계 (absent/weak/strong/dominant) by crowd_blame_peak threshold
   - confession_volume scenario-normalized (sacred는 60+이 high, 다른 scenario는 100+)
   - 가치: 같은 raw 수치도 시나리오 맥락에서 다른 의미로 해석.

3. **Probe-hash variation pool**:
   - `variant_pick(probe_id, slot, pool)` — md5 hash 기반 deterministic 선택
   - 같은 IR 입력에도 probe_id 다르면 다른 sentence 선택
   - 가치: P4=P5 같은 동일-IR 케이스에서도 텍스트 차이 발생 (C6 marginal 해결)

4. **LLM 자유 생성 거부**:
   - Template-guided rendering으로 limit
   - 가치: forbidden 0건 보장 (raw ID, 숫자, 메타 phrase) + 디버깅 가능 + reproducibility
   - 비용: variation 한계 (대형 sentence pool 필요)

5. **Branch C가 story output에 immediate value**:
   - 36 Branch C probes에 같은 파이프라인 적용 → 48 stories
   - Configuration sensitivity (LOW_ACTIVITY rare, nonmonotonic, placement reversal) 모두 narrative tone에서 surface
   - 가치: 두 cycle (Branch C 1차 evidence + Story output)이 *결합 시 추가 가치 큼*. 단순 add-on이 아닌 multiplicative.

**교훈**:

1. **Engine output을 자연어로 즉시 변환하지 말 것**. 중간 IR 단계 도입이 quality 진단/개선의 단일 가장 중요한 결정.
2. **Atom 임계값은 scenario-aware**: 같은 confession_count도 sacred vs scarcity에서 다른 의미. 시나리오 정규화가 필요.
3. **Variation은 deterministic hash로 도입**: 같은 입력 같은 출력 보장 + probe 간 차이 발생.
4. **Spec §6 forbidden phrase 검증은 자동화**: audit_report.py가 raw ID/숫자/메타 자동 차단.
5. **MVP acceptance criteria가 서사 quality의 객관적 metric** 역할: 6 binary criteria로 PASS/FAIL 분명. 길이/어떤 단어 같은 표면 metric보다 *흐름 식별 가능성*이 더 본질.
6. **Story output은 v2.0 Narrative Witness Layer entry point**: 지금까지 Witness가 만들어 온 trace/probe/annotated가 *읽힘 자산*으로 변환 가능함을 증명. v2.0 인터랙티브 layer는 이 위에 build 가능.

---

### L14. Autonomous mode produces working docs that don't pass HARNESS audit (LOOP 80-81, 2026-04-28)

`scripts/audit_report.py` (built LOOP 80) audited all 15 Branch C docs created during LOOPs 51-78. **15/15 FAIL** — every doc missing at least 3 HARNESS sections (typically H4 What-could-still-be-wrong, H5 Lee verbatim, H7 HARNESS 자가감사).

After synonym support added (LOOP 81), best score: FIRST_EVIDENCE_SUMMARY = 3 violations (still fails). Most docs at 5-7 violations.

**교훈**:

1. **HARNESS compliance is binary in current implementation**: required sections must literally exist. Synonyms help (e.g., "Limitations" matches "What could still be wrong"), but H5/H7 sections are absent in most autonomous-mode outputs.
2. **Autonomous mode prioritizes content over structure**. When pursuing substantive findings (S2 nonmonotonicity, D' rejection, cross-seed walkback), HARNESS sections are easy to skip. The findings ARE in the docs — just not in the standardized HARNESS section structure.
3. **Distinguish working notes from final reports**: not every doc warrants full HARNESS structure. Working notes (e.g., `BRANCH_C_S2_DESIGN_PLAN.md`) shouldn't require Lee verbatim quote section. But final reports (e.g., `LEE_GATE_2026-04-28_BRANCH_C.md`) absolutely should — and that one currently fails 6 violations.
4. **Audit tool surfaces this gap mechanically**. Without `audit_report.py`, this would be invisible. The tool's value is detecting drift even within a HARNESS-aware project.
5. **Future autonomous-mode discipline**: any doc explicitly destined for Lee (LEE_GATE, FIRST_EVIDENCE_SUMMARY, BLIND_PACKAGE) should run audit before close. Working notes can fail audit silently — they're scratch.

---

### L13. Seed=0-only baseline conditioning understates AND overstates effects unpredictably (LOOP 73-76, 2026-04-28)

**Cycle**: LOOP 67-69 generated 36 probes at seed=0. LOOP 70 found nonmonotonicity (S2 triple→RECOVERY 3/3 across density variants). LOOP 73 ran seed-robustness check on S2 baseline → triple→RECOVERY drops to 3/5 across seeds. LOOP 74-76 ran full cross-seed re-tests of all 4 slices.

**Result**: per-dimension sensitivity (seed=0 → ensemble):
- S5 placement: 67% → 44% (-23pp)
- S4 cast: 67% → 56% (-11pp)
- S3 event density: 22% → 44% **(+22pp INCREASE)**
- S2 scarcity depth: 44% → 11% (-33pp)
- Mean: 50% → 39% (-11pp)

**Key surprise**: cross-seed effect is NOT systematic walkback. S3 sensitivity *increased* (+22pp) — seed=0 underestimated event density effects. S2 dropped severely — most flips were seed-conditional. S4 was most stable.

**교훈**:

1. **Seed=0 is biased in unpredictable directions**, not just toward optimism. Some cells have RECOVERY/SATURATION balance that depends entirely on the deterministic random seed. Sensitivity claims at seed=0 can be 30+ pp off in either direction.
2. **Cross-seed ensemble is the only reliable measure** for sensitivity ratios. Single-seed measurements are inadequate even for relative comparisons (S2 went from 4th-most sensitive to least sensitive after ensemble correction).
3. **Surprising findings (like LOOP 69 nonmonotonicity) need IMMEDIATE seed-robustness check** before docs are written. The 1-loop delay (LOOP 73) revealed the finding was largely seed=0 artifact.
4. **Within-cell variance varies by slice**: S3 has 4/9 unanimous (most stable), S4/S2 have 0/9 unanimous. Stability is *itself* a configuration-dependent property worth measuring.
5. **HARNESS H4 "What I did NOT try" surfaces real falsification paths**: the seed=0 caveat was explicitly noted in H4 sections from LOOP 64. Honoring those caveats with actual tests turned them into evidence — H4 is not just a hedge, it's a roadmap to discovering errors.
6. **Autonomous-mode self-falsification is possible**: 4 LOOP cycle (73-76) of progressive walkback was entirely self-driven — no Lee feedback needed. HARNESS H1 + H4 discipline kept this honest.

---

### L12. Hypothesis falsification via cross-scenario test reveals scenario-specific dynamics (LOOP 67-72, 2026-04-28)

**Cycle**: S2 scarcity depth (LOOP 69) found triple→RECOVERY nonmonotonicity. LOOP 70 tested 3 hypotheses (A/B/C all rejected) and proposed D (oscillation enables confession). LOOP 70 verified D in scarcity. LOOP 72 tested D' (D generalizes to accusation+sacred) — **D' REJECTED**.

**Result**: scenario-specific dynamics-rules. Same spacing input produces opposite outcomes per scenario:
- scarcity spread → RECOVERY
- accusation spread → SATURATION  
- sacred spread → RECOVERY

**교훈**:

1. **Falsification via generalization test is highly informative**. D' rejection is *more useful* than D acceptance — it reveals scenario-specific dynamics, a stronger claim than "scarcity has unique pattern".
2. **Don't rush to mechanism-level claim from single scenario**. D was tempting after S2 nonmonotonicity test, but it took only 1 test (LOOP 72, 8 probes, ~5 min) to falsify. Always test generalization before claiming mechanism.
3. **HARNESS H1 (null hypothesis discipline) survived multiple cycles**: scarcity→fisher_laborer invariance rejected routing-only (v4). Cross-scenario D' rejection rejected universal-mechanism. Both findings are negative results that strengthen the project's claim system.
4. **Configuration sensitivity has 2 layers**: within-scenario (S5/S4/S3/S2) AND cross-scenario (D'). Both layers needed for full Branch C activation evidence. Single-layer claim would be incomplete.
5. **Autonomous-mode hypothesis cycles**: 6 LOOPs (67-72) covered 1 new slice + 1 hypothesis cycle (D→D test→D'→D' test→D' rejection→canonical claim revision). High mechanism-level density per loop, no engine touch, fully reversible. This is a *productive* autonomous mode pattern.

---

### L11. Engine state surface gap ≠ Engine logic gap (LOOP 64 v4, 2026-04-28)

GPT FILLED §6 N=12 measured Q3b interpersonal axis "partial" — `c.blame_concentration[target]`은 engine state에 이미 존재하지만 annotated 헤드라인에 노출 안 됨. v4 = generator-level surfacing으로 30 probes regenerate, 30/30 PASS validate_annotated_v4.

**Falsification test (HARNESS H1)**: scarcity routes accusation events through `merchant` but top blame은 `fisher_laborer`로 100% 향함 → trivial routing-only hypothesis 기각, field captures emergent crowd dynamics.

**교훈**:
1. **Surface gap vs logic gap 구분**: measurement field가 없을 뿐 engine 데이터는 충분한 경우가 많음. v3 (public_suspicion/authority_vigilance), v4 (top_blame_target) 모두 같은 패턴. Engine 변경 vs generator 변경의 cost 차이는 두 자릿수.
2. **Validator forking pattern**: `validate_annotated_v3.py` → `validate_annotated_v4.py`로 fork. v3 보존 (이력), forward는 v4. spec evolution과 함께 검증기도 진화.
3. **Falsification first**: 새 field 추가 시 "trivial explanation으로 재현 가능한가?" 즉시 체크. v4의 fisher_laborer invariance가 routing-only 가설을 정확히 기각 — H1 자가검증 통과.
