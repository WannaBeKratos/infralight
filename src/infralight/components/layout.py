"""Layout shell — Quasar header + left-drawer + page container.

Usage::

    with page_layout(app_ctrl, active="/") as main:
        ui.label("Page content goes here")
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from nicegui import ui
from nicegui.element import Element

from infralight.components.sidebar import sidebar
from infralight.components.theme import inject_theme

if TYPE_CHECKING:
    from infralight.controllers.app_controller import AppController


@contextmanager
def page_layout(app_ctrl: AppController, active: str) -> Generator[Element, None, None]:
    """Render header + drawer and yield the main content column."""
    inject_theme()
    state = app_ctrl.state

    # Header
    with ui.header().props("elevated").classes("bg-dark q-px-md items-center"):
        ui.icon("bolt", color="primary", size="sm")
        ui.label("Infralight").classes("text-subtitle1 text-weight-bold q-ml-xs")
        ui.space()
        if state.project:
            ui.badge(state.project.name, color="deep-purple-8").props("outline")
        ui.button("Rescan", icon="refresh", on_click=lambda: app_ctrl.rescan()).props(
            "flat dense no-caps color=grey-4 size=sm"
        )

    # Sidebar
    with (
        ui.left_drawer(value=True, bordered=True)
        .props("width=260 breakpoint=0 dark")
        .classes("bg-dark")
    ):
        sidebar(state, active)

    # Page content area
    main = ui.column().classes("w-full q-pa-lg q-gutter-md")
    with main:
        yield main
