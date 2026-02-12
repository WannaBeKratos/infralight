"""View-model dataclasses — typed structures passed between layers.

These replace the raw ``dict`` returns so every field is explicit,
documented, and statically checked.  Quasar tables still need
``list[dict]``, so row dataclasses provide a ``to_dict()`` helper
and the ``rows_to_dicts()`` utility converts a whole list.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any


def rows_to_dicts(rows: list[Any]) -> list[dict[str, Any]]:
    """Convert a list of dataclass rows to list[dict] for Quasar tables."""
    return [asdict(r) for r in rows]


@dataclass
class FileRow:
    name: str
    path: str
    type: str
    kind: str


@dataclass
class SaltRow:
    file: str
    path: str
    kind: str
    states: int
    modules: str


@dataclass
class ResourceSummary:
    """One parsed resource within a salt detail view."""

    id: str
    type: str
    name: str
    props: str


@dataclass
class TfRow:
    id: str
    type: str
    name: str
    provider: str
    file: str
    line: int | str


@dataclass
class PropertyPair:
    key: str
    value: str


@dataclass
class RenderedFileRow:
    name: str
    path: str
    size: str


@dataclass
class EditableFileRow:
    name: str
    path: str
    type: str
    kind: str
    language: str


@dataclass
class SaltDetail:
    name: str
    content: str
    language: str
    resources: list[ResourceSummary]


@dataclass
class TfDetail:
    type: str
    name: str
    properties: list[PropertyPair]


@dataclass
class FileContent:
    """Full file payload for the visual editor."""

    name: str
    path: str
    abs_path: str
    content: str
    language: str
    kind: str
    type: str


@dataclass
class DashboardStats:
    files: str
    salt: str
    tf: str
    il: str
    resources: str


@dataclass
class Issue:
    level: str  # "warn", "info", "ok", "error"
    message: str


@dataclass
class VisNodeVM:
    id: str
    label: str
    group: str
    icon: str


@dataclass
class VisEdgeVM:
    src: str
    tgt: str
    label: str
    style: str


@dataclass
class VisGroupVM:
    id: str
    label: str


@dataclass
class DashboardVM:
    stats: DashboardStats
    issues: list[Issue]
    has_project: bool
    file_rows: list[FileRow]
    on_rescan: Callable[[], None]


@dataclass
class StatesVM:
    rows: list[SaltRow]
    count: int


@dataclass
class ResourcesVM:
    rows: list[TfRow]
    count: int


@dataclass
class VisVM:
    nodes: list[VisNodeVM]
    edges: list[VisEdgeVM]
    groups: list[VisGroupVM]
    mermaid: str
    layout: str
    has_data: bool


@dataclass
class InfraVisVM:
    """Infrastructure visualization — TF + Salt + IL decorators."""

    il_graph: VisVM  # from IL decorators only
    tf_graph: VisVM  # auto-generated from Terraform resources
    salt_graph: VisVM  # auto-generated from Salt states


@dataclass
class OutputVM:
    has_project: bool
    il_count: int
    output_dir: str
    rendered_rows: list[RenderedFileRow]
    on_render: Callable[..., None]


@dataclass
class EditorVM:
    has_project: bool
    files: list[EditableFileRow]
    count: int


@dataclass
class SaltCategoryItem:
    """One resource in a Salt module category (pkg, service, file, …)."""

    state_id: str
    name: str
    action: str  # e.g. "installed", "running", "managed"
    source_file: str
    line: int
    key_props: str  # abbreviated properties string


@dataclass
class SaltCategory:
    """A grouped module category with its resources."""

    module: str  # e.g. "pkg"
    label: str  # e.g. "Packages"
    icon: str  # Material icon
    color: str
    items: list[SaltCategoryItem]

    @property
    def count(self) -> int:
        return len(self.items)


@dataclass
class SaltRequisite:
    """A dependency between two salt states."""

    from_state: str
    relation: str  # "require", "watch", etc.
    to_module: str
    to_state: str
    source_file: str


@dataclass
class SaltOverviewVM:
    """Full view-model for the Salt Overview page."""

    has_project: bool
    total_states: int
    total_packages: int
    total_services: int
    total_files: int
    categories: list[SaltCategory]
    requisites: list[SaltRequisite]
    unique_packages: list[str]  # deduplicated package names
    unique_services: list[str]  # deduplicated service names
