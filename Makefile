
.PHONY: help install test lint clean deploy setup-dev

# Default target
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation and Setup
install: ## Install all dependencies
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installing Ansible Galaxy dependencies..."
	ansible-galaxy install -r requirements.yml --force
	@echo "Installation complete!"

setup-dev: install ## Setup development environment
	@echo "Setting up development environment..."
	pip install -r requirements-dev.txt
	pre-commit install
	@echo "Development environment ready!"

# Testing
test: ## Run all tests
	@echo "Running molecule tests for all roles..."
	@for role in roles/*/; do \
	        if [ -d "$$role/molecule" ]; then \
	                echo "Testing $$role"; \
	                cd "$$role" && molecule test && cd ../..; \
	        fi \
	done

test-role: ## Test specific role (usage: make test-role ROLE=nginx)
	@if [ -z "$(ROLE)" ]; then \
	        echo "Please specify ROLE. Usage: make test-role ROLE=nginx"; \
	        exit 1; \
	fi
	@if [ -d "roles/$(ROLE)/molecule" ]; then \
	        cd roles/$(ROLE) && molecule test; \
	else \
	        echo "Role $(ROLE) not found or no molecule tests available"; \
	fi

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

deploy-prod: ## Deploy to production environment (DRY-RUN by default - use deploy-prod-confirm for actual deployment)
	@echo "🚨 PRODUCTION DEPLOYMENT - DRY RUN MODE 🚨"
	@echo "This will show what would be changed without making actual changes."
	@echo "Use 'make deploy-prod-confirm' for actual deployment."
	@echo ""
	ansible-playbook -i inventory/environments/production playbooks/site/main.yml --ask-vault-pass --check --diff

deploy-prod-confirm: safety-check ## Deploy to production environment (ACTUAL DEPLOYMENT)
	@echo "🚨🚨🚨 CRITICAL: ACTUAL PRODUCTION DEPLOYMENT 🚨🚨🚨"
	@echo "This will make REAL changes to production infrastructure!"
	@echo "Make sure you have:"
	@echo "  ✓ Reviewed all changes in dry-run mode"
	@echo "  ✓ Obtained proper approvals"
	@echo "  ✓ Scheduled maintenance window"
	@echo "  ✓ Prepared rollback plan"
	@echo ""
	@read -p "Type 'DEPLOY-TO-PRODUCTION' to confirm: " confirm && [ "$$confirm" = "DEPLOY-TO-PRODUCTION" ]
	ansible-playbook -i inventory/environments/production playbooks/site/main.yml --ask-vault-pass

# Safety and validation
safety-check: ## Run comprehensive safety checks before production deployment
	@echo "🔍 Running comprehensive safety checks..."
	@echo ""
	@echo "1. Checking security settings..."
	@if grep -q "host_key_checking = True" ansible.cfg; then \
	        echo "  ✅ Host key checking is enabled"; \
	else \
	        echo "  ❌ CRITICAL: Host key checking is disabled!"; \
	        exit 1; \
	fi
	@echo ""
	@echo "2. Checking for SECURITY.md..."
	@if [ -f "SECURITY.md" ]; then \
	        echo "  ✅ SECURITY.md exists"; \
	else \
	        echo "  ❌ CRITICAL: SECURITY.md is missing!"; \
	        exit 1; \
	fi
	@echo ""
	@echo "3. Checking .gitignore for sensitive files..."
	@if grep -q "vault" .gitignore; then \
	        echo "  ✅ Vault files are in .gitignore"; \
	else \
	        echo "  ❌ WARNING: Vault files may not be properly excluded"; \
	fi
	@echo ""
	@echo "4. Checking for secrets in repository..."
	@if command -v detect-secrets >/dev/null 2>&1; then \
	        detect-secrets scan --baseline .secrets.baseline || echo "  ⚠️  Secret scanning completed with findings"; \
	else \
	        echo "  ⚠️  detect-secrets not installed, skipping secret scan"; \
	fi
	@echo ""
	@echo "5. Validating inventory files..."
	@ansible-inventory -i inventory/environments/production --list >/dev/null && echo "  ✅ Production inventory is valid" || (echo "  ❌ CRITICAL: Production inventory is invalid!" && exit 1)
	@echo ""
	@echo "✅ Safety checks completed successfully!"

test-role: ## Test a specific role (usage: make test-role ROLE=role_name)
	@if [ -z "$(ROLE)" ]; then \
	        echo "❌ ERROR: Please specify a role name: make test-role ROLE=role_name"; \
	        exit 1; \
	fi
	@if [ ! -d "roles/$(ROLE)" ]; then \
	        echo "❌ ERROR: Role 'roles/$(ROLE)' does not exist!"; \
	        echo "Available roles:"; \
	        ls -1 roles/ | sed 's/^/  - /'; \
	        exit 1; \
	fi
	@echo "🧪 Testing role: $(ROLE)"
	ansible-playbook -i inventory/environments/development --check --diff -e "target_role=$(ROLE)" playbooks/test-role.yml

# Development setup
setup-dev: ## Set up development environment
	@echo "🔧 Setting up development environment..."
	pip install -r requirements-dev.txt
	pre-commit install
	@if [ ! -f ".secrets.baseline" ]; then \
	        detect-secrets scan --baseline .secrets.baseline; \
	fi
	@echo "✅ Development environment setup complete!"

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
	mkdocs build

docs-serve: ## Serve documentation locally
	mkdocs serve

# Cleanup
clean: ## Clean up temporary files
	@echo "Cleaning up temporary files..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	find . -name "*.retry" -delete
	rm -rf .pytest_cache/
	rm -rf .molecule/
	docker system prune -f
	@echo "Cleanup complete!"

# Environment Management
create-env: ## Create new environment (usage: make create-env ENV=new-env)
	@if [ -z "$(ENV)" ]; then \
	        echo "Please specify ENV. Usage: make create-env ENV=new-env"; \
	        exit 1; \
	fi
	cp -r inventory/environments/example inventory/environments/$(ENV)
	@echo "Environment $(ENV) created. Please edit inventory/environments/$(ENV)/hosts.yml"

# Scaling Operations
scale-web: ## Scale web tier (usage: make scale-web COUNT=5)
	@if [ -z "$(COUNT)" ]; then \
	        echo "Please specify COUNT. Usage: make scale-web COUNT=5"; \
	        exit 1; \
	fi
	ansible-playbook -i inventory/environments/production playbooks/scaling/scale-web.yml -e "web_server_count=$(COUNT)"

scale-app: ## Scale application tier (usage: make scale-app COUNT=6)
	@if [ -z "$(COUNT)" ]; then \
	        echo "Please specify COUNT. Usage: make scale-app COUNT=6"; \
	        exit 1; \
	fi
	ansible-playbook -i inventory/environments/production playbooks/scaling/scale-app.yml -e "app_server_count=$(COUNT)"

# Monitoring
monitor-status: ## Check monitoring services status
	ansible monitoring_servers -i inventory/environments/production -m service -a "name=prometheus state=started"
	ansible monitoring_servers -i inventory/environments/production -m service -a "name=grafana-server state=started"

# SSL Management
update-ssl: ## Update SSL certificates
	ansible-playbook -i inventory/environments/production playbooks/security/ssl-update.yml

# Database Operations
db-backup: ## Backup databases
	ansible-playbook -i inventory/environments/production playbooks/maintenance/backup.yml --tags "database"

db-restore: ## Restore database (usage: make db-restore DATE=2025-09-17)
	@if [ -z "$(DATE)" ]; then \
	        echo "Please specify DATE. Usage: make db-restore DATE=2025-09-17"; \
	        exit 1; \
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
