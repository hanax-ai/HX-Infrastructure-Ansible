# hx_ca_trust_standardized

## Overview

Professional-grade Certificate Authority trust management for HX Infrastructure

**Author:** HX Infrastructure Team  
**Version:** Unknown

## Variables

The following variables can be configured for this role:

```yaml
hx_ca_trust_enabled: True
hx_ca_trust_version: 1.0.0
hx_ca_host: hx-ca-server.dev-test.hana-x.ai
hx_ca_root_ca_path_on_ca: /home/agent0/easy-rsa/pki/ca.crt
hx_ca_root_ca_filename: hx-rootCA.crt
hx_ca_local_cert_path: /usr/local/share/ca-certificates/hx-root-ca.crt
hx_ca_dc_host: hx-dc-server.dev-test.hana-x.ai
hx_ca_dc_report_dir: /var/log/hx
hx_ca_security_enabled: True
hx_ca_expected_sha256: 
hx_ca_verify_chain: True
hx_ca_strict_permissions: True
hx_ca_validation_enabled: True
hx_ca_san_check_targets: []
hx_ca_health_checks_enabled: True
hx_ca_cert_owner: root
hx_ca_cert_group: root
hx_ca_cert_mode: 0644
hx_ca_packages: ['ca-certificates', 'openssl']
hx_ca_backup_enabled: True
hx_ca_monitoring_enabled: False
hx_ca_audit_logging_enabled: True
hx_ca_update_timeout: 30
hx_ca_validation_retries: 3
hx_ca_validation_delay: 5
```

## Dependencies

No dependencies.


## Tasks

The following task files are included:

- `security.yml`
- `configure.yml`
- `validate.yml`
- `health_checks.yml`
- `main.yml`
- `install.yml`


## Handlers

The following handlers are available:

- `main.yml`


## Templates

The following templates are provided:

- `security_audit.j2`
- `ca_monitor.sh.j2`
- `health_report.j2`
