# ── Redis cache state ─────────────────────────────────────
# Installs Redis 7 with production tuning.

redis:
  pkg.installed:
    - name: redis-server
  service.running:
    - name: redis-server
    - enable: True
    - require:
      - pkg: redis
    - watch:
      - file: redis_conf

redis_conf:
  file.managed:
    - name: /etc/redis/redis.conf
    - source: salt://files/redis/redis.conf
    - user: redis
    - group: redis
    - mode: '0640'
    - require:
      - pkg: redis

redis_firewall:
  cmd.run:
    - name: ufw allow from 10.0.0.0/8 to any port 6379
    - unless: ufw status | grep -q '6379'
    - require:
      - pkg: firewall_base

redis_sysctl:
  sysctl.present:
    - name: vm.overcommit_memory
    - value: 1

redis_hugepages:
  cmd.run:
    - name: echo never > /sys/kernel/mm/transparent_hugepage/enabled
    - unless: grep -q '\[never\]' /sys/kernel/mm/transparent_hugepage/enabled
