# ── Grains: app-02 ─────────────────────────────────────────
# Minion: app-02.example.com — Node.js application server

roles:
  - appserver

datacenter: us-east-1b
environment: production
tier: application

hardware:
  cpu_count: 4
  memory_gb: 8
  disk_gb: 100
  instance_type: t3.large

network:
  private_ip: 10.0.20.11
  subnet: private

managed_by: saltstack
provisioned_by: terraform
