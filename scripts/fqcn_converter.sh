
#!/bin/bash

# FQCN Conversion Script - Convert bare module names to Fully Qualified Collection Names
echo "Starting FQCN conversion..."

# Common ansible.builtin modules
declare -a BUILTIN_MODULES=(
  "apt" "yum" "dnf" "package" 
  "service" "systemd"
  "file" "copy" "template" "fetch" "synchronize"
  "lineinfile" "replace" "blockinfile"
  "user" "group" "authorized_key"
  "shell" "command" "raw" "script"
  "debug" "set_fact" "assert" "fail"
  "include" "include_tasks" "include_vars" "include_role"
  "import_tasks" "import_playbook" "import_role"
  "meta" "pause" "wait_for"
  "stat" "find" "get_url" "uri"
  "mount" "filesystem" "lvg" "lvol"
  "cron" "at"
  "iptables" "firewalld"
  "sysctl" "hostname" "reboot"
  "ping" "setup"
)

# Find all YAML files (excluding hidden and backup dirs)
find . -name "*.yml" -o -name "*.yaml" | grep -v -E "(\/.git\/|venv|backup|\.bak)" | while read -r file; do
    # Skip if file doesn't contain tasks
    if ! grep -q "^\s*-\s*name:" "$file" 2>/dev/null; then
        continue
    fi
    
    echo "Processing: $file"
    
    # Convert each builtin module
    for module in "${BUILTIN_MODULES[@]}"; do
        # Match pattern: whitespace + module: (not already FQCN)
        sed -i "s/^\(\s\+\)${module}:\s*$/\1ansible.builtin.${module}:/" "$file"
    done
done

echo "FQCN conversion completed!"
