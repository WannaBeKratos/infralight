"""Dashboard view — renders the dashboard from a typed view-model.

This is a **View** in MVC.  It receives a pre-built view-model from the
controller and only renders Quasar widgets — no data transformation or
business logic lives here.
"""

from __future__ import annotations

from nicegui import ui

from infralight.components.data_table import data_table
from infralight.components.empty_state import empty_state
from infralight.components.panel import panel
from infralight.components.stat_card import stat_card
from infralight.components.theme import COLORS
from infralight.models.viewmodels import (
    DashboardStats,
    DashboardVM,
    Issue,
    rows_to_dicts,
)


def render(vm: DashboardVM) -> None:
    """Render dashboard from *vm* (produced by DashboardController)."""
    _stats_row(vm.stats)
    _issues_panel(vm.has_project, vm.issues)
    _files_panel(vm.file_rows, vm.on_rescan)


def _stats_row(stats: DashboardStats) -> None:
    with ui.row().classes("w-full q-gutter-sm flex-wrap"):
        stat_card("Files", stats.files, "description", COLORS["info"])
        stat_card("Salt States", stats.salt, "terminal", COLORS["salt"])
        stat_card("TF Resources", stats.tf, "cloud", COLORS["terraform"])
        stat_card("IL Templates", stats.il, "auto_awesome", COLORS["il"])
        stat_card("Resources", stats.resources, "widgets", COLORS["neutral"])


def _issues_panel(has_project: bool, issues: list[Issue]) -> None:
    with panel("Issues", icon="warning", color=COLORS["salt"]):
        if not has_project:
            _issue("info", "No project open — use Open Folder to get started.")
            return
        if not issues:
            _issue("ok", "No issues found.")
        for iss in issues:
            _issue(iss.level, iss.message)


def _issue(level: str, msg: str) -> None:
    icons = {"ok": "check_circle", "info": "info", "warn": "warning", "error": "error"}
    colors = {
        "ok": "green-5",
        "info": "light-blue-5",
        "warn": "orange-6",
        "error": "red-5",
    }
    with ui.row().classes("w-full items-center q-gutter-sm q-py-xs"):
        ui.icon(icons.get(level, "info"), color=colors.get(level, "grey-6"), size="xs")
        ui.label(msg).classes("text-body2 text-grey-4")


def _files_panel(rows, on_rescan) -> None:
    with panel(
        "Project Files",
        icon="folder_open",
        color=COLORS["info"],
        actions=[("Refresh", "refresh", on_rescan)],
    ):
        if not rows:
            empty_state("folder_open", "No files discovered")
            return

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
                {
                    "name": "type",
                    "label": "Type",
                    "field": "type",
                    "sortable": True,
                    "align": "left",
                },
                {
                    "name": "kind",
                    "label": "Kind",
                    "field": "kind",
                    "sortable": True,
                    "align": "left",
                },
            ],
            rows=rows_to_dicts(rows),
            row_key="path",
        )
