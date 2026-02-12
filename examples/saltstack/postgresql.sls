# ── PostgreSQL database state ─────────────────────────────
# Installs PostgreSQL 16, creates app database and users.

postgresql_repo:
  pkgrepo.managed:
    - name: deb http://apt.postgresql.org/pub/repos/apt jammy-pgdg main
    - key_url: https://www.postgresql.org/media/keys/ACCC4CF8.asc
    - file: /etc/apt/sources.list.d/pgdg.list

postgresql:
  pkg.installed:
    - pkgs:
      - postgresql-16
      - postgresql-client-16
      - libpq-dev
    - require:
      - pkgrepo: postgresql_repo
  service.running:
    - name: postgresql
    - enable: True
    - require:
      - pkg: postgresql

pg_hba_conf:
  file.managed:
    - name: /etc/postgresql/16/main/pg_hba.conf
    - source: salt://files/postgresql/pg_hba.conf
    - user: postgres
    - group: postgres
    - mode: '0640'
    - require:
      - pkg: postgresql

postgresql_conf:
  file.managed:
    - name: /etc/postgresql/16/main/postgresql.conf
    - source: salt://files/postgresql/postgresql.conf
    - user: postgres
    - group: postgres
    - mode: '0644'
    - require:
      - pkg: postgresql

postgresql_restart:
  service.running:
    - name: postgresql
    - watch:
      - file: pg_hba_conf
      - file: postgresql_conf

create_app_db:
  postgres_database.present:
    - name: infralight_prod
    - owner: app_user
    - require:
      - service: postgresql

create_app_user:
  postgres_user.present:
    - name: app_user
    - password: "{{ pillar['db_password'] }}"
    - login: True
    - require:
      - service: postgresql

create_readonly_user:
  postgres_user.present:
    - name: readonly_user
    - password: "{{ pillar['db_readonly_password'] }}"
    - login: True
    - require:
      - service: postgresql

pg_firewall:
  cmd.run:
    - name: ufw allow from 10.0.0.0/8 to any port 5432
    - unless: ufw status | grep -q '5432'
    - require:
      - pkg: firewall_base

pg_backup_cron:
  cron.present:
    - name: pg_dump infralight_prod | gzip > /var/backups/pg/infralight_$(date +\%Y\%m\%d).sql.gz
    - user: postgres
    - hour: 2
    - minute: 0
    - require:
      - postgres_database: create_app_db

/var/backups/pg:
  file.directory:
    - user: postgres
    - group: postgres
    - mode: '0750'
    - makedirs: True
