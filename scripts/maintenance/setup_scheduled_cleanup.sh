
#!/bin/bash
# Setup Scheduled Archive Cleanup
# Usage: ./setup_scheduled_cleanup.sh [enable|disable]

set -euo pipefail

ACTION=${1:-"enable"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLEANUP_SCRIPT="$SCRIPT_DIR/archive_cleanup.sh"
LOG_FILE="/tmp/scheduled_cleanup_setup.log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Validate action
if [[ "$ACTION" != "enable" && "$ACTION" != "disable" ]]; then
    echo "Usage: $0 [enable|disable]"
    echo "Example: $0 enable"
    exit 1
fi

log "Setting up scheduled archive cleanup: $ACTION"

if [[ "$ACTION" == "enable" ]]; then
    # Create scheduled cleanup workflow
    WORKFLOW_FILE=".github/workflows/scheduled-cleanup.yml"
    
    log "Creating scheduled cleanup workflow: $WORKFLOW_FILE"
    
    cat > "$WORKFLOW_FILE" << 'EOF'
name: Scheduled Archive Cleanup

on:
  schedule:
    # Run once a week on Sundays at 3 AM UTC
    - cron: '0 3 * * 0'
  workflow_dispatch:
    # Allow manual triggering
    inputs:
      dry_run:
        description: 'Run in dry-run mode'
        required: false
        default: 'false'
        type: boolean

jobs:
  archive-cleanup:
    name: Archive Branch Cleanup
    runs-on: ubuntu-latest
    permissions:
      contents: write
      
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history needed for branch analysis
          
      - name: Setup Git
        run: |
          git config --global user.name "GitHub Actions"
          git config --global user.email "actions@github.com"
          
      - name: Run archive cleanup
        run: |
          if [[ "${{ github.event.inputs.dry_run }}" == "true" ]]; then
            echo "Running in dry-run mode"
            ./scripts/maintenance/archive_cleanup.sh dry-run
          else
            echo "Running live cleanup"
            ./scripts/maintenance/archive_cleanup.sh
          fi
          
      - name: Upload cleanup log
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: archive-cleanup-log-${{ github.run_number }}
          path: /tmp/archive_cleanup_*.log
          retention-days: 90
EOF

    log "Scheduled cleanup workflow created"
    
    # Test the cleanup script
    log "Testing cleanup script in dry-run mode..."
    if bash "$CLEANUP_SCRIPT" dry-run; then
        log "Cleanup script test successful"
    else
        log "WARNING: Cleanup script test failed"
    fi
    
elif [[ "$ACTION" == "disable" ]]; then
    WORKFLOW_FILE=".github/workflows/scheduled-cleanup.yml"
    
    if [[ -f "$WORKFLOW_FILE" ]]; then
        log "Removing scheduled cleanup workflow: $WORKFLOW_FILE"
        rm "$WORKFLOW_FILE"
        log "Scheduled cleanup workflow removed"
    else
        log "Scheduled cleanup workflow not found - nothing to disable"
    fi
fi

# Security reminder
log "SECURITY REMINDER:"
log "Archive cleanup operations are destructive and should be:"
log "1. Tested thoroughly in dry-run mode first"
log "2. Reviewed by operations team before enabling"
log "3. Monitored for unexpected branch deletions"
log "4. Configured with appropriate branch protection rules"

log "Scheduled cleanup setup complete: $ACTION"
log "Log file: $LOG_FILE"

echo "Scheduled archive cleanup: $ACTION"
if [[ "$ACTION" == "enable" ]]; then
    echo "  Workflow: .github/workflows/scheduled-cleanup.yml"
    echo "  Schedule: Weekly on Sundays at 3 AM UTC"
    echo "  Manual trigger: Available in GitHub Actions"
fi
echo "Log: $LOG_FILE"
