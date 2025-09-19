
#!/bin/bash
# HX Infrastructure - Health Check Script
# Phase 3.4 - Production Operations Automation

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../" && pwd)"
LOG_DIR="/var/log/hx-infrastructure"
HEALTH_CHECK_TIMEOUT=30

# Default values
CHECK_TYPE="${CHECK_TYPE:-all}"
OUTPUT_FORMAT="${OUTPUT_FORMAT:-json}"
ALERT_ON_FAILURE="${ALERT_ON_FAILURE:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Initialize health check results
init_results() {
    HEALTH_RESULTS='{
        "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
        "hostname": "'$(hostname)'",
        "checks": {},
        "overall_status": "unknown",
        "failed_checks": []
    }'
}

# System resource checks
check_system_resources() {
    log "Checking system resources..."
    
    local cpu_usage memory_usage disk_usage load_avg
    
    # CPU usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}' || echo "0")
    
    # Memory usage
    memory_usage=$(free | grep Mem | awk '{printf "%.1f", ($3/$2) * 100.0}' || echo "0")
    
    # Disk usage
    disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//' || echo "0")
    
    # Load average
    load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//' || echo "0")
    
    # Evaluate thresholds
    local cpu_status="healthy"
    local memory_status="healthy"
    local disk_status="healthy"
    local load_status="healthy"
    
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        cpu_status="critical"
    elif (( $(echo "$cpu_usage > 60" | bc -l) )); then
        cpu_status="warning"
    fi
    
    if (( $(echo "$memory_usage > 85" | bc -l) )); then
        memory_status="critical"
    elif (( $(echo "$memory_usage > 70" | bc -l) )); then
        memory_status="warning"
    fi
    
    if (( disk_usage > 90 )); then
        disk_status="critical"
    elif (( disk_usage > 80 )); then
        disk_status="warning"
    fi
    
    if (( $(echo "$load_avg > 5.0" | bc -l) )); then
        load_status="critical"
    elif (( $(echo "$load_avg > 3.0" | bc -l) )); then
        load_status="warning"
    fi
    
    # Update results
    HEALTH_RESULTS=$(echo "$HEALTH_RESULTS" | jq --argjson system_check '{
        "cpu": {
            "usage": '${cpu_usage}',
            "status": "'${cpu_status}'"
        },
        "memory": {
            "usage": '${memory_usage}',
            "status": "'${memory_status}'"
        },
        "disk": {
            "usage": '${disk_usage}',
            "status": "'${disk_status}'"
        },
        "load": {
            "average": '${load_avg}',
            "status": "'${load_status}'"
        }
    }' '.checks.system = $system_check')
    
    success "System resource check completed"
}

# Service health checks
check_services() {
    log "Checking critical services..."
    
    local services=("nginx" "postgresql" "docker" "ssh")
    local service_results='{}'
    
    for service in "${services[@]}"; do
        local status="unknown"
        local active="false"
        
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            status="healthy"
            active="true"
        else
            status="critical"
            active="false"
        fi
        
        service_results=$(echo "$service_results" | jq --arg service "$service" --arg status "$status" --argjson active "$active" \
            '.[$service] = {"status": $status, "active": $active}')
    done
    
    HEALTH_RESULTS=$(echo "$HEALTH_RESULTS" | jq --argjson services "$service_results" '.checks.services = $services')
    
    success "Service health check completed"
}

# Application endpoint checks
check_endpoints() {
    log "Checking application endpoints..."
    
    local endpoints=("http://localhost/health" "http://localhost/api/status")
    local endpoint_results='{}'
    
    for endpoint in "${endpoints[@]}"; do
        local status="unknown"
        local response_time=0
        local http_code=0
        
        if command -v curl &> /dev/null; then
            local curl_output
            curl_output=$(curl -s -w "%{http_code},%{time_total}" --max-time "$HEALTH_CHECK_TIMEOUT" "$endpoint" 2>/dev/null || echo "000,0")
            http_code=$(echo "$curl_output" | tail -1 | cut -d',' -f1)
            response_time=$(echo "$curl_output" | tail -1 | cut -d',' -f2)
            
            if [[ "$http_code" == "200" ]]; then
                status="healthy"
            elif [[ "$http_code" =~ ^[45][0-9][0-9]$ ]]; then
                status="critical"
            else
                status="warning"
            fi
        else
            warning "curl not available, skipping endpoint checks"
            continue
        fi
        
        endpoint_results=$(echo "$endpoint_results" | jq --arg endpoint "$endpoint" --arg status "$status" \
            --argjson http_code "$http_code" --argjson response_time "$response_time" \
            '.[$endpoint] = {"status": $status, "http_code": $http_code, "response_time": $response_time}')
    done
    
    HEALTH_RESULTS=$(echo "$HEALTH_RESULTS" | jq --argjson endpoints "$endpoint_results" '.checks.endpoints = $endpoints')
    
    success "Endpoint health check completed"
}

