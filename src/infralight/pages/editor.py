"""Editor view — visual file editor with syntax highlighting.

Pure view — receives an EditorController, renders a file tree
(no selection boxes) and a code editor.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nicegui import ui

from infralight.components.empty_state import empty_state
from infralight.components.file_tree import file_tree
from infralight.components.panel import panel
from infralight.components.theme import COLORS
from infralight.models.viewmodels import FileContent

if TYPE_CHECKING:
    from infralight.controllers.editor_controller import EditorController


def render(ctrl: EditorController, *, initial_file: str = "") -> None:
    """Render the editor page.

    *initial_file* — relative path to auto-open on load (from query param).
    """
    vm = ctrl.get_view_model()

    if not vm.has_project:
        empty_state(
            "folder_open", "No project open — use the sidebar to load a project"
        )
        return
    editor_container = ui.column().classes("w-full")
    current_path: dict[str, str] = {}  # mutable box for closure

    def _open_file(rel_path: str) -> None:
        """Load a file into the editor panel."""
        detail = ctrl.get_file_content(rel_path)
        if not detail:
            ui.notify(f"Could not load {rel_path}", type="warning")
            return
        current_path["path"] = rel_path
        _render_editor(detail)

    def _render_editor(detail: FileContent) -> None:
        """Fill the editor container with a code editor for *detail*."""
        editor_container.clear()
        with (
            editor_container,
            panel(
                detail.name,
                icon="edit_note",
                color=COLORS["salt"]
                if detail.type == "Saltstack"
                else COLORS["terraform"],
                badge=detail.kind,
            ),
        ):
            # Info bar
            with ui.row().classes("w-full items-center q-gutter-sm q-mb-sm"):
                ui.icon("folder", size="xs", color="grey-6")
                ui.label(detail.path).classes("text-caption text-grey-5")
                ui.space()
                ui.badge(detail.language.upper(), color="grey-8").props("dense outline")

            # Map file language to CodeMirror language
            cm_lang = "YAML" if detail.language == "yaml" else "Properties files"

            # Code editor
            cm = (
                ui.codemirror(detail.content, language=cm_lang)
                .classes("w-full")
                .props('style="min-height:400px; max-height:70vh;"')
            )

            # Action buttons
            with ui.row().classes("w-full justify-end q-gutter-sm q-mt-sm"):
                ui.button(
                    "Revert",
                    icon="undo",
                    on_click=lambda: _open_file(current_path["path"]),
                ).props("flat dense no-caps color=grey-5 size=sm")

                def _save() -> None:
                    ctrl.save_file(current_path["path"], cm.value)

                ui.button("Save", icon="save", on_click=_save).props(
                    "dense no-caps color=deep-purple-8 size=sm"
                )

    with ui.row().classes("w-full q-gutter-md"):
        # Left: file tree
        with ui.column().classes("col-3"):
            with panel(
                "Project Files",
                icon="description",
                color=COLORS["info"],
                badge=str(vm.count),
            ):
                if not vm.files:
                    empty_state("description", "No files found in project")
                else:
                    proj = ctrl.state.project
                    if proj:
                        with (
                            ui.scroll_area()
                            .classes("w-full")
                            .style("max-height: 65vh;")
                        ):
                            file_tree(proj, on_select=_open_file)

        # Right: editor area
        with ui.column().classes("col"):
            if not initial_file:
                with editor_container:
                    empty_state("edit_note", "Click a file in the tree to edit it")
            else:
                _open_file(initial_file)
