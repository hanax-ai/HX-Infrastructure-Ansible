
# HX-Infrastructure Ansible Project

## Overview
This repository contains the standardized Ansible infrastructure automation for HX environments, implementing enterprise-grade configuration management, deployment automation, and operational procedures.

## Project Status
- **Phase**: 1.0 - Repository Foundation and Structure Setup
- **Status**: Directory structure implemented, ready for development
- **Last Updated**: September 17, 2025

## Quick Start
```bash
# Clone and navigate to project
cd hx-infrastructure-ansible

# Install dependencies
ansible-galaxy install -r requirements.yml

# Run site playbook for development environment
ansible-playbook -i inventories/dev site.yml
```

## Directory Structure
See [docs/structure_guide.md](docs/structure_guide.md) for complete directory structure documentation.

## Key Components
- **Inventories**: Environment-specific host definitions (dev/test/prod)
- **Roles**: Reusable automation components for services and infrastructure
- **Playbooks**: Orchestration workflows for deployment and operations
- **Variables**: Hierarchical configuration management
- **Vault**: Encrypted secrets management per environment

## Documentation
- [Structure Guide](docs/structure_guide.md) - Complete directory organization
- [Architecture](docs/architecture/) - System design and patterns
- [Deployment](docs/deployment/) - Deployment procedures and workflows
- [Operations](docs/operations/) - Day-to-day operational procedures
- [Security](docs/security/) - Security policies and compliance

## Development Workflow
1. Create feature branch from main
2. Develop roles and playbooks following structure guidelines
3. Test using molecule framework in `tests/` directory
4. Submit pull request with evidence documentation
5. Deploy through CI/CD pipeline in `ci/` directory

## Environment Management
- **Development**: `inventories/dev/` - Development and testing
- **Test**: `inventories/test/` - Pre-production validation
- **Production**: `inventories/prod/` - Live production systems

## Support
For questions, issues, or contributions, please refer to the documentation in the `docs/` directory or contact the infrastructure team.
