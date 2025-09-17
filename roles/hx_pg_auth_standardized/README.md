
# HX PostgreSQL Authentication Standardized Role

## Description

Enterprise-grade Ansible role for PostgreSQL authentication and security management. This role implements comprehensive PostgreSQL security hardening, authentication configuration, and database access control following SOLID principles and security best practices.

## Features

- **Secure Authentication**: Multi-method authentication support (md5, scram-sha-256, cert)
- **Access Control**: Granular pg_hba.conf management with role-based access
- **SSL/TLS**: Complete SSL certificate management and encrypted connections
- **Security Hardening**: PostgreSQL security configuration following CIS benchmarks
- **Monitoring**: Built-in health checks and monitoring integration
- **Backup Integration**: Automated backup user and permission management

## Requirements

- Ansible >= 2.12
- PostgreSQL >= 12
- Python psycopg2 library
- SSL certificates (for encrypted connections)

## Role Variables

### Authentication Configuration
```yaml
# Authentication method (md5, scram-sha-256, cert, trust)
hx_pg_auth_method: "scram-sha-256"

# SSL configuration
hx_pg_ssl_enabled: true
hx_pg_ssl_cert_file: "/etc/ssl/certs/postgresql.crt"
hx_pg_ssl_key_file: "/etc/ssl/private/postgresql.key"
hx_pg_ssl_ca_file: "/etc/ssl/certs/ca.crt"

# Database users and roles
hx_pg_users:
  - name: "app_user"
    password: "{{ vault_app_user_password }}"
    role_attr_flags: "CREATEDB,NOSUPERUSER"
    db: "application_db"
  - name: "readonly_user"
    password: "{{ vault_readonly_password }}"
    role_attr_flags: "NOSUPERUSER,NOCREATEDB"
    db: "application_db"
```

### Security Configuration
```yaml
# Connection limits
hx_pg_max_connections: 200
hx_pg_superuser_reserved_connections: 3

# Logging configuration
hx_pg_log_connections: true
hx_pg_log_disconnections: true
hx_pg_log_failed_connections: true

# Password encryption
hx_pg_password_encryption: "scram-sha-256"
```

## Dependencies

- geerlingguy.postgresql (for base PostgreSQL installation)

## Example Playbook

```yaml
- hosts: database_servers
  become: yes
  roles:
    - role: hx_pg_auth_standardized
      vars:
        hx_pg_auth_method: "scram-sha-256"
        hx_pg_ssl_enabled: true
        hx_pg_users:
          - name: "myapp_user"
            password: "{{ vault_myapp_password }}"
            role_attr_flags: "CREATEDB"
            db: "myapp_db"
```

## Security Considerations

- All passwords must be stored in Ansible Vault
- SSL certificates should be managed externally
- Regular security audits recommended
- Monitor failed authentication attempts

## Testing

Run molecule tests:
```bash
molecule test
```

## License

MIT

## Author Information

HX Infrastructure Team
