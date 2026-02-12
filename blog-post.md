# Introducing Infralight: A Visual Dashboard for SaltStack & Terraform

**Infrastructure-as-Code is powerful. Understanding it shouldn't require a PhD.**

If you've ever stared at a sprawling directory of `.sls` and `.tf` files wondering which services depend on what, which packages are installed where, or how your states connect to each other — Infralight was built for you.

## The Problem

SaltStack and Terraform are exceptional tools for managing infrastructure. But as projects grow, so does the cognitive load. You end up with dozens of state files, hundreds of resources, and a web of dependencies that lives entirely in your head (or worse, in tribal knowledge that walks out the door when someone leaves the team).

Existing tools either require a running Salt Master to inspect state, or they only handle Terraform. There's no lightweight way to just *point at a directory* and immediately see what's inside.

## What Infralight Does

Infralight is an open-source, browser-based dashboard that scans your project directory and gives you instant visibility into your infrastructure code — no Salt Master required, no Terraform state files needed.

Drop it into any directory containing `.sls` or `.tf` files, and within seconds you get:

### A Dashboard at a Glance

The main dashboard shows file counts, resource totals, and potential issues. It's the 30-second health check for your IaC codebase.

### Salt States Browser

Every SaltStack file is listed with its state count and the modules it uses. Click any file to inspect its parsed states, see the raw YAML, and understand what each state ID does — all without opening a terminal.

### Salt Overview — The Feature You Didn't Know You Needed

This is where Infralight really shines. The Salt Overview page categorises every resource by module type:

- **Packages** — Every `pkg.installed`, `pkg.latest`, `pkg.purged` in your project, listed and deduplicated. At a glance, you can see that your infrastructure depends on `nginx`, `postgresql`, `redis-server`, and `python3-pip`. No grepping required.

- **Services** — Every `service.running`, `service.enabled`, `service.dead`. See which services are managed, which are enabled at boot, and where they're defined.

- **Files** — `file.managed`, `file.directory`, `file.symlink` — the full picture of what Salt is putting on disk.

- **Commands, Git Repos, Users, Groups, Cron Jobs, Pip Packages, Mounts, Network** — every Salt module category gets its own tab with a sortable, filterable table.

And then there's the **dependency graph**. Infralight parses all requisites — `require`, `watch`, `onchanges`, `listen`, and their `_in` variants — and shows you a table of every state-to-state dependency. You can finally answer "what breaks if I remove this package?" without tracing through YAML by hand.

### Terraform Resources

Terraform gets the same treatment. Resources, data sources, variables, outputs, and modules are all parsed and displayed with their properties, provider, source file, and line number. Click any resource to drill into its attributes.

### Infrastructure Visualisation

Here's the twist: Infralight introduces **IL decorators** — Jinja2 template functions you embed directly in your IaC files:

```yaml
{{ il_group("web", label="Web Tier", icon="globe", color="#42A5F5") }}
{{ il_node("nginx", label="Nginx LB", icon="dns", group="web") }}

nginx:
  pkg.installed:
    - name: nginx
  service.running:
    - enable: True

{{ il_edge("nginx", "app", label="proxy_pass :8080") }}
```

These decorators render to empty strings — your output is still valid SaltStack YAML or Terraform HCL. But Infralight reads them and generates an interactive architecture diagram showing how your components connect.

No separate diagramming tool. No stale Confluence page. The diagram lives *in the code* and updates every time you edit.

### Built-in File Editor

Edit your SaltStack and Terraform files directly in the browser with syntax-highlighted CodeMirror. Save, revert, and immediately see the parsed results update.

### Render Pipeline

IL template files (`.il.sls`, `.il.tf`) get rendered to clean output files with all decorator lines stripped. The output directory contains production-ready IaC — no Infralight dependencies at deploy time.

## The Tech Stack

Infralight is a Python application with a deliberately minimal dependency footprint:

- **NiceGUI** — Python-to-browser framework built on Vue 3 and Quasar
- **Jinja2** — Template rendering for IL decorators
- **PyYAML** — SaltStack state parsing
- **Regex-based HCL parsing** — No external HCL library needed for Terraform

No database. No external services. No containers required (though a Dockerfile is included). Install with `pip install -e .` and run with `python -m infralight.main`.

The architecture follows a clean MVC pattern with typed dataclasses throughout — every piece of data flowing between layers has an explicit, documented type. Controllers return typed view-models, views use dot-access instead of magic string keys, and the model layer is completely decoupled from the UI.

## Who Is This For?

- **Platform engineers** who want a quick visual inventory of what Salt or Terraform is managing across a project
- **DevOps teams** onboarding new members who need to understand an existing IaC codebase
- **Architects** who want living diagrams that stay in sync with the actual infrastructure code
- **Anyone** tired of grepping through YAML to answer "what packages does this project install?"

## Getting Started

```bash
git clone https://github.com/your-org/infralight.git
cd infralight
python -m venv .venv
.venv/Scripts/activate      # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -e .
python -m infralight.main
```

Open `http://localhost:8080`, click **Open Folder**, and point at any directory with `.sls` or `.tf` files. That's it.

## What's Next

Infralight is at v0.1.0 and already useful for daily work. On the roadmap:

- **Pillar data visualisation** — Show pillar values alongside the states that consume them
- **Grain-based filtering** — View states as they'd apply to specific minion profiles
- **Terraform plan integration** — Overlay `terraform plan` output on the resource view
- **Export** — Generate standalone HTML reports and SVG diagrams for documentation
- **Salt Master API** — Optionally connect to a live Salt Master for real-time minion state

## Open Source

Infralight is MIT-licensed. Contributions, issues, and feature requests are welcome.

Infrastructure code deserves the same visibility tools that application code has had for decades. Infralight is a step toward making IaC not just writable, but *readable*.

---

*Infralight — see your infrastructure.*
