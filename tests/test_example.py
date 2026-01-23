from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_example_script_runs() -> None:
    """Ensure example.py runs without errors."""
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    src_path = str(repo_root / "src")
    env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
    result = subprocess.run(
        [sys.executable, str(repo_root / "example.py")],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"example.py failed: stdout={result.stdout} stderr={result.stderr}"
