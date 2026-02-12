# ── Pillar Top File ───────────────────────────────────────
# Maps minion roles to pillar data.

base:
  '*':
    - common

  'roles:webserver':
    - match: grain
    - web

  'roles:appserver':
    - match: grain
    - app

  'roles:database':
    - match: grain
    - database

  'roles:monitoring':
    - match: grain
    - monitoring
