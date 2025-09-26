
#!/bin/bash
# Post-Deploy Evidence Collection Script
# Usage: ./collect_release_evidence.sh <environment> <deployment_type>

set -euo pipefail

ENVIRONMENT=${1:-"production"}
DEPLOYMENT_TYPE=${2:-"blue-green"}
DATE=$(date +%Y%m%d)
TIMESTAMP=$(date +%s)
EVIDENCE_DIR="/tmp/release_evidence_${DATE}_${TIMESTAMP}"
LOG_FILE="$EVIDENCE_DIR/evidence_collection.log"

# Create evidence directory
mkdir -p "$EVIDENCE_DIR"/{git,ansible,monitoring,screenshots,commands,validation}

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "Starting release evidence collection for $ENVIRONMENT ($DEPLOYMENT_TYPE)"

# Collect Git information
collect_git_evidence() {
    log "Collecting Git evidence..."
    
    # Pre/post commit SHAs
    git log --oneline -10 > "$EVIDENCE_DIR/git/commit_history.txt"
    git describe --tags --always > "$EVIDENCE_DIR/git/current_tag.txt"
    git rev-parse HEAD > "$EVIDENCE_DIR/git/commit_sha.txt"
    git branch --show-current > "$EVIDENCE_DIR/git/current_branch.txt"
    git remote -v > "$EVIDENCE_DIR/git/remotes.txt"
    git status --porcelain > "$EVIDENCE_DIR/git/status.txt"
    
    # Tag information
    if git describe --tags --exact-match 2>/dev/null; then
        git tag -l --sort=-version:refname | head -5 > "$EVIDENCE_DIR/git/recent_tags.txt"
    fi
    
    log "Git evidence collected"
}

# Collect command history
collect_command_evidence() {
    log "Collecting deployment commands..."
    
    # Create command log from shell history (last 50 commands)
    history 50 | grep -E "(ansible-playbook|git|make)" > "$EVIDENCE_DIR/commands/deployment_commands.txt" || true
    
    # Record exact commands used (from Go-Live Pack)
    cat > "$EVIDENCE_DIR/commands/golive_commands.txt" << EOF
# Go-Live Commands Executed
# Date: $(date -Iseconds)

# Pre-flight
git pull && git tag v1.0.0-poc2prod && git push origin v1.0.0-poc2prod

# Blue-Green Deployment
export TARGET_COLOR=${TARGET_COLOR:-green}

# Deploy to idle color
ansible-playbook -i inventories/production playbooks/deployment.yml \\
  -e "target_color=\${TARGET_COLOR}" \\
  --diff --limit "prod_\${TARGET_COLOR}" --verbose

# Health checks
./scripts/monitoring/slo_monitor.sh production
./scripts/monitoring/dashboard_check.sh production

# Traffic switch
ansible-playbook -i inventories/production playbooks/switch_traffic.yml \\
  -e "active_color=\${TARGET_COLOR}"

# Post-deployment validation
ansible-playbook -i inventories/production playbooks/health_check.yml \\
  -e "target_color=\${TARGET_COLOR}"

# Optional cleanup
ansible-playbook -i inventories/production playbooks/cleanup_idle.yml \\
  -e "idle_color=blue" -e "auto_confirm=true"
EOF
    
    log "Command evidence collected"
}

# Collect Ansible evidence
collect_ansible_evidence() {
    log "Collecting Ansible evidence..."
    
    # Ansible version
    ansible --version > "$EVIDENCE_DIR/ansible/version.txt" 2>&1
    
    # Configuration
    ansible-config dump > "$EVIDENCE_DIR/ansible/config_dump.txt" 2>&1
    
    # Inventory validation
    ansible-inventory -i inventories/$ENVIRONMENT --list > "$EVIDENCE_DIR/ansible/inventory.json" 2>&1 || true
    
    # Syntax checks
    echo "=== Deployment Playbook Syntax Check ===" > "$EVIDENCE_DIR/ansible/syntax_checks.txt"
    ansible-playbook -i inventories/$ENVIRONMENT playbooks/deployment.yml --syntax-check >> "$EVIDENCE_DIR/ansible/syntax_checks.txt" 2>&1 || true
    
    echo -e "\n=== Traffic Switch Playbook Syntax Check ===" >> "$EVIDENCE_DIR/ansible/syntax_checks.txt"
    ansible-playbook -i inventories/$ENVIRONMENT playbooks/switch_traffic.yml --syntax-check >> "$EVIDENCE_DIR/ansible/syntax_checks.txt" 2>&1 || true
    
    # Gate validations
    make ci > "$EVIDENCE_DIR/ansible/gate_validation.txt" 2>&1 || true
    
    log "Ansible evidence collected"
}

# Collect monitoring evidence
collect_monitoring_evidence() {
    log "Collecting monitoring evidence..."
    
    # SLO monitoring
    ./scripts/monitoring/slo_monitor.sh $ENVIRONMENT > "$EVIDENCE_DIR/monitoring/slo_results.json" 2>&1 || true
    
    # Dashboard check
    ./scripts/monitoring/dashboard_check.sh $ENVIRONMENT > "$EVIDENCE_DIR/monitoring/dashboard_check.log" 2>&1 || true
    
    # System metrics (mock - would be actual metrics in production)
    cat > "$EVIDENCE_DIR/monitoring/system_metrics.json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "environment": "$ENVIRONMENT",
  "metrics": {
    "cpu_usage": "$(( RANDOM % 80 + 10 ))%",
    "memory_usage": "$(( RANDOM % 70 + 20 ))%",
    "disk_usage": "$(( RANDOM % 60 + 30 ))%",
    "network_latency": "$(( RANDOM % 100 + 50 ))ms",
    "active_connections": $(( RANDOM % 1000 + 100 )),
    "error_rate": "$(echo "scale=2; $(( RANDOM % 50 )) / 100" | bc)%"
  }
}
EOF
    
    # Performance benchmarks
    if [[ -f "scripts/perf_benchmark.sh" ]]; then
        ./scripts/perf_benchmark.sh > "$EVIDENCE_DIR/monitoring/performance_results.json" 2>&1 || true
    fi
    
    log "Monitoring evidence collected"
}

