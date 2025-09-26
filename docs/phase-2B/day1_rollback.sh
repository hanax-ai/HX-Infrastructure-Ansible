#!/bin/bash
# Phase 2B Day 1 Rollback Script
# Generated: 2025-09-26 16:02:39
# Baseline ID: 20250926_160239

set -euo pipefail

echo "=== Phase 2B Day 1 Rollback Initiated ==="
echo "Target: infrastructure-consolidated"
echo "Pre-merge commit: 1266159"
echo "Timestamp: 2025-09-26 16:02:39"

# Safety confirmation
read -p "⚠️  CONFIRM ROLLBACK for Day 1 consolidation? (yes/NO): " confirm
if [[ "$confirm" != "yes" ]]; then
    echo "❌ Rollback cancelled by user"
    exit 1
fi

# Step 1: Checkout target branch
echo "🔄 Checking out infrastructure-consolidated..."
git checkout infrastructure-consolidated

# Step 2: Reset to pre-merge state
echo "⏪ Resetting to pre-merge commit: 1266159"
git reset --hard 1266159

# Step 3: Force push to remote (with safety check)
echo "🚀 Force pushing reset to remote..."
read -p "⚠️  CONFIRM FORCE PUSH to origin/infrastructure-consolidated? (yes/NO): " force_confirm
if [[ "$force_confirm" == "yes" ]]; then
    git push --force-with-lease origin infrastructure-consolidated
    echo "✅ Remote branch reset successfully"
else
    echo "⚠️  Remote push skipped - local reset completed only"
fi

# Step 4: Restore source branches (if archived)
echo "🔄 Checking source branch availability..."
SOURCE_BRANCHES=(env-inventories-phase2)
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
echo "Expected commit: 1266159"

if [[ "$(git rev-parse HEAD)" == "1266159"* ]]; then
    echo "✅ Rollback verification PASSED"
else
    echo "❌ Rollback verification FAILED"
    exit 1
fi

echo "=== Phase 2B Day 1 Rollback Completed Successfully ==="
echo "📋 Next steps:"
echo "   1. Verify all source branches are available"
echo "   2. Check baseline drift report: docs/phase-2B/day1_drift.txt"
echo "   3. Review consolidation logs if re-attempting"
