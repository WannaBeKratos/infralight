"""Output controller — render IL files, report results."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from nicegui import ui

from infralight.models.viewmodels import OutputVM

if TYPE_CHECKING:
    from infralight.models.state import AppState

log = logging.getLogger(__name__)


class OutputController:
    """Builds the render-output view-model and executes rendering."""

    def __init__(self, state: AppState) -> None:
        self.state = state

    def get_view_model(self) -> OutputVM:
        has_project = self.state.project is not None
        il_count = len(self.state.project.il_files) if self.state.project else 0
        output_dir = (
            (self.state.project.output_dir or self.state.project.root / "output")
            if self.state.project
            else None
        )
        return OutputVM(
            has_project=has_project,
            il_count=il_count,
            output_dir=str(output_dir) if output_dir else "",
            rendered_rows=self.state.rendered_file_rows(),
            on_render=lambda log_widget: self.do_render(log_widget),
        )

    def do_render(self, log_widget=None) -> None:
        """Execute rendering and push messages to the log widget."""
        if not self.state.project:
            return

        output_dir = self.state.project.output_dir or self.state.project.root / "output"
        if log_widget:
            log_widget.push(
                f"Rendering {len(self.state.project.il_files)} file(s) → {output_dir}"
            )

        try:
            results = self.state.render_il_files()
            if log_widget:
                for name in results:
                    log_widget.push(f"  ✓ {name}")
                log_widget.push(f"Done — {len(results)} file(s) rendered.")
            ui.notify(f"Rendered {len(results)} file(s)", type="positive")
        except Exception as exc:
            log.exception("Render failed")
            if log_widget:
                log_widget.push(f"  ✗ Error: {exc}")
            ui.notify(f"Render failed: {exc}", type="negative")

        ui.navigate.to("/output")
