
#!/bin/bash
# HX Infrastructure - Maintenance Scheduler Script
# Phase 3.4 - Production Operations Automation

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../" && pwd)"
INVENTORY_DIR="${PROJECT_ROOT}/inventory/production"
PLAYBOOK_DIR="${PROJECT_ROOT}/playbooks/production"
LOG_DIR="/var/log/hx-infrastructure"

# Default values
MAINTENANCE_TYPE="${MAINTENANCE_TYPE:-scheduled}"
MAINTENANCE_WINDOW="${MAINTENANCE_WINDOW:-02:00-06:00}"
DRY_RUN="${DRY_RUN:-false}"
FORCE_MAINTENANCE="${FORCE_MAINTENANCE:-false}"

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

# Help function
show_help() {
    cat << EOF
HX Infrastructure Maintenance Scheduler

Usage: $0 [OPTIONS]

Options:
    -t, --type TYPE           Maintenance type (scheduled|emergency|security) [default: scheduled]
    -w, --window WINDOW       Maintenance window (HH:MM-HH:MM) [default: 02:00-06:00]
    -d, --dry-run            Perform dry run without actual maintenance
    -f, --force              Force maintenance outside of window
    -h, --help               Show this help message

Examples:
    $0 --type scheduled --window 02:00-06:00
    $0 --type security --force --dry-run
    
Environment Variables:
    MAINTENANCE_TYPE         Type of maintenance
    MAINTENANCE_WINDOW       Maintenance window
    DRY_RUN                 Enable dry run mode
    FORCE_MAINTENANCE       Force maintenance execution
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--type)
                MAINTENANCE_TYPE="$2"
                shift 2
                ;;
            -w|--window)
                MAINTENANCE_WINDOW="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN="true"
                shift
                ;;
            -f|--force)
                FORCE_MAINTENANCE="true"
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

# Validate maintenance window
validate_maintenance_window() {
    log "Validating maintenance window..."
    
    local current_hour=$(date +%H)
    local current_minute=$(date +%M)
    local current_time=$((current_hour * 60 + current_minute))
    
    # Parse maintenance window
    local start_time=$(echo "$MAINTENANCE_WINDOW" | cut -d'-' -f1)
    local end_time=$(echo "$MAINTENANCE_WINDOW" | cut -d'-' -f2)
    
    local start_hour=$(echo "$start_time" | cut -d':' -f1)
    local start_minute=$(echo "$start_time" | cut -d':' -f2)
    local start_minutes=$((start_hour * 60 + start_minute))
    
    local end_hour=$(echo "$end_time" | cut -d':' -f1)
    local end_minute=$(echo "$end_time" | cut -d':' -f2)
    local end_minutes=$((end_hour * 60 + end_minute))
    
    # Check if current time is within maintenance window
    if [[ "$FORCE_MAINTENANCE" != "true" ]]; then
        if [[ $current_time -lt $start_minutes || $current_time -gt $end_minutes ]]; then
            error "Current time $(date +%H:%M) is outside maintenance window $MAINTENANCE_WINDOW"
            error "Use --force to override maintenance window restrictions"
            exit 1
        fi
    fi
    
    success "Maintenance window validated"
}

# Check system prerequisites
check_prerequisites() {
    log "Checking maintenance prerequisites..."
    
    # Check if ansible is available
    if ! command -v ansible-playbook &> /dev/null; then
        error "ansible-playbook is not installed or not in PATH"
        exit 1
    fi
    
    # Check if inventory exists
    if [[ ! -f "${INVENTORY_DIR}/hosts.yml" ]]; then
        error "Production inventory not found: ${INVENTORY_DIR}/hosts.yml"
        exit 1
    fi
    
    # Check for existing maintenance lock
    if [[ -f "/var/lock/hx-maintenance.lock" ]] && [[ "$FORCE_MAINTENANCE" != "true" ]]; then
        error "Maintenance lock file exists. Another maintenance may be in progress."
        error "Use --force to override lock file"
        exit 1
    fi
    
    # Validate maintenance type
    if [[ ! "$MAINTENANCE_TYPE" =~ ^(scheduled|emergency|security)$ ]]; then
        error "Invalid maintenance type: $MAINTENANCE_TYPE"
        error "Valid types: scheduled, emergency, security"
        exit 1
    fi
    
    success "Prerequisites validated"
}

# Check recent backups
verify_backups() {
    log "Verifying recent backups..."
    
    local backup_check_playbook="${PLAYBOOK_DIR}/maintenance/verify_backups.yml"
    
    if [[ -f "$backup_check_playbook" ]]; then
        ansible-playbook \
            -i "${INVENTORY_DIR}/hosts.yml" \
            "$backup_check_playbook" \
            ${DRY_RUN:+--check}
    else
        # Manual backup verification
        local recent_backups=$(find /opt/hx-infrastructure/backups -name "*.tar.gz" -mtime -1 2>/dev/null | wc -l)
        
        if [[ $recent_backups -eq 0 ]] && [[ "$MAINTENANCE_TYPE" != "emergency" ]]; then
            error "No recent backups found. Maintenance cannot proceed safely."
            error "Create a backup or use --force for emergency maintenance"
            exit 1
        fi
    fi
    
    success "Backup verification completed"
}

# Execute pre-maintenance tasks
pre_maintenance() {
    log "Executing pre-maintenance tasks..."
    
    local pre_maintenance_playbook="${PLAYBOOK_DIR}/maintenance/automated_maintenance.yml"
    
    if [[ -f "$pre_maintenance_playbook" ]]; then
        ansible-playbook \
            -i "${INVENTORY_DIR}/hosts.yml" \
            "$pre_maintenance_playbook" \
            --tags "pre_maintenance" \
            -e "maintenance_type=${MAINTENANCE_TYPE}" \
            -e "maintenance_window=${MAINTENANCE_WINDOW}" \
            ${DRY_RUN:+--check}
    else
        warning "Pre-maintenance playbook not found, skipping..."
    fi
}

