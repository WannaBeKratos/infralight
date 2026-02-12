"""Application state — pure data, no UI dependencies.

This is the **Model** in MVC.  It knows nothing about NiceGUI, Quasar,
or any view layer.  Controllers read from it and call its methods;
views receive typed view-model dataclasses assembled by controllers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from infralight.core.models import (
    IaCResource,
    Project,
    VisEdge,
    VisGroup,
    VisNode,
    Visualization,
)
from infralight.core.parsers import parse_file
from infralight.core.renderer import extract_visualization, render_all
from infralight.core.scanner import scan_directory
from infralight.models.viewmodels import (
    DashboardStats,
    EditableFileRow,
    FileContent,
    FileRow,
    Issue,
    PropertyPair,
    RenderedFileRow,
    ResourceSummary,
    SaltCategory,
    SaltCategoryItem,
    SaltDetail,
    SaltOverviewVM,
    SaltRequisite,
    SaltRow,
    TfDetail,
    TfRow,
)

log = logging.getLogger(__name__)


@dataclass
class AppState:
    """Central state — one instance per browser session."""

    project: Project | None = None
    current_vis: Visualization = field(default_factory=Visualization)

    def load_project(self, root: Path) -> None:
        """Scan *root*, parse all files, set output dir."""
        proj = scan_directory(root)
        for sf in proj.files:
            proj.resources.extend(parse_file(sf))
        proj.output_dir = root / "output"
        self.project = proj
        log.info(
            "Loaded %s — %d files, %d resources",
            root,
            len(proj.files),
            len(proj.resources),
        )

    def rescan(self) -> None:
        """Re-scan current project root.  Returns True on success."""
        if self.project:
            self.load_project(self.project.root)

    def build_visualization(self) -> Visualization:
        """Merge IL decorator graphs from all IL files."""
        combined = Visualization()
        if not self.project:
            return combined
        for sf in self.project.il_files:
            combined.merge(extract_visualization(sf))
        self.current_vis = combined
        return combined

    def build_tf_graph(self) -> Visualization:
        """Auto-generate a graph from Terraform resources only.

        - Terraform resources become nodes grouped by provider
        - TF resource references (id = ... in properties) become edges
        """
        vis = Visualization()
        if not self.project:
            return vis

        seen_nodes: set[str] = set()
        tf_groups: set[str] = set()
        for r in self.project.resources:
            if r.provider == "salt":
                continue

            provider = r.provider or "terraform"
            if provider not in tf_groups:
                tf_groups.add(provider)
                vis.groups.append(
                    VisGroup(
                        id=f"tf_{provider}",
                        label=f"TF: {provider.title()}",
                        icon="cloud",
                        color="#42A5F5",
                    )
                )

            node_id = r.id.replace(".", "_")
            if node_id not in seen_nodes:
                seen_nodes.add(node_id)
                icon = _tf_icon(r.resource_type)
                vis.nodes.append(
                    VisNode(
                        id=node_id,
                        label=r.name,
                        icon=icon,
                        color="#42A5F5",
                        group=f"tf_{provider}",
                        source_file=r.source_file,
                        source_line=r.source_line,
                    )
                )

        tf_ids = {r.id for r in self.project.resources if r.provider != "salt"}
        for r in self.project.resources:
            if r.provider == "salt":
                continue
            for _k, v in r.properties.items():
                if not isinstance(v, str):
                    continue
                for other_id in tf_ids:
                    if other_id != r.id and other_id.replace(
                        ".", "_"
                    ) in v.replace(".", "_"):
                        src = r.id.replace(".", "_")
                        tgt = other_id.replace(".", "_")
                        vis.edges.append(
                            VisEdge(
                                source=src,
                                target=tgt,
                                label="ref",
                                style="dashed",
                                color="#64B5F6",
                            )
                        )

        return vis

    def build_salt_graph(self) -> Visualization:
        """Auto-generate a graph from Salt states only.

        - Salt states become nodes grouped by module (pkg, service, ...)
        - Salt requisites become edges
        """
        vis = Visualization()
        if not self.project:
            return vis

        seen_nodes: set[str] = set()
        salt_groups: set[str] = set()
        salt_nodes_by_state: dict[str, str] = {}
        for r in self.project.resources:
            if r.provider != "salt":
                continue

            module = r.properties.get("__module", "salt")
            if module not in salt_groups:
                salt_groups.add(module)
                meta = self._SALT_MODULE_META.get(
                    module,
                    (module.title(), "extension", "#FFA726"),
                )
                vis.groups.append(
                    VisGroup(
                        id=f"salt_{module}",
                        label=f"Salt: {meta[0]}",
                        icon=meta[1],
                        color=meta[2],
                    )
                )

            func = r.properties.get("__function", "")
            node_id = f"salt_{r.id}_{module}"
            if node_id not in seen_nodes:
                seen_nodes.add(node_id)
                salt_nodes_by_state[r.id] = node_id
                vis.nodes.append(
                    VisNode(
                        id=node_id,
                        label=f"{r.name} ({module}.{func})",
                        icon=_salt_icon(module),
                        color=_salt_color(module),
                        group=f"salt_{module}",
                        source_file=r.source_file,
                        source_line=r.source_line,
                    )
                )

        for r in self.project.resources:
            if r.provider != "salt":
                continue
            reqs = r.properties.get("__requisites", [])
            src_node = salt_nodes_by_state.get(r.id)
            if not src_node:
                continue
            for req in reqs:
                to_state = req.get("state", "")
                rel = req.get("type", "require")
                tgt_node = salt_nodes_by_state.get(to_state)
                if not tgt_node:
                    for sid, nid in salt_nodes_by_state.items():
                        if sid == to_state:
                            tgt_node = nid
                            break
                if tgt_node and src_node != tgt_node:
                    style = (
                        "dashed"
                        if rel in ("watch", "listen", "onchanges")
                        else "solid"
                    )
                    vis.edges.append(
                        VisEdge(
                            source=src_node,
                            target=tgt_node,
                            label=rel,
                            style=style,
                            color="#FFA726",
                        )
                    )

        return vis

    def render_il_files(self) -> dict[str, str]:
        """Render all IL templates to output dir.

        Returns a dict of ``{filename: rendered_text}``.
        Raises on error — callers handle the exception.
        """
        if not self.project:
            return {}
        output_dir = self.project.output_dir or self.project.root / "output"
        results, vis = render_all(self.project.il_files, output_dir)
        self.current_vis = vis
        return results

    def dashboard_stats(self) -> DashboardStats:
        p = self.project
        if not p:
            return DashboardStats(
                files="—",
                salt="—",
                tf="—",
                il="—",
                resources="—",
            )
        return DashboardStats(
            files=str(len(p.files)),
            salt=str(len(p.salt_files)),
            tf=str(len(p.tf_files)),
            il=str(len(p.il_files)),
            resources=str(len(p.resources)),
        )

    def gather_issues(self) -> list[Issue]:
        issues: list[Issue] = []
        if not self.project:
            return issues
        if not self.project.files:
            issues.append(
                Issue(
                    "warn", "No SaltStack or Terraform files found in this directory."
                )
            )
        il = self.project.il_files
        if il:
            names = ", ".join(f.name for f in il[:5])
            issues.append(
                Issue("info", f"{len(il)} IL template(s) ready to render: {names}")
            )
        return issues

    def file_rows(self) -> list[FileRow]:
        if not self.project:
            return []
        rows: list[FileRow] = []
        for sf in self.project.files:
            try:
                rel = sf.path.relative_to(self.project.root).as_posix()
            except ValueError:
                rel = sf.name
            rows.append(
                FileRow(
                    name=sf.name,
                    path=rel,
                    type=sf.file_type.value.title(),
                    kind="IL Template" if sf.kind.value == "il" else "Native",
                )
            )
        return rows

    def salt_rows(self) -> list[SaltRow]:
        if not self.project:
            return []
        rows: list[SaltRow] = []
        for sf in self.project.salt_files:
            res = [r for r in self.project.resources if r.source_file == str(sf.path)]
            try:
                rel = sf.path.relative_to(self.project.root).as_posix()
            except ValueError:
                rel = sf.name
            rows.append(
                SaltRow(
                    file=sf.name,
                    path=rel,
                    kind="IL Template" if sf.kind.value == "il" else "Native",
                    states=len(res),
                    modules=", ".join(r.resource_type for r in res[:4]),
                )
            )
        return rows

    def salt_detail(self, rel_path: str) -> SaltDetail | None:
        """Return detail for a salt file identified by relative path."""
        if not self.project:
            return None
        for f in self.project.salt_files:
            try:
                rel = f.path.relative_to(self.project.root).as_posix()
            except ValueError:
                rel = f.name
            if rel == rel_path:
                res = [
                    r for r in self.project.resources if r.source_file == str(f.path)
                ]
                return SaltDetail(
                    name=f.name,
                    content=f.content,
                    language=f.language,
                    resources=[
                        ResourceSummary(
                            id=r.id,
                            type=r.resource_type,
                            name=r.name,
                            props=", ".join(
                                f"{k}={v}" for k, v in list(r.properties.items())[:3]
                            ),
                        )
                        for r in res
                    ],
                )
        return None

    # Module → (label, icon, color)
    _SALT_MODULE_META: ClassVar[dict[str, tuple[str, str, str]]] = {
        "pkg": ("Packages", "inventory_2", "#66BB6A"),
        "service": ("Services", "miscellaneous_services", "#42A5F5"),
        "file": ("Files", "description", "#FFA726"),
        "user": ("Users", "person", "#AB47BC"),
        "group": ("Groups", "group", "#7E57C2"),
        "git": ("Git Repos", "source", "#EF5350"),
        "cmd": ("Commands", "terminal", "#78909C"),
        "pip": ("Pip Packages", "code", "#26C6DA"),
        "cron": ("Cron Jobs", "schedule", "#EC407A"),
        "mount": ("Mounts", "storage", "#8D6E63"),
        "network": ("Network", "wifi", "#5C6BC0"),
    }

    def salt_overview(self) -> SaltOverviewVM:
        """Build a complete Salt overview with categories and requisites."""
        if not self.project:
            return SaltOverviewVM(
                has_project=False,
                total_states=0,
                total_packages=0,
                total_services=0,
                total_files=0,
                categories=[],
                requisites=[],
                unique_packages=[],
                unique_services=[],
            )

        salt_res = [r for r in self.project.resources if r.provider == "salt"]

        # Group by module
        by_module: dict[str, list[IaCResource]] = {}
        for r in salt_res:
            mod = r.properties.get("__module", r.resource_type.split(".")[0])
            by_module.setdefault(mod, []).append(r)

        categories: list[SaltCategory] = []
        for mod, resources in sorted(by_module.items()):
            label, icon, color = self._SALT_MODULE_META.get(
                mod,
                (mod.title(), "extension", "#90A4AE"),
            )
            items: list[SaltCategoryItem] = []
            for r in resources:
                func = r.properties.get("__function", "")
                # Build key props string (skip internal keys)
                kp = ", ".join(
                    f"{k}={v}"
                    for k, v in list(r.properties.items())[:5]
                    if not k.startswith("__")
                    and k
                    not in (
                        "require",
                        "watch",
                        "onchanges",
                        "onfail",
                        "prereq",
                        "listen",
                        "name",
                    )
                )
                src = (
                    r.source_file.split("/")[-1]
                    if "/" in r.source_file
                    else r.source_file.split("\\")[-1]
                )
                items.append(
                    SaltCategoryItem(
                        state_id=r.id,
                        name=r.name,
                        action=func,
                        source_file=src,
                        line=r.source_line,
                        key_props=kp,
                    )
                )
            categories.append(
                SaltCategory(
                    module=mod,
                    label=label,
                    icon=icon,
                    color=color,
                    items=items,
                )
            )

        # Collect requisites
        requisites: list[SaltRequisite] = []
        for r in salt_res:
            reqs = r.properties.get("__requisites", [])
            src = (
                r.source_file.split("/")[-1]
                if "/" in r.source_file
                else r.source_file.split("\\")[-1]
            )
            for req in reqs:
                requisites.append(
                    SaltRequisite(
                        from_state=r.id,
                        relation=req.get("type", ""),
                        to_module=req.get("module", ""),
                        to_state=req.get("state", ""),
                        source_file=src,
                    )
                )

        # Unique package names
        pkg_resources = by_module.get("pkg", [])
        unique_pkgs = sorted({r.name for r in pkg_resources})

        # Unique service names
        svc_resources = by_module.get("service", [])
        unique_svcs = sorted({r.name for r in svc_resources})

        # Count by well-known modules
        file_resources = by_module.get("file", [])

        return SaltOverviewVM(
            has_project=True,
            total_states=len(salt_res),
            total_packages=len(pkg_resources),
            total_services=len(svc_resources),
            total_files=len(file_resources),
            categories=categories,
            requisites=requisites,
            unique_packages=unique_pkgs,
            unique_services=unique_svcs,
        )

    def tf_rows(self) -> list[TfRow]:
        if not self.project:
            return []
        files = self.project.tf_files
        resources = self.project.resources
        tf_res = [
            r for r in resources if any(str(f.path) == r.source_file for f in files)
        ]
        return [
            TfRow(
                id=r.id,
                type=r.resource_type,
                name=r.name,
                provider=r.provider or "",
                file=(
                    r.source_file.split("/")[-1]
                    if "/" in r.source_file
                    else r.source_file.split("\\")[-1]
                ),
                line=r.source_line or "",
            )
            for r in tf_res
        ]

    def tf_detail(self, resource_id: str) -> TfDetail | None:
        if not self.project:
            return None
        for r in self.project.resources:
            if r.id == resource_id:
                return TfDetail(
                    type=r.resource_type,
                    name=r.name,
                    properties=[
                        PropertyPair(key=k, value=str(v))
                        for k, v in r.properties.items()
                    ],
                )
        return None

    def rendered_file_rows(self) -> list[RenderedFileRow]:
        output_dir = self.project.output_dir if self.project else None
        if not output_dir or not output_dir.exists():
            return []
        files = sorted(f for f in output_dir.rglob("*") if f.is_file())
        rows: list[RenderedFileRow] = []
        for f in files:
            try:
                rel = f.relative_to(output_dir).as_posix()
            except ValueError:
                rel = f.name
            rows.append(
                RenderedFileRow(
                    name=f.name,
                    path=rel,
                    size=f"{f.stat().st_size:,} B",
                )
            )
        return rows

    def editable_file_rows(self) -> list[EditableFileRow]:
        """Return a list of rows for files that can be edited."""
        if not self.project:
            return []
        rows: list[EditableFileRow] = []
        for sf in self.project.files:
            try:
                rel = sf.path.relative_to(self.project.root).as_posix()
            except ValueError:
                rel = sf.name
            rows.append(
                EditableFileRow(
                    name=sf.name,
                    path=rel,
                    type=sf.file_type.value.title(),
                    kind="IL Template" if sf.kind.value == "il" else "Native",
                    language=sf.language,
                )
            )
        return rows

    def get_file_content(self, rel_path: str) -> FileContent | None:
        """Return file content and metadata for the editor."""
        if not self.project:
            return None
        for sf in self.project.files:
            try:
                rel = sf.path.relative_to(self.project.root).as_posix()
            except ValueError:
                rel = sf.name
            if rel == rel_path:
                return FileContent(
                    name=sf.name,
                    path=rel,
                    abs_path=str(sf.path),
                    content=sf.content,
                    language=sf.language,
                    kind="IL Template" if sf.kind.value == "il" else "Native",
                    type=sf.file_type.value.title(),
                )
        return None

    def save_file_content(self, rel_path: str, content: str) -> bool:
        """Write *content* back to disk and update in-memory state.

        Returns True on success, False if the file is not found.
        """
        if not self.project:
            return False
        for sf in self.project.files:
            try:
                rel = sf.path.relative_to(self.project.root).as_posix()
            except ValueError:
                rel = sf.name
            if rel == rel_path:
                sf.path.write_text(content, encoding="utf-8")
                sf.content = content
                log.info("Saved %s (%d chars)", sf.path, len(content))
                return True
        return False


_TF_ICONS: dict[str, str] = {
    "vpc": "cloud",
    "subnet": "lan",
    "instance": "dns",
    "security_group": "shield",
    "db_instance": "storage",
    "internet_gateway": "public",
    "nat_gateway": "router",
    "route_table": "alt_route",
    "load_balancer": "mediation",
    "s3_bucket": "inventory_2",
    "iam_role": "badge",
    "lambda_function": "bolt",
}

_SALT_ICONS: dict[str, str] = {
    "pkg": "inventory_2",
    "service": "play_circle",
    "file": "description",
    "cmd": "terminal",
    "git": "source",
    "user": "person",
    "group": "group",
    "cron": "schedule",
    "mount": "hard_drive",
    "pip": "downloading",
    "gem": "diamond",
    "npm": "javascript",
    "archive": "folder_zip",
}

_SALT_COLORS: dict[str, str] = {
    "pkg": "#66BB6A",
    "service": "#FFA726",
    "file": "#AB47BC",
    "cmd": "#EF5350",
    "git": "#42A5F5",
    "user": "#26C6DA",
    "group": "#26A69A",
}


def _tf_icon(resource_type: str) -> str:
    """Return a Material icon name for a Terraform resource type."""
    rt = resource_type.lower()
    for key, icon in _TF_ICONS.items():
        if key in rt:
            return icon
    return "cloud"


def _salt_icon(module: str) -> str:
    return _SALT_ICONS.get(module, "extension")


def _salt_color(module: str) -> str:
    return _SALT_COLORS.get(module, "#78909C")
