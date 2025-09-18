
# HX-Infrastructure Ansible Project

## 🚨 CRITICAL DIRECTIVE - IMMEDIATE ACTION REQUIRED

**⚠️ URGENT: Critical Infrastructure Misalignment Identified**

A **CRITICAL DIRECTIVE** has been issued by the Manus AI Infrastructure Audit Team identifying critical misalignments between actual HX infrastructure and Ansible repository configuration.

**📋 [READ FULL DIRECTIVE: docs/CRITICAL DIRECTIVE_ HX Infrastructure Ansible Engineering Team.md](docs/CRITICAL%20DIRECTIVE_%20HX%20Infrastructure%20Ansible%20Engineering%20Team.md)**

### Critical Issues Summary:
- ❌ **IP Address Misalignment**: Production servers using 192.168.10.x range, but Ansible inventory configured for 10.0.1.x range
- ❌ **Environment Classification Error**: Production servers incorrectly labeled as "dev-test" environment  
- ❌ **Security Vulnerabilities**: 1,109 security findings requiring immediate attention
- ❌ **Code Quality Issues**: 31/100 compliance score with extensive linting errors

### Immediate Actions Required:
1. **Phase 1 (0-24 hours)**: Fix IP address misalignments and security vulnerabilities
2. **Phase 2 (24-48 hours)**: Security remediation and SSH hardening
3. **Phase 3 (48-72 hours)**: Code quality improvements and linting fixes

**⏰ Deadline for Phase 1 completion: 24 hours from directive receipt**

**🔗 DevOps Context**: "devops is the host node" - hx-devops-server (192.168.10.14) serves as the control node

---

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
