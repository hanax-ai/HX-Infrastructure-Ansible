# hx_domain_join_standardized

## Overview

Professional-grade Active Directory domain integration for HX Infrastructure

**Author:** HX Infrastructure Team  
**Version:** Unknown

## Variables

The following variables can be configured for this role:

```yaml
hx_domain_join_enabled: True
hx_domain_join_version: 1.0.0
hx_ad_domain: dev-test.hana-x.ai
hx_ad_admin_user: agent0
hx_ad_admin_password: 
hx_ad_realm: DEV-TEST.HANA-X.AI
hx_ad_domain_controller: 
hx_ad_ou_path: 
hx_ad_computer_name: {{ ansible_hostname | upper }}
hx_ad_computer_description: HX Infrastructure Server - {{ ansible_hostname }}
hx_ad_computer_location: HX Infrastructure
hx_domain_security_enabled: True
hx_domain_strict_validation: True
hx_domain_require_encryption: True
hx_domain_verify_certificates: True
hx_sssd_enabled: True
hx_sssd_cache_credentials: True
hx_sssd_enumerate_users: False
hx_sssd_enumerate_groups: False
hx_sssd_case_sensitive: False
hx_sssd_use_fully_qualified_names: False
hx_krb5_enabled: True
hx_krb5_default_realm: {{ hx_ad_realm }}
hx_krb5_ticket_lifetime: 24h
hx_krb5_renew_lifetime: 7d
hx_krb5_forwardable: True
hx_dns_update_enabled: True
hx_dns_search_domains: ['{{ hx_ad_domain }}']
hx_dns_nameservers: []
hx_domain_packages: ['realmd', 'sssd', 'sssd-tools', 'adcli', 'krb5-user', 'krb5-workstation', 'packagekit', 'samba-common-tools']
hx_domain_backup_enabled: True
hx_domain_monitoring_enabled: False
hx_domain_audit_logging_enabled: True
hx_domain_health_checks_enabled: True
hx_domain_join_timeout: 300
hx_domain_validation_retries: 3
hx_domain_validation_delay: 10
hx_domain_discovery_timeout: 60
hx_home_dir_enabled: False
hx_home_dir_base: /home
hx_home_dir_create: True
hx_home_dir_umask: 0077
hx_sudo_enabled: False
hx_sudo_groups: []
hx_sudo_users: []
hx_login_shell: /bin/bash
hx_login_create_homedir: True
hx_login_fallback_homedir: /tmp
```

## Dependencies

- {'role': 'hx_ca_trust_standardized', 'when': 'hx_domain_verify_certificates | bool'}


## Tasks

The following task files are included:

- `security.yml`
- `configure.yml`
- `validate.yml`
- `health_checks.yml`
- `main.yml`
- `join_domain.yml`
- `install.yml`


## Handlers

The following handlers are available:

- `main.yml`


## Templates

The following templates are provided:

- `security_audit.j2`
- `krb5.conf.j2`
- `sudoers_domain.j2`
- `resolv.conf.j2`
- `realmd.conf.j2`
- `sssd.conf.j2`
- `health_report.j2`
