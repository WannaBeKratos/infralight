# ── PgBouncer connection pooler ────────────────────────────

pgbouncer:
  pkg.installed:
    - name: pgbouncer
  service.running:
    - name: pgbouncer
    - enable: True
    - require:
      - pkg: pgbouncer
      - service: postgresql
    - watch:
      - file: pgbouncer_config
      - file: pgbouncer_userlist

pgbouncer_config:
  file.managed:
    - name: /etc/pgbouncer/pgbouncer.ini
    - source: salt://files/pgbouncer/pgbouncer.ini
    - template: jinja
    - user: postgres
    - group: postgres
    - mode: '0640'
    - require:
      - pkg: pgbouncer

pgbouncer_userlist:
  file.managed:
    - name: /etc/pgbouncer/userlist.txt
    - source: salt://files/pgbouncer/userlist.txt
    - template: jinja
    - user: postgres
    - group: postgres
    - mode: '0600'
    - require:
      - pkg: pgbouncer

pgbouncer_firewall:
  cmd.run:
    - name: ufw allow from 10.0.0.0/8 to any port 6432
    - unless: ufw status | grep -q '6432'
    - require:
      - pkg: firewall_base
