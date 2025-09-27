
#!/bin/bash
# Full Code Rollback Script
# Usage: ./full_code_rollback.sh <target_color>

set -euo pipefail

TARGET_COLOR=${1:-}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +%s)
LOG_FILE="/tmp/full_rollback_${TIMESTAMP}.log"
ROLLBACK_TAG="v1.0.0-poc2prod"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Validation
if [[ -z "$TARGET_COLOR" ]]; then
    echo "Usage: $0 <target_color>"
    echo "Example: $0 blue"
    exit 1
fi

if [[ "$TARGET_COLOR" != "blue" && "$TARGET_COLOR" != "green" ]]; then
    echo "Error: target_color must be 'blue' or 'green'"
    exit 1
fi

# Determine inactive color
if [[ "$TARGET_COLOR" == "green" ]]; then
    INACTIVE_COLOR="blue"
else
    INACTIVE_COLOR="green"
fi

log "FULL CODE ROLLBACK: Rolling back to $ROLLBACK_TAG and deploying to $TARGET_COLOR"

# Save current state
log "Saving current repository state..."
git stash push -m "Emergency rollback stash - $(date)"

# Rollback to production tag
log "Rolling back code to $ROLLBACK_TAG..."
git reset --hard "$ROLLBACK_TAG"

# Deploy to target color
log "Deploying rolled-back code to $TARGET_COLOR environment..."
ansible-playbook -i inventories/production playbooks/deployment.yml \
    -e "target_color=$TARGET_COLOR" \
    --diff --limit "prod_$TARGET_COLOR" --verbose

# Switch traffic to rolled-back environment
log "Switching traffic to rolled-back $TARGET_COLOR environment..."
ansible-playbook -i inventories/production playbooks/switch_traffic.yml \
    -e "active_color=$TARGET_COLOR"

# Verify rollback success
log "Verifying full rollback success..."
sleep 30
for attempt in {1..5}; do
    if curl -sf "http://$(grep -A5 "\[load_balancers\]" inventories/production | grep -v "^\[" | head -1)/health" >/dev/null 2>&1; then
        log "SUCCESS: Full code rollback completed successfully"
        log "Active environment: $TARGET_COLOR (rolled back to $ROLLBACK_TAG)"
        log "Log file: $LOG_FILE"
        exit 0
    fi
    log "Attempt $attempt failed, retrying in 10 seconds..."
    sleep 10
done

log "ERROR: Full rollback verification failed after 5 attempts"
exit 1
