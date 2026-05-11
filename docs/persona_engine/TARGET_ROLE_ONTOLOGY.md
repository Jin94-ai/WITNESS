# Generic Target-Role Ontology (Step D)

**작성:** 2026-04-23
**목적:** `twelve_disciples`, `broader_followers`, `jesus` 같은 scenario-specific target 이름을 engine에서 제거, generic role 이름으로 교체.

---

## 0. 왜 이 교체가 필요한가

Rule #1 은 **engine/ 에 특정 인물 이름 금지**. 현재 `ACTIVE_VARIABLES_META.default_targets` 에서:

- `belonging`: `[twelve_disciples, broader_followers]` ← Peter-specific
- `love / loyalty / trust`: `[primary_figure, peers, family]` ← primary_figure/family는 generic, peers는 ambiguous

engine이 generic이려면 이 default 이름 자체가 role 추상화여야 한다.

---

## 1. 10 Generic Role

| Role | 의미 | Peter 시나리오 매핑 | Judas 시나리오 매핑 |
|---|---|---|---|
| `self` | 자기 자신 (self-directed emotions, e.g. guilt[self]) | self | self |
| `primary_focus` | 중심 결속 대상 (가장 강한 love/loyalty target) | Jesus | Jesus (pre-betrayal) |
| `intimate_other` | 가까운 1인 타자 (가족, 연인, 멘토 - primary_focus 아닌) | family | family |
| `peer_group` | 같은 지위/그룹의 동료들 | 제자 12인 | 제자 12인 |
| `in_group` | 자기 소속 공동체 (peer_group 포함 가능, 넓은 범위) | 추종자들 (넓은) | 추종자들 |
| `public_group` | 공개 현장의 외부 관찰자 | 성전 군중 / 대제사장 마당 사람 | 성전 군중 |
| `authority_group` | 권력/결정권자 | 대제사장, 로마 | 대제사장 |
| `rival` | 적대 / 경쟁 대상 | (Peter 직접 rival 없음) | 동문 (자신을 의심하는) |
| `protected_other` | 보호 대상 (부모/자녀/약자) | (Peter에게 명확 없음) | (Judas에게 없음) |
| `family` | 혈연 / 원초적 결속 | 부모, 형제 | 부모 |

---

## 2. Target-aware 변수 교체

### 2.1 Before (Peter-친화 default)

```python
VariableMeta(name="love",      ..., default_targets=["primary_figure", "peers", "family"]),
VariableMeta(name="loyalty",   ..., default_targets=["primary_figure", "peers"]),
VariableMeta(name="trust",     ..., default_targets=["primary_figure", "peers"]),
VariableMeta(name="belonging", ..., default_targets=["twelve_disciples", "broader_followers"]),
VariableMeta(name="guilt",     ..., default_targets=["primary_figure", "self"]),
VariableMeta(name="shame",     ..., default_targets=["crowd", "peers", "self"]),
```

### 2.2 After (Generic roles)

```python
VariableMeta(name="love",      ..., default_targets=["primary_focus", "peer_group", "family"]),
VariableMeta(name="loyalty",   ..., default_targets=["primary_focus", "peer_group"]),
VariableMeta(name="trust",     ..., default_targets=["primary_focus", "peer_group"]),
VariableMeta(name="belonging", ..., default_targets=["peer_group", "public_group"]),
VariableMeta(name="guilt",     ..., default_targets=["primary_focus", "self"]),
VariableMeta(name="shame",     ..., default_targets=["public_group", "peer_group", "self"]),
```

**변경 요약:**
- `primary_figure` → `primary_focus` (더 generic, "figure"는 인물 암시)
- `peers` → `peer_group` (명시적 group role)
- `crowd` → `public_group`
- `twelve_disciples` → `peer_group`
- `broader_followers` → `public_group` (또는 `in_group`)

`family` 는 generic role로 유지.

---

## 3. content/<scenario>/targets.json 확장

