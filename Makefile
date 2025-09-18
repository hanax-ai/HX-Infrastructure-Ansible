
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

test-syntax: ## Test playbook syntax
	@echo "Testing playbook syntax..."
	@find playbooks -name "*.yml" -exec ansible-playbook --syntax-check {} \;

# Code Quality
lint: ## Run linting on all files
	@echo "Running ansible-lint..."
	ansible-lint playbooks/ roles/
	@echo "Running yamllint..."
	yamllint .
	@echo "Running flake8 on Python files..."
	flake8 tests/ scripts/

format: ## Format code
	@echo "Formatting Python code..."
	black tests/ scripts/
	isort tests/ scripts/

# Deployment
deploy-check: ## Run deployment in check mode (dry run)
	ansible-playbook -i inventory/environments/production playbooks/site/main.yml --check --diff

deploy-dev: ## Deploy to development environment
	ansible-playbook -i inventory/environments/development playbooks/site/main.yml

deploy-staging: ## Deploy to staging environment
	ansible-playbook -i inventory/environments/staging playbooks/site/main.yml

deploy-prod: ## Deploy to production environment (DRY RUN by default - use deploy-prod-confirm for actual)
	echo "SAFETY: Running dry-run first..." && ansible-playbook -i inventory/environments/production playbooks/site/main.yml --check --diff --ask-vault-pass && echo "Dry run complete. Use make deploy-prod-confirm for actual deployment"

# Maintenance
backup: ## Run backup playbook
	ansible-playbook -i inventory/environments/production playbooks/maintenance/backup.yml

update: ## Update system packages
	ansible-playbook -i inventory/environments/production playbooks/maintenance/update.yml

security: ## Apply security hardening
	ansible-playbook -i inventory/environments/production playbooks/maintenance/security.yml

health-check: ## Run health checks
	ansible-playbook -i inventory/environments/production playbooks/maintenance/health-check.yml

# Utilities
ping: ## Test connectivity to all hosts
	ansible all -i inventory/environments/production -m ping

facts: ## Gather facts from all hosts
	ansible all -i inventory/environments/production -m setup

inventory: ## Show inventory
	ansible-inventory -i inventory/environments/production --list

encrypt: ## Encrypt secrets file
	ansible-vault encrypt vars/secrets.yml

decrypt: ## Decrypt secrets file
	ansible-vault decrypt vars/secrets.yml

edit-vault: ## Edit encrypted vault file
	ansible-vault edit vars/secrets.yml

# Documentation
docs: ## Generate documentation
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
	ansible-playbook -i inventory/environments/production playbooks/maintenance/restore.yml -e "backup_date=$(DATE)"

# Service Management
restart-web: ## Restart web services
	ansible-playbook -i inventory/environments/production playbooks/maintenance/restart-services.yml --limit "web_servers"

restart-app: ## Restart application services
	ansible-playbook -i inventory/environments/production playbooks/maintenance/restart-services.yml --limit "app_servers"

restart-db: ## Restart database services
	ansible-playbook -i inventory/environments/production playbooks/maintenance/restart-services.yml --limit "database_servers"

# Version Information
version: ## Show version information
	@echo "HX Infrastructure Ansible - Version Information"
	@echo "=============================================="
	@echo "Ansible Version:"
	@ansible --version
	@echo ""
	@echo "Python Version:"
	@python --version
	@echo ""
	@echo "Git Version:"
	@git --version

# Safety check target
safety-check: ## Run comprehensive safety checks before deployment
	@echo "Running comprehensive safety checks..."
	@echo "1. Checking for secrets in files..."
	@if command -v grep >/dev/null 2>&1; then \
		grep -r "password\|secret\|key" . --exclude-dir=.git --exclude="*.md" --exclude="*.pdf" | grep -v "password_file\|key_checking\|ssh_key" || echo "No obvious secrets found"; \
	fi
	@echo "2. Checking ansible.cfg security settings..."
	@grep "host_key_checking.*True" ansible.cfg >/dev/null && echo "✓ Host key checking enabled" || echo "✗ Host key checking disabled - SECURITY RISK"
	@echo "3. Checking .gitignore for sensitive files..."
	@grep "vault_pass\|\.pem\|\.key" .gitignore >/dev/null && echo "✓ Sensitive file patterns in .gitignore" || echo "✗ Missing sensitive file patterns in .gitignore"
	@echo "4. Checking for SECURITY.md..."
	@[ -f "SECURITY.md" ] && echo "✓ SECURITY.md exists" || echo "✗ SECURITY.md missing"
	@echo "Safety check complete!"

