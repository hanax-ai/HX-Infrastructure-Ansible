# operational_safety

## Overview

No description available.

**Author:** Unknown  
**Version:** Unknown

## Variables

The following variables can be configured for this role:

```yaml
safety_confirmation_required: True
safety_require_backup: True
safety_require_maintenance_window: False
safety_dangerous_command_protection: True
safety_create_rollback_script: True
safety_check_monitoring: False
safety_check_cluster_health: False
safety_backup_base_dir: /opt/ansible-backups
safety_backup_database: False
safety_backup_paths: ['/etc', '/opt/config', '/var/lib/important']
operational_safety_log_dir: /var/log/ansible-safety
safety_dangerous_commands: ['rm -rf', 'dd if=', 'mkfs', 'fdisk', 'parted', 'wipefs', 'shred', 'format', 'del /s', 'rmdir /s', 'truncate -s 0', '>']
safety_maintenance_start: 02:00
safety_maintenance_end: 06:00
safety_forbidden_environments: []
safety_risks: ['System downtime', 'Data loss', 'Service interruption', 'Configuration corruption', 'Security policy changes']
monitoring_api_url: http://localhost:9090/api/v1/alerts
db_host: localhost
db_user: postgres
db_name: hx_db
```

## Dependencies

No dependencies.


## Tasks

The following task files are included:

- `main.yml`


## Handlers

The following handlers are available:



## Templates

The following templates are provided:

- `rollback_script.sh.j2`