# Database connectivity check
check_database() {
    log "Checking database connectivity..."
    
    local db_status="unknown"
    local connection_time=0
    
    if command -v psql &> /dev/null; then
        local start_time end_time
        start_time=$(date +%s.%N)
        
        if PGPASSWORD="${DB_PASSWORD:-}" psql -h "${DB_HOST:-localhost}" -U "${DB_USER:-postgres}" -d "${DB_NAME:-hx_infrastructure}" -c "SELECT 1;" &>/dev/null; then
            db_status="healthy"
            end_time=$(date +%s.%N)
            connection_time=$(echo "$end_time - $start_time" | bc -l)
        else
            db_status="critical"
        fi
    else
        warning "psql not available, skipping database check"
        db_status="skipped"
    fi
    
    HEALTH_RESULTS=$(echo "$HEALTH_RESULTS" | jq --arg status "$db_status" --argjson connection_time "$connection_time" \
        '.checks.database = {"status": $status, "connection_time": $connection_time}')
    
    success "Database connectivity check completed"
}

# Determine overall health status
determine_overall_status() {
    local failed_checks
    failed_checks=$(echo "$HEALTH_RESULTS" | jq -r '
        [
            (.checks.system // {} | to_entries[] | select(.value.status == "critical") | "system." + .key),
            (.checks.services // {} | to_entries[] | select(.value.status == "critical") | "service." + .key),
            (.checks.endpoints // {} | to_entries[] | select(.value.status == "critical") | "endpoint." + .key),
            (if .checks.database.status == "critical" then "database" else empty end)
        ]
    ')
    
    local overall_status
    if [[ "$(echo "$failed_checks" | jq 'length')" -gt 0 ]]; then
        overall_status="critical"
    else
        local warning_checks
        warning_checks=$(echo "$HEALTH_RESULTS" | jq -r '
            [
                (.checks.system // {} | to_entries[] | select(.value.status == "warning") | "system." + .key),
                (.checks.services // {} | to_entries[] | select(.value.status == "warning") | "service." + .key),
                (.checks.endpoints // {} | to_entries[] | select(.value.status == "warning") | "endpoint." + .key)
            ]
        ')
        
        if [[ "$(echo "$warning_checks" | jq 'length')" -gt 0 ]]; then
            overall_status="warning"
        else
            overall_status="healthy"
        fi
    fi
    
    HEALTH_RESULTS=$(echo "$HEALTH_RESULTS" | jq --arg status "$overall_status" --argjson failed "$failed_checks" \
        '.overall_status = $status | .failed_checks = $failed')
}

# Output results
output_results() {
    case "$OUTPUT_FORMAT" in
        json)
            echo "$HEALTH_RESULTS" | jq '.'
            ;;
        summary)
            local overall_status
            overall_status=$(echo "$HEALTH_RESULTS" | jq -r '.overall_status')
            
            case "$overall_status" in
                healthy)
                    success "Overall system status: HEALTHY"
                    ;;
                warning)
                    warning "Overall system status: WARNING"
                    ;;
                critical)
                    error "Overall system status: CRITICAL"
                    ;;
            esac
            
            echo "$HEALTH_RESULTS" | jq -r '.failed_checks[]' | while read -r check; do
                error "Failed check: $check"
            done
            ;;
    esac
}

# Save results to log file
save_results() {
    mkdir -p "$LOG_DIR"
    local log_file="${LOG_DIR}/health-check-$(date +%Y%m%d-%H%M%S).json"
    echo "$HEALTH_RESULTS" > "$log_file"
    log "Health check results saved to: $log_file"
}

# Send alerts if needed
send_alerts() {
    local overall_status
    overall_status=$(echo "$HEALTH_RESULTS" | jq -r '.overall_status')
    
    if [[ "$ALERT_ON_FAILURE" == "true" ]] && [[ "$overall_status" == "critical" ]]; then
        warning "Critical health issues detected - alerts should be sent"
        # Here you would integrate with your alerting system
        # Example: send to Slack, PagerDuty, email, etc.
    fi
}

# Help function
show_help() {
    cat << EOF
HX Infrastructure Health Check Script

Usage: $0 [OPTIONS]

Options:
    -t, --type TYPE           Check type (all|system|services|endpoints|database) [default: all]
    -f, --format FORMAT       Output format (json|summary) [default: json]
    -a, --alert-on-failure    Send alerts on failure [default: true]
    -h, --help               Show this help message

Examples:
    $0 --type system --format summary
    $0 --type all --format json
    
Environment Variables:
    CHECK_TYPE               Type of checks to perform
    OUTPUT_FORMAT           Output format
    ALERT_ON_FAILURE        Enable alerting on failure
    DB_HOST                 Database host
    DB_USER                 Database user
    DB_PASSWORD             Database password
    DB_NAME                 Database name
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--type)
                CHECK_TYPE="$2"
                shift 2
                ;;
            -f|--format)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            -a|--alert-on-failure)
                ALERT_ON_FAILURE="true"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Main execution
main() {
    log "Starting HX Infrastructure Health Check"
    
    init_results
    
    case "$CHECK_TYPE" in
        all)
            check_system_resources
            check_services
            check_endpoints
            check_database
            ;;
        system)
            check_system_resources
            ;;
        services)
            check_services
            ;;
        endpoints)
            check_endpoints
            ;;
        database)
            check_database
            ;;
        *)
            error "Invalid check type: $CHECK_TYPE"
            exit 1
            ;;
    esac
    
    determine_overall_status
    output_results
    save_results
    send_alerts
    
    # Exit with appropriate code
    local overall_status
    overall_status=$(echo "$HEALTH_RESULTS" | jq -r '.overall_status')
    case "$overall_status" in
        healthy)
            exit 0
            ;;
        warning)
            exit 1
            ;;
        critical)
            exit 2
            ;;
        *)
            exit 3
            ;;
    esac
}

# Parse arguments and run main function
parse_args "$@"
main