Scenario binding이 generic role → scenario-specific name 매핑을 제공:

```json
// content/peter/v3/targets.json
{
  "role_bindings": {
    "self": "peter",
    "primary_focus": "jesus",
    "intimate_other": "peter_family",
    "peer_group": "twelve_disciples",
    "in_group": "galilean_followers",
    "public_group": "jerusalem_crowd",
    "authority_group": "sanhedrin",
    "rival": null,
    "protected_other": null,
    "family": "peter_family"
  }
}
```

```json
// content/judas/v3/targets.json
{
  "role_bindings": {
    "self": "judas",
    "primary_focus": "jesus",
    "peer_group": "twelve_disciples",
    "public_group": "jerusalem_crowd",
    "authority_group": "sanhedrin",
    "rival": "pharisees",
    "family": "judas_family"
  }
}
```

---

## 4. Scene semantics content 분리

Rubric scene_response / context_break 의 scenario-specific 내용을 content로 이동:

```json
// content/peter/v3/scene_semantics.json
{
  "scene_response_families": {
    "public_accusation": ["deny", "withdraw_in_fear", ...],
    "restoration_moment": ["confess", "run_to_tomb", ...]
  },
  "affordance_preconditions": {
    "run_to_tomb": ["requires_recent_restoration"],
    "jump_into_sea": ["requires_boat_or_shore"]
  },
  "motif_scene_mapping": {
    "public_accusation": {"conceal": 1.0, "withdraw": 0.5},
    "eye_contact": {"grieve": 1.0, "seek_repair": 0.3}
  }
}
```

Engine critics 는 content 주입 시 override, 없으면 generic DEFAULT 사용.

---

## 5. faith_stage_tag도 scenario content로

현재 `engine/person/state_derived.py::faith_stage_tag` 는 Christian narrative 특수어 (shepherd / foundation / restored) 를 사용. 교체:

**generic API:**
```python
# engine 쪽
def role_trajectory_tag(state, scenario_tag_fn) -> str:
    """Scenario content가 제공하는 tag function 호출."""
    return scenario_tag_fn(state)
```

**content 쪽 (Peter):**
```python
# content/peter/v3/derived.py
def faith_stage_tag(state):
    # 기존 로직 동일 (shepherd/foundation/restored/failed/tested/follower/none)
    ...
```

**content 쪽 (Judas):**
```python
# content/judas/v3/derived.py  
def betrayal_arc_tag(state):
    # compliant / conflicted / bargained / betrayed / remorseful / despaired
    ...
```

---

## 6. 구현 체크리스트 (ordered)

- [ ] `ACTIVE_VARIABLES_META` default_targets 교체 (→ Step D 부분 구현)
- [ ] `content/peter/v3/initial_state.json` role key 업데이트 (기존 primary_figure → primary_focus 등)
- [ ] `content/peter/v3/targets.json` role_bindings 추가
- [ ] `content/judas/v3/initial_state.json` 동일 업데이트
- [ ] `content/judas/v3/targets.json` role_bindings
- [ ] `_scalar_target(state, field, key)` 호출들이 새 key 이름 사용하도록 점검
- [ ] `engine/rubric/scene_response_critic.py` scene families를 scenario content에서 주입 가능하게 ctor 확장 (기존 DEFAULT 유지)
- [ ] `engine/rubric/context_break_critic.py` affordances/motive_requirements 주입 가능하게 확장
- [ ] `faith_stage_tag` — content-provided tag function로 이동 (Step E 와 함께)

---

## 7. 영향 범위

**깨질 가능성 높은 곳:**
- `content/peter/v3/initial_state.json` — target key 이름 변경 필요
- 모든 Peter tests (target key 접근 시)
- Judas initial state (현재 primary_figure 씀)

**영향 없음:**
- Engine API (generic이므로 key string만 다름)
- Rubric critics 구조

---

**End of Step D.**
