"""Dashboard controller — prepares view-model for the dashboard view."""

from __future__ import annotations

from typing import TYPE_CHECKING

from infralight.models.viewmodels import DashboardVM

if TYPE_CHECKING:
    from infralight.models.state import AppState


class DashboardController:
    """Builds the dashboard view-model."""

    def __init__(self, state: AppState) -> None:
        self.state = state

    def get_view_model(self) -> DashboardVM:
        """Build the typed view-model consumed by the dashboard view."""
        from infralight.controllers.app_controller import AppController

        return DashboardVM(
            stats=self.state.dashboard_stats(),
            issues=self.state.gather_issues() if self.state.project else [],
            has_project=self.state.project is not None,
            file_rows=self.state.file_rows(),
            on_rescan=lambda: AppController(self.state).rescan(),
        )
