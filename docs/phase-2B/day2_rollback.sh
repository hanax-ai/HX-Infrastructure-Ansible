#!/bin/bash
# Phase 2B Day 2 Rollback Script
# Generated: 2025-09-26 16:04:05
# Baseline ID: 20250926_160347

set -euo pipefail

echo "=== Phase 2B Day 2 Rollback Initiated ==="
echo "Target: phase-2-consolidated"
echo "Pre-merge commit: 214da48c61bfa2376ce8df7192ab22c3d602f4a7"
echo "Timestamp: 2025-09-26 16:04:05"

# Safety confirmation
read -p "⚠️  CONFIRM ROLLBACK for Day 2 consolidation? (yes/NO): " confirm
if [[ "$confirm" != "yes" ]]; then
    echo "❌ Rollback cancelled by user"
    exit 1
fi

# Step 1: Checkout target branch
echo "🔄 Checking out phase-2-consolidated..."
git checkout phase-2-consolidated

# Step 2: Reset to pre-merge state
echo "⏪ Resetting to pre-merge commit: 214da48c61bfa2376ce8df7192ab22c3d602f4a7"
git reset --hard 214da48c61bfa2376ce8df7192ab22c3d602f4a7

# Step 3: Force push to remote (with safety check)
echo "🚀 Force pushing reset to remote..."
read -p "⚠️  CONFIRM FORCE PUSH to origin/phase-2-consolidated? (yes/NO): " force_confirm
if [[ "$force_confirm" == "yes" ]]; then
    git push --force-with-lease origin phase-2-consolidated
    echo "✅ Remote branch reset successfully"
else
    echo "⚠️  Remote push skipped - local reset completed only"
fi

# Step 4: Restore source branches (if archived)
echo "🔄 Checking source branch availability..."
SOURCE_BRANCHES=(phase-2-ansible-standards phase2-role-standardization feature/phase2-security feature/phase-3-4-production-ops feat/var-templates-phase3 feature/sprint2-advanced feature/sprint3-operational-excellence feature/sprint4-final-production fix/phase3_4_remediation remediation-phase3_4-comprehensive remediate-r6-r7-feedback phase4/quality-standards-complete phase-3.3-backup-automation)
for branch in "${SOURCE_BRANCHES[@]}"; do
    if git show-ref --verify --quiet refs/heads/$branch; then
        echo "✅ Source branch '$branch' still available locally"
    elif git show-ref --verify --quiet refs/remotes/origin/$branch; then
        echo "🔄 Restoring source branch '$branch' from remote..."
        git checkout -b $branch origin/$branch
    else
        echo "⚠️  Source branch '$branch' not found - may need manual restoration"
    fi
done

# Step 5: Verification
echo "🔍 Verifying rollback state..."
echo "Current branch: $(git branch --show-current)"
echo "Current commit: $(git rev-parse HEAD)"
echo "Expected commit: 214da48c61bfa2376ce8df7192ab22c3d602f4a7"

if [[ "$(git rev-parse HEAD)" == "214da48c61bfa2376ce8df7192ab22c3d602f4a7" ]]; then
    echo "✅ Rollback verification PASSED"
else
    echo "❌ Rollback verification FAILED"
    exit 1
fi

echo "=== Phase 2B Day 2 Rollback Completed Successfully ==="
echo "📋 Next steps:"
echo "   1. Verify all source branches are available"
echo "   2. Check baseline drift report: docs/phase-2B/day2_drift.txt"
echo "   3. Review consolidation logs if re-attempting"
echo ""
echo "📊 Consolidated branches that were rolled back:"
echo "   - feature/phase2-security (security enhancements)"
echo "   - feature/sprint2-advanced (advanced features and documentation)"
echo "   - feature/sprint3-operational-excellence (operational excellence)"
echo "   - feature/sprint4-final-production (final production features)"
