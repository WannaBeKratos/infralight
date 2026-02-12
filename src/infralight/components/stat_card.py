"""Stat card — small metric display widget using Quasar."""

from nicegui import ui


def stat_card(title: str, value: str, icon: str, color: str) -> None:
    """Render a stat card using Quasar components."""
    with (
        ui.card()
        .props("flat bordered dark")
        .classes("q-pa-sm")
        .style("min-width:140px")
    ):
        with ui.row().classes("items-center q-gutter-sm no-wrap"):
            ui.icon(icon, color=color, size="md")
            with ui.column().classes("q-gutter-none"):
                ui.label(value).classes("text-h5 text-weight-bold")
                ui.label(title).classes("text-caption text-grey-6")
