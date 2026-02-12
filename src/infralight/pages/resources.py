"""Resources view — renders terraform resources from a typed view-model.

Pure view — receives data from ResourcesController.
"""

from __future__ import annotations

from collections.abc import Callable

from nicegui import ui

from infralight.components.data_table import data_table
from infralight.components.empty_state import empty_state
from infralight.components.panel import panel
from infralight.components.theme import COLORS
from infralight.models.viewmodels import ResourcesVM, TfDetail, rows_to_dicts


def render(vm: ResourcesVM, on_select: Callable) -> None:
    """Render the resources table."""
    with panel(
        "Terraform Resources",
        icon="cloud",
        color=COLORS["terraform"],
        badge=str(vm.count),
    ):
        if not vm.rows:
            empty_state("cloud_off", "No Terraform resources found")
            return

        data_table(
            columns=[
                {
                    "name": "id",
                    "label": "ID",
                    "field": "id",
                    "sortable": True,
                    "align": "left",
                },
                {
                    "name": "type",
                    "label": "Type",
                    "field": "type",
                    "sortable": True,
                    "align": "left",
                },
                {
                    "name": "name",
                    "label": "Name",
                    "field": "name",
                    "sortable": True,
                    "align": "left",
                },
                {
                    "name": "provider",
                    "label": "Provider",
                    "field": "provider",
                    "sortable": True,
                    "align": "left",
                },
                {
                    "name": "file",
                    "label": "File",
                    "field": "file",
                    "sortable": True,
                    "align": "left",
                },
                {"name": "line", "label": "Line", "field": "line"},
            ],
            rows=rows_to_dicts(vm.rows),
            row_key="id",
            selection="single",
            on_select=on_select,
        )


def render_detail(detail: TfDetail | None, container) -> None:
    """Fill *container* with resource detail."""
    container.clear()
    if not detail:
        return

    with container:
        with panel("Resource Details", icon="description", color=COLORS["terraform"]):
            with ui.row().classes("q-gutter-sm q-mb-sm items-center"):
                ui.label(detail.type).classes(
                    "text-subtitle2 text-weight-bold text-grey-3"
                )
                ui.label(detail.name).classes("text-body2 text-grey-6")

            if detail.properties:
                data_table(
                    columns=[
                        {
                            "name": "key",
                            "label": "Property",
                            "field": "key",
                            "align": "left",
                        },
                        {
                            "name": "value",
                            "label": "Value",
                            "field": "value",
                            "align": "left",
                        },
                    ],
                    rows=rows_to_dicts(detail.properties),
                    row_key="key",
                )
            else:
                ui.label("No properties extracted.").classes("text-caption text-grey-7")
