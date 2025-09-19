# dependency_validator

## Overview

Comprehensive dependency validation framework for HX Infrastructure

**Author:** HX Infrastructure Team  
**Version:** Unknown

## Variables

The following variables can be configured for this role:

```yaml
dependency_validation_enabled: True
dependency_validation_version: 3.0.0
dependency_validation_strict_mode: True
dependency_validation_fail_fast: False
system_requirements: {'min_memory_gb': 2, 'min_disk_gb': 10, 'min_cpu_cores': 1, 'supported_architectures': ['x86_64', 'aarch64'], 'supported_os_families': ['RedHat', 'Debian', 'Ubuntu'], 'supported_os_versions': {'RedHat': ['8', '9'], 'Debian': ['10', '11', '12'], 'Ubuntu': ['20.04', '22.04', '24.04']}}
package_dependencies: {'essential_packages': ['python3', 'curl', 'wget', 'openssl', 'ca-certificates'], 'role_specific_packages': {}, 'version_constraints': {}}
service_dependencies: {'required_services': [], 'forbidden_services': [], 'service_states': {'required_running': [], 'required_stopped': []}}
network_dependencies: {'connectivity_checks': [{'host': '8.8.8.8', 'port': 53, 'protocol': 'udp', 'timeout': 5}, {'host': '1.1.1.1', 'port': 53, 'protocol': 'udp', 'timeout': 5}], 'dns_resolution_checks': ['google.com', 'github.com'], 'required_ports_open': [], 'required_ports_closed': []}
certificate_dependencies: {'validate_ca_bundle': True, 'required_ca_certificates': [], 'ssl_endpoints_check': [], 'certificate_expiry_days': 30}
external_dependencies: {'api_endpoints': [], 'database_connections': [], 'message_queues': [], 'storage_backends': []}
dependency_cache: {'enabled': True, 'cache_dir': '/tmp/ansible-dependency-cache', 'cache_ttl_seconds': 3600, 'offline_mode': False}
validation_timeouts: {'network_timeout': 10, 'service_timeout': 30, 'package_timeout': 300, 'overall_timeout': 600}
validation_retries: {'network_retries': 3, 'service_retries': 2, 'package_retries': 1, 'retry_delay': 5}
dependency_reporting: {'generate_report': True, 'report_format': 'json', 'report_path': '/tmp/dependency-validation-report.json', 'detailed_logging': True, 'log_level': 'INFO'}
environment_overrides: {'development': {'dependency_validation_strict_mode': False, 'validation_timeouts': {'overall_timeout': 300}}, 'testing': {'dependency_validation_strict_mode': True, 'dependency_cache': {'cache_ttl_seconds': 1800}}, 'production': {'dependency_validation_strict_mode': True, 'dependency_validation_fail_fast': True, 'validation_retries': {'network_retries': 5, 'service_retries': 3}}}
features: {'validate_system_requirements': True, 'validate_packages': True, 'validate_services': True, 'validate_network': True, 'validate_certificates': True, 'validate_external_deps': True, 'generate_dependency_matrix': True, 'offline_validation': False}
```

## Dependencies

No dependencies.


## Tasks

The following task files are included:

- `system_requirements.yml`
- `network_validation.yml`
- `package_validation.yml`
- `main.yml`


## Handlers

The following handlers are available:



## Templates

The following templates are provided:

