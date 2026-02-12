# ── Let's Encrypt / Certbot state ──────────────────────────

certbot:
  pkg.installed:
    - pkgs:
      - certbot
      - python3-certbot-nginx

certbot_obtain:
  cmd.run:
    - name: certbot --nginx -d {{ pillar['domain'] }} --non-interactive --agree-tos -m {{ pillar['admin_email'] }}
    - unless: test -d /etc/letsencrypt/live/{{ pillar['domain'] }}
    - require:
      - pkg: certbot
      - service: nginx

certbot_renew_cron:
  cron.present:
    - name: certbot renew --quiet --post-hook "systemctl reload nginx"
    - user: root
    - hour: 3
    - minute: 30
    - identifier: certbot-renew
    - require:
      - cmd: certbot_obtain
