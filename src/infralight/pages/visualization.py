"""Visualization view — renders the infrastructure graph.

Pure view — receives data from VisController.
Three tabs: Terraform, Salt, and IL Decorators.
"""

from __future__ import annotations

from nicegui import ui

from infralight.components.data_table import data_table
from infralight.components.empty_state import empty_state
from infralight.components.panel import panel
from infralight.components.theme import COLORS
from infralight.models.viewmodels import InfraVisVM, VisVM, rows_to_dicts


def render(vm: InfraVisVM) -> None:
    """Render visualization page from *vm* (from VisController)."""

    with (
        ui.tabs()
        .classes("w-full")
        .props("dense align=left active-color=primary") as tabs
    ):
        ui.tab("terraform", label="Terraform", icon="cloud")
        ui.tab("salt", label="Salt", icon="terminal")
        ui.tab("il", label="IL Decorators", icon="auto_fix_high")

    with ui.tab_panels(tabs, value="terraform").classes("w-full"):
        with ui.tab_panel("terraform"):
            _graph_section(
                vm.tf_graph,
                "Terraform Graph",
                "Auto-generated from Terraform resources and references",
            )
        with ui.tab_panel("salt"):
            _graph_section(
                vm.salt_graph,
                "Salt Graph",
                "Auto-generated from Salt states and requisites",
            )
        with ui.tab_panel("il"):
            _graph_section(
                vm.il_graph,
                "IL Decorator Graph",
                "Only nodes and edges declared via il_node / il_edge decorators",
            )


def _graph_section(vm: VisVM, title: str, subtitle: str) -> None:
    """Render a full graph panel + tables for one sub-graph."""
    _graph_panel(vm, title, subtitle)
    _tables(vm)


def _graph_panel(vm: VisVM, title: str, subtitle: str) -> None:
    with panel(title, icon="hub", color=COLORS["vis"]):
        ui.label(subtitle).classes("text-caption text-grey-7 q-mb-sm")

        if not vm.has_data:
            empty_state(
                "hub",
                "No graph data",
                "Load a project with Terraform / Salt files or IL decorators",
            )
            return

        # Mermaid diagram — let NiceGUI render it, then wrap in panzoom
        cid = f"mermaid-zoom-{id(vm)}"
        zoom_in = f"window._mzZoom('{cid}', 1.3)"
        zoom_out = f"window._mzZoom('{cid}', 0.7)"
        reset = f"window._mzReset('{cid}')"
        ui.html(
            f'<div id="{cid}" class="mermaid-zoom-container">'
            '<div class="mermaid-zoom-controls">'
            f'<button onclick="{zoom_in}" title="Zoom in">+</button>'
            f'<button onclick="{zoom_out}" title="Zoom out">&minus;</button>'
            f'<button onclick="{reset}" title="Reset">&#8634;</button>'
            "</div>"
            '<div class="mermaid-zoom-inner"></div>'
            "</div>"
        ).classes("w-full q-pa-sm")

        # Hidden NiceGUI mermaid element — once it renders, move its SVG
        # into our zoom container and attach panzoom.
        m_el = ui.mermaid(vm.mermaid).classes("hidden")
        nicegui_id = f"c{m_el.id}"

        # Repeating timer — hidden tabs aren't in the DOM until
        # the user switches to them, so we keep checking until the
        # SVG appears.  The ``dataset.rendered`` guard makes repeat
        # ticks effectively free.
        ui.timer(
            1.0,
            lambda cid=cid, nid=nicegui_id: ui.run_javascript(f"""
            (function() {{
                const wrap = document.getElementById('{cid}');
                const src  = document.getElementById('{nid}');
                if (!wrap || !src) return;
                const inner = wrap.querySelector('.mermaid-zoom-inner');
                if (!inner || inner.dataset.rendered) return;

                const svg = src.querySelector('svg');
                if (!svg) return;
                inner.dataset.rendered = '1';

                // Move the rendered SVG into our zoom container
                inner.appendChild(svg.cloneNode(true));
                const cloned = inner.querySelector('svg');
                if (cloned) {{
                    cloned.removeAttribute('height');
                    cloned.style.height = 'auto';
                    cloned.style.minHeight = '600px';
                    cloned.style.maxHeight = 'none';
                }}

                // Attach panzoom
                if (typeof panzoom !== 'undefined') {{
                    const pz = panzoom(inner, {{
                        maxZoom: 5, minZoom: 0.2, smoothScroll: false,
                        bounds: true, boundsPadding: 0.3
                    }});
                    wrap._pz = pz;
                }}
            }})();

            // Global helpers for zoom buttons
            window._mzZoom = window._mzZoom || function(id, factor) {{
                const w = document.getElementById(id);
                if (w && w._pz) {{
                    const cx = w.offsetWidth / 2, cy = w.offsetHeight / 2;
                    w._pz.smoothZoom(cx, cy, factor);
                }}
            }};
            window._mzReset = window._mzReset || function(id) {{
                const w = document.getElementById(id);
                if (w && w._pz) {{ w._pz.moveTo(0, 0); w._pz.zoomAbs(0, 0, 1); }}
            }};
        """),
        )

        with ui.row().classes("w-full items-center q-mt-sm"):
            ui.label(
                f"Layout: {vm.layout}  ·  {len(vm.nodes)} nodes  ·  "
                f"{len(vm.edges)} edges  ·  {len(vm.groups)} groups"
            ).classes("text-caption text-grey-7")
            ui.space()
            code = vm.mermaid
            ui.button(
                "Copy Mermaid", icon="content_copy", on_click=lambda: _copy(code)
            ).props("flat dense size=sm color=grey-6")


