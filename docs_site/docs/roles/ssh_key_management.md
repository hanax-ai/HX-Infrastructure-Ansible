# ssh_key_management

## Overview

No description available.

**Author:** Unknown  
**Version:** Unknown

## Variables

The following variables can be configured for this role:

```yaml
ssh_key_type: ed25519
ssh_key_size: 256
ssh_key_comment: Ansible managed key - {{ inventory_hostname }} - {{ ansible_date_time.date }}
ssh_key_private_path: {{ ansible_user_dir }}/.ssh/id_{{ ssh_key_type }}
ssh_key_force_regenerate: False
ssh_key_exclusive: False
ssh_key_backup_enabled: True
ssh_key_test_connectivity: True
ssh_client_config_enabled: True
ssh_security_hardening: True
ssh_key_rotation_enabled: False
ssh_key_backup_dir: /opt/ssh_key_backups
ssh_key_log_dir: /var/log/ssh_key_management
ansible_user_dir: /home/{{ ansible_user }}
ssh_key_patterns: ['id_*', '*.pub', 'authorized_keys', 'known_hosts']
ssh_connection_timeout: 30
ssh_client_config: {'StrictHostKeyChecking': 'yes', 'UserKnownHostsFile': "~/.ssh/known_hosts_{{ environment_type | default('dev') }}", 'ControlMaster': 'auto', 'ControlPath': '~/.ssh/control-%h-%p-%r', 'ControlPersist': '300s', 'ServerAliveInterval': '60', 'ServerAliveCountMax': '3', 'ConnectTimeout': '10', 'BatchMode': 'yes', 'LogLevel': 'ERROR'}
ssh_security_settings: {'Protocol': '2', 'PermitRootLogin': 'no', 'PasswordAuthentication': 'no', 'PubkeyAuthentication': 'yes', 'PermitEmptyPasswords': 'no', 'ChallengeResponseAuthentication': 'no', 'X11Forwarding': 'no', 'ClientAliveInterval': '300', 'ClientAliveCountMax': '2', 'MaxAuthTries': '3', 'MaxSessions': '10', 'LoginGraceTime': '60'}
ssh_key_rotation_days: 90
ssh_key_rotation_warning_days: 7
```

## Dependencies

No dependencies.


## Tasks

The following task files are included:

- `main.yml`


## Handlers

The following handlers are available:

- `main.yml`


## Templates

The following templates are provided:

- `rotate_ssh_keys.sh.j2`
- `ssh_config.j2`
- `ssh_key_inventory.yml.j2`
