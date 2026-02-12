# ── Grains: web-01 ─────────────────────────────────────────
# Minion: web-01.example.com — Nginx reverse proxy

roles:
  - webserver

datacenter: us-east-1a
environment: production
tier: frontend

hardware:
  cpu_count: 2
  memory_gb: 4
  disk_gb: 50
  instance_type: t3.medium

network:
  public_ip: 10.0.1.10
  private_ip: 10.0.10.10
  subnet: public

managed_by: saltstack
provisioned_by: terraform
