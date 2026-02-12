"""States view — renders salt-states from a typed view-model.

Pure view — receives data from StatesController, only renders widgets.
"""

from __future__ import annotations

from collections.abc import Callable

from nicegui import ui

from infralight.components.data_table import data_table
from infralight.components.empty_state import empty_state
from infralight.components.panel import panel
from infralight.components.theme import COLORS
from infralight.models.viewmodels import SaltDetail, StatesVM, rows_to_dicts


def render(vm: StatesVM, on_select: Callable) -> None:
    """Render the states page.

    *vm* is a ``StatesVM`` with ``rows`` and ``count``.
    *on_select* is called with the selected row's ``path``.
    """
    with panel(
        "Salt States", icon="terminal", color=COLORS["salt"], badge=str(vm.count)
    ):
        if not vm.rows:
            empty_state("terminal", "No SaltStack files found")
            return

        data_table(
            columns=[
                {
                    "name": "file",
                    "label": "File",
                    "field": "file",
                    "sortable": True,
                    "align": "left",
                },
                {"name": "path", "label": "Path", "field": "path", "align": "left"},
                {
                    "name": "kind",
                    "label": "Kind",
                    "field": "kind",
                    "sortable": True,
                    "align": "left",
                },
                {
                    "name": "states",
                    "label": "States",
                    "field": "states",
                    "sortable": True,
                },
                {
                    "name": "modules",
                    "label": "Modules",
                    "field": "modules",
                    "align": "left",
                },
            ],
            rows=rows_to_dicts(vm.rows),
            row_key="path",
            selection="single",
            on_select=on_select,
        )


def render_detail(detail: SaltDetail | None, container) -> None:
    """Fill *container* with detail for a selected salt file."""
    container.clear()
    if not detail:
        return

    with container:
        with panel("State Details", icon="description", color=COLORS["salt"]):
            ui.label(detail.name).classes(
                "text-subtitle2 text-weight-bold text-grey-3 q-mb-sm"
            )

            if detail.resources:
                data_table(
                    columns=[
                        {
                            "name": "id",
                            "label": "State ID",
                            "field": "id",
                            "align": "left",
                        },
                        {
                            "name": "type",
                            "label": "Module",
                            "field": "type",
                            "align": "left",
                        },
                        {
                            "name": "name",
                            "label": "Name",
                            "field": "name",
                            "align": "left",
                        },
                        {
                            "name": "props",
                            "label": "Properties",
                            "field": "props",
                            "align": "left",
                        },
                    ],
                    rows=rows_to_dicts(detail.resources),
                    row_key="id",
                )
            else:
                ui.label("No states parsed from this file.").classes(
                    "text-caption text-grey-7"
                )

            with (
                ui.expansion("Raw Content", icon="code")
                .classes("w-full q-mt-sm")
                .props("dense dark")
            ):
                ui.code(detail.content, language=detail.language).classes(
                    "w-full"
                ).style("max-height:300px; overflow:auto;")
