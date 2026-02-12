"""Domain models for Infralight.

Keeps the data layer separate from UI or I/O.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class FileType(str, Enum):
    SALTSTACK = "saltstack"
    TERRAFORM = "terraform"


class FileKind(str, Enum):
    NATIVE = "native"  # plain .sls / .tf
    IL = "il"  # .il.sls / .il.tf — contains Infralight decorators


@dataclass
class SourceFile:
    """A file discovered by the scanner."""

    path: Path
    file_type: FileType
    kind: FileKind
    content: str = ""

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def language(self) -> str:
        return "yaml" if self.file_type == FileType.SALTSTACK else "hcl"

    @property
    def output_name(self) -> str:
        """Filename after stripping the .il suffix."""
        n = self.name
        for il_ext, native in [(".il.sls", ".sls"), (".il.tf", ".tf")]:
            if n.endswith(il_ext):
                return n[: -len(il_ext)] + native
        return n


@dataclass
class IaCResource:
    """A single resource parsed from a SaltStack or Terraform file."""

    id: str  # unique within the file
    name: str  # human label
    resource_type: str  # e.g. "pkg.installed", "aws_instance"
    provider: str = ""  # e.g. "salt", "aws", "docker"
    source_file: str = ""
    source_line: int = 0
    properties: dict[str, Any] = field(default_factory=dict)

    @property
    def kind_label(self) -> str:
        """Short badge text for tables."""
        return (
            self.resource_type.split(".")[-1]
            if "." in self.resource_type
            else self.resource_type
        )


@dataclass
class VisNode:
    id: str
    label: str = ""
    icon: str = "server"
    color: str = "#4FC3F7"
    shape: str = "box"
    group: str | None = None
    source_file: str = ""
    source_line: int = 0
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class VisEdge:
    source: str
    target: str
    label: str = ""
    style: str = "solid"
    color: str = "#90A4AE"
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class VisGroup:
    id: str
    label: str = ""
    icon: str = "folder"
    color: str = "#37474F"
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class VisNote:
    text: str
    target: str | None = None
    color: str = "#FFF176"


@dataclass
class Visualization:
    """Complete visualisation graph."""

    nodes: list[VisNode] = field(default_factory=list)
    edges: list[VisEdge] = field(default_factory=list)
    groups: list[VisGroup] = field(default_factory=list)
    notes: list[VisNote] = field(default_factory=list)
    layout: str = "dagre"

    def merge(self, other: Visualization) -> None:
        self.nodes.extend(other.nodes)
        self.edges.extend(other.edges)
        self.groups.extend(other.groups)
        self.notes.extend(other.notes)

    def clear(self) -> None:
        self.nodes.clear()
        self.edges.clear()
        self.groups.clear()
        self.notes.clear()

    def to_mermaid(self) -> str:
        lines: list[str] = ["graph TD"]
        grouped: dict[str, list[VisNode]] = {g.id: [] for g in self.groups}
        ungrouped: list[VisNode] = []

        for n in self.nodes:
            bucket = grouped.get(n.group or "")
            if bucket is not None:
                bucket.append(n)
            else:
                ungrouped.append(n)

        for g in self.groups:
            lines.append(f'  subgraph {g.id}["{_esc(g.label or g.id)}"]')
            for n in grouped.get(g.id, []):
                lines.append(f'    {n.id}["{_esc(n.label or n.id)}"]')
            lines.append("  end")

        for n in ungrouped:
            lines.append(f'  {n.id}["{_esc(n.label or n.id)}"]')

        for e in self.edges:
            arrow = "-->" if e.style == "solid" else "-.->"
            lbl = f"|{_esc(e.label)}|" if e.label else ""
            lines.append(f"  {e.source} {arrow}{lbl} {e.target}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "nodes": [
                {
                    "id": n.id,
                    "label": n.label or n.id,
                    "icon": n.icon,
                    "color": n.color,
                    "group": n.group,
                }
                for n in self.nodes
            ],
            "edges": [
                {"from": e.source, "to": e.target, "label": e.label, "style": e.style}
                for e in self.edges
            ],
            "groups": [
                {"id": g.id, "label": g.label or g.id, "color": g.color}
                for g in self.groups
            ],
            "layout": self.layout,
        }


def _esc(text: str) -> str:
    """Escape text for safe Mermaid label rendering."""
    return text.replace('"', "'").replace("\n", " ").replace("\r", "")


@dataclass
class Project:
    """An open project directory."""

    root: Path
    files: list[SourceFile] = field(default_factory=list)
    resources: list[IaCResource] = field(default_factory=list)
    visualization: Visualization = field(default_factory=Visualization)
    output_dir: Path | None = None

    @property
    def name(self) -> str:
        return self.root.name

    @property
    def salt_files(self) -> list[SourceFile]:
        return [f for f in self.files if f.file_type == FileType.SALTSTACK]

    @property
    def tf_files(self) -> list[SourceFile]:
        return [f for f in self.files if f.file_type == FileType.TERRAFORM]

    @property
    def il_files(self) -> list[SourceFile]:
        return [f for f in self.files if f.kind == FileKind.IL]
