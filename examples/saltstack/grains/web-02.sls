# ── Grains: web-02 ─────────────────────────────────────────
# Minion: web-02.example.com — Nginx reverse proxy

roles:
  - webserver

datacenter: us-east-1b
environment: production
tier: frontend

hardware:
  cpu_count: 2
  memory_gb: 4
  disk_gb: 50
  instance_type: t3.medium

network:
  public_ip: 10.0.1.11
  private_ip: 10.0.10.11
  subnet: public

managed_by: saltstack
provisioned_by: terraform
