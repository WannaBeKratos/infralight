"""Infralight — entry point.

Wires Controllers → Views inside a shared layout shell.
"""

from __future__ import annotations

import logging

from nicegui import ui

from infralight.components.layout import page_layout
from infralight.controllers.app_controller import AppController
from infralight.controllers.dashboard_controller import DashboardController
from infralight.controllers.editor_controller import EditorController
from infralight.controllers.output_controller import OutputController
from infralight.controllers.resources_controller import ResourcesController
from infralight.controllers.salt_overview_controller import SaltOverviewController
from infralight.controllers.states_controller import StatesController
from infralight.controllers.vis_controller import VisController
from infralight.pages import (
    dashboard,
    editor,
    output,
    resources,
    salt_overview,
    states,
    visualization,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")


@ui.page("/")
def page_dashboard():
    state = AppController.build_state()
    app_ctrl = AppController(state)
    with page_layout(app_ctrl, active="/"):
        vm = DashboardController(state).get_view_model()
        dashboard.render(vm)


@ui.page("/states")
def page_states():
    state = AppController.build_state()
    app_ctrl = AppController(state)
    ctrl = StatesController(state)
    with page_layout(app_ctrl, active="/states"):
        vm = ctrl.get_view_model()
        detail_container = ui.column().classes("w-full")

        def _on_select(event):
            sel = event.selection if hasattr(event, "selection") else []
            if not sel:
                return
            path = sel[0].get("path", "")
            detail = ctrl.get_detail(path)
            states.render_detail(detail, detail_container)

        states.render(vm, on_select=_on_select)


@ui.page("/salt-overview")
def page_salt_overview():
    state = AppController.build_state()
    app_ctrl = AppController(state)
    with page_layout(app_ctrl, active="/salt-overview"):
        vm = SaltOverviewController(state).get_view_model()
        salt_overview.render(vm)


@ui.page("/resources")
def page_resources():
    state = AppController.build_state()
    app_ctrl = AppController(state)
    ctrl = ResourcesController(state)
    with page_layout(app_ctrl, active="/resources"):
        vm = ctrl.get_view_model()
        detail_container = ui.column().classes("w-full")

        def _on_select(event):
            sel = event.selection if hasattr(event, "selection") else []
            if not sel:
                return
            rid = sel[0].get("id", "")
            detail = ctrl.get_detail(rid)
            resources.render_detail(detail, detail_container)

        resources.render(vm, on_select=_on_select)


@ui.page("/visualization")
def page_visualization():
    state = AppController.build_state()
    app_ctrl = AppController(state)
    with page_layout(app_ctrl, active="/visualization"):
        vm = VisController(state).get_view_model()
        visualization.render(vm)


@ui.page("/output")
def page_output():
    state = AppController.build_state()
    app_ctrl = AppController(state)
    with page_layout(app_ctrl, active="/output"):
        vm = OutputController(state).get_view_model()
        output.render(vm)


@ui.page("/editor")
def page_editor(file: str = ""):
    state = AppController.build_state()
    app_ctrl = AppController(state)
    ctrl = EditorController(state)
    with page_layout(app_ctrl, active="/editor"):
        editor.render(ctrl, initial_file=file)


ui.run(
    title="Infralight",
    port=8080,
    dark=True,
    reload=True,
    storage_secret="infralight-secret-key-change-me",
)