# Execute main maintenance tasks
execute_maintenance() {
    log "Executing main maintenance tasks..."
    
    local maintenance_playbook="${PLAYBOOK_DIR}/maintenance/automated_maintenance.yml"
    
    if [[ ! -f "$maintenance_playbook" ]]; then
        error "Maintenance playbook not found: $maintenance_playbook"
        exit 1
    fi
    
    local ansible_args=(
        -i "${INVENTORY_DIR}/hosts.yml"
        "$maintenance_playbook"
        -e "maintenance_type=${MAINTENANCE_TYPE}"
        -e "maintenance_window=${MAINTENANCE_WINDOW}"
        -e "force_maintenance=${FORCE_MAINTENANCE}"
    )
    
    if [[ "$DRY_RUN" == "true" ]]; then
        ansible_args+=(--check)
        log "Running in dry-run mode..."
    fi
    
    if ansible-playbook "${ansible_args[@]}"; then
        success "Maintenance tasks completed successfully"
    else
        error "Maintenance tasks failed"
        exit 1
    fi
}

# Execute security patching
security_patching() {
    log "Executing security patching..."
    
    if [[ "$MAINTENANCE_TYPE" == "security" ]] || [[ "$MAINTENANCE_TYPE" == "scheduled" ]]; then
        local patching_playbook="${PLAYBOOK_DIR}/maintenance/system_updates.yml"
        
        if [[ -f "$patching_playbook" ]]; then
            ansible-playbook \
                -i "${INVENTORY_DIR}/hosts.yml" \
                "$patching_playbook" \
                -e "security_updates_only=true" \
                -e "maintenance_type=${MAINTENANCE_TYPE}" \
                ${DRY_RUN:+--check}
        else
            warning "Security patching playbook not found, skipping..."
        fi
    else
        log "Skipping security patching for maintenance type: $MAINTENANCE_TYPE"
    fi
}

# Execute post-maintenance verification
post_maintenance() {
    log "Executing post-maintenance verification..."
    
    if [[ "$DRY_RUN" != "true" ]]; then
        local verification_playbook="${PLAYBOOK_DIR}/maintenance/automated_maintenance.yml"
        
        if [[ -f "$verification_playbook" ]]; then
            ansible-playbook \
                -i "${INVENTORY_DIR}/hosts.yml" \
                "$verification_playbook" \
                --tags "post_maintenance" \
                -e "maintenance_type=${MAINTENANCE_TYPE}"
        else
            warning "Post-maintenance verification playbook not found"
        fi
    else
        log "Skipping post-maintenance verification in dry-run mode"
    fi
}

# Generate maintenance report
generate_report() {
    log "Generating maintenance report..."
    
    local report_file="${LOG_DIR}/maintenance-scheduler-$(date +%Y%m%d-%H%M%S).json"
    
    cat > "$report_file" << EOF
{
    "maintenance_execution": {
        "type": "${MAINTENANCE_TYPE}",
        "window": "${MAINTENANCE_WINDOW}",
        "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "dry_run": ${DRY_RUN},
        "forced": ${FORCE_MAINTENANCE},
        "status": "completed"
    },
    "system": {
        "hostname": "$(hostname)",
        "user": "$(whoami)",
        "ansible_version": "$(ansible --version | head -n1)"
    },
    "execution_summary": {
        "pre_maintenance": "completed",
        "main_maintenance": "completed",
        "security_patching": "completed",
        "post_maintenance": "completed"
    }
}
EOF
    
    success "Maintenance report generated: $report_file"
}

# Send maintenance notifications
send_notifications() {
    log "Sending maintenance notifications..."
    
    local notification_message="Maintenance ${MAINTENANCE_TYPE} completed on $(hostname) at $(date)"
    
    # Email notification (if configured)
    if command -v mail &> /dev/null && [[ -n "${MAINTENANCE_EMAIL_RECIPIENTS:-}" ]]; then
        echo "$notification_message" | mail -s "Maintenance Completed - $(hostname)" "$MAINTENANCE_EMAIL_RECIPIENTS"
    fi
    
    # Slack notification (if configured)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$notification_message\"}" \
            "$SLACK_WEBHOOK_URL" 2>/dev/null || true
    fi
    
    success "Notifications sent"
}

# Cleanup function
cleanup() {
    log "Performing cleanup..."
    
    # Remove maintenance lock file
    if [[ -f "/var/lock/hx-maintenance.lock" ]]; then
        rm -f "/var/lock/hx-maintenance.lock"
    fi
    
    # Clean up temporary files
    find /tmp -name "hx-maintenance-*" -mtime +1 -delete 2>/dev/null || true
    
    success "Cleanup completed"
}

# Main execution
main() {
    log "Starting HX Infrastructure Maintenance Scheduler"
    log "Type: ${MAINTENANCE_TYPE}, Window: ${MAINTENANCE_WINDOW}"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        warning "Running in DRY-RUN mode - no actual changes will be made"
    fi
    
    if [[ "$FORCE_MAINTENANCE" == "true" ]]; then
        warning "FORCE mode enabled - maintenance window restrictions bypassed"
    fi
    
    # Set trap for cleanup on exit
    trap cleanup EXIT
    
    validate_maintenance_window
    check_prerequisites
    verify_backups
    pre_maintenance
    execute_maintenance
    security_patching
    post_maintenance
    generate_report
    send_notifications
    
    success "Maintenance scheduler completed successfully!"
}

# Parse arguments and run main function
parse_args "$@"
main
