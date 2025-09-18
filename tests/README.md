
# Testing Framework

## Overview
This directory contains the comprehensive testing framework for the HX-Infrastructure Ansible project, implementing multiple levels of validation to ensure reliability and compliance.

## Testing Structure

### Unit Tests (`unit/`)
- Individual role and task validation
- Variable and template testing
- Syntax and linting verification

### Integration Tests (`integration/`)
- Multi-role workflow testing
- Environment-specific validation
- Service integration verification

### Molecule Tests (`molecule/`)
- Role-based testing scenarios
- Multi-platform validation
- Idempotency testing

### Functional Tests (`functional/`)
- End-to-end system validation
- Performance and load testing
- Compliance verification

## Getting Started

1. Install testing dependencies:
   ```bash
   pip install molecule[docker] ansible-lint yamllint
   ```

2. Run molecule tests:
   ```bash
   cd roles/web_server
   molecule test
   ```

3. Execute integration tests:
   ```bash
   ansible-playbook tests/integration/site_deployment.yml
   ```

## Testing Standards
- All roles must include molecule scenarios
- Integration tests required for multi-role playbooks
- Functional tests for production deployment validation
- Evidence collection for compliance requirements
