
#!/bin/bash
# Phase 2C Performance Gate Validation Script
# Machine-checkable gate for performance SLOs

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "=== Phase 2C Performance Gate Validation ==="
echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

# Exit codes
EXIT_SUCCESS=0
EXIT_FAILURE=1

# SLO Thresholds (in seconds)
SLO_DEPLOY_TIME_P95=480    # 8 minutes
SLO_PLAYBOOK_RUNTIME=90    # 90 seconds
SLO_ROLE_EXECUTION=30      # 30 seconds per role
SLO_TEMPLATE_RENDER=5      # 5 seconds
SLO_VAULT_DECRYPT=2        # 2 seconds

# Validation counters
CHECKS_PASSED=0
CHECKS_FAILED=0

# Helper function for check results
check_result() {
    local test_name="$1"
    local result="$2"
    local actual_time="$3"
    local threshold="$4"
    
    if [ "$result" -eq 0 ]; then
        echo "✅ PASS: $test_name (${actual_time}s ≤ ${threshold}s)"
        ((CHECKS_PASSED++))
    else
        echo "❌ FAIL: $test_name (${actual_time}s > ${threshold}s)"
        ((CHECKS_FAILED++))
    fi
}

# Helper function to measure execution time
measure_time() {
    local start_time=$(date +%s.%N)
    "$@"
    local exit_code=$?
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)
    echo "$duration"
    return $exit_code
}

echo "--- Performance SLO Validation ---"
cd "$PROJECT_ROOT"

# 1. Playbook Syntax Check Performance
echo "Testing playbook syntax check performance..."
duration=$(measure_time ansible-playbook --syntax-check site.yml 2>/dev/null)
exit_code=$?
actual_time=$(printf "%.2f" "$duration")
if [ "$exit_code" -eq 0 ] && [ "$(echo "$duration < $SLO_PLAYBOOK_RUNTIME" | bc -l)" -eq 1 ]; then
    check_result "Playbook syntax check" 0 "$actual_time" "$SLO_PLAYBOOK_RUNTIME"
else
    check_result "Playbook syntax check" 1 "$actual_time" "$SLO_PLAYBOOK_RUNTIME"
fi

# 2. Role Installation Performance
echo "Testing role installation performance..."
if [ -f "requirements.yml" ]; then
    duration=$(measure_time ansible-galaxy install -r requirements.yml --force 2>/dev/null)
    exit_code=$?
    actual_time=$(printf "%.2f" "$duration")
    if [ "$exit_code" -eq 0 ] && [ "$(echo "$duration < $SLO_ROLE_EXECUTION" | bc -l)" -eq 1 ]; then
        check_result "Role installation" 0 "$actual_time" "$SLO_ROLE_EXECUTION"
    else
        check_result "Role installation" 1 "$actual_time" "$SLO_ROLE_EXECUTION"
    fi
fi

# 3. Template Rendering Performance
echo "Testing template rendering performance..."
template_count=0
total_template_time=0

find . -name "*.j2" -type f | while read -r template; do
    duration=$(measure_time python3 -c "
import jinja2
import time
start = time.time()
with open('$template', 'r') as f:
    jinja2.Template(f.read()).render()
print(time.time() - start)
" 2>/dev/null | tail -1)
    
    if [ -n "$duration" ]; then
        template_count=$((template_count + 1))
        total_template_time=$(echo "$total_template_time + $duration" | bc -l)
        
        actual_time=$(printf "%.2f" "$duration")
        if [ "$(echo "$duration < $SLO_TEMPLATE_RENDER" | bc -l)" -eq 1 ]; then
            check_result "Template render: $(basename "$template")" 0 "$actual_time" "$SLO_TEMPLATE_RENDER"
        else
            check_result "Template render: $(basename "$template")" 1 "$actual_time" "$SLO_TEMPLATE_RENDER"
        fi
    fi
done

# 4. Inventory Parsing Performance
echo "Testing inventory parsing performance..."
for env in dev test prod; do
    if [ -f "environments/${env}/inventories/hosts.yml" ]; then
        duration=$(measure_time ansible-inventory -i "environments/${env}/inventories/hosts.yml" --list 2>/dev/null)
        exit_code=$?
        actual_time=$(printf "%.2f" "$duration")
        
        if [ "$exit_code" -eq 0 ] && [ "$(echo "$duration < 10" | bc -l)" -eq 1 ]; then
            check_result "Inventory parsing: $env" 0 "$actual_time" "10"
        else
            check_result "Inventory parsing: $env" 1 "$actual_time" "10"
        fi
    fi
done

# 5. Linting Performance
echo "Testing linting performance..."
duration=$(measure_time yamllint . 2>/dev/null)
exit_code=$?
actual_time=$(printf "%.2f" "$duration")
if [ "$(echo "$duration < 15" | bc -l)" -eq 1 ]; then
    check_result "YAML linting" 0 "$actual_time" "15"
else
    check_result "YAML linting" 1 "$actual_time" "15"
fi

duration=$(measure_time ansible-lint 2>/dev/null)
exit_code=$?
actual_time=$(printf "%.2f" "$duration")
if [ "$(echo "$duration < 30" | bc -l)" -eq 1 ]; then
    check_result "Ansible linting" 0 "$actual_time" "30"
else
    check_result "Ansible linting" 1 "$actual_time" "30"
fi

# Final Results
echo ""
echo "=== Performance Gate Results ==="
echo "Checks Passed: $CHECKS_PASSED"
echo "Checks Failed: $CHECKS_FAILED"
echo "Total Checks: $((CHECKS_PASSED + CHECKS_FAILED))"

echo ""
echo "=== SLO Summary ==="
echo "Deploy Time P95 Target: ≤ ${SLO_DEPLOY_TIME_P95}s (8 min)"
echo "Playbook Runtime Target: ≤ ${SLO_PLAYBOOK_RUNTIME}s"
echo "Role Execution Target: ≤ ${SLO_ROLE_EXECUTION}s"
echo "Template Render Target: ≤ ${SLO_TEMPLATE_RENDER}s"
echo "Vault Decrypt Target: ≤ ${SLO_VAULT_DECRYPT}s"

if [ $CHECKS_FAILED -eq 0 ]; then
    echo "🎉 PERFORMANCE GATE: PASSED"
    exit $EXIT_SUCCESS
else
    echo "🚫 PERFORMANCE GATE: FAILED"
    echo "Performance SLOs not met. Please optimize before proceeding."
    exit $EXIT_FAILURE
fi
