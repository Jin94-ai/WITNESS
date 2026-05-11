"""PYHASH guard -- ensures PYTHONHASHSEED=0 BEFORE Python starts.

Iter 105 found that `os.environ.setdefault("PYTHONHASHSEED", "0")`
inside scripts is too late -- Python initializes hash randomization
salt at interpreter startup. This guard re-runs the script via
subprocess with the env var set if it wasn't already.

Usage (place at TOP of probe script, before other imports):

    from scripts.b_direction._pyhash_guard import enforce_pyhash
    enforce_pyhash()

    # ... rest of imports ...
"""

from __future__ import annotations

import os
import subprocess
import sys


def enforce_pyhash(value: str = "0") -> None:
    """If PYTHONHASHSEED != value, re-run self via subprocess with it set.

    Uses subprocess instead of os.execvpe to avoid Windows segfault.
    The current process exits with the subprocess's return code.

    Skipped when running under pytest: a SystemExit during test-time module
    import is reported as a collection failure even when the relaunched
    subprocess passes. Tests should configure determinism explicitly (e.g.
    via fixtures or env in CI), not via a module-load-time relaunch.
    """
    if os.environ.get("PYTHONHASHSEED") == value:
        return
    if "pytest" in sys.modules:
        return
    new_env = {**os.environ, "PYTHONHASHSEED": value}
    result = subprocess.run(
        [sys.executable, *sys.argv],
        env=new_env,
        check=False,
    )
    sys.exit(result.returncode)
