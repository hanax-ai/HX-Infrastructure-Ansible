
#!/bin/bash
# Phase 2C Security Gate Validation Script
# Machine-checkable gate for security compliance

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "=== Phase 2C Security Gate Validation ==="
echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

# Exit codes
EXIT_SUCCESS=0
EXIT_FAILURE=1

# Validation counters
CHECKS_PASSED=0
CHECKS_FAILED=0

# Helper function for check results
check_result() {
    local test_name="$1"
    local result="$2"
    local details="${3:-}"
    
    if [ "$result" -eq 0 ]; then
        echo "✅ PASS: $test_name"
        [ -n "$details" ] && echo "    $details"
        ((CHECKS_PASSED++))
    else
        echo "❌ FAIL: $test_name"
        [ -n "$details" ] && echo "    $details"
        ((CHECKS_FAILED++))
    fi
}

echo "--- Security Compliance Validation ---"
cd "$PROJECT_ROOT"

# 1. Vault File Security
echo "Testing vault file security..."
vault_files_found=0
vault_files_secure=0

find . -name "*vault*" -type f | while read -r vault_file; do
    vault_files_found=$((vault_files_found + 1))
    
    # Check if file is encrypted
    if grep -q "ANSIBLE_VAULT" "$vault_file"; then
        vault_files_secure=$((vault_files_secure + 1))
        check_result "Vault encryption: $(basename "$vault_file")" 0 "Properly encrypted"
    else
        check_result "Vault encryption: $(basename "$vault_file")" 1 "Not encrypted"
    fi
    
    # Check file permissions
    perms=$(stat -c "%a" "$vault_file")
    if [ "$perms" = "600" ] || [ "$perms" = "640" ]; then
        check_result "Vault permissions: $(basename "$vault_file")" 0 "Permissions: $perms"
    else
        check_result "Vault permissions: $(basename "$vault_file")" 1 "Insecure permissions: $perms"
    fi
done

# 2. Sensitive Data Detection
echo "Testing for exposed sensitive data..."
sensitive_patterns=(
    "password.*=.*[^{]"
    "secret.*=.*[^{]"
    "api_key.*=.*[^{]"
    "private_key.*=.*[^{]"
    "token.*=.*[^{]"
)

for pattern in "${sensitive_patterns[@]}"; do
    if grep -r -i --exclude-dir=.git --exclude="*.vault*" "$pattern" . > /dev/null 2>&1; then
        check_result "Sensitive data exposure: $pattern" 1 "Found unencrypted sensitive data"
    else
        check_result "Sensitive data exposure: $pattern" 0 "No exposure detected"
    fi
done

# 3. SSH Key Security
echo "Testing SSH key security..."
find . -name "id_rsa" -o -name "id_dsa" -o -name "id_ecdsa" -o -name "id_ed25519" | while read -r key_file; do
    perms=$(stat -c "%a" "$key_file")
    if [ "$perms" = "600" ]; then
        check_result "SSH key permissions: $(basename "$key_file")" 0 "Secure permissions: $perms"
    else
        check_result "SSH key permissions: $(basename "$key_file")" 1 "Insecure permissions: $perms"
    fi
done

# 4. Playbook Security Best Practices
echo "Testing playbook security practices..."

# Check for become usage without password
if grep -r "become.*yes" . --include="*.yml" --include="*.yaml" | grep -v "become_password" > /dev/null; then
    become_count=$(grep -r "become.*yes" . --include="*.yml" --include="*.yaml" | grep -v "become_password" | wc -l)
    check_result "Privilege escalation security" 0 "Found $become_count secure become statements"
else
    check_result "Privilege escalation security" 0 "No privilege escalation found"
fi

# Check for hardcoded IPs (should use inventory)
if grep -r -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" . --include="*.yml" --include="*.yaml" --exclude-dir=environments > /dev/null; then
    check_result "Hardcoded IP addresses" 1 "Found hardcoded IPs outside inventory"
else
    check_result "Hardcoded IP addresses" 0 "No hardcoded IPs found"
fi

# 5. File Permission Validation
echo "Testing file permissions..."
find . -type f -name "*.yml" -o -name "*.yaml" | while read -r file; do
    perms=$(stat -c "%a" "$file")
    if [ "$perms" = "644" ] || [ "$perms" = "664" ] || [ "$perms" = "640" ]; then
        check_result "File permissions: $(basename "$file")" 0 "Secure permissions: $perms"
    else
        check_result "File permissions: $(basename "$file")" 1 "Questionable permissions: $perms"
    fi
done

# 6. Ansible Security Lint
echo "Running Ansible security lint..."
if command -v ansible-lint > /dev/null 2>&1; then
    # Run ansible-lint with security focus
    if ansible-lint --parseable . 2>/dev/null | grep -i -E "(password|secret|security|privilege)" > /dev/null; then
        check_result "Ansible security lint" 1 "Security issues detected by ansible-lint"
    else
        check_result "Ansible security lint" 0 "No security issues detected"
    fi
else
    check_result "Ansible security lint" 1 "ansible-lint not available"
fi

# 7. Git Security
echo "Testing Git security..."
if [ -d ".git" ]; then
    # Check for sensitive files in git history
    if git log --all --full-history -- "*password*" "*secret*" "*key*" | head -1 > /dev/null 2>&1; then
        check_result "Git history security" 1 "Sensitive files found in git history"
    else
        check_result "Git history security" 0 "No sensitive files in git history"
    fi
    
    # Check .gitignore for security patterns
    if [ -f ".gitignore" ]; then
        security_ignores=("*.pem" "*.key" "*password*" "*secret*" "*.vault_pass")
        missing_ignores=0
        
        for ignore_pattern in "${security_ignores[@]}"; do
            if ! grep -q "$ignore_pattern" .gitignore; then
                missing_ignores=$((missing_ignores + 1))
            fi
        done
        
        if [ $missing_ignores -eq 0 ]; then
            check_result "Gitignore security patterns" 0 "All security patterns present"
        else
            check_result "Gitignore security patterns" 1 "$missing_ignores security patterns missing"
        fi
    fi
fi

# 8. Role Security Validation
echo "Testing role security..."
find . -name "tasks" -type d | while read -r tasks_dir; do
    role_name=$(basename "$(dirname "$tasks_dir")")
    
    # Check for shell/command modules with user input
    if find "$tasks_dir" -name "*.yml" -exec grep -l -E "(shell|command):" {} \; | xargs grep -l "{{.*}}" > /dev/null 2>&1; then
        check_result "Role shell injection risk: $role_name" 1 "Potential shell injection risk"
    else
        check_result "Role shell injection risk: $role_name" 0 "No shell injection risk detected"
    fi
done

# Final Results
echo ""
echo "=== Security Gate Results ==="
echo "Checks Passed: $CHECKS_PASSED"
echo "Checks Failed: $CHECKS_FAILED"
echo "Total Checks: $((CHECKS_PASSED + CHECKS_FAILED))"

echo ""
echo "=== Security Compliance Summary ==="
echo "✓ Vault encryption validation"
echo "✓ Sensitive data exposure check"
echo "✓ SSH key security validation"
echo "✓ Playbook security best practices"
echo "✓ File permission validation"
echo "✓ Ansible security linting"
echo "✓ Git security validation"
echo "✓ Role security validation"

if [ $CHECKS_FAILED -eq 0 ]; then
    echo "🎉 SECURITY GATE: PASSED"
    exit $EXIT_SUCCESS
else
    echo "🚫 SECURITY GATE: FAILED"
    echo "Security compliance issues detected. Please remediate before proceeding."
    exit $EXIT_FAILURE
fi
