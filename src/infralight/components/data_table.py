"""Data table — thin wrapper that applies Infralight styling."""

from __future__ import annotations

from typing import Any

from nicegui import ui
from nicegui.elements.table import Table


def data_table(
    columns: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    *,
    row_key: str = "id",
    selection: str | None = None,
    on_select: Any = None,
) -> Table:
    """Create a styled Quasar table."""
    kwargs: dict[str, Any] = {
        "columns": columns,
        "rows": rows,
        "row_key": row_key,
    }
    if selection:
        kwargs["selection"] = selection
    if on_select:
        kwargs["on_select"] = on_select

    return (
        ui.table(**kwargs)
        .classes("w-full")
        .props("dense flat bordered dark separator=cell")
    )
