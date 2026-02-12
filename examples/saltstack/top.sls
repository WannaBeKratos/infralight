# ── SaltStack Top File ────────────────────────────────────
# Maps minion roles (via grains) to state files.

base:
  '*':
    - common

  'roles:webserver':
    - match: grain
    - webserver
    - nginx
    - certbot

  'roles:appserver':
    - match: grain
    - appserver
    - nodejs
    - pm2

  'roles:database':
    - match: grain
    - database
    - postgresql
    - pgbouncer

  'roles:cache':
    - match: grain
    - redis

  'roles:monitoring':
    - match: grain
    - monitoring
    - prometheus
    - grafana

  'roles:loadbalancer':
    - match: grain
    - haproxy
