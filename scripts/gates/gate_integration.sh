
#!/bin/bash
# Phase 2C Integration Gate Validation Script
# Machine-checkable gate for integration readiness

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "=== Phase 2C Integration Gate Validation ==="
echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

# Exit codes
EXIT_SUCCESS=0
EXIT_FAILURE=1

# Validation counters
CHECKS_PASSED=0
CHECKS_FAILED=0

# Helper function for check results
check_result() {
    local test_name="$1"
    local result="$2"
    
    if [ "$result" -eq 0 ]; then
        echo "✅ PASS: $test_name"
        ((CHECKS_PASSED++))
    else
        echo "❌ FAIL: $test_name"
        ((CHECKS_FAILED++))
    fi
}

# 1. Ansible Syntax Validation
echo "--- Checking Ansible Syntax ---"
cd "$PROJECT_ROOT"
ansible-playbook --syntax-check site.yml > /dev/null 2>&1
check_result "Ansible playbook syntax" $?

# 2. Role Dependencies Check
echo "--- Checking Role Dependencies ---"
if [ -f "requirements.yml" ]; then
    ansible-galaxy install -r requirements.yml --force > /dev/null 2>&1
    check_result "Role dependencies installation" $?
else
    check_result "Role dependencies file exists" 1
fi

# 3. Inventory Validation
echo "--- Checking Inventory Files ---"
for env in dev test prod; do
    if [ -f "environments/${env}/inventories/hosts.yml" ]; then
        ansible-inventory -i "environments/${env}/inventories/hosts.yml" --list > /dev/null 2>&1
        check_result "Inventory validation: $env" $?
    else
        check_result "Inventory file exists: $env" 1
    fi
done

# 4. Template Validation
echo "--- Checking Template Syntax ---"
find . -name "*.j2" -type f | while read -r template; do
    python3 -c "
import jinja2
try:
    with open('$template', 'r') as f:
        jinja2.Template(f.read())
    exit(0)
except Exception as e:
    print(f'Template error in $template: {e}')
    exit(1)
" > /dev/null 2>&1
    check_result "Template syntax: $(basename "$template")" $?
done

# 5. Vault File Validation
echo "--- Checking Vault Files ---"
find . -name "*vault*" -type f | while read -r vault_file; do
    if ansible-vault view "$vault_file" --vault-password-file <(echo "test") > /dev/null 2>&1; then
        check_result "Vault file accessible: $(basename "$vault_file")" 0
    else
        # Check if it's encrypted at least
        if grep -q "ANSIBLE_VAULT" "$vault_file"; then
            check_result "Vault file encrypted: $(basename "$vault_file")" 0
        else
            check_result "Vault file format: $(basename "$vault_file")" 1
        fi
    fi
done

# 6. Golden Path Integration Tests
echo "--- Running Golden Path Integration Tests ---"
if [ -f "tests/golden_path/blue_green.sh" ]; then
    bash tests/golden_path/blue_green.sh --validate-only > /dev/null 2>&1
    check_result "Blue-green deployment path" $?
fi

if [ -f "tests/golden_path/monitoring.sh" ]; then
    bash tests/golden_path/monitoring.sh --validate-only > /dev/null 2>&1
    check_result "Monitoring integration path" $?
fi

if [ -f "tests/golden_path/self_healing.sh" ]; then
    bash tests/golden_path/self_healing.sh --validate-only > /dev/null 2>&1
    check_result "Self-healing integration path" $?
fi

# Final Results
echo ""
echo "=== Integration Gate Results ==="
echo "Checks Passed: $CHECKS_PASSED"
echo "Checks Failed: $CHECKS_FAILED"
echo "Total Checks: $((CHECKS_PASSED + CHECKS_FAILED))"

if [ $CHECKS_FAILED -eq 0 ]; then
    echo "🎉 INTEGRATION GATE: PASSED"
    exit $EXIT_SUCCESS
else
    echo "🚫 INTEGRATION GATE: FAILED"
    echo "Please fix the failed checks before proceeding."
    exit $EXIT_FAILURE
fi
