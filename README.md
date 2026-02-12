# Infralight

**Visualisation and editing tool for SaltStack & Terraform.**

Infralight scans a project directory for `.sls` (SaltStack) and `.tf` (Terraform)
files, parses resources, and presents an interactive dashboard with graphs,
tables, and a code editor — all in the browser via [NiceGUI](https://nicegui.io).

Files with an `.il.sls` or `.il.tf` extension can use special **Infralight
decorators** — Jinja2 functions that add visualisation metadata without affecting
the rendered output.

## Features

| Page | Description |
|---|---|
| **Dashboard** | Stat cards (files, states, resources), issues panel, file overview table |
| **Salt States** | Browsable table of all `.sls` files with state counts, modules, and detail drill-down |
| **Salt Overview** | Categorised view of Salt resources (packages, services, files, commands …) with requisite graph |
| **TF Resources** | Table of all Terraform resources with property detail |
| **Visualization** | Interactive Mermaid graph with pan/zoom — three tabs: Combined, Infrastructure, IL Decorators |
| **File Editor** | File tree + syntax-highlighted CodeMirror editor with save/revert |
| **Render Output** | Shows rendered (decorator-stripped) output files |

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows  (source .venv/bin/activate on *nix)
pip install -e ".[dev]"

# Run the app
python -m infralight.main
```

Open **http://localhost:8080**. The app loads the bundled `examples/` project by
default. Enter a different path in the sidebar to switch projects.

## Project structure

```
src/infralight/
  main.py                  # Routes & ui.run()
  core/
    models.py              # SourceFile, IaCResource, Visualization, Project
    parsers.py             # SaltStack & Terraform parsers
    scanner.py             # Directory scanner
    renderer.py            # IL template renderer (Jinja2)
    decorators.py          # il_node, il_edge, il_group, …
  models/
    state.py               # AppState — all business logic
    viewmodels.py          # Typed dataclass view-models
  controllers/
    app_controller.py      # Project load/rescan
    dashboard_controller.py
    states_controller.py
    resources_controller.py
    vis_controller.py
    output_controller.py
    editor_controller.py
    salt_overview_controller.py
  pages/                   # Pure views (NiceGUI / Quasar widgets)
    dashboard.py, states.py, salt_overview.py, resources.py,
    visualization.py, editor.py, output.py
  components/              # Reusable UI components
    layout.py, sidebar.py, panel.py, stat_card.py,
    data_table.py, empty_state.py, file_tree.py, theme.py
examples/                  # Sample SaltStack + Terraform project (28 files)
tests/
  conftest.py              # Playwright fixture (starts server in subprocess)
  _test_server.py          # Standalone test server entrypoint
  test_playwright.py       # E2E tests (33 tests across all pages)
```

## Infralight decorators

Inside `.il.sls` / `.il.tf` files the following Jinja2 functions are available:

| Decorator | Purpose |
|---|---|
| `{{ il_node(id, label, icon, color, shape, group) }}` | Mark a resource as a graph node |
| `{{ il_edge(source, target, label, style, color) }}` | Connect two nodes |
| `{{ il_group(id, label, icon, color) }}` | Define a visual group |
| `{{ il_note(text, target, color) }}` | Attach an annotation |
| `{{ il_layout(layout) }}` | Set layout algorithm (`dagre` / `elk` / `force` / `grid`) |

All decorators render to an **empty string** so the final output is clean IaC.

### Example — `webserver.il.sls`

```yaml
{{ il_group("web", label="Web Tier", icon="globe", color="#42A5F5") }}
{{ il_node("nginx", label="Nginx LB", icon="dns", group="web") }}

nginx:
  pkg.installed:
    - name: nginx
  service.running:
    - enable: True

{{ il_node("app", label="App Server", icon="code", group="web") }}
{{ il_edge("nginx", "app", label="proxy_pass") }}

app_deploy:
  git.latest:
    - name: https://github.com/acme/app.git
    - target: /srv/app
```

Running **Render** produces a clean `webserver.sls` in the output folder with all
decorator lines stripped.

## Testing

```bash
# Install Playwright browsers (first time only)
playwright install chromium

# Run E2E tests
pytest tests/test_playwright.py -v

# Other checks
ruff check src tests          # lint
ruff format src tests         # format
mypy src                      # type-check
```

## Architecture

Infralight follows a strict **MVC** pattern:

- **Model** — `AppState` dataclass holds all business logic; no UI imports
- **Controller** — class-based, receives `AppState`, returns typed view-model dataclasses
- **View** — pages use only NiceGUI/Quasar widgets with dot-access on view-models

All view-models are stdlib `@dataclass` instances. Tables use `rows_to_dicts()`
to convert dataclass lists to dicts for Quasar's `QTable`.
