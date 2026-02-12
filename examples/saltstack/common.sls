# ── Common state — applied to ALL minions ────────────────
# Base packages, users, firewall, NTP, and SSH hardening.

common_packages:
  pkg.installed:
    - pkgs:
      - curl
      - wget
      - vim
      - htop
      - git
      - net-tools
      - unzip
      - jq
      - ca-certificates
      - gnupg

admin_user:
  user.present:
    - name: deploy
    - shell: /bin/bash
    - home: /home/deploy
    - groups:
      - sudo
      - docker

deploy_ssh_key:
  ssh_auth.present:
    - user: deploy
    - name: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFakeKeyForDemoOnly deploy@infra
    - require:
      - user: admin_user

ntp_service:
  pkg.installed:
    - name: chrony
  service.running:
    - name: chrony
    - enable: True
    - require:
      - pkg: ntp_service

sshd_config:
  file.managed:
    - name: /etc/ssh/sshd_config
    - source: salt://files/sshd_config
    - user: root
    - group: root
    - mode: '0600'

sshd_service:
  service.running:
    - name: sshd
    - enable: True
    - watch:
      - file: sshd_config

firewall_base:
  pkg.installed:
    - name: ufw
  cmd.run:
    - name: ufw default deny incoming && ufw default allow outgoing && ufw allow 22/tcp && ufw --force enable
    - unless: ufw status | grep -q 'Status: active'
    - require:
      - pkg: firewall_base

/var/log/infralight:
  file.directory:
    - user: deploy
    - group: deploy
    - mode: '0755'
    - makedirs: True

set_timezone:
  timezone.system:
    - name: UTC

sysctl_tuning:
  sysctl.present:
    - name: net.core.somaxconn
    - value: 65535

vm_swappiness:
  sysctl.present:
    - name: vm.swappiness
    - value: 10
