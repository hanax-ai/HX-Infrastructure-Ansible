# HX Infrastructure Ansible

[![Ansible CI/CD Pipeline](https://github.com/hanax-ai/HX-Infrastructure-Ansible/actions/workflows/ansible-ci.yml/badge.svg)](https://github.com/hanax-ai/HX-Infrastructure-Ansible/actions/workflows/ansible-ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview

HX Infrastructure Ansible is an enterprise-grade Infrastructure as Code (IaC) solution for managing and deploying the Hanax AI infrastructure. This repository provides automated, scalable, and secure infrastructure management across multiple environments.

## 🏗️ Architecture

This repository follows enterprise best practices with a professional directory structure:

```
├── .github/workflows/          # CI/CD pipelines
├── docs/                      # Centralized documentation
│   ├── architecture/          # Architecture documentation
│   ├── deployment/           # Deployment guides
│   ├── operations/           # Operations documentation
│   └── security/             # Security documentation
├── environments/             # Multi-environment separation
│   ├── dev/                 # Development environment
│   ├── test/                # Test environment
│   └── prod/                # Production environment
├── playbooks/               # Organized playbooks
├── roles/                   # Custom roles
├── tests/                   # Comprehensive testing
├── scripts/                 # Automation scripts
└── vault/                   # Encrypted secrets
```

## 🚀 Quick Start

### Prerequisites

- Ansible >= 2.14
- Python >= 3.8
- SSH access to target hosts
- Proper vault passwords configured

### Installation

1. Clone the repository:
```bash
git clone https://github.com/hanax-ai/HX-Infrastructure-Ansible.git
cd HX-Infrastructure-Ansible
```

2. Install dependencies:
```bash
pip install -r requirements.txt
ansible-galaxy install -r requirements.yml
```

3. Configure your environment:
```bash
# Copy and customize inventory for your environment
cp environments/dev/inventories/hosts.yml.example environments/dev/inventories/hosts.yml
```

### Basic Usage

Deploy to development environment:
```bash
ansible-playbook -i environments/dev/inventories/hosts.yml site.yml
```

Deploy to production environment:
```bash
ansible-playbook -i environments/prod/inventories/hosts.yml site.yml --ask-vault-pass
```

## 📁 Directory Structure

### Environments
- **dev/**: Development environment with relaxed security for testing
- **test/**: Testing environment mirroring production setup
- **prod/**: Production environment with high security and availability

### Documentation
- **architecture/**: System architecture and design documents
- **deployment/**: Step-by-step deployment guides
- **operations/**: Day-to-day operations documentation
- **security/**: Security policies and procedures

### Testing
- **molecule/**: Molecule testing scenarios
- **integration/**: Integration test suites
- **security/**: Security validation tests

## 🔒 Security

This repository implements enterprise-grade security practices:

- Environment-specific vault encryption
- Role-based access control
- Security scanning in CI/CD
- Compliance with security standards

See [Security Documentation](docs/security/) for detailed information.

## 🧪 Testing

Run the complete test suite:
```bash
# Syntax validation
make syntax-check

# Linting
make lint

# Security tests
make security-test

# Integration tests
make integration-test
```

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Architecture Guide](docs/architecture/)
- [Deployment Guide](docs/deployment/)
- [Operations Manual](docs/operations/)
- [Security Documentation](docs/security/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Requirements

See [requirements.txt](requirements.txt) and [requirements.yml](requirements.yml) for detailed dependency information.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue in this repository
- Check the [troubleshooting guide](docs/troubleshooting/)
- Review existing documentation in `docs/`

## 🏷️ Version History

See [CHANGELOG](docs/CHANGELOG.md) for detailed version history and changes.

---

**Hanax AI Infrastructure Team**
