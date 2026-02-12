"""Playwright test fixtures — starts Infralight server for E2E tests."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
_VENV_PYTHON = _ROOT / ".venv" / "Scripts" / "python.exe"


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _wait_for_server(port: int, proc: subprocess.Popen, timeout: float = 30.0) -> None:
    """Block until the server is accepting connections."""
    log_file = _ROOT / "tests" / "_server.log"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        # Check process is alive
        if proc.poll() is not None:
            log = log_file.read_text() if log_file.exists() else "(no log)"
            raise RuntimeError(
                f"Server process exited with code {proc.returncode}.\nLog:\n{log}"
            )
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return
        except OSError:
            time.sleep(0.5)
    log = log_file.read_text() if log_file.exists() else "(no log)"
    raise RuntimeError(
        f"Server did not start within {timeout}s on port {port}.\nLog:\n{log}"
    )


@pytest.fixture(scope="session")
def base_url():
    """Start the Infralight server in a subprocess, return its base URL."""
    port = _find_free_port()

    python = str(_VENV_PYTHON) if _VENV_PYTHON.exists() else sys.executable
    env = os.environ.copy()
    env["PYTHONPATH"] = str(_SRC)

    log_file = _ROOT / "tests" / "_server.log"
    log_fh = log_file.open("w")

    env["NICEGUI_SCREEN_TEST_PORT"] = str(port)

    proc = subprocess.Popen(
        [python, "-u", str(_ROOT / "tests" / "_test_server.py"), str(port)],
        cwd=str(_ROOT),
        env=env,
        stdout=log_fh,
        stderr=subprocess.STDOUT,
    )
    try:
        _wait_for_server(port, proc)
        yield f"http://127.0.0.1:{port}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        log_fh.close()
