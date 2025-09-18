
# HX Infrastructure Makefile
# Provides convenient commands for variable management and validation

.PHONY: help validate-vars validate-dev validate-test validate-prod generate-templates check-syntax lint clean

# Default target
help:
	@echo "HX Infrastructure Variable Management"
	@echo "===================================="
	@echo ""
	@echo "Available targets:"
	@echo "  validate-vars     - Validate all variables across all environments"
	@echo "  validate-dev      - Validate development environment variables"
	@echo "  validate-test     - Validate test environment variables"
	@echo "  validate-prod     - Validate production environment variables"
	@echo "  generate-templates - Generate variable templates for new environments"
	@echo "  check-syntax      - Check YAML syntax for all variable files"
	@echo "  lint             - Run comprehensive linting on all files"
	@echo "  clean            - Clean up temporary files"
	@echo ""
	@echo "Examples:"
	@echo "  make validate-dev"
	@echo "  make validate-prod"
	@echo "  make lint"

# Variable validation targets
validate-vars:
	@echo "Validating all variables..."
	@python3 vars_validation/validate_vars.py inventories/group_vars/*.yml
	@echo "✅ All variables validated successfully"

validate-dev:
	@echo "Validating development environment variables..."
	@python3 vars_validation/validate_vars.py \
		inventories/group_vars/*.yml \
		inventories/dev/group_vars/*.yml 2>/dev/null || \
		python3 vars_validation/validate_vars.py inventories/group_vars/*.yml
	@echo "✅ Development environment variables validated"

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

# Template generation
generate-templates:
	@echo "Generating variable templates..."
	@mkdir -p inventories/template/group_vars
	@cp group_vars/templates/all.yml.j2 inventories/template/group_vars/all.yml.template
	@echo "# Infrastructure Service Variables" > inventories/template/group_vars/infrastructure.yml.template
	@echo "# Copy from role_defaults/infrastructure/defaults/main.yml and customize" >> inventories/template/group_vars/infrastructure.yml.template
	@echo "# AI/ML Service Variables" > inventories/template/group_vars/ai_ml.yml.template
	@echo "# Copy from role_defaults/ai_ml/defaults/main.yml and customize" >> inventories/template/group_vars/ai_ml.yml.template
	@echo "# Operations Service Variables" > inventories/template/group_vars/operations.yml.template
	@echo "# Copy from role_defaults/operations/defaults/main.yml and customize" >> inventories/template/group_vars/operations.yml.template
	@echo "# UI Service Variables" > inventories/template/group_vars/ui.yml.template
	@echo "# Copy from role_defaults/ui/defaults/main.yml and customize" >> inventories/template/group_vars/ui.yml.template
	@echo "✅ Variable templates generated in inventories/template/"

# Syntax checking
check-syntax:
	@echo "Checking YAML syntax..."
	@find inventories/ -name "*.yml" -exec python3 -c "import yaml; yaml.safe_load(open('{}'))" \; 2>/dev/null || \
		(echo "❌ YAML syntax errors found" && exit 1)
	@find role_defaults/ -name "*.yml" -exec python3 -c "import yaml; yaml.safe_load(open('{}'))" \; 2>/dev/null || \
		(echo "❌ YAML syntax errors found" && exit 1)
	@find vars_validation/ -name "*.yml" -exec python3 -c "import yaml; yaml.safe_load(open('{}'))" \; 2>/dev/null || \
		(echo "❌ YAML syntax errors found" && exit 1)
	@echo "✅ All YAML files have valid syntax"

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
clean:
	@echo "Cleaning up temporary files..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.tmp" -delete
	@find . -name ".DS_Store" -delete
	@echo "✅ Cleanup completed"

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

# Backup current configuration
backup:
	@echo "Creating backup of current configuration..."
	@mkdir -p backups
	@tar -czf backups/variables-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz \
		inventories/group_vars/ \
		role_defaults/ \
		vars_validation/
	@echo "✅ Backup created in backups/ directory"

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
