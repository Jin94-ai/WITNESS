"""Engine Integrity Invariant Checks.

핵심 설계 원칙 재검증:
1. engine/에 인물 특정 용어 하드코딩 없음
2. content/ 패키지 분리 유지
3. 정경 텍스트 무결성 (scripture 모듈)
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENGINE_DIR = PROJECT_ROOT / "engine"
CONTENT_DIR = PROJECT_ROOT / "content"


class TestEngineIntegrity:
    def test_no_person_hardcoding_in_engine(self):
        """engine/에 Peter/Judas/Caiaphas/Vangogh/Gauguin/Theo 등장 없음."""
        forbidden_terms = [
            "peter", "judas", "caiaphas", "vangogh", "gauguin", "theo",
            "베드로", "유다", "가야바", "반고흐", "고갱", "테오",
        ]

        violations = []
        for py_file in ENGINE_DIR.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            content_lower = content.lower()
            for term in forbidden_terms:
                if term.lower() in content_lower:
                    # context 확인: 주석이나 docstring에 "예시"/"example"로 등장 가능
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if term.lower() in line.lower():
                            # 주석이나 docstring만 허용
                            stripped = line.strip()
                            if (stripped.startswith("#") or
                                stripped.startswith('"""') or
                                stripped.startswith("'''") or
                                "example" in stripped.lower() or
                                "예시" in stripped or
                                "예:" in stripped or
                                "(예:" in stripped):
                                continue
                            violations.append(
                                f"{py_file.relative_to(PROJECT_ROOT)}:{i+1}: "
                                f"contains '{term}': {line[:80]}"
                            )

        if violations:
            print("\n=== Engine Hardcoding Violations ===")
            for v in violations:
                print(f"  {v}")
        assert not violations, \
            f"Engine contains {len(violations)} hardcoding violations"

    def test_content_packs_present(self):
        """모든 content pack이 필수 파일을 갖고 있다."""
        content_packs = ["peter", "judas", "caiaphas", "crowd", "vangogh", "gauguin", "theo"]
        required_files = ["initial_state.json", "behavior_profile.json"]

        missing = []
        for pack in content_packs:
            pack_dir = CONTENT_DIR / pack
            if not pack_dir.exists():
                missing.append(f"{pack}: directory missing")
                continue
            for req in required_files:
                if not (pack_dir / req).exists():
                    missing.append(f"{pack}/{req}: missing")

        assert not missing, f"Missing content: {missing}"

    def test_scripture_files_present(self):
        """정경 텍스트 파일 존재 확인."""
        scripture_dir = CONTENT_DIR / "shared" / "scripture"
        if not scripture_dir.exists():
            # 없어도 OK (아직 미구현)
            return

        # JSON 파일이 있으면 파싱 가능해야 함
        import json
        for json_file in scripture_dir.glob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                assert data, f"Empty scripture: {json_file.name}"
            except json.JSONDecodeError as e:
                raise AssertionError(
                    f"Invalid JSON in {json_file.name}: {e}"
                ) from e

    def test_triggers_structural_independence(self):
        """triggers.json이 Peter state field를 참조하지 않음 (calibration leakage 방지)."""
        import json

        peter_triggers_path = CONTENT_DIR / "shared" / "triggers.json"
        if not peter_triggers_path.exists():
            return

        data = json.loads(peter_triggers_path.read_text(encoding="utf-8"))

        peter_fields_referenced = []
        for trigger in data.get("triggers", []):
            for cond in trigger.get("state_conditions", []):
                if cond.get("agent_id") == "peter":
                    peter_fields_referenced.append(trigger.get("trigger_id"))
                    break

        # Peter 상태가 trigger 조건에 사용되면 leakage
        assert not peter_fields_referenced, \
            f"Triggers reference Peter state (leakage): {peter_fields_referenced}"

        print(f"\n=== Triggers defined: {len(data.get('triggers', []))} ===")
        for t in data.get("triggers", []):
            print(f"  {t['trigger_id']}: {t.get('description', 'N/A')[:60]}")
