"""Visualization controller — builds the graph view-models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from infralight.models.viewmodels import (
    InfraVisVM,
    VisEdgeVM,
    VisGroupVM,
    VisNodeVM,
    VisVM,
)

if TYPE_CHECKING:
    from infralight.core.models import Visualization
    from infralight.models.state import AppState


class VisController:
    """Builds three visualization sub-graphs: Terraform, Salt, IL Decorators."""

    def __init__(self, state: AppState) -> None:
        self.state = state

    def get_view_model(self) -> InfraVisVM:
        il_vis = self.state.build_visualization()
        tf_vis = self.state.build_tf_graph()
        salt_vis = self.state.build_salt_graph()

        return InfraVisVM(
            il_graph=self._to_vm(il_vis),
            tf_graph=self._to_vm(tf_vis),
            salt_graph=self._to_vm(salt_vis),
        )

    @staticmethod
    def _to_vm(vis: Visualization) -> VisVM:
        return VisVM(
            nodes=[
                VisNodeVM(id=n.id, label=n.label, group=n.group or "", icon=n.icon)
                for n in vis.nodes
            ],
            edges=[
                VisEdgeVM(src=e.source, tgt=e.target, label=e.label, style=e.style)
                for e in vis.edges
            ],
            groups=[VisGroupVM(id=g.id, label=g.label) for g in vis.groups],
            mermaid=vis.to_mermaid() if (vis.nodes or vis.edges) else "",
            layout=vis.layout,
            has_data=bool(vis.nodes or vis.edges),
        )
