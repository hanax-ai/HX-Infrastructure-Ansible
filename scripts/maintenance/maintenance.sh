#!/bin/bash
# HX Infrastructure Maintenance Script

set -euo pipefail

ENVIRONMENT=${1:-dev}
ACTION=${2:-status}

echo "=== HX Infrastructure Maintenance ==="
echo "Environment: $ENVIRONMENT"
echo "Action: $ACTION"

case $ACTION in
    status)
        ansible all -i "environments/$ENVIRONMENT/inventories/hosts.yml" -m ping
        ;;
    update)
        ansible-playbook -i "environments/$ENVIRONMENT/inventories/hosts.yml" playbooks/maintenance/system-update.yml
        ;;
    restart)
        ansible-playbook -i "environments/$ENVIRONMENT/inventories/hosts.yml" playbooks/maintenance/service-restart.yml
        ;;
    *)
        echo "Usage: $0 <environment> <status|update|restart>"
        exit 1
        ;;
esac
