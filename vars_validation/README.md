
# Variable Validation System

This directory contains the variable validation system for HX Infrastructure, providing comprehensive validation rules and automated checking for all configuration variables.

## Overview

The validation system ensures that:
- All required variables are defined
- Variable types and formats are correct
- Dependencies between variables are satisfied
- Cross-service configurations are consistent
- Resource requirements are met
- Environment-specific rules are enforced

## Files

### `validation_rules.yml`
Comprehensive validation rules defining:
- **Global Required Variables**: Essential variables for all environments
- **Service-Specific Variables**: Variables for infrastructure, AI/ML, operations, and UI services
- **Security Variables**: Authentication, encryption, and access control variables
- **Network Variables**: IP addresses, subnets, and network configuration
- **Performance Variables**: Resource allocation and optimization settings
- **Environment-Specific Rules**: Different validation rules per environment
- **Dependency Rules**: Variable interdependencies
- **Cross-Service Rules**: Consistency checks across services
- **Resource Validation**: Hardware and capacity requirements

### `validate_vars.py`
Python script that:
- Loads variables from YAML files
- Validates against all defined rules
- Checks dependencies and cross-service consistency
- Provides detailed error and warning messages
- Returns appropriate exit codes for CI/CD integration

## Usage

### Basic Validation
```bash
# Validate variables from group_vars files
python vars_validation/validate_vars.py inventories/group_vars/all.yml inventories/group_vars/infrastructure.yml

# Validate all group_vars for an environment
python vars_validation/validate_vars.py inventories/group_vars/*.yml inventories/dev/group_vars/*.yml
```

### Integration with Ansible
```bash
# Run validation before playbook execution
python vars_validation/validate_vars.py inventories/group_vars/*.yml && ansible-playbook site.yml
```

### CI/CD Integration
```yaml
# Example GitHub Actions step
- name: Validate Variables
  run: |
    python vars_validation/validate_vars.py inventories/group_vars/*.yml
    if [ $? -ne 0 ]; then
      echo "Variable validation failed"
      exit 1
    fi
```

## Validation Rules

### Variable Types
- **string**: Text values with optional pattern matching
- **integer**: Numeric values with optional range validation
- **float**: Decimal values with range validation
- **boolean**: True/false values
- **list**: Arrays with optional item type validation
- **dict**: Key-value objects

### Validation Features

#### Pattern Matching
```yaml
- name: "domain_name"
  type: "string"
  pattern: "^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\\.[a-zA-Z]{2,}$"
```

#### Range Validation
```yaml
- name: "postgresql_max_connections"
  type: "integer"
  min_value: 50
  max_value: 1000
```

#### Length Validation
```yaml
- name: "vault_jwt_secret"
  type: "string"
  min_length: 32
```

#### Allowed Values
```yaml
- name: "environment"
  type: "string"
  allowed_values: ["development", "test", "production"]
```

#### List Item Validation
```yaml
- name: "dns_servers"
  type: "list"
  item_type: "string"
  item_pattern: "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
```

### Dependency Validation
Ensures that when certain conditions are met, required variables are present:

```yaml
- condition: "gpu_enabled == true"
  requires:
    - "cuda_version"
    - "ai_ml_gpu_memory_fraction"
  description: "GPU-enabled hosts require CUDA configuration"
```

### Cross-Service Validation
Validates consistency across different services:

```yaml
- name: "database_connectivity"
  description: "Ensure database connectivity variables are consistent"
  rules:
    - "groups['databases'] is defined and groups['databases'] | length > 0"
    - "vault_webui_db_user is defined"
```

### Environment-Specific Rules
Different validation rules for different environments:

```yaml
environment_specific_rules:
  production:
    required_overrides:
      - name: "ssl_verification"
        type: "boolean"
        default: true
    optional_overrides:
      - name: "backup_enabled"
        type: "boolean"
        default: true
```

## Custom Validation Functions

The system supports custom Python validation functions for complex rules:

```python
def validate_password_strength(password):
    # Custom password validation logic
    return True, "Password meets security requirements"
```

## Error Handling

The validator provides detailed error messages:

```
VALIDATION ERRORS:
  ❌ Missing required global variable: domain_name
  ❌ postgresql_max_connections: Value 2000 is outside allowed range [50, 1000]
  ❌ vault_jwt_secret: String length 16 is less than minimum 32
  ❌ Dependency error: GPU-enabled hosts require CUDA configuration - Missing required variable: cuda_version
```

## Best Practices

1. **Run validation early**: Validate variables before deployment
2. **Environment-specific validation**: Use different rules for dev/test/prod
3. **Secure variable handling**: Never log or expose sensitive variables
4. **Comprehensive coverage**: Validate all variables, not just required ones
5. **Clear error messages**: Provide actionable feedback for validation failures

## Extension

To add new validation rules:

1. Update `validation_rules.yml` with new rules
2. Add custom validation functions to `validate_vars.py` if needed
3. Test validation with sample data
4. Update documentation

## Integration with Ansible Vault

The validator works with Ansible Vault encrypted variables:

```bash
# Decrypt vault files for validation
ansible-vault decrypt inventories/group_vars/vault.yml
python vars_validation/validate_vars.py inventories/group_vars/*.yml
ansible-vault encrypt inventories/group_vars/vault.yml
```

This validation system ensures robust, consistent, and secure variable management across the entire HX Infrastructure deployment.
