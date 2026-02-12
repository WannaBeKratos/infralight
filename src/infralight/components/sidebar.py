"""Sidebar — Quasar list navigation + project file tree."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from nicegui import app as nicegui_app
from nicegui import ui

from infralight.components.file_tree import file_tree

if TYPE_CHECKING:
    from infralight.models.state import AppState

_NAV_ITEMS = [
    ("Dashboard", "dashboard", "/"),
    ("Salt States", "terminal", "/states"),
    ("Salt Overview", "inventory_2", "/salt-overview"),
    ("TF Resources", "cloud", "/resources"),
    ("Visualization", "account_tree", "/visualization"),
    ("File Editor", "edit_note", "/editor"),
    ("Render Output", "play_arrow", "/output"),
]


def sidebar(state: AppState, active: str) -> None:
    """Render the drawer contents: nav items, file tree, project path."""
    with ui.list().props("dark dense"):
        for label, icon, href in _NAV_ITEMS:
            is_active = href == active
            with (
                ui.item(on_click=lambda h=href: ui.navigate.to(h))
                .props(f"clickable {'active' if is_active else ''}")
                .classes("rounded-borders q-mx-xs")
            ):
                with ui.item_section().props("avatar"):
                    ui.icon(icon, color="primary" if is_active else "grey-6")
                with ui.item_section():
                    ui.item_label(label)

    ui.separator().props("dark")
    if state.project:
        ui.label("FILES").classes("text-overline text-grey-7 q-px-md q-pt-sm")

        with ui.scroll_area().classes("w-full").style("max-height: 45vh;"):

            def _on_file_click(rel_path: str) -> None:
                """Navigate to editor with the selected file."""
                ui.navigate.to(f"/editor?file={rel_path}")

            file_tree(state.project, on_select=_on_file_click)
    else:
        with ui.column().classes("q-pa-md items-center"):
            ui.icon("folder_open", size="md", color="grey-7")
            ui.label("No project open").classes("text-caption text-grey-7")

    ui.space()
    ui.separator().props("dark")
    with ui.column().classes("q-pa-sm q-gutter-xs"):
        if state.project:
            ui.label(state.project.name).classes("text-subtitle2 text-grey-3")
            ui.label(str(state.project.root)).classes("text-caption text-grey-6").style(
                "word-break:break-all;"
            )
            ui.label(
                f"{len(state.project.files)} files  ·  "
                f"{len(state.project.resources)} resources"
            ).classes("text-caption text-grey-7")

        # Inline path input — replaces the dialog
        with ui.row().classes("w-full items-end q-gutter-xs q-mt-xs"):
            path_input = (
                ui.input(
                    label="Project path",
                    value=str(state.project.root) if state.project else "",
                )
                .props("dense outlined dark")
                .classes("col")
            )

            def _load_path() -> None:
                p = Path(path_input.value.strip())
                if not p.is_dir():
                    ui.notify(f"Not a valid directory: {p}", type="negative")
                    return
                nicegui_app.storage.browser["project_dir"] = str(p)
                ui.navigate.to("/")

            ui.button(icon="folder_open", on_click=_load_path).props(
                "dense flat color=primary size=sm"
            ).tooltip("Load project")
