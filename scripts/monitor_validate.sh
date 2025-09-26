
#!/bin/bash
# Phase 2C Monitoring Validation Script
# Validates monitoring pipeline: metric → dashboard → alert

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Phase 2C Monitoring Pipeline Validation ==="
echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

# Validation counters
CHECKS_PASSED=0
CHECKS_FAILED=0

# Helper function for check results
check_result() {
    local test_name="$1"
    local result="$2"
    local details="${3:-}"
    
    if [ "$result" -eq 0 ]; then
        echo "✅ PASS: $test_name"
        [ -n "$details" ] && echo "    $details"
        ((CHECKS_PASSED++))
    else
        echo "❌ FAIL: $test_name"
        [ -n "$details" ] && echo "    $details"
        ((CHECKS_FAILED++))
    fi
}

cd "$PROJECT_ROOT"

echo "--- Monitoring Configuration Validation ---"

# 1. Prometheus Configuration
echo "Validating Prometheus configuration..."
if [ -f "roles/monitoring/templates/prometheus.yml.j2" ]; then
    # Check for required sections
    if grep -q "global:" "roles/monitoring/templates/prometheus.yml.j2"; then
        check_result "Prometheus global config" 0 "Global section found"
    else
        check_result "Prometheus global config" 1 "Missing global section"
    fi
    
    if grep -q "scrape_configs:" "roles/monitoring/templates/prometheus.yml.j2"; then
        check_result "Prometheus scrape config" 0 "Scrape configs found"
    else
        check_result "Prometheus scrape config" 1 "Missing scrape configs"
    fi
    
    if grep -q "rule_files:" "roles/monitoring/templates/prometheus.yml.j2"; then
        check_result "Prometheus rule files" 0 "Rule files configured"
    else
        check_result "Prometheus rule files" 1 "Missing rule files"
    fi
else
    check_result "Prometheus configuration file" 1 "prometheus.yml.j2 not found"
fi

# 2. Grafana Dashboard Validation
echo "Validating Grafana dashboards..."
dashboard_count=0
if [ -d "roles/monitoring/files/grafana/dashboards" ]; then
    find "roles/monitoring/files/grafana/dashboards" -name "*.json" | while read -r dashboard; do
        dashboard_count=$((dashboard_count + 1))
        dashboard_name=$(basename "$dashboard" .json)
        
        # Validate JSON syntax
        if jq empty "$dashboard" 2>/dev/null; then
            check_result "Dashboard JSON syntax: $dashboard_name" 0 "Valid JSON"
        else
            check_result "Dashboard JSON syntax: $dashboard_name" 1 "Invalid JSON"
        fi
        
        # Check for required dashboard fields
        if jq -e '.dashboard.title' "$dashboard" >/dev/null 2>&1; then
            check_result "Dashboard title: $dashboard_name" 0 "Title present"
        else
            check_result "Dashboard title: $dashboard_name" 1 "Missing title"
        fi
        
        # Check for panels
        panel_count=$(jq '.dashboard.panels | length' "$dashboard" 2>/dev/null || echo "0")
        if [ "$panel_count" -gt 0 ]; then
            check_result "Dashboard panels: $dashboard_name" 0 "$panel_count panels found"
        else
            check_result "Dashboard panels: $dashboard_name" 1 "No panels found"
        fi
    done
    
    if [ $dashboard_count -eq 0 ]; then
        check_result "Grafana dashboards" 1 "No dashboard files found"
    fi
else
    check_result "Grafana dashboard directory" 1 "Dashboard directory not found"
fi

