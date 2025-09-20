# common_templates

## Overview

No description available.

**Author:** Unknown  
**Version:** Unknown

## Variables

The following variables can be configured for this role:

```yaml
template_version: 1.0.0
template_last_updated: {{ ansible_date_time.iso8601 }}
base_template_path: common_templates
template_encoding: utf-8
organization_name: {{ organization_name | default('HX Infrastructure') }}
environment: {{ ansible_environment | default('production') }}
managed_by: Ansible HX Infrastructure Framework
enable_template_inheritance: True
template_validation_enabled: True
template_security_scanning: True
common_blocks: ['header', 'configuration', 'security', 'monitoring', 'footer']
template_cache_enabled: True
template_optimization_level: standard
template_security: {'escape_variables': True, 'validate_input': True, 'sanitize_output': True, 'audit_logging': True}
template_documentation: {'auto_generate': True, 'include_examples': True, 'include_variables': True, 'include_blocks': True}
quality_thresholds: {'security_score_min': 80, 'performance_score_min': 75, 'complexity_max': 15, 'max_template_lines': 200}
standardization: {'enforce_naming_convention': True, 'require_documentation': True, 'enforce_indentation': True, 'indentation_type': 'spaces', 'indentation_size': 2}
monitoring: {'track_usage': True, 'performance_monitoring': True, 'error_tracking': True, 'audit_trail': True}
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

- `template_metadata.json.j2`
- `base.j2`
