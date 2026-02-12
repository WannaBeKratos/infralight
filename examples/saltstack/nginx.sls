# ── Nginx web server state ────────────────────────────────
# Installs and configures Nginx as a reverse proxy.

nginx_repo:
  pkgrepo.managed:
    - name: deb http://nginx.org/packages/ubuntu jammy nginx
    - key_url: https://nginx.org/keys/nginx_signing.key
    - file: /etc/apt/sources.list.d/nginx.list

nginx:
  pkg.installed:
    - name: nginx
    - require:
      - pkgrepo: nginx_repo
  service.running:
    - name: nginx
    - enable: True
    - require:
      - pkg: nginx
    - watch:
      - file: nginx_conf
      - file: nginx_vhost

nginx_conf:
  file.managed:
    - name: /etc/nginx/nginx.conf
    - source: salt://files/nginx/nginx.conf
    - user: root
    - group: root
    - mode: '0644'
    - require:
      - pkg: nginx

nginx_vhost:
  file.managed:
    - name: /etc/nginx/sites-available/app.conf
    - source: salt://files/nginx/app.conf
    - user: root
    - group: root
    - mode: '0644'
    - require:
      - pkg: nginx

nginx_vhost_enable:
  file.symlink:
    - name: /etc/nginx/sites-enabled/app.conf
    - target: /etc/nginx/sites-available/app.conf
    - require:
      - file: nginx_vhost

nginx_firewall:
  cmd.run:
    - name: ufw allow 80/tcp && ufw allow 443/tcp
    - unless: ufw status | grep -q '80/tcp'
    - require:
      - pkg: firewall_base

nginx_logrotate:
  file.managed:
    - name: /etc/logrotate.d/nginx
    - source: salt://files/nginx/logrotate
    - user: root
    - group: root
    - mode: '0644'
