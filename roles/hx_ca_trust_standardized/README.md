
# HX CA Trust Standardized Role

## Overview

The `hx_ca_trust_standardized` role provides comprehensive Certificate Authority (CA) trust management for the HX Infrastructure platform. This role implements SOLID principles and follows enterprise security best practices for certificate lifecycle management.

## Features

- **Complete CA Lifecycle Management**: Creation, configuration, and maintenance of Certificate Authorities
- **SOLID Architecture**: Single responsibility, extensible design with clear interfaces
- **Security-First Design**: Comprehensive security hardening and compliance features
- **Multi-Platform Support**: Ubuntu, CentOS, RedHat, and Debian compatibility
- **Enterprise Integration**: Java keystore, system trust store, and service integration
- **Monitoring & Alerting**: Certificate expiration monitoring and automated notifications
- **Backup & Recovery**: Automated backup with encryption and retention policies
- **Compliance Support**: FIPS mode, Common Criteria, and audit logging

## Requirements

- Ansible 2.15+
- Python 3.6+
- OpenSSL 1.1.1+
- Target OS: Ubuntu 20.04+, CentOS 8+, RedHat 8+, Debian 11+
- Sudo privileges on target systems

## Role Variables

### Required Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `hx_ca_trust_ca_name` | string | Name of the Certificate Authority | `"HX-Root-CA"` |
| `hx_ca_trust_ca_organization` | string | Organization name for CA | `"Hanax AI"` |
| `hx_ca_trust_ca_country` | string | Country code for CA | `"US"` |

### Optional Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `hx_ca_trust_key_size` | integer | `4096` | RSA key size in bits |
| `hx_ca_trust_validity_days` | integer | `3650` | Certificate validity in days |
| `hx_ca_trust_digest` | string | `"sha256"` | Digest algorithm |
| `hx_ca_trust_backup_enabled` | boolean | `true` | Enable certificate backup |
| `hx_ca_trust_update_system_store` | boolean | `true` | Update system certificate store |

For a complete list of variables, see [defaults/main.yml](defaults/main.yml).

## Dependencies

- `common` role (optional)
- `ansible.posix` collection
- `community.general` collection
- `community.crypto` collection

## Example Playbook

### Basic Usage

```yaml
- hosts: ca_servers
  roles:
    - role: hx_ca_trust_standardized
      vars:
        hx_ca_trust_ca_name: "HX-Production-CA"
        hx_ca_trust_ca_organization: "Hanax AI"
        hx_ca_trust_ca_country: "US"
        hx_ca_trust_ca_state: "California"
        hx_ca_trust_ca_locality: "San Francisco"
```

### Advanced Configuration

```yaml
- hosts: ca_servers
  roles:
    - role: hx_ca_trust_standardized
      vars:
        hx_ca_trust_ca_name: "HX-Enterprise-CA"
        hx_ca_trust_ca_organization: "Hanax AI"
        hx_ca_trust_ca_country: "US"
        hx_ca_trust_key_size: 4096
        hx_ca_trust_validity_days: 7300
        hx_ca_trust_backup_enabled: true
        hx_ca_trust_check_expiration: true
        hx_ca_trust_expiration_warning_days: 60
        hx_ca_trust_java_keystore_update: true
        hx_ca_trust_crl_enabled: true
        hx_ca_trust_ocsp_enabled: true
        hx_ca_trust_notifications_enabled: true
        hx_ca_trust_notification_email: "security@hanax.ai"
        hx_ca_trust_intermediate_cas:
          - name: "HX-Intermediate-CA"
            cert_path: "/etc/ssl/certs/hx-intermediate.crt"
            key_path: "/etc/ssl/private/hx-intermediate.key"
            parent_ca: "HX-Enterprise-CA"
```

### Multi-Environment Setup

