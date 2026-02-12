"""Editor controller — file viewing and editing."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from nicegui import ui

from infralight.models.viewmodels import EditorVM, FileContent

if TYPE_CHECKING:
    from infralight.models.state import AppState

log = logging.getLogger(__name__)


class EditorController:
    """Manages reading and writing project files for the visual editor."""

    def __init__(self, state: AppState) -> None:
        self.state = state

    def get_view_model(self) -> EditorVM:
        """Build the file-list view-model for the editor page."""
        return EditorVM(
            has_project=self.state.project is not None,
            files=self.state.editable_file_rows(),
            count=len(self.state.project.files) if self.state.project else 0,
        )

    def get_file_content(self, rel_path: str) -> FileContent | None:
        """Get file content + metadata for editing."""
        return self.state.get_file_content(rel_path)

    def save_file(self, rel_path: str, content: str) -> None:
        """Save edited content to disk and notify."""
        ok = self.state.save_file_content(rel_path, content)
        if ok:
            ui.notify(f"Saved {rel_path}", type="positive")
        else:
            ui.notify(f"Failed to save {rel_path}", type="negative")
