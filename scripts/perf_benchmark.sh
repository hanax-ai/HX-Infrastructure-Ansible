
#!/bin/bash
# Phase 2C Performance Benchmark Script
# Quantified SLO measurement and validation

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Phase 2C Performance Benchmark ==="
echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

# Create benchmark results directory
RESULTS_DIR="$PROJECT_ROOT/benchmark_results"
mkdir -p "$RESULTS_DIR"
RESULTS_FILE="$RESULTS_DIR/benchmark_$(date +%Y%m%d_%H%M%S).json"

# SLO Thresholds
declare -A SLO_THRESHOLDS=(
    ["deploy_time_p95"]=480      # 8 minutes
    ["playbook_runtime"]=90      # 90 seconds
    ["role_execution"]=30        # 30 seconds per role
    ["template_render"]=5        # 5 seconds
    ["vault_decrypt"]=2          # 2 seconds
    ["inventory_parse"]=10       # 10 seconds
    ["lint_yaml"]=15            # 15 seconds
    ["lint_ansible"]=30         # 30 seconds
)

# Initialize results JSON
cat > "$RESULTS_FILE" << EOF
{
  "benchmark_timestamp": "$(date -u '+%Y-%m-%d %H:%M:%S UTC')",
  "slo_thresholds": $(printf '%s\n' "${!SLO_THRESHOLDS[@]}" | jq -R . | jq -s 'map(split("=") | {(.[0]): .[1]|tonumber}) | add'),
  "results": {},
  "summary": {
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "slo_compliance": 0.0
  }
}
EOF

# Helper function to measure execution time
measure_execution() {
    local test_name="$1"
    local threshold="$2"
    shift 2
    
    echo "Benchmarking: $test_name"
    
    local start_time=$(date +%s.%N)
    local exit_code=0
    "$@" > /dev/null 2>&1 || exit_code=$?
    local end_time=$(date +%s.%N)
    
    local duration=$(echo "$end_time - $start_time" | bc -l)
    local duration_formatted=$(printf "%.3f" "$duration")
    local passed=$([ "$(echo "$duration < $threshold" | bc -l)" -eq 1 ] && echo "true" || echo "false")
    
    # Update results JSON
    jq --arg name "$test_name" \
       --arg duration "$duration_formatted" \
       --arg threshold "$threshold" \
       --arg passed "$passed" \
       --arg exit_code "$exit_code" \
       '.results[$name] = {
         "duration_seconds": ($duration | tonumber),
         "threshold_seconds": ($threshold | tonumber),
         "passed": ($passed | test("true")),
         "exit_code": ($exit_code | tonumber),
         "slo_met": ($passed | test("true"))
       }' "$RESULTS_FILE" > "${RESULTS_FILE}.tmp" && mv "${RESULTS_FILE}.tmp" "$RESULTS_FILE"
    
    if [ "$passed" = "true" ]; then
        echo "  ✅ PASS: ${duration_formatted}s ≤ ${threshold}s"
    else
        echo "  ❌ FAIL: ${duration_formatted}s > ${threshold}s"
    fi
    
    return $exit_code
}

cd "$PROJECT_ROOT"

echo "--- Running Performance Benchmarks ---"

# 1. Playbook Syntax Check
measure_execution "playbook_syntax_check" "${SLO_THRESHOLDS[playbook_runtime]}" \
    ansible-playbook --syntax-check site.yml

# 2. Role Installation
if [ -f "requirements.yml" ]; then
    measure_execution "role_installation" "${SLO_THRESHOLDS[role_execution]}" \
        ansible-galaxy install -r requirements.yml --force
fi

# 3. Inventory Parsing
for env in dev test prod; do
    if [ -f "environments/${env}/inventories/hosts.yml" ]; then
        measure_execution "inventory_parse_${env}" "${SLO_THRESHOLDS[inventory_parse]}" \
            ansible-inventory -i "environments/${env}/inventories/hosts.yml" --list
    fi
done

