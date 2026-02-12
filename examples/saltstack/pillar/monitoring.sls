# ── Monitoring pillar ─────────────────────────────────────

prometheus:
  scrape_interval: 15s
  evaluation_interval: 15s
  retention: 30d
  storage_path: /var/lib/prometheus/data

  scrape_targets:
    - job: node
      targets:
        - web-01:9100
        - web-02:9100
        - app-01:9100
        - app-02:9100
        - db-01:9100
        - cache-01:9100
        - mon-01:9100
        - lb-01:9100

    - job: nginx
      targets:
        - web-01:9113
        - web-02:9113

    - job: postgres
      targets:
        - db-01:9187

    - job: redis
      targets:
        - cache-01:9121

grafana:
  admin_password: "gr4f4n4-4dm1n"
  allow_sign_up: false
  root_url: "https://{{ pillar['domain'] }}/grafana"
