# ── Grains: cache-01 ───────────────────────────────────────
# Minion: cache-01.example.com — Redis cache

roles:
  - cache

datacenter: us-east-1a
environment: production
tier: data

hardware:
  cpu_count: 2
  memory_gb: 16
  disk_gb: 50
  instance_type: r6g.large

network:
  private_ip: 10.0.30.20
  subnet: private-data

managed_by: saltstack
provisioned_by: terraform
