"""States controller — prepares view-model for salt-states view."""

from __future__ import annotations

from typing import TYPE_CHECKING

from infralight.models.viewmodels import SaltDetail, StatesVM

if TYPE_CHECKING:
    from infralight.models.state import AppState


class StatesController:
    """Builds the salt-states view-model."""

    def __init__(self, state: AppState) -> None:
        self.state = state

    def get_view_model(self) -> StatesVM:
        return StatesVM(
            rows=self.state.salt_rows(),
            count=len(self.state.project.salt_files) if self.state.project else 0,
        )

    def get_detail(self, rel_path: str) -> SaltDetail | None:
        """Return detail for a selected salt file."""
        return self.state.salt_detail(rel_path)
