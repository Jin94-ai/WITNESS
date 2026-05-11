WITNESS 프로젝트는 이제 Visual Explorer v0까지 완료되었다. 앞으로의 작업은 “새 기능 무한 추가”가 아니라, 최종 목표인 움직이는 세계 관찰/탐색 시스템으로 가기 위한 단계적 로드맵에 따라 진행한다.

최종 목표:
도트 기반으로 흐르는 세계를 관찰하고, 특정 인물/집단/사건/세계 흐름을 줌인/줌아웃하며, 후보 이야기를 발견하고, 필요하면 텍스트 packet/story로 확인할 수 있는 내부 탐색 시스템을 만든다.

핵심 원칙:
1. Visual은 세계를 먼저 보게 한다.
2. Text는 선택한 순간을 이해하게 한다.
3. Story는 선택한 후보를 서사로 읽게 한다.
4. 시스템은 좋은 이야기/나쁜 이야기를 자동 판정하지 않는다.
5. 새 기능은 “세계 탐색이 쉬워지는가?”에 직접 기여할 때만 추가한다.
6. renderer 재개, 3D, React dashboard, 캐릭터 비주얼, player intervention은 별도 명시 전까지 금지한다.

==================================================
PHASE 1 — Visual Explorer v0.1 운영 정리
==================================================

목표:
explorer.html을 visual layer의 기준 entry로 정리한다.

해야 할 일:
1. docs/visual/VISUAL_EXPLORER_V0_1_OPERATING_GUIDE.md 작성
   - 실행 방법
   - 필요한 데이터 파일
   - anchor dropdown 사용법
   - single-run view 사용법
   - cross-seed view 사용법
   - candidate panel 사용법
   - story/packet side panel의 현재 한계
   - 추천 사용 흐름 3개

2. docs/visual/VISUAL_EXPLORER_V0_1_SMOKE_TEST.md 작성
   - explorer.html 로드
   - baseline single-run view 로드
   - triple single-run view 로드
   - triple cross-seed view 로드
   - candidate filter 작동
   - candidate click 시 panel 갱신
   - seed row click 시 candidate panel 갱신
   - story placeholder 명확 표시

3. README.md / CLAUDE.md / DESIGN.md 갱신
   - explorer.html = broad navigation entry
   - dot_observer_replay.html = single-run deep view
   - dot_observer_cross_seed.html = cross-seed deep view

금지:
- 새 기능 구현 금지
- visual polish 금지
- story renderer 재개 금지

완료 조건:
- 운영 문서 + smoke test 문서 + core docs sync 완료
- 코드 수정이 필요 없는 상태면 여기서 멈추지 말고 Phase 2로 이동

==================================================
PHASE 2 — Explorer v0.2 최소 연결 개선
==================================================

목표:
Explorer가 “보기는 되지만 placeholder가 있는 상태”에서, 실제 후보 확인이 더 쉬운 상태로 개선한다.

허용 작업:
1. story/packet side panel에 precomputed candidate packet 연결
   - story renderer 재개 금지
   - 새 story 생성 금지
   - 이미 있는 packet/candidate metadata만 연결

2. candidate click 동작 개선
   - single-run view에서는 tick jump 명확화
   - cross-seed view에서는 seed focus 명확화

3. 작은 legend/label 개선
   - 색/marker 의미가 즉시 이해되게
   - 과도한 visual polish 금지

4. keyboard shortcut은 필요할 때만
   - ← / → tick 이동 정도만 허용

산출물:
- visual/explorer.html 업데이트
- docs/visual/VISUAL_EXPLORER_V0_2_REVIEW.md

성공 기준:
1. candidate를 클릭하면 “왜 이 후보인지” 더 빨리 이해된다.
2. packet side panel이 placeholder보다 확실히 낫다.
3. single-run과 cross-seed 전환이 덜 헷갈린다.
4. 기존 deep view 기능을 깨지 않는다.

실패 기준:
1. explorer.html이 너무 복잡해진다.
2. packet 연결이 또 다른 renderer처럼 커진다.
3. 기존 visual files를 불필요하게 리팩터한다.

완료 후:
- 성공이면 Phase 3
- 복잡해지면 rollback 또는 v0.1 유지

==================================================
PHASE 3 — Multi-anchor 최소 확장
==================================================

목표:
현재 visual explorer가 peter_scarcity 계열에만 맞춰진 것이 아닌지 확인한다.

주의:
대규모 multi-anchor 확장이 아니다.
딱 1개 anchor만 추가한다.

추천 후보:
- vangogh_sacred 또는 accusation canonical 중 하나
- 선택 기준:
  1. 기존 anchor와 world dynamics가 다를 것
  2. event-heavy 또는 sacred/world-heavy 성격이 보일 것
  3. 기존 exporter로 비교적 쉽게 생성 가능할 것

해야 할 일:
1. docs/visual/ANCHOR_3_SELECTION_NOTE.md 작성
   - 왜 이 anchor를 고르는지
   - 기대하는 차이
   - 검증할 질문

2. 해당 anchor visual data export
   - 기존 schema 유지
   - 새 schema 금지

3. explorer에 anchor option 추가
   - 대규모 UI 변경 금지

4. docs/visual/ANCHOR_3_VISUAL_VALIDATION.md 작성
   - single-run view 작동 여부
   - candidate distribution 차이
   - world/event/person lens 차이
   - 기존 visual encoding으로 충분한지

성공 기준:
- 기존 scarcity 계열과 다른 visual pattern이 보인다.
- explorer가 새 anchor도 무리 없이 로드한다.
- candidate 탐색 흐름이 유지된다.

