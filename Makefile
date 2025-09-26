# HX Infrastructure Ansible Makefile

.PHONY: help install lint syntax-check test security-test deploy-dev deploy-test deploy-prod

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
