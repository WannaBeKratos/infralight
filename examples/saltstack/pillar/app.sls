# ── App server pillar ─────────────────────────────────────

app:
  repo: https://github.com/acme/webapp.git
  branch: main
  port: 3000
  node_env: production
  workers: 4

  env_vars:
    DATABASE_URL: "postgresql://app_user:{{ pillar['db_password'] }}@db-01:6432/infralight_prod"
    REDIS_URL: "redis://cache-01:6379/0"
    SESSION_SECRET: "ch4ng3-m3-1n-pr0duct10n"
    LOG_LEVEL: info