def _copy(text: str) -> None:
    ui.run_javascript(f"navigator.clipboard.writeText({text!r})")
    ui.notify("Copied to clipboard", type="positive", position="bottom", timeout=1500)


def _tables(vm: VisVM) -> None:
    if not vm.has_data:
        return

    with ui.row().classes("w-full q-gutter-md"):
        with ui.column().classes("col"):
            with panel(
                "Nodes", icon="circle", color=COLORS["vis"], badge=str(len(vm.nodes))
            ):
                if vm.nodes:
                    data_table(
                        columns=[
                            {
                                "name": "id",
                                "label": "ID",
                                "field": "id",
                                "align": "left",
                            },
                            {
                                "name": "label",
                                "label": "Label",
                                "field": "label",
                                "align": "left",
                            },
                            {
                                "name": "group",
                                "label": "Group",
                                "field": "group",
                                "align": "left",
                            },
                            {"name": "icon", "label": "Icon", "field": "icon"},
                        ],
                        rows=rows_to_dicts(vm.nodes),
                        row_key="id",
                    )
                else:
                    empty_state("circle", "No nodes")

        with ui.column().classes("col"):
            with panel(
                "Edges",
                icon="arrow_forward",
                color=COLORS["vis"],
                badge=str(len(vm.edges)),
            ):
                if vm.edges:
                    data_table(
                        columns=[
                            {
                                "name": "src",
                                "label": "From",
                                "field": "src",
                                "align": "left",
                            },
                            {
                                "name": "tgt",
                                "label": "To",
                                "field": "tgt",
                                "align": "left",
                            },
                            {
                                "name": "label",
                                "label": "Label",
                                "field": "label",
                                "align": "left",
                            },
                            {"name": "style", "label": "Style", "field": "style"},
                        ],
                        rows=rows_to_dicts(vm.edges),
                        row_key="src",
                    )
                else:
                    empty_state("arrow_forward", "No edges")

    if vm.groups:
        with panel(
            "Groups", icon="folder", color=COLORS["vis"], badge=str(len(vm.groups))
        ):
            data_table(
                columns=[
                    {"name": "id", "label": "ID", "field": "id", "align": "left"},
                    {
                        "name": "label",
                        "label": "Label",
                        "field": "label",
                        "align": "left",
                    },
                ],
                rows=rows_to_dicts(vm.groups),
                row_key="id",
            )
