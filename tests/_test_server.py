"""Minimal test server — used by conftest.py to start Infralight in a subprocess.

Usage:  python _test_server.py <port>
"""

from __future__ import annotations

import sys

from nicegui import ui

# Swallow the top-level ui.run() call that fires when main.py is imported
_original_run = ui.run
ui.run = lambda **_kw: None  # type: ignore[assignment]

import infralight.main  # noqa: E402, F401 — registers all @ui.page routes

# Restore and start the server on the requested port
ui.run = _original_run  # type: ignore[assignment]

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

ui.run(
    title="Infralight Test",
    port=port,
    dark=True,
    reload=False,
    show=False,
    storage_secret="test-secret",
)
