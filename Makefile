
# HX Infrastructure Ansible Makefile

.PHONY: help install lint syntax-check test security-test deploy-dev deploy-test deploy-prod gate-integration gate-performance gate-security

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt
	ansible-galaxy install -r requirements.yml

lint: ## Run linting checks
	yamllint .
	ansible-lint

syntax-check: ## Run syntax checks for all environments
	ansible-playbook --syntax-check -i environments/dev/inventories/hosts.yml site.yml
	ansible-playbook --syntax-check -i environments/test/inventories/hosts.yml site.yml
	ansible-playbook --syntax-check -i environments/prod/inventories/hosts.yml site.yml

test: ## Run all tests
	ansible-playbook tests/integration/test_basic.yml

security-test: ## Run security tests
	ansible-playbook tests/security/security_tests.yml

deploy-dev: ## Deploy to development environment
	./scripts/deploy/deploy.sh dev

deploy-test: ## Deploy to test environment
	./scripts/deploy/deploy.sh test

deploy-prod: ## Deploy to production environment
	./scripts/deploy/deploy.sh prod

backup: ## Create backup
	./scripts/backup/backup.sh

clean: ## Clean temporary files
	find . -name "*.retry" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Phase 2C Machine-Checkable Gates
gate-integration: ## Run integration gate validation
	@echo "Running integration gate validation..."
	./scripts/gates/gate_integration.sh

gate-performance: ## Run performance gate validation
	@echo "Running performance gate validation..."
	./scripts/gates/gate_performance.sh

gate-security: ## Run security gate validation
	@echo "Running security gate validation..."
	./scripts/gates/gate_security.sh

# Phase 2C Golden Path Tests
golden-path-all: ## Run all golden path tests
	@echo "Running all golden path tests..."
	./tests/golden_path/blue_green.sh
	./tests/golden_path/monitoring.sh
	./tests/golden_path/self_healing.sh

# Phase 2C Performance Benchmarks
benchmark: ## Run performance benchmarks
	@echo "Running performance benchmarks..."
	./scripts/perf_benchmark.sh

# Phase 2C Monitoring Validation
monitor-validate: ## Validate monitoring pipeline
	@echo "Validating monitoring pipeline..."
	./scripts/monitor_validate.sh
