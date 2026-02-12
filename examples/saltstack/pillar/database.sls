# ── Database pillar ───────────────────────────────────────

db_password: "s3cure-pr0d-passw0rd"
db_readonly_password: "r34d-0nly-passw0rd"

postgresql:
  version: 16
  max_connections: 200
  shared_buffers: 2GB
  effective_cache_size: 6GB
  work_mem: 16MB
  maintenance_work_mem: 512MB
  wal_level: replica
  max_wal_senders: 3

pgbouncer:
  pool_mode: transaction
  max_client_conn: 400
  default_pool_size: 40
  listen_port: 6432
