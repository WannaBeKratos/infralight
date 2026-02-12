# ── HAProxy load balancer state ────────────────────────────

haproxy:
  pkg.installed:
    - name: haproxy
  service.running:
    - name: haproxy
    - enable: True
    - require:
      - pkg: haproxy
    - watch:
      - file: haproxy_config

haproxy_config:
  file.managed:
    - name: /etc/haproxy/haproxy.cfg
    - source: salt://files/haproxy/haproxy.cfg
    - template: jinja
    - user: root
    - group: root
    - mode: '0644'
    - require:
      - pkg: haproxy

haproxy_firewall:
  cmd.run:
    - name: ufw allow 80/tcp && ufw allow 443/tcp && ufw allow 8404/tcp
    - unless: ufw status | grep -q '8404'
    - require:
      - pkg: firewall_base

haproxy_rsyslog:
  file.managed:
    - name: /etc/rsyslog.d/49-haproxy.conf
    - contents: |
        local0.* /var/log/haproxy/access.log
        local0.notice /var/log/haproxy/admin.log
    - require:
      - pkg: haproxy

/var/log/haproxy:
  file.directory:
    - user: syslog
    - group: adm
    - mode: '0755'
    - makedirs: True
