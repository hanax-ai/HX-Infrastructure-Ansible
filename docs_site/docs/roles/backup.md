# backup

## Overview

Comprehensive backup automation role for HX Infrastructure

**Author:** HX Infrastructure Team  
**Version:** Unknown

## Variables

The following variables can be configured for this role:

```yaml
backup_base_dir: /opt/backups
backup_log_dir: /var/log/backup
backup_config_dir: /etc/backup
backup_user: backup
backup_group: backup
backup_home_dir: /home/backup
backup_daily_hour: 2
backup_daily_minute: 0
backup_weekly_hour: 3
backup_weekly_minute: 0
backup_weekly_day: 0
backup_monthly_hour: 4
backup_monthly_minute: 0
backup_monthly_day: 1
backup_cleanup_hour: 5
backup_cleanup_minute: 30
backup_retention_daily: 7
backup_retention_weekly: 4
backup_retention_monthly: 12
backup_encryption_enabled: True
backup_key_file: /etc/backup/encryption.key
backup_remote_enabled: False
backup_remote_host: 
backup_remote_path: backups/
backup_ssh_key_path: 
backup_systemd_timer_enabled: False
backup_monitoring_enabled: False
backup_notifications_enabled: False
backup_notification_email: 
backup_min_space_kb: 1048576
backup_stop_services: []
backup_application_paths: []
backup_databases: []
```

## Dependencies

No dependencies.


## Tasks

The following task files are included:

- `remote_storage.yml`
- `configuration.yml`
- `initial_validation.yml`
- `application.yml`
- `scheduling.yml`
- `service.yml`
- `system.yml`
- `main.yml`
- `directories.yml`
- `verification.yml`
- `encryption.yml`
- `install.yml`


## Handlers

The following handlers are available:

- `main.yml`


## Templates

The following templates are provided:

