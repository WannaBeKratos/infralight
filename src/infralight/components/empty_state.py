"""Empty state — placeholder shown when there's no data to display."""

from nicegui import ui


def empty_state(
    icon: str = "inbox",
    title: str = "Nothing here yet",
    subtitle: str = "",
) -> None:
    """Render a centered empty-state placeholder using Quasar."""
    with ui.column().classes("w-full items-center q-pa-xl q-gutter-sm"):
        ui.icon(icon, color="grey-8", size="xl")
        ui.label(title).classes("text-subtitle1 text-grey-6")
        if subtitle:
            ui.label(subtitle).classes("text-caption text-grey-8")
