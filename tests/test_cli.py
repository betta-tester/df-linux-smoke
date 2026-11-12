"""Black-box contract tests for the installed ``smoke`` console script."""

import os
import pty
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from importlib.metadata import version
from pathlib import Path

MAX_RESPONSE_SECONDS = 1.0
SOCKET_BLOCKER = (
    "import socket\n"
    "def _blocked(*a, **k):\n"
    "    raise OSError('network disabled')\n"
    "socket.socket = _blocked\n"
    "socket.create_connection = _blocked\n"
    "socket.getaddrinfo = _blocked\n"
)
CONTROL_CHARS = re.compile(rb"[\x00-\x09\x0b-\x1f\x7f]")


def command() -> str:
    """Resolve the console script by name in the active environment."""
    scripts = str(Path(sys.executable).parent)
    found = shutil.which("smoke", path=scripts + os.pathsep + os.environ["PATH"])
    assert found, "console script `smoke` is not installed"
    return found


def run(
    *args: str, cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[bytes]:
    """Run ``smoke`` as a separate process, capturing bytes."""
    return subprocess.run(
        [command(), *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=False,
        check=False,
    )


def expected_line() -> bytes:
    """Build the expected stdout from installed metadata at run time."""
    return f"smoke {version('smoke')}\n".encode()


def test_version_prints_single_version_line(tmp_path: Path) -> None:
    result = run("--version", cwd=tmp_path)
    assert result.returncode == 0
    assert result.stdout.count(b"\n") == 1
    assert result.stdout.endswith(b"\n")
    assert result.stdout.startswith(b"smoke ")


def test_version_matches_installed_metadata(tmp_path: Path) -> None:
    result = run("--version", cwd=tmp_path)
    assert result.stdout == expected_line()


def test_console_script_is_installed(tmp_path: Path) -> None:
    assert Path(command()).name.startswith("smoke")
    result = run("--version", cwd=tmp_path)
    assert result.returncode == 0
    assert result.stdout == expected_line()


def test_version_stdout_is_plain_single_line(tmp_path: Path) -> None:
    out = run("--version", cwd=tmp_path).stdout
    lines = out.split(b"\n")
    assert len(lines) == 2 and lines[1] == b""
    assert lines[0].strip() == lines[0] != b""
    assert b"\x1b" not in out
    assert not CONTROL_CHARS.search(out)


def run_on_pty(cwd: Path) -> bytes:
    """Run ``smoke --version`` with stdout on a pty slave; return the buffer."""
    master, slave = pty.openpty()
    try:
        proc = subprocess.Popen(
            [command(), "--version"], cwd=cwd, stdout=slave, stderr=subprocess.PIPE
        )
        os.close(slave)
        slave = -1
        proc.wait()
        chunks = []
        while True:
            try:
                data = os.read(master, 4096)
            except OSError:
                break
            if not data:
                break
            chunks.append(data)
            if len(data) < 4096:
                break
        if proc.stderr:
            proc.stderr.close()
        return b"".join(chunks)
    finally:
        os.close(master)
        if slave != -1:
            os.close(slave)


def test_version_output_identical_tty_and_pipe(tmp_path: Path) -> None:
    piped = run("--version", cwd=tmp_path).stdout
    tty = run_on_pty(tmp_path).replace(b"\r\n", b"\n")
    assert tty == piped
    assert run("--version", cwd=tmp_path).stdout == piped


def test_no_args_does_not_print_version(tmp_path: Path) -> None:
    result = run(cwd=tmp_path)
    assert not re.search(rb"^smoke \S+$", result.stdout, re.MULTILINE)
    assert result.stderr
    assert b"usage" in result.stderr.lower()
    assert result.returncode == 2


def snapshot(*roots: Path) -> dict[str, tuple[int, int]]:
    """Map every file under roots to its (mtime_ns, size)."""
    return {
        str(p): (p.stat().st_mtime_ns, p.stat().st_size)
        for root in roots
        for p in root.rglob("*")
    }


def test_version_responds_under_one_second_without_side_effects(
    tmp_path: Path, record_property: Callable[[str, object], None]
) -> None:
    workdir = tmp_path / "work"
    home = tmp_path / "home"
    blocker = tmp_path / "blocker"
    for d in (workdir, home, blocker):
        d.mkdir()
    (blocker / "sitecustomize.py").write_text(SOCKET_BLOCKER)
    env = {**os.environ, "HOME": str(home)}

    before = snapshot(workdir, home)
    started = time.perf_counter()
    result = run("--version", cwd=workdir, env=env)
    elapsed = time.perf_counter() - started
    after = snapshot(workdir, home)

    blocked_env = {**env, "PYTHONPATH": str(blocker)}
    blocked = run("--version", cwd=workdir, env=blocked_env)

    record_property("elapsed_seconds", elapsed)
    record_property("files_changed", len(set(after.items()) ^ set(before.items())))
    record_property("blocked_returncode", blocked.returncode)
    assert result.returncode == 0
    assert elapsed < MAX_RESPONSE_SECONDS
    assert after == before
    assert blocked.returncode == 0
    assert blocked.stdout == expected_line()
