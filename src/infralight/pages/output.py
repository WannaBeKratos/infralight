"""Output view — render controls and results listing.

Pure view — receives data from OutputController.
"""

from __future__ import annotations

from nicegui import ui

from infralight.components.data_table import data_table
from infralight.components.empty_state import empty_state
from infralight.components.panel import panel
from infralight.components.theme import COLORS
from infralight.models.viewmodels import OutputVM, rows_to_dicts


def render(vm: OutputVM) -> None:
    """Render output page from *vm* (from OutputController)."""
    _controls(vm)
    _results(vm)


def _controls(vm: OutputVM) -> None:
    with panel("Render Controls", icon="play_arrow", color=COLORS["positive"]):
        if not vm.has_project:
            empty_state("play_arrow", "No project open")
            return

        if not vm.il_count:
            empty_state(
                "code_off",
                "No IL templates found",
                "Create .il.sls or .il.tf files with IL decorators",
            )
            return

        ui.label(f"{vm.il_count} IL template(s) ready to render").classes(
            "text-body2 text-grey-4"
        )
        ui.label(f"Output → {vm.output_dir}").classes("text-caption text-grey-7")

        log_area = (
            ui.log(max_lines=200).classes("w-full q-mt-sm").style("height:200px;")
        )
        on_render = vm.on_render

        with ui.row().classes("q-mt-sm q-gutter-sm"):
            ui.button(
                "Render All", icon="play_arrow", on_click=lambda: on_render(log_area)
            ).props("color=positive no-caps")
            ui.button(
                "Clear Log", icon="delete_sweep", on_click=lambda: log_area.clear()
            ).props("flat no-caps color=grey-6")


def _results(vm: OutputVM) -> None:
    if not vm.rendered_rows:
        return

    with panel(
        "Rendered Files",
        icon="description",
        color=COLORS["info"],
        badge=str(len(vm.rendered_rows)),
    ):
        data_table(
            columns=[
                {
                    "name": "name",
                    "label": "File",
                    "field": "name",
                    "sortable": True,
                    "align": "left",
                },
                {"name": "path", "label": "Path", "field": "path", "align": "left"},
                {"name": "size", "label": "Size", "field": "size"},
            ],
            rows=rows_to_dicts(vm.rendered_rows),
            row_key="path",
        )
