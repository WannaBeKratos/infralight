"""Salt overview controller — prepares the Salt Overview view-model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from infralight.models.viewmodels import SaltOverviewVM

if TYPE_CHECKING:
    from infralight.models.state import AppState


class SaltOverviewController:
    """Builds the Salt Overview view-model with categories and dependencies."""

    def __init__(self, state: AppState) -> None:
        self.state = state

    def get_view_model(self) -> SaltOverviewVM:
        return self.state.salt_overview()
