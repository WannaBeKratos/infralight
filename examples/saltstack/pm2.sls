# ── PM2 process manager state ─────────────────────────────
# Manages the Node.js application with PM2.

pm2_install:
  npm.installed:
    - name: pm2
    - require:
      - pkg: nodejs

pm2_ecosystem:
  file.managed:
    - name: /srv/app/ecosystem.config.js
    - source: salt://files/app/ecosystem.config.js
    - user: app
    - group: app
    - mode: '0644'
    - require:
      - git: app_deploy

pm2_start:
  cmd.run:
    - name: pm2 start ecosystem.config.js --env production
    - cwd: /srv/app
    - runas: app
    - require:
      - npm: pm2_install
      - file: pm2_ecosystem
      - cmd: app_npm_install

pm2_startup:
  cmd.run:
    - name: pm2 startup systemd -u app --hp /home/app
    - require:
      - cmd: pm2_start

pm2_save:
  cmd.run:
    - name: pm2 save
    - runas: app
    - require:
      - cmd: pm2_startup

pm2_logrotate:
  cmd.run:
    - name: pm2 install pm2-logrotate
    - runas: app
    - unless: pm2 list | grep -q pm2-logrotate
    - require:
      - cmd: pm2_start
