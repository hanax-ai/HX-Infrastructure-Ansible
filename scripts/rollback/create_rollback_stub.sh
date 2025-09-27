
#!/bin/bash
# Create Rollback Stub Script
# Usage: ./create_rollback_stub.sh <environment> [description]

set -euo pipefail

ENVIRONMENT=${1:-}
DESCRIPTION=${2:-"Rollback stub"}
TIMESTAMP=$(date +%s)
STUB_DIR="/tmp/rollback_stubs"
LOG_FILE="/tmp/rollback_stub_${TIMESTAMP}.log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Validation
if [[ -z "$ENVIRONMENT" ]]; then
    echo "Usage: $0 <environment> [description]"
    echo "Example: $0 production 'Pre-deployment rollback stub'"
    exit 1
fi

# Create rollback stub directory
mkdir -p "$STUB_DIR"

# Current git state
CURRENT_COMMIT=$(git rev-parse HEAD)
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_TAG=$(git describe --tags --exact-match 2>/dev/null || echo "No tag")

log "Creating rollback stub for $ENVIRONMENT environment"
log "Current commit: $CURRENT_COMMIT"
log "Current branch: $CURRENT_BRANCH"
log "Current tag: $CURRENT_TAG"

# Create rollback stub file
STUB_FILE="$STUB_DIR/rollback_${ENVIRONMENT}_${TIMESTAMP}.json"
cat > "$STUB_FILE" << EOF
{
  "created_at": "$(date -Iseconds)",
  "environment": "$ENVIRONMENT",
  "description": "$DESCRIPTION",
  "git_state": {
    "commit": "$CURRENT_COMMIT",
    "branch": "$CURRENT_BRANCH",
    "tag": "$CURRENT_TAG",
    "repository": "$(git config --get remote.origin.url)"
  },
  "rollback_commands": {
    "instant_traffic_flip": "./scripts/rollback/instant_traffic_flip.sh",
    "full_code_rollback": "./scripts/rollback/full_code_rollback.sh",
    "git_reset": "git reset --hard $CURRENT_COMMIT"
  },
  "ansible_inventories": {
    "production": "inventories/production",
    "staging": "inventories/staging",
    "development": "inventories/development"
  },
  "deployment_info": {
    "playbook": "playbooks/deployment.yml",
    "traffic_switch": "playbooks/switch_traffic.yml",
    "cleanup": "playbooks/cleanup_idle.yml"
  }
}
EOF

# Create human-readable stub
README_FILE="$STUB_DIR/rollback_${ENVIRONMENT}_${TIMESTAMP}_README.md"
cat > "$README_FILE" << EOF
# Rollback Stub - $ENVIRONMENT Environment

**Created:** $(date -Iseconds)  
**Description:** $DESCRIPTION  
**Git Commit:** $CURRENT_COMMIT  
**Git Branch:** $CURRENT_BRANCH  
**Git Tag:** $CURRENT_TAG  

## Quick Rollback Commands

### Instant Traffic Flip (≤10 minutes)
\`\`\`bash
# Switch traffic back to previous environment
./scripts/rollback/instant_traffic_flip.sh <current_color>
\`\`\`

### Full Code Rollback
\`\`\`bash
# Complete rollback to this commit
git reset --hard $CURRENT_COMMIT
git push origin HEAD:main --force-with-lease
./scripts/rollback/full_code_rollback.sh <target_color>
\`\`\`

### Manual Git Reset
\`\`\`bash
git reset --hard $CURRENT_COMMIT
\`\`\`

## Deployment Commands Used
\`\`\`bash
# Deploy to specific environment
ansible-playbook -i inventories/production playbooks/deployment.yml -e "target_color=<color>"

# Switch traffic
ansible-playbook -i inventories/production playbooks/switch_traffic.yml -e "active_color=<color>"

# Cleanup idle environment  
ansible-playbook -i inventories/production playbooks/cleanup_idle.yml -e "idle_color=<color>"
\`\`\`

## Emergency Contacts
- DRI: <name>
- Reviewer: <name>
- Approver: <name>
- On-call: <name>

EOF

log "Rollback stub created successfully:"
log "  JSON: $STUB_FILE"
log "  README: $README_FILE"
log "  Log: $LOG_FILE"

echo "Rollback stub created: $STUB_FILE"
echo "README: $README_FILE"
