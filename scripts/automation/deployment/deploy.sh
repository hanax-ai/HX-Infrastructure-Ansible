
#!/bin/bash
# HX Infrastructure - Production Deployment Script
# Phase 3.4 - Production Operations Automation

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../" && pwd)"
INVENTORY_DIR="${PROJECT_ROOT}/inventory/production"
PLAYBOOK_DIR="${PROJECT_ROOT}/playbooks/production"

# Default values
DEPLOYMENT_STRATEGY="${DEPLOYMENT_STRATEGY:-blue_green}"
TARGET_ENVIRONMENT="${TARGET_ENVIRONMENT:-production}"
APP_VERSION="${APP_VERSION:-latest}"
DRY_RUN="${DRY_RUN:-false}"

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
HX Infrastructure Production Deployment Script

Usage: $0 [OPTIONS]

Options:
    -s, --strategy STRATEGY    Deployment strategy (blue_green|canary) [default: blue_green]
    -e, --environment ENV      Target environment [default: production]
    -v, --version VERSION      Application version to deploy [default: latest]
    -d, --dry-run             Perform dry run without actual deployment
    -h, --help                Show this help message

Examples:
    $0 --strategy blue_green --version v1.2.3
    $0 --strategy canary --environment staging --dry-run
    
Environment Variables:
    DEPLOYMENT_STRATEGY       Deployment strategy
    TARGET_ENVIRONMENT        Target environment
    APP_VERSION              Application version
    DRY_RUN                  Enable dry run mode
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--strategy)
                DEPLOYMENT_STRATEGY="$2"
                shift 2
                ;;
            -e|--environment)
                TARGET_ENVIRONMENT="$2"
                shift 2
                ;;
            -v|--version)
                APP_VERSION="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN="true"
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

# Validate prerequisites
validate_prerequisites() {
    log "Validating deployment prerequisites..."
    
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
    
    # Validate deployment strategy
    if [[ ! "$DEPLOYMENT_STRATEGY" =~ ^(blue_green|canary)$ ]]; then
        error "Invalid deployment strategy: $DEPLOYMENT_STRATEGY"
        error "Valid strategies: blue_green, canary"
        exit 1
    fi
    
    success "Prerequisites validated"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."
    
    local check_playbook="${PLAYBOOK_DIR}/deployment/pre_deployment_checks.yml"
    
    if [[ -f "$check_playbook" ]]; then
        ansible-playbook \
            -i "${INVENTORY_DIR}/hosts.yml" \
            "$check_playbook" \
            -e "target_environment=${TARGET_ENVIRONMENT}" \
            -e "app_version=${APP_VERSION}" \
            ${DRY_RUN:+--check}
    else
        warning "Pre-deployment checks playbook not found, skipping..."
    fi
}

# Execute deployment
execute_deployment() {
    log "Executing ${DEPLOYMENT_STRATEGY} deployment..."
    
    local deployment_playbook
    case "$DEPLOYMENT_STRATEGY" in
        blue_green)
            deployment_playbook="${PLAYBOOK_DIR}/deployment/blue_green_deploy.yml"
            ;;
        canary)
            deployment_playbook="${PLAYBOOK_DIR}/deployment/canary_deploy.yml"
            ;;
    esac
    
    if [[ ! -f "$deployment_playbook" ]]; then
        error "Deployment playbook not found: $deployment_playbook"
        exit 1
    fi
    
    local ansible_args=(
        -i "${INVENTORY_DIR}/hosts.yml"
        "$deployment_playbook"
        -e "target_environment=${TARGET_ENVIRONMENT}"
        -e "app_version=${APP_VERSION}"
        -e "deployment_strategy=${DEPLOYMENT_STRATEGY}"
    )
    
    if [[ "$DRY_RUN" == "true" ]]; then
        ansible_args+=(--check)
        log "Running in dry-run mode..."
    fi
    
    if ansible-playbook "${ansible_args[@]}"; then
        success "Deployment completed successfully"
    else
        error "Deployment failed"
        exit 1
    fi
}

# Post-deployment verification
post_deployment_verification() {
    log "Running post-deployment verification..."
    
    local verify_playbook="${PLAYBOOK_DIR}/deployment/post_deployment_verification.yml"
    
    if [[ -f "$verify_playbook" ]] && [[ "$DRY_RUN" != "true" ]]; then
        ansible-playbook \
            -i "${INVENTORY_DIR}/hosts.yml" \
            "$verify_playbook" \
            -e "target_environment=${TARGET_ENVIRONMENT}" \
            -e "app_version=${APP_VERSION}"
    else
        warning "Post-deployment verification skipped (dry-run mode or playbook not found)"
    fi
}

# Generate deployment report
generate_report() {
    log "Generating deployment report..."
    
    local report_file="/tmp/deployment-report-$(date +%Y%m%d-%H%M%S).json"
    
    cat > "$report_file" << EOF
{
    "deployment": {
        "strategy": "${DEPLOYMENT_STRATEGY}",
        "environment": "${TARGET_ENVIRONMENT}",
        "version": "${APP_VERSION}",
        "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "dry_run": ${DRY_RUN},
        "status": "completed"
    },
    "system": {
        "hostname": "$(hostname)",
        "user": "$(whoami)",
        "ansible_version": "$(ansible --version | head -n1)"
    }
}
EOF
    
    success "Deployment report generated: $report_file"
}

# Main execution
main() {
    log "Starting HX Infrastructure Production Deployment"
    log "Strategy: ${DEPLOYMENT_STRATEGY}, Environment: ${TARGET_ENVIRONMENT}, Version: ${APP_VERSION}"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        warning "Running in DRY-RUN mode - no actual changes will be made"
    fi
    
    validate_prerequisites
    pre_deployment_checks
    execute_deployment
    post_deployment_verification
    generate_report
    
    success "Deployment process completed successfully!"
}

# Parse arguments and run main function
parse_args "$@"
main
