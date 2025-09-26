#!/bin/bash
# Phase 2B Day 3 Rollback Script
# Generated: 2025-09-26 16:09:30
# Baseline ID: 20250926_160650

set -euo pipefail

echo "=== Phase 2B Day 3 Rollback Initiated ==="
echo "Target: feature-consolidated-production"
echo "Pre-merge commit: 46d952e22734f3500e3fde89d40c825e95f165c1"
echo "Timestamp: 2025-09-26 16:09:30"

# Safety confirmation
read -p "⚠️  CONFIRM ROLLBACK for Day 3 consolidation? (yes/NO): " confirm
if [[ "$confirm" != "yes" ]]; then
    echo "❌ Rollback cancelled by user"
    exit 1
fi

# Step 1: Checkout target branch
echo "🔄 Checking out feature-consolidated-production..."
git checkout feature-consolidated-production

# Step 2: Reset to pre-merge state
echo "⏪ Resetting to pre-merge commit: 46d952e22734f3500e3fde89d40c825e95f165c1"
git reset --hard 46d952e22734f3500e3fde89d40c825e95f165c1

# Step 3: Force push to remote (with safety check)
echo "🚀 Force pushing reset to remote..."
read -p "⚠️  CONFIRM FORCE PUSH to origin/feature-consolidated-production? (yes/NO): " force_confirm
if [[ "$force_confirm" == "yes" ]]; then
    git push --force-with-lease origin feature-consolidated-production
    echo "✅ Remote branch reset successfully"
else
    echo "⚠️  Remote push skipped - local reset completed only"
fi

# Step 4: Restore source branches (if archived)
echo "🔄 Checking source branch availability..."
SOURCE_BRANCHES=(feature/coderabbit-remediation feature/pin-critical-directive feature/repo-recovery-phase1 feature/repo-recovery-phase2 feature-consolidated-production)
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
echo "Expected commit: 46d952e22734f3500e3fde89d40c825e95f165c1"

if [[ "$(git rev-parse HEAD)" == "46d952e22734f3500e3fde89d40c825e95f165c1" ]]; then
    echo "✅ Rollback verification PASSED"
else
    echo "❌ Rollback verification FAILED"
    exit 1
fi

echo "=== Phase 2B Day 3 Rollback Completed Successfully ==="
echo "📋 Next steps:"
echo "   1. Verify all source branches are available"
echo "   2. Check baseline drift report: docs/phase-2B/day3_drift.txt"
echo "   3. Review consolidation logs if re-attempting"
echo ""
echo "📊 Phase 2B Consolidation Summary:"
echo "   - Day 1: Infrastructure consolidation ✅"
echo "   - Day 2: Phase consolidation (13 branches) ✅"
echo "   - Day 3: Feature consolidation (5 branches) ✅"
echo "   - Total: 19 branches consolidated across 3 days"