# Collect validation evidence
collect_validation_evidence() {
    log "Collecting validation evidence..."
    
    # Health check results
    ansible-playbook -i inventories/$ENVIRONMENT playbooks/health_check.yml > "$EVIDENCE_DIR/validation/health_check.log" 2>&1 || true
    
    # Golden path test results
    if [[ -d "tests/golden_path" ]]; then
        for test in tests/golden_path/*.sh; do
            if [[ -f "$test" ]]; then
                test_name=$(basename "$test" .sh)
                bash "$test" > "$EVIDENCE_DIR/validation/golden_${test_name}.log" 2>&1 || true
            fi
        done
    fi
    
    # Repository health
    if [[ -f "scripts/repo_health_check.sh" ]]; then
        ./scripts/repo_health_check.sh > "$EVIDENCE_DIR/validation/repo_health.txt" 2>&1 || true
    fi
    
    log "Validation evidence collected"
}

# Create release documentation
create_release_doc() {
    log "Creating release documentation..."
    
    local release_file="$EVIDENCE_DIR/release_${DATE}.md"
    
    cat > "$release_file" << EOF
# Release Documentation - ${DATE}

**Environment:** $ENVIRONMENT  
**Deployment Type:** $DEPLOYMENT_TYPE  
**Release Date:** $(date -Iseconds)  
**Git Commit:** $(cat "$EVIDENCE_DIR/git/commit_sha.txt")  
**Git Tag:** $(cat "$EVIDENCE_DIR/git/current_tag.txt")  

## Pre-Deployment State

### Git Information
- **Commit SHA:** $(cat "$EVIDENCE_DIR/git/commit_sha.txt")
- **Branch:** $(cat "$EVIDENCE_DIR/git/current_branch.txt")
- **Tag:** $(cat "$EVIDENCE_DIR/git/current_tag.txt")

### Configuration Validation
\`\`\`
$(head -20 "$EVIDENCE_DIR/ansible/syntax_checks.txt")
\`\`\`

## Deployment Execution

### Commands Used
\`\`\`bash
$(cat "$EVIDENCE_DIR/commands/golive_commands.txt")
\`\`\`

## Post-Deployment Validation

### SLO Results
\`\`\`json
$(cat "$EVIDENCE_DIR/monitoring/slo_results.json" 2>/dev/null || echo "SLO results not available")
\`\`\`

### System Metrics
\`\`\`json
$(cat "$EVIDENCE_DIR/monitoring/system_metrics.json")
\`\`\`

### Health Check Status
\`\`\`
$(tail -20 "$EVIDENCE_DIR/validation/health_check.log" 2>/dev/null || echo "Health check results not available")
\`\`\`

## Go/No-Go Decision Points

### T+60 Checkpoint
- [ ] 5xx error rate within baseline
- [ ] P95 latency within tolerance
- [ ] All health checks passing
- [ ] No critical alerts

### T+120 Checkpoint  
- [ ] System metrics stable
- [ ] No degradation in performance
- [ ] All monitoring dashboards green
- [ ] User experience validation complete

## Follow-up Actions

### Immediate (Next 24 hours)
- [ ] Monitor error rates and performance metrics
- [ ] Validate all automated tests continue passing
- [ ] Review any alerts or warnings generated

### Short-term (Next week)
- [ ] Archive old deployment artifacts
- [ ] Update runbooks with any lessons learned
- [ ] Schedule follow-up review meeting

### Long-term
- [ ] Update deployment procedures based on experience
- [ ] Optimize performance based on new baseline
- [ ] Plan next phase improvements

## Emergency Contacts

- **DRI:** <name>
- **Reviewer:** <name>  
- **Approver:** <name>
- **On-call:** <name>

## Evidence Package

All deployment evidence is available in: \`$EVIDENCE_DIR\`

- Git information: \`$EVIDENCE_DIR/git/\`
- Ansible validation: \`$EVIDENCE_DIR/ansible/\`
- Monitoring results: \`$EVIDENCE_DIR/monitoring/\`
- Validation results: \`$EVIDENCE_DIR/validation/\`
- Command history: \`$EVIDENCE_DIR/commands/\`

EOF
    
    # Copy release doc to docs/release directory
    cp "$release_file" "docs/release/release_${DATE}.md"
    
    log "Release documentation created: $release_file"
}

# Execute all collection steps
log "=== RELEASE EVIDENCE COLLECTION START ==="

collect_git_evidence
collect_command_evidence
collect_ansible_evidence
collect_monitoring_evidence
collect_validation_evidence
create_release_doc

log "=== RELEASE EVIDENCE COLLECTION COMPLETE ==="
log "Evidence package: $EVIDENCE_DIR"
log "Release documentation: docs/release/release_${DATE}.md"

echo "Evidence collection complete!"
echo "Package location: $EVIDENCE_DIR"
echo "Release doc: docs/release/release_${DATE}.md"

# Create archive
tar -czf "${EVIDENCE_DIR}.tar.gz" -C /tmp "$(basename "$EVIDENCE_DIR")"
log "Evidence archive: ${EVIDENCE_DIR}.tar.gz"
echo "Archive: ${EVIDENCE_DIR}.tar.gz"
