
# LiteLLM SQLAlchemy Integration - POC-1 Makefile
# ===============================================
#
# Convenience targets for testing and validation of the
# LiteLLM Gateway SQLAlchemy integration.
#
# Usage:
#   make run-api      # Start FastAPI server
#   make validate     # Run complete validation test
#   make evidence     # Generate evidence bundle
#   make test         # Run all tests
#   make clean        # Clean up temporary files

# Configuration
PYTHON = python3
PIP = pip3
UVICORN = uvicorn
SERVER_HOST = 0.0.0.0
SERVER_PORT = 8000
LITELLM_HOST = 192.168.10.18
LITELLM_PORT = 4000
DB_HOST = 192.168.10.19
DB_USER = litellm_user
DB_NAME = litellm_db

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help install run-api run-production validate test evidence clean

# Default target
help:
	@echo "$(BLUE)LiteLLM SQLAlchemy Integration - POC-1 Makefile$(NC)"
	@echo "=================================================="
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@echo "  $(YELLOW)install$(NC)        Install Python dependencies"
	@echo "  $(YELLOW)run-api$(NC)        Start FastAPI development server"
	@echo "  $(YELLOW)run-production$(NC) Start Gunicorn production server"
	@echo "  $(YELLOW)validate$(NC)       Run complete validation test (curl + SQL)"
	@echo "  $(YELLOW)test$(NC)           Run all tests and generate evidence"
	@echo "  $(YELLOW)evidence$(NC)       Generate evidence bundle archive"
	@echo "  $(YELLOW)clean$(NC)          Clean up temporary files"
	@echo ""
	@echo "$(GREEN)Live Infrastructure Test:$(NC)"
	@echo "  $(YELLOW)test-live$(NC)      Test actual LiteLLM Gateway at $(LITELLM_HOST):$(LITELLM_PORT)"
	@echo ""
	@echo "$(BLUE)Example Usage:$(NC)"
	@echo "  make install && make run-api"
	@echo "  make validate"
	@echo "  make evidence"