실패 기준:
- 새 anchor에서도 차이가 거의 안 보인다.
- 데이터 export를 위해 engine을 건드려야 한다.
- visual encoding이 anchor마다 따로 놀기 시작한다.

완료 후:
- 성공이면 Phase 4
- 실패하면 anchor 확장 중단하고 visual encoding 재검토

==================================================
PHASE 4 — Observer-based Browsing Pack v1
==================================================

목표:
Lee가 실제로 훑어볼 수 있는 내부 결과물 패키지를 만든다.

이건 public demo가 아니다.
내부 탐색용 curated pack이다.

구성:
1. Single-run observation pack
   - 대표 run 2개
   - 각 run의 key ticks
   - world/person/event 요약

2. Cross-seed comparison pack
   - peter_scarcity_triple 5 seeds
   - outcome distribution
   - seed별 salient moments
   - candidate distribution

3. Candidate browsing pack
   - story_ready top candidates
   - observation_only candidates
   - low_activity_hold candidates
   - packet 링크 또는 요약

4. Visual entry guide
   - 어떤 파일을 열면 되는지
   - 어떤 순서로 보면 되는지

산출물:
- docs/visual/OBSERVER_BASED_BROWSING_PACK_V1.md
- docs/visual/OBSERVER_BASED_BROWSING_PACK_REVIEW.md

성공 기준:
1. Lee가 10~15분 안에 현재 세계 흐름과 후보를 훑을 수 있다.
2. 텍스트와 visual이 서로 보완된다.
3. 무엇이 story candidate인지 찾기 쉬워진다.

완료 후:
- 성공이면 Phase 5
- 약하면 explorer navigation/packet 구조만 국소 개선

==================================================
PHASE 5 — Text / Visual 역할 재평가
==================================================

목표:
텍스트를 더 개선해야 하는지, visual을 더 확장해야 하는지 판단한다.

해야 할 질문:
1. 인물의 이야기는 아직 약한가?
2. 인물 간 이야기는 별도 interaction layer가 필요한가?
3. 사건 중심 이야기는 visual+packet으로 충분한가?
4. 세계 전체 흐름은 text보다 visual이 더 잘 보여주는가?
5. story renderer를 재개할 이유가 있는가, 아니면 freeze 유지가 맞는가?

산출물:
- docs/creative/TEXT_VISUAL_ROLE_REASSESSMENT.md

판정:
A. Visual 중심 계속
   - visual explorer / browsing pack 강화

B. Text 보강 필요
   - renderer 재개가 아니라 person arc window / relation candidate 쪽만 검토

C. Interaction layer 필요
   - 인물 간 관계/상호작용 후보를 별도 backlog로 분리

D. 현재 수준 freeze
   - 다음은 public/internal demo 패키징

주의:
이 단계에서도 story renderer를 바로 재개하지 말고, 필요성을 먼저 문서로 판단한다.

==================================================
PHASE 6 — Internal Demo Package v1
==================================================

목표:
현재 WITNESS를 “보여줄 수 있는 내부 데모” 형태로 묶는다.

구성:
1. 실행 방법
2. explorer.html 진입
3. 대표 anchor 2~3개
4. single-run replay
5. cross-seed comparison
6. candidate packet
7. selected story sample
8. 한계와 caveat

산출물:
- docs/demo/INTERNAL_DEMO_PACKAGE_V1.md
- docs/demo/DEMO_SCRIPT_V1.md
- docs/demo/KNOWN_LIMITATIONS_V1.md

성공 기준:
- Lee가 혼자 실행하고 설명할 수 있다.
- 프로젝트가 무엇을 하는지 5분 안에 설명 가능하다.
- “세계가 흐르고, 관찰하고, 후보 이야기를 찾는다”가 보인다.

완료 후:
- public demo 여부 판단
- playable/intervention은 아직 보류

==================================================
PHASE 7 — Long-term Fork Decision
==================================================

목표:
이 프로젝트를 앞으로 어디로 확장할지 결정한다.

선택지:
1. Visual Explorer 중심
   - 관찰형 세계 엔진으로 발전

2. Story/IP Asset 중심
   - 좋은 후보를 선별해 이야기/IP 씨앗으로 발전

3. Simulation Research 중심
   - paper / engine validation 강화

4. Playable Prototype 중심
   - intervention / what-if / player action 도입

산출물:
- docs/roadmap/WITNESS_FORK_DECISION.md

판정 기준:
- 가장 많이 살아 있는 결과물이 무엇인가?
- Lee가 계속 만지고 싶은 방향은 무엇인가?
- 실제 결과물로 보여주기 쉬운 방향은 무엇인가?
- 구현 난이도 대비 가치가 가장 큰 방향은 무엇인가?

==================================================
GLOBAL FORBIDDEN UNTIL EXPLICIT DIRECTIVE
==================================================

아래는 명시적 지시 전까지 금지:

- 3D
- React dashboard
- 캐릭터 일러스트
- animation polish
- player intervention
- story renderer full restart
- PyTorch encoder
- new scenario generation
- Talleyrand scenario
- public-facing product packaging
- multi-anchor 대규모 확장
- complex UI refactor
- 기존 안정 파일 대규모 리팩터

==================================================
GLOBAL STOP RULE
==================================================

각 Phase가 끝날 때마다 반드시:
1. 산출물 요약
2. 성공/실패 판정
3. 다음 Phase로 갈지 여부
4. 새 기능을 더 붙이지 않았는지 확인
5. forbidden 위반 여부 확인

을 남겨라.

작업이 marginal cleanup만 남으면 idle로 종료한다.
새 directive 없이 기능을 임의로 확장하지 않는다.