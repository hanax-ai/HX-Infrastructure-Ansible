
#!/usr/bin/env bash
set -euo pipefail
# Markdown + basic docs checks
npm i -g markdownlint-cli2 >/dev/null
markdownlint-cli2 "**/*.md" "#node_modules"
echo "Docs OK"
