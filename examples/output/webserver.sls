nginx:
  pkg.installed:
    - name: nginx
  service.running:
    - name: nginx
    - enable: True
    - require:
      - pkg: nginx

app_deploy:
  git.latest:
    - name: https://github.com/acme/webapp.git
    - target: /srv/app
  cmd.run:
    - name: /srv/app/start.sh
    - require:
      - git: app_deploy

postgresql:
  pkg.installed:
    - name: postgresql
  service.running:
    - name: postgresql
    - enable: True

redis:
  pkg.installed:
    - name: redis-server
  service.running:
    - name: redis-server
    - enable: True
