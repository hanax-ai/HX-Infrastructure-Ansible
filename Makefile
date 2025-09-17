
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

validate-test:
	@echo "Validating test environment variables..."
	@python3 vars_validation/validate_vars.py \
		inventories/group_vars/*.yml \
		inventories/test/group_vars/*.yml 2>/dev/null || \
		python3 vars_validation/validate_vars.py inventories/group_vars/*.yml
	@echo "✅ Test environment variables validated"

validate-prod:
	@echo "Validating production environment variables..."
	@python3 vars_validation/validate_vars.py \
		inventories/group_vars/*.yml \
		inventories/prod/group_vars/*.yml 2>/dev/null || \
		python3 vars_validation/validate_vars.py inventories/group_vars/*.yml
	@echo "✅ Production environment variables validated"

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

# Comprehensive linting
lint: check-syntax
	@echo "Running comprehensive linting..."
	@echo "Checking for common variable naming issues..."
	@! grep -r "ansible_ssh_pass" inventories/ || (echo "❌ Found hardcoded SSH passwords" && exit 1)
	@! grep -r "password.*:" inventories/group_vars/ | grep -v vault || (echo "❌ Found unencrypted passwords" && exit 1)
	@echo "Checking for required vault variables..."
	@grep -q "vault_postgres_password" inventories/group_vars/vault.yml 2>/dev/null || \
		echo "⚠️  Warning: vault_postgres_password not found in vault.yml"
	@grep -q "vault_jwt_secret" inventories/group_vars/vault.yml 2>/dev/null || \
		echo "⚠️  Warning: vault_jwt_secret not found in vault.yml"
	@echo "Checking variable consistency..."
	@python3 -c "
import yaml, glob, sys
files = glob.glob('inventories/group_vars/*.yml')
vars_found = set()
for f in files:
    if 'vault' not in f:
        try:
            with open(f) as file:
                data = yaml.safe_load(file) or {}
                def extract_vars(d, prefix=''):
                    for k, v in d.items():
                        if isinstance(v, dict):
                            extract_vars(v, prefix + k + '_')
                        else:
                            vars_found.add(prefix + k)
                extract_vars(data)
        except Exception as e:
            print(f'Error processing {f}: {e}')
            sys.exit(1)
print('✅ Variable consistency check passed')
"
	@echo "✅ All linting checks passed"

# Cleanup
clean:
	@echo "Cleaning up temporary files..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.tmp" -delete
	@find . -name ".DS_Store" -delete
	@echo "✅ Cleanup completed"

# Development helpers
dev-setup:
	@echo "Setting up development environment..."
	@pip3 install pyyaml ansible-core
	@chmod +x vars_validation/validate_vars.py
	@echo "✅ Development environment ready"

# Quick validation for CI/CD
ci-validate: check-syntax validate-vars
	@echo "✅ CI validation completed successfully"

# Generate documentation
docs:
	@echo "Generating documentation..."
	@python3 -c "
import yaml
with open('vars_validation/validation_rules.yml') as f:
    rules = yaml.safe_load(f)
    
print('# Variable Reference\\n')
for category, vars_info in rules.items():
    if category.endswith('_variables'):
        print(f'## {category.replace(\"_\", \" \").title()}\\n')
        if 'required' in vars_info:
            print('### Required Variables\\n')
            for var in vars_info['required']:
                print(f'- **{var[\"name\"]}**: {var.get(\"description\", \"No description\")}')
            print()
        if 'optional' in vars_info:
            print('### Optional Variables\\n')
            for var in vars_info['optional']:
                print(f'- **{var[\"name\"]}**: {var.get(\"description\", \"No description\")} (default: {var.get(\"default\", \"None\")})')
            print()
" > docs/VARIABLE_REFERENCE.md
	@echo "✅ Documentation generated"

# Backup current configuration
backup:
	@echo "Creating backup of current configuration..."
	@mkdir -p backups
	@tar -czf backups/variables-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz \
		inventories/group_vars/ \
		role_defaults/ \
		vars_validation/
	@echo "✅ Backup created in backups/ directory"

# Restore from backup
restore:
	@echo "Available backups:"
	@ls -la backups/variables-backup-*.tar.gz 2>/dev/null || echo "No backups found"
	@echo "To restore, run: tar -xzf backups/variables-backup-YYYYMMDD-HHMMSS.tar.gz"
