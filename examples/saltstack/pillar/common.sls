# ── Common pillar data — all minions ──────────────────────

domain: app.example.com
admin_email: ops@example.com
environment: production
datacenter: us-east-1

dns_servers:
  - 10.0.0.2
  - 10.0.0.3

ntp_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org

allowed_ssh_keys:
  - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFakeKeyForDemoOnly deploy@infra
  - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAnotherFakeKeyHere admin@infra
