# ── Monitoring stack — Prometheus + node_exporter ─────────
# Deployed on monitoring minions.

prometheus_user:
  user.present:
    - name: prometheus
    - shell: /usr/sbin/nologin
    - system: True
    - home: /var/lib/prometheus

/etc/prometheus:
  file.directory:
    - user: prometheus
    - group: prometheus
    - mode: '0755'
    - makedirs: True

/var/lib/prometheus:
  file.directory:
    - user: prometheus
    - group: prometheus
    - mode: '0755'
    - makedirs: True

prometheus_binary:
  archive.extracted:
    - name: /opt/prometheus
    - source: https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz
    - skip_verify: True
    - enforce_toplevel: False

prometheus_config:
  file.managed:
    - name: /etc/prometheus/prometheus.yml
    - source: salt://files/prometheus/prometheus.yml
    - template: jinja
    - user: prometheus
    - group: prometheus
    - mode: '0644'

prometheus_service_unit:
  file.managed:
    - name: /etc/systemd/system/prometheus.service
    - source: salt://files/prometheus/prometheus.service
    - user: root
    - group: root
    - mode: '0644'

prometheus_service:
  service.running:
    - name: prometheus
    - enable: True
    - require:
      - file: prometheus_service_unit
      - file: prometheus_config
      - archive: prometheus_binary
    - watch:
      - file: prometheus_config

# ── Node exporter (installed on ALL minions via separate targeting)

node_exporter_binary:
  archive.extracted:
    - name: /opt/node_exporter
    - source: https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
    - skip_verify: True
    - enforce_toplevel: False

node_exporter_unit:
  file.managed:
    - name: /etc/systemd/system/node_exporter.service
    - source: salt://files/prometheus/node_exporter.service
    - user: root
    - group: root
    - mode: '0644'

node_exporter:
  service.running:
    - name: node_exporter
    - enable: True
    - require:
      - archive: node_exporter_binary
      - file: node_exporter_unit

prometheus_firewall:
  cmd.run:
    - name: ufw allow from 10.0.0.0/8 to any port 9090 && ufw allow from 10.0.0.0/8 to any port 9100
    - unless: ufw status | grep -q '9090'
    - require:
      - pkg: firewall_base
