{{ il_group("lb", label="Load Balancing", icon="mediation", color="#26C6DA") }}
{{ il_group("web", label="Web Tier", icon="dns", color="#42A5F5") }}
{{ il_group("app", label="Application Tier", icon="code", color="#66BB6A") }}
{{ il_group("data", label="Data Tier", icon="storage", color="#FF7043") }}
{{ il_group("monitor", label="Monitoring", icon="monitoring", color="#AB47BC") }}

{{ il_node("haproxy", label="HAProxy LB", icon="mediation", group="lb") }}
{{ il_node("nginx1", label="Nginx Web 1", icon="dns", group="web") }}
{{ il_node("nginx2", label="Nginx Web 2", icon="dns", group="web") }}
{{ il_node("certbot", label="Certbot TLS", icon="lock", group="web") }}
{{ il_node("app1", label="App Server 1", icon="code", group="app") }}
{{ il_node("app2", label="App Server 2", icon="code", group="app") }}
{{ il_node("pm2", label="PM2 Manager", icon="play_circle", group="app") }}
{{ il_node("postgres", label="PostgreSQL 16", icon="database", group="data") }}
{{ il_node("pgbouncer", label="PgBouncer Pool", icon="sync", group="data") }}
{{ il_node("redis", label="Redis Cache", icon="memory", group="data") }}
{{ il_node("prometheus", label="Prometheus", icon="monitoring", group="monitor") }}
{{ il_node("grafana", label="Grafana", icon="dashboard", group="monitor") }}
{{ il_node("exporter", label="Node Exporter", icon="sensors", group="monitor") }}

{{ il_edge("haproxy", "nginx1", label="HTTP/HTTPS") }}
{{ il_edge("haproxy", "nginx2", label="HTTP/HTTPS") }}
{{ il_edge("certbot", "nginx1", label="TLS certs") }}
{{ il_edge("certbot", "nginx2", label="TLS certs") }}
{{ il_edge("nginx1", "app1", label="proxy :3000") }}
{{ il_edge("nginx2", "app2", label="proxy :3000") }}
{{ il_edge("pm2", "app1", label="manages", style="dashed") }}
{{ il_edge("pm2", "app2", label="manages", style="dashed") }}
{{ il_edge("app1", "pgbouncer", label="port 6432") }}
{{ il_edge("app2", "pgbouncer", label="port 6432") }}
{{ il_edge("pgbouncer", "postgres", label="pool") }}
{{ il_edge("app1", "redis", label="port 6379", style="dashed") }}
{{ il_edge("app2", "redis", label="port 6379", style="dashed") }}
{{ il_edge("prometheus", "exporter", label="scrape :9100", style="dashed") }}
{{ il_edge("grafana", "prometheus", label="query :9090") }}

{{ il_note("Production infrastructure managed by SaltStack + Infralight") }}

# ── Nginx web servers (web-01, web-02) ────────────────────

nginx:
  pkg.installed:
    - name: nginx
  service.running:
    - name: nginx
    - enable: True
    - require:
      - pkg: nginx

# ── Application deployment ────────────────────────────────

app_deploy:
  git.latest:
    - name: https://github.com/acme/webapp.git
    - target: /srv/app
  cmd.run:
    - name: npm ci --production && pm2 reload ecosystem.config.js
    - cwd: /srv/app
    - require:
      - git: app_deploy

# ── PostgreSQL primary ────────────────────────────────────

postgresql:
  pkg.installed:
    - name: postgresql-16
  service.running:
    - name: postgresql
    - enable: True
    - require:
      - pkg: postgresql

# ── Redis cache ───────────────────────────────────────────

redis:
  pkg.installed:
    - name: redis-server
  service.running:
    - name: redis-server
    - enable: True
    - require:
      - pkg: redis

