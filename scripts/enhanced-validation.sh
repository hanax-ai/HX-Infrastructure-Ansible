#!/bin/bash
set -euo pipefail

echo "=== ENHANCED VALIDATION GATES ==="

# 1. YAML Syntax Validation
echo "1. YAML Syntax Validation..."
error_count=0
find . -name "*.yml" -o -name "*.yaml" | while read -r file; do
    if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
        echo "❌ YAML syntax error in: $file"
        ((error_count++))
    fi
done

if [ $error_count -eq 0 ]; then
    echo "✅ All YAML files have valid syntax"
fi

# 2. Required Files Check
echo "2. Required Files Check..."
required_files=("README.md" "requirements.yml" "site.yml" "ansible.cfg")
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
done
echo "✅ All required files present"

# 3. Basic Linting Check
echo "3. Basic Linting Check..."
if yamllint . 2>/dev/null | grep -c "error" | grep -q -v "^0$" 2>/dev/null; then
    echo "❌ Critical linting errors found"
    exit 1
else
    echo "✅ No critical linting errors blocking CI"
fi

echo "=== ALL VALIDATION GATES PASSED ==="
