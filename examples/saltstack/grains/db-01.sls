# ── Grains: db-01 ──────────────────────────────────────────
# Minion: db-01.example.com — PostgreSQL primary + PgBouncer

roles:
  - database

datacenter: us-east-1a
environment: production
tier: data

hardware:
  cpu_count: 8
  memory_gb: 32
  disk_gb: 500
  disk_type: io2
  instance_type: r6g.2xlarge

network:
  private_ip: 10.0.30.10
  subnet: private-data

managed_by: saltstack
provisioned_by: terraform
