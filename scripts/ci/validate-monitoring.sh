
#!/usr/bin/env bash
set -euo pipefail
# Placeholder monitoring schema check (expand later)
test -d "monitoring" || { echo "No monitoring/ directory"; exit 1; }
find monitoring -type f -name "*.y*ml" -print0 | xargs -0 -r yamllint -d "{extends: default, rules: {line-length: disable}}"
echo "Monitoring OK"
