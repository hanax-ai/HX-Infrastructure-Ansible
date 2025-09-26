#!/bin/bash
# HX Infrastructure Backup Script

set -euo pipefail

ENVIRONMENT=${1:-prod}
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

echo "=== HX Infrastructure Backup ==="
echo "Environment: $ENVIRONMENT"
echo "Backup Directory: $BACKUP_DIR"

mkdir -p "$BACKUP_DIR"

# Backup configurations
cp -r "environments/$ENVIRONMENT" "$BACKUP_DIR/"
cp site.yml "$BACKUP_DIR/"
cp ansible.cfg "$BACKUP_DIR/"

echo "Backup completed: $BACKUP_DIR"
