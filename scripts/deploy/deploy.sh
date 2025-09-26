#!/bin/bash
# HX Infrastructure Deployment Script

set -euo pipefail

ENVIRONMENT=${1:-dev}
PLAYBOOK=${2:-site.yml}
VAULT_PASSWORD_FILE=${3:-}

echo "=== HX Infrastructure Deployment ==="
echo "Environment: $ENVIRONMENT"
echo "Playbook: $PLAYBOOK"
echo "Timestamp: $(date)"

# Validate environment
if [[ ! -d "environments/$ENVIRONMENT" ]]; then
    echo "Error: Environment '$ENVIRONMENT' not found"
    exit 1
fi

# Build ansible-playbook command
ANSIBLE_CMD="ansible-playbook -i environments/$ENVIRONMENT/inventories/hosts.yml $PLAYBOOK"

if [[ -n "$VAULT_PASSWORD_FILE" ]]; then
    ANSIBLE_CMD="$ANSIBLE_CMD --vault-password-file $VAULT_PASSWORD_FILE"
fi

# Execute deployment
echo "Executing: $ANSIBLE_CMD"
$ANSIBLE_CMD

echo "=== Deployment completed successfully ==="
