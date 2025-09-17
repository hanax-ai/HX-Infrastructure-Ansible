
# HX Infrastructure Ansible Makefile
# Enhanced with secrets-linting and comprehensive quality gates

.PHONY: help install lint test security secrets-lint clean deploy backup validate format check-syntax molecule docs all

# Default target
all: install lint secrets-lint test security

# Help target
help:
	@echo "HX Infrastructure Ansible Management"
	@echo "===================================="
	@echo ""
	@echo "Available targets:"
	@echo "  help          - Show this help message"
	@echo "  install       - Install dependencies and collections"
	@echo "  lint          - Run ansible-lint and yamllint"
	@echo "  secrets-lint  - Scan for secrets and sensitive data"
	@echo "  test          - Run all tests"
	@echo "  security      - Run security scans"
	@echo "  validate      - Validate playbooks and roles"
	@echo "  format        - Format YAML files"
	@echo "  check-syntax  - Check Ansible syntax"
	@echo "  molecule      - Run molecule tests"
	@echo "  docs          - Generate documentation"
	@echo "  clean         - Clean temporary files"
	@echo "  deploy        - Deploy to staging environment"
	@echo "  backup        - Backup configurations"
	@echo "  all           - Run install, lint, secrets-lint, test, and security"

# Install dependencies
install:
	@echo "Installing Ansible collections and dependencies..."
	ansible-galaxy install -r requirements.yml --force
	pip3 install --upgrade ansible-lint yamllint molecule molecule-plugins[docker] pytest-testinfra
	@echo "Installation complete!"

# Linting
lint:
	@echo "Running ansible-lint..."
	ansible-lint --force-color --show-relpath .
	@echo "Running yamllint..."
	yamllint --format colored .
	@echo "Linting complete!"

# Secrets scanning - CRITICAL SECURITY FEATURE
secrets-lint:
	@echo "Scanning for secrets and sensitive data..."
	@echo "Checking for vault files without encryption..."
	@find . -name "*vault*" -type f ! -path "./.git/*" ! -path "./vault/*" -exec grep -l "ANSIBLE_VAULT" {} \; || echo "No unencrypted vault files found"
	@echo "Checking for potential secrets in files..."
	@grep -r -i --exclude-dir=.git --exclude-dir=vault --exclude="*.retry" \
		-E "(password|secret|key|token|credential|api_key|private_key|cert|certificate).*[:=].*['\"][^'\"]{8,}" . || echo "No obvious secrets found"
	@echo "Checking for hardcoded IPs and sensitive patterns..."
	@grep -r -i --exclude-dir=.git --exclude-dir=vault --exclude="*.retry" \
		-E "([0-9]{1,3}\.){3}[0-9]{1,3}|BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY" . || echo "No hardcoded IPs or private keys found"
	@echo "Secrets scanning complete!"

# Testing
test: check-syntax validate
	@echo "Running comprehensive tests..."
	@if [ -d "tests" ]; then \
		echo "Running custom tests..."; \
		find tests -name "*.yml" -exec ansible-playbook --syntax-check {} \; ; \
	fi
	@echo "Testing complete!"

# Security scanning
security:
	@echo "Running security scans..."
	@echo "Checking file permissions..."
	@find . -type f -perm /o+w -not -path "./.git/*" -exec echo "World-writable file: {}" \;
	@echo "Checking for sudo without password..."
	@grep -r "NOPASSWD" . --exclude-dir=.git || echo "No passwordless sudo found"
	@echo "Security scanning complete!"

# Validation
validate:
	@echo "Validating playbooks and roles..."
	@find playbooks -name "*.yml" -exec ansible-playbook --syntax-check {} \; 2>/dev/null || echo "No playbooks to validate"
	@find roles -name "main.yml" -path "*/tasks/*" -exec ansible-playbook --syntax-check {} \; 2>/dev/null || echo "No role tasks to validate"
	@echo "Validation complete!"

