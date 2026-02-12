# ── Node.js application server state ──────────────────────
# Installs Node.js 20 LTS via NodeSource, deploys the application.

nodejs_repo:
  pkgrepo.managed:
    - name: deb https://deb.nodesource.com/node_20.x nodistro main
    - key_url: https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key
    - file: /etc/apt/sources.list.d/nodesource.list

nodejs:
  pkg.installed:
    - name: nodejs
    - require:
      - pkgrepo: nodejs_repo

build_essentials:
  pkg.installed:
    - pkgs:
      - build-essential
      - python3

app_user:
  user.present:
    - name: app
    - shell: /bin/bash
    - home: /home/app
    - system: True

/srv/app:
  file.directory:
    - user: app
    - group: app
    - mode: '0755'
    - makedirs: True

app_deploy:
  git.latest:
    - name: https://github.com/acme/webapp.git
    - target: /srv/app
    - user: app
    - branch: main
    - require:
      - file: /srv/app
      - pkg: nodejs

app_npm_install:
  cmd.run:
    - name: npm ci --production
    - cwd: /srv/app
    - runas: app
    - require:
      - git: app_deploy
    - onchanges:
      - git: app_deploy

app_env:
  file.managed:
    - name: /srv/app/.env
    - source: salt://files/app/env.j2
    - template: jinja
    - user: app
    - group: app
    - mode: '0600'

app_firewall:
  cmd.run:
    - name: ufw allow from 10.0.0.0/8 to any port 3000
    - unless: ufw status | grep -q '3000'
    - require:
      - pkg: firewall_base
