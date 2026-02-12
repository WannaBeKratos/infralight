# ── Grains: lb-01 ──────────────────────────────────────────
# Minion: lb-01.example.com — HAProxy load balancer

roles:
  - loadbalancer

datacenter: us-east-1a
environment: production
tier: edge

hardware:
  cpu_count: 2
  memory_gb: 4
  disk_gb: 50
  instance_type: t3.medium

network:
  public_ip: 10.0.1.5
  private_ip: 10.0.10.5
  subnet: public

managed_by: saltstack
provisioned_by: terraform
