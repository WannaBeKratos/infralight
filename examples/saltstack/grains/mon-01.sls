# ── Grains: mon-01 ─────────────────────────────────────────
# Minion: mon-01.example.com — Prometheus + Grafana

roles:
  - monitoring

datacenter: us-east-1a
environment: production
tier: management

hardware:
  cpu_count: 4
  memory_gb: 8
  disk_gb: 200
  instance_type: t3.large

network:
  private_ip: 10.0.40.10
  subnet: private-mgmt

managed_by: saltstack
provisioned_by: terraform
