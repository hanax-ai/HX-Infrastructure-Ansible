
#!/bin/bash
# Instant Traffic Flip Rollback Script
# Usage: ./instant_traffic_flip.sh <current_color>

set -euo pipefail

CURRENT_COLOR=${1:-}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +%s)
LOG_FILE="/tmp/rollback_${TIMESTAMP}.log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Validation
if [[ -z "$CURRENT_COLOR" ]]; then
    echo "Usage: $0 <current_color>"
    echo "Example: $0 green"
    exit 1
fi

if [[ "$CURRENT_COLOR" != "blue" && "$CURRENT_COLOR" != "green" ]]; then
    echo "Error: current_color must be 'blue' or 'green'"
    exit 1
fi

# Determine target color
if [[ "$CURRENT_COLOR" == "green" ]]; then
    TARGET_COLOR="blue"
else
    TARGET_COLOR="green"
fi

log "EMERGENCY ROLLBACK: Instant traffic flip from $CURRENT_COLOR to $TARGET_COLOR"

# Pre-rollback health check
log "Performing pre-rollback health check on $TARGET_COLOR environment..."
if ! ansible-playbook -i inventories/production playbooks/health_check.yml \
    -e "target_color=$TARGET_COLOR" \
    --limit "prod_$TARGET_COLOR" 2>/dev/null; then
    log "WARNING: Health check failed on $TARGET_COLOR environment"
    read -p "Continue with rollback anyway? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        log "Rollback cancelled by user"
        exit 1
    fi
fi

# Execute instant traffic flip
log "Executing instant traffic flip to $TARGET_COLOR..."
ansible-playbook -i inventories/production playbooks/switch_traffic.yml \
    -e "active_color=$TARGET_COLOR" \
    -e "emergency_mode=true"

# Verify rollback success
log "Verifying rollback success..."
sleep 10
if curl -sf "http://$(grep -A5 "\[load_balancers\]" inventories/production | grep -v "^\[" | head -1)/health" >/dev/null 2>&1; then
    log "SUCCESS: Instant traffic flip rollback completed successfully"
    log "Active environment: $TARGET_COLOR"
    log "Log file: $LOG_FILE"
else
    log "ERROR: Rollback verification failed"
    exit 1
fi
