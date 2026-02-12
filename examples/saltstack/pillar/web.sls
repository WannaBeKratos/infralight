# ── Web server pillar ─────────────────────────────────────

nginx:
  worker_processes: auto
  worker_connections: 4096
  keepalive_timeout: 65
  client_max_body_size: 50M

  upstream_servers:
    - app-01:3000
    - app-02:3000

ssl:
  protocols: TLSv1.2 TLSv1.3
  ciphers: ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
