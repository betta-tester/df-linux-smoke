"""Refusal of ``smoke --version`` when the distribution is not installed."""

import os
import subprocess
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
LAUNCH = ["uv", "run", "--no-project", "--isolated", "python"]
CODE = "import sys; from smoke.cli import main; sys.exit(main(['--version']))"


def test_missing_distribution_prints_no_version(tmp_path: Path) -> None:
    command = [*LAUNCH, "-c", CODE]
    env = {**os.environ, "PYTHONPATH": str(SRC)}
    result = subprocess.run(
        command, cwd=tmp_path, env=env, capture_output=True, check=False
    )
    print(f"command: {' '.join(command)} (cwd={tmp_path}, PYTHONPATH={SRC})")
    print(f"returncode={result.returncode} stderr={result.stderr!r}")

    assert result.returncode == 1
    assert result.stdout == b""
    stderr = result.stderr.decode()
    assert len(stderr.splitlines()) == 1
    assert "smoke" in stderr and "not installed" in stderr
    assert "uv sync" in stderr
    assert "Traceback" not in stderr
