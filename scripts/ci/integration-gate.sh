
#!/usr/bin/env bash
set -euo pipefail
# For now: ensure ansible scaffold is runnable in check mode against dev inventory
export ANSIBLE_CONFIG="infrastructure/ansible/ansible.cfg"
ansible-playbook -i infrastructure/ansible/inventories/dev/hosts.yml \
  infrastructure/ansible/playbooks/site.yml --check --syntax-check
echo "Integration gate OK"