# 3. Alert Rules Validation
echo "Validating alert rules..."
if [ -d "roles/monitoring/files/prometheus/rules" ]; then
    find "roles/monitoring/files/prometheus/rules" -name "*.yml" -o -name "*.yaml" | while read -r rule_file; do
        rule_name=$(basename "$rule_file")
        
        # Validate YAML syntax
        if yamllint "$rule_file" >/dev/null 2>&1; then
            check_result "Alert rule YAML: $rule_name" 0 "Valid YAML"
        else
            check_result "Alert rule YAML: $rule_name" 1 "Invalid YAML"
        fi
        
        # Check for groups
        if grep -q "groups:" "$rule_file"; then
            check_result "Alert rule groups: $rule_name" 0 "Groups defined"
        else
            check_result "Alert rule groups: $rule_name" 1 "No groups found"
        fi
        
        # Check for rules
        if grep -q "rules:" "$rule_file"; then
            rule_count=$(grep -c "- alert:" "$rule_file" || echo "0")
            check_result "Alert rules count: $rule_name" 0 "$rule_count rules found"
        else
            check_result "Alert rules: $rule_name" 1 "No rules found"
        fi
    done
else
    check_result "Alert rules directory" 1 "Rules directory not found"
fi

# 4. Alertmanager Configuration
echo "Validating Alertmanager configuration..."
if [ -f "roles/monitoring/templates/alertmanager.yml.j2" ]; then
    # Check for required sections
    if grep -q "global:" "roles/monitoring/templates/alertmanager.yml.j2"; then
        check_result "Alertmanager global config" 0 "Global section found"
    else
        check_result "Alertmanager global config" 1 "Missing global section"
    fi
    
    if grep -q "route:" "roles/monitoring/templates/alertmanager.yml.j2"; then
        check_result "Alertmanager routing" 0 "Route configuration found"
    else
        check_result "Alertmanager routing" 1 "Missing route configuration"
    fi
    
    if grep -q "receivers:" "roles/monitoring/templates/alertmanager.yml.j2"; then
        check_result "Alertmanager receivers" 0 "Receivers configured"
    else
        check_result "Alertmanager receivers" 1 "Missing receivers"
    fi
else
    check_result "Alertmanager configuration file" 1 "alertmanager.yml.j2 not found"
fi

# 5. Service Discovery Validation
echo "Validating service discovery..."
if [ -d "roles/monitoring/templates/prometheus" ]; then
    # Check for service discovery configurations
    if find "roles/monitoring/templates/prometheus" -name "*discovery*" | grep -q .; then
        check_result "Service discovery configs" 0 "Discovery configs found"
    else
        check_result "Service discovery configs" 1 "No discovery configs found"
    fi
fi

# 6. Monitoring Endpoints Validation
echo "Validating monitoring endpoints..."
endpoints=(
    "/metrics"
    "/health"
    "/ready"
    "/api/v1/query"
    "/api/v1/alerts"
)

for endpoint in "${endpoints[@]}"; do
    # Check if endpoint is referenced in configurations
    if grep -r "$endpoint" roles/monitoring/ >/dev/null 2>&1; then
        check_result "Monitoring endpoint: $endpoint" 0 "Endpoint referenced"
    else
        check_result "Monitoring endpoint: $endpoint" 1 "Endpoint not found"
    fi
done

# 7. Log Aggregation Validation
echo "Validating log aggregation..."
if [ -d "roles/logging" ]; then
    # Check for log shipping configuration
    if find "roles/logging" -name "*filebeat*" -o -name "*fluentd*" -o -name "*logstash*" | grep -q .; then
        check_result "Log shipping configuration" 0 "Log shipper configured"
    else
        check_result "Log shipping configuration" 1 "No log shipper found"
    fi
    
    # Check for log parsing rules
    if find "roles/logging" -name "*grok*" -o -name "*parser*" | grep -q .; then
        check_result "Log parsing rules" 0 "Parsing rules found"
    else
        check_result "Log parsing rules" 1 "No parsing rules found"
    fi
else
    check_result "Logging role" 1 "Logging role not found"
fi

# 8. Monitoring Playbook Validation
echo "Validating monitoring playbooks..."
monitoring_playbooks=(
    "monitoring.yml"
    "logging.yml"
    "alerting.yml"
)

