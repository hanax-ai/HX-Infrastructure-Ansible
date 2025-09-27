
#!/bin/bash
# Archive Cleanup Script with 30-day retention
# Usage: ./archive_cleanup.sh [dry-run]

set -euo pipefail

DRY_RUN=${1:-""}
RETENTION_DAYS=30
TIMESTAMP=$(date +%s)
LOG_FILE="/tmp/archive_cleanup_${TIMESTAMP}.log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Validation function
validate_branch() {
    local branch=$1
    local branch_date
    
    # Get last commit date for the branch
    if git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
        branch_date=$(git log -1 --format="%ct" "origin/$branch" 2>/dev/null || echo "0")
        local days_old=$(( (TIMESTAMP - branch_date) / 86400 ))
        
        if [[ $days_old -gt $RETENTION_DAYS ]]; then
            return 0  # Branch is older than retention period
        else
            return 1  # Branch is within retention period
        fi
    else
        return 2  # Branch doesn't exist
    fi
}

log "Starting archive cleanup with $RETENTION_DAYS day retention policy"

if [[ "$DRY_RUN" == "dry-run" ]]; then
    log "DRY RUN MODE - No branches will be deleted"
fi

# Get all remote branches
log "Fetching remote branch information..."
git fetch --all --prune

# Archive branches (branches that should be cleaned up after retention period)
ARCHIVE_BRANCHES=(
    "audit-fixes-*"
    "day*-consolidation*"
    "doc-refactor/*"
    "emergency-*"
    "feature/*"
    "fix/*"
    "hotfix/*"
    "phase-*"
    "phase1*"
    "phase2*"
    "phase3*"
    "phase4*"
    "remediate-*"
    "remediation-*"
    "security-remediation-*"
)

# Protected branches (never delete)
PROTECTED_BRANCHES=(
    "main"
    "master" 
    "develop"
    "staging"
    "production"
)

deleted_count=0
skipped_count=0
protected_count=0

# Process each remote branch
log "Processing remote branches for cleanup..."

for branch in $(git branch -r | grep -v "HEAD" | sed 's/origin\///g' | sort); do
    # Skip protected branches
    if [[ " ${PROTECTED_BRANCHES[*]} " =~ " ${branch} " ]]; then
        log "PROTECTED: Skipping protected branch '$branch'"
        ((protected_count++))
        continue
    fi
    
    # Check if branch matches archive patterns
    should_archive=false
    for pattern in "${ARCHIVE_BRANCHES[@]}"; do
        if [[ "$branch" == $pattern ]]; then
            should_archive=true
            break
        fi
    done
    
    if [[ "$should_archive" == false ]]; then
        log "SKIP: Branch '$branch' doesn't match archive patterns"
        ((skipped_count++))
        continue
    fi
    
    # Check retention period
    if validate_branch "$branch"; then
        log "CANDIDATE: Branch '$branch' is older than $RETENTION_DAYS days"
        
        if [[ "$DRY_RUN" == "dry-run" ]]; then
            log "DRY-RUN: Would delete branch '$branch'"
            ((deleted_count++))
        else
            # Actually delete the branch
            log "DELETING: Removing branch '$branch'"
            if git push origin --delete "$branch" 2>/dev/null; then
                log "SUCCESS: Deleted branch '$branch'"
                ((deleted_count++))
            else
                log "ERROR: Failed to delete branch '$branch'"
            fi
        fi
    else
        case $? in
            1)
                log "RETAIN: Branch '$branch' is within retention period"
                ((skipped_count++))
                ;;
            2)
                log "MISSING: Branch '$branch' doesn't exist remotely"
                ((skipped_count++))
                ;;
        esac
    fi
done

# Cleanup local tracking branches for deleted remotes
log "Cleaning up local tracking branches..."
git remote prune origin

# Summary
log "=== CLEANUP SUMMARY ==="
log "Retention period: $RETENTION_DAYS days"
log "Protected branches: $protected_count"
log "Skipped branches: $skipped_count"  
log "Processed branches: $deleted_count"
log "Mode: $(if [[ "$DRY_RUN" == "dry-run" ]]; then echo "DRY RUN"; else echo "LIVE"; fi)"
log "Log file: $LOG_FILE"

if [[ "$DRY_RUN" == "dry-run" ]]; then
    log "To execute cleanup, run: $(basename "$0")"
else
    log "Archive cleanup completed successfully"
fi

echo "Archive cleanup summary:"
echo "  Protected: $protected_count"  
echo "  Skipped: $skipped_count"
echo "  Processed: $deleted_count"
echo "  Mode: $(if [[ "$DRY_RUN" == "dry-run" ]]; then echo "DRY RUN"; else echo "LIVE"; fi)"