# 4. Template Rendering
template_count=0
find . -name "*.j2" -type f | head -5 | while read -r template; do
    template_name=$(basename "$template" .j2)
    measure_execution "template_render_${template_name}" "${SLO_THRESHOLDS[template_render]}" \
        python3 -c "
import jinja2
with open('$template', 'r') as f:
    jinja2.Template(f.read()).render()
"
    template_count=$((template_count + 1))
done

# 5. Linting Performance
measure_execution "yaml_linting" "${SLO_THRESHOLDS[lint_yaml]}" \
    yamllint .

measure_execution "ansible_linting" "${SLO_THRESHOLDS[lint_ansible]}" \
    ansible-lint

# 6. Vault Operations (if vault files exist)
find . -name "*vault*" -type f | head -3 | while read -r vault_file; do
    vault_name=$(basename "$vault_file")
    # Test vault file validation (not decryption due to password requirements)
    measure_execution "vault_validate_${vault_name}" "${SLO_THRESHOLDS[vault_decrypt]}" \
        python3 -c "
import os
with open('$vault_file', 'r') as f:
    content = f.read()
    if 'ANSIBLE_VAULT' in content:
        print('Valid vault file')
    else:
        raise ValueError('Invalid vault file')
"
done

# 7. Golden Path Performance Tests
if [ -f "tests/golden_path/blue_green.sh" ]; then
    measure_execution "golden_path_blue_green" "60" \
        bash tests/golden_path/blue_green.sh --benchmark-mode
fi

if [ -f "tests/golden_path/monitoring.sh" ]; then
    measure_execution "golden_path_monitoring" "30" \
        bash tests/golden_path/monitoring.sh --benchmark-mode
fi

if [ -f "tests/golden_path/self_healing.sh" ]; then
    measure_execution "golden_path_self_healing" "45" \
        bash tests/golden_path/self_healing.sh --benchmark-mode
fi

# Calculate summary statistics
jq '
.summary.total_tests = (.results | length) |
.summary.passed_tests = [.results[] | select(.slo_met == true)] | length |
.summary.failed_tests = [.results[] | select(.slo_met == false)] | length |
.summary.slo_compliance = ((.summary.passed_tests / .summary.total_tests) * 100 | floor) |
.summary.average_duration = ([.results[].duration_seconds] | add / length) |
.summary.p95_duration = ([.results[].duration_seconds] | sort | .[(.| length * 0.95 | floor)]) |
.summary.max_duration = ([.results[].duration_seconds] | max)
' "$RESULTS_FILE" > "${RESULTS_FILE}.tmp" && mv "${RESULTS_FILE}.tmp" "$RESULTS_FILE"

# Display results
echo ""
echo "=== Benchmark Results Summary ==="
jq -r '
"Total Tests: " + (.summary.total_tests | tostring) +
"\nPassed Tests: " + (.summary.passed_tests | tostring) +
"\nFailed Tests: " + (.summary.failed_tests | tostring) +
"\nSLO Compliance: " + (.summary.slo_compliance | tostring) + "%" +
"\nAverage Duration: " + (.summary.average_duration | tostring) + "s" +
"\nP95 Duration: " + (.summary.p95_duration | tostring) + "s" +
"\nMax Duration: " + (.summary.max_duration | tostring) + "s"
' "$RESULTS_FILE"

echo ""
echo "=== SLO Compliance Details ==="
jq -r '
.results | to_entries[] | 
"  " + .key + ": " + 
(.value.duration_seconds | tostring) + "s / " + 
(.value.threshold_seconds | tostring) + "s " +
(if .value.slo_met then "✅" else "❌" end)
' "$RESULTS_FILE"

echo ""
echo "Detailed results saved to: $RESULTS_FILE"

# Exit with appropriate code
compliance=$(jq -r '.summary.slo_compliance' "$RESULTS_FILE")
if [ "$compliance" -eq 100 ]; then
    echo "🎉 ALL SLOs MET"
    exit 0
else
    echo "⚠️  SLO COMPLIANCE: ${compliance}%"
    exit 1
fi
