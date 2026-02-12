"""Infralight Jinja2 decorator functions.

Injected into the Jinja2 rendering context so ``.il.sls`` / ``.il.tf``
authors can annotate resources with visualisation hints.  Every function
returns ``""`` so the rendered output stays clean.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any

from infralight.core.models import VisEdge, VisGroup, VisNode, VisNote, Visualization


@dataclass
class _Collector:
    nodes: list[VisNode] = field(default_factory=list)
    edges: list[VisEdge] = field(default_factory=list)
    groups: list[VisGroup] = field(default_factory=list)
    notes: list[VisNote] = field(default_factory=list)
    layout: str = "dagre"
    source_file: str = ""

    def to_vis(self) -> Visualization:
        return Visualization(
            list(self.nodes),
            list(self.edges),
            list(self.groups),
            list(self.notes),
            self.layout,
        )

    def clear(self) -> None:
        self.nodes.clear()
        self.edges.clear()
        self.groups.clear()
        self.notes.clear()
        self.layout = "dagre"


_local = threading.local()


def _col() -> _Collector:
    if not hasattr(_local, "c"):
        _local.c = _Collector()
    return _local.c


def begin_collect(source: str = "") -> None:
    c = _col()
    c.clear()
    c.source_file = source


def end_collect() -> Visualization:
    c = _col()
    v = c.to_vis()
    c.clear()
    return v


def il_node(
    id: str,
    label: str = "",
    icon: str = "server",
    color: str = "#4FC3F7",
    shape: str = "box",
    group: str | None = None,
    **meta: Any,
) -> str:
    _col().nodes.append(
        VisNode(
            id=id,
            label=label or id,
            icon=icon,
            color=color,
            shape=shape,
            group=group,
            source_file=_col().source_file,
            meta=dict(meta),
        )
    )
    return ""


def il_edge(
    source: str,
    target: str,
    label: str = "",
    style: str = "solid",
    color: str = "#90A4AE",
    **meta: Any,
) -> str:
    _col().edges.append(
        VisEdge(
            source=source,
            target=target,
            label=label,
            style=style,
            color=color,
            meta=dict(meta),
        )
    )
    return ""


def il_group(
    id: str, label: str = "", icon: str = "folder", color: str = "#37474F", **meta: Any
) -> str:
    _col().groups.append(
        VisGroup(id=id, label=label or id, icon=icon, color=color, meta=dict(meta))
    )
    return ""


def il_note(text: str, target: str | None = None, color: str = "#FFF176") -> str:
    _col().notes.append(VisNote(text=text, target=target, color=color))
    return ""


def il_layout(layout: str = "dagre") -> str:
    _col().layout = layout
    return ""


IL_GLOBALS: dict[str, Any] = {
    "il_node": il_node,
    "il_edge": il_edge,
    "il_group": il_group,
    "il_note": il_note,
    "il_layout": il_layout,
}
