
#!/bin/bash
# LiteLLM SQLAlchemy Integration - Live Infrastructure Test
# ========================================================
#
# This script runs the exact test sequence requested for final validation:
# 1. Test LiteLLM Gateway API at 192.168.10.18:4000
# 2. Verify database entries at 192.168.10.19
# 3. Confirm foreign key relationships and data integrity
#
# Expected: HTTP 200 + new rows in both tables immediately after curl

set -e  # Exit on error

# Configuration
LITELLM_HOST="192.168.10.18"
LITELLM_PORT="4000"
DB_HOST="192.168.10.19"
DB_USER="litellm_user"
DB_NAME="litellm_db"
EVIDENCE_DIR="evidence"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔬 LiteLLM SQLAlchemy Integration - Live Infrastructure Test${NC}"
echo "=============================================================="
echo ""
echo -e "${YELLOW}Target Infrastructure:${NC}"
echo "  LiteLLM Gateway: ${LITELLM_HOST}:${LITELLM_PORT}"
echo "  PostgreSQL DB:   ${DB_HOST}:5432/${DB_NAME}"
echo "  Evidence Dir:    ${EVIDENCE_DIR}/"
echo ""

# Create evidence directory
mkdir -p "${EVIDENCE_DIR}"

# Timestamp for evidence files
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

echo -e "${GREEN}Step 1: Testing LiteLLM Gateway API${NC}"
echo "-----------------------------------"
echo ""
echo -e "${BLUE}Command:${NC}"
echo "curl -sS -w '\\nHTTP:%{http_code}\\n' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'Authorization: Bearer TEST_KEY' \\"
echo "  -X POST http://${LITELLM_HOST}:${LITELLM_PORT}/v1/chat/completions \\"
echo "  -d '{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}'"
echo ""

# Execute the curl command
echo -e "${YELLOW}Executing API test...${NC}"
if curl -sS -w '\nHTTP:%{http_code}\n' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer TEST_KEY' \
  -X POST "http://${LITELLM_HOST}:${LITELLM_PORT}/v1/chat/completions" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hello"}]}' \
  | tee "${EVIDENCE_DIR}/live_chat_call_${TIMESTAMP}.json"; then
    echo -e "${GREEN}✅ API test completed${NC}"
else
    echo -e "${RED}❌ API test failed - check network connectivity to ${LITELLM_HOST}:${LITELLM_PORT}${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Step 2: Verifying Database Requests Table${NC}"
echo "----------------------------------------"
echo ""
echo -e "${BLUE}Command:${NC}"
echo "psql \"host=${DB_HOST} dbname=${DB_NAME} user=${DB_USER} sslmode=disable\" \\"
echo "  -c \"SELECT id, created_at, request_id, route, model, status_code FROM requests ORDER BY created_at DESC LIMIT 3;\""
echo ""

# Execute database query for requests
echo -e "${YELLOW}Querying requests table...${NC}"
if psql "host=${DB_HOST} dbname=${DB_NAME} user=${DB_USER} sslmode=disable" \
  -c "SELECT id, created_at, request_id, route, model, status_code FROM requests ORDER BY created_at DESC LIMIT 3;" \
  | tee "${EVIDENCE_DIR}/live_requests_${TIMESTAMP}.txt"; then
    echo -e "${GREEN}✅ Requests table query completed${NC}"
else
    echo -e "${RED}❌ Requests table query failed - check database connectivity${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Step 3: Verifying Database Responses with JOIN${NC}"
echo "---------------------------------------------"
echo ""
echo -e "${BLUE}Command:${NC}"
echo "psql \"host=${DB_HOST} dbname=${DB_NAME} user=${DB_USER} sslmode=disable\" \\"
echo "  -c \"SELECT r.id AS resp_id, r.created_at, r.latency_ms, req.request_id, req.model FROM responses r JOIN requests req ON r.request_id_fk=req.id ORDER BY r.created_at DESC LIMIT 3;\""
echo ""

# Execute database query for responses with JOIN
echo -e "${YELLOW}Querying responses table with JOIN...${NC}"
if psql "host=${DB_HOST} dbname=${DB_NAME} user=${DB_USER} sslmode=disable" \
  -c "SELECT r.id AS resp_id, r.created_at, r.latency_ms, req.request_id, req.model FROM responses r JOIN requests req ON r.request_id_fk=req.id ORDER BY r.created_at DESC LIMIT 3;" \
  | tee "${EVIDENCE_DIR}/live_join_check_${TIMESTAMP}.txt"; then
    echo -e "${GREEN}✅ Responses JOIN query completed${NC}"
else
    echo -e "${RED}❌ Responses JOIN query failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Live Infrastructure Test Complete${NC}"
echo "======================================="
echo ""
echo -e "${BLUE}Evidence Files Generated:${NC}"
echo "  • ${EVIDENCE_DIR}/live_chat_call_${TIMESTAMP}.json     (API response)"
echo "  • ${EVIDENCE_DIR}/live_requests_${TIMESTAMP}.txt      (database requests)"
echo "  • ${EVIDENCE_DIR}/live_join_check_${TIMESTAMP}.txt    (database responses with JOIN)"
echo ""
echo -e "${YELLOW}Expected Results:${NC}"
echo "  ✅ API call returns HTTP 200 with chat completion response"
echo "  ✅ New request entry appears in requests table immediately"
echo "  ✅ New response entry appears in responses table with foreign key relationship"
echo "  ✅ JOIN query confirms request_id_fk relationship integrity"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo "  1. Review evidence files in ${EVIDENCE_DIR}/"
echo "  2. Verify response times meet <5ms database overhead requirement"
echo "  3. Confirm all foreign key relationships are maintained"
echo "  4. Package evidence into final POC-1 deliverable"
echo ""
echo -e "${BLUE}Test completed at: $(date)${NC}"