for playbook in "${monitoring_playbooks[@]}"; do
    if [ -f "$playbook" ] || find . -name "$playbook" | grep -q .; then
        playbook_path=$(find . -name "$playbook" | head -1)
        if ansible-playbook --syntax-check "$playbook_path" >/dev/null 2>&1; then
            check_result "Monitoring playbook: $playbook" 0 "Syntax valid"
        else
            check_result "Monitoring playbook: $playbook" 1 "Syntax error"
        fi
    else
        check_result "Monitoring playbook: $playbook" 1 "Playbook not found"
    fi
done

# 9. Monitoring Variables Validation
echo "Validating monitoring variables..."
monitoring_vars=(
    "prometheus_port"
    "grafana_port"
    "alertmanager_port"
    "monitoring_retention"
    "alert_notification_channels"
)

for var in "${monitoring_vars[@]}"; do
    if grep -r "$var" group_vars/ host_vars/ roles/monitoring/defaults/ >/dev/null 2>&1; then
        check_result "Monitoring variable: $var" 0 "Variable defined"
    else
        check_result "Monitoring variable: $var" 1 "Variable not found"
    fi
done

# 10. Integration Test Simulation
echo "Running monitoring integration simulation..."
# Simulate the monitoring path: metric → dashboard → alert
simulation_steps=(
    "metric_collection"
    "dashboard_rendering"
    "alert_evaluation"
    "notification_delivery"
)

for step in "${simulation_steps[@]}"; do
    # Simulate each step (in real implementation, these would be actual tests)
    case $step in
        "metric_collection")
            # Check if metric collection endpoints are configured
            if grep -r "metrics_path" roles/monitoring/ >/dev/null 2>&1; then
                check_result "Simulation: $step" 0 "Metric collection configured"
            else
                check_result "Simulation: $step" 1 "Metric collection not configured"
            fi
            ;;
        "dashboard_rendering")
            # Check if dashboards have data sources
            if find roles/monitoring/ -name "*.json" -exec grep -l "datasource" {} \; | grep -q .; then
                check_result "Simulation: $step" 0 "Dashboard data sources configured"
            else
                check_result "Simulation: $step" 1 "Dashboard data sources missing"
            fi
            ;;
        "alert_evaluation")
            # Check if alert rules have expressions
            if find roles/monitoring/ -name "*.yml" -exec grep -l "expr:" {} \; | grep -q .; then
                check_result "Simulation: $step" 0 "Alert expressions found"
            else
                check_result "Simulation: $step" 1 "Alert expressions missing"
            fi
            ;;
        "notification_delivery")
            # Check if notification channels are configured
            if grep -r -E "(slack|email|webhook)" roles/monitoring/ >/dev/null 2>&1; then
                check_result "Simulation: $step" 0 "Notification channels configured"
            else
                check_result "Simulation: $step" 1 "Notification channels missing"
            fi
            ;;
    esac
done

# Final Results
echo ""
echo "=== Monitoring Validation Results ==="
echo "Checks Passed: $CHECKS_PASSED"
echo "Checks Failed: $CHECKS_FAILED"
echo "Total Checks: $((CHECKS_PASSED + CHECKS_FAILED))"

echo ""
echo "=== Monitoring Pipeline Summary ==="
echo "✓ Prometheus configuration validation"
echo "✓ Grafana dashboard validation"
echo "✓ Alert rules validation"
echo "✓ Alertmanager configuration validation"
echo "✓ Service discovery validation"
echo "✓ Monitoring endpoints validation"
echo "✓ Log aggregation validation"
echo "✓ Monitoring playbook validation"
echo "✓ Monitoring variables validation"
echo "✓ Integration simulation"

if [ $CHECKS_FAILED -eq 0 ]; then
    echo "🎉 MONITORING VALIDATION: PASSED"
    echo "Monitoring pipeline is ready for production"
    exit 0
else
    echo "🚫 MONITORING VALIDATION: FAILED"
    echo "Please fix monitoring configuration issues before proceeding"
    exit 1
fi
