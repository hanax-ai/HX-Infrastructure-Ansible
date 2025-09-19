
# Ansible Configuration Management

## Overview

The HX Infrastructure project uses a standardized Ansible configuration approach with environment-specific settings and clear separation between control node and development configurations.

## Configuration Files

### Primary Configuration: `ansible.cfg`

The main `ansible.cfg` file in the project root is configured for **production control node operations**:

- **Inventory**: Points to `inventory/environments/production` (note: currently using `inventories/` structure)
- **Performance**: Optimized for production deployments with smart gathering and fact caching
- **Security**: Configured with vault password file and secure SSH settings
- **Logging**: Full logging enabled for audit trails

### Development Configuration

For development and testing purposes, developers should create a local `ansible-dev.cfg` file with:

```ini
[defaults]
inventory = inventories/dev
host_key_checking = False
remote_user = agent0
private_key_file = ~/.ssh/hx_infrastructure_dev
timeout = 30
forks = 5
gathering = explicit
fact_caching = memory
log_path = ./ansible-dev.log
stdout_callback = yaml
```

## When to Use Each Configuration

### Use Main `ansible.cfg` for:
- Production deployments
- Staging environment operations
- CI/CD pipeline executions
- Formal testing procedures
- Operations team activities

### Use Development Configuration for:
- Local development and testing
- Playbook development and debugging
- Individual developer workflows
- Experimental configurations
- Learning and training

## Configuration Standardization

As of Phase 4.0, we are standardizing on:
- **YAML inventory format** for all environments
- **Consistent inventory paths** under `inventory/environments/`
- **Environment-specific configurations** with clear inheritance
- **Standardized SSH and security settings**

## Migration Notes

The project is transitioning from the current `inventories/` structure to the standardized `inventory/environments/` structure referenced in the main ansible.cfg. This migration will:

1. Maintain backward compatibility during transition
2. Provide clearer environment separation
3. Align with Ansible best practices
4. Support the new discovery process integration

## Related Documentation

- [Inventory Management](../inventory/README.md)
- [Process for New Discoveries](../process/new_discoveries.md)
- [Documentation Standards](../standards/Documentation_Standards.md)
