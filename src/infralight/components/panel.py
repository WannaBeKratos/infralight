"""Panel — Quasar card with a coloured header bar.

Usage::

    with panel("Salt States", icon="terminal", color="orange-6") as body:
        ui.label("Content goes here")
"""

from __future__ import annotations

from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

from nicegui import ui
from nicegui.element import Element


@contextmanager
def panel(
    title: str,
    *,
    icon: str = "info",
    color: str = "blue-grey-5",
    badge: str = "",
    actions: list[tuple[str, str, Callable[[], Any]]] | None = None,
) -> Generator[Element, None, None]:
    """Render a Quasar card with a header section, yield the body."""
    with ui.card().props("flat bordered dark").classes("w-full q-mb-md"):
        # Header
        with ui.card_section().classes("row items-center q-gutter-sm q-py-sm"):
            ui.icon(icon, color=color, size="xs")
            ui.label(title).classes("text-subtitle2 text-weight-bold")
            if badge:
                ui.badge(badge, color="grey-8").props("dense outline")
            ui.space()
            if actions:
                for lbl, ic, cb in actions:
                    ui.button(lbl, icon=ic, on_click=cb).props(
                        "flat dense no-caps color=grey-4 size=sm"
                    )

        ui.separator().props("dark")

        # Body
        with ui.card_section() as body:
            yield body