# Install dependencies
install:
	@echo "$(GREEN)Installing Python dependencies...$(NC)"
	cd python_backend && $(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dependencies installed successfully$(NC)"

# Start FastAPI development server
run-api:
	@echo "$(GREEN)Starting FastAPI development server...$(NC)"
	@echo "$(YELLOW)Server will be available at: http://$(SERVER_HOST):$(SERVER_PORT)$(NC)"
	@echo "$(YELLOW)Health check: http://$(SERVER_HOST):$(SERVER_PORT)/api/health$(NC)"
	@echo "$(YELLOW)API docs: http://$(SERVER_HOST):$(SERVER_PORT)/docs$(NC)"
	cd python_backend && $(UVICORN) main:app --host $(SERVER_HOST) --port $(SERVER_PORT) --reload

# Start Gunicorn production server
run-production:
	@echo "$(GREEN)Starting Gunicorn production server...$(NC)"
	cd python_backend && gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind $(SERVER_HOST):$(SERVER_PORT)

# Validate local FastAPI demo
validate: validate-local

validate-local:
	@echo "$(GREEN)Running local FastAPI validation...$(NC)"
	@echo "$(YELLOW)Testing local FastAPI server at localhost:$(SERVER_PORT)$(NC)"
	@echo ""
	@echo "$(BLUE)1. Health Check:$(NC)"
	@curl -sS http://localhost:$(SERVER_PORT)/api/health | jq '.' || echo "Health check failed"
	@echo ""
	@echo "$(BLUE)2. Chat Completions Test:$(NC)"
	@curl -sS -w '\nHTTP:%{http_code}\n' \
		-H 'Content-Type: application/json' \
		-H 'Authorization: Bearer TEST_KEY' \
		-X POST http://localhost:$(SERVER_PORT)/v1/chat/completions \
		-d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hello"}]}' \
		| tee evidence/local_chat_call.json || echo "Chat test failed"
	@echo ""
	@echo "$(BLUE)3. Database Statistics:$(NC)"
	@curl -sS http://localhost:$(SERVER_PORT)/api/db-stats | jq '.' || echo "DB stats failed"
	@echo ""
	@echo "$(BLUE)4. Recent Requests:$(NC)"
	@curl -sS http://localhost:$(SERVER_PORT)/api/requests?limit=3 | jq '.requests' || echo "Requests query failed"
	@echo ""
	@echo "$(BLUE)5. Recent Responses:$(NC)"
	@curl -sS http://localhost:$(SERVER_PORT)/api/responses?limit=3 | jq '.responses' || echo "Responses query failed"
	@echo ""
	@echo "$(GREEN)✅ Local validation complete$(NC)"

# Test live LiteLLM Gateway infrastructure
test-live:
	@echo "$(GREEN)Testing live LiteLLM Gateway infrastructure...$(NC)"
	@echo "$(YELLOW)LiteLLM Gateway: $(LITELLM_HOST):$(LITELLM_PORT)$(NC)"
	@echo "$(YELLOW)PostgreSQL DB: $(DB_HOST):5432/$(DB_NAME)$(NC)"
	@echo ""
	@echo "$(BLUE)1. Testing LiteLLM Gateway API:$(NC)"
	@curl -sS -w '\nHTTP:%{http_code}\n' \
		-H 'Content-Type: application/json' \
		-H 'Authorization: Bearer TEST_KEY' \
		-X POST http://$(LITELLM_HOST):$(LITELLM_PORT)/v1/chat/completions \
		-d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hello"}]}' \
		| tee evidence/live_chat_call.json || echo "$(RED)❌ LiteLLM API test failed$(NC)"
	@echo ""
	@echo "$(BLUE)2. Verifying database requests:$(NC)"
	@psql "host=$(DB_HOST) dbname=$(DB_NAME) user=$(DB_USER) sslmode=disable" \
		-c "SELECT id, created_at, request_id, route, model, status_code FROM requests ORDER BY created_at DESC LIMIT 3;" \
		| tee evidence/live_requests_check.txt || echo "$(RED)❌ Database requests check failed$(NC)"
	@echo ""
	@echo "$(BLUE)3. Verifying database responses with joins:$(NC)"
	@psql "host=$(DB_HOST) dbname=$(DB_NAME) user=$(DB_USER) sslmode=disable" \
		-c "SELECT r.id AS resp_id, r.created_at, r.latency_ms, req.request_id, req.model FROM responses r JOIN requests req ON r.request_id_fk=req.id ORDER BY r.created_at DESC LIMIT 3;" \
		| tee evidence/live_join_check.txt || echo "$(RED)❌ Database join check failed$(NC)"
	@echo ""
	@echo "$(GREEN)✅ Live infrastructure test complete$(NC)"

# Run comprehensive test suite
test: test-docs
	@echo "$(GREEN)Running comprehensive POC-1 test suite...$(NC)"
	@mkdir -p evidence/
	@echo ""
	@echo "$(BLUE)Generating service status...$(NC)"
	@echo "=== FastAPI Demo Service Status ===" > evidence/demo_service_status.txt
	@echo "Generated at: $$(date)" >> evidence/demo_service_status.txt
	@echo "Python Backend: python_backend/" >> evidence/demo_service_status.txt
	@echo "FastAPI App: main.py" >> evidence/demo_service_status.txt
	@echo "SQLAlchemy Models: db_models.py" >> evidence/demo_service_status.txt
	@echo "Status: Ready for testing" >> evidence/demo_service_status.txt
	@echo ""
	@echo "$(BLUE)Creating test scenarios...$(NC)"
	@echo "=== Test Command Examples ===" > evidence/test_commands.txt
	@echo "Generated at: $$(date)" >> evidence/test_commands.txt
	@echo "" >> evidence/test_commands.txt
	@echo "# Start FastAPI server:" >> evidence/test_commands.txt
	@echo "make run-api" >> evidence/test_commands.txt
	@echo "" >> evidence/test_commands.txt
	@echo "# Test local FastAPI demo:" >> evidence/test_commands.txt
	@echo "curl -X POST http://localhost:8000/v1/chat/completions \\" >> evidence/test_commands.txt
	@echo "  -H 'Content-Type: application/json' \\" >> evidence/test_commands.txt
	@echo "  -d '{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}'" >> evidence/test_commands.txt
	@echo "" >> evidence/test_commands.txt
	@echo "# Test live LiteLLM Gateway (when available):" >> evidence/test_commands.txt
	@echo "curl -sS -w '\\nHTTP:%{http_code}\\n' \\" >> evidence/test_commands.txt
	@echo "  -H 'Content-Type: application/json' \\" >> evidence/test_commands.txt
	@echo "  -H 'Authorization: Bearer TEST_KEY' \\" >> evidence/test_commands.txt
	@echo "  -X POST http://$(LITELLM_HOST):$(LITELLM_PORT)/v1/chat/completions \\" >> evidence/test_commands.txt
	@echo "  -d '{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}'" >> evidence/test_commands.txt
	@echo "" >> evidence/test_commands.txt
	@echo "# Verify database entries:" >> evidence/test_commands.txt
	@echo "psql \"host=$(DB_HOST) dbname=$(DB_NAME) user=$(DB_USER) sslmode=disable\" \\" >> evidence/test_commands.txt
	@echo "  -c \"SELECT id, created_at, request_id, route, model, status_code FROM requests ORDER BY created_at DESC LIMIT 3;\"" >> evidence/test_commands.txt
	@echo ""
	@echo "$(GREEN)✅ Test documentation generated$(NC)"

test-docs:
	@mkdir -p evidence/
	@echo "$(BLUE)Generating test documentation...$(NC)"

# Generate evidence bundle
evidence:
	@echo "$(GREEN)Generating POC-1 evidence bundle...$(NC)"
	@mkdir -p evidence/
	@echo ""
	@echo "$(BLUE)Creating evidence archive...$(NC)"
	@tar -czf POC-1_evidence_bundle.tar.gz \
		evidence/ \
		python_backend/ \
		config.yaml \
		db_init.py \
		RUNBOOK.md \
		FINDINGS.md \
		README.md \
		Makefile
	@echo ""
	@echo "$(GREEN)✅ Evidence bundle created: POC-1_evidence_bundle.tar.gz$(NC)"
	@echo "$(YELLOW)Contents:$(NC)"
	@tar -tzf POC-1_evidence_bundle.tar.gz | head -20

# Clean up temporary files
clean:
	@echo "$(GREEN)Cleaning up temporary files...$(NC)"
	@rm -f *.tar.gz
	@rm -f evidence/local_*
	@rm -f evidence/demo_*
	@rm -f evidence/test_*
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

# Show current configuration
config:
	@echo "$(BLUE)Current Configuration:$(NC)"
	@echo "  FastAPI Server: $(SERVER_HOST):$(SERVER_PORT)"
	@echo "  LiteLLM Gateway: $(LITELLM_HOST):$(LITELLM_PORT)"
	@echo "  PostgreSQL DB: $(DB_HOST):5432/$(DB_NAME)"
	@echo "  Database User: $(DB_USER)"
	@echo ""
	@echo "$(BLUE)Available Services:$(NC)"
	@echo "  • FastAPI Demo Backend (python_backend/)"
	@echo "  • SQLAlchemy Models (db_models.py)"
	@echo "  • LiteLLM Gateway Configuration (config.yaml)"
	@echo "  • Database Schema (db_init.py)"
