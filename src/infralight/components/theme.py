"""Theme — colour tokens and Quasar style setup."""

from nicegui import ui

COLORS = {
    "salt": "orange-6",
    "terraform": "light-blue-5",
    "il": "purple-4",
    "vis": "cyan-5",
    "positive": "green-5",
    "negative": "red-5",
    "info": "light-blue-5",
    "warning": "orange-6",
    "neutral": "blue-grey-5",
}


def inject_theme() -> None:
    """Call once per page — sets Quasar dark colours, no custom layout CSS."""
    ui.colors(
        primary="#7c4dff",
        secondary="#bb86fc",
        accent="#ce93d8",
        dark="#121212",
        dark_page="#0d0d1a",
        positive="#66bb6a",
        negative="#ef5350",
        info="#4fc3f7",
        warning="#ffb74d",
    )
    # Make Mermaid diagrams render larger with more spacing
    ui.add_head_html("""
    <style>
    /* Let the mermaid container grow to fit the diagram */
    .mermaid { overflow: hidden; }
    .mermaid svg {
        min-height: 600px !important;
        height: auto !important;
        max-height: none !important;
    }
    .mermaid .node rect, .mermaid .node polygon { rx: 8; ry: 8; }
    /* Quasar tab-panels must not clip children */
    .q-tab-panels, .q-tab-panel { overflow: visible !important; }
    /* Zoom container */
    .mermaid-zoom-container {
        position: relative;
        border: 1px solid #333;
        border-radius: 8px;
        overflow: hidden;
        min-height: 600px;
        cursor: grab;
    }
    .mermaid-zoom-container:active { cursor: grabbing; }
    .mermaid-zoom-controls {
        position: absolute; top: 8px; right: 8px; z-index: 10;
        display: flex; gap: 4px;
    }
    .mermaid-zoom-controls button {
        width: 32px; height: 32px; border-radius: 6px;
        border: 1px solid #555; background: #1e1e2e; color: #ccc;
        cursor: pointer; font-size: 16px; display: flex;
        align-items: center; justify-content: center;
    }
    .mermaid-zoom-controls button:hover { background: #333; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/panzoom@9.4.3/dist/panzoom.min.js"></script>
    """)
