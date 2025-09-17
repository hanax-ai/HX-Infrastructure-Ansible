
# Inventory Management Standards

## Overview

The HX Infrastructure project uses YAML-based inventory management for maximum flexibility, readability, and maintainability. This document establishes the standard format and migration path from any legacy INI configurations.

## Standard Inventory Structure

### Directory Layout
```
inventory/
├── environments/
│   ├── production/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   ├── staging/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── development/
│       ├── hosts.yml
│       └── group_vars/
└── group_vars/
    ├── all.yml
    ├── infrastructure.yml
    ├── ai_ml.yml
    ├── ui.yml
    └── operations.yml
```

### Current Structure (Transitional)
The project currently uses `inventories/` with the following structure:
```
inventories/
├── dev/hosts.yml
├── test/hosts.yml
├── prod/hosts.yml
└── group_vars/
```

## YAML Format Standard

### Why YAML Over INI

**YAML Advantages:**
- **Hierarchical Structure**: Natural representation of complex relationships
- **Rich Data Types**: Support for lists, dictionaries, and complex variables
- **Readability**: Self-documenting structure with clear indentation
- **Extensibility**: Easy to add metadata and complex configurations
- **Ansible Native**: Better integration with Ansible's variable system

**INI Limitations:**
- Flat structure limits complex relationships
- Limited data type support
- Difficult to maintain large inventories
- Less readable for complex configurations

### Standard YAML Inventory Format

```yaml
all:
  children:
    # Service Groups
    infrastructure:
      children:
        domain_controllers:
          hosts:
            hx-dc-01.example.com:
              ansible_host: 192.168.10.10
              server_role: primary_domain_controller
              services: ['active_directory', 'dns', 'dhcp']
              os_type: windows_server
              memory_gb: 8
              cpu_cores: 4
    
    ai_ml:
      children:
        llm_services:
          hosts:
            hx-litellm-01.example.com:
              ansible_host: 192.168.10.20
              server_role: litellm_gateway
              services: ['litellm', 'api_gateway']
              os_type: linux
              memory_gb: 16
              cpu_cores: 8
              gpu_enabled: true

  vars:
    # Global environment variables
    environment: production
    domain_name: example.com
    ansible_user: admin
    
    # Common configuration
    timezone: UTC
    ntp_servers:
      - 0.pool.ntp.org
      - 1.pool.ntp.org
```

## Migration Guide: INI to YAML

### Step 1: Identify Current INI Files
```bash
find . -name "*.ini" -type f
```

### Step 2: Convert INI Structure to YAML

**INI Format:**
```ini
[webservers]
web1.example.com ansible_host=192.168.1.10
web2.example.com ansible_host=192.168.1.11

[databases]
db1.example.com ansible_host=192.168.1.20

[webservers:vars]
http_port=80
```

**YAML Equivalent:**
```yaml
all:
  children:
    webservers:
      hosts:
        web1.example.com:
          ansible_host: 192.168.1.10
        web2.example.com:
          ansible_host: 192.168.1.11
      vars:
        http_port: 80
    
    databases:
      hosts:
        db1.example.com:
          ansible_host: 192.168.1.20
```

### Step 3: Update ansible.cfg

Update the inventory path in `ansible.cfg`:
```ini
[defaults]
inventory = inventory/environments/production
```

### Step 4: Validate Migration

```bash
# Test inventory parsing
ansible-inventory --list

# Verify host connectivity
ansible all -m ping

# Check variable resolution
ansible-inventory --host hostname
```

## Environment-Specific Configurations

### Development Environment
- **Path**: `inventory/environments/development/hosts.yml`
- **Domain**: `dev-test.hana-x.ai`
- **Network**: `192.168.10.0/24`
- **Features**: Debug mode, test data, relaxed security

### Staging Environment
- **Path**: `inventory/environments/staging/hosts.yml`
- **Domain**: `staging.hana-x.ai`
- **Network**: `10.1.0.0/16`
- **Features**: Production-like, limited test data

### Production Environment
- **Path**: `inventory/environments/production/hosts.yml`
- **Domain**: `hana-x.ai`
- **Network**: `10.0.0.0/16`
- **Features**: Full security, monitoring, backup

## Best Practices

### Variable Hierarchy
1. **Global variables**: `inventory/group_vars/all.yml`
2. **Service group variables**: `inventory/group_vars/[service].yml`
3. **Environment variables**: `inventory/environments/[env]/group_vars/`
4. **Host-specific variables**: Defined in `hosts.yml` or separate host_vars

### Naming Conventions
- **Hostnames**: `hx-[service]-[number].[domain]`
- **Groups**: Use service-based grouping (infrastructure, ai_ml, ui, operations)
- **Variables**: Use snake_case for consistency
- **Environments**: Use full names (development, staging, production)

### Security Considerations
- Store sensitive variables in Ansible Vault
- Use separate vault files per environment
- Never commit unencrypted secrets
- Use vault password files for automation

## Integration with Discovery Process

The standardized inventory format supports the [Process for New Discoveries](../process/new_discoveries.md):

1. **Discovery Phase**: New services are documented in temporary inventory sections
2. **Integration Phase**: Services are moved to appropriate group structures
3. **Validation Phase**: Inventory changes are validated against standards
4. **Deployment Phase**: Standardized inventory enables consistent deployments

## Related Documentation

- [Ansible Configuration](../ansible/README.md)
- [Process for New Discoveries](../process/new_discoveries.md)
- [Documentation Standards](../standards/Documentation_Standards.md)
