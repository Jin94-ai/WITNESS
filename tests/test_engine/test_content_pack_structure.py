"""Content pack structural validator.

각 `content/[name]/` 폴더가 엔진 로드 규격을 충족하는지 검증.
새 시나리오 추가 시 이 테스트만 통과하면 엔진과 호환.

SCENARIO_TEMPLATE.md §3.1 에 명시된 필수 파일 기준.
"""

import json
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


_NON_AGENT_DIRS = {"shared", "worlds", "interventions", "anchors", "universal", "genres"}


def _list_agent_packs() -> list[Path]:
    """Content 하위의 agent pack 디렉터리 목록.

    `shared/` 는 공용 리소스, `worlds/` 는 v2.0 세계 pack (WORLD_DESIGN.md §4.1),
    `interventions/` 는 v2.0 Spike 4 counterfactual spec 모음.
    전부 agent pack 규격이 아니므로 이 검증에서 제외한다.
    """
    return [
        d for d in CONTENT_DIR.iterdir()
        if d.is_dir() and d.name not in _NON_AGENT_DIRS and not d.name.startswith("__")
    ]


class TestAgentPackStructure:
    def test_initial_state_present(self):
        """모든 agent pack에 initial_state.json 존재."""
        missing = []
        for pack in _list_agent_packs():
            if not (pack / "initial_state.json").exists():
                missing.append(pack.name)
        assert not missing, f"Missing initial_state.json: {missing}"

    def test_behavior_profile_present(self):
        """모든 agent pack에 behavior_profile.json 존재."""
        missing = []
        for pack in _list_agent_packs():
            if not (pack / "behavior_profile.json").exists():
                missing.append(pack.name)
        assert not missing, f"Missing behavior_profile.json: {missing}"

    def test_initial_state_schema(self):
        """initial_state.json이 기본 필드를 갖는다."""
        errors = []
        for pack in _list_agent_packs():
            path = pack / "initial_state.json"
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                errors.append(f"{pack.name}: invalid JSON — {e}")
                continue
            # Required top-level
            for field in ["agent_id"]:
                if field not in data:
                    errors.append(f"{pack.name}: missing '{field}'")
            # emotion/physical optional but if present must be dict
            for optional in ["emotions", "physical", "slow_state", "domain_state"]:
                if optional in data and not isinstance(data[optional], dict):
                    errors.append(f"{pack.name}: '{optional}' not dict")
        assert not errors, f"Schema violations: {errors}"

    def test_behavior_profile_schema(self):
        """behavior_profile.json의 actions가 required 필드를 갖는다."""
        errors = []
        for pack in _list_agent_packs():
            path = pack / "behavior_profile.json"
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                errors.append(f"{pack.name}: invalid JSON — {e}")
                continue
            if "agent_id" not in data:
                errors.append(f"{pack.name}: missing 'agent_id'")
            actions = data.get("actions", [])
            if not isinstance(actions, list):
                errors.append(f"{pack.name}: 'actions' not list")
                continue
            for i, act in enumerate(actions):
                if not isinstance(act, dict):
                    errors.append(f"{pack.name}.actions[{i}]: not dict")
                    continue
                for field in ["action_id", "weight_formula"]:
                    if field not in act:
                        errors.append(f"{pack.name}.actions[{i}]: missing '{field}'")
                wf = act.get("weight_formula", {})
                if "base_weight" not in wf:
                    errors.append(f"{pack.name}.actions[{i}].weight_formula: missing 'base_weight'")
        assert not errors, f"Behavior profile violations: {errors}"

    def test_no_engine_hardcoding_in_content(self):
        """content/ 에는 engine import가 있어도 engine 내부 로직 재정의 없음.

        Smoke: domain_*.py 파일이 DomainState를 상속만 하고 엔진 로직을 override하지 않는지.
        """
        violations = []
        for pack in _list_agent_packs():
            for py in pack.glob("domain_*.py"):
                text = py.read_text(encoding="utf-8")
                # Rule 정의(class ... Rule) 이나 engine 내부 로직 override는 금지
                forbidden_patterns = [
                    "class.*Rule.*:",
                    "class SimulationWorld",
                    "class HazardEngine",
                    "class TriggerEngine",
                ]
                import re
                for pattern in forbidden_patterns:
                    if re.search(pattern, text):
                        violations.append(f"{py.relative_to(CONTENT_DIR.parent)}: pattern '{pattern}'")
        assert not violations, f"Content has engine logic: {violations}"


class TestSharedContent:
    def test_shared_triggers_if_present(self):
        """shared/triggers.json 존재 시 구조 검증."""
        path = CONTENT_DIR / "shared" / "triggers.json"
        if not path.exists():
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "triggers" in data
        for i, t in enumerate(data["triggers"]):
            assert "trigger_id" in t, f"triggers[{i}] missing id"
            assert "event_template_id" in t, f"triggers[{i}] missing event_template_id"

    def test_scripture_valid_json(self):
        """shared/scripture/ 하위 JSON 파일 모두 파싱 가능."""
        sdir = CONTENT_DIR / "shared" / "scripture"
        if not sdir.exists():
            return
        for jf in sdir.glob("*.json"):
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                raise AssertionError(f"{jf.name}: {e}") from e
            assert data, f"{jf.name} empty"


class TestCurrentPacksEnumerated:
    def test_known_agent_packs_present(self):
        """현재 7개 agent pack이 존재."""
        expected = {"peter", "judas", "caiaphas", "crowd", "vangogh", "gauguin", "theo"}
        actual = {p.name for p in _list_agent_packs()}
        missing = expected - actual
        assert not missing, f"Missing expected packs: {missing}"

    def test_pack_count_reasonable(self):
        """Pack 수가 합리적 범위 (3~100)."""
        packs = _list_agent_packs()
        assert 3 <= len(packs) <= 100, f"Pack count {len(packs)} unusual"
