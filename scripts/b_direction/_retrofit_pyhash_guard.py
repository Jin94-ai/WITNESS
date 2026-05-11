"""One-shot retrofit: add PYHASH guard to all probe scripts in scripts/b_direction.

Iter 105 finding: `os.environ.setdefault("PYTHONHASHSEED", "0")` is
too late; Python reads PYTHONHASHSEED at startup. This retrofit
replaces that pattern with proper guard import.

Run: `python scripts/b_direction/_retrofit_pyhash_guard.py`
"""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).parent
GUARD_INSERT = (
    "\nfrom scripts.b_direction._pyhash_guard import enforce_pyhash"
    "\nenforce_pyhash()\n"
)


def retrofit(path: Path) -> bool:
    """Replace the buggy setdefault with proper guard call.

    Returns True if file modified, False otherwise.
    """
    content = path.read_text(encoding="utf-8")
    needle = 'os.environ.setdefault("PYTHONHASHSEED", "0")'
    if needle not in content:
        return False
    if "_pyhash_guard" in content:
        # Already retrofitted
        return False
    # Strategy:
    # 1. Remove the setdefault line entirely
    # 2. Insert guard import after `sys.path.insert(0, str(ROOT))`
    new_content = content.replace(needle + "\n", "")
    sys_path_line = "    sys.path.insert(0, str(ROOT))"
    if sys_path_line not in new_content:
        # Fallback: insert near end of imports
        return False
    new_content = new_content.replace(
        sys_path_line + "\n",
        sys_path_line + "\n" + GUARD_INSERT,
    )
    path.write_text(new_content, encoding="utf-8")
    return True


def main() -> int:
    skip_files = {"_pyhash_guard.py", "_retrofit_pyhash_guard.py"}
    scripts = sorted(HERE.glob("*.py"))
    modified = []
    skipped = []
    for s in scripts:
        if s.name in skip_files:
            continue
        if retrofit(s):
            modified.append(s.name)
        else:
            skipped.append(s.name)

    print(f"[retrofit] modified {len(modified)} files:")
    for f in modified:
        print(f"  + {f}")
    print(f"[retrofit] skipped {len(skipped)} files (no needle or already done):")
    for f in skipped:
        print(f"  - {f}")
    return 0


if __name__ == "__main__":
    main()
