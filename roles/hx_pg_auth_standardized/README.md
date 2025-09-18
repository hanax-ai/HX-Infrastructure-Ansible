# hx_pg_auth_standardized

## Overview

This role provides PostgreSQL authentication and authorization management for the HX Infrastructure platform.

## Features

- PostgreSQL user and role management
- Database authentication configuration
- Security hardening for PostgreSQL
- Backup and recovery procedures
- Health monitoring and validation

## Requirements

- PostgreSQL 12+
- Ansible 2.12+
- Administrative access to PostgreSQL server

## Variables

See `defaults/main.yml` for all available variables and their default values.

## Usage

```yaml
- hosts: database_servers
  roles:
    - hx_pg_auth_standardized
```

## Testing

Run tests with Molecule:

```bash
cd roles/hx_pg_auth_standardized
molecule test
```

## License

MIT

## Author

HX Infrastructure Team
