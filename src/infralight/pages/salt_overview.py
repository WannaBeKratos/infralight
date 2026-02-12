"""Salt overview page — categorised view of Salt resources.

Shows installed packages, services, files, commands, and other Salt
module categories with their requisite dependencies.
"""

from __future__ import annotations

from nicegui import ui

from infralight.components.data_table import data_table
from infralight.components.empty_state import empty_state
from infralight.components.panel import panel
from infralight.components.stat_card import stat_card
from infralight.models.viewmodels import (
    SaltCategory,
    SaltOverviewVM,
    SaltRequisite,
    rows_to_dicts,
)


def render(vm: SaltOverviewVM) -> None:
    """Render the full Salt Overview page."""
    if not vm.has_project:
        empty_state(
            "terminal",
            "No project loaded",
            "Open a folder containing SaltStack files to get started.",
        )
        return

    if vm.total_states == 0:
        empty_state(
            "terminal",
            "No Salt states found",
            "No SaltStack .sls files were found in the project.",
        )
        return
    _stats_row(vm)
    if vm.unique_packages or vm.unique_services:
        _quick_lists(vm)
    if vm.categories:
        _category_tabs(vm.categories)
    if vm.requisites:
        _requisites_panel(vm.requisites)


def _stats_row(vm: SaltOverviewVM) -> None:
    with ui.row().classes("w-full q-gutter-sm q-mb-md"):
        stat_card("Total States", str(vm.total_states), "terminal", "#FFA726")
        stat_card("Packages", str(vm.total_packages), "inventory_2", "#66BB6A")
        stat_card(
            "Services", str(vm.total_services), "miscellaneous_services", "#42A5F5"
        )
        stat_card("Files", str(vm.total_files), "description", "#FFA726")
        stat_card("Dependencies", str(len(vm.requisites)), "link", "#AB47BC")


def _quick_lists(vm: SaltOverviewVM) -> None:
    """Show chip badges for unique packages and services."""
    with ui.row().classes("w-full q-gutter-md q-mb-md"):
        if vm.unique_packages:
            with panel(
                "Installed Packages",
                icon="inventory_2",
                color="#66BB6A",
                badge=str(len(vm.unique_packages)),
            ):
                with ui.row().classes("q-gutter-xs"):
                    for pkg in vm.unique_packages:
                        ui.badge(pkg, color="green-9").props("outline").classes(
                            "text-caption"
                        )

        if vm.unique_services:
            with panel(
                "Managed Services",
                icon="miscellaneous_services",
                color="#42A5F5",
                badge=str(len(vm.unique_services)),
            ):
                with ui.row().classes("q-gutter-xs"):
                    for svc in vm.unique_services:
                        ui.badge(svc, color="blue-9").props("outline").classes(
                            "text-caption"
                        )


def _category_tabs(categories: list[SaltCategory]) -> None:
    """Render a tab panel per module category."""
    with panel("Resources by Module", icon="category", color="orange-6"):
        with ui.tabs().props("dense dark align=left").classes("text-grey-4") as tabs:
            tab_map = {}
            for cat in categories:
                t = ui.tab(
                    cat.module, label=f"{cat.label} ({cat.count})", icon=cat.icon
                )
                tab_map[cat.module] = t

        with ui.tab_panels(tabs).props("dark animated").classes("w-full"):
            for cat in categories:
                with ui.tab_panel(cat.module):
                    _category_table(cat)


def _category_table(cat: SaltCategory) -> None:
    """Render the table for one module category."""
    columns = [
        {
            "name": "state_id",
            "label": "State ID",
            "field": "state_id",
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
            "name": "action",
            "label": "Action",
            "field": "action",
            "sortable": True,
            "align": "left",
        },
        {
            "name": "key_props",
            "label": "Properties",
            "field": "key_props",
            "align": "left",
        },
        {
            "name": "source_file",
            "label": "Source",
            "field": "source_file",
            "align": "left",
        },
        {"name": "line", "label": "Line", "field": "line", "sortable": True},
    ]
    data_table(
        columns=columns,
        rows=rows_to_dicts(cat.items),
        row_key="state_id",
    )


def _requisites_panel(requisites: list[SaltRequisite]) -> None:
    """Show a table of all state-to-state dependencies."""
    with panel(
        "State Dependencies", icon="link", color="#AB47BC", badge=str(len(requisites))
    ):
        columns = [
            {
                "name": "from_state",
                "label": "From State",
                "field": "from_state",
                "sortable": True,
                "align": "left",
            },
            {
                "name": "relation",
                "label": "Relation",
                "field": "relation",
                "sortable": True,
                "align": "left",
            },
            {
                "name": "to_module",
                "label": "To Module",
                "field": "to_module",
                "sortable": True,
                "align": "left",
            },
            {
                "name": "to_state",
                "label": "To State",
                "field": "to_state",
                "sortable": True,
                "align": "left",
            },
            {
                "name": "source_file",
                "label": "Source",
                "field": "source_file",
                "align": "left",
            },
        ]
        data_table(
            columns=columns,
            rows=rows_to_dicts(requisites),
            row_key="from_state",
        )
