"""File tree component — directory-style tree using Quasar q-tree.

Builds a hierarchical tree from project files and fires a callback
when a file node is clicked.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any

from nicegui import ui

if TYPE_CHECKING:
    from infralight.core.models import Project


def build_tree_nodes(project: Project) -> list[dict[str, Any]]:
    """Convert project files into a nested tree structure for ui.tree.

    Returns a list like::

        [
            {"id": "saltstack", "label": "saltstack", "icon": "folder",
             "children": [
                {"id": "saltstack/webserver.il.sls", "label": "webserver.il.sls",
                 "icon": "description"},
             ]},
        ]
    """
    root: dict[str, Any] = {}  # path_part → sub-dict or None (leaf)

    for sf in sorted(project.files, key=lambda f: str(f.path)):
        try:
            rel = sf.path.relative_to(project.root)
        except ValueError:
            rel = PurePosixPath(sf.name)

        parts = list(rel.parts)
        node = root
        for i, part in enumerate(parts):
            if part not in node:
                node[part] = {} if i < len(parts) - 1 else None
            elif node[part] is None and i < len(parts) - 1:
                node[part] = {}
            if i < len(parts) - 1:
                node = node[part]

    def _to_nodes(d: dict[str, Any], prefix: str = "") -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        # Sort: folders first, then files
        folders = sorted(k for k, v in d.items() if v is not None)
        files = sorted(k for k, v in d.items() if v is None)

        for name in folders:
            path = f"{prefix}{name}" if not prefix else f"{prefix}/{name}"
            children = _to_nodes(d[name], path)
            nodes.append(
                {
                    "id": path,
                    "label": name,
                    "icon": "folder",
                    "children": children,
                }
            )

        for name in files:
            path = f"{prefix}{name}" if not prefix else f"{prefix}/{name}"
            icon = _file_icon(name)
            nodes.append(
                {
                    "id": path,
                    "label": name,
                    "icon": icon,
                }
            )

        return nodes

    return _to_nodes(root)


def file_tree(
    project: Project,
    *,
    on_select: Callable[[str], None] | None = None,
) -> ui.tree | None:
    """Render a clickable file tree for the project.

    *on_select* receives the relative file path when a leaf node (file)
    is clicked.
    """
    if not project or not project.files:
        return None

    nodes = build_tree_nodes(project)

    def _handle_select(e) -> None:
        if not on_select:
            return
        node_id = e.value  # the selected node "id"
        if not node_id:
            return
        # Only fire for leaf nodes (files, not folders)
        if _is_file_node(node_id, nodes):
            on_select(node_id)

    tree = (
        ui.tree(
            nodes,
            label_key="label",
            node_key="id",
            on_select=_handle_select,
        )
        .props("dense dark default-expand-all no-selection-unset")
        .classes("w-full")
    )

    return tree


def _is_file_node(node_id: str, nodes: list[dict]) -> bool:
    """Check if a node ID corresponds to a leaf (file) node."""
    for n in nodes:
        if n["id"] == node_id:
            return "children" not in n
        if "children" in n and _is_file_node(node_id, n["children"]):
            return True
    return False


def _file_icon(name: str) -> str:
    """Return a Material icon for a filename."""
    lower = name.lower()
    if lower.endswith((".il.sls", ".il.tf")):
        return "auto_fix_high"
    if lower.endswith(".sls"):
        return "terminal"
    if lower.endswith(".tf"):
        return "cloud"
    if lower.endswith((".yaml", ".yml")):
        return "data_object"
    if lower.endswith(".json"):
        return "data_object"
    return "description"
