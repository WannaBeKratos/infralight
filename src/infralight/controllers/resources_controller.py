"""Resources controller — prepares view-model for terraform-resources view."""

from __future__ import annotations

from typing import TYPE_CHECKING

from infralight.models.viewmodels import ResourcesVM, TfDetail

if TYPE_CHECKING:
    from infralight.models.state import AppState


class ResourcesController:
    """Builds the Terraform resources view-model."""

    def __init__(self, state: AppState) -> None:
        self.state = state

    def get_view_model(self) -> ResourcesVM:
        rows = self.state.tf_rows()
        return ResourcesVM(
            rows=rows,
            count=len(rows),
        )

    def get_detail(self, resource_id: str) -> TfDetail | None:
        return self.state.tf_detail(resource_id)