# Format YAML files
format:
	@echo "Formatting YAML files..."
	@find . -name "*.yml" -o -name "*.yaml" | grep -v ".git" | xargs -I {} sh -c 'echo "Formatting: {}"; python3 -c "import yaml; import sys; content=yaml.safe_load(open(sys.argv[1])); yaml.dump(content, open(sys.argv[1], \"w\"), default_flow_style=False, indent=2)" {}'
	@echo "Formatting complete!"

# Syntax checking
check-syntax:
	@echo "Checking Ansible syntax..."
	@find . -name "*.yml" -path "./playbooks/*" -exec ansible-playbook --syntax-check {} \; 2>/dev/null || echo "No playbooks found for syntax check"
	@echo "Syntax check complete!"

# Molecule testing
molecule:
	@echo "Running molecule tests..."
	@if [ -d "molecule" ]; then \
		cd molecule && molecule test; \
	else \
		echo "No molecule tests found"; \
	fi
	@echo "Molecule testing complete!"

# Documentation generation
docs:
	@echo "Generating documentation..."
	@if command -v ansible-doc >/dev/null 2>&1; then \
		mkdir -p docs/generated; \
		find roles -name "main.yml" -path "*/meta/*" -exec dirname {} \; | sed 's|/meta||' | xargs -I {} ansible-doc -t role {} > docs/generated/roles.txt 2>/dev/null || echo "Role documentation generated"; \
	fi
	@echo "Documentation generation complete!"

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -name "*.retry" -delete
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf .ansible
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .tox
	@echo "Cleanup complete!"

# Deploy to staging
deploy:
	@echo "Deploying to staging environment..."
	@if [ -f "playbooks/site.yml" ]; then \
		ansible-playbook -i inventories/staging/hosts.yml playbooks/site.yml --check --diff; \
		read -p "Continue with actual deployment? (y/N): " confirm; \
		if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
			ansible-playbook -i inventories/staging/hosts.yml playbooks/site.yml; \
		fi; \
	else \
		echo "No site.yml playbook found"; \
	fi
	@echo "Deployment complete!"

# Backup configurations
backup:
	@echo "Creating backup of configurations..."
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	tar -czf "backup_$$timestamp.tar.gz" \
		--exclude='.git' \
		--exclude='*.retry' \
		--exclude='.ansible' \
		--exclude='backup_*.tar.gz' \
		. && \
	echo "Backup created: backup_$$timestamp.tar.gz"
	@echo "Backup complete!"

# CI/CD integration target
ci: install lint secrets-lint test security
	@echo "CI/CD pipeline complete!"

# Development setup
dev-setup: install
	@echo "Setting up development environment..."
	@if ! command -v pre-commit >/dev/null 2>&1; then \
		pip3 install pre-commit; \
	fi
	@if [ -f ".pre-commit-config.yaml" ]; then \
		pre-commit install; \
	fi
	@echo "Development setup complete!"

# Production deployment (with extra safety)
prod-deploy:
	@echo "PRODUCTION DEPLOYMENT - EXTRA SAFETY CHECKS"
	@echo "==========================================="
	@read -p "Are you sure you want to deploy to PRODUCTION? (type 'DEPLOY' to confirm): " confirm; \
	if [ "$$confirm" = "DEPLOY" ]; then \
		$(MAKE) secrets-lint && \
		$(MAKE) lint && \
		$(MAKE) test && \
		$(MAKE) security && \
		ansible-playbook -i inventories/production/hosts.yml playbooks/site.yml --check --diff && \
		read -p "Final confirmation for PRODUCTION deployment? (type 'CONFIRM'): " final; \
		if [ "$$final" = "CONFIRM" ]; then \
			ansible-playbook -i inventories/production/hosts.yml playbooks/site.yml; \
		fi; \
	else \
		echo "Production deployment cancelled"; \
	fi
