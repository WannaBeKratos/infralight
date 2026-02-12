# ── Grafana dashboarding state ─────────────────────────────

grafana_repo:
  pkgrepo.managed:
    - name: deb https://apt.grafana.com stable main
    - key_url: https://apt.grafana.com/gpg.key
    - file: /etc/apt/sources.list.d/grafana.list

grafana:
  pkg.installed:
    - name: grafana
    - require:
      - pkgrepo: grafana_repo
  service.running:
    - name: grafana-server
    - enable: True
    - require:
      - pkg: grafana
    - watch:
      - file: grafana_config
      - file: grafana_datasource

grafana_config:
  file.managed:
    - name: /etc/grafana/grafana.ini
    - source: salt://files/grafana/grafana.ini
    - template: jinja
    - user: root
    - group: grafana
    - mode: '0640'
    - require:
      - pkg: grafana

grafana_datasource:
  file.managed:
    - name: /etc/grafana/provisioning/datasources/prometheus.yml
    - source: salt://files/grafana/prometheus-datasource.yml
    - user: root
    - group: grafana
    - mode: '0640'
    - require:
      - pkg: grafana

grafana_firewall:
  cmd.run:
    - name: ufw allow 3000/tcp
    - unless: ufw status | grep -q '3000/tcp'
    - require:
      - pkg: firewall_base
