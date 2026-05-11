"""AnchorRegistry — separates anchor-specific identity from universal seeds.

Per `docs/witness_narrative_mode_plan.md` §3.5:
    뼈대 엔진은 universal seed만 출력한다. anchor-specific 인물명, 시대 배경,
    문화 표현은 별도 AnchorRegistry가 보관한다.

이 모듈은 universal seed + anchor binding을 합쳐 anchor-rendered surface를
생성하는 *경계 layer*. skeleton engine은 이 모듈을 import하지 않는다.
flesh engine과 portfolio surface만 사용.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


_ANCHORS_ROOT = Path(__file__).resolve().parents[2] / "content" / "anchors"


# ---------------------------------------------------------------------------
# AnchorBinding — universal role → anchor-specific name / label
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AnchorBinding:
    """Universal seed의 main_role / supporting_roles → anchor 표시 이름 매핑.

    매핑은 content/anchors/{anchor_id}/binding.json에서 옴. 이 모듈은
    구조만 정의하고, 구체 이름은 보관하지 않는다.
    """
    anchor_id: str
    description_ko: str
    role_to_display_name_ko: dict[str, str] = field(default_factory=dict)
    archetype_to_display_name_ko: dict[str, str] = field(default_factory=dict)
    raw_id_to_display_name_ko: dict[str, str] = field(default_factory=dict)
    role_label_overrides_ko: dict[str, str] = field(default_factory=dict)

    def display_name_for_role(self, role: str) -> str:
        return self.role_to_display_name_ko.get(role, role)

    def display_name_for_raw(self, raw_name: str) -> str:
        """영어 raw 이름 → 한국어 display로 매핑. 매핑 없으면 그대로 반환."""
        return self.raw_id_to_display_name_ko.get(raw_name, raw_name)

    def to_dict(self) -> dict:
        return {
            "anchor_id": self.anchor_id,
            "description_ko": self.description_ko,
            "role_to_display_name_ko": dict(self.role_to_display_name_ko),
            "archetype_to_display_name_ko": dict(self.archetype_to_display_name_ko),
            "raw_id_to_display_name_ko": dict(self.raw_id_to_display_name_ko),
            "role_label_overrides_ko": dict(self.role_label_overrides_ko),
        }


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def load_anchor_binding(anchor_id: str, content_root: Path | None = None) -> AnchorBinding | None:
    """Load `content/anchors/{anchor_id}/binding.json` if present.

    Returns None if no binding file — caller can fall back to universal-only
    rendering.
    """
    root = content_root or _ANCHORS_ROOT
    p = root / anchor_id / "binding.json"
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    return AnchorBinding(
        anchor_id=anchor_id,
        description_ko=data.get("description_ko", ""),
        role_to_display_name_ko=data.get("role_to_display_name_ko", {}),
        archetype_to_display_name_ko=data.get("archetype_to_display_name_ko", {}),
        raw_id_to_display_name_ko=data.get("raw_id_to_display_name_ko", {}),
        role_label_overrides_ko=data.get("role_label_overrides_ko", {}),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class AnchorRegistry:
    """In-memory cache of anchor bindings.

    Flesh engine / portfolio surface usage:
        registry = AnchorRegistry()
        binding = registry.get(anchor_id)
        display = binding.display_name_for_raw(raw_name)
    """

    def __init__(self, content_root: Path | None = None) -> None:
        self._root = content_root or _ANCHORS_ROOT
        self._cache: dict[str, AnchorBinding] = {}

    def get(self, anchor_id: str) -> AnchorBinding | None:
        if anchor_id in self._cache:
            return self._cache[anchor_id]
        binding = load_anchor_binding(anchor_id, content_root=self._root)
        if binding is not None:
            self._cache[anchor_id] = binding
        return binding

    def list_anchors(self) -> list[str]:
        if not self._root.exists():
            return []
        return sorted(
            p.name for p in self._root.iterdir()
            if p.is_dir() and (p / "binding.json").exists()
        )