```yaml
- hosts: production_ca
  roles:
    - role: hx_ca_trust_standardized
      vars:
        hx_ca_trust_ca_name: "HX-Production-CA"
        hx_ca_trust_compliance_mode: "strict"
        hx_ca_trust_fips_mode: true
        hx_ca_trust_audit_enabled: true

- hosts: staging_ca
  roles:
    - role: hx_ca_trust_standardized
      vars:
        hx_ca_trust_ca_name: "HX-Staging-CA"
        hx_ca_trust_validity_days: 1095
        hx_ca_trust_compliance_mode: "standard"
```

## Task Structure

The role follows SOLID principles with a clear task structure:

1. **validate.yml**: Input validation and system compatibility checks
2. **prepare.yml**: System preparation and dependency installation
3. **install.yml**: Certificate Authority creation and installation
4. **configure.yml**: Post-installation configuration and integration
5. **security.yml**: Security hardening and compliance measures
6. **verify.yml**: Comprehensive testing and validation

## Security Features

### File Security
- Secure file permissions (0600 for private keys, 0644 for certificates)
- Immutable file attributes for critical files
- SELinux/AppArmor integration
- Secure temporary file cleanup

### Audit and Monitoring
- Comprehensive audit logging
- Certificate expiration monitoring
- Intrusion detection integration (AIDE)
- Real-time file integrity monitoring

### Compliance
- FIPS 140-2 mode support
- Common Criteria compliance
- SOC 2 audit trail
- Configurable security policies

### Network Security
- Firewall rule management
- Secure communication protocols
- Certificate pinning support
- OCSP responder integration

## Integration

### System Integration
- System certificate store updates
- Java keystore integration
- Service integration (Nginx, Apache, PostgreSQL)
- Docker registry integration

### Monitoring Integration
- Prometheus metrics export
- Grafana dashboard templates
- Alert manager integration
- SIEM log forwarding

## Backup and Recovery

### Automated Backup
- Scheduled certificate backups
- Encrypted backup storage
- Configurable retention policies
- Recovery testing procedures

### Disaster Recovery
- Certificate restoration procedures
- Emergency certificate issuance
- Cross-site replication support
- Recovery time optimization

## Testing

### Validation Tests
- Certificate creation and validation
- Certificate chain verification
- System integration testing
- Performance benchmarking

### Continuous Testing
- Automated test execution
- Integration with CI/CD pipelines
- Regression testing
- Security testing

## Troubleshooting

### Common Issues

#### Certificate Generation Fails
```bash
# Check OpenSSL version
openssl version

# Verify permissions
ls -la /etc/ssl/private/

# Check disk space
df -h /etc/ssl/
```

#### System Trust Store Issues
```bash
# Update certificate store manually
sudo update-ca-certificates  # Debian/Ubuntu
sudo update-ca-trust         # RedHat/CentOS

# Verify certificate installation
openssl verify -CApath /etc/ssl/certs /path/to/certificate
```

#### Permission Errors
```bash
# Fix certificate directory permissions
sudo chown -R root:root /etc/ssl/
sudo chmod 755 /etc/ssl/certs/
sudo chmod 700 /etc/ssl/private/
```

### Debug Mode

Enable debug logging:
```yaml
hx_ca_trust_enable_logging: true
hx_ca_trust_log_level: "DEBUG"
```

### Performance Issues

Monitor certificate operations:
```bash
# Check certificate generation time
time openssl genrsa -out test.key 4096

# Monitor system resources
htop
iotop
```

## License

MIT

## Author Information

**HX Infrastructure Team**
- Email: infrastructure@hanax.ai
- Documentation: [HX Infrastructure Docs](https://docs.hanax.ai)
- Support: [GitHub Issues](https://github.com/hanax-ai/HX-Infrastructure-Ansible/issues)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Changelog

### Version 1.0.0
- Initial release with complete CA management
- SOLID architecture implementation
- Comprehensive security features
- Multi-platform support
- Enterprise integration capabilities

### Version 1.1.0 (Planned)
- Enhanced OCSP support
- Certificate transparency integration
- Advanced monitoring features
- Performance optimizations
