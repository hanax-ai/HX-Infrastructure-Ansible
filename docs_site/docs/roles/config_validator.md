# config_validator

## Overview

Comprehensive configuration validation and standardization framework

**Author:** HX Infrastructure Team  
**Version:** Unknown

## Variables

The following variables can be configured for this role:

```yaml
config_validation_enabled: True
config_validation_version: 3.0.0
config_validation_strict_mode: True
config_validation_schema_validation: True
variable_naming_conventions: {'prefix_patterns': ['hx_', 'ansible_', 'environment_', 'safety_', 'operational_', 'security_', 'monitoring_', 'backup_'], 'suffix_patterns': ['_enabled', '_config', '_settings', '_version', '_timeout', '_retries', '_path', '_dir', '_file', '_url', '_port', '_host'], 'forbidden_patterns': ['temp_', 'tmp_', 'test_', 'debug_'], 'case_style': 'snake_case', 'max_length': 50}
config_schemas: {'environment_config': {'required_fields': ['environment_type', 'environment_tier', 'deployment_stage'], 'optional_fields': ['environment_description', 'environment_owner'], 'field_types': {'environment_type': 'string', 'environment_tier': 'string', 'deployment_stage': 'string'}, 'allowed_values': {'environment_type': ['development', 'testing', 'staging', 'production'], 'environment_tier': ['dev', 'test', 'stage', 'prod'], 'deployment_stage': ['development', 'testing', 'staging', 'production']}}, 'security_config': {'required_fields': ['security_hardening', 'firewall_config', 'ssl_config'], 'field_types': {'security_hardening': 'dict', 'firewall_config': 'dict', 'ssl_config': 'dict'}}, 'operational_config': {'required_fields': ['operational_safety', 'backup_configuration', 'monitoring_config'], 'field_types': {'operational_safety': 'dict', 'backup_configuration': 'dict', 'monitoring_config': 'dict'}}}
standardized_defaults: {'timeouts': {'connection_timeout': 30, 'command_timeout': 600, 'ssh_timeout': 30, 'network_timeout': 10, 'service_timeout': 30}, 'retries': {'max_retries': 3, 'retry_delay': 5, 'network_retries': 3, 'service_retries': 2}, 'paths': {'log_base_dir': '/var/log', 'config_base_dir': '/etc', 'backup_base_dir': '/opt/backups', 'cache_base_dir': '/tmp'}, 'permissions': {'config_file_mode': '0644', 'secret_file_mode': '0600', 'directory_mode': '0755', 'executable_mode': '0755'}}
inheritance_rules: {'global_precedence': ['group_vars/all.yml', 'group_vars/{{ environment_type }}.yml', 'host_vars/{{ inventory_hostname }}.yml', 'role defaults', 'role vars'], 'merge_strategies': {'lists': 'append', 'dictionaries': 'merge', 'scalars': 'override'}}
drift_detection: {'enabled': True, 'baseline_path': '/tmp/config_baseline.yml', 'drift_report_path': '/tmp/config_drift_report.json', 'ignore_patterns': ['ansible_date_time', 'ansible_hostname', 'ansible_fqdn', '*_timestamp', '*_generated_*']}
validation_rules: {'required_variables': {'all_hosts': ['environment_type', 'ansible_user'], 'production': ['operational_safety', 'backup_configuration', 'security_hardening', 'monitoring_config'], 'development': ['environment_type']}, 'forbidden_variables': {'production': ['debug_mode', 'test_mode', 'unsafe_*']}, 'variable_constraints': {'environment_type': {'type': 'string', 'allowed_values': ['development', 'testing', 'staging', 'production']}, 'ansible_user': {'type': 'string', 'min_length': 3, 'max_length': 32}}}
template_validation: {'enabled': True, 'syntax_check': True, 'variable_check': True, 'undefined_variable_behavior': 'strict', 'template_extensions': ['.j2', '.jinja2']}
documentation_generation: {'enabled': True, 'output_format': 'markdown', 'output_path': 'docs/configuration_reference.md', 'include_examples': True, 'include_schemas': True}
environment_overrides: {'development': {'config_validation_strict_mode': False, 'validation_rules': {'required_variables': {'all_hosts': ['environment_type']}}}, 'production': {'config_validation_strict_mode': True, 'drift_detection': {'enabled': True}, 'template_validation': {'undefined_variable_behavior': 'strict'}}}
reporting: {'generate_report': True, 'report_format': 'json', 'report_path': '/tmp/config_validation_report.json', 'include_recommendations': True, 'include_examples': True}
```

## Dependencies

No dependencies.


## Tasks

The following task files are included:

- `main.yml`
- `schema_validation.yml`
- `variable_naming.yml`


## Handlers

The following handlers are available:



## Templates

The following templates are provided:

