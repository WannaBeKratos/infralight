"""App-level controller — rescan, persistence, state factory.

Owns all UI side-effects that live outside any single page.
Folder selection is now inline in the sidebar, not a dialog.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from nicegui import app as nicegui_app
from nicegui import ui

if TYPE_CHECKING:
    from infralight.models.state import AppState

log = logging.getLogger(__name__)


class AppController:
    """Application-level controller — one per page request."""

    def __init__(self, state: AppState) -> None:
        self.state = state

    @staticmethod
    def build_state() -> AppState:
        """Create an AppState and hydrate from browser storage.

        Falls back to the bundled ``examples/`` directory so the UI is
        never empty on first launch.
        """
        from infralight.models.state import AppState

        stored = nicegui_app.storage.browser.get("project_dir")
        state = AppState()
        if stored:
            p = Path(stored)
            if p.is_dir():
                state.load_project(p)
                return state

        # Default: load the examples shipped with the project
        examples = Path(__file__).resolve().parents[3] / "examples"
        if examples.is_dir():
            state.load_project(examples)
        return state

    def rescan(self) -> None:
        """Re-scan current project and reload the current page."""
        self.state.rescan()
        if self.state.project:
            ui.notify(
                f"Rescanned — {len(self.state.project.files)} files",
                type="positive",
            )
        ui.navigate.to(ui.context.client.page.path)
