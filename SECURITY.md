# Security Policy

## Supported Versions

We actively support and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.x.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in this project, please report it responsibly.

### How to Report

1. **Do NOT** create a public GitHub issue for security vulnerabilities
2. Send an email to security@hanax.ai with:
   - A clear description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Any suggested fixes (if available)

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 5 business days
- **Updates**: We will keep you informed of our progress throughout the investigation
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days
- **Disclosure**: We will coordinate with you on responsible disclosure timing

### Security Best Practices

This repository follows these security practices:

- All secrets are managed through Ansible Vault
- Host key checking is enabled for SSH connections
- Regular security updates and patches are applied
- Access controls and authentication are properly configured
- Security hardening playbooks are maintained and regularly updated

### Scope

This security policy covers:
- Ansible playbooks and roles in this repository
- Configuration templates and variables
- Documentation and deployment procedures
- CI/CD pipeline security

### Out of Scope

- Third-party dependencies (report to their respective maintainers)
- Infrastructure vulnerabilities (report through appropriate channels)
- Social engineering attacks

## Security Hardening

This repository includes security hardening measures:
- SSH configuration hardening
- Firewall configuration
- System update automation
- User access management
- Audit logging configuration

For more information, see our [Security Hardening Guide](docs/security-hardening.md).
